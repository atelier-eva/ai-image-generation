from dataclasses import dataclass


@dataclass
class SceneLighting:
    positive_features: tuple[str, ...] = ()
    negative_features: tuple[str, ...] = ()
