"""Command-line entry point for the AI image generation assistant."""

from importlib.metadata import version


def main() -> None:
    print(f"ai-image-generation {version('ai-image-generation')}")
