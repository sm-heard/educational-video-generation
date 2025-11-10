"""Pydantic models describing lesson specifications."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, ConfigDict


class StyleTokens(BaseModel):
    """Visual identity tokens shared across scenes."""

    model_config = ConfigDict(extra="ignore")

    name: str = "default"
    fonts: dict[str, dict[str, Any]] = Field(
        default_factory=lambda: {
            "title": {"family": "Inter", "size": 40},
            "heading": {"family": "Inter", "size": 32},
            "body": {"family": "Inter", "size": 24},
            "caption": {"family": "Inter", "size": 20},
        }
    )
    colors: dict[str, str] = Field(
        default_factory=lambda: {
            "background": "#0B0F19",
            "text": "#F6F8FF",
            "accent_primary": "#3498DB",
            "accent_secondary": "#E74C3C",
            "highlight": "#F1C40F",
            "neutral": "#95A5A6",
        }
    )
    transitions: dict[str, Any] = Field(
        default_factory=lambda: {"duration_ms": 300, "easing": "ease_in_out"}
    )
    layout: dict[str, Any] = Field(
        default_factory=lambda: {
            "title_y": 3.2,
            "formula_x": 5.2,
            "safe_margin": 0.3,
        }
    )


class NarrationChunk(BaseModel):
    """Narration text with optional timing data."""

    text: str
    duration_seconds: float = Field(default=6.0, ge=0.0)
    start_seconds: float | None = Field(default=None, ge=0.0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Event(BaseModel):
    """Animation or visual event aligned to narration."""

    id: str
    at_seconds: float = Field(ge=0.0)
    type: str
    payload: dict[str, Any] = Field(default_factory=dict)


class SceneSpec(BaseModel):
    """A single instructional scene."""

    id: str
    title: str
    summary: str
    duration_target: float = Field(default=30.0, gt=0.0)
    narration: list[NarrationChunk] = Field(default_factory=list)
    events: list[Event] = Field(default_factory=list)
    preview_only: bool = False


class LessonSpec(BaseModel):
    """Top-level lesson specification derived from a prompt."""

    model_config = ConfigDict(extra="ignore")

    lesson_id: str
    topic: str
    prompt: str
    target_audience: str = "17-year-old physics students"
    style: StyleTokens = Field(default_factory=StyleTokens)
    scenes: list[SceneSpec] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TimelineEvent(BaseModel):
    """Resolved timeline entry for rendering and QA."""

    scene_id: str
    event_id: str
    at_seconds: float
    payload: dict[str, Any] = Field(default_factory=dict)


class Timeline(BaseModel):
    """Simple container for scheduled events."""

    scenes: list[str]
    events: list[TimelineEvent] = Field(default_factory=list)
