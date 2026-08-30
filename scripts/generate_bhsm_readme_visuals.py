"""Generate the deterministic BHSM README visual suite.

The generator emits editable SVG, static PNG, and restrained animated GIF
variants.  Scientific-status labels are read from the adjacent JSON manifest;
no measured particle value or physical prediction is generated here.
"""

from __future__ import annotations

import argparse
import html
import json
import math
from pathlib import Path
from typing import Callable, Iterable, Sequence

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "docs" / "assets"
STATUS_PATH = ASSET_DIR / "bhsm_readme_visual_status.json"

W, H = 1280, 720
FRAMES = 16

C = {
    "bg": "#07111d",
    "bg2": "#0b1928",
    "panel": "#102338",
    "panel2": "#132b42",
    "grid": "#173149",
    "white": "#f1f6fa",
    "muted": "#9fb3c5",
    "cyan": "#43d7e8",
    "cyan2": "#1e8fa9",
    "gold": "#e2b85b",
    "gold2": "#8f6d2f",
    "red": "#e07a78",
    "green": "#71d4ad",
    "gray": "#6f8394",
    "black": "#03070b",
}


def color(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))


def font_path(bold: bool = False) -> str | None:
    candidates = [
        Path("C:/Windows/Fonts/seguisb.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    return str(next((item for item in candidates if item.exists()), candidates[-1]))


_FONTS: dict[tuple[int, bool], ImageFont.FreeTypeFont | ImageFont.ImageFont] = {}


def get_font(size: int, bold: bool = False):
    key = (size, bold)
    if key not in _FONTS:
        try:
            _FONTS[key] = ImageFont.truetype(font_path(bold), size)
        except OSError:
            _FONTS[key] = ImageFont.load_default()
    return _FONTS[key]


def wrap(text: str, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) <= width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


class Scene:
    def __init__(self, frame: int | None = None):
        self.frame = frame
        self.items: list[dict] = []

    def rect(self, box, fill, outline=None, width=1, radius=0, pulse=False):
        self.items.append({"kind": "rect", "box": box, "fill": fill, "outline": outline,
                           "width": width, "radius": radius, "pulse": pulse})

    def line(self, points, fill, width=2, dash=None, animated=False, delay=0.0):
        self.items.append({"kind": "line", "points": points, "fill": fill, "width": width,
                           "dash": dash, "animated": animated, "delay": delay})

    def ellipse(self, box, fill, outline=None, width=1, pulse=False):
        self.items.append({"kind": "ellipse", "box": box, "fill": fill, "outline": outline,
                           "width": width, "pulse": pulse})

    def polygon(self, points, fill, outline=None):
        self.items.append({"kind": "polygon", "points": points, "fill": fill, "outline": outline})

    def text(self, xy, value, size=24, fill=C["white"], bold=False, anchor="la"):
        self.items.append({"kind": "text", "xy": xy, "value": value, "size": size,
                           "fill": fill, "bold": bold, "anchor": anchor})

    def render(self) -> Image.Image:
        image = Image.new("RGB", (W, H), color(C["bg"]))
        draw = ImageDraw.Draw(image)
        for item in self.items:
            kind = item["kind"]
            if kind == "rect":
                outline = item["outline"]
                if item["pulse"] and self.frame is not None:
                    wave = 0.5 + 0.5 * math.sin(2 * math.pi * self.frame / FRAMES)
                    outline = C["cyan"] if wave > 0.45 else outline
                draw.rounded_rectangle(item["box"], radius=item["radius"], fill=item["fill"],
                                       outline=outline, width=item["width"])
            elif kind == "line":
                points = item["points"]
                draw.line(points, fill=item["fill"], width=item["width"], joint="curve")
                if item["animated"] and self.frame is not None:
                    t = (self.frame / FRAMES + item["delay"]) % 1.0
                    point = polyline_point(points, t)
                    r = max(3, item["width"] + 1)
                    draw.ellipse((point[0] - r, point[1] - r, point[0] + r, point[1] + r),
                                 fill=color(C["white"]), outline=color(C["cyan"]))
            elif kind == "ellipse":
                outline = item["outline"]
                draw.ellipse(item["box"], fill=item["fill"], outline=outline, width=item["width"])
            elif kind == "polygon":
                draw.polygon(item["points"], fill=item["fill"], outline=item["outline"])
            elif kind == "text":
                draw.text(item["xy"], item["value"], font=get_font(item["size"], item["bold"]),
                          fill=item["fill"], anchor=item["anchor"])
        return image

    def svg(self) -> str:
        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
            '<title>BHSM scientific workflow diagram</title>',
            '<desc>Deterministic claim-safe repository visual. Animated flow markers indicate computational direction.</desc>',
        ]
        for item in self.items:
            kind = item["kind"]
            if kind == "rect":
                x0, y0, x1, y1 = item["box"]
                attrs = f'x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" rx="{item["radius"]}" fill="{item["fill"]}"'
                if item["outline"]:
                    attrs += f' stroke="{item["outline"]}" stroke-width="{item["width"]}"'
                parts.append(f'<rect {attrs}/>')
            elif kind == "line":
                path = svg_path(item["points"])
                parts.append(f'<path d="{path}" fill="none" stroke="{item["fill"]}" stroke-width="{item["width"]}" stroke-linecap="round" stroke-linejoin="round"/>')
                if item["animated"]:
                    parts.append(f'<circle r="5" fill="{C["white"]}" stroke="{C["cyan"]}" stroke-width="2"><animateMotion dur="2.8s" repeatCount="indefinite" begin="{-item["delay"]*2.8:.2f}s" path="{path}"/></circle>')
            elif kind == "ellipse":
                x0, y0, x1, y1 = item["box"]
                attrs = f'cx="{(x0+x1)/2}" cy="{(y0+y1)/2}" rx="{(x1-x0)/2}" ry="{(y1-y0)/2}" fill="{item["fill"]}"'
                if item["outline"]:
                    attrs += f' stroke="{item["outline"]}" stroke-width="{item["width"]}"'
                parts.append(f'<ellipse {attrs}/>')
            elif kind == "polygon":
                points = " ".join(f"{x},{y}" for x, y in item["points"])
                parts.append(f'<polygon points="{points}" fill="{item["fill"]}"/>')
            elif kind == "text":
                x, y = item["xy"]
                anchor = {"la": "start", "ma": "middle", "ra": "end", "mm": "middle", "lm": "start", "rm": "end"}.get(item["anchor"], "start")
                baseline = "central" if item["anchor"] in {"mm", "lm", "rm"} else "auto"
                weight = "700" if item["bold"] else "400"
                parts.append(f'<text x="{x}" y="{y}" fill="{item["fill"]}" font-family="Segoe UI,Arial,sans-serif" font-size="{item["size"]}" font-weight="{weight}" text-anchor="{anchor}" dominant-baseline="{baseline}">{html.escape(item["value"])}</text>')
        parts.append("</svg>\n")
        return "".join(parts)


def polyline_point(points: Sequence[tuple[float, float]], t: float) -> tuple[float, float]:
    lengths = [math.dist(a, b) for a, b in zip(points, points[1:])]
    total = sum(lengths)
    target = t * total
    walked = 0.0
    for (a, b), length in zip(zip(points, points[1:]), lengths):
        if walked + length >= target:
            local = 0 if length == 0 else (target - walked) / length
            return a[0] + local * (b[0] - a[0]), a[1] + local * (b[1] - a[1])
        walked += length
    return points[-1]


def svg_path(points: Sequence[tuple[float, float]]) -> str:
    return "M " + " L ".join(f"{x} {y}" for x, y in points)


def background(scene: Scene, title: str, subtitle: str | None = None):
    scene.rect((0, 0, W, H), C["bg"])
    scene.rect((0, 0, W, 92), C["bg2"])
    for x in range(0, W + 1, 40):
        scene.line([(x, 92), (x, H)], C["grid"], 1)
    for y in range(92, H + 1, 40):
        scene.line([(0, y), (W, y)], C["grid"], 1)
    scene.line([(30, 82), (1250, 82)], C["cyan2"], 2)
    scene.text((40, 42), title, 34, C["white"], True, "lm")
    if subtitle:
        scene.text((1240, 44), subtitle, 17, C["muted"], False, "rm")


def node(scene: Scene, box, title: str, lines: Iterable[str] = (), accent=C["cyan"], pulse=False,
         title_size=22, body_size=16):
    scene.rect(box, C["panel"], accent, 2, 12, pulse)
    x0, y0, x1, y1 = box
    scene.rect((x0, y0, x0 + 7, y1), accent, None, 0, 4)
    scene.text(((x0 + x1) / 2, y0 + 29), title, title_size, C["white"], True, "mm")
    y = y0 + 58
    for line in lines:
        scene.text(((x0 + x1) / 2, y), line, body_size, C["muted"], False, "mm")
        y += body_size + 9


def arrow(scene: Scene, start, end, delay=0.0, color_value=C["cyan"], width=3, bend=None):
    if bend is None:
        points = [start, end]
    else:
        points = [start, bend, end]
    scene.line(points, color_value, width, animated=True, delay=delay)
    x, y = end
    angle = math.atan2(end[1] - points[-2][1], end[0] - points[-2][0])
    size = 10
    left = (x - size * math.cos(angle - 0.5), y - size * math.sin(angle - 0.5))
    right = (x - size * math.cos(angle + 0.5), y - size * math.sin(angle + 0.5))
    scene.polygon([end, left, right], color_value)


def badge(scene: Scene, box, text_value: str, accent=C["gold"]):
    scene.rect(box, C["black"], accent, 1, 12)
    scene.text(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2), text_value, 14, accent, True, "mm")


