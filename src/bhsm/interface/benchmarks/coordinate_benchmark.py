"""CLI runner for the synthetic coordinate-method performance audit."""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

from .coordinate_methods import (
    BHSM_KERNEL_STATUS,
    KERNELS,
    KERNEL_STATUS,
    benchmark_kernel,
    branch_counter_status,
    generate_kinematic_dataset,
    validate_kernel_equivalence,
    write_json,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=int, default=1_000_000)
    parser.add_argument("--boundary-fraction", type=float, default=0.30)
    parser.add_argument("--seed", type=int, default=1729)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", default="artifacts/coordinate_benchmark/coordinate_benchmark_results.json")
    parser.add_argument("--markdown", default="docs/coordinate_benchmark_results.md")
    parser.add_argument("--plot", default="artifacts/coordinate_benchmark/coordinate_benchmark_latency.png")
    parser.add_argument("--worker", choices=tuple(KERNELS), default=None, help=argparse.SUPPRESS)
    return parser


def _worker(args: argparse.Namespace) -> int:
    states, _, summary = generate_kinematic_dataset(args.events, args.boundary_fraction, args.seed)
    result = benchmark_kernel(args.worker, states, args.repeats)
    print(json.dumps({"dataset": summary.to_dict(), "result": result.to_dict()}, sort_keys=True))
    return 0


