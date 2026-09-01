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
SIMULATED_SPECTRUM_PATH = ROOT / "data" / "museum" / "bhsm_simulated_particle_spectrum_v1.json"

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

    def ellipse(self, box, fill, outline=None, width=1, pulse=False, reveal=None):
        self.items.append({"kind": "ellipse", "box": box, "fill": fill, "outline": outline,
                           "width": width, "pulse": pulse, "reveal": reveal})

    def polygon(self, points, fill, outline=None):
        self.items.append({"kind": "polygon", "points": points, "fill": fill, "outline": outline})

    def text(self, xy, value, size=24, fill=C["white"], bold=False, anchor="la",
             pulse=False, delay=0.0):
        self.items.append({"kind": "text", "xy": xy, "value": value, "size": size,
                           "fill": fill, "bold": bold, "anchor": anchor,
                           "pulse": pulse, "delay": delay})

    def scan(self, x0, x1, y0, y1, fill=C["cyan"]):
        self.items.append({"kind": "scan", "x0": x0, "x1": x1, "y0": y0,
                           "y1": y1, "fill": fill})

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
                fill = item["fill"]
                if item["reveal"] is not None and self.frame is not None:
                    progress = self.frame / max(1, FRAMES - 1)
                    if progress < item["reveal"]:
                        fill = C["panel"]
                        outline = C["gray"]
                draw.ellipse(item["box"], fill=fill, outline=outline, width=item["width"])
            elif kind == "polygon":
                draw.polygon(item["points"], fill=item["fill"], outline=item["outline"])
            elif kind == "text":
                fill = item["fill"]
                if item["pulse"] and self.frame is not None:
                    phase = (self.frame / FRAMES - item["delay"]) % 1.0
                    if phase < 0.18:
                        fill = C["gold"]
                draw.text(item["xy"], item["value"], font=get_font(item["size"], item["bold"]),
                          fill=fill, anchor=item["anchor"])
            elif kind == "scan":
                progress = 0.0 if self.frame is None else self.frame / max(1, FRAMES - 1)
                x = item["x0"] + progress * (item["x1"] - item["x0"])
                draw.line([(x, item["y0"]), (x, item["y1"])], fill=item["fill"], width=3)
                draw.ellipse((x - 5, item["y0"] - 5, x + 5, item["y0"] + 5), fill=C["white"])
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
                if item["pulse"] and item["outline"]:
                    parts.append(f'<rect {attrs}><animate attributeName="stroke" values="{item["outline"]};{C["white"]};{item["outline"]}" dur="2.8s" repeatCount="indefinite"/></rect>')
                else:
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
                if item["reveal"] is not None:
                    delay = float(item["reveal"])
                    key = min(0.9, delay + 0.03)
                    parts.append(f'<ellipse {attrs} opacity="0"><animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;{delay:.2f};{key:.2f};0.94;1" dur="3.2s" repeatCount="indefinite"/></ellipse>')
                else:
                    parts.append(f'<ellipse {attrs}/>')
            elif kind == "polygon":
                points = " ".join(f"{x},{y}" for x, y in item["points"])
                parts.append(f'<polygon points="{points}" fill="{item["fill"]}"/>')
            elif kind == "text":
                x, y = item["xy"]
                anchor = {"la": "start", "ma": "middle", "ra": "end", "mm": "middle", "lm": "start", "rm": "end"}.get(item["anchor"], "start")
                baseline = "central" if item["anchor"] in {"mm", "lm", "rm"} else "auto"
                weight = "700" if item["bold"] else "400"
                body = html.escape(item["value"])
                if item["pulse"]:
                    parts.append(f'<text x="{x}" y="{y}" fill="{item["fill"]}" font-family="Segoe UI,Arial,sans-serif" font-size="{item["size"]}" font-weight="{weight}" text-anchor="{anchor}" dominant-baseline="{baseline}">{body}<animate attributeName="fill" values="{item["fill"]};{C["gold"]};{item["fill"]}" dur="2.8s" begin="{-item["delay"]*2.8:.2f}s" repeatCount="indefinite"/></text>')
                else:
                    parts.append(f'<text x="{x}" y="{y}" fill="{item["fill"]}" font-family="Segoe UI,Arial,sans-serif" font-size="{item["size"]}" font-weight="{weight}" text-anchor="{anchor}" dominant-baseline="{baseline}">{body}</text>')
            elif kind == "scan":
                parts.append(f'<line x1="{item["x0"]}" x2="{item["x0"]}" y1="{item["y0"]}" y2="{item["y1"]}" stroke="{item["fill"]}" stroke-width="3"><animate attributeName="x1" values="{item["x0"]};{item["x1"]}" dur="3.2s" repeatCount="indefinite"/><animate attributeName="x2" values="{item["x0"]};{item["x1"]}" dur="3.2s" repeatCount="indefinite"/></line>')
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


