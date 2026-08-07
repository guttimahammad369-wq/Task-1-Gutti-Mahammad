import os
from dotenv import load_dotenv
from google import genai

load_dotenv()


class LLMService:

    def __init__(self):

        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )

        self.model = "gemini-2.5-flash"

    def ask(self, prompt):

        try:

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )

            return response.text

        except Exception as e:

            return f"""
❌ AI Service Temporarily Unavailable

Reason:
{e}

Please try again.
"""