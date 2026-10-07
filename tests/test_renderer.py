"""Renderer tests (no Home Assistant needed)."""

import importlib.util
from io import BytesIO
from pathlib import Path

from PIL import Image

_spec = importlib.util.spec_from_file_location(
    "renderer",
    Path(__file__).parent.parent / "custom_components" / "niimbridge" / "renderer.py",
)
renderer = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(renderer)


def _size(png: bytes) -> tuple[int, int]:
    return Image.open(BytesIO(png)).size


def test_item_label_matches_spec_size():
    spec = renderer.LabelSpec(320, 96)
    png = renderer.render_item_label(spec, "Drill", "A1", "Shed", "https://x/y")
    assert _size(png) == (320, 96)


def test_item_label_handles_long_name_and_no_extras():
    spec = renderer.LabelSpec(240, 120)
    assert _size(renderer.render_item_label(spec, "word " * 40)) == (240, 120)


def test_qr_percent_is_clamped():
    spec = renderer.LabelSpec(320, 96, qr_percent=500)
    assert _size(renderer.render_item_label(spec, "x", url="u")) == (320, 96)


def test_fit_image_scales_to_label():
    src = renderer.render_item_label(renderer.LabelSpec(640, 200), "Src")
    spec = renderer.LabelSpec(400, 240)
    assert _size(renderer.fit_image_to_label(spec, src)) == (400, 240)
