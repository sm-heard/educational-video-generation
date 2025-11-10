"""Streamlit interface for the educational video generator."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from ..config import load_defaults, load_style_tokens
from ..prompting.generator import generate_lesson_spec

DEFAULT_STYLE_PATH = Path("configs/style.json")
DEFAULT_DEFAULTS_PATH = Path("configs/defaults.yaml")


def render() -> None:
    st.set_page_config(page_title="Educational Video Generator", page_icon="🎬", layout="wide")
    st.title("Educational Video Generator")
    st.caption("Create structured lesson specs and review style tokens before rendering.")

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
        generate_button = st.button("Generate Lesson Spec", type="primary")

    if generate_button:
        if not prompt.strip():
            st.warning("Please add a prompt before generating a lesson specification.")
            st.stop()

        style_tokens = load_style_tokens(DEFAULT_STYLE_PATH)
        defaults = load_defaults(DEFAULT_DEFAULTS_PATH)
        lesson = generate_lesson_spec(prompt, style_tokens, defaults)

        st.success("Lesson specification generated. Review the details below.")

        st.subheader("Lesson Overview")
        st.write(
            {
                "lesson_id": lesson.lesson_id,
                "topic": lesson.topic,
                "voice": voice,
                "scene_count": len(lesson.scenes),
            }
        )

        st.subheader("Scenes")
        for scene in lesson.scenes:
            with st.expander(scene.title, expanded=True):
                st.write(
                    {
                        "scene_id": scene.id,
                        "summary": scene.summary,
                        "duration_target": scene.duration_target,
                    }
                )
                st.write("Narration", [chunk.text for chunk in scene.narration])
                st.write("Events", [event.model_dump() for event in scene.events])

        spec_json = lesson.model_dump_json(indent=2)
        st.download_button(
            "Download lesson.json",
            data=spec_json,
            file_name=f"{lesson.lesson_id}.lesson.json",
            mime="application/json",
        )

        if uploaded_assets:
            st.info(
                "Uploaded assets are not yet incorporated automatically. "
                "Save them alongside the lesson spec for future iterations.",
            )
            for asset in uploaded_assets:
                st.write(f"- {asset.name} ({asset.size} bytes)")
    else:
        _render_instructions()


def _render_instructions() -> None:
    st.markdown(
        """
        ### Workflow

        1. Provide a single prompt describing the learning objective.
        2. Generate the structured lesson specification.
        3. Use the CLI (`uv run video …`) to preview, render, and export frames.
        4. Iterate on the style tokens in `configs/style.json` for visual consistency.
        """
    )


if __name__ == "__main__":
    render()
