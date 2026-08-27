from dataclasses import dataclass, field

from ai_media_generation.domain.camera.angle.camera_angle import CameraAngle
from ai_media_generation.domain.camera.distance.camera_distance import CameraDistance
from ai_media_generation.domain.camera.frame.camera_frame import CameraFrame


@dataclass
class Camera:
    angle: CameraAngle
    distance: CameraDistance
    frame: CameraFrame = field(init=False)

    def __post_init__(self) -> None:
        self.frame = self.distance.frame
