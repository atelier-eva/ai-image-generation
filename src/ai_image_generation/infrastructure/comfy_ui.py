import copy
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from ai_image_generation.repository.json_io import read_json

LORA_TRAINING_IMAGE_CREATION_API_JSON = Path("art/lora-training-image-creation-api.json")


class ComfyUi:
    _POLL_INTERVAL_SECONDS = 2
    _POLL_TIMEOUT_SECONDS = 600

    def __init__(self, url: str = "http://127.0.0.1:8188") -> None:
        self._url = url.rstrip("/")
        self._template = read_json(LORA_TRAINING_IMAGE_CREATION_API_JSON)

    def generate_images(
        self,
        filename_prefix: str,
        width: int,
        height: int,
        positive_prompt: str,
        negative_prompt: str,
        seed: int,
        batch_size: int = 4,
    ) -> dict[str, Any]:
        workflow = self._workflow(
            filename_prefix,
            width,
            height,
            positive_prompt,
            negative_prompt,
            seed,
            batch_size,
        )
        response = self._request("POST", "/prompt", {"prompt": workflow})
        node_errors = response.get("node_errors")
        if node_errors:
            raise RuntimeError(f"ComfyUI node_errors: {node_errors}")
        prompt_id = str(response.get("prompt_id") or "").strip()
        if not prompt_id:
            raise RuntimeError("ComfyUI /prompt did not return prompt_id.")
        return self._wait_until_complete(prompt_id)

    def _completed(self, status: dict[str, Any]) -> bool:
        if "completed" in status:
            return status["completed"] is True
        return status.get("status_str") == "success"

    def _image_names(self, entry: dict[str, Any]) -> tuple[str, ...]:
        names: list[str] = []
        for output in (entry.get("outputs") or {}).values():
            for image in output.get("images") or []:
                filename = str(image.get("filename") or "").strip()
                if filename:
                    names.append(filename)
        return tuple(names)

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

    def _wait_until_complete(self, prompt_id: str) -> dict[str, Any]:
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
            if self._image_names(entry):
                return entry
        raise TimeoutError(
            f"Timed out after {self._POLL_TIMEOUT_SECONDS}s waiting for image outputs "
            f"from prompt_id {prompt_id}."
        )

    def _workflow(
        self,
        filename_prefix: str,
        width: int,
        height: int,
        positive_prompt: str,
        negative_prompt: str,
        seed: int,
        batch_size: int,
    ) -> dict[str, Any]:
        workflow = copy.deepcopy(self._template)
        workflow["3"]["inputs"]["text"] = positive_prompt
        workflow["4"]["inputs"]["text"] = negative_prompt
        workflow["8"]["inputs"]["width"] = width
        workflow["8"]["inputs"]["height"] = height
        workflow["8"]["inputs"]["batch_size"] = batch_size
        workflow["11"]["inputs"]["filename_prefix"] = filename_prefix
        workflow["7"]["inputs"]["seed"] = seed
        return workflow
