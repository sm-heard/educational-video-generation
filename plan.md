# Educational Video Generation – Implementation Plan

## Milestones & Tasks

### M0 — Project Setup (Day 0–1)
- Create repo scaffolding: `src/`, `assets/`, `outputs/`, `configs/`, `examples/`, `scripts/`.
- Python 3.14 with uv for env/deps. Initialize `pyproject.toml` and `uv.lock`.
- Add baseline deps via uv: Manim CE, Typer, Pydantic, python-dotenv, Rich, MoviePy, SoundFile/PyDub, NumPy.
- Verify toolchain: FFmpeg, LaTeX (TeX Live/MiKTeX), Manim CLI.
- Configure ruff for lint+format (`pyproject.toml`), and pre-commit hooks via `uvx pre-commit` (optional).
- Define `project.scripts` in `pyproject.toml` and run via `uv run` (prefer uv over Makefile).

### M1 — Data Model & Style System (Day 1–2)
- Define Pydantic schemas for: `LessonSpec`, `SceneSpec`, `NarrationChunk`, `Event`, `StyleTokens`.
- Add `configs/style.json` with fonts, colors, sizes, easing, transition durations, safe areas, variable color rules.
- Create `configs/defaults.yaml` for global parameters (fps=30, res=1080p, seeds, cache settings).
- Implement deterministic seed management and run folder naming based on content hash.

### M2 — Prompt Expansion & Script Generation (Day 2–3)
- Create `src/prompting/generator.py` to turn a single prompt into `lesson.json` (skills, narration chunks, visuals plan, timing cues).
- Provide provider-adapter interface (OpenAI, local stub). Include structured-output parsing into Pydantic models.
- Add a fully offline example `examples/newtons_laws.lesson.json` for dev without API.

### M3 — TTS Narration (Day 3–4)
- Build `src/audio/tts.py` with pluggable providers (OpenAI TTS, ElevenLabs). Inputs: chunks; Outputs: WAV/MP3 per chunk + `alignment.json` with measured durations.
- Measure actual durations with `soundfile` or `pydub`; write `alignment.json` per scene and global `cues.json`.
- Support SSML options (pauses, emphasis) where provider supports; fallback to chunk-level gaps.

### M4 — Event Timeline & Sync (Day 4–5)
- Implement `src/timeline/scheduler.py` to map narration chunks → event timestamps (front-load object creation; reveal at events).
- Support speed-factor correction per scene: `speed = actual/expected`; adjust event times; hard clamp drift ≤300ms.
- Export timeline with resolved times for rendering and for QA overlays.

### M5 — Manim Base Components (Day 5–7)
- Create base scene `BaseSkillScene` with style tokens, safe-area guides, and helper methods (`show_title`, `draw_formula`, `highlight`, `fade_old`).
- Utilities for LaTeX/MathTex with variable color coding and progressive draw.
- Graph/axes helpers (sequential axes → units → data → highlight) and reusable vector/FBD primitives.

### M6 — Rendering Pipeline (Day 7–8)
- Implement `src/render/render_scene.py` to render each `SceneSpec` at low/med/high quality.
- Add preview mode: `-ql`, 5 fps option, static frame snapshots at t=0/25/50/75/100, and overlap checker (bounding-box collision).
- Integrate audio: either Manim `add_sound` at t=0 for scene, or assemble with MoviePy/FFmpeg post-render.

### M7 — Assembly & Outputs (Day 8–9)
- Concatenate verified scenes, add 1–2s padding between scenes as configured.
- Emit final MP4 (1080p, 30 fps), `outputs/<run_id>/cues.json`, `narration.txt`, and all generated assets.
- Verify durations with `ffprobe` and sync with automated checks (event vs narration timestamps). Fail build if drift >300ms.

### M8 — UI for Creators (Day 9–10)
- Build a Streamlit app: input prompt, upload optional images, pick voice/style; run pipeline and display preview/final.
- Show logs, timings, and auto-generated static frames for quick review; allow re-runs with small edits to spec/style.

### M9 — Example Content & QA (Day 10–12)
- Produce three videos for Newton’s Laws using the pipeline; iterate on style tokens for readability and pacing.
- Run QA checklist: no overlaps, font sizes ≥18pt, color contrast, consistent transitions, total durations 80–180s.

### M10 — Documentation & Handoff (Day 12–13)
- Write `README.md` with setup, commands, and troubleshooting.
- Add `STYLE_GUIDE.md` documenting tokens and usage; `SCHEMA.md` for JSON specs.
- Record known quirks and iteration workflow (preview → lock audio → final render).

## CLI Commands (initial targets)
- `uv run video gen --prompt "…" --style configs/style.json --out outputs/` → one-shot generation.
- `uv run video preview --spec examples/newtons_laws.lesson.json` → quick preview low-res.
- `uv run video render --spec <file> --quality high` → final render.
- `uv run video frames --spec <file>` → dump static frames for overlap check.
- `uvx ruff check .` and `uvx ruff format .` → lint/format.

## Acceptance Criteria
- Three Newton’s Laws videos, 80–180s each, consistent style, readable, and synced within ±300 ms.
- Reproducible runs: same inputs → similar outputs, seed-locked where applicable.
- Iteration loop supports low-res preview and targeted changes without regressions.

## Nice-to-Haves (Post-MVP)
- WhisperX/Gentle-based forced alignment for word-level cues when needed.
- Asset cache keyed by spec/style hashes; partial scene re-render.
- Theme preview generator and palette contrast checker.
- Next.js + FastAPI UI if/when Streamlit hits limits.
