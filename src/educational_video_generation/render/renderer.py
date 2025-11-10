"""Placeholder rendering helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..specs.models import LessonSpec, Timeline


def render_preview(
    lesson: LessonSpec,
    timeline: Timeline,
    output_dir: Path,
    quality: str = "low",
) -> Path:
    """Create a preview placeholder file for the lesson."""

    preview_dir = output_dir / lesson.lesson_id / "preview"
    preview_dir.mkdir(parents=True, exist_ok=True)
    (preview_dir / "README.txt").write_text(
        _format_summary("preview", lesson, timeline, {"quality": quality}),
        encoding="utf-8",
    )
    return preview_dir


def render_final(
    lesson: LessonSpec,
    timeline: Timeline,
    output_dir: Path,
    quality: str = "high",
) -> Path:
    """Create a placeholder final render manifest."""

    final_dir = output_dir / lesson.lesson_id / "final"
    final_dir.mkdir(parents=True, exist_ok=True)
    (final_dir / "README.txt").write_text(
        _format_summary("final", lesson, timeline, {"quality": quality}),
        encoding="utf-8",
    )
    return final_dir


def export_static_frames(
    lesson: LessonSpec,
    timeline: Timeline,
    output_dir: Path,
) -> Path:
    """Create static frame placeholders used for QA."""

    frames_dir = output_dir / lesson.lesson_id / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    for idx, scene_id in enumerate(timeline.scenes, start=1):
        frame_path = frames_dir / f"scene_{idx:02d}_{scene_id}.txt"
        frame_path.write_text(
            f"Placeholder frame for scene {scene_id}. Add Manim renders here.",
            encoding="utf-8",
        )
    return frames_dir


def _format_summary(stage: str, lesson: LessonSpec, timeline: Timeline, extra: dict[str, Any]) -> str:
    return (
        f"Stage: {stage}\n"
        f"Lesson: {lesson.lesson_id}\n"
        f"Topic: {lesson.topic}\n"
        f"Scenes: {len(lesson.scenes)}\n"
        f"Events: {len(timeline.events)}\n"
        f"Extra: {extra}\n"
        "Replace this file with real render outputs once implemented.\n"
    )
