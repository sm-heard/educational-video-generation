# Educational Video Generation

Prototype tooling for turning a single prompt into a structured physics lesson that can be rendered with Manim. The current implementation focuses on scaffolding – the heavy lifting (OpenAI prompt expansion, narration synthesis, and Manim rendering) still needs to be wired in.

## Quick Start

```bash
# Ensure dependencies are installed
uv sync

# Generate an end-to-end video (spec → audio → preview → final)
uv run video run "Explain Newton's First Law"

# Generate a lesson spec from a prompt (uses OpenAI if OPENAI_API_KEY is set)
uv run video gen "Explain Newton's Second Law"

# Produce preview clips (synthesises narration under outputs/<lesson>/audio)
uv run video preview outputs/physics-explain-newtons-second-law.lesson.json
uv run video render outputs/physics-explain-newtons-second-law.lesson.json

# Launch the Streamlit UI
uv run streamlit run streamlit_app.py
```

Preview clips render to `outputs/<lesson>/preview/scene_*.mp4`; final renders land in `outputs/<lesson>/final/<lesson>.mp4`. Run `uv run video frames ...` after previewing to grab representative PNGs for QA.

If you want to skip API calls, append `--dry-run` to the `gen`, `preview`, or `render` commands. Configuration lives in `configs/` (style tokens + defaults). Example specs are in `examples/`.

### Prerequisites

- FFmpeg available on PATH (system install or via `imageio-ffmpeg`).
- A LaTeX distribution (e.g. MacTeX) for Manim’s text rendering.
- Optional: `.env` file in the project root for secrets.

### Environment

Set the following variables (for example by adding them to a `.env` file loaded via `python-dotenv`) before running the CLI or Streamlit app:

```
OPENAI_API_KEY=sk-...
OPENAI_TTS_VOICE=ballad  # optional override
```

On Streamlit Community Cloud, add the same keys via Settings → Secrets. For GitHub Actions or other runners, configure them as repository secrets and expose them as environment variables.
