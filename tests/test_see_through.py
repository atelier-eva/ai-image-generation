import os
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

from ai_media_generation.infrastructure.error import InfrastructureError
from ai_media_generation.infrastructure.see_through import SeeThrough, _png_max_alpha

_COMFY_ENV = {
    "COMFY_UI_URL": "http://127.0.0.1:8188",
    "COMFY_UI_CKPT_NAME": "animagine-xl-4.0-opt.safetensors",
    "COMFY_UI_FILENAME_PREFIX": "lora",
}

_STUB_SCRIPT = r"""
import argparse
import struct
import zlib
from pathlib import Path

PNG_SIG = b"\x89PNG\r\n\x1a\n"


def chunk(tag: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def write_rgba(path: Path, width: int, height: int, rgba: bytes) -> None:
    stride = width * 4
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        raw.extend(rgba[y * stride : (y + 1) * stride])
    compressed = zlib.compress(bytes(raw), 9)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    path.write_bytes(
        PNG_SIG + chunk(b"IHDR", ihdr) + chunk(b"IDAT", compressed) + chunk(b"IEND", b"")
    )


parser = argparse.ArgumentParser()
parser.add_argument("--srcp", required=True)
parser.add_argument("--save_dir", required=True)
parser.add_argument("--seed", type=int, default=42)
parser.add_argument("--repo_id_layerdiff", default="")
parser.add_argument("--repo_id_depth", default="")
parser.add_argument("--disable_progressbar", action="store_true")
args = parser.parse_args()
src = Path(args.srcp)
if not src.is_file():
    raise SystemExit(f"missing image {src}")
out = Path(args.save_dir) / src.stem / "optimized"
out.mkdir(parents=True, exist_ok=True)
opaque = bytes([10, 20, 30, 255] * 4)
empty = bytes([0, 0, 0, 0] * 4)
write_rgba(out / "face.png", 2, 2, opaque)
write_rgba(out / "front hair.png", 2, 2, opaque)
write_rgba(out / "tail.png", 2, 2, empty)
write_rgba(out / "src_img.png", 2, 2, opaque)
write_rgba(out / "face_depth.png", 2, 2, opaque)
(out / "info.json").write_text("{}", encoding="utf-8")
"""


def _write_rgba_png(
    path: Path, width: int, height: int, rgba: bytes, filter_type: int = 0
) -> None:
    stride = width * 4
    raw = bytearray()
    previous = bytes(stride)
    for y in range(height):
        row = bytearray(rgba[y * stride : (y + 1) * stride])
        raw.append(filter_type)
        if filter_type == 2:
            raw.extend((row[i] - previous[i]) & 255 for i in range(stride))
        else:
            raw.extend(row)
        previous = bytes(row)
    compressed = zlib.compress(bytes(raw), 9)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", compressed)
        + chunk(b"IEND", b"")
    )


class SeeThroughTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.root = Path(self._tmpdir.name) / "see-through"
        script_dir = self.root / "inference" / "scripts"
        script_dir.mkdir(parents=True)
        self.script = script_dir / "inference_psd.py"
        self.script.write_text(_STUB_SCRIPT, encoding="utf-8")
        self.save_dir = Path(self._tmpdir.name) / "work"
        self.image = Path(self._tmpdir.name) / "hero.png"
        _write_rgba_png(self.image, 2, 2, bytes([255, 0, 0, 255] * 4))
        self._environ = os.environ.copy()
        os.environ.update(_COMFY_ENV)
        os.environ["SEE_THROUGH_ROOT"] = str(self.root)
        os.environ["SEE_THROUGH_PYTHON"] = str(Path(sys.executable).resolve())
        os.environ["SEE_THROUGH_SAVE_DIRECTORY"] = str(self.save_dir)
        os.environ["SEE_THROUGH_TIMEOUT_SECONDS"] = "30"
        self.addCleanup(self._restore_environ)

    def _restore_environ(self) -> None:
        os.environ.clear()
        os.environ.update(self._environ)

    def test_requires_root(self) -> None:
        del os.environ["SEE_THROUGH_ROOT"]
        with self.assertRaises(ValueError) as raised:
            SeeThrough()
        self.assertIn("SEE_THROUGH_ROOT", str(raised.exception))

    def test_check_environment_rejects_missing_script(self) -> None:
        self.script.unlink()
        with self.assertRaises(InfrastructureError) as raised:
            SeeThrough().check_environment()
        self.assertIn("inference script not found", str(raised.exception))

    def test_decompose_keeps_character_parts_and_drops_empty(self) -> None:
        layers = SeeThrough().decompose(self.image, seed=7)
        parts = tuple(layer.part for layer in layers)
        self.assertEqual(parts, ("front hair", "face"))
        dest = Path(self._tmpdir.name) / "out"
        written = SeeThrough().write_layers(layers, dest)
        self.assertEqual(written, 2)
        self.assertTrue((dest / "front hair.png").is_file())
        self.assertTrue((dest / "face.png").is_file())
        self.assertFalse((dest / "tail.png").exists())
        self.assertFalse((dest / "src_img.png").exists())
        self.assertFalse((dest / "face_depth.png").exists())

    def test_decompose_times_out(self) -> None:
        os.environ["SEE_THROUGH_TIMEOUT_SECONDS"] = "1"
        self.script.write_text("import time\ntime.sleep(5)\n", encoding="utf-8")
        with self.assertRaises(InfrastructureError) as raised:
            SeeThrough().decompose(self.image)
        self.assertIn("Timed out", str(raised.exception))

    def test_decompose_missing_image(self) -> None:
        with self.assertRaises(FileNotFoundError):
            SeeThrough().decompose(self.image.parent / "missing.png")

    def test_decompose_reports_cli_failure(self) -> None:
        self.script.write_text("raise SystemExit('boom')\n", encoding="utf-8")
        with self.assertRaises(InfrastructureError) as raised:
            SeeThrough().decompose(self.image)
        self.assertIn("inference_psd.py failed", str(raised.exception))
        self.assertIn("boom", str(raised.exception))

    def test_png_up_filter_alpha(self) -> None:
        path = Path(self._tmpdir.name) / "filtered.png"
        _write_rgba_png(path, 2, 2, bytes([1, 2, 3, 200] * 4), filter_type=2)
        self.assertEqual(_png_max_alpha(path), 200)


if __name__ == "__main__":
    unittest.main()
