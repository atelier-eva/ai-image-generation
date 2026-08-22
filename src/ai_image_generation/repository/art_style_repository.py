from typing import Any

from ai_image_generation.domain.art_style.art_style import ArtStyle
from ai_image_generation.repository.json_io import ART_STYLE_JSON, read_json, to_string_tuple


class ArtStyleRepository:
    def find(self) -> ArtStyle:
        return self._to_art_style(read_json(ART_STYLE_JSON))

    def _to_art_style(self, data: dict[str, Any]) -> ArtStyle:
        positive = data.get("positive") or {}
        return ArtStyle(
            positive_features=to_string_tuple(positive.get("prefix")),
            negative_features=to_string_tuple(data.get("negative")),
        )
