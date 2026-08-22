from dataclasses import dataclass, field

from ai_image_generation.domain.art_style.art_style import ArtStyle
from ai_image_generation.domain.camera.camera import Camera
from ai_image_generation.domain.expression.expression_settings import ExpressionSettings
from ai_image_generation.domain.quality.quality import Quality
from ai_image_generation.domain.rating.content_rating import ContentRating
from ai_image_generation.domain.scene.scene import Scene
from ai_image_generation.domain.subject.feature.subject_feature import SubjectFeature
from ai_image_generation.domain.subject.subject import Subject


@dataclass
class Shoot:
    cameras: tuple[Camera, ...] = ()
    subjects: tuple[Subject, ...] = ()
    expressions: ExpressionSettings = field(default_factory=ExpressionSettings)
    scene: Scene | None = None
    art_style: ArtStyle | None = None
    quality: Quality | None = None
    rating: ContentRating | None = None

    def includes_expression_patterns(self, camera: Camera) -> bool:
        return self.expressions.includes(camera)

    def filtered_features(
        self, subject: Subject, camera: Camera
    ) -> tuple[SubjectFeature, ...]:
        return tuple(
            feature for feature in subject.features if not feature.skips(camera)
        )
