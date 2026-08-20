from dataclasses import dataclass
from enum import Enum


class CameraDistanceName(Enum):
    FULL_BODY = "full_body"
    FACE_CLOSE_UP = "face_close_up"
    BUST_UP = "bust_up"


@dataclass
class CameraDistance:
    name: CameraDistanceName
    positive_features: tuple[str, ...] = ()
    negative_features: tuple[str, ...] = ()