def crossed(scene: Scene, box, fill=C["red"]):
    x0, y0, x1, y1 = box
    scene.line([(x0, y0), (x1, y1)], fill, 3)
    scene.line([(x0, y1), (x1, y0)], fill, 3)


def hero(frame=None) -> Scene:
    s = Scene(frame)
    background(s, "BHSM — FROM GEOMETRY TO PREDICTION", "SHARED ACTION-DERIVED TRUNK")
    node(s, (40, 210, 245, 390), "GEOMETRY / ACTION", ["physical quotient", "frozen provenance"], C["gold"], True, 18)
    node(s, (285, 210, 485, 390), "ACTION EXPANSION", (), C["cyan"], True)
    s.text((335, 290), "S²", 22, C["muted"], True, "mm", True, 0.00)
    s.text((385, 290), "S³", 22, C["muted"], True, "mm", True, 0.18)
    s.text((435, 290), "S⁴", 22, C["muted"], True, "mm", True, 0.36)
    s.text((385, 330), "one action jet", 15, C["muted"], False, "mm")
    node(s, (525, 210, 725, 390), "MODES + VERTICES", ["propagator poles", "shared vertices"], C["cyan"], True, 18)
    node(s, (765, 210, 940, 390), "AMPLITUDES", ["contact + exchange", "one engine"], C["cyan"], True)
    outputs = [(1000, 135, 1235, 205, "MAGNETIC MOMENT"), (1000, 225, 1235, 295, "DECAYS"),
               (1000, 315, 1235, 385, "COLLISIONS"), (1000, 405, 1235, 475, "SPECTRAL FORECASTS")]
    trunk_edges = [((245, 300), (285, 300)), ((485, 300), (525, 300)), ((725, 300), (765, 300))]
    for index, (a, b) in enumerate(trunk_edges):
        arrow(s, a, b, index * 0.14)
    for index, box in enumerate(outputs):
        node(s, box[:4], box[4], (), C["gold"] if index in {0, 3} else C["cyan"], title_size=18)
        arrow(s, (940, 300), (1000, (box[1] + box[3]) / 2), 0.45 + index * 0.11,
              bend=(970, (box[1] + box[3]) / 2))
    badge(s, (300, 510, 980, 550), "ONE ACTION • ONE SCALE • ONE OBSERVABLE PIPELINE")
    badge(s, (430, 558, 850, 594), "ACTION-OWNED • NO-FIT", C["cyan"])
    s.rect((300, 612, 980, 666), C["panel2"], C["red"], 2, 10)
    s.text((640, 639), "AE2 STOP + EVENT CHILD DERIVED • LOCAL ENCLOSURE BRIDGE OPEN", 18, C["red"], True, "mm")
    return s


