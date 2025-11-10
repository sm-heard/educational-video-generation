"""Placeholder text-to-speech helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..specs.models import LessonSpec


def synthesize_narration(
    lesson: LessonSpec,
    output_dir: Path,
    voice: str = "ballad",
) -> Path:
    """Create a placeholder manifest representing synthesized narration."""

    narration_dir = output_dir / lesson.lesson_id / "audio"
    narration_dir.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, Any] = {
        "voice": voice,
        "scenes": [],
    }

    for scene in lesson.scenes:
        scene_chunks = [
            {
                "text": chunk.text,
                "duration_seconds": chunk.duration_seconds,
            }
            for chunk in scene.narration
        ]
        manifest["scenes"].append({"scene_id": scene.id, "chunks": scene_chunks})

    manifest_path = narration_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest_path
