import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union
import pandas as pd

from config.settings import settings
from utils.logger import logger


@dataclass
class DatasetMetadata:
    """Encapsulates metadata and schema context of the loaded dataset.

    Used to inform the LLM about dataset structure without passing raw rows.
    """

    num_rows: int
    num_columns: int
    columns: List[str]
    column_dtypes: Dict[str, str]
    categorical_values: Dict[str, List[str]]
    date_range: Dict[str, str]
    numeric_summaries: Dict[str, Dict[str, float]]
    null_counts: Dict[str, int]

    def to_system_prompt_context(self) -> str:
        """Formats dataset metadata into a clear context block for LLM system prompts.

        Returns:
            str: Formatted markdown representation of the dataset schema.
        """
        lines = [
            "### DATASET SCHEMA & CONTEXT",
            f"- **Total Records**: {self.num_rows:,} rows",
            f"- **Total Columns**: {self.num_columns}",
            f"- **Date Range**: {self.date_range.get('min', 'N/A')} to {self.date_range.get('max', 'N/A')}",
            "",
            "#### Available Columns & Types:",
        ]

        for col, dtype in self.column_dtypes.items():
            null_info = f" ({self.null_counts[col]} nulls)" if self.null_counts.get(col, 0) > 0 else ""
            lines.append(f"  - `{col}` ({dtype}){null_info}")

        if self.categorical_values:
            lines.append("\n#### Categorical Column Values:")
            for col, vals in self.categorical_values.items():
                val_str = ", ".join(f"'{v}'" for v in vals[:10])
                suffix = "..." if len(vals) > 10 else ""
                lines.append(f"  - `{col}`: [{val_str}{suffix}]")

        return "\n".join(lines)


class DataLoader:
    """Handles Excel and CSV dataset ingestion, validation, and metadata extraction."""

    def __init__(self, file_path: Optional[Union[str, Path]] = None):
        """Initializes DataLoader with a file path or falls back to default dataset.

        Args:
            file_path: Path to Excel or CSV file.
        """
        self.file_path = Path(file_path) if file_path else settings.DEFAULT_DATASET_PATH
        self.df: Optional[pd.DataFrame] = None
        self.metadata: Optional[DatasetMetadata] = None

    def load_data(self) -> pd.DataFrame:
        """Loads and cleans the dataset from the file path.

        Returns:
            pd.DataFrame: Cleaned Pandas DataFrame.

        Raises:
            FileNotFoundError: If the file path does not exist.
            ValueError: If file format is unsupported or file is empty.
        """
        if not self.file_path.exists():
            logger.error(f"Dataset file not found at: {self.file_path}")
            raise FileNotFoundError(f"File not found: {self.file_path}")

        logger.info(f"Ingesting dataset from: {self.file_path.name}")

        try:
            if self.file_path.suffix.lower() in [".xlsx", ".xls"]:
                self.df = pd.read_excel(self.file_path)
            elif self.file_path.suffix.lower() == ".csv":
                self.df = pd.read_csv(self.file_path)
            else:
                raise ValueError(f"Unsupported file format: {self.file_path.suffix}")

            if self.df.empty:
                raise ValueError("Loaded dataset is empty.")

            # Apply data sanitization
            self._sanitize_data()
            # Extract metadata for LLM prompt context
            self.metadata = self._extract_metadata()

            logger.info(
                f"Successfully ingested {len(self.df):,} rows and {len(self.df.columns)} columns."
            )
            return self.df

        except Exception as e:
            logger.error(f"Error loading dataset: {e}", exc_info=True)
            raise

    def _sanitize_data(self) -> None:
        """Sanitizes raw dataframe columns, handles missing values, and casts types."""
        if self.df is None:
            return

        # Strip whitespace from column names
        self.df.columns = [str(col).strip() for col in self.df.columns]

        # Strip leading/trailing whitespaces in string columns
        for col in self.df.select_dtypes(include=["object"]).columns:
            self.df[col] = self.df[col].astype(str).str.strip()

        # Handle Date parsing
        if "Date" in self.df.columns:
            self.df["Date"] = pd.to_datetime(self.df["Date"], errors="coerce")

        # Cast numeric fields safely
        numeric_cols = ["Quantity", "UnitPrice", "TotalPrice", "ItemsInCart"]
        for col in numeric_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors="coerce")

        # Clean CouponCode missing values
        if "CouponCode" in self.df.columns:
            self.df["CouponCode"] = self.df["CouponCode"].replace(["nan", "None", ""], "NO_COUPON")
            self.df["CouponCode"] = self.df["CouponCode"].fillna("NO_COUPON")

    def _extract_metadata(self) -> DatasetMetadata:
        """Extracts dataset schema and structural metadata for LLM context."""
        assert self.df is not None, "DataFrame must be loaded before extracting metadata."

        col_dtypes = {col: str(dtype) for col, dtype in self.df.dtypes.items()}
        null_counts = self.df.isnull().sum().to_dict()

        # Extract unique values for key categorical columns
        categorical_cols = ["Product", "PaymentMethod", "OrderStatus", "ReferralSource", "CouponCode"]
        categorical_values = {}
        for col in categorical_cols:
            if col in self.df.columns:
                unique_vals = self.df[col].dropna().unique().tolist()
                categorical_values[col] = [str(v) for v in sorted(unique_vals)]

        # Extract Date range
        date_range = {}
        if "Date" in self.df.columns and not self.df["Date"].isnull().all():
            date_range["min"] = self.df["Date"].min().strftime("%Y-%m-%d")
            date_range["max"] = self.df["Date"].max().strftime("%Y-%m-%d")

        # Extract basic numerical summaries
        numeric_summaries = {}
        numeric_df = self.df.select_dtypes(include=["number"])
        for col in numeric_df.columns:
            numeric_summaries[col] = {
                "min": float(numeric_df[col].min()),
                "max": float(numeric_df[col].max()),
                "mean": round(float(numeric_df[col].mean()), 2),
                "sum": round(float(numeric_df[col].sum()), 2),
            }

        return DatasetMetadata(
            num_rows=len(self.df),
            num_columns=len(self.df.columns),
            columns=list(self.df.columns),
            column_dtypes=col_dtypes,
            categorical_values=categorical_values,
            date_range=date_range,
            numeric_summaries=numeric_summaries,
            null_counts=null_counts,
        )


# Global singleton instance for single dataset loading
data_loader = DataLoader()