def universal(frame=None) -> Scene:
    s = Scene(frame)
    background(s, "UNIVERSAL PREDICTIVE ENGINE", "NO SEPARATE HANDWRITTEN READOUT RULES")
    boxes = [
        (25, 150, 220, 270, "FROZEN BACKGROUND", ["state registry retained", "physical quotient"]),
        (245, 150, 440, 270, "ACTION EXPANSION", ["S² • S³ • S⁴", "one provenance"]),
        (465, 150, 660, 270, "SPECTRUM", ["poles / residues", "propagators"]),
        (685, 150, 880, 270, "VERTICES", ["cubic + quartic", "action derivatives"]),
        (905, 150, 1255, 270, "AMPLITUDE ENGINE", ["M = contact + exchange", "crossed channels"]),
    ]
    for index, box in enumerate(boxes):
        node(s, box[:4], box[4], box[5], C["gold"] if index == 0 else C["cyan"], title_size=16 if index == 0 else 18)
        if index:
            arrow(s, (boxes[index-1][2], 210), (box[0], 210), index * 0.14)
    ownership = ["S² → poles / residues", "S³, S⁴ → vertices", "propagators + vertices → M"]
    for index, text_value in enumerate(ownership):
        badge(s, (80 + index * 390, 305, 420 + index * 390, 345), text_value, C["cyan"])
    node(s, (505, 365, 775, 430), "LSZ / ON-SHELL NORMALIZATION", (), C["gold"], True, 16)
    arrow(s, (1080, 270), (640, 365), 0.58, C["gold"], bend=(1080, 330))
    labels = ["DECAY WIDTHS / LIFETIMES", "COLLISION CROSS SECTIONS", "F1 / F2 FORM FACTORS", "SPECTRAL FORECASTS", "STABILITY / SELECTION RULES"]
    for index, label in enumerate(labels):
        x0 = 25 + index * 250
        node(s, (x0, 500, x0 + 230, 590), label, (), C["gold"] if index in {2, 3} else C["cyan"], title_size=15)
        arrow(s, (640, 430), (x0 + 115, 500), 0.15 * index, bend=(x0 + 115, 465))
    s.text((640, 650), "ENGINE CAPABILITY • ENCLOSURE TRANSPORT REMAINS FAIL-CLOSED UNTIL THE BRIDGE PASSES", 16, C["red"], True, "mm")
    return s


def spectral(frame=None) -> Scene:
    s = Scene(frame)
    background(s, "SPECTRAL FORECAST — BAND VIEW", "REPOSITORY-DERIVED STRUCTURE • PROVISIONAL")
    x0, x1 = 150, 1190
    y0, y1 = 165, 555
    s.text((58, 147), "CLASS", 14, C["muted"], True, "la")
    s.text((1190, 147), "NORMALIZED SPECTRAL COORDINATE ξ  (NOT MASS)", 15, C["muted"], False, "ra")
    for tick in range(6):
        x = x0 + tick * (x1 - x0) / 5
        s.line([(x, y0), (x, y1)], C["grid"], 1)
        s.text((x, y1 + 28), f"{tick / 5:.1f}", 13, C["muted"], False, "mm")
    rows = [
        (205, "MODE A", 0.10, 0.28, 0.06, C["cyan"]),
        (285, "MODE B", 0.34, 0.51, 0.04, C["gold"]),
        (365, "NULL", 0.56, 0.69, 0.00, C["red"]),
        (445, "MODE C", 0.73, 0.91, 0.08, C["gray"]),
    ]
    for row, label, lo, hi, uncertainty, accent in rows:
        s.text((118, row), label, 15, accent, True, "rm")
        s.line([(x0, row), (x1, row)], C["panel2"], 2)
        left = x0 + lo * (x1 - x0)
        right = x0 + hi * (x1 - x0)
        if uncertainty:
            outer_left = x0 + max(0.0, lo - uncertainty) * (x1 - x0)
            outer_right = x0 + min(1.0, hi + uncertainty) * (x1 - x0)
            s.rect((outer_left, row - 18, outer_right, row + 18), C["panel2"], accent, 1, 9)
        s.rect((left, row - 11, right, row + 11), accent, C["white"], 1, 6)
        if label == "NULL":
            for hatch_x in range(int(left), int(right) + 1, 18):
                s.line([(hatch_x, row - 11), (max(left, hatch_x - 18), row + 11)], C["black"], 1)
    s.scan(x0, x1, y0, y1)
    legend = [
        (170, C["cyan"], "ADMISSIBLE BAND"),
        (430, C["panel2"], "UNCERTAINTY ENVELOPE"),
        (760, C["red"], "NULL WINDOW"),
        (1010, C["gray"], "UNRESOLVED"),
    ]
    for x, accent, label in legend:
        s.rect((x, 615, x + 24, 631), accent, C["white"], 1, 3)
        s.text((x + 34, 624), label, 13, C["muted"], True, "lm")
    s.text((640, 682), "BAND WIDTH ENCODES INTERVAL AUTHORITY; THE SCAN LINE SHOWS CLASSIFICATION, NOT DISCOVERY", 14, C["white"], True, "mm")
    return s