def hero(frame=None) -> Scene:
    s = Scene(frame)
    background(s, "BHSM — FROM GEOMETRY TO PREDICTION", "SHARED ACTION-DERIVED TRUNK")
    node(s, (40, 210, 245, 390), "GEOMETRY / ACTION", ["physical quotient", "frozen provenance"], C["gold"], True)
    node(s, (285, 210, 485, 390), "ACTION EXPANSION", ["S² spectrum", "S³ + S⁴ vertices"], C["cyan"], True)
    node(s, (525, 210, 725, 390), "PARTICLES +", ["propagator poles", "shared vertices"], C["cyan"], True)
    node(s, (765, 210, 940, 390), "AMPLITUDES", ["contact + exchange", "one engine"], C["cyan"], True)
    outputs = [(1000, 135, 1235, 205, "MAGNETIC MOMENT"), (1000, 225, 1235, 295, "DECAYS"),
               (1000, 315, 1235, 385, "COLLISIONS"), (1000, 405, 1235, 475, "SPECTRAL FORECASTS")]
    centers = [(245, 300), (485, 300), (725, 300), (940, 300)]
    for index, (a, b) in enumerate(zip(centers, centers[1:])):
        arrow(s, a, b, index * 0.14)
    for index, box in enumerate(outputs):
        node(s, box[:4], box[4], (), C["gold"] if index in {0, 3} else C["cyan"], title_size=18)
        arrow(s, (940, 300), (1000, (box[1] + box[3]) / 2), 0.45 + index * 0.11,
              bend=(970, (box[1] + box[3]) / 2))
    badge(s, (335, 525, 945, 565), "ACTION-OWNED • NO-FIT PREDICTION PIPELINE")
    s.rect((300, 592, 980, 646), C["panel2"], C["red"], 2, 10)
    s.text((640, 619), "PHYSICAL PROMOTION GATED PENDING FORMAL GATE 7 CLOSURE", 18, C["red"], True, "mm")
    return s


