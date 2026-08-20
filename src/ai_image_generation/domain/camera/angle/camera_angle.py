from dataclasses import dataclass
from enum import Enum


class CameraAngleName(Enum):
    FRONT = "front"
    SIDE = "side"
    BACK = "back"
    DIAGONAL_RIGHT = "diagonal_right"
    DIAGONAL_LEFT = "diagonal_left"


@dataclass
class CameraAngle:
    name: CameraAngleName
    positive_features: tuple[str, ...] = ()
    negative_features: tuple[str, ...] = ()
