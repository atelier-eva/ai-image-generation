import json
from functools import cache
from importlib.resources import files
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError, best_match

from ai_image_generation.config import Config

_SCHEMA_FILES = {
    "art-style.json": "art-style.schema.json",
    "scene.json": "scene.schema.json",
    "shoot.json": "shoot.schema.json",
}


def read_json(path: Path) -> dict[str, Any]:
    return _read_json(path.expanduser().resolve())


@cache
def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"JSON not found: {path}")
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"JSON must be an object: {path}")
    validator = _validator(path.name)
    if validator is None:
        return loaded
    error = best_match(validator.iter_errors(loaded))
    if error is not None:
        raise ValueError(_format_validation_error(path, error)) from error
    return loaded


def to_string_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    return tuple(tag.strip() for tag in value if str(tag).strip())


@cache
def _validator(json_name: str) -> Draft202012Validator | None:
    schema_name = _SCHEMA_FILES.get(json_name)
    if schema_name is None:
        return None
    schema = json.loads(
        files("ai_image_generation.resources")
        .joinpath(Config.LORA_TRAINING_DIRECTORY, schema_name)
        .read_text(encoding="utf-8")
    )
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _format_validation_error(path: Path, error: ValidationError) -> str:
    location = ".".join(str(part) for part in error.absolute_path)
    suffix = f" at {location}" if location else ""
    return f"Invalid JSON: {path}: {error.message}{suffix}"
