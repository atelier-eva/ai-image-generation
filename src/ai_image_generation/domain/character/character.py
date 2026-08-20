from dataclasses import dataclass

from ai_image_generation.domain.character.expression.character_expression import (
    CharacterExpression,
)
from ai_image_generation.domain.character.feature.character_feature import (
    CharacterFeature,
)


@dataclass
class Character:
    name: str
    subject: str | None = None
    features: tuple[CharacterFeature, ...] = ()
    expressions: tuple[CharacterExpression, ...] = ()
