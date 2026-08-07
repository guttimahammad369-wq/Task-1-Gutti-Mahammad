from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Enumeration of message sender roles in LLM conversations."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(BaseModel):
    """Structured representation of a single conversation message."""

    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tokens: Optional[int] = None

    def to_dict(self) -> Dict[str, str]:
        """Converts message to standard LLM format dict: {'role': ..., 'content': ...}."""
        return {"role": self.role.value, "content": self.content}


class ConversationThread(BaseModel):
    """Container for an entire session conversation thread."""

    session_id: str
    messages: List[ChatMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def add_message(self, role: MessageRole, content: str, metadata: Optional[Dict[str, Any]] = None) -> ChatMessage:
        """Appends a new message to the thread and updates timestamp."""
        msg = ChatMessage(
            role=role,
            content=content,
            metadata=metadata or {},
        )
        self.messages.append(msg)
        self.updated_at = datetime.now()
        return msg

    def total_messages(self) -> int:
        """Returns total message count in thread."""
        return len(self.messages)
