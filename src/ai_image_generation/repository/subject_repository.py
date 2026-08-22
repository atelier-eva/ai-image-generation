from typing import Any

from ai_image_generation.config import Config
from ai_image_generation.domain.subject.feature.subject_feature import (
    SubjectFeature,
    SubjectFeaturePolarity,
)
from ai_image_generation.domain.subject.subject import Subject
from ai_image_generation.repository.json_io import read_json, to_string_tuple


class SubjectRepository:
    def find(self) -> tuple[Subject, ...]:
        return tuple(
            self._to_subject(item)
            for item in read_json(Config().shoot_json).get("characters") or []
        )

    def _to_subject(self, data: dict[str, Any]) -> Subject:
        features = tuple(
            self._to_feature(entry, SubjectFeaturePolarity.POSITIVE)
            for entry in data.get("positive") or []
        ) + tuple(
            SubjectFeature(tag, SubjectFeaturePolarity.NEGATIVE)
            for tag in to_string_tuple(data.get("negative"))
        )
        return Subject(
            name=data["name"].strip(),
            kinds=self._to_kinds(data.get("subject")),
            features=features,
        )

    def _to_feature(
        self, entry: Any, polarity: SubjectFeaturePolarity
    ) -> SubjectFeature:
        if isinstance(entry, str):
            return SubjectFeature(entry.strip(), polarity)
        skip = entry.get("skip_camera") or {}
        return SubjectFeature(
            entry["tag"].strip(),
            polarity,
            weight=self._to_weight(entry.get("weight")),
            skip_angles=to_string_tuple(skip.get("angle")),
            skip_distances=to_string_tuple(skip.get("distance")),
        )

    def _to_weight(self, value: Any) -> float | None:
        if value is None:
            return None
        weight = float(value)
        if weight <= 0:
            raise ValueError(f"Feature weight must be greater than 0: {weight}")
        return weight

    def _to_kinds(self, value: Any) -> tuple[str, ...]:
        if isinstance(value, str):
            kind = value.strip()
            return (kind,) if kind else ()
        return to_string_tuple(value)
