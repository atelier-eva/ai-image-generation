from dataclasses import dataclass

from ai_media_generation.domain.music_spec.music_spec import MusicSpec


@dataclass
class MusicSpecDto:
    id: str
    prompt: str
    lyrics: str
    vocal_language: str | None
    duration: float | None
    bpm: int | None


class GetMusicSpecsOutput:
    def __init__(self, specs: tuple[MusicSpec, ...]) -> None:
        self.dtos = tuple(self._to_dto(spec) for spec in specs)

    @staticmethod
    def _to_dto(spec: MusicSpec) -> MusicSpecDto:
        return MusicSpecDto(
            id=spec.id,
            prompt=spec.prompt,
            lyrics=spec.lyrics,
            vocal_language=spec.vocal_language,
            duration=spec.duration,
            bpm=spec.bpm,
        )