def universal(frame=None) -> Scene:
    s = Scene(frame)
    background(s, "UNIVERSAL PREDICTIVE ENGINE", "NO SEPARATE HANDWRITTEN READOUT RULES")
    boxes = [
        (25, 150, 220, 270, "BACKGROUND", ["certified domain", "physical quotient"]),
        (245, 150, 440, 270, "ACTION EXPANSION", ["S² • S³ • S⁴", "one provenance"]),
        (465, 150, 660, 270, "SPECTRUM", ["poles / residues", "propagators"]),
        (685, 150, 880, 270, "VERTICES", ["cubic + quartic", "action derivatives"]),
        (905, 150, 1255, 270, "AMPLITUDE ENGINE", ["M = contact + exchange", "crossed channels"]),
    ]
    for index, box in enumerate(boxes):
        node(s, box[:4], box[4], box[5], C["gold"] if index == 0 else C["cyan"], title_size=18)
        if index:
            arrow(s, (boxes[index-1][2], 210), (box[0], 210), index * 0.14)
    ownership = ["S² → poles / residues", "S³, S⁴ → vertices", "propagators + vertices → M"]
    for index, text_value in enumerate(ownership):
        badge(s, (80 + index * 390, 305, 420 + index * 390, 345), text_value, C["cyan"])
    labels = ["DECAY WIDTHS / LIFETIMES", "COLLISION CROSS SECTIONS", "F1 / F2 FORM FACTORS", "SPECTRAL FORECASTS", "STABILITY / SELECTION RULES"]
    for index, label in enumerate(labels):
        x0 = 25 + index * 250
        node(s, (x0, 430, x0 + 230, 520), label, (), C["gold"] if index in {2, 3} else C["cyan"], title_size=15)
        arrow(s, (1080, 270), (x0 + 115, 430), 0.15 * index, bend=(x0 + 115, 380))
    s.text((640, 622), "ENGINE CAPABILITY • PHYSICAL READOUTS REMAIN FAIL-CLOSED UNTIL PROMOTION GATES PASS", 16, C["red"], True, "mm")
    return s


