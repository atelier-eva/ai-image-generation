from dataclasses import dataclass


@dataclass
class MusicSpec:
    id: str
    prompt: str
    lyrics: str = ""
    vocal_language: str | None = None
    duration: float | None = None
    bpm: int | None = None
