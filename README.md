# Educational Video Generation

Prototype tooling for turning a single prompt into a structured physics lesson that can be rendered with Manim. The current implementation focuses on scaffolding – the heavy lifting (OpenAI prompt expansion, narration synthesis, and Manim rendering) still needs to be wired in.

## Quick Start

```bash
# Ensure dependencies are installed
uv sync

# Generate a lesson spec from a prompt
uv run video gen "Explain Newton's Second Law"

# Produce placeholder preview/final artifacts
uv run video preview outputs/physics-explain-newtons-second-law.lesson.json
uv run video render outputs/physics-explain-newtons-second-law.lesson.json

# Launch the Streamlit UI
uv run streamlit run streamlit_app.py
```

Configuration lives in `configs/` (style tokens + defaults). Example specs are in `examples/`.
