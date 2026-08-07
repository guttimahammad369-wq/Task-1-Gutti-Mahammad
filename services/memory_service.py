class MemoryService:

    def __init__(self):
        self.chat_history = []

    def add_user_message(self, message):
        self.chat_history.append(
            {
                "role": "user",
                "parts": [{"text": message}]
            }
        )

    def add_ai_message(self, message):
        self.chat_history.append(
            {
                "role": "model",
                "parts": [{"text": message}]
            }
        )

    def get_history(self):
        return self.chat_history