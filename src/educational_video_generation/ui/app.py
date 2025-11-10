"""Streamlit interface for running the full educational video pipeline."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

import streamlit as st

from ..audio.tts import synthesize_narration
from ..config import load_defaults, load_style_tokens
from ..prompting.generator import generate_lesson_spec
from ..render.renderer import export_static_frames, render_final, render_preview
from ..timeline.scheduler import build_timeline

DEFAULT_STYLE_PATH = Path("configs/style.json")
DEFAULT_DEFAULTS_PATH = Path("configs/defaults.yaml")
DEFAULT_OUTPUT_DIR = Path("outputs")


def render() -> None:
    st.set_page_config(page_title="Educational Video Generator", page_icon="🎬", layout="wide")
    st.title("Educational Video Generator")
    st.caption("Supply a single prompt and produce previews, final MP4s, and QA frames.")

    with st.sidebar:
        st.header("Inputs")
        prompt = st.text_area(
            "Prompt",
            placeholder="Explain Newton's First Law with examples…",
            height=150,
        )
        uploaded_assets = st.file_uploader(
            "Optional supporting assets",
            accept_multiple_files=True,
            type=["png", "jpg", "jpeg", "svg", "json"],
        )
        voice = st.selectbox("Voice", options=["ballad"], index=0)
        preview_quality = st.selectbox(
            "Preview quality",
            options=["low", "medium", "high"],
            index=0,
        )
        final_quality = st.selectbox("Final quality", options=["high", "medium"], index=0)
        dry_run = st.checkbox(
            "Dry run (no OpenAI calls)",
            value=not bool(os.getenv("OPENAI_API_KEY")),
            help="Use deterministic stubs without hitting the OpenAI API.",
        )
        skip_frames = st.checkbox("Skip QA frames", value=False)
        output_dir = Path(st.text_input("Output directory", value=str(DEFAULT_OUTPUT_DIR)))
        run_button = st.button("Generate Video", type="primary")

    if not run_button:
        _render_instructions()
        return

    if not prompt.strip():
        st.warning("Please add a prompt before generating a lesson specification.")
        st.stop()

    output_dir.mkdir(parents=True, exist_ok=True)

    style_tokens = load_style_tokens(DEFAULT_STYLE_PATH)
    defaults = load_defaults(DEFAULT_DEFAULTS_PATH)

    with st.spinner("Generating lesson specification…"):
        lesson = generate_lesson_spec(
            prompt,
            style_tokens,
            defaults,
            dry_run=True if dry_run else None,
        )

    spec_path = output_dir / f"{lesson.lesson_id}.lesson.json"
    spec_path.write_text(lesson.model_dump_json(indent=2), encoding="utf-8")

    timeline = build_timeline(lesson)

    with st.spinner("Synthesising narration…"):
        manifest_path = synthesize_narration(
            lesson,
            output_dir,
            voice=voice,
            model="gpt-4o-mini-tts",
            dry_run=True if dry_run else None,
        )

    with st.spinner("Rendering preview clips…"):
        preview_dir = render_preview(
            lesson,
            timeline,
            output_dir,
            quality=preview_quality,
            audio_manifest=manifest_path,
        )

    with st.spinner("Rendering final video…"):
        final_dir = render_final(
            lesson,
            timeline,
            output_dir,
            quality=final_quality,
            audio_manifest=manifest_path,
        )
    final_video = final_dir / f"{lesson.lesson_id}.mp4"

    frames_dir = None
    if not skip_frames:
        with st.spinner("Exporting QA frames…"):
            frames_dir = export_static_frames(lesson, timeline, output_dir)

    st.success("Pipeline complete! Review artifacts below.")

    _render_overview(lesson, voice, dry_run)
    _render_downloads(spec_path, final_video, preview_dir, frames_dir)

    if uploaded_assets:
        st.info(
            "Uploaded assets are not yet incorporated automatically. "
            "Save them alongside the lesson spec for future iterations.",
        )
        _list_uploaded_assets(uploaded_assets)


def _render_instructions() -> None:
    st.markdown(
        """
        ### Workflow

        1. Provide a single prompt describing the learning objective.
        2. Click **Generate Video** to produce lesson specs, narration audio,
           preview clips, and the final MP4.
        3. Inspect the outputs in `outputs/<lesson_id>/` and iterate on style tokens
           in `configs/style.json` as needed.
        """
    )


def _render_overview(lesson, voice: str, dry_run: bool) -> None:
    st.subheader("Lesson Overview")
    st.write(
        {
            "lesson_id": lesson.lesson_id,
            "topic": lesson.topic,
            "voice": voice,
            "scene_count": len(lesson.scenes),
            "dry_run": dry_run,
        }
    )

    with st.expander(" Scenes", expanded=False):
        for scene in lesson.scenes:
            st.write(
                {
                    "scene_id": scene.id,
                    "title": scene.title,
                    "summary": scene.summary,
                    "duration_target": scene.duration_target,
                }
            )


def _render_downloads(
    spec_path: Path,
    final_video: Path,
    preview_dir: Path,
    frames_dir: Path | None,
) -> None:
    spec_json = spec_path.read_text(encoding="utf-8")
    st.download_button(
        "Download lesson.json",
        data=spec_json,
        file_name=spec_path.name,
        mime="application/json",
    )

    st.video(str(final_video))
    st.download_button(
        "Download final mp4",
        data=final_video.read_bytes(),
        file_name=final_video.name,
        mime="video/mp4",
    )

    with st.expander("Preview clips", expanded=False):
        clips = sorted(preview_dir.glob("scene_*.mp4"))
        if not clips:
            st.write("No preview clips found.")
        for clip in clips:
            st.write(f"- {clip}")

    if frames_dir:
        with st.expander("QA frames", expanded=False):
            frames = sorted(frames_dir.glob("*.png"))
            if not frames:
                st.write("No frames generated. Run previews first.")
            for frame in frames:
                st.write(f"- {frame}")


def _list_uploaded_assets(files: Iterable[st.runtime.uploaded_file_manager.UploadedFile]) -> None:
    for asset in files:
        st.write(f"- {asset.name} ({asset.size} bytes)")


if __name__ == "__main__":
    render()
