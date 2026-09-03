import struct
import subprocess
import zlib
from dataclasses import dataclass
from pathlib import Path

from ai_media_generation.config import Config
from ai_media_generation.infrastructure.error import InfrastructureError

_INFERENCE_SCRIPT = ("inference", "scripts", "inference_psd.py")
_LAYERDIFF_REPO_ID = "layerdifforg/seethroughv0.0.2_layerdiff3d"
_MARIGOLD_REPO_ID = "24yearsold/seethroughv0.0.1_marigold"
_SKIP_STEMS = frozenset(
    {"src_img", "src_head", "reconstruction", "head", "final"}
)
_V3_PARTS = (
    "front hair",
    "back hair",
    "headwear",
    "face",
    "irides",
    "eyebrow",
    "eyewhite",
    "eyelash",
    "eyewear",
    "ears",
    "earwear",
    "nose",
    "mouth",
    "neck",
    "neckwear",
    "topwear",
    "handwear",
    "bottomwear",
    "legwear",
    "footwear",
    "tail",
    "wings",
    "objects",
)
_V3_PART_SET = frozenset(_V3_PARTS)
_EMPTY_ALPHA = 15
_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_ERROR_LOG_LIMIT = 4000


class SeeThrough:
    @dataclass(frozen=True)
    class Layer:
        part: str
        path: Path

    def __init__(self) -> None:
        config = Config()
        root = config.see_through_root
        python = config.see_through_python
        if not root:
            raise ValueError("SEE_THROUGH_ROOT is not set.")
        if not python:
            raise ValueError("SEE_THROUGH_PYTHON is not set.")
        self._root = Path(root).expanduser().resolve()
        self._python = _command(python)
        self._save_directory = config.see_through_save_directory
        self._timeout_seconds = config.see_through_timeout_seconds
        self._script = self._root.joinpath(*_INFERENCE_SCRIPT)

    def check_environment(self) -> None:
        if not self._root.is_dir():
            raise InfrastructureError(
                f"See-through root is not a directory: {self._root}"
            )
        if not self._script.is_file():
            raise InfrastructureError(
                f"See-through inference script not found: {self._script}"
            )
        try:
            completed = subprocess.run(
                [
                    self._python,
                    "-c",
                    "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')",
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except FileNotFoundError as error:
            raise InfrastructureError(
                f"See-through Python was not found: {self._python}"
            ) from error
        except subprocess.TimeoutExpired as error:
            raise InfrastructureError(
                "Timed out checking See-through Python."
            ) from error
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or "").strip()
            suffix = f" {detail}" if detail else ""
            raise InfrastructureError(
                f"See-through Python failed to start: {self._python}.{suffix}"
            )

    def decompose(self, image_path: str | Path, seed: int = 42) -> tuple["SeeThrough.Layer", ...]:
        image = Path(image_path).expanduser().resolve()
        if not image.is_file():
            raise FileNotFoundError(f"Image not found: {image}")
        self.check_environment()
        save_dir = self._save_directory
        save_dir.mkdir(parents=True, exist_ok=True)
        command = [
            self._python,
            str(self._script),
            "--srcp",
            str(image),
            "--save_dir",
            str(save_dir),
            "--seed",
            str(seed),
            "--repo_id_layerdiff",
            _LAYERDIFF_REPO_ID,
            "--repo_id_depth",
            _MARIGOLD_REPO_ID,
            "--disable_progressbar",
        ]
        try:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=self._timeout_seconds,
                cwd=str(self._root),
            )
        except subprocess.TimeoutExpired as error:
            raise InfrastructureError(
                f"Timed out after {self._timeout_seconds}s waiting for "
                f"See-through inference_psd.py."
            ) from error
        if completed.returncode != 0:
            raise InfrastructureError(
                "See-through inference_psd.py failed: "
                f"{_command_error(completed)}"
            )
        layers = self._layers(save_dir / image.stem)
        if not layers:
            raise InfrastructureError(
                "See-through produced no character layers "
                f"under {save_dir / image.stem}."
            )
        return layers

    def write_layers(
        self, layers: tuple["SeeThrough.Layer", ...], directory: Path
    ) -> int:
        if not layers:
            raise InfrastructureError(
                "No See-through layers; cannot write layers."
            )
        directory.mkdir(parents=True, exist_ok=True)
        written = 0
        for layer in layers:
            if not layer.path.is_file():
                raise FileNotFoundError(f"Layer not found: {layer.path}")
            destination = directory / _layer_filename(layer)
            destination.write_bytes(layer.path.read_bytes())
            written += 1
        return written

    def _layers(self, run_directory: Path) -> tuple["SeeThrough.Layer", ...]:
        if not run_directory.is_dir():
            return ()
        optimized = run_directory / "optimized"
        source = optimized if _has_part_pngs(optimized) else run_directory
        found: dict[str, Path] = {}
        for path in sorted(source.iterdir()):
            part = _part_name(path)
            if part is None:
                continue
            if not _has_visible_pixels(path):
                continue
            found[part] = path
        return tuple(
            SeeThrough.Layer(part=part, path=found[part])
            for part in _V3_PARTS
            if part in found
        )


