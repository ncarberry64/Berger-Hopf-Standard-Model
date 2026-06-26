from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGETS = ROOT / "data" / "pdg_targets_template_v0_1.json"


def _load_json(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        rows = payload.get("target_rows", [])
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    raise ValueError(f"{path} does not contain a list or target_rows array")


def _load_csv(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_target_rows(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return _load_json(path)
    if suffix == ".csv":
        return _load_csv(path)
    raise ValueError("targets must be JSON or CSV")


def _number(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(parsed):
        return None
    return parsed


def real_comparison_rows(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    real_rows: list[dict[str, Any]] = []
    for row in rows:
        pdg_value = _number(row.get("pdg_value"))
        bhsm_value = _number(row.get("bhsm_value"))
        if pdg_value is None or bhsm_value is None:
            continue
        if str(row.get("comparison_status", "")).upper().startswith("TEMPLATE_ONLY"):
            continue
        enriched = dict(row)
        enriched["pdg_value"] = pdg_value
        enriched["bhsm_value"] = bhsm_value
        enriched["relative_residual"] = (
            None if pdg_value == 0 else (bhsm_value - pdg_value) / pdg_value
        )
        real_rows.append(enriched)
    return real_rows


def write_summary(rows: list[dict[str, Any]], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "pdg_validation_residuals.csv"
    fieldnames = [
        "quantity_name",
        "sector",
        "pdg_value",
        "bhsm_value",
        "relative_residual",
        "unit",
        "scheme",
        "scale",
        "source_reference",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name) for name in fieldnames})
    return path


def write_plot(rows: list[dict[str, Any]], output_dir: Path) -> Path:
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "matplotlib is required to generate plots when real target data are supplied"
        ) from exc

    labels = [str(row.get("quantity_name") or f"row_{i}") for i, row in enumerate(rows)]
    residuals = [row.get("relative_residual") for row in rows]
    if any(value is None for value in residuals):
        raise ValueError("cannot plot relative residuals when a PDG value is zero")

    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "pdg_validation_relative_residuals.png"
    fig, ax = plt.subplots(figsize=(max(6, len(labels) * 0.8), 4))
    ax.bar(labels, residuals)
    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.set_ylabel("relative residual (BHSM - target) / target")
    ax.set_title("BHSM v1.0.1 PDG-style validation residuals")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate BHSM PDG validation plots only from real supplied target data."
    )
    parser.add_argument("--targets", type=Path, default=DEFAULT_TARGETS)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs" / "pdg_validation")
    parser.add_argument("--no-plot", action="store_true", help="Write residual CSV only.")
    args = parser.parse_args()

    if not args.targets.exists():
        print(f"No PDG target data supplied: {args.targets} does not exist.")
        print("No validation plots generated.")
        return 0

    rows = load_target_rows(args.targets)
    real_rows = real_comparison_rows(rows)
    if not real_rows:
        print(f"No real numeric PDG target rows found in {args.targets}.")
        print("No fake validation plots generated.")
        return 0

    summary = write_summary(real_rows, args.output_dir)
    print(f"Wrote residual summary: {summary}")
    if not args.no_plot:
        plot = write_plot(real_rows, args.output_dir)
        print(f"Wrote validation plot: {plot}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
