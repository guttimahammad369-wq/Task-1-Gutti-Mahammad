from services.prompt_service import PromptService
from services.llm_service import LLMService
from services.query_planner import QueryPlanner
from services.execution_engine import ExecutionEngine


class AIAgent:

    def __init__(self, dataframe):

        self.df = dataframe

        self.planner = QueryPlanner(dataframe)
        self.engine = ExecutionEngine(dataframe)

        self.prompt_service = PromptService(dataframe)
        self.llm = LLMService()

    # --------------------------------------------------

    def ask(self, question):

        try:

            # --------------------------------------
            # Step 1
            # Try Local Analytics First
            # --------------------------------------

            plan = self.planner.build(question)

            result = self.engine.execute(plan)

            if result is not None:

                return self.format_result(result)

            # --------------------------------------
            # Step 2
            # Fallback to Gemini
            # --------------------------------------

            prompt = self.prompt_service.build(question)

            return self.llm.ask(prompt)

        except Exception as e:

            return f"""
❌ AI Agent Error

{e}
"""

    # --------------------------------------------------

    def format_result(self, result):

        try:

            if hasattr(result, "to_markdown"):
                return result.to_markdown()

            if hasattr(result, "to_string"):
                return result.to_string()

            return str(result)

        except Exception:

            return str(result)