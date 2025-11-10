"""Prompt expansion utilities."""

from __future__ import annotations

from typing import Any

from ..specs.models import LessonSpec, StyleTokens
from .service import PromptExpansionService
from .stub import build_stub_lesson


def generate_lesson_spec(
    prompt: str,
    style: StyleTokens,
    defaults: dict[str, Any] | None = None,
    *,
    model: str | None = None,
    dry_run: bool | None = None,
) -> LessonSpec:
    """Create a structured lesson specification from a free-form prompt."""

    defaults = defaults or {}
    service = PromptExpansionService(model=model or "gpt-4o-mini", dry_run=dry_run)
    try:
        return service.expand_prompt(prompt, style=style, defaults=defaults)
    except Exception as exc:  # pragma: no cover - fallback path
        # Fall back to deterministic stub if OpenAI request fails or is unavailable.
        print(f"[prompting] Falling back to stub generator: {exc}")
        return build_stub_lesson(prompt=prompt, style=style, defaults=defaults)


__all__ = ["generate_lesson_spec", "build_stub_lesson"]
