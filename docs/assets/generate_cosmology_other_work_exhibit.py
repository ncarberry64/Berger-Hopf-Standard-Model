"""Generate the museum's cosmology other-work exhibit.

The display summarizes the mechanism proposed in Norman P. Carberry's
non-peer-reviewed preprint 10.20944/preprints202601.1427.v1. It is a schematic
model visualization, not an observational data product or an established
cosmological result.
"""

from __future__ import annotations

import base64
import io
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
W, H = 1280, 720
FRAMES = 40
BG = "#06111c"
PANEL = "#0c1d2c"
GRID = "#17364c"
INK = "#eef6f8"
MUTED = "#9bb0bf"
CYAN = "#43d7e8"
GOLD = "#e5bc63"
GREEN = "#63d6a3"
VIOLET = "#a9a0ff"
RED = "#e37d7d"

FONT = Path("C:/Windows/Fonts/segoeui.ttf")
BOLD = Path("C:/Windows/Fonts/segoeuib.ttf")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(BOLD if bold else FONT), size)


def text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    value: str,
    size: int,
    fill: str = INK,
    *,
    bold: bool = False,
    anchor: str = "la",
) -> None:
    draw.text(xy, value, font=font(size, bold), fill=fill, anchor=anchor)


def panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    draw.rounded_rectangle(box, radius=12, fill=PANEL, outline=GRID, width=2)


def axes(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    xlabel: str,
) -> None:
    x0, y0, x1, y1 = box
    for i in range(1, 6):
        x = x0 + i * (x1 - x0) / 6
        y = y0 + i * (y1 - y0) / 6
        draw.line((x, y0, x, y1), fill=GRID, width=1)
        draw.line((x0, y, x1, y), fill=GRID, width=1)
    draw.line((x0, y1, x1, y1), fill=MUTED, width=2)
    draw.line((x0, y0, x0, y1), fill=MUTED, width=2)
    text(draw, ((x0 + x1) / 2, y1 + 23), xlabel, 15, MUTED, anchor="ma")


def color_mix(a: tuple[int, int, int], b: tuple[int, int, int], u: float) -> tuple[int, int, int]:
    return tuple(round(x + (y - x) * u) for x, y in zip(a, b))


def gaussian(z: float, center: float, width: float) -> float:
    return math.exp(-0.5 * ((z - center) / width) ** 2)


