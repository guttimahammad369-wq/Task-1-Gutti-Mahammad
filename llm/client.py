import re
import time
from typing import Any, Dict, List, Optional
from google import genai
from google.genai import types
from google.genai.errors import APIError, ClientError

from analytics.data_loader import data_loader
from analytics.engine import analytics_engine
from config.prompts import SYSTEM_PROMPT_TEMPLATE
from config.settings import settings
from memory.conversation_memory import ConversationMemoryManager
from utils.logger import logger


class LLMClient:
    """Production-grade LLM service orchestrator interfacing with Gemini SDK.

    Manages system prompt construction, sliding-window memory integration,
    deterministic analytics retrieval, and API rate-limit resilience with graceful fallbacks.
    """

    def __init__(self, model_name: str = settings.PRIMARY_LLM_MODEL):
        """Initializes Gemini API client using application settings.

        Args:
            model_name: Gemini model string identifier.
        """
        self.model_name = model_name
        self.gemini_key = settings.GEMINI_API_KEY
        self.client = None

        if self.gemini_key:
            try:
                self.client = genai.Client(api_key=self.gemini_key)
                logger.info(f"Initialized Gemini LLMClient with model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini Client: {e}")

    def generate_response(
        self,
        user_query: str,
        memory_manager: ConversationMemoryManager,
        dataset_path: Optional[str] = None,
    ) -> str:
        """Orchestrates multi-turn conversational response generation.

        Steps:
        1. Appends user query to stateful conversation memory.
        2. Retrieves dataset schema context and relevant deterministic analytics.
        3. Formats sliding window message history.
        4. Invokes LLM API with automatic retry backoff and fallback synthesis.
        5. Appends assistant response to stateful memory.

        Args:
            user_query: User natural language question.
            memory_manager: Active session ConversationMemoryManager instance.
            dataset_path: Optional path to custom loaded dataset.

        Returns:
            str: Generated assistant response.
        """
        # Step 1: Record user message in memory
        memory_manager.add_user_message(user_query)

        # Step 2: Extract dataset context metadata
        if data_loader.metadata is None:
            data_loader.load_data()

        schema_context = data_loader.metadata.to_system_prompt_context()

        # Step 3: Compute deterministic analytics relevant to query
        analytics_context = self._retrieve_analytics_context(user_query, memory_manager)

        # Step 4: Build combined system prompt
        system_instruction = SYSTEM_PROMPT_TEMPLATE.format(
            dataset_context=f"{schema_context}\n\n{analytics_context}"
        )

        # Step 5: Format sliding window conversation history for API payload
        history = memory_manager.get_sliding_window_history()

        # Build contents prompt for Gemini API
        prompt_parts = [system_instruction, "\n--- CONVERSATION HISTORY & CURRENT QUERY ---"]
        for msg in history:
            role_label = "User" if msg["role"] == "user" else "Assistant"
            prompt_parts.append(f"{role_label}: {msg['content']}")

        full_prompt = "\n".join(prompt_parts)

        # Step 6: Call Gemini API with exponential backoff retry and fallback
        response_text = self._call_llm_with_retry(full_prompt, analytics_context, user_query, memory_manager)

        # Step 7: Record assistant response in stateful memory
        memory_manager.add_assistant_message(response_text)

        return response_text

    def _retrieve_analytics_context(self, query: str, memory_manager: Optional[ConversationMemoryManager] = None) -> str:
        """Retrieves exact deterministic metrics based on query keywords and memory context.

        Args:
            query: User prompt.
            memory_manager: ConversationMemoryManager for resolving context pronouns ("it").

        Returns:
            str: Formatted markdown string containing pre-calculated metrics.
        """
        query_lower = query.lower()
        context_parts = ["### DETERMINISTIC METRICS FROM DATASET:"]

        # Pronoun resolution check: if "it" or "that product" is asked, check previous memory turn for product name
        resolved_product = None
        if memory_manager and re.search(r"\b(it|that product|its revenue|its sales)\b", query_lower):
            history = memory_manager.get_sliding_window_history()
            for msg in reversed(history[:-1]):
                content = msg.get("content", "")
                for prod in ["Chair", "Printer", "Laptop", "Tablet", "Monitor", "Desk", "Phone"]:
                    if prod.lower() in content.lower():
                        resolved_product = prod
                        break
                if resolved_product:
                    break

        if resolved_product:
            prod_df = analytics_engine.filter_dataset(product=resolved_product)
            total_rev = prod_df["TotalPrice"].sum()
            units_sold = prod_df["Quantity"].sum()
            order_cnt = len(prod_df)
            context_parts.append(
                f"- **Resolved Context Product**: `{resolved_product}`\n"
                f"- **{resolved_product} Total Revenue**: ${total_rev:,.2f}\n"
                f"- **{resolved_product} Units Sold**: {units_sold:,}\n"
                f"- **{resolved_product} Total Orders**: {order_cnt:,}"
            )

        if re.search(r"\b(total|revenue|sales|summary|kpi|average|aov|orders|order)\b", query_lower) and not resolved_product:
            kpis = analytics_engine.get_summary_kpis()
            context_parts.append(
                f"- **Total Revenue**: ${kpis['total_revenue']:,.2f}\n"
                f"- **Total Orders**: {kpis['total_orders']:,}\n"
                f"- **Average Order Value (AOV)**: ${kpis['average_order_value']:,.2f}\n"
                f"- **Cancelled Orders**: {kpis['cancelled_orders']} ({kpis['cancellation_rate_pct']}%)"
            )

        if re.search(r"\b(product|products|top|item|laptop|chair|phone|printer|tablet|highest|sold|most)\b", query_lower):
            top_prods = analytics_engine.get_revenue_by_product(5)
            context_parts.append(
                f"\n- **Top Products by Revenue**:\n{top_prods.to_markdown(index=False)}"
            )

        if re.search(r"\b(month|monthly|trend|january|february|year)\b", query_lower):
            monthly = analytics_engine.get_monthly_sales_trend()
            context_parts.append(
                f"\n- **Monthly Sales Trend (Latest 6 Months)**:\n{monthly.tail(6).to_markdown(index=False)}"
            )

        if re.search(r"\b(status|cancel|cancelled|delivered|pending|returned)\b", query_lower):
            status_df = analytics_engine.get_order_status_distribution()
            context_parts.append(
                f"\n- **Order Status Distribution**:\n{status_df.to_markdown(index=False)}"
            )

        if re.search(r"\b(payment|card|cash|credit|debit|gift|online)\b", query_lower):
            pay_df = analytics_engine.get_payment_method_distribution()
            context_parts.append(
                f"\n- **Payment Method Split**:\n{pay_df.to_markdown(index=False)}"
            )

        if re.search(r"\b(referral|source|instagram|facebook|google|email)\b", query_lower):
            ref_df = analytics_engine.get_referral_source_performance()
            context_parts.append(
                f"\n- **Referral Source Performance**:\n{ref_df.to_markdown(index=False)}"
            )

        if re.search(r"\b(coupon|discount|code|freeship|save10|winter15)\b", query_lower):
            coupon_df = analytics_engine.get_coupon_code_performance()
            context_parts.append(
                f"\n- **Coupon Performance**:\n{coupon_df.to_markdown(index=False)}"
            )

        return "\n".join(context_parts) if len(context_parts) > 1 else ""

    def _call_llm_with_retry(
        self,
        prompt: str,
        analytics_context: str,
        user_query: str,
        memory_manager: Optional[ConversationMemoryManager] = None,
        max_retries: int = 2,
    ) -> str:
        """Invokes Gemini API with exponential backoff and analytics fallback.

        Args:
            prompt: Text prompt for generation.
            analytics_context: Extracted deterministic metrics.
            user_query: Original user query.
            memory_manager: Session memory manager.
            max_retries: Maximum API retry attempts.

        Returns:
            str: Generated text response.
        """
        if not self.client:
            return self._generate_fallback_synthesis(analytics_context, user_query, memory_manager)

        delay = 2.0
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Sending LLM request to {self.model_name} (Attempt {attempt}/{max_retries})")
                config = types.GenerateContentConfig(
                    temperature=settings.LLM_TEMPERATURE,
                    max_output_tokens=settings.MAX_OUTPUT_TOKENS,
                )
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config,
                )
                if response and hasattr(response, "text") and response.text:
                    return response.text.strip()

            except ClientError as e:
                logger.warning(
                    f"Gemini API ClientError (code {e.code}): {e.message}. Attempt {attempt}/{max_retries}"
                )
                if e.code == 429 and attempt < max_retries:
                    time.sleep(delay)
                    delay *= 2.0
            except Exception as e:
                logger.error(f"Unexpected error during LLM generation: {e}", exc_info=True)
                break

        # Fallback synthesis if API limit occurs
        logger.info("Falling back to deterministic analytics synthesis engine.")
        return self._generate_fallback_synthesis(analytics_context, user_query, memory_manager)

    def _generate_fallback_synthesis(
        self,
        analytics_context: str,
        user_query: str,
        memory_manager: Optional[ConversationMemoryManager] = None,
    ) -> str:
        """Generates intelligent contextual response when API limits occur.

        Args:
            analytics_context: Pre-calculated metrics.
            user_query: User query string.
            memory_manager: Memory manager instance.

        Returns:
            str: Clean analytical response.
        """
        query_lower = user_query.lower().strip()

        # Handle greetings using regex word boundaries
        if re.search(r"\b(hey|hi|hello|greetings|good morning|good afternoon)\b", query_lower):
            return (
                "Hello! 👋 I am your AI Data Analytics Assistant.\n\n"
                "I am ready to help you analyze your business dataset. You can ask questions like:\n"
                "- **\"What is the total revenue?\"**\n"
                "- **\"Which product generated the highest revenue?\"**\n"
                "- **\"Show monthly sales trend.\"**\n"
                "- **\"What payment method is used most?\"**"
            )

        # Handle general ML question
        if re.search(r"\b(ml|machine learning)\b", query_lower):
            return (
                "**Machine Learning (ML)** is a branch of Artificial Intelligence (AI) that enables systems to learn patterns from data and make predictions without explicit hardcoded rules.\n\n"
                "In data analytics, ML is used for predictive forecasting, customer segmentation, recommendation engines, and automated anomaly detection."
            )

        if not analytics_context:
            kpis = analytics_engine.get_summary_kpis()
            return (
                f"Here is the summary analysis for your dataset:\n\n"
                f"- **Total Revenue**: ${kpis['total_revenue']:,.2f}\n"
                f"- **Total Orders**: {kpis['total_orders']:,}\n"
                f"- **Average Order Value (AOV)**: ${kpis['average_order_value']:,.2f}\n"
                f"- **Cancellation Rate**: {kpis['cancellation_rate_pct']}%\n"
            )

        clean_metrics = analytics_context.replace("### DETERMINISTIC METRICS FROM DATASET:", "").strip()
        return (
            f"Based on the business dataset analytics for **\"{user_query}\"**:\n\n"
            f"{clean_metrics}"
        )


# Global singleton instance
llm_client = LLMClient()
