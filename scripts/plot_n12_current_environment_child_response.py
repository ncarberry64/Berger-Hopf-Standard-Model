"""Plot the computed N12 source susceptibility and intrinsic family shape.

Reads the actual integrated numerical report. The two panels retain their
different normalizations; they are not combined into a total coupling score.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "artifacts/current_runtime/dop853_system_integration_current_finer/report.json"
SECTORS = ("charged_lepton", "up", "down")
LABELS = ("Charged lepton", "Up quark", "Down quark")
COLORS = ("#2967a0", "#b45a27", "#447b50")
ROLES = ("heavy", "middle", "light")


def render(report: Path, output: Path) -> tuple[Path, Path]:
    payload = json.loads(report.read_text(encoding="utf-8"))
    coupling = payload.get("environment_child_coupling", payload)
    rows = coupling["existing_fiber_couplings"]
    lookup = {(row["sector"], row["role"]): row for row in rows}
    if set(lookup) != {(sector, role) for sector in SECTORS for role in ROLES}:
        raise ValueError("the nine existing sector/family rows are required")
    output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "svg.fonttype": "none"})
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.8), layout="constrained")
    x = np.arange(3)
    width = 0.23
    for i, (sector, label, color) in enumerate(zip(SECTORS, LABELS, COLORS, strict=True)):
        selected = [lookup[sector, role] for role in ROLES]
        susceptibility = [r["coexact_source_second_response_per_factor"]["plus"] for r in selected]
        axes[0].bar(x + (i - 1) * width, susceptibility, width, label=label, color=color)
        shape = [r["normalized_internal_family_response_squared_to_heavy"] for r in selected]
        axes[1].plot(x, shape, marker=("o", "s", "^")[i], color=color, label=label, linewidth=1.8)
    axes[0].set_title("Environmental source response\nPer L/R pair; per color for quarks",
                      loc="left", fontsize=11, pad=10)
    axes[0].set_ylabel("Hypercharge-weighted boundary susceptibility")
    axes[0].legend(frameon=False, loc="upper right")
    axes[0].set_ylim(0, 2.1)
    axes[1].set_title("Intrinsic family response\nSector-wise shape; quark absolute scales unavailable",
                      loc="left", fontsize=11, pad=10)
    axes[1].set_ylabel("Squared family response / heavy squared response")
    axes[1].set_yscale("log")
    minimum_shape = min(r["normalized_internal_family_response_squared_to_heavy"] for r in rows)
    axes[1].set_ylim(minimum_shape / 3.0, 2)
    for ax in axes:
        ax.set_xticks(x, [role.capitalize() for role in ROLES])
        ax.set_xlabel("Existing family slot")
        ax.grid(axis="y", alpha=0.2)
        ax.set_axisbelow(True)
    domain = coupling["numerical_domain"]
    fig.suptitle("Current N12 environment and nine existing child fibers", fontsize=14, fontweight="bold")
    caption = (f"Stored 1222→stop history · {domain['segment_count']} coefficient segments · "
               f"T = {domain['proper_duration']:.8e} · probe z = {domain['spectral_parameter']:g}\n"
               "External source center E₀ = 0; source profile p(τ) = 1/√T. Each panel uses its stated normalization.")
    fig.supxlabel(caption, fontsize=9)
    png, svg = output / "environment_child_response.png", output / "environment_child_response.svg"
    fig.savefig(png, dpi=200)
    fig.savefig(svg)
    plt.close(fig)
    (output / "figure_inputs.json").write_text(json.dumps({"report": str(report.resolve()),
        "coefficient_path": coupling["coefficient_path"], "numerical_domain": domain,
        "panels": ["coexact_source_second_response_per_factor.plus",
                   "normalized_internal_family_response_squared_to_heavy"]}, indent=2) + "\n",
        encoding="utf-8")
    return png, svg


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or args.report.parent
    png, svg = render(args.report, output)
    print(json.dumps({"png": str(png.resolve()), "svg": str(svg.resolve())}, indent=2))


if __name__ == "__main__":
    main()
