"""Render the museum's share card using the welcome exhibit's linked geometry.

Requires Pillow. The checked-in PNG is served directly; builds need no renderer.
Usage: python museum/scripts/render-social-preview.py --font-dir C:/Windows/Fonts
"""

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def render(font_dir: Path) -> Path:
    scale = 2
    image = Image.new("RGB", (1200 * scale, 630 * scale), "#050608")
    draw = ImageDraw.Draw(image)
    amber, lavender, cyan = "#ffbc77", "#bda7f5", "#71e5eb"

    def line(points, fill, width=1):
        draw.line([(round(x * scale), round(y * scale)) for x, y in points],
                  fill=fill, width=round(width * scale), joint="curve")

    def text(x, y, label, size, fill, bold=False):
        font = ImageFont.truetype(str(font_dir / ("segoeuib.ttf" if bold else "segoeui.ttf")), size * scale)
        draw.text((x * scale, y * scale), label, font=font, fill=fill, anchor="lt")

    # Rounded amber cap and lavender baseline match the exhibit frames.
    draw.rounded_rectangle((28 * scale, 28 * scale, 1172 * scale, 602 * scale),
                           radius=40 * scale, outline="#342c3f", width=scale)
    line([(66, 31), (1135, 31)], amber, 8)
    line([(66, 599), (1135, 599)], lavender, 4)
    text(64, 73, "BHSM MUSEUM", 38, "#f8f5ef", True)
    text(66, 129, "BERGER–HOPF STANDARD MODEL", 16, lavender)
    text(62, 211, "Geometry, matter", 61, "#f8f5ef")
    text(62, 287, "and interaction.", 61, amber)
    text(66, 392, "Explore the science.", 25, "#f8f5ef")
    text(66, 433, "Geometry, evidence & open questions", 20, "#b9b5c5")

    # Same S3 linked-circle projection as GeometryField in science-console.tsx.
    colors = [amber, lavender, cyan]
    for f in range(24):
        phi = f * math.tau / 24
        points = []
        for i in range(201):
            t = i * math.tau / 200
            eta = 0.48
            d = 1 - math.sin(eta) * math.sin(t + phi)
            x = math.cos(eta) * math.cos(t) / d
            y = math.cos(eta) * math.sin(t) / d
            z = math.sin(eta) * math.cos(t + phi) / d
            a = 0.7
            xx = x * math.cos(a) - z * math.sin(a)
            zz = x * math.sin(a) + z * math.cos(a)
            points.append((902 + xx * 132, 280 + (y * 0.78 + zz * 0.38) * 132))
        line(points, colors[f % 3], 1.3 if f % 3 == 0 else 0.65)
    text(773, 479, "LINKED GEOMETRY", 16, lavender)
    line([(65, 519), (1135, 519)], "#342c3f")
    text(66, 548, "MATTER   /   FORCES   /   COSMOLOGY", 19, amber)
    text(873, 548, "Explore. Interact. Question.", 16, "#b9b5c5")

    output = Path(__file__).resolve().parents[1] / "public" / "bhsm-museum-social-2026-09-27.png"
    image.resize((1200, 630), Image.Resampling.LANCZOS).save(output, optimize=True)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font-dir", type=Path, required=True)
    print(render(parser.parse_args().font_dir))
