from dataclasses import dataclass


@dataclass
class ArtStyle:
    positive_features: tuple[str, ...] = ()
    negative_features: tuple[str, ...] = ()
