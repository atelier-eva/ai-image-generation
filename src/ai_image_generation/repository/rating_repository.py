from typing import Any

from ai_image_generation.domain.rating.content_rating import ContentRating
from ai_image_generation.repository.json_io import art_style_json, read_json, to_string_tuple


class RatingRepository:
    def find(self) -> ContentRating | None:
        return self._to_rating(read_json(art_style_json()).get("rating"))

    def _to_rating(self, data: Any) -> ContentRating | None:
        if not data:
            return None
        name = str(data.get("name") or "").strip()
        if not name:
            return None
        positive = to_string_tuple(data.get("positive"))
        if not positive:
            positive = (name,)
        return ContentRating(
            name=name,
            positive_features=positive,
            negative_features=to_string_tuple(data.get("negative")),
        )
