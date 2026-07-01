"""Generate the compact PR #98 CMS sample and offline README animation."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
EXPECTED_SHA256 = "1ac3a44aa66562fa201882ac6e7fd550ac186df3586c0478095df4c77c529710"
SAMPLE_EVENTS = 64
EVENT_COUNT = 100_000
WIDTH, HEIGHT = 900, 500
COLORS = {"ink": "#17212b", "blue": "#2878b5", "teal": "#21867a", "gold": "#d39b2a", "red": "#b84a4a", "light": "#f4f7f8", "grid": "#d9e0e3"}
GIF_FRAMES = 32
GIF_DURATION_MS = 90


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    names = ["DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", "arialbd.ttf" if bold else "arial.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def source_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def selected_event_indices() -> set[int]:
    return {round(index * (EVENT_COUNT - 1) / (SAMPLE_EVENTS - 1)) for index in range(SAMPLE_EVENTS)}


def extract_sample(source: Path) -> dict[str, object]:
    if source_hash(source) != EXPECTED_SHA256:
        raise ValueError("CMS source SHA-256 does not match the PR #98 artifact")
    targets = selected_event_indices()
    vectors: list[dict[str, object]] = []
    with source.open(newline="", encoding="utf-8") as stream:
        for event_index, row in enumerate(csv.DictReader(stream)):
            if event_index not in targets:
                continue
            for muon in (1, 2):
                vectors.append(
                    {
                        "event_index": event_index,
                        "run": int(row["Run"]),
                        "event": int(row["Event"]),
                        "muon": muon,
                        "E": float(row[f"E{muon}"]),
                        "px": float(row[f"px{muon}" if muon == 2 else "px1 "]),
                        "py": float(row[f"py{muon}"]),
                        "pz": float(row[f"pz{muon}"]),
                        "pt": float(row[f"pt{muon}"]),
                        "eta": float(row[f"eta{muon}"]),
                        "phi": float(row[f"phi{muon}"]),
                        "charge": int(row[f"Q{muon}"]),
                    }
                )
    if len(vectors) != 2 * SAMPLE_EVENTS:
        raise ValueError(f"expected {2 * SAMPLE_EVENTS} sampled vectors, found {len(vectors)}")
    return {
        "sample_status": "DETERMINISTIC_DERIVED_SAMPLE_NOT_FULL_DATASET",
        "selection": "64 evenly spaced source-event row indices; both muon four-vectors retained",
        "source_sha256": EXPECTED_SHA256,
        "vector_count": len(vectors),
        "vectors": vectors,
    }


def manifest() -> dict[str, object]:
    return {
        "source": "CMS dimuon open data",
        "cern_open_data_record": 303,
        "doi": "10.7483/OPENDATA.CMS.4M97.3SQ9",
        "license": "CC0 Public Domain",
        "pr": 98,
        "merge_commit": "e20f4eb1cba6a0619cee27676fd3035028d8738e",
        "events_validated": 100000,
        "unique_muon_four_vectors": 200000,
        "replication_factor": 10,
        "timed_workload_four_vectors": 2000000,
        "source_file_size_bytes": 15075838,
        "adler32": "b47f7436",
        "sha256": EXPECTED_SHA256,
        "speedup_vs_vectorized_control": 3.225,
        "run_to_run_variance": "<0.5%",
        "max_absolute_delta": 5.821e-11,
        "max_kinematic_squared_scale": 6.77e10,
        "backward_error": "<2.4 machine-epsilon",
        "ci_gate": "<128 machine-epsilon",
        "sample_events": SAMPLE_EVENTS,
        "sample_four_vectors": 2 * SAMPLE_EVENTS,
        "claim_boundary": "Engine validation only; not empirical validation of BHSM Physics.",
        "detector_reconstruction_claimed": False,
        "cms_cern_endorsement_claimed": False,
        "frozen_predictions_modified": False,
        "official_prediction_logic_modified": False,
    }


def normalized_points(vectors: list[dict[str, object]], transformed: bool) -> list[tuple[float, float, int]]:
    if transformed:
        return [((float(v["phi"]) + math.pi) / (2 * math.pi), (math.tanh(float(v["eta"]) / 3) + 1) / 2, int(v["charge"])) for v in vectors]
    scale = max(max(math.asinh(abs(float(v["px"]))), math.asinh(abs(float(v["pz"])))) for v in vectors)
    return [((math.copysign(math.asinh(abs(float(v["px"]))), float(v["px"])) / scale + 1) / 2, (math.copysign(math.asinh(abs(float(v["pz"]))), float(v["pz"])) / scale + 1) / 2, int(v["charge"])) for v in vectors]


def base_frame(title: str, subtitle: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (WIDTH, HEIGHT), COLORS["light"])
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, WIDTH, 72), fill=COLORS["ink"])
    draw.text((28, 16), title, fill="white", font=font(28, True))
    draw.text((30, 76), subtitle, fill=COLORS["ink"], font=font(15))
    return image, draw


def draw_cloud(draw: ImageDraw.ImageDraw, points: list[tuple[float, float, int]], box: tuple[int, int, int, int], label: str) -> None:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=8, fill="white", outline=COLORS["grid"], width=2)
    draw.text((x0 + 14, y0 + 10), label, fill=COLORS["ink"], font=font(16, True))
    for x, y, charge in points:
        px = x0 + 16 + x * (x1 - x0 - 32)
        py = y1 - 16 - y * (y1 - y0 - 52)
        color = COLORS["blue"] if charge < 0 else COLORS["gold"]
        draw.ellipse((px - 3, py - 3, px + 3, py + 3), fill=color)


def ease_in_out(t: float) -> float:
    return 0.5 - 0.5 * math.cos(math.tau * t)


def interpolate_points(
    incoming: list[tuple[float, float, int]],
    mapped: list[tuple[float, float, int]],
    t: float,
) -> list[tuple[float, float, int]]:
    eased = ease_in_out(t)
    return [
        (x0 + (x1 - x0) * eased, y0 + (y1 - y0) * eased, charge)
        for (x0, y0, charge), (x1, y1, _) in zip(incoming, mapped)
    ]


def draw_point_layer(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[float, float, int]],
    box: tuple[int, int, int, int],
    radius: int,
    alpha_style: str = "active",
) -> None:
    x0, y0, x1, y1 = box
    for x, y, charge in points:
        px = x0 + 20 + x * (x1 - x0 - 40)
        py = y1 - 20 - y * (y1 - y0 - 62)
        if alpha_style == "faint":
            color = "#b8cdd8" if charge < 0 else "#e4cf9f"
        else:
            color = COLORS["blue"] if charge < 0 else COLORS["gold"]
        draw.ellipse((px - radius, py - radius, px + radius, py + radius), fill=color)


def draw_continuous_scene(
    points: list[tuple[float, float, int]],
    incoming: list[tuple[float, float, int]],
    mapped: list[tuple[float, float, int]],
    frame_index: int,
) -> Image.Image:
    image, draw = base_frame(
        "BHSM Engine on real CMS Open Data",
        "Continuous morph of 128 collision-derived muon four-vectors from input projection to boundary-safe angular chart",
    )
    box = (70, 116, 610, 404)
    draw.rounded_rectangle(box, radius=8, fill="white", outline=COLORS["grid"], width=2)
    draw.text((92, 131), "real PR #98 display sample: px/pz projection -> (phi, eta) chart", fill=COLORS["ink"], font=font(15, True))
    for fraction in (0.25, 0.5, 0.75):
        x = box[0] + 20 + fraction * (box[2] - box[0] - 40)
        y = box[1] + 42 + fraction * (box[3] - box[1] - 62)
        draw.line((x, box[1] + 42, x, box[3] - 20), fill=COLORS["grid"], width=1)
        draw.line((box[0] + 20, y, box[2] - 20, y), fill=COLORS["grid"], width=1)
    draw_point_layer(draw, incoming, box, 2, "faint")
    draw_point_layer(draw, mapped, box, 2, "faint")
    for offset in (3, 2, 1):
        t = ((frame_index - offset) % GIF_FRAMES) / GIF_FRAMES
        trail = interpolate_points(incoming, mapped, t)
        draw_point_layer(draw, trail, box, max(1, 4 - offset), "faint")
    draw_point_layer(draw, points, box, 4)

    progress = frame_index / GIF_FRAMES
    bar_x0, bar_y0, bar_x1, bar_y1 = 90, 430, 590, 442
    draw.rounded_rectangle((bar_x0, bar_y0, bar_x1, bar_y1), radius=6, fill="#e8eef0")
    draw.rounded_rectangle((bar_x0, bar_y0, bar_x0 + (bar_x1 - bar_x0) * progress, bar_y1), radius=6, fill=COLORS["teal"])
    draw.text((90, 452), "looping transform path; points are real sampled CMS dimuon muon four-vectors", fill=COLORS["ink"], font=font(13))

    panel = (650, 116, 840, 404)
    draw.rounded_rectangle(panel, radius=8, fill="white", outline=COLORS["grid"], width=2)
    rows = [
        ("source", "CMS Record 303"),
        ("vectors", "128 displayed"),
        ("validated", "200,000"),
        ("workload", "2,000,000"),
        ("speedup", "3.225x"),
        ("error", "<2.4 eps"),
    ]
    for index, (label, value) in enumerate(rows):
        y = 142 + index * 38
        draw.text((668, y), label, fill=COLORS["ink"], font=font(13))
        draw.text((820, y), value, fill=COLORS["teal"], font=font(13, True), anchor="ra")
    draw.line((668, 372, 822, 372), fill=COLORS["grid"], width=1)
    draw.text((745, 392), "Engine validation only", fill=COLORS["red"], font=font(14, True), anchor="mm")
    return image


def render_frames(sample: dict[str, object]) -> list[Image.Image]:
    vectors = sample["vectors"]
    incoming = normalized_points(vectors, False)
    mapped = normalized_points(vectors, True)
    return [
        draw_continuous_scene(interpolate_points(incoming, mapped, index / GIF_FRAMES), incoming, mapped, index)
        for index in range(GIF_FRAMES)
    ]


def write_svg(sample: dict[str, object], path: Path) -> None:
    points = normalized_points(sample["vectors"], True)
    circles = []
    for x, y, charge in points:
        cx, cy = 55 + x * 410, 115 + (1 - y) * 255
        color = COLORS["blue"] if charge < 0 else COLORS["gold"]
        circles.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="2.7" fill="{color}"/>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="500" viewBox="0 0 900 500">
<rect width="900" height="500" fill="{COLORS['light']}"/><rect width="900" height="72" fill="{COLORS['ink']}"/>
<text x="28" y="45" fill="white" font-family="sans-serif" font-size="28" font-weight="bold">BHSM Engine on CMS Open Data</text>
<rect x="35" y="95" width="450" height="300" rx="8" fill="white" stroke="{COLORS['grid']}" stroke-width="2"/>
<text x="55" y="125" fill="{COLORS['ink']}" font-family="sans-serif" font-size="16" font-weight="bold">128-vector display sample: transformed (phi, eta)</text>
{''.join(circles)}
<text x="520" y="130" fill="{COLORS['ink']}" font-family="sans-serif" font-size="18" font-weight="bold">PR #98 validation</text>
<text x="520" y="175" fill="{COLORS['ink']}" font-family="sans-serif" font-size="16">200,000 unique four-vectors</text>
<text x="520" y="215" fill="{COLORS['ink']}" font-family="sans-serif" font-size="16">2,000,000 timed transforms</text>
<text x="520" y="255" fill="{COLORS['teal']}" font-family="sans-serif" font-size="20" font-weight="bold">3.225x vs vectorized control</text>
<text x="520" y="300" fill="{COLORS['ink']}" font-family="sans-serif" font-size="16">Backward error &lt;2.4 machine-epsilon</text>
<text x="520" y="340" fill="{COLORS['ink']}" font-family="sans-serif" font-size="16">CI gate &lt;128 machine-epsilon</text>
<text x="450" y="435" text-anchor="middle" fill="{COLORS['red']}" font-family="sans-serif" font-size="17" font-weight="bold">Engine validation only - not empirical validation of BHSM Physics.</text>
<text x="450" y="468" text-anchor="middle" fill="{COLORS['ink']}" font-family="sans-serif" font-size="14">CMS Open Data Record 303 | DOI 10.7483/OPENDATA.CMS.4M97.3SQ9 | no endorsement claimed</text>
</svg>'''
    path.write_text(svg, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=ROOT / "data/external/cern_open_data/dimuon.csv")
    args = parser.parse_args()
    if args.input.exists():
        sample = extract_sample(args.input)
    else:
        sample = json.loads((HERE / "pr98_cms_four_vector_sample.json").read_text(encoding="utf-8"))
    (HERE / "pr98_cms_sample_manifest.json").write_text(json.dumps(manifest(), indent=2) + "\n", encoding="utf-8")
    (HERE / "pr98_cms_four_vector_sample.json").write_text(json.dumps(sample, indent=2) + "\n", encoding="utf-8")
    frames = render_frames(sample)
    frames[0].save(
        HERE / "pr98_cms_engine_validation_continuous.gif",
        save_all=True,
        append_images=frames[1:],
        duration=GIF_DURATION_MS,
        loop=0,
        disposal=2,
        optimize=False,
    )
    write_svg(sample, HERE / "pr98_cms_engine_validation.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
