"""Services for expanding prompts into lesson specifications."""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

from ..specs.models import LessonSpec, StyleTokens
from .stub import build_stub_lesson

try:  # pragma: no cover - optional dependency during tests
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore


class PromptExpansionService:
    """Generate structured lesson specifications using OpenAI responses."""

    def __init__(
        self,
        *,
        model: str = "gpt-4o-mini",
        dry_run: bool | None = None,
    ) -> None:
        self.model = model
        api_key = os.getenv("OPENAI_API_KEY")
        self.dry_run = dry_run if dry_run is not None else not api_key
        if not self.dry_run and OpenAI is None:
            raise RuntimeError("openai package is required but not installed")
        self._client = None if self.dry_run else OpenAI()

    def expand_prompt(
        self,
        prompt: str,
        *,
        style: StyleTokens,
        defaults: dict[str, Any],
    ) -> LessonSpec:
        if self.dry_run or self._client is None:
            return build_stub_lesson(prompt=prompt, style=style, defaults=defaults)

        system_prompt = (
            "You are an instructional designer creating educational physics videos for 17-year-old "
            "students. Return JSON that matches the provided schema. Ensure narration chunks are "
            "concise (<= 3 sentences) and include timelines for visuals."
        )

        response = self._client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": [{"type": "text", "text": system_prompt}],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": _build_user_prompt(prompt, style, defaults),
                        }
                    ],
                },
            ],
            response_format={"type": "json_object"},
        )

        raw_json = response.output_text  # type: ignore[attr-defined]
        payload = json.loads(raw_json)

        payload.setdefault("lesson_id", defaults.get("lesson_id_prefix", "lesson"))
        payload.setdefault("topic", prompt.title())
        payload.setdefault("prompt", prompt)
        payload.setdefault("style", style.model_dump())
        payload.setdefault(
            "metadata",
            {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "source_prompt": prompt,
                "assets": [],
            },
        )

        return LessonSpec.model_validate(payload)


def _build_user_prompt(prompt: str, style: StyleTokens, defaults: dict[str, Any]) -> str:
    return (
        "PROMPT:\n"
        f"{prompt}\n\n"
        "STYLE TOKENS:\n"
        f"{json.dumps(style.model_dump(), indent=2)}\n\n"
        "DEFAULTS:\n"
        f"{json.dumps(defaults, indent=2)}\n\n"
        "REQUIREMENTS:\n"
        "- Provide between 3 and 4 scenes covering introduction, concept, and worked example.\n"
        "- Each scene needs narration chunks with duration estimates and corresponding visual events.\n"
        "- Use consistent identifiers (scene_id, event_id) derived from the lesson topic.\n"
        "- Include on-screen text, equations, or diagram notes as part of the payload for events.\n"
        "- Ensure narration matches the pacing targets from defaults.\n"
        "Return only JSON.""
    )
