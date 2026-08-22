from typing import Any

from ai_image_generation.config import Config
from ai_image_generation.domain.quality.quality import Quality
from ai_image_generation.repository.json_io import read_json, to_string_tuple


class QualityRepository:
    def find(self) -> Quality:
        return self._to_quality(read_json(Config().art_style_json).get("quality"))

    def _to_quality(self, data: Any) -> Quality:
        if not data:
            return Quality()
        return Quality(
            positive_features=to_string_tuple(data.get("positive")),
            negative_features=to_string_tuple(data.get("negative")),
        )