def spectral(frame=None) -> Scene:
    s = Scene(frame)
    background(s, "BHSM SPECTRAL FORECAST", "STRUCTURAL / PROVISIONAL — NO INVENTED MASS SCALE")
    s.text((80, 155), "ACTION-DERIVED SPECTRAL COORDINATE", 20, C["white"], True, "la")
    s.text((1200, 155), "not a physical mass axis", 16, C["muted"], False, "ra")
    y = 360
    s.line([(80, y), (1200, y)], C["white"], 3, animated=True)
    for x in range(80, 1201, 140):
        s.line([(x, y - 8), (x, y + 8)], C["muted"], 2)
    s.rect((150, 245, 235, 360), C["panel2"], C["cyan"], 2, 6)
    s.text((192, 227), "ACTION-DERIVED", 14, C["cyan"], True, "mm")
    s.text((192, 260), "MODE", 16, C["white"], True, "mm")
    s.rect((310, 315, 480, 405), C["panel2"], C["gold"], 2, 6)
    s.text((395, 292), "ADMISSIBLE INTERVAL", 14, C["gold"], True, "mm")
    s.rect((550, 315, 720, 405), C["black"], C["red"], 2, 6)
    for x in range(550, 721, 18):
        s.line([(x, 315), (max(550, x - 50), 405)], C["red"], 1)
    s.text((635, 292), "SPECTRAL NULL WINDOW", 14, C["red"], True, "mm")
    s.rect((790, 300, 1010, 420), C["panel"], C["gray"], 2, 6)
    s.text((900, 277), "UNRESOLVED", 14, C["gray"], True, "mm")
    s.ellipse((1090, 323, 1164, 397), C["panel2"], C["cyan"], 3)
    s.text((1127, 360), "MODE", 14, C["white"], True, "mm")
    cards = [
        (100, "OPEN + NONZERO", "UNSTABLE", C["red"]),
        (385, "KINEMATICALLY CLOSED", "CHANNEL CLOSED", C["gold"]),
        (670, "EXACT ZERO", "SELECTION-RULE FORBIDDEN", C["cyan"]),
        (955, "INCOMPLETE LEDGER", "STABILITY UNRESOLVED", C["gray"]),
    ]
    for x, top, bottom, accent in cards:
        node(s, (x, 500, x + 225, 590), top, [bottom], accent, title_size=14, body_size=13)
    s.text((640, 660), "STABILITY IS CERTIFIED ONLY FROM A COMPLETE ACTION-DERIVED CHANNEL LEDGER", 15, C["muted"], True, "mm")
    return s


