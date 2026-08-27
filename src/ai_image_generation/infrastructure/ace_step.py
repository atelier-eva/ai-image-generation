import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from ai_image_generation.config import Config


class AceStep:
    _POLL_INTERVAL_SECONDS = 2
    _POLL_TIMEOUT_SECONDS = 1800

    @dataclass
    class SavedAudio:
        filename: str
        file: str

    def __init__(self) -> None:
        config = Config()
        url = config.ace_step_url
        if not url:
            raise ValueError("ACE_STEP_URL is not set.")
        self._url = url
        self._api_key = config.ace_step_api_key
        self._output_directory = config.output_directory

    def generate(
        self,
        filename_prefix: str,
        prompt: str,
        lyrics: str = "",
        thinking: bool = True,
        vocal_language: str = "en",
        audio_duration: float | None = None,
        bpm: int | None = None,
        audio_format: str = "mp3",
        inference_steps: int = 8,
        seed: int | None = None,
        batch_size: int = 1,
    ) -> tuple["AceStep.SavedAudio", ...]:
        prefix = filename_prefix.strip()
        if not prefix:
            raise ValueError("filename_prefix is empty.")
        body: dict[str, Any] = {
            "prompt": prompt,
            "lyrics": lyrics,
            "thinking": thinking,
            "vocal_language": vocal_language,
            "audio_format": audio_format,
            "inference_steps": inference_steps,
            "batch_size": batch_size,
            "task_type": "text2music",
        }
        if audio_duration is not None:
            body["audio_duration"] = audio_duration
        if bpm is not None:
            body["bpm"] = bpm
        if seed is None:
            body["use_random_seed"] = True
        else:
            body["use_random_seed"] = False
            body["seed"] = seed
        data = self._request("POST", "/release_task", body)
        if not isinstance(data, dict):
            raise RuntimeError("ACE-Step /release_task did not return an object.")
        task_id = str(data.get("task_id") or "").strip()
        if not task_id:
            raise RuntimeError("ACE-Step /release_task did not return task_id.")
        files = [
            file
            for item in self._wait_until_complete(task_id)
            if (file := str(item.get("file") or "").strip())
        ]
        if not files:
            raise RuntimeError("ACE-Step generation succeeded without audio files.")
        extension = self._extension(audio_format)
        if len(files) == 1:
            return (AceStep.SavedAudio(filename=f"{prefix}.{extension}", file=files[0]),)
        return tuple(
            AceStep.SavedAudio(filename=f"{prefix}_{index}.{extension}", file=file)
            for index, file in enumerate(files, start=1)
        )

    def fetch_audio(self, audio: "AceStep.SavedAudio") -> bytes:
        request = urllib.request.Request(
            self._audio_url(audio.file),
            headers=self._headers(),
            method="GET",
        )
        try:
            with urllib.request.urlopen(request) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            raise RuntimeError(self._http_error_message(audio.file, error)) from error
        except urllib.error.URLError as error:
            raise RuntimeError(f"ACE-Step is not reachable at {self._url}") from error

    def write_audio(self, audios: tuple["AceStep.SavedAudio", ...]) -> int:
        if not audios:
            raise RuntimeError("No saved audio from ACE-Step; cannot write audio.")
        written = 0
        for audio in audios:
            path = self._output_directory / audio.filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(self.fetch_audio(audio))
            written += 1
        return written

    def _audio_url(self, file: str) -> str:
        if file.startswith("http://") or file.startswith("https://"):
            return file
        if not file.startswith("/"):
            file = f"/{file}"
        return f"{self._url}{file}"

    def _extension(self, audio_format: str) -> str:
        text = audio_format.strip().lower().lstrip(".")
        if text == "wav32":
            return "wav"
        if not text:
            return "mp3"
        return text

    def _headers(self, content_type: str | None = None) -> dict[str, str]:
        headers: dict[str, str] = {}
        if content_type:
            headers["Content-Type"] = content_type
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    def _http_error_message(self, path: str, error: urllib.error.HTTPError) -> str:
        body = error.read().decode("utf-8", errors="replace").strip()
        if error.code == 401:
            return "ACE-Step authentication failed."
        if error.code == 429:
            return "ACE-Step queue is full."
        detail = body
        try:
            loaded = json.loads(body)
        except json.JSONDecodeError:
            loaded = None
        if isinstance(loaded, dict):
            if loaded.get("detail"):
                detail = str(loaded["detail"])
            elif loaded.get("error"):
                detail = str(loaded["error"])
        if detail:
            return f"ACE-Step {path} failed: {error.code} {detail}"
        return f"ACE-Step {path} failed: {error.code}"

    def _parse_result(self, result: Any) -> list[dict[str, Any]]:
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except json.JSONDecodeError as error:
                raise RuntimeError("ACE-Step result was not valid JSON.") from error
        if not isinstance(result, list):
            raise RuntimeError("ACE-Step result was not a list.")
        items: list[dict[str, Any]] = []
        for item in result:
            if not isinstance(item, dict):
                raise RuntimeError("ACE-Step result item was not an object.")
            items.append(item)
        return items

    def _request(
        self, method: str, path: str, body: dict[str, Any] | None = None
    ) -> Any:
        data = None
        content_type = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            content_type = "application/json; charset=utf-8"
        request = urllib.request.Request(
            f"{self._url}{path}",
            data=data,
            headers=self._headers(content_type),
            method=method,
        )
        try:
            with urllib.request.urlopen(request) as response:
                loaded = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            raise RuntimeError(self._http_error_message(path, error)) from error
        except urllib.error.URLError as error:
            raise RuntimeError(f"ACE-Step is not reachable at {self._url}") from error
        except json.JSONDecodeError as error:
            raise RuntimeError(f"ACE-Step {path} did not return JSON.") from error
        if not isinstance(loaded, dict):
            raise RuntimeError(f"ACE-Step {path} did not return an object.")
        code = loaded.get("code")
        if code not in (None, 200):
            message = loaded.get("error") or f"code {code}"
            raise RuntimeError(f"ACE-Step {path} failed: {message}")
        return loaded.get("data")

    def _wait_until_complete(self, task_id: str) -> list[dict[str, Any]]:
        deadline = time.monotonic() + self._POLL_TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            time.sleep(self._POLL_INTERVAL_SECONDS)
            data = self._request(
                "POST",
                "/query_result",
                {"task_id_list": [task_id]},
            )
            if not isinstance(data, list):
                raise RuntimeError("ACE-Step /query_result did not return a list.")
            entry = next(
                (
                    item
                    for item in data
                    if isinstance(item, dict)
                    and str(item.get("task_id") or "").strip() == task_id
                ),
                None,
            )
            if not entry:
                continue
            status = entry.get("status")
            if status == 2:
                raise RuntimeError(f"ACE-Step generation failed for task_id {task_id}.")
            if status != 1:
                continue
            return self._parse_result(entry.get("result"))
        raise TimeoutError(
            f"Timed out after {self._POLL_TIMEOUT_SECONDS}s waiting for audio "
            f"from task_id {task_id}."
        )
