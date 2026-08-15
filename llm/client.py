import time
from typing import Optional

from google import genai
from google.genai import types
from google.genai.errors import APIError, ClientError

from config.settings import settings
from memory.conversation_memory import ConversationMemoryManager
from utils.logger import logger


class LLMClient:
    """
    LLM client responsible only for conversational AI.

    Flow:

        User Message
             ↓
        Conversation Memory
             ↓
        Sliding Window
             ↓
        Gemini API
             ↓
        Assistant Response
             ↓
        Conversation Memory
    """

    def __init__(
        self,
        model_name: str = settings.PRIMARY_LLM_MODEL,
    ):
        self.model_name = model_name
        self.gemini_key = settings.GEMINI_API_KEY
        self.client = None

        if self.gemini_key:
            try:
                self.client = genai.Client(
                    api_key=self.gemini_key
                )

                logger.info(
                    f"Initialized Gemini LLMClient "
                    f"with model: {self.model_name}"
                )

            except Exception as error:
                logger.error(
                    f"Failed to initialize Gemini Client: "
                    f"{error}"
                )

    # =========================================================
    # MAIN RESPONSE PIPELINE
    # =========================================================

    def generate_response(
        self,
        user_query: str,
        memory_manager: ConversationMemoryManager,
        dataset_path: Optional[str] = None,
    ) -> str:
        """
        Generate a conversational response.

        The conversation history is maintained by
        ConversationMemoryManager and restricted using
        its sliding-window/token protection.
        """

        # -----------------------------------------------------
        # 1. Validate input
        # -----------------------------------------------------

        user_query = user_query.strip()

        if not user_query:
            raise ValueError(
                "User message cannot be empty."
            )

        # -----------------------------------------------------
        # 2. Store user message
        # -----------------------------------------------------

        memory_manager.add_user_message(
            user_query
        )

        # -----------------------------------------------------
        # 3. Get bounded conversation history
        # -----------------------------------------------------

        history = (
            memory_manager
            .get_sliding_window_history()
        )

        # -----------------------------------------------------
        # 4. Build conversational prompt
        # -----------------------------------------------------

        prompt_parts = [
            (
                "You are a helpful conversational AI "
                "assistant."
            ),
            (
                "Use the conversation history below "
                "to maintain context across turns."
            ),
            (
                "Answer the user's current message "
                "naturally and accurately."
            ),
            "",
            "--- CONVERSATION HISTORY ---",
        ]

        for message in history:

            role = message["role"]
            content = message["content"]

            if role == "user":
                role_label = "User"

            elif role == "assistant":
                role_label = "Assistant"

            elif role == "system":
                role_label = "System"

            else:
                role_label = role.capitalize()

            prompt_parts.append(
                f"{role_label}: {content}"
            )

        full_prompt = "\n".join(
            prompt_parts
        )

        # -----------------------------------------------------
        # 5. Call Gemini
        # -----------------------------------------------------

        response_text = (
            self._call_llm_with_retry(
                full_prompt
            )
        )

        # -----------------------------------------------------
        # 6. Store assistant response
        # -----------------------------------------------------

        memory_manager.add_assistant_message(
            response_text
        )

        return response_text

    # =========================================================
    # GEMINI API CALL
    # =========================================================

    def _call_llm_with_retry(
        self,
        prompt: str,
        max_retries: int = 2,
    ) -> str:
        """
        Call Gemini with retry handling.
        """

        if not self.client:

            logger.error(
                "Gemini client is unavailable."
            )

            raise RuntimeError(
                "Gemini client is not initialized. "
                "Check GEMINI_API_KEY."
            )

        delay = 2.0

        for attempt in range(
            1,
            max_retries + 1,
        ):

            try:

                logger.info(
                    f"Sending LLM request to "
                    f"{self.model_name} "
                    f"(Attempt "
                    f"{attempt}/{max_retries})"
                )

                config = (
                    types.GenerateContentConfig(
                        temperature=(
                            settings.LLM_TEMPERATURE
                        ),
                        max_output_tokens=(
                            settings.MAX_OUTPUT_TOKENS
                        ),
                    )
                )

                response = (
                    self.client
                    .models
                    .generate_content(
                        model=self.model_name,
                        contents=prompt,
                        config=config,
                    )
                )

                if (
                    response
                    and hasattr(
                        response,
                        "text",
                    )
                    and response.text
                ):

                    return response.text.strip()

                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            except ClientError as error:

                logger.warning(
                    "Gemini API ClientError "
                    f"(code {error.code}): "
                    f"{error.message}. "
                    f"Attempt {attempt}/"
                    f"{max_retries}"
                )

                if (
                    error.code == 429
                    and attempt < max_retries
                ):

                    time.sleep(delay)
                    delay *= 2.0

                else:
                    raise

            except APIError as error:

                logger.warning(
                    f"Gemini API error: {error}"
                )

                if attempt < max_retries:
                    time.sleep(delay)
                    delay *= 2.0
                else:
                    raise

            except Exception as error:

                logger.error(
                    "Unexpected error during "
                    f"LLM generation: {error}",
                    exc_info=True,
                )

                raise


# =============================================================
# GLOBAL SINGLETON
# =============================================================

llm_client = LLMClient()