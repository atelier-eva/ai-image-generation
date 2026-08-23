import json
from functools import cache
from importlib.resources import files
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError, best_match

from ai_image_generation.config import Config

_SCHEMAS = {
    "art-style.json": "art-style.schema.json",
    "camera.json": "camera.schema.json",
    "characters": "characters.schema.json",
    "expression.json": "expression.schema.json",
    "generation.json": "generation.schema.json",
    "pose.json": "pose.schema.json",
    "scene.json": "scene.schema.json",
}


def read_json(path: Path) -> dict[str, Any]:
    return _read_json(path.expanduser().resolve())


def read_resource_json(*relative: str) -> dict[str, Any]:
    return _read_resource_json(relative)


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON: {path}: {error.msg} "
            f"(line {error.lineno} column {error.colno})"
        ) from error


@cache
def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"JSON not found: {path}")
    loaded = _load_json(path)
    if not isinstance(loaded, dict):
        raise ValueError(f"Invalid JSON: {path}: JSON must be an object")
    schema_name = _schema_name(path)
    if schema_name is None:
        return loaded
    validator = _validator(schema_name)
    error = best_match(validator.iter_errors(loaded))
    if error is not None:
        raise ValueError(_format_validation_error(path, error)) from error
    return loaded


@cache
def _read_resource_json(relative: tuple[str, ...]) -> dict[str, Any]:
    resource = files("ai_image_generation.resources").joinpath(*relative)
    loaded = json.loads(resource.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"JSON must be an object: {resource}")
    return loaded


def to_string_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    return tuple(tag.strip() for tag in value if str(tag).strip())


def _schema_name(path: Path) -> str | None:
    return _SCHEMAS.get(path.parent.name) or _SCHEMAS.get(path.name)


@cache
def _validator(schema_name: str) -> Draft202012Validator:
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
