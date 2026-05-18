"""Local transcription using faster-whisper (CPU)."""

import logging
import time
from pathlib import Path

from faster_whisper import WhisperModel

from src.transcriber.base import Transcriber
from src.models.schemas import TranscriptResult

logger = logging.getLogger(__name__)

# Model size options (in order of accuracy/speed): tiny, base, small, medium, large-v3
# For CPU Chinese ASR, 'small' is a good tradeoff
DEFAULT_MODEL = "small"


class LocalTranscriber(Transcriber):
    """Transcribe locally using faster-whisper on CPU."""

    def __init__(self, model_size: str = DEFAULT_MODEL):
        logger.info("Loading faster-whisper model: %s (CPU, int8)...", model_size)
        t0 = time.time()
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        elapsed = time.time() - t0
        logger.info("Model loaded in %.1f sec", elapsed)

    def transcribe(self, audio_path: Path, duration_sec: float | None = None) -> TranscriptResult:
        logger.info("Transcribing %s...", audio_path.name)
        t0 = time.time()

        segments, info = self.model.transcribe(
            str(audio_path),
            language="zh",
            beam_size=5,
            word_timestamps=False,
        )

        text_parts = []
        seg_list = []
        for seg in segments:
            text_parts.append(seg.text.strip())
            seg_list.append({
                "text": seg.text.strip(),
                "start_time": seg.start,
                "end_time": seg.end,
            })

        full_text = "\n".join(text_parts)
        actual_duration = info.duration or duration_sec or 0
        elapsed = time.time() - t0

        logger.info(
            "Transcription done: %d chars in %.1f sec (RTF=%.2f)",
            len(full_text), elapsed, elapsed / actual_duration if actual_duration else 0,
        )

        return TranscriptResult(
            raw_text=full_text,
            segments=seg_list,
            duration_sec=actual_duration,
            cost_yuan=0.0,  # free!
        )