def cosmology_frame(k: int) -> Image.Image:
    image = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(image)
    phase = 2 * math.pi * k / FRAMES

    draw.rectangle((0, 0, W, 92), fill="#091827")
    draw.line((36, 82, W - 36, 82), fill=CYAN, width=2)
    text(draw, (40, 37), "HYPERSPHERICAL SCALAR-TOPOGRAPHY MONITOR", 29, bold=True)
    text(draw, (W - 40, 39), "OTHER WORK / COSMOLOGY", 16, MUTED, bold=True, anchor="ra")

    panel(draw, (36, 116, 714, 638))
    panel(draw, (738, 116, 1244, 638))
    text(draw, (58, 142), "Long-wavelength mode on S3(R_H)", 22, bold=True)
    text(draw, (760, 142), "Shared redshift projection", 22, bold=True)

    cx, cy, radius = 365, 382, 194
    cyan_rgb = (67, 215, 232)
    gold_rgb = (229, 188, 99)
    for x in range(cx - radius + 2, cx + radius - 1, 7):
        normalized = (x - cx) / radius
        extent = radius * math.sqrt(max(0.0, 1 - normalized**2))
        mode = 0.5 + 0.5 * math.cos(math.pi * normalized - phase * 0.22)
        color = color_mix(cyan_rgb, gold_rgb, mode)
        draw.line((x, cy - extent, x, cy + extent), fill=color, width=8)

    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=INK, width=3)
    for squash in (0.28, 0.56):
        ry = radius * squash
        draw.ellipse((cx - radius, cy - ry, cx + radius, cy + ry), outline=GRID, width=2)
    for squash in (0.32, 0.62):
        rx = radius * squash
        draw.ellipse((cx - rx, cy - radius, cx + rx, cy + radius), outline=GRID, width=2)

    axis_angle = -0.30 + 0.08 * math.sin(phase)
    dx, dy = math.cos(axis_angle), math.sin(axis_angle)
    x0, y0 = cx - radius * 0.92 * dx, cy + radius * 0.92 * dy
    x1, y1 = cx + radius * 0.92 * dx, cy - radius * 0.92 * dy
    draw.line((x0, y0, x1, y1), fill=INK, width=3)
    draw.ellipse((x0 - 9, y0 - 9, x0 + 9, y0 + 9), fill=CYAN, outline=INK, width=2)
    draw.ellipse((x1 - 9, y1 - 9, x1 + 9, y1 + 9), fill=GOLD, outline=INK, width=2)
    text(draw, (x0 - 12, y0 + 20), "low T", 16, CYAN, bold=True, anchor="ra")
    text(draw, (x1 + 12, y1 - 22), "high T", 16, GOLD, bold=True)

    pulse = 0.5 + 0.5 * math.sin(phase)
    for index in range(4):
        ring_radius = 36 + index * 38 + pulse * 12
        stretch = 1 + 0.08 * math.cos(phase + index * 0.7)
        draw.ellipse(
            (
                cx - ring_radius * stretch,
                cy - ring_radius / stretch,
                cx + ring_radius * stretch,
                cy + ring_radius / stretch,
            ),
            outline=INK if index == 3 else "#b9d4dc",
            width=2,
        )

    text(draw, (58, 598), "A single smooth mode changes distance projections by direction.", 17, MUTED)

    plot = (778, 188, 1204, 410)
    axes(draw, plot, "redshift z")
    curves = [
        ("K_BAO", CYAN, 0.55, 0.18),
        ("K_SN", GOLD, 0.23, 0.12),
        ("overlap", VIOLET, 0.32, 0.14),
    ]
    cursor_z = 1.2 * k / (FRAMES - 1)
    for row, (label, color, center, width) in enumerate(curves):
        baseline = plot[1] + 48 + row * 60
        points = []
        for sample in range(180):
            z = 1.2 * sample / 179
            amplitude = gaussian(z, center, width)
            points.append((plot[0] + sample / 179 * (plot[2] - plot[0]), baseline - amplitude * 37))
        draw.line(points, fill=color, width=4, joint="curve")
        text(draw, (plot[0] + 8, baseline - 43), label, 15, color, bold=True)
        value = gaussian(cursor_z, center, width)
        cursor_x = plot[0] + cursor_z / 1.2 * (plot[2] - plot[0])
        cursor_y = baseline - value * 37
        draw.ellipse((cursor_x - 6, cursor_y - 6, cursor_x + 6, cursor_y + 6), fill=INK, outline=color, width=2)

    cursor_x = plot[0] + cursor_z / 1.2 * (plot[2] - plot[0])
    draw.line((cursor_x, plot[1], cursor_x, plot[3]), fill=INK, width=2)

    cards = [
        ("CURVATURE SCALE", "R_H >= 24 Gpc", CYAN),
        ("BAO-SN TEST", "10^-3  ->  0.7-0.8 km s^-1 Mpc^-1", GOLD),
        ("H_EFF TRANSITION", "z about 0.4-0.5", VIOLET),
    ]
    for row, (label, value, color) in enumerate(cards):
        y = 458 + row * 51
        draw.rounded_rectangle((778, y, 1204, y + 40), radius=7, fill="#102538", outline=GRID, width=1)
        text(draw, (792, y + 20), label, 13, MUTED, bold=True, anchor="lm")
        text(draw, (1190, y + 20), value, 15, color, bold=True, anchor="rm")

    text(
        draw,
        (40, 688),
        "PREPRINT MODEL DISPLAY - SCHEMATIC - NOT PEER REVIEWED - ORDER-OF-MAGNITUDE COMPARISONS",
        15,
        GOLD,
        bold=True,
    )
    text(draw, (W - 40, 688), "DOI 10.20944/PREPRINTS202601.1427.V1", 14, MUTED, bold=True, anchor="ra")
    return image


def svg_document(still: Image.Image) -> str:
    data = io.BytesIO()
    still.save(data, format="PNG", optimize=True)
    encoded = base64.b64encode(data.getvalue()).decode("ascii")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720" data-visual-kind="preprint-model-display">
<title>Hyperspherical scalar-topography cosmology monitor</title>
<desc>Schematic animation of one long-wavelength scalar mode and its BAO, supernova, and effective-Hubble projection kernels. The cited preprint is not peer reviewed.</desc>
<metadata>Generator: docs/assets/generate_cosmology_other_work_exhibit.py; source DOI: 10.20944/preprints202601.1427.v1; scope: schematic preprint model display.</metadata>
<image width="1280" height="720" href="data:image/png;base64,{encoded}"/>
<line x1="778" y1="188" x2="778" y2="410" stroke="#eef6f8" stroke-width="3" opacity="0.7">
  <animate attributeName="x1" values="778;1204;778" dur="6s" repeatCount="indefinite"/>
  <animate attributeName="x2" values="778;1204;778" dur="6s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values="0;0.7;0" dur="6s" repeatCount="indefinite"/>
</line>
</svg>'''


def main() -> None:
    name = "cosmology_hyperspherical_scalar_topography"
    frames = [cosmology_frame(k) for k in range(FRAMES)]
    frames[-1].save(ROOT / f"{name}.png", optimize=True)
    frames[0].save(
        ROOT / f"{name}_animated.gif",
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=0,
        optimize=True,
    )
    (ROOT / f"{name}.svg").write_text(svg_document(frames[-1]), encoding="utf-8")
    print(f"generated {name}")


if __name__ == "__main__":
    main()
