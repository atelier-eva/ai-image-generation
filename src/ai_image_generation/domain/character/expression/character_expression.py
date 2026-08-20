from dataclasses import dataclass


@dataclass
class CharacterExpression:
    name: str
    positive_features: tuple[str, ...] = ()
    negative_features: tuple[str, ...] = ()
