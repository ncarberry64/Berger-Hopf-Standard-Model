"""Optional deterministic status plots for the BHSM prediction gallery."""

from __future__ import annotations

from importlib.util import find_spec
from pathlib import Path
from typing import Any

from .gallery import build_prediction_gallery


def is_matplotlib_available() -> bool:
    return find_spec("matplotlib") is not None


def gallery_plot_manifest(output_dir: Path | str = "artifacts/plots", generated: bool = False) -> dict[str, Any]:
    root = Path(output_dir)
    specs = (
        ("prediction_status_counts", "BHSM_prediction_status_counts_v0_2.svg", "status_counts"),
        ("prediction_category_counts", "BHSM_prediction_category_counts_v0_2.svg", "category_counts"),
        ("runtime_gate_summary", "BHSM_runtime_gate_summary_v0_2.svg", "runtime_gate_status"),
    )
    return {"plots": [{"plot_id": pid, "path": str(root / name).replace("\\", "/"), "source_artifact": "artifacts/BHSM_prediction_gallery_table_v0_2.json", "plot_type": kind, "claim_boundary": "Registry/status plot only; not empirical validation.", "generated": generated, "requires_matplotlib": True, "speculative_included": False, "notes": "Deterministic offline gallery summary."} for pid, name, kind in specs]}


def generate_gallery_plots(output_dir: Path | str = "artifacts/plots", dry_run: bool = False) -> dict[str, Any]:
    if dry_run:
        return gallery_plot_manifest(output_dir, generated=False)
    if not is_matplotlib_available():
        raise RuntimeError("matplotlib is optional and unavailable; use --dry-run for the manifest")
    import matplotlib
    matplotlib.use("Agg")
    matplotlib.rcParams["svg.hashsalt"] = "bhsm-gallery-v0-2"
    import matplotlib.pyplot as plt
    gallery = build_prediction_gallery()
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    datasets = (
        (gallery.status_counts(), "Prediction registry status counts", "BHSM_prediction_status_counts_v0_2.svg"),
        (gallery.category_counts(), "Prediction gallery category counts", "BHSM_prediction_category_counts_v0_2.svg"),
        ({"runtime_disabled": sum(e.category == "runtime_disabled_gate" for e in gallery.entries), "other": sum(e.category != "runtime_disabled_gate" for e in gallery.entries)}, "Runtime gate registry summary", "BHSM_runtime_gate_summary_v0_2.svg"),
    )
    for data, title, filename in datasets:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.bar(list(data), list(data.values()), color="#315a7d")
        ax.set_title(title + "\nStatus summary only - not empirical validation")
        ax.set_ylabel("Registry entries")
        ax.tick_params(axis="x", rotation=30)
        fig.tight_layout()
        path = output / filename
        fig.savefig(path, format="svg", metadata={"Title": title, "Description": "Registry status plot; not empirical validation.", "Date": "2026-06-27"})
        plt.close(fig)
        normalized = "\n".join(line.rstrip() for line in path.read_text(encoding="utf-8").splitlines()) + "\n"
        path.write_text(normalized, encoding="utf-8")
    return gallery_plot_manifest(output, generated=True)
