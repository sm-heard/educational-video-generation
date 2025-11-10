"""Prompt expansion package."""

from .generator import generate_lesson_spec
from .service import PromptExpansionService
from .stub import build_stub_lesson

__all__ = ["generate_lesson_spec", "build_stub_lesson", "PromptExpansionService"]
