"""Utilities for loading configuration files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from ..specs.models import StyleTokens


def load_style_tokens(path: Path) -> StyleTokens:
    """Load style tokens from a JSON file."""

    data = json.loads(path.read_text(encoding="utf-8"))
    return StyleTokens.model_validate(data)


def load_defaults(path: Path) -> dict[str, Any]:
    """Load global defaults from a YAML file."""

    if not path.exists():
        return {}
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return raw or {}