def particle_spectrum(frame=None) -> Scene:
    payload = json.loads(SIMULATED_SPECTRUM_PATH.read_text(encoding="utf-8"))
    s = Scene(frame)
    background(s, "SIMULATED BHSM PARTICLE SPECTRUM", "MUSEUM DISPLAY DATA • NOT A PHYSICAL PREDICTION")
    x0, x1 = 120, 1200
    y0, y1 = 175, 570
    for tick in range(6):
        x = x0 + tick * (x1 - x0) / 5
        s.line([(x, y0), (x, y1)], C["grid"], 1)
        s.text((x, y1 + 27), f"{tick / 5:.1f}", 13, C["muted"], False, "mm")
    s.text((1200, 145), "DIMENSIONLESS DISPLAY COORDINATE ξ", 15, C["muted"], False, "ra")
    family_rows = {"lepton": 235, "gauge": 340, "quark": 445}
    family_colors = {"lepton": C["cyan"], "gauge": C["gold"], "quark": C["green"]}
    for family, row in family_rows.items():
        accent = family_colors[family]
        s.text((95, row), family.upper(), 14, accent, True, "rm")
        s.line([(x0, row), (x1, row)], C["panel2"], 2)
    for index, mode in enumerate(payload["modes"]):
        row = family_rows[mode["family"]]
        accent = family_colors[mode["family"]]
        x = x0 + float(mode["display_coordinate"]) * (x1 - x0)
        height = 28 + 40 * float(mode["relative_intensity"])
        reveal = 0.04 + index * 0.07
        s.line([(x, row), (x, row - height)], accent, 4)
        s.ellipse((x - 8, row - height - 8, x + 8, row - height + 8), accent, C["white"], 2, reveal=reveal)
        label_y = row + 27 if index % 2 == 0 else row + 48
        s.text((x, label_y), mode["label"], 12, C["white"], True, "mm")
    s.scan(x0, x1, y0, y1)
    badge(s, (220, 630, 1060, 670), "SIMULATED POSITIONS + INTENSITIES • FAMILIAR PARTICLE LABELS ARE REFERENCE IDENTITIES", C["gold"])
    return s


def gminus2(frame=None) -> Scene:
    s = Scene(frame)
    background(s, "MUON g−2 READOUT PIPELINE", "BASIS-INDEPENDENT F1 / F2 PROJECTION")
    boxes = [
        (30, 180, 220, 300, "S_BHSM", ["shared action"]),
        (255, 180, 455, 300, "μμγ VERTEX", ["action-owned mode"]),
        (490, 180, 690, 300, "Γ^μ(p′,p)", ["renormalized vertex"]),
        (725, 180, 935, 300, "F1(q²), F2(q²)", ["tensor projection"]),
        (970, 180, 1250, 300, "a_μ = F2(0)", ["only after all gates"]),
    ]
    for index, box in enumerate(boxes):
        node(s, box[:4], box[4], box[5], C["gold"] if index in {0, 4} else C["cyan"], pulse=index == 4, title_size=20)
        if index:
            arrow(s, (boxes[index-1][2], 240), (box[0], 240), index * 0.16)
    s.rect((105, 365, 1175, 455), C["black"], C["cyan2"], 2, 10)
    s.text((640, 410), "Γ^μ = F1(q²) γ^μ + [i σ^μν q_ν / (2m_μ)] F2(q²) + …", 25, C["white"], False, "mm")
    badge(s, (140, 495, 1140, 540), "F2(0) ENGINE READY • NO NUMERICAL BHSM a_μ DISPLAYED", C["gold"])
    s.rect((220, 580, 1060, 638), C["panel2"], C["red"], 2, 10)
    s.text((640, 609), "PHYSICAL PREDICTION GATED: ENCLOSURE BRIDGE • WARD IDENTITY • RENORMALIZATION • EXTERNAL MODE", 15, C["red"], True, "mm")
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
        node(s, box[:4], box[4], box[5], box[6], pulse=index == 0, title_size=19)
        arrow(s, (640, 220), ((box[0] + box[2]) / 2, box[1]), index * 0.16,
              color_value=box[6], bend=((box[0] + box[2]) / 2, 285))
    crossed(s, (430, 290, 520, 342), C["red"])
    s.rect((190, 525, 1090, 580), C["black"], C["cyan2"], 2, 10)
    s.text((640, 552), "Γ_i = Σ_f Γ_(i→f)       •       τ_i = hbar / Γ_i", 25, C["white"], True, "mm")
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


