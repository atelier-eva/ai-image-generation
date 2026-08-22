from typing import Any

from ai_image_generation.domain.quality.quality import Quality
from ai_image_generation.repository.json_io import ART_STYLE_JSON, read_json, to_string_tuple


class QualityRepository:
    def find(self) -> Quality:
        return self._to_quality(read_json(ART_STYLE_JSON))

    def _to_quality(self, data: dict[str, Any]) -> Quality:
        positive = data.get("positive") or {}
        return Quality(
            positive_features=to_string_tuple(positive.get("suffix")),
        )
