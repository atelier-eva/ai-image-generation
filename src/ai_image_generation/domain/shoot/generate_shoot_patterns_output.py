from dataclasses import dataclass


@dataclass
class GenerateShootPatternsOutput:
    filename_prefix: str
    width: int
    height: int
    positive_prompt: str
    negative_prompt: str
    caption_prompt: str
