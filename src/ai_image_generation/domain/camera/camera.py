from dataclasses import dataclass, field

from ai_image_generation.domain.camera.angle.camera_angle import CameraAngle
from ai_image_generation.domain.camera.distance.camera_distance import (
    CameraDistance,
    CameraDistanceName,
)
from ai_image_generation.domain.camera.frame.camera_frame import CameraFrame

_FRAME_BY_DISTANCE = {
    CameraDistanceName.FULL_BODY: CameraFrame(768, 1344),
    CameraDistanceName.FACE_CLOSE_UP: CameraFrame(1024, 1024),
    CameraDistanceName.BUST_UP: CameraFrame(896, 1152),
}


@dataclass
class Camera:
    angle: CameraAngle
    distance: CameraDistance
    frame: CameraFrame = field(init=False)

    def __post_init__(self) -> None:
        self.frame = _FRAME_BY_DISTANCE[self.distance.name]
