from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass
class DashboardConfig:
    """A class to design the Dashboard."""

    title: str = "📊 Data Dashboard"
    layout: Literal["wide", "centered"] = "wide"
    default_data_path: Path | None = None
    numeric_cols_only: bool = False
