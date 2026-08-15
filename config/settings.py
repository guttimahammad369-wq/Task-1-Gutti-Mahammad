import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Centralized configuration settings for the AI Conversational Analytics Assistant."""

    # Project directory
    BASE_DIR: Path = field(
        default_factory=lambda: Path(__file__).resolve().parent.parent
    )

    # API credentials and LLM configuration
    GEMINI_API_KEY: str = field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY", "")
    )

    OPENAI_API_KEY: str = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", "")
    )

    PRIMARY_LLM_MODEL: str = field(
        default_factory=lambda: os.getenv(
            "LLM_MODEL",
            "gemini-flash-latest",
        )
    )

    LLM_TEMPERATURE: float = 0.2

    MAX_OUTPUT_TOKENS: int = 1500

    # Memory configuration
    MAX_MEMORY_TURNS: int = 10

    MAX_HISTORY_TOKENS: int = 3000

    # Logging configuration
    LOG_LEVEL: str = field(
        default_factory=lambda: os.getenv(
            "LOG_LEVEL",
            "INFO",
        )
    )

    LOG_FILE_PATH: Path = field(
        default_factory=lambda: (
            Path(__file__).resolve().parent.parent
            / "app.log"
        )
    )

    def validate(self) -> None:
        """Validate required environment configuration."""

        if not self.GEMINI_API_KEY and not self.OPENAI_API_KEY:
            raise ValueError(
                "API Key missing! Please set GEMINI_API_KEY "
                "or OPENAI_API_KEY in your .env file."
            )


settings = Settings()
