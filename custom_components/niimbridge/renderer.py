"""Label rendering. Pure Pillow/segno so it can be tested without Home Assistant."""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps
import segno


@dataclass(frozen=True)
class LabelSpec:
    """Geometry and typography for a label."""

    width: int
    height: int
    font_path: str | None = None
    font_size: int = 0  # 0 = auto-fit
    qr_percent: int = 90


def _font(spec: LabelSpec, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if spec.font_path:
        try:
            return ImageFont.truetype(spec.font_path, size)
        except OSError:
            pass
    return ImageFont.load_default(size)


def _wrap(
    draw: ImageDraw.ImageDraw, text: str, font: Any, max_width: int
) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=font) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _fit_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    spec: LabelSpec,
    box_w: int,
    box_h: int,
    max_size: int,
) -> tuple[list[str], Any]:
    """Return wrapped lines and the largest font that fits the box."""
    sizes = [spec.font_size] if spec.font_size > 0 else range(max_size, 7, -1)
    font = _font(spec, 8)
    lines: list[str] = [text]
    for size in sizes:
        font = _font(spec, size)
        lines = _wrap(draw, text, font, box_w)
        line_h = int(size * 1.15)
        widest = max((draw.textlength(line, font=font) for line in lines), default=0)
        if widest <= box_w and line_h * len(lines) <= box_h:
            break
    return lines, font


def _qr_image(data: str, size: int) -> Image.Image:
    buf = BytesIO()
    segno.make(data, error="m").save(buf, kind="png", scale=1, border=0)
    buf.seek(0)
    qr = Image.open(buf).convert("1")
    scale = max(1, size // qr.width)
    qr = qr.resize((qr.width * scale, qr.height * scale), Image.NEAREST)
    return qr


def render_item_label(
    spec: LabelSpec,
    name: str,
    asset_id: str = "",
    location: str = "",
    url: str = "",
) -> bytes:
    """Render the standard layout: QR on the left, name/asset/location on the right."""
    img = Image.new("1", (spec.width, spec.height), 1)
    draw = ImageDraw.Draw(img)
    pad = max(4, spec.height // 12)

    qr_data = url or asset_id or name
    qr_size = max(16, spec.height * min(100, max(30, spec.qr_percent)) // 100)
    qr = _qr_image(qr_data, qr_size)
    qr_x = pad if qr_size <= spec.height - 2 * pad else (spec.height - qr.height) // 2
    img.paste(qr, (qr_x, (spec.height - qr.height) // 2))

    text_x = qr_x + qr.width + pad
    box_w = spec.width - text_x - pad
    box_h = spec.height - 2 * pad

    secondary = " · ".join(part for part in (asset_id, location) if part)
    # Reserve roughly a third of the height for the secondary line when present.
    name_h = int(box_h * 0.65) if secondary else box_h
    lines, font = _fit_text(draw, name, spec, box_w, name_h, max_size=name_h)
    size = getattr(font, "size", 12)
    y = pad
    for line in lines:
        draw.text((text_x, y), line, font=font, fill=0)
        y += int(size * 1.15)

    if secondary:
        sec_h = spec.height - pad - y
        if sec_h >= 8:
            sec_lines, sec_font = _fit_text(
                draw, secondary, spec, box_w, sec_h, max_size=max(8, sec_h)
            )
            sec_size = getattr(sec_font, "size", 10)
            sy = spec.height - pad - int(sec_size * 1.15) * len(sec_lines)
            for line in sec_lines:
                draw.text((text_x, sy), line, font=sec_font, fill=0)
                sy += int(sec_size * 1.15)

    return _to_png(img)


def fit_image_to_label(spec: LabelSpec, png: bytes) -> bytes:
    """Scale an arbitrary image to fit the label, centred on white, 1-bit."""
    src = Image.open(BytesIO(png))
    if src.mode in ("RGBA", "LA", "P"):
        src = src.convert("RGBA")
        background = Image.new("RGBA", src.size, "white")
        src = Image.alpha_composite(background, src)
    src = src.convert("L")
    # A portrait source on a landscape label is almost certainly rotated.
    if (src.height > src.width) != (spec.height > spec.width):
        src = src.rotate(90, expand=True)
    src = ImageOps.contain(src, (spec.width, spec.height), Image.LANCZOS)
    canvas = Image.new("L", (spec.width, spec.height), 255)
    canvas.paste(src, ((spec.width - src.width) // 2, (spec.height - src.height) // 2))
    return _to_png(canvas.convert("1"))


def _to_png(img: Image.Image) -> bytes:
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
