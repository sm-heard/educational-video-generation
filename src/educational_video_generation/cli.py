"""Command line entry point."""

from __future__ import annotations

from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from .audio.tts import synthesize_narration
from .config import load_defaults, load_style_tokens
from .prompting.generator import generate_lesson_spec
from .render.renderer import export_static_frames, render_final, render_preview
from .specs.models import LessonSpec
from .timeline.scheduler import build_timeline

load_dotenv()


DEFAULT_STYLE_PATH = Path("configs/style.json")
DEFAULT_DEFAULTS_PATH = Path("configs/defaults.yaml")
DEFAULT_OUTPUT_DIR = Path("outputs")

app = typer.Typer(help="Educational video generation utilities.")
console = Console()


def _load_spec(path: Path) -> LessonSpec:
    return LessonSpec.model_validate_json(path.read_text(encoding="utf-8"))


def _display_spec(spec: LessonSpec) -> None:
    table = Table(title=f"Lesson: {spec.lesson_id}")
    table.add_column("Scene ID")
    table.add_column("Title")
    table.add_column("Duration Target")
    for scene in spec.scenes:
        table.add_row(scene.id, scene.title, f"{scene.duration_target:.1f}s")
    console.print(table)


@app.command()
def gen(
    prompt: str = typer.Argument(..., help="Single prompt describing the lesson."),
    style: Path = typer.Option(
        DEFAULT_STYLE_PATH,
        exists=True,
        file_okay=True,
        dir_okay=False,
        help="Path to the style tokens JSON file.",
    ),
    defaults: Path = typer.Option(
        DEFAULT_DEFAULTS_PATH,
        exists=False,
        help="Optional defaults YAML overriding duration, pacing, etc.",
    ),
    output_dir: Path = typer.Option(
        DEFAULT_OUTPUT_DIR,
        file_okay=False,
        help="Directory where generated specs are saved.",
    ),
    prompt_model: str = typer.Option(
        "gpt-4o-mini",
        help="OpenAI model used for prompt expansion.",
    ),
    dry_run: bool = typer.Option(
        False,
        help="Force offline stub generation even when an API key is available.",
    ),
) -> None:
    """Generate a structured lesson specification from a prompt."""

    output_dir.mkdir(parents=True, exist_ok=True)
    style_tokens = load_style_tokens(style)
    defaults_payload = load_defaults(defaults)
    lesson = generate_lesson_spec(
        prompt,
        style_tokens,
        defaults_payload,
        model=prompt_model,
        dry_run=True if dry_run else None,
    )
    spec_path = output_dir / f"{lesson.lesson_id}.lesson.json"
    spec_path.write_text(lesson.model_dump_json(indent=2), encoding="utf-8")

    console.print(f"[green]Saved lesson spec to {spec_path}")
    _display_spec(lesson)


@app.command()
def preview(
    spec: Path = typer.Argument(..., exists=True, help="Path to a lesson spec JSON file."),
    output_dir: Path = typer.Option(
        DEFAULT_OUTPUT_DIR,
        file_okay=False,
        help="Directory for preview artifacts.",
    ),
    quality: str = typer.Option(
        "low",
        help="Preview quality hint (low|medium|high).",
    ),
    voice: str = typer.Option("ballad", help="Voice preset to embed in manifests."),
    speech_model: str = typer.Option(
        "gpt-4o-mini-tts",
        help="OpenAI model for speech synthesis.",
    ),
    dry_run: bool = typer.Option(
        False,
        help="Force local silent audio generation instead of calling OpenAI.",
    ),
) -> None:
    """Produce placeholder narration + preview artifacts."""

    lesson = _load_spec(spec)
    timeline = build_timeline(lesson)
    manifest_path = synthesize_narration(
        lesson,
        output_dir,
        voice=voice,
        model=speech_model,
        dry_run=True if dry_run else None,
    )
    preview_dir = render_preview(
        lesson,
        timeline,
        output_dir,
        quality=quality,
        audio_manifest=manifest_path,
    )
    console.print(f"[green]Preview artifacts at {preview_dir}")
    console.print(f"[green]Narration manifest at {manifest_path}")


@app.command()
def render(
    spec: Path = typer.Argument(..., exists=True, help="Lesson spec to render."),
    output_dir: Path = typer.Option(
        DEFAULT_OUTPUT_DIR,
        file_okay=False,
        help="Directory for final outputs.",
    ),
    quality: str = typer.Option("high", help="Final render quality hint."),
    voice: str = typer.Option("ballad", help="Voice preset for narration."),
    speech_model: str = typer.Option(
        "gpt-4o-mini-tts",
        help="OpenAI model used for narration synthesis.",
    ),
    dry_run: bool = typer.Option(
        False,
        help="Force local silent audio generation instead of calling OpenAI.",
    ),
) -> None:
    """Render all scenes at production quality and assemble the final MP4."""

    lesson = _load_spec(spec)
    timeline = build_timeline(lesson)
    manifest_path = synthesize_narration(
        lesson,
        output_dir,
        voice=voice,
        model=speech_model,
        dry_run=True if dry_run else None,
    )
    final_dir = render_final(
        lesson,
        timeline,
        output_dir,
        quality=quality,
        audio_manifest=manifest_path,
    )
    final_video = final_dir / f"{lesson.lesson_id}.mp4"
    console.print(f"[green]Final render written to {final_video}")


@app.command()
def frames(
    spec: Path = typer.Argument(..., exists=True, help="Lesson spec to snapshot."),
    output_dir: Path = typer.Option(
        DEFAULT_OUTPUT_DIR,
        file_okay=False,
        help="Directory to store frame placeholders.",
    ),
) -> None:
    """Export static frames for quick QA checks (requires preview renders)."""

    lesson = _load_spec(spec)
    timeline = build_timeline(lesson)
    frames_dir = export_static_frames(lesson, timeline, output_dir)
    console.print(f"[green]Static frame placeholders at {frames_dir}")


def main() -> None:
    app()
