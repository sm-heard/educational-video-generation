"""Prompt expansion utilities."""

from __future__ import annotations

from datetime import datetime
import itertools
from pathlib import Path
from typing import Any

from ..specs.models import Event, LessonSpec, NarrationChunk, SceneSpec, StyleTokens


def generate_lesson_spec(
    prompt: str,
    style: StyleTokens,
    defaults: dict[str, Any] | None = None,
) -> LessonSpec:
    """Create a structured lesson specification from a free-form prompt."""

    defaults = defaults or {}
    lesson_id = _slugify(defaults.get("lesson_id_prefix", "lesson"), prompt)
    topic = defaults.get("topic", prompt.title())

    base_scene_templates = [
        {
            "title": "Introduction",
            "summary": "Hook the learner and preview the key questions we will answer.",
        },
        {
            "title": "Concept Walkthrough",
            "summary": "Explain the core idea with supporting visuals and definitions.",
        },
        {
            "title": "Worked Example",
            "summary": "Apply the idea to a concrete physics problem with step-by-step narration.",
        },
    ]

    scenes: list[SceneSpec] = []
    for index, template in enumerate(base_scene_templates, start=1):
        narration = [
            NarrationChunk(
                text=f"{template['title']}: Placeholder narration tied to '{prompt}'.",
                duration_seconds=defaults.get("default_chunk_duration", 6.0),
            ),
            NarrationChunk(
                text="Additional supporting narration for visuals.",
                duration_seconds=defaults.get("default_chunk_duration", 6.0),
            ),
        ]
        events = [
            Event(
                id=f"{lesson_id}_scene{index}_event{event_index}",
                at_seconds=event_index * defaults.get("event_spacing", 3.0),
                type="show_text" if event_index == 0 else "highlight",
                payload={
                    "text": chunk.text,
                    "style": "body" if event_index else "title",
                },
            )
            for event_index, chunk in enumerate(narration)
        ]

        scene = SceneSpec(
            id=f"{lesson_id}_scene{index}",
            title=template["title"],
            summary=template["summary"],
            narration=narration,
            events=events,
            duration_target=defaults.get("default_scene_duration", 30.0),
        )
        scenes.append(scene)

    metadata = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "source_prompt": prompt,
        "assets": [],
    }

    return LessonSpec(
        lesson_id=lesson_id,
        topic=topic,
        prompt=prompt,
        style=style,
        scenes=scenes,
        metadata=metadata,
    )


def _slugify(prefix: str, prompt: str) -> str:
    words = ["".join(filter(str.isalnum, part.lower())) for part in prompt.split()]
    slug_core = "-".join(itertools.islice((w for w in words if w), 5)) or "lesson"
    return "-".join(filter(None, [prefix, slug_core]))
