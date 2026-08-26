from dataclasses import dataclass


@dataclass
class Lora:
    id: str
    model_strength: float = 1.0
    text_encoder_strength: float = 1.0