def gminus2(frame=None) -> Scene:
    s = Scene(frame)
    background(s, "MUON g−2 READOUT PIPELINE", "BASIS-INDEPENDENT F1 / F2 PROJECTION")
    boxes = [
        (30, 180, 220, 300, "S_BHSM", ["shared action"]),
        (255, 180, 455, 300, "μμγ VERTEX", ["action-owned mode"]),
        (490, 180, 690, 300, "Γᵘ(p′,p)", ["renormalized vertex"]),
        (725, 180, 935, 300, "F1(q²), F2(q²)", ["tensor projection"]),
        (970, 180, 1250, 300, "a_μ = F2(0)", ["only after all gates"]),
    ]
    for index, box in enumerate(boxes):
        node(s, box[:4], box[4], box[5], C["gold"] if index in {0, 4} else C["cyan"], title_size=20)
        if index:
            arrow(s, (boxes[index-1][2], 240), (box[0], 240), index * 0.16)
    s.rect((105, 365, 1175, 455), C["black"], C["cyan2"], 2, 10)
    s.text((640, 410), "Γᵘ = F1(q²) γᵘ + [i σᵘᵛ qᵥ / (2m_μ)] F2(q²) + …", 25, C["white"], False, "mm")
    badge(s, (140, 495, 1140, 540), "F2(0) ENGINE READY • NO NUMERICAL BHSM a_μ DISPLAYED", C["gold"])
    s.rect((220, 580, 1060, 638), C["panel2"], C["red"], 2, 10)
    s.text((640, 609), "PHYSICAL PREDICTION GATED: GATE 7 • WARD IDENTITY • RENORMALIZATION • EXTERNAL MODE", 15, C["red"], True, "mm")
    return s


def collision(frame=None) -> Scene:
    s = Scene(frame)
    background(s, "COLLISION PREDICTOR", "SHARED AMPLITUDE + PHASE-SPACE READOUT")
    s.text((95, 250), "e⁻", 38, C["white"], True, "mm")
    s.text((95, 390), "e⁺", 38, C["white"], True, "mm")
    node(s, (455, 220, 825, 420), "BHSM INTERACTION BLOCK", ["propagator + shared vertices", "contact + exchange", "no inserted cross section"], C["cyan"], True, 22, 17)
    s.text((1185, 250), "μ⁻", 38, C["white"], True, "mm")
    s.text((1185, 390), "μ⁺", 38, C["white"], True, "mm")
    arrow(s, (125, 250), (455, 285), 0.0)
    arrow(s, (125, 390), (455, 355), 0.2)
    arrow(s, (825, 285), (1150, 250), 0.4)
    arrow(s, (825, 355), (1150, 390), 0.6)
    s.rect((120, 470, 1160, 530), C["black"], C["gold"], 2, 10)
    s.text((640, 500), "M  →  |M|²  →  dσ/dΩ  →  σ_total", 28, C["white"], True, "mm")
    labels = ["THRESHOLDS", "PERMITTED", "FORBIDDEN", "RESONANCES", "WIDTHS", "BRANCHING"]
    for index, label in enumerate(labels):
        x0 = 70 + index * 200
        badge(s, (x0, 575, x0 + 170, 615), label, C["cyan"] if index % 2 == 0 else C["gold"])
    s.text((640, 665), "PROCESS SHOWN AS ENGINE TOPOLOGY • NO NUMERICAL CROSS SECTION CLAIMED", 15, C["red"], True, "mm")
    return s


def decay(frame=None) -> Scene:
    s = Scene(frame)
    background(s, "DECAY / STABILITY ENGINE", "COMPLETE LEDGER REQUIRED FOR A STABILITY CLAIM")
    node(s, (475, 125, 805, 220), "BHSM STATE", ["action-derived mode interval"], C["gold"], True, 24)
    branches = [
        (60, 360, 280, 470, "ALLOWED", ["open + nonzero", "contributes Γ_f"], C["green"]),
        (365, 360, 585, 470, "FORBIDDEN", ["exact selection rule", "Γ_f = 0"], C["cyan"]),
        (670, 360, 890, 470, "CLOSED", ["threshold not reached", "Γ_f = 0"], C["gold"]),
        (975, 360, 1195, 470, "UNRESOLVED", ["interval overlap", "no verdict"], C["gray"]),
    ]
    for index, box in enumerate(branches):
        node(s, box[:4], box[4], box[5], box[6], title_size=19)
        arrow(s, (640, 220), ((box[0] + box[2]) / 2, box[1]), index * 0.16,
              color_value=box[6], bend=((box[0] + box[2]) / 2, 285))
    s.rect((190, 525, 1090, 580), C["black"], C["cyan2"], 2, 10)
    s.text((640, 552), "Γ_i = Σ_f Γ_(i→f)       •       τ_i = ℏ / Γ_i", 25, C["white"], True, "mm")
    badge(s, (250, 620, 1030, 662), "STABLE ONLY IF A COMPLETE LEDGER PROVES NO OPEN NONZERO CHANNEL", C["red"])
    return s