def _command(value: str) -> str:
    path = Path(value).expanduser()
    if path.exists():
        return str(path.resolve())
    return value


def _command_error(completed: subprocess.CompletedProcess[str]) -> str:
    text = (completed.stderr or completed.stdout or "").strip()
    if not text:
        return f"exit {completed.returncode}"
    if len(text) > _ERROR_LOG_LIMIT:
        text = text[-_ERROR_LOG_LIMIT:]
    return f"exit {completed.returncode}: {text}"


def _has_part_pngs(directory: Path) -> bool:
    if not directory.is_dir():
        return False
    return any(_part_name(path) is not None for path in directory.iterdir())


def _has_visible_pixels(path: Path) -> bool:
    alpha = _png_max_alpha(path)
    if alpha is None:
        return path.stat().st_size > 0
    return alpha >= _EMPTY_ALPHA


def _layer_filename(layer: SeeThrough.Layer) -> str:
    suffix = layer.path.suffix.lower() or ".png"
    return f"{layer.part}{suffix}"


def _part_name(path: Path) -> str | None:
    if not path.is_file():
        return None
    if path.suffix.lower() != ".png":
        return None
    stem = path.stem
    if stem.endswith("_depth") or stem in _SKIP_STEMS:
        return None
    if stem in _V3_PART_SET:
        return stem
    return None


def _png_max_alpha(path: Path) -> int | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if len(data) < 33 or not data.startswith(_PNG_SIGNATURE):
        return None
    width = height = bit_depth = color_type = interlace = None
    idat = bytearray()
    offset = 8
    while offset + 12 <= len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk = data[offset + 4 : offset + 8]
        start = offset + 8
        end = start + length
        if end + 4 > len(data):
            return None
        payload = data[start:end]
        offset = end + 4
        if chunk == b"IHDR" and length >= 13:
            width, height, bit_depth, color_type, _, _, interlace = struct.unpack(
                ">IIBBBBB", payload[:13]
            )
        elif chunk == b"IDAT":
            idat.extend(payload)
        elif chunk == b"IEND":
            break
    if None in (width, height, bit_depth, color_type, interlace):
        return None
    if bit_depth != 8 or interlace != 0 or color_type not in (2, 4, 6):
        return None
    channels = {2: 3, 4: 2, 6: 4}[color_type]
    try:
        raw = zlib.decompress(bytes(idat))
    except zlib.error:
        return None
    stride = width * channels
    expected = height * (1 + stride)
    if len(raw) != expected:
        return None
    rows = _png_unfilter(raw, height, stride, channels)
    if not rows:
        return None
    if color_type == 2:
        return 255 if any(any(pixel for pixel in row) for row in rows) else 0
    max_alpha = 0
    alpha_index = 1 if color_type == 4 else 3
    for row in rows:
        max_alpha = max(max_alpha, max(row[alpha_index::channels], default=0))
        if max_alpha >= 255:
            return max_alpha
    return max_alpha


def _png_unfilter(
    raw: bytes, height: int, stride: int, channels: int
) -> list[bytes]:
    rows: list[bytes] = []
    previous = bytes(stride)
    offset = 0
    for _ in range(height):
        filter_type = raw[offset]
        scan = bytearray(raw[offset + 1 : offset + 1 + stride])
        offset += 1 + stride
        if filter_type == 1:
            for index in range(stride):
                left = scan[index - channels] if index >= channels else 0
                scan[index] = (scan[index] + left) & 255
        elif filter_type == 2:
            for index in range(stride):
                scan[index] = (scan[index] + previous[index]) & 255
        elif filter_type == 3:
            for index in range(stride):
                left = scan[index - channels] if index >= channels else 0
                scan[index] = (scan[index] + ((left + previous[index]) // 2)) & 255
        elif filter_type == 4:
            for index in range(stride):
                left = scan[index - channels] if index >= channels else 0
                up = previous[index]
                up_left = previous[index - channels] if index >= channels else 0
                scan[index] = (scan[index] + _paeth(left, up, up_left)) & 255
        elif filter_type != 0:
            return []
        row = bytes(scan)
        rows.append(row)
        previous = row
    return rows


def _paeth(left: int, up: int, up_left: int) -> int:
    estimate = left + up - up_left
    distance_left = abs(estimate - left)
    distance_up = abs(estimate - up)
    distance_up_left = abs(estimate - up_left)
    if distance_left <= distance_up and distance_left <= distance_up_left:
        return left
    if distance_up <= distance_up_left:
        return up
    return up_left
