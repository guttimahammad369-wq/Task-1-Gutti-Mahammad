import uuid
from typing import Any, Dict, List, Optional
from config.settings import settings
from models.chat_models import ChatMessage, ConversationThread, MessageRole
from utils.logger import logger


class ConversationMemoryManager:
    """Stateful conversation memory manager with sliding window pruning.

    Stores role-based chat messages in structured objects and provides
    context preservation and dynamic sliding window context pruning.
    """

    def __init__(
        self,
        session_id: Optional[str] = None,
        max_turns: int = settings.MAX_MEMORY_TURNS,
        max_tokens: int = settings.MAX_HISTORY_TOKENS,
    ):
        """Initializes conversation memory for a session.

        Args:
            session_id: Unique session identifier. Defaults to new UUID.
            max_turns: Maximum user-assistant message pairs retained.
            max_tokens: Maximum token threshold for sliding window.
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.max_turns = max_turns
        self.max_tokens = max_tokens
        self.thread = ConversationThread(session_id=self.session_id)
        logger.info(f"Initialized ConversationMemoryManager for session: {self.session_id}")

    def add_user_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> ChatMessage:
        """Appends a user message to conversation history."""
        msg = self.thread.add_message(MessageRole.USER, content, metadata)
        logger.debug(f"[{self.session_id}] Added User message: '{content[:50]}...'")
        return msg

    def add_assistant_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> ChatMessage:
        """Appends an assistant message to conversation history."""
        msg = self.thread.add_message(MessageRole.ASSISTANT, content, metadata)
        logger.debug(f"[{self.session_id}] Added Assistant message: '{content[:50]}...'")
        return msg

    def add_system_message(self, content: str) -> ChatMessage:
        """Appends or updates system prompt context."""
        msg = self.thread.add_message(MessageRole.SYSTEM, content)
        return msg

    def estimate_tokens(self, text: str) -> int:
        """Estimates token count for text using standard word/character heuristic.

        Rule of thumb: ~1 token ≈ 4 characters or ~0.75 words.

        Args:
            text: Input string.

        Returns:
            int: Estimated token count.
        """
        if not text:
            return 0
        return max(1, int(len(text) / 4))

    def get_sliding_window_history(self) -> List[Dict[str, str]]:
        """Applies sliding window pruning algorithm to retrieve context window.

        Algorithm Rules:
        1. System messages are prioritized and preserved at the front.
        2. Retains up to `max_turns` (user + assistant message pairs).
        3. Prunes older messages if total estimated tokens exceed `max_tokens`.

        Returns:
            List[Dict[str, str]]: Pruned message history ready for LLM API call.
        """
        all_messages = self.thread.messages
        if not all_messages:
            return []

        # Separate system messages from chat conversation turns
        system_msgs = [m for m in all_messages if m.role == MessageRole.SYSTEM]
        chat_msgs = [m for m in all_messages if m.role != MessageRole.SYSTEM]

        # 1. Turn-based window restriction (max_turns pairs = 2 * max_turns messages)
        max_msg_limit = self.max_turns * 2
        pruned_chat = chat_msgs[-max_msg_limit:] if len(chat_msgs) > max_msg_limit else chat_msgs

        # 2. Token-based window pruning (traverse backwards from newest to oldest)
        accumulated_tokens = sum(self.estimate_tokens(m.content) for m in system_msgs)
        selected_chat: List[ChatMessage] = []

        for msg in reversed(pruned_chat):
            msg_tokens = self.estimate_tokens(msg.content)
            if accumulated_tokens + msg_tokens > self.max_tokens:
                logger.info(
                    f"[{self.session_id}] Sliding window token limit hit ({accumulated_tokens}/{self.max_tokens}). "
                    f"Pruned older message."
                )
                break
            selected_chat.insert(0, msg)
            accumulated_tokens += msg_tokens

        final_history = system_msgs + selected_chat
        return [msg.to_dict() for msg in final_history]

    def clear_memory(self) -> None:
        """Resets conversation history for active session."""
        self.thread.messages.clear()
        logger.info(f"Cleared memory for session: {self.session_id}")

    def get_stats(self) -> Dict[str, Any]:
        """Returns diagnostic statistics about memory usage."""
        total_msgs = len(self.thread.messages)
        pruned_history = self.get_sliding_window_history()
        total_est_tokens = sum(self.estimate_tokens(m.content) for m in self.thread.messages)
        active_est_tokens = sum(self.estimate_tokens(m.get("content", "")) for m in pruned_history)

        return {
            "session_id": self.session_id,
            "total_messages_stored": total_msgs,
            "active_window_messages": len(pruned_history),
            "total_estimated_tokens": total_est_tokens,
            "active_window_tokens": active_est_tokens,
            "max_allowed_turns": self.max_turns,
            "max_allowed_tokens": self.max_tokens,
        }