def _isolated_result(args: argparse.Namespace, kernel: str) -> dict[str, object]:
    command = [
        sys.executable,
        "-m",
        "bhsm.interface.benchmarks.coordinate_benchmark",
        "--worker",
        kernel,
        "--events",
        str(args.events),
        "--boundary-fraction",
        str(args.boundary_fraction),
        "--seed",
        str(args.seed),
        "--repeats",
        str(args.repeats),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode:
        raise RuntimeError(f"worker {kernel} failed: {completed.stderr}")
    return json.loads(completed.stdout)


def _markdown(payload: dict[str, object]) -> str:
    dataset = payload["dataset"]
    results = payload["results"]
    comparisons = payload["comparisons"]
    lines = [
        "# Synthetic Coordinate-Method Benchmark",
        "",
        "> This is a controlled Python/NumPy microbenchmark, not a comparison with Geant4, ACTS,",
        "> CMSSW, Athena, production detector tracking, or validated HEP reconstruction software.",
        "",
        f"Events: `{dataset['event_count']:,}`; boundary/edge events: `{dataset['boundary_event_count']:,}`; seed: `{payload['configuration']['seed']}`.",
        "",
        "| Kernel | Median latency (s) | Events/s | Peak RSS (MiB) | Branch misses |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for name in KERNELS:
        row = results[name]
        peak = "n/a" if row["peak_rss_bytes"] is None else f"{row['peak_rss_bytes'] / 2**20:.1f}"
        misses = "not available" if row["hardware_branch_misses"] is None else str(row["hardware_branch_misses"])
        lines.append(
            f"| `{name}` | {row['median_seconds']:.6f} | {row['events_per_second']:,.0f} | {peak} | {misses} |"
        )
    lines.extend(
        [
            "",
            "## Deltas",
            "",
            f"- Scalar branch-heavy baseline / BHSM-inspired direct map: `{comparisons['scalar_baseline_speedup']:.3f}x`.",
            f"- Vectorized cylindrical control / BHSM-inspired direct map: `{comparisons['vectorized_control_speedup']:.3f}x`.",
            f"- Peak RSS reduction versus scalar baseline: `{comparisons['memory_reduction_vs_scalar_percent']:.1f}%` (negative means higher memory).",
            f"- Peak RSS reduction versus vectorized control: `{comparisons['memory_reduction_vs_vectorized_control_percent']:.1f}%`.",
            "",
            "## Correctness",
            "",
            f"Maximum absolute delta versus scalar baseline: `{payload['correctness']['maximum_absolute_difference']:.3e}`.",
            f"All kernels agree at `rtol=atol=1e-12`: `{payload['correctness']['all_kernels_equivalent']}`.",
            "",
            "## Branch-counter status",
            "",
            f"`{payload['hardware_counters']['status']}`. Hardware branch-misprediction values are not inferred from timing.",
            "",
            "## Interpretation boundary",
            "",
            f"- `{KERNEL_STATUS}`.",
            f"- `{BHSM_KERNEL_STATUS}`.",
            "- The scalar speedup includes Python-loop versus NumPy-vectorization effects.",
            "- The vectorized-control delta is the more relevant coordinate-formula comparison.",
            "- No physics accuracy, detector efficiency, tracking quality, or production HEP speedup is claimed.",
            "- Frozen BHSM predictions and official model logic are unchanged.",
        ]
    )
    return "\n".join(lines) + "\n"


def _plot(payload: dict[str, object], path: Path) -> None:
    import matplotlib.pyplot as plt

    names = list(KERNELS)
    values = [payload["results"][name]["median_seconds"] for name in names]
    labels = ["Scalar cylindrical", "Vectorized cylindrical", "BHSM-inspired direct"]
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    bars = ax.bar(labels, values, color=("#7a8088", "#2878a8", "#2f8f5b"))
    ax.set_ylabel("Median wall time (seconds)")
    ax.set_title(f"Synthetic coordinate mapping - {payload['dataset']['event_count']:,} events")
    ax.grid(axis="y", alpha=0.25)
    ax.bar_label(bars, labels=[f"{value:.4f}s" for value in values], padding=3)
    ax.tick_params(axis="x", labelrotation=10)
    fig.text(0.5, 0.01, "Microbenchmark only; not production HEP tracking validation.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def run(args: argparse.Namespace) -> dict[str, object]:
    small, _, _ = generate_kinematic_dataset(min(args.events, 20_000), args.boundary_fraction, args.seed)
    equivalence = validate_kernel_equivalence(small)
    workers = [_isolated_result(args, name) for name in KERNELS]
    dataset = workers[0]["dataset"]
    if any(worker["dataset"]["sha256"] != dataset["sha256"] for worker in workers[1:]):
        raise RuntimeError("isolated workers did not generate identical datasets")
    results = {worker["result"]["kernel"]: worker["result"] for worker in workers}
    scalar = results["branchy_cylindrical_scalar"]["median_seconds"]
    control = results["cylindrical_vectorized_control"]["median_seconds"]
    bhsm = results["bhsm_boundary_vectorized"]["median_seconds"]
    scalar_peak = results["branchy_cylindrical_scalar"]["peak_rss_bytes"]
    control_peak = results["cylindrical_vectorized_control"]["peak_rss_bytes"]
    bhsm_peak = results["bhsm_boundary_vectorized"]["peak_rss_bytes"]

    def memory_reduction(reference: int | None) -> float | None:
        if reference is None or bhsm_peak is None:
            return None
        return 100.0 * (reference - bhsm_peak) / reference

    max_delta = max(row["max_absolute_difference"] for row in equivalence.values())
    payload: dict[str, object] = {
        "benchmark_status": KERNEL_STATUS,
        "bhsm_kernel_status": BHSM_KERNEL_STATUS,
        "configuration": {
            "events": args.events,
            "boundary_fraction": args.boundary_fraction,
            "seed": args.seed,
            "repeats": args.repeats,
            "python": sys.version,
            "platform": platform.platform(),
            "processor": platform.processor(),
            "numpy": __import__("numpy").__version__,
            "cpu_count": os.cpu_count(),
        },
        "dataset": dataset,
        "results": results,
        "comparisons": {
            "scalar_baseline_speedup": scalar / bhsm,
            "vectorized_control_speedup": control / bhsm,
            "memory_reduction_vs_scalar_percent": memory_reduction(scalar_peak),
            "memory_reduction_vs_vectorized_control_percent": memory_reduction(control_peak),
        },
        "correctness": {
            "rows": equivalence,
            "maximum_absolute_difference": max_delta,
            "all_kernels_equivalent": all(
                row["allclose_rtol_1e_12_atol_1e_12"] for row in equivalence.values()
            ),
        },
        "hardware_counters": {
            "status": branch_counter_status(),
            "branch_mispredictions_collected": False,
            "note": "Use Linux perf stat around an isolated worker for hardware counters.",
        },
        "claim_boundaries": [
            "synthetic coordinate-mapping microbenchmark only",
            "not production HEP tracking validation",
            "BHSM-inspired kernel is not the official BHSM prediction engine",
            "no frozen or official prediction changes",
        ],
    }
    write_json(args.output, payload)
    markdown_path = Path(args.markdown)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(_markdown(payload), encoding="utf-8")
    _plot(payload, Path(args.plot))
    return payload


def main() -> int:
    args = _parser().parse_args()
    if args.worker:
        return _worker(args)
    payload = run(args)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
