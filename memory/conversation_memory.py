import uuid
from typing import Any, Dict, List, Optional

from config.settings import settings
from models.chat_models import ChatMessage, ConversationThread, MessageRole
from utils.logger import logger


class ConversationMemoryManager:
    """
    Stateful conversation memory manager with sliding-window pruning.

    Stores role-based chat messages in structured objects and provides
    context preservation with dynamic sliding-window context pruning.

    The active history supports:

        User -> Assistant
        User -> Assistant
        User -> Assistant
        User (current pending request)

    The final User message is allowed to exist without an Assistant
    response because generate_response() adds the user message before
    calling the LLM.
    """

    def __init__(
        self,
        session_id: Optional[str] = None,
        max_turns: int = settings.MAX_MEMORY_TURNS,
        max_tokens: int = settings.MAX_HISTORY_TOKENS,
    ):
        """
        Initializes conversation memory for a session.

        Args:
            session_id:
                Unique session identifier. Defaults to a new UUID.

            max_turns:
                Maximum number of completed user-assistant pairs
                retained in the active context.

            max_tokens:
                Maximum estimated token budget for the active context.
        """

        self.session_id = session_id or str(uuid.uuid4())
        self.max_turns = max(0, max_turns)
        self.max_tokens = max(0, max_tokens)

        self.thread = ConversationThread(
            session_id=self.session_id
        )

        logger.info(
            f"Initialized ConversationMemoryManager "
            f"for session: {self.session_id}"
        )

    # =========================================================
    # MESSAGE MANAGEMENT
    # =========================================================

    def add_user_message(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ChatMessage:
        """Appends a new user message to conversation history."""

        if not isinstance(content, str):
            raise TypeError("User message content must be a string.")

        content = content.strip()

        if not content:
            raise ValueError("User message cannot be empty.")

        msg = self.thread.add_message(
            MessageRole.USER,
            content,
            metadata,
        )

        logger.debug(
            f"[{self.session_id}] "
            f"Added User message: '{content[:50]}...'"
        )

        return msg

    def add_assistant_message(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ChatMessage:
        """Appends a new assistant message to conversation history."""

        if not isinstance(content, str):
            raise TypeError(
                "Assistant message content must be a string."
            )

        content = content.strip()

        if not content:
            raise ValueError(
                "Assistant message cannot be empty."
            )

        msg = self.thread.add_message(
            MessageRole.ASSISTANT,
            content,
            metadata,
        )

        logger.debug(
            f"[{self.session_id}] "
            f"Added Assistant message: '{content[:50]}...'"
        )

        return msg

    def add_system_message(
        self,
        content: str,
    ) -> ChatMessage:
        """Appends a system message to conversation history."""

        if not isinstance(content, str):
            raise TypeError(
                "System message content must be a string."
            )

        content = content.strip()

        if not content:
            raise ValueError(
                "System message cannot be empty."
            )

        msg = self.thread.add_message(
            MessageRole.SYSTEM,
            content,
        )

        return msg

    # =========================================================
    # TOKEN ESTIMATION
    # =========================================================

    def estimate_tokens(
        self,
        text: str,
    ) -> int:
        """
        Estimates token count using a simple character heuristic.

        Rule of thumb:

            approximately 1 token ≈ 4 characters.

        This is only an estimate and is not a replacement for
        the tokenizer used by the actual LLM.
        """

        if not text:
            return 0

        return max(
            1,
            int(len(text) / 4),
        )

    # =========================================================
    # SLIDING WINDOW
    # =========================================================

    def get_sliding_window_history(
        self,
    ) -> List[Dict[str, str]]:
        """
        Returns the bounded conversation history for the LLM.

        The algorithm handles both:

        1. Completed conversation turns:

               User
               Assistant

        2. The current pending user request:

               User

        The pending user message is important because
        generate_response() stores the user's message before
        requesting the LLM response.

        Rules:

        1. System messages are preserved at the beginning.
        2. At most max_turns completed user-assistant pairs
           are retained.
        3. A newest pending user message is preserved.
        4. Older conversation turns are processed from newest
           to oldest.
        5. User-assistant pairs are never split.
        6. Token pruning removes the oldest complete pairs first.
        7. The current user request is preserved even if it alone
           exceeds the configured token budget.
        """

        all_messages = self.thread.messages

        if not all_messages:
            return []

        # -----------------------------------------------------
        # Separate system messages from conversation messages
        # -----------------------------------------------------

        system_msgs = [
            message
            for message in all_messages
            if message.role == MessageRole.SYSTEM
        ]

        chat_msgs = [
            message
            for message in all_messages
            if message.role != MessageRole.SYSTEM
        ]

        if not chat_msgs:
            return [
                message.to_dict()
                for message in system_msgs
            ]

        # -----------------------------------------------------
        # Calculate tokens already used by system messages
        # -----------------------------------------------------

        accumulated_tokens = sum(
            self.estimate_tokens(message.content)
            for message in system_msgs
        )

        selected_chat: List[ChatMessage] = []

        # -----------------------------------------------------
        # Detect the newest message
        # -----------------------------------------------------
        #
        # During generate_response():
        #
        #   add_user_message()
        #          ↓
        #   get_sliding_window_history()
        #
        # Therefore the newest message can legitimately be:
        #
        #   User
        #
        # without an Assistant response yet.
        # -----------------------------------------------------

        index = len(chat_msgs) - 1

        pending_user_message: Optional[ChatMessage] = None

        if (
            index >= 0
            and chat_msgs[index].role == MessageRole.USER
        ):
            pending_user_message = chat_msgs[index]

            index -= 1

        # -----------------------------------------------------
        # Apply completed-turn limit
        # -----------------------------------------------------
        #
        # We intentionally do NOT slice chat_msgs[-max_turns * 2:]
        # because doing that can begin in the middle of a pair.
        #
        # Example:
        #
        #   U A U A U A U
        #
        # A naive last-6 slice produces:
        #
        #   A U A U A U
        #
        # which is malformed.
        #
        # Instead, we count complete pairs from newest to oldest.
        # -----------------------------------------------------

        completed_pairs_selected = 0

        # -----------------------------------------------------
        # Preserve current pending user message
        # -----------------------------------------------------

        if pending_user_message is not None:
            pending_tokens = self.estimate_tokens(
                pending_user_message.content
            )

            selected_chat.append(
                pending_user_message
            )

            accumulated_tokens += pending_tokens

        # -----------------------------------------------------
        # Select completed User -> Assistant pairs
        # -----------------------------------------------------

        while (
            index >= 1
            and completed_pairs_selected < self.max_turns
        ):
            assistant_msg = chat_msgs[index]
            user_msg = chat_msgs[index - 1]

            # -------------------------------------------------
            # Validate conversation pair
            # -------------------------------------------------

            if (
                user_msg.role != MessageRole.USER
                or assistant_msg.role != MessageRole.ASSISTANT
            ):
                logger.warning(
                    f"[{self.session_id}] "
                    "Encountered an incomplete or malformed "
                    "conversation pair during pruning. "
                    "Stopping older-history traversal."
                )

                break

            pair_tokens = (
                self.estimate_tokens(
                    user_msg.content
                )
                + self.estimate_tokens(
                    assistant_msg.content
                )
            )

            # -------------------------------------------------
            # Token budget check
            # -------------------------------------------------

            if (
                accumulated_tokens + pair_tokens
                > self.max_tokens
            ):
                logger.info(
                    f"[{self.session_id}] "
                    "Sliding window token limit hit "
                    f"({accumulated_tokens}/"
                    f"{self.max_tokens}). "
                    "Pruned older message pair."
                )

                break

            # -------------------------------------------------
            # Insert pair at the beginning.
            #
            # We traverse newest -> oldest, so inserting at
            # index 0 restores chronological order.
            # -------------------------------------------------

            selected_chat.insert(
                0,
                assistant_msg,
            )

            selected_chat.insert(
                0,
                user_msg,
            )

            accumulated_tokens += pair_tokens

            completed_pairs_selected += 1

            index -= 2

        # -----------------------------------------------------
        # Final history
        # -----------------------------------------------------
        #
        # System messages:
        #
        #   System
        #
        # followed by:
        #
        #   User
        #   Assistant
        #   User
        #   Assistant
        #   User (current request)
        # -----------------------------------------------------

        final_history = (
            system_msgs + selected_chat
        )

        return [
            message.to_dict()
            for message in final_history
        ]

    # =========================================================
    # CLEAR MEMORY
    # =========================================================

    def clear_memory(self) -> None:
        """Resets conversation history for the active session."""

        self.thread.messages.clear()

        logger.info(
            f"Cleared memory for session: "
            f"{self.session_id}"
        )

    # =========================================================
    # MEMORY STATISTICS
    # =========================================================

    def get_stats(
        self,
    ) -> Dict[str, Any]:
        """
        Returns diagnostic statistics about memory usage.
        """

        total_msgs = len(
            self.thread.messages
        )

        pruned_history = (
            self.get_sliding_window_history()
        )

        total_est_tokens = sum(
            self.estimate_tokens(
                message.content
            )
            for message in self.thread.messages
        )

        active_est_tokens = sum(
            self.estimate_tokens(
                message.get("content", "")
            )
            for message in pruned_history
        )

        return {
            "session_id": self.session_id,
            "total_messages_stored": total_msgs,
            "active_window_messages": len(
                pruned_history
            ),
            "total_estimated_tokens": total_est_tokens,
            "active_window_tokens": active_est_tokens,
            "max_allowed_turns": self.max_turns,
            "max_allowed_tokens": self.max_tokens,
        }