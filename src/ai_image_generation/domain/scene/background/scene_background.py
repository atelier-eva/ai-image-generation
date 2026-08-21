from dataclasses import dataclass


@dataclass
class SceneBackground:
    positive_features: tuple[str, ...] = ()
    negative_features: tuple[str, ...] = ()
