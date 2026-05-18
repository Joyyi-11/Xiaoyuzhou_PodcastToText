from dataclasses import dataclass, field
from typing import Optional


@dataclass
class EpisodeInfo:
    """Xiaoyuzhou episode metadata scraped from the page."""
    url: str
    title: str
    podcast_name: str
    pub_date: str
    show_notes: str
    audio_url: str
    cover_url: Optional[str] = None


@dataclass
class TranscriptResult:
    """Result from ASR transcription."""
    raw_text: str
    segments: list[dict]  # [{"text": ..., "start_time": ..., "end_time": ...}]
    duration_sec: float
    cost_yuan: float = 0.0


@dataclass
class KeyPoint:
    """A single key point with supporting evidence."""
    point: str
    evidence: str


@dataclass
class OutputDoc:
    """Final structured output document."""
    title: str
    podcast_name: str
    pub_date: str
    show_notes: str
    key_points: list[KeyPoint]
    highlight_quotes: list[str] = field(default_factory=list)
    full_text: str = ""  # cleaned and formatted full transcript (Markdown)
    costs: dict = field(default_factory=dict)  # {"transcription": 0.0, "llm": 0.0}
    timings: dict = field(default_factory=dict)  # {"scrape": 0, "transcribe": 0, "process": 0}
