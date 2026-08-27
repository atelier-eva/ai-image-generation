from dataclasses import dataclass

from ai_media_generation.domain.camera.frame.camera_frame import CameraFrame


@dataclass
class CameraDistance:
    name: str
    frame: CameraFrame
    positive_features: tuple[str, ...] = ()
    negative_features: tuple[str, ...] = ()
