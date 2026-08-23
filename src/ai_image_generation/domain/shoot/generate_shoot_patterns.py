import re

from ai_image_generation.config import Config
from ai_image_generation.domain.art_style.art_style import ArtStyle
from ai_image_generation.domain.camera.camera import Camera
from ai_image_generation.domain.expression.expression import Expression
from ai_image_generation.domain.pose.pose import Pose
from ai_image_generation.domain.shoot.generate_shoot_patterns_output import (
    GenerateShootPatternsOutput,
)
from ai_image_generation.domain.shoot.shoot import Shoot
from ai_image_generation.domain.subject.feature.subject_feature import SubjectFeature
from ai_image_generation.domain.subject.subject import Subject
from ai_image_generation.repository.shoot_repository import ShootRepository


class GenerateShootPatterns:
    def execute(self) -> tuple[GenerateShootPatternsOutput, ...]:
        shoot = ShootRepository().find()
        filename_prefix = Config().comfy_ui_filename_prefix
        patterns: list[GenerateShootPatternsOutput] = []
        row_number = 0
        for subject in shoot.subjects:
            for camera in shoot.cameras:
                for expression in self._expand_expressions(shoot, camera):
                    for pose in self._expand_poses(shoot, camera):
                        for art_style in self._expand_art_styles(shoot):
                            row_number += 1
                            patterns.append(
                                self._to_output(
                                    shoot,
                                    camera,
                                    subject,
                                    expression,
                                    pose,
                                    art_style,
                                    row_number,
                                    filename_prefix,
                                )
                            )
        return tuple(patterns)

    def _caption_prompt(
        self,
        camera: Camera,
        subject: Subject,
        expression: Expression | None,
        pose: Pose | None,
        art_style: ArtStyle | None,
    ) -> str:
        caption = self._join(
            (subject.name,),
            subject.kinds,
            self._feature_names(subject.positive_features(camera)),
            camera.angle.positive_features,
            camera.distance.positive_features,
            expression.positive_features if expression else (),
            pose.positive_features if pose else (),
            art_style.positive_features if art_style else (),
        )
        if not caption:
            raise ValueError(
                "caption_prompt is empty for "
                f"{subject.name} / {camera.angle.name} / {camera.distance.name}."
            )
        return caption

    def _expand_art_styles(self, shoot: Shoot) -> tuple[ArtStyle | None, ...]:
        if shoot.art_styles:
            return shoot.art_styles
        return (None,)

    def _expand_expressions(
        self, shoot: Shoot, camera: Camera
    ) -> tuple[Expression | None, ...]:
        if shoot.expressions.includes(camera):
            return shoot.expressions.patterns
        return (None,)

    def _expand_poses(self, shoot: Shoot, camera: Camera) -> tuple[Pose | None, ...]:
        if shoot.poses.includes(camera):
            return shoot.poses.patterns
        return (None,)

    def _feature_names(
        self, features: tuple[SubjectFeature, ...], *, weighted: bool = False
    ) -> tuple[str, ...]:
        return tuple(
            self._weighted_name(feature) if weighted else feature.name
            for feature in features
        )

    def _filename_prefix(
        self,
        row_number: int,
        camera: Camera,
        subject: Subject,
        expression: Expression | None,
        pose: Pose | None,
        art_style: ArtStyle | None,
        prefix: str,
    ) -> str:
        parts = [
            f"{self._slug(prefix)}_{row_number:03d}",
            subject.name,
            self._slug(camera.angle.name),
            self._slug(camera.distance.name),
        ]
        if expression is not None:
            parts.append(self._slug(expression.name))
        if pose is not None:
            parts.append(self._slug(pose.name))
        if art_style is not None:
            parts.append(self._slug(art_style.name))
        return "_".join(parts)

    def _join(self, *groups: tuple[str, ...]) -> str:
        return ", ".join(name for group in groups for name in group if name)

    def _negative_prompt(
        self,
        shoot: Shoot,
        camera: Camera,
        subject: Subject,
        expression: Expression | None,
        pose: Pose | None,
        art_style: ArtStyle | None,
    ) -> str:
        return self._join(
            shoot.rating.negative_features if shoot.rating else (),
            art_style.negative_features if art_style else (),
            shoot.quality.negative_features if shoot.quality else (),
            shoot.scene.negative_features if shoot.scene else (),
            self._feature_names(subject.negative_features(camera)),
            camera.angle.negative_features,
            camera.distance.negative_features,
            expression.negative_features if expression else (),
            pose.negative_features if pose else (),
        )

    def _positive_prompt(
        self,
        shoot: Shoot,
        camera: Camera,
        subject: Subject,
        expression: Expression | None,
        pose: Pose | None,
        art_style: ArtStyle | None,
    ) -> str:
        return self._join(
            subject.kinds,
            shoot.rating.positive_features if shoot.rating else (),
            art_style.positive_features if art_style else (),
            self._feature_names(subject.positive_features(camera), weighted=True),
            camera.angle.positive_features,
            camera.distance.positive_features,
            expression.positive_features if expression else (),
            pose.positive_features if pose else (),
            shoot.scene.positive_features if shoot.scene else (),
            shoot.quality.positive_features if shoot.quality else (),
        )

    def _slug(self, name: str) -> str:
        return re.sub(r"\s+", "-", name.strip().lower())

    def _to_output(
        self,
        shoot: Shoot,
        camera: Camera,
        subject: Subject,
        expression: Expression | None,
        pose: Pose | None,
        art_style: ArtStyle | None,
        row_number: int,
        prefix: str,
    ) -> GenerateShootPatternsOutput:
        return GenerateShootPatternsOutput(
            filename_prefix=self._filename_prefix(
                row_number, camera, subject, expression, pose, art_style, prefix
            ),
            width=camera.frame.width,
            height=camera.frame.height,
            positive_prompt=self._positive_prompt(
                shoot, camera, subject, expression, pose, art_style
            ),
            negative_prompt=self._negative_prompt(
                shoot, camera, subject, expression, pose, art_style
            ),
            caption_prompt=self._caption_prompt(
                camera, subject, expression, pose, art_style
            ),
        )

    def _weighted_name(self, feature: SubjectFeature) -> str:
        if feature.weight is None:
            return feature.name
        return f"({feature.name}:{format(feature.weight, 'g')})"
