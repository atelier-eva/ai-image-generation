from dataclasses import dataclass


@dataclass
class ContentRating:
    name: str
    positive_features: tuple[str, ...] = ()
    negative_features: tuple[str, ...] = ()
