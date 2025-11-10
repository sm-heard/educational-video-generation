"""Rendering helpers that convert lesson specs into videos via Manim."""

from __future__ import annotations

import json
import textwrap
from contextlib import ExitStack
from pathlib import Path
from typing import Any

from manim import (
    DOWN,
    LEFT,
    UP,
    FadeIn,
    FadeOut,
    Scene,
    SurroundingRectangle,
    Text,
    VGroup,
    tempconfig,
)
from moviepy import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip

from ..specs.models import LessonSpec, SceneSpec, StyleTokens, Timeline

QUALITY_PRESETS: dict[str, dict[str, int]] = {
    "low": {"pixel_width": 640, "pixel_height": 360, "frame_rate": 15},
    "medium": {"pixel_width": 1280, "pixel_height": 720, "frame_rate": 30},
    "high": {"pixel_width": 1920, "pixel_height": 1080, "frame_rate": 30},
}


def render_preview(
    lesson: LessonSpec,
    timeline: Timeline,
    output_dir: Path,
    quality: str = "low",
    audio_manifest: Path | None = None,
) -> Path:
    """Render each scene as a low-resolution preview clip."""

    preview_dir = output_dir / lesson.lesson_id / "preview"
    preview_dir.mkdir(parents=True, exist_ok=True)

    audio_index = _load_audio_manifest(audio_manifest)
    scene_files = _render_scenes(
        lesson,
        preview_dir,
        quality=quality,
        audio_index=audio_index,
    )

    manifest_path = preview_dir / "preview_manifest.json"
    manifest_data = {
        "videos": [str(path.relative_to(output_dir)) for path in scene_files],
        "quality": quality,
    }
    manifest_path.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")
    return preview_dir


def render_final(
    lesson: LessonSpec,
    timeline: Timeline,
    output_dir: Path,
    quality: str = "high",
    audio_manifest: Path | None = None,
) -> Path:
    """Render high-quality scene clips and concatenate them into a final MP4."""

    final_dir = output_dir / lesson.lesson_id / "final"
    final_dir.mkdir(parents=True, exist_ok=True)

    audio_index = _load_audio_manifest(audio_manifest)
    scene_files = _render_scenes(
        lesson,
        final_dir,
        quality=quality,
        audio_index=audio_index,
    )

    final_video = final_dir / f"{lesson.lesson_id}.mp4"
    _concatenate_videos(scene_files, final_video)

    (final_dir / "final_manifest.json").write_text(
        json.dumps({"final_video": str(final_video.relative_to(output_dir))}, indent=2),
        encoding="utf-8",
    )
    return final_dir


def export_static_frames(
    lesson: LessonSpec,
    timeline: Timeline,
    output_dir: Path,
) -> Path:
    """Extract representative frames from preview videos for QA."""

    frames_dir = output_dir / lesson.lesson_id / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    preview_dir = output_dir / lesson.lesson_id / "preview"
    previews = sorted(preview_dir.glob("scene_*.mp4"))

    if not previews:
        # No preview videos available. Leave informational files to prompt rerun.
        for idx, scene_id in enumerate(timeline.scenes, start=1):
            frame_path = frames_dir / f"scene_{idx:02d}_{scene_id}.txt"
            frame_path.write_text(
                "Preview renders missing. Run `video preview` before exporting frames.",
                encoding="utf-8",
            )
        return frames_dir

    for idx, video_path in enumerate(previews, start=1):
        frame_path = frames_dir / f"scene_{idx:02d}.png"
        with VideoFileClip(str(video_path)) as clip:
            timestamp = min(max(clip.duration / 2, 0.1), clip.duration - 0.1)
            clip.save_frame(str(frame_path), t=timestamp)

    return frames_dir


def _render_scenes(
    lesson: LessonSpec,
    target_dir: Path,
    *,
    quality: str,
    audio_index: dict[str, list[dict[str, Any]]],
) -> list[Path]:
    scene_paths: list[Path] = []
    style = lesson.style
    preset = QUALITY_PRESETS.get(quality, QUALITY_PRESETS["low"])

    for order, scene_spec in enumerate(lesson.scenes, start=1):
        output_path = target_dir / f"scene_{order:02d}_{scene_spec.id}.mp4"
        _render_scene_to_file(
            scene_spec,
            style,
            audio_index.get(scene_spec.id, []),
            output_path,
            preset,
        )
        scene_paths.append(output_path)

    return scene_paths


