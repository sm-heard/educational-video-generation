"""Text-to-speech utilities backed by OpenAI Speech."""

from __future__ import annotations

import json
import os
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..specs.models import LessonSpec

try:  # pragma: no cover - optional dependency during tests
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore


@dataclass
class SpeechConfig:
    model: str = "gpt-4o-mini-tts"
    voice: str = "ballad"
    format: str = "wav"


def synthesize_narration(
    lesson: LessonSpec,
    output_dir: Path,
    voice: str = "ballad",
    *,
    model: str = "gpt-4o-mini-tts",
    dry_run: bool | None = None,
) -> Path:
    """Generate narration audio per scene and return the alignment manifest path."""

    config = SpeechConfig(model=model, voice=voice)
    synthesizer = SpeechSynthesizer(config=config, dry_run=dry_run)
    return synthesizer.run(lesson=lesson, output_dir=output_dir)


class SpeechSynthesizer:
    def __init__(self, *, config: SpeechConfig, dry_run: bool | None = None) -> None:
        self.config = config
        api_key = os.getenv("OPENAI_API_KEY")
        self.dry_run = dry_run if dry_run is not None else not api_key
        if not self.dry_run and OpenAI is None:
            raise RuntimeError("openai package is required but not installed")
        self._client = None if self.dry_run else OpenAI()

    def run(self, *, lesson: LessonSpec, output_dir: Path) -> Path:
        audio_root = output_dir / lesson.lesson_id / "audio"
        audio_root.mkdir(parents=True, exist_ok=True)

        manifest: dict[str, Any] = {
            "voice": self.config.voice,
            "model": self.config.model,
            "scenes": [],
        }

        for scene in lesson.scenes:
            scene_dir = audio_root / scene.id
            scene_dir.mkdir(parents=True, exist_ok=True)
            scene_info: dict[str, Any] = {"scene_id": scene.id, "chunks": []}

            time_cursor = 0.0
            for chunk_index, chunk in enumerate(scene.narration, start=1):
                filename = f"chunk_{chunk_index:02d}.{self.config.format}"
                chunk_path = scene_dir / filename
                duration = self._synthesize_chunk(
                    text=chunk.text,
                    output_path=chunk_path,
                    fallback_duration=chunk.duration_seconds,
                )

                scene_info["chunks"].append(
                    {
                        "index": chunk_index,
                        "text": chunk.text,
                        "file": str(chunk_path.relative_to(audio_root)),
                        "duration_seconds": duration,
                        "start_seconds": time_cursor,
                    }
                )
                time_cursor += duration

            manifest["scenes"].append(scene_info)

        manifest_path = audio_root / "alignment.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return manifest_path

    def _synthesize_chunk(
        self,
        *,
        text: str,
        output_path: Path,
        fallback_duration: float,
    ) -> float:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if self.dry_run or self._client is None:
            duration = max(fallback_duration, 2.0)
            _write_silence(output_path, duration_seconds=duration)
            return duration

        with self._client.audio.speech.with_streaming_response.create(
            model=self.config.model,
            voice=self.config.voice,
            input=text,
            audio_format=self.config.format,
        ) as response:
            response.stream_to_file(output_path)

        return _measure_duration(output_path)


def _write_silence(path: Path, *, duration_seconds: float, sample_rate: int = 22050) -> None:
    n_frames = max(int(duration_seconds * sample_rate), sample_rate)
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b"\x00\x00" * n_frames)


def _measure_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav_file:
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()
    if rate == 0:
        return 0.0
    return frames / float(rate)
