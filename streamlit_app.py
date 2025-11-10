"""Entry point for Streamlit Cloud deployments."""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv


def _ensure_src_on_path() -> None:
    project_root = Path(__file__).resolve().parent
    src_dir = project_root / "src"
    if src_dir.exists():
        sys.path.insert(0, str(src_dir))


_ensure_src_on_path()

load_dotenv()

from educational_video_generation.ui.app import render


if __name__ == "__main__":
    render()
