from typing import Any

from ai_image_generation.domain.art_style.art_style import ArtStyle
from ai_image_generation.repository.json_io import art_style_json, read_json, to_string_tuple


class ArtStyleRepository:
    def find(self) -> ArtStyle:
        return self._to_art_style(read_json(art_style_json()).get("artStyle"))

    def _to_art_style(self, data: Any) -> ArtStyle:
        if not data:
            return ArtStyle()
        return ArtStyle(
            positive_features=to_string_tuple(data.get("positive")),
            negative_features=to_string_tuple(data.get("negative")),
        )
