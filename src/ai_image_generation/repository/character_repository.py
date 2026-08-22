from typing import Any

from ai_image_generation.domain.character.character import Character
from ai_image_generation.domain.character.expression.character_expression import (
    CharacterExpression,
)
from ai_image_generation.domain.character.feature.character_feature import (
    CharacterFeature,
    CharacterFeaturePolarity,
)
from ai_image_generation.repository.json_io import SHOOT_JSON, read_json, to_string_tuple


class CharacterRepository:
    def find(self) -> tuple[Character, ...]:
        shoot = read_json(SHOOT_JSON)
        expressions = tuple(
            self._to_expression(item)
            for item in (shoot.get("expression") or {}).get("pattern") or []
        )
        return tuple(
            self._to_character(item, expressions)
            for item in shoot.get("characters") or []
        )

    def _to_character(
        self,
        data: dict[str, Any],
        expressions: tuple[CharacterExpression, ...],
    ) -> Character:
        features = tuple(
            self._to_feature(entry, CharacterFeaturePolarity.POSITIVE)
            for entry in data.get("positive") or []
        ) + tuple(
            CharacterFeature(tag, CharacterFeaturePolarity.NEGATIVE)
            for tag in to_string_tuple(data.get("negative"))
        )
        return Character(
            name=data["name"].strip(),
            subject=self._to_subject(data.get("subject")),
            features=features,
            expressions=expressions,
        )

    def _to_expression(self, data: dict[str, Any]) -> CharacterExpression:
        positive = to_string_tuple(data.get("positive"))
        if not positive:
            positive = (data["name"].strip(),)
        return CharacterExpression(
            name=data["name"].strip(),
            positive_features=positive,
            negative_features=to_string_tuple(data.get("negative")),
        )

    def _to_feature(
        self, entry: Any, polarity: CharacterFeaturePolarity
    ) -> CharacterFeature:
        if isinstance(entry, str):
            return CharacterFeature(entry.strip(), polarity)
        return CharacterFeature(entry["tag"].strip(), polarity)

    def _to_subject(self, value: Any) -> str | None:
        if isinstance(value, list):
            subject = ", ".join(tag.strip() for tag in value if str(tag).strip())
            return subject or None
        if isinstance(value, str) and value.strip():
            return value.strip()
        return None
