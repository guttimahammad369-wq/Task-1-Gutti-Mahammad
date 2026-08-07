import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

# Automatically locate and load environment variables from the root .env file
load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Centralized Configuration Settings for the AI Conversational Analytics Assistant.

    Provides immutable configuration parameters with sensible defaults.
    """

    # --- Project Directory Paths ---
    BASE_DIR: Path = field(
        default_factory=lambda: Path(__file__).resolve().parent.parent
    )
    DATA_DIR: Path = field(
        default_factory=lambda: Path(__file__).resolve().parent.parent / "data"
    )
    DEFAULT_DATASET_PATH: Path = field(
        default_factory=lambda: Path(__file__).resolve().parent.parent
        / "data"
        / "Dataset for Data Analytics (1).xlsx"
    )

    # --- API Credentials & LLM Configuration ---
    GEMINI_API_KEY: str = field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY", "")
    )
    OPENAI_API_KEY: str = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", "")
    )
    PRIMARY_LLM_MODEL: str = field(
        default_factory=lambda: os.getenv("LLM_MODEL", "gemini-flash-latest")
    )
    LLM_TEMPERATURE: float = 0.2
    MAX_OUTPUT_TOKENS: int = 1500

    # --- Memory & Context Window Configuration ---
    MAX_MEMORY_TURNS: int = 10  # Maximum user-assistant message pairs retained in memory
    MAX_HISTORY_TOKENS: int = 3000  # Token safety threshold for sliding window pruning

    # --- Application Logging Settings ---
    LOG_LEVEL: str = field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO")
    )
    LOG_FILE_PATH: Path = field(
        default_factory=lambda: Path(__file__).resolve().parent.parent
        / "app.log"
    )

    def validate(self) -> None:
        """Validates critical environment configurations.

        Raises:
            ValueError: If neither GEMINI_API_KEY nor OPENAI_API_KEY is found.
        """
        if not self.GEMINI_API_KEY and not self.OPENAI_API_KEY:
            raise ValueError(
                "API Key missing! Please set GEMINI_API_KEY or OPENAI_API_KEY in your .env file."
            )


# Global singleton instance for app-wide settings access
settings = Settings()
