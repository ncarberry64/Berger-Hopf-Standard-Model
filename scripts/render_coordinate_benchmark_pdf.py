"""Render the coordinate benchmark JSON and chart into a one-page PDF."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="artifacts/coordinate_benchmark/coordinate_benchmark_results.json")
    parser.add_argument("--chart", default="artifacts/coordinate_benchmark/coordinate_benchmark_latency.png")
    parser.add_argument("--output", default="output/pdf/BHSM_coordinate_method_benchmark.pdf")
    args = parser.parse_args()
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    document = SimpleDocTemplate(
        str(destination), pagesize=letter, rightMargin=0.55 * inch, leftMargin=0.55 * inch,
        topMargin=0.45 * inch, bottomMargin=0.45 * inch,
    )
    story = [
        Paragraph("BHSM Synthetic Coordinate-Method Benchmark", styles["Title"]),
        Paragraph(
            "Controlled Python/NumPy microbenchmark. This is not production HEP tracking validation.",
            styles["Italic"],
        ),
        Paragraph(
            f"{payload['dataset']['event_count']:,} events; "
            f"{payload['dataset']['boundary_fraction_requested']:.0%} boundary/edge cases; "
            f"{payload['configuration']['repeats']} isolated repeats.",
            styles["BodyText"],
        ),
        Spacer(1, 0.12 * inch),
    ]
    table_data = [["Kernel", "Median (s)", "Events/s", "Peak RSS (MiB)"]]
    labels = {
        "branchy_cylindrical_scalar": "Scalar cylindrical",
        "cylindrical_vectorized_control": "Vectorized cylindrical",
        "bhsm_boundary_vectorized": "BHSM-inspired direct",
    }
    for name, label in labels.items():
        row = payload["results"][name]
        peak = "n/a" if row["peak_rss_bytes"] is None else f"{row['peak_rss_bytes'] / 2**20:.1f}"
        table_data.append([label, f"{row['median_seconds']:.6f}", f"{row['events_per_second']:,.0f}", peak])
    table = Table(table_data, colWidths=(2.2 * inch, 1.1 * inch, 1.25 * inch, 1.25 * inch))
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#263746")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9aa5ad")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), (colors.white, colors.HexColor("#eef3f5"))),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.extend([table, Spacer(1, 0.12 * inch), Image(args.chart, width=6.8 * inch, height=3.98 * inch)])
    comparisons = payload["comparisons"]
    counters = payload["hardware_counters"]
    story.extend([
        Spacer(1, 0.08 * inch),
        Paragraph(
            f"Scalar/BHSM-inspired speedup: <b>{comparisons['scalar_baseline_speedup']:.3f}x</b>. "
            f"Vectorized-control/BHSM-inspired speedup: <b>{comparisons['vectorized_control_speedup']:.3f}x</b>.",
            styles["BodyText"],
        ),
        Paragraph(
            f"Peak RSS reduction: <b>{comparisons['memory_reduction_vs_scalar_percent']:.1f}%</b> versus scalar "
            f"and <b>{comparisons['memory_reduction_vs_vectorized_control_percent']:.1f}%</b> versus vectorized control. "
            f"Maximum numerical delta: <b>{payload['correctness']['maximum_absolute_difference']:.3e}</b>.",
            styles["BodyText"],
        ),
        Paragraph(
            f"Branch counters: {counters['status']}. No branch-misprediction value is inferred.",
            styles["BodyText"],
        ),
    ])
    document.build(story)
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
