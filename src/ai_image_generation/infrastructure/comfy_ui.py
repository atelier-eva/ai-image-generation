import copy
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

from ai_image_generation.config import Config
from ai_image_generation.repository.json_io import read_resource_json

_LORA_TRAINING_IMAGE_GENERATION_API_JSON = (
    "comfyui",
    "lora-training-image-generation-api.json",
)
_IMAGE_CREATION_API_JSON = (
    "comfyui",
    "image-creation-api.json",
)


class ComfyUi:
    _POLL_INTERVAL_SECONDS = 2
    _POLL_TIMEOUT_SECONDS = 600

    @dataclass
    class SavedImage:
        filename: str
        subfolder: str = ""

    def __init__(self) -> None:
        config = Config()
        self._url = config.comfy_ui_url
        self._ckpt_name = config.comfy_ui_ckpt_name
        self._output_directory = config.output_directory
        self._lora_training_template = read_resource_json(
            *_LORA_TRAINING_IMAGE_GENERATION_API_JSON
        )
        self._template = read_resource_json(*_IMAGE_CREATION_API_JSON)

    def generate_lora_training_images(
        self,
        filename_prefix: str,
        width: int,
        height: int,
        positive_prompt: str,
        negative_prompt: str,
        seed: int,
        batch_size: int = 4,
    ) -> tuple["ComfyUi.SavedImage", ...]:
        return self._queue_prompt(
            self._lora_training_workflow(
                filename_prefix,
                width,
                height,
                positive_prompt,
                negative_prompt,
                seed,
                batch_size,
            )
        )

    def generate_images(
        self,
        filename_prefix: str,
        width: int,
        height: int,
        positive_prompt: str,
        negative_prompt: str,
        lora_name: str,
        strength_model: float,
        strength_clip: float,
        pose_id: str | None,
        seed: int,
        batch_size: int = 4,
    ) -> tuple["ComfyUi.SavedImage", ...]:
        return self._queue_prompt(
            self._workflow(
                filename_prefix,
                width,
                height,
                positive_prompt,
                negative_prompt,
                lora_name,
                strength_model,
                strength_clip,
                pose_id,
                seed,
                batch_size,
            )
        )

    def fetch_image(self, image: "ComfyUi.SavedImage") -> bytes:
        query = urllib.parse.urlencode(
            {
                "filename": image.filename,
                "subfolder": image.subfolder,
                "type": "output",
            }
        )
        request = urllib.request.Request(f"{self._url}/view?{query}", method="GET")
        try:
            with urllib.request.urlopen(request) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            raise RuntimeError(
                f"ComfyUI /view failed for {image.filename}: {error.code}"
            ) from error
        except urllib.error.URLError as error:
            raise RuntimeError(f"ComfyUI is not reachable at {self._url}") from error

    def write_captions(
        self,
        images: tuple["ComfyUi.SavedImage", ...],
        caption: str,
    ) -> int:
        directory = self._output_directory
        text = caption.strip()
        if not text:
            raise ValueError("caption_prompt is empty or missing.")
        if not images:
            raise RuntimeError(
                "No saved images in ComfyUI history; cannot write captions."
            )
        written = 0
        for image in images:
            image_dir = directory / image.subfolder if image.subfolder else directory
            image_path = image_dir / image.filename
            if not image_path.is_file():
                raise FileNotFoundError(f"Image not found for caption: {image_path}")
            caption_path = image_dir / f"{image_path.stem}.txt"
            caption_path.write_text(text, encoding="utf-8", newline="\n")
            written += 1
        return written

    def write_images(self, images: tuple["ComfyUi.SavedImage", ...]) -> int:
        directory = self._output_directory
        if not images:
            raise RuntimeError(
                "No saved images in ComfyUI history; cannot write images."
            )
        written = 0
        for image in images:
            image_dir = directory / image.subfolder if image.subfolder else directory
            image_dir.mkdir(parents=True, exist_ok=True)
            (image_dir / image.filename).write_bytes(self.fetch_image(image))
            written += 1
        return written

    def _completed(self, status: dict[str, Any]) -> bool:
        if "completed" in status:
            return status["completed"] is True
        return status.get("status_str") == "success"

    def _request(
        self, method: str, path: str, body: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        data = None
        headers: dict[str, str] = {}
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json; charset=utf-8"
        request = urllib.request.Request(
            f"{self._url}{path}",
            data=data,
            headers=headers,
            method=method,
        )
        try:
            with urllib.request.urlopen(request) as response:
                loaded = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as error:
            raise RuntimeError(f"ComfyUI is not reachable at {self._url}") from error
        if not isinstance(loaded, dict):
            raise RuntimeError(f"ComfyUI {path} did not return an object.")
        return loaded

    def _saved_images(self, entry: dict[str, Any]) -> tuple["ComfyUi.SavedImage", ...]:
        images: list[ComfyUi.SavedImage] = []
        for output in (entry.get("outputs") or {}).values():
            for image in output.get("images") or []:
                filename = str(image.get("filename") or "").strip()
                if not filename:
                    continue
                images.append(
                    ComfyUi.SavedImage(
                        filename=filename,
                        subfolder=str(image.get("subfolder") or ""),
                    )
                )
        return tuple(images)

    def _wait_until_complete(self, prompt_id: str) -> tuple["ComfyUi.SavedImage", ...]:
        deadline = time.monotonic() + self._POLL_TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            time.sleep(self._POLL_INTERVAL_SECONDS)
            history = self._request("GET", f"/history/{prompt_id}")
            entry = history.get(prompt_id)
            if not entry:
                continue
            status = entry.get("status") or {}
            if status.get("status_str") == "error":
                raise RuntimeError(f"ComfyUI generation failed: {status.get('messages')}")
            if not self._completed(status):
                continue
            images = self._saved_images(entry)
            if images:
                return images
        raise TimeoutError(
            f"Timed out after {self._POLL_TIMEOUT_SECONDS}s waiting for image outputs "
            f"from prompt_id {prompt_id}."
        )

    def _queue_prompt(self, workflow: dict[str, Any]) -> tuple["ComfyUi.SavedImage", ...]:
        response = self._request("POST", "/prompt", {"prompt": workflow})
        node_errors = response.get("node_errors")
        if node_errors:
            raise RuntimeError(f"ComfyUI node_errors: {node_errors}")
        prompt_id = str(response.get("prompt_id") or "").strip()
        if not prompt_id:
            raise RuntimeError("ComfyUI /prompt did not return prompt_id.")
        return self._wait_until_complete(prompt_id)

    def _lora_training_workflow(
        self,
        filename_prefix: str,
        width: int,
        height: int,
        positive_prompt: str,
        negative_prompt: str,
        seed: int,
        batch_size: int,
    ) -> dict[str, Any]:
        workflow = copy.deepcopy(self._lora_training_template)
        workflow["2"]["inputs"]["ckpt_name"] = self._ckpt_name
        workflow["3"]["inputs"]["text"] = positive_prompt
        workflow["4"]["inputs"]["text"] = negative_prompt
        workflow["8"]["inputs"]["width"] = width
        workflow["8"]["inputs"]["height"] = height
        workflow["8"]["inputs"]["batch_size"] = batch_size
        workflow["11"]["inputs"]["filename_prefix"] = filename_prefix
        workflow["7"]["inputs"]["seed"] = seed
        return workflow

    def _workflow(
        self,
        filename_prefix: str,
        width: int,
        height: int,
        positive_prompt: str,
        negative_prompt: str,
        lora_name: str,
        strength_model: float,
        strength_clip: float,
        pose_id: str | None,
        seed: int,
        batch_size: int,
    ) -> dict[str, Any]:
        workflow = copy.deepcopy(self._template)
        workflow["2"]["inputs"]["ckpt_name"] = self._ckpt_name
        workflow["3"]["inputs"]["text"] = positive_prompt
        workflow["4"]["inputs"]["text"] = negative_prompt
        workflow["8"]["inputs"]["width"] = width
        workflow["8"]["inputs"]["height"] = height
        workflow["8"]["inputs"]["batch_size"] = batch_size
        workflow["11"]["inputs"]["filename_prefix"] = filename_prefix
        workflow["16"]["inputs"]["lora_name"] = lora_name
        workflow["16"]["inputs"]["strength_model"] = strength_model
        workflow["16"]["inputs"]["strength_clip"] = strength_clip
        workflow["7"]["inputs"]["seed"] = seed
        if pose_id is None:
            del workflow["5"]
            del workflow["6"]
            del workflow["12"]
            del workflow["13"]
            workflow["7"]["inputs"]["positive"] = ["3", 0]
            workflow["7"]["inputs"]["negative"] = ["4", 0]
        else:
            workflow["12"]["inputs"]["image"] = pose_id
        return workflow
