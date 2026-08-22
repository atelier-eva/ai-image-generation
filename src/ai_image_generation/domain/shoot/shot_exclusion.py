from dataclasses import dataclass

from ai_image_generation.domain.camera.camera import Camera


@dataclass
class ShotExclusion:
    angles: tuple[str, ...] = ()
    distances: tuple[str, ...] = ()

    def excludes(self, camera: Camera) -> bool:
        angle_ok = not self.angles or camera.angle.name in self.angles
        distance_ok = not self.distances or camera.distance.name in self.distances
        return angle_ok and distance_ok