def _render_scene_to_file(
    scene_spec: SceneSpec,
    style: StyleTokens,
    audio_chunks: list[dict[str, Any]],
    output_path: Path,
    preset: dict[str, int],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path = output_path.resolve()

    scene_class = _build_scene_class(scene_spec, style, audio_chunks)

    with tempconfig(
        {
            "write_to_movie": True,
            "save_last_frame": False,
            "media_dir": str(output_path.parent),
            "video_dir": str(output_path.parent),
            "images_dir": str(output_path.parent / "frames"),
            "output_file": output_path.stem,
            "pixel_width": preset["pixel_width"],
            "pixel_height": preset["pixel_height"],
            "frame_rate": preset["frame_rate"],
        }
    ):
        scene = scene_class()
        scene.render()
        movie_path = Path(scene.renderer.file_writer.movie_file_path).resolve()
        if movie_path != output_path:
            output_path.unlink(missing_ok=True)
            movie_path.rename(output_path)


def _build_scene_class(
    scene_spec: SceneSpec,
    style: StyleTokens,
    audio_chunks: list[dict[str, Any]],
):
    fonts = style.fonts or {}
    colors = style.colors or {}

    title_style = fonts.get("title", {"family": "Inter", "size": 40})
    body_style = fonts.get("body", {"family": "Inter", "size": 24})

    background_color = colors.get("background", "#0B0F19")
    text_color = colors.get("text", "#F6F8FF")
    highlight_color = colors.get("highlight", "#F1C40F")

    sorted_events = sorted(scene_spec.events, key=lambda event: event.at_seconds)

    class GeneratedScene(Scene):  # type: ignore[misc]
        def construct(self) -> None:  # noqa: D401 - internal helper
            self.camera.background_color = background_color

            for chunk in audio_chunks:
                file_path = chunk.get("abs_path") or chunk.get("file")
                if file_path:
                    offset = float(chunk.get("start_seconds", 0.0))
                    self.add_sound(str(file_path), time_offset=offset)

            title = Text(
                scene_spec.title,
                font=title_style.get("family"),
                font_size=title_style.get("size", 40),
                color=text_color,
                weight="BOLD",
            )
            title.to_edge(UP).shift(DOWN * 0.2)
            self.play(FadeIn(title, shift=DOWN, run_time=0.6))

            body_texts: list[VGroup] = []
            last_time = 0.0

            for index, event in enumerate(sorted_events, start=1):
                desired_time = float(event.at_seconds)
                pause = max(0.0, desired_time - last_time)
                if pause:
                    self.wait(pause)
                    last_time += pause

                event_text = event.payload.get("text") if event.payload else None
                if not event_text:
                    continue

                lines = textwrap.wrap(event_text, width=60) or [event_text]
                paragraph = VGroup(
                    *[
                        Text(
                            line,
                            font=body_style.get("family"),
                            font_size=body_style.get("size", 24),
                            color=text_color,
                        )
                        for line in lines
                    ]
                ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)

                paragraph.to_edge(LEFT).shift(DOWN * (0.5 + 1.1 * (index - 1)))
                self.play(FadeIn(paragraph, run_time=0.4))
                body_texts.append(paragraph)

                if event.type == "highlight":
                    highlight = SurroundingRectangle(
                        paragraph,
                        color=highlight_color,
                        buff=0.25,
                        stroke_width=3,
                    )
                    self.play(FadeIn(highlight, run_time=0.3))

                last_time = desired_time

            self.wait(0.75)

            for text_group in body_texts:
                self.play(FadeOut(text_group, run_time=0.2))
            self.play(FadeOut(title, run_time=0.3))

    GeneratedScene.__name__ = f"Scene_{scene_spec.id.replace('-', '_')}"
    return GeneratedScene


def _load_audio_manifest(path: Path | None) -> dict[str, list[dict[str, Any]]]:
    if not path or not path.exists():
        return {}

    data = json.loads(path.read_text(encoding="utf-8"))
    scenes = data.get("scenes", [])
    audio_root = path.parent

    result: dict[str, list[dict[str, Any]]] = {}
    for scene in scenes:
        scene_id = scene.get("scene_id")
        if not scene_id:
            continue
        entries: list[dict[str, Any]] = []
        for chunk in scene.get("chunks", []):
            relative = chunk.get("file")
            abs_path = audio_root / relative if relative else None
            entries.append({
                **chunk,
                "abs_path": abs_path,
            })
        result[scene_id] = entries
    return result


def _concatenate_videos(scene_paths: list[Path], output_path: Path) -> None:
    if not scene_paths:
        raise ValueError("No scene videos generated; cannot assemble final render.")

    clips = []
    with ExitStack() as stack:
        for path in scene_paths:
            clip = stack.enter_context(VideoFileClip(str(path)))
            clips.append(clip)
        final_clip = concatenate_videoclips(clips, method="compose")
        stack.enter_context(final_clip)
        final_clip.write_videofile(
            str(output_path),
            fps=clips[0].fps,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile=str(output_path.with_suffix(".temp-audio.m4a")),
            remove_temp=True,
            logger=None,
        )
