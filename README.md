# Educational Video Generation

Prototype tooling for turning a single prompt into a structured physics lesson that can be rendered with Manim. The current implementation focuses on scaffolding – the heavy lifting (OpenAI prompt expansion, narration synthesis, and Manim rendering) still needs to be wired in.

## Quick Start

```bash
# Ensure dependencies are installed
uv sync

# Generate a lesson spec from a prompt (uses OpenAI if OPENAI_API_KEY is set)
uv run video gen "Explain Newton's Second Law"

# Produce preview artifacts (synthesises narration under outputs/<lesson>/audio)
uv run video preview outputs/physics-explain-newtons-second-law.lesson.json
uv run video render outputs/physics-explain-newtons-second-law.lesson.json

# Launch the Streamlit UI
uv run streamlit run streamlit_app.py
```

If you want to skip API calls, append `--dry-run` to the `gen` or `preview` commands. Configuration lives in `configs/` (style tokens + defaults). Example specs are in `examples/`.

### Environment

Set the following variables (for example by adding them to a `.env` file loaded via `python-dotenv`) before running the CLI or Streamlit app:

```
OPENAI_API_KEY=sk-...
OPENAI_TTS_VOICE=ballad  # optional override
```

On Streamlit Community Cloud, add the same keys via Settings → Secrets. For GitHub Actions or other runners, configure them as repository secrets and expose them as environment variables.