def firewall(frame=None) -> Scene:
    s = Scene(frame)
    background(s, "INPUTS vs OUTPUTS", "THE NO-FIT PREDICTION FIREWALL")
    node(s, (45, 145, 375, 610), "BHSM INPUTS", ["geometry / topology", "frozen action", "physical domain / quotient", "universal scale calibration", "boundary / mode structure"], C["gold"], title_size=24, body_size=19)
    s.rect((455, 125, 825, 630), C["black"], C["red"], 3, 18, True)
    s.text((640, 180), "PREDICTION", 27, C["red"], True, "mm")
    s.text((640, 216), "FIREWALL", 27, C["red"], True, "mm")
    message = "MEASURED PARTICLE VALUES MAY NOT SELECT UPSTREAM BRANCHES, NORMALIZATIONS, MODES, OR FORMULAS"
    for index, line in enumerate(wrap(message, 24)):
        s.text((640, 300 + index * 42), line, 22, C["white"], True, "mm")
    s.line([(478, 565), (802, 565)], C["red"], 3, animated=True)
    s.text((640, 595), "FAIL CLOSED", 18, C["red"], True, "mm")
    node(s, (905, 115, 1235, 640), "BHSM OUTPUTS", ["spectrum / poles", "vertices / mixing", "decays / lifetimes", "cross sections", "magnetic moments", "new-particle intervals", "null spectral regions"], C["cyan"], title_size=24, body_size=18)
    arrow(s, (375, 380), (455, 380), 0.0, C["gold"])
    arrow(s, (825, 380), (905, 380), 0.5, C["cyan"])
    return s


VISUALS: dict[str, Callable[[int | None], Scene]] = {
    "bhsm_geometry_to_prediction": hero,
    "bhsm_universal_predictive_engine": universal,
    "bhsm_spectral_forecast": spectral,
    "bhsm_muon_g2_pipeline": gminus2,
    "bhsm_collision_predictor": collision,
    "bhsm_decay_stability_engine": decay,
    "bhsm_no_fit_firewall": firewall,
}


def validate_status() -> dict:
    status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    if status["promotion"]["gate7_closed"]:
        raise RuntimeError("visual manifest unexpectedly promotes Gate 7")
    if status["capabilities"]["complete_physical_predictions"]:
        raise RuntimeError("visual manifest unexpectedly claims complete predictions")
    if status["spectral_visualization"]["physical_mass_scale_available"]:
        raise RuntimeError("visual suite is intentionally non-numeric until a physical scale exists")
    return status


def save_gif(builder: Callable[[int | None], Scene], path: Path):
    frames = [builder(index).render() for index in range(FRAMES)]
    palette = frames[0].convert("P", palette=Image.Palette.ADAPTIVE, colors=128)
    converted = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    converted[0].save(path, save_all=True, append_images=converted[1:], duration=120,
                      loop=0, optimize=True, disposal=2)


def generate(selected: Iterable[str]):
    validate_status()
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    for name in selected:
        builder = VISUALS[name]
        scene = builder(None)
        (ASSET_DIR / f"{name}.svg").write_text(scene.svg(), encoding="utf-8", newline="\n")
        scene.render().save(ASSET_DIR / f"{name}.png", optimize=True)
        save_gif(builder, ASSET_DIR / f"{name}_animated.gif")
        print(f"generated {name}: svg, png, animated gif")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", choices=sorted(VISUALS), action="append",
                        help="generate one named visual; repeat for more")
    args = parser.parse_args()
    generate(args.only or VISUALS.keys())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
