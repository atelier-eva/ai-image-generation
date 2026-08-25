from dataclasses import dataclass


@dataclass
class GenerateImageSpecOutput:
    name: str
    filename_prefix: str
    width: int
    height: int
    positive_prompt: str
    negative_prompt: str
    lora_name: str
    model_strength: float
    text_encoder_strength: float
    pose_image: str | None
