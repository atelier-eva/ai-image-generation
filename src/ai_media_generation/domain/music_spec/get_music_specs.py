from ai_media_generation.domain.music_spec.get_music_specs_output import (
    GetMusicSpecsOutput,
)
from ai_media_generation.repository.music_spec_repository import MusicSpecRepository


class GetMusicSpecs:
    def execute(self, ids: tuple[str, ...] = ()) -> GetMusicSpecsOutput:
        return GetMusicSpecsOutput(MusicSpecRepository().get(ids))
