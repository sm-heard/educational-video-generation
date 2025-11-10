"""Derive simple timelines from lesson specifications."""

from __future__ import annotations

from typing import Iterable

from ..specs.models import Event, LessonSpec, Timeline, TimelineEvent


def build_timeline(lesson: LessonSpec) -> Timeline:
    """Create a naive timeline by copying scene events in order."""

    ordered_scene_ids = [scene.id for scene in lesson.scenes]
    events = [
        TimelineEvent(
            scene_id=scene.id,
            event_id=event.id,
            at_seconds=event.at_seconds,
            payload=event.payload,
        )
        for scene in lesson.scenes
        for event in _sorted_events(scene.events)
    ]
    return Timeline(scenes=ordered_scene_ids, events=events)


def _sorted_events(events: Iterable[Event]) -> list[Event]:
    return sorted(events, key=lambda e: e.at_seconds)