def identification_bridge(frame=None) -> Scene:
    s = Scene(frame)
    background(s, "PHYSICAL IDENTIFICATION — STATE SPACE", "AE2 EVENT CHILD → CANDIDATE LOCAL ENCLOSURE")
    x0, x1, y0, y1 = 115, 880, 150, 610
    for tick in range(6):
        x = x0 + tick * (x1 - x0) / 5
        y = y1 - tick * (y1 - y0) / 5
        s.line([(x, y0), (x, y1)], C["grid"], 1)
        s.line([(x0, y), (x1, y)], C["grid"], 1)
    s.line([(x0, y1), (x1, y1)], C["white"], 2)
    s.line([(x0, y0), (x0, y1)], C["white"], 2)
    s.text(((x0 + x1) / 2, 651), "EVENT-CHILD COORDINATE q_EC", 15, C["muted"], True, "mm")
    s.text((116, 126), "R_ENC", 13, C["muted"], True, "la")
    # Nested contours are the candidate action-owned enclosure, not a proof.
    s.ellipse((420, 230, 830, 545), C["panel"], C["red"], 3)
    s.ellipse((485, 280, 770, 505), C["panel2"], C["gold"], 2)
    s.ellipse((550, 330, 715, 465), C["black"], C["cyan"], 2)
    s.text((625, 213), "CANDIDATE ENCLOSURE CONTOURS", 14, C["red"], True, "mm")
    trajectories = [
        ([(150, 540), (300, 470), (440, 410), (575, 390)], C["cyan"], "FAMILY α"),
        ([(160, 350), (310, 360), (455, 385), (600, 410)], C["gold"], "MODE β"),
        ([(180, 210), (330, 270), (470, 335), (620, 385)], C["green"], "CURRENT γ"),
    ]
    for index, (points, accent, label) in enumerate(trajectories):
        s.line(points, accent, 3, animated=True, delay=index * 0.24)
        s.text((points[0][0], points[0][1] - 22), label, 13, accent, True, "mm")
    s.scan(135, 830, 170, 575, C["cyan"])
    node(s, (930, 150, 1235, 290), "REUSED STATE", ["family / mode", "representation • projector", "current • topology"], C["gold"], title_size=18)
    node(s, (930, 315, 1235, 440), "DYNAMICS", ["selected stop λ₂₄ = 0", "geometric event child"], C["cyan"], title_size=18)
    node(s, (930, 465, 1235, 600), "OPEN PROOF", ["enclosure owner", "junction + attachment", "intertwining transport"], C["red"], True, 18)
    s.text((1080, 625), "CONTOUR = TARGET REGION, NOT CLOSURE", 13, C["red"], True, "mm")
    s.text((640, 690), "A FAMILY OR MODE MAY MANIFEST AS AN SM PARTICLE ONLY AFTER STRUCTURE-PRESERVING ENCLOSURE", 14, C["white"], True, "mm")
    return s


VISUALS: dict[str, Callable[[int | None], Scene]] = {
    "bhsm_geometry_to_prediction": hero,
    "bhsm_universal_predictive_engine": universal,
    "bhsm_simulated_particle_spectrum": particle_spectrum,
    "bhsm_spectral_forecast": spectral,
    "bhsm_muon_g2_pipeline": gminus2,
    "bhsm_collision_predictor": collision,
    "bhsm_decay_stability_engine": decay,
    "bhsm_no_fit_firewall": firewall,
    "bhsm_physical_identification_bridge": identification_bridge,
}


def validate_status() -> dict:
    status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    if status["promotion"]["gate7_closed"]:
        raise RuntimeError("visual manifest unexpectedly promotes Gate 7")
    if status["capabilities"]["complete_physical_predictions"]:
        raise RuntimeError("visual manifest unexpectedly claims complete predictions")
    if status["spectral_visualization"]["physical_mass_scale_available"]:
        raise RuntimeError("visual suite is intentionally non-numeric until a physical scale exists")
    if status["identification_bridge"]["local_enclosure_proved"]:
        raise RuntimeError("visual manifest unexpectedly promotes the local enclosure bridge")
    if not status["identification_bridge"]["frozen_particle_registry_reused"]:
        raise RuntimeError("visual manifest must reuse the frozen particle registry")
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
