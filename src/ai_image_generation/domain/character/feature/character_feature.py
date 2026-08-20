from dataclasses import dataclass
from enum import Enum


class CharacterFeaturePolarity(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"


@dataclass
class CharacterFeature:
    name: str
    polarity: CharacterFeaturePolarity
