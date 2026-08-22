from typing import Any

from ai_image_generation.domain.expression.expression import Expression
from ai_image_generation.domain.expression.expression_settings import ExpressionSettings
from ai_image_generation.repository.json_io import SHOOT_JSON, read_json, to_string_tuple


class ExpressionRepository:
    def find(self) -> ExpressionSettings:
        expression = read_json(SHOOT_JSON).get("expression") or {}
        skip = expression.get("skipCamera") or {}
        return ExpressionSettings(
            patterns=tuple(
                self._to_expression(item) for item in expression.get("pattern") or []
            ),
            skip_angles=to_string_tuple(skip.get("angle")),
            skip_distances=to_string_tuple(skip.get("distance")),
        )

    def _to_expression(self, data: dict[str, Any]) -> Expression:
        positive = to_string_tuple(data.get("positive"))
        if not positive:
            positive = (data["name"].strip(),)
        return Expression(
            name=data["name"].strip(),
            positive_features=positive,
            negative_features=to_string_tuple(data.get("negative")),
        )
