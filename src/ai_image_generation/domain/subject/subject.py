from dataclasses import dataclass

from ai_image_generation.domain.subject.feature.subject_feature import SubjectFeature


@dataclass
class Subject:
    name: str
    kinds: tuple[str, ...] = ()
    features: tuple[SubjectFeature, ...] = ()
