"""Benchmark BHSM-inspired coordinate mapping on published CMS dimuon data."""

from __future__ import annotations

import argparse
import json
import platform
import statistics
import time
from pathlib import Path

import numpy as np

from .cern_open_data import (
    REAL_DATA_STATUS,
    boundary_diagnostics,
    download_open_data,
    load_cms_dimuon_vectors,
    load_manifest,
)
from .coordinate_methods import KERNELS, validate_kernel_equivalence, write_json


DEFAULT_MANIFEST = Path("data/manifests/cms_open_data_dimuon_2010.json")
DEFAULT_DATA = Path("data/external/cern_open_data/dimuon.csv")
FLOAT64_EPSILON_BOUND = 128.0


def benchmark(states: np.ndarray, repeats: int) -> dict[str, object]:
    if repeats <= 0:
        raise ValueError("repeats must be positive")
    results: dict[str, object] = {}
    for name, kernel in KERNELS.items():
        kernel(states[: min(10_000, len(states))])
        timings = []
        output = None
        for _ in range(repeats):
            start = time.perf_counter_ns()
            output = kernel(states)
            timings.append((time.perf_counter_ns() - start) / 1.0e9)
        assert output is not None
        median = statistics.median(timings)
        results[name] = {
            "median_seconds": median,
            "minimum_seconds": min(timings),
            "maximum_seconds": max(timings),
            "timings_seconds": timings,
            "vectors_per_second": len(states) / median,
            "output_checksum": float(np.sum(output, dtype=np.float64)),
        }
    return results


def scale_aware_consistency(states: np.ndarray) -> dict[str, object]:
    """Measure backward error in machine-epsilon units at the input scale."""

    baseline = KERNELS["branchy_cylindrical_scalar"](states)
    momentum_sq = np.einsum("ij,ij->i", states[:, 1:4], states[:, 1:4])
    scales = np.ones_like(baseline)
    scales[:, 0] = np.maximum(1.0, np.abs(baseline[:, 0]))
    scales[:, 4] = np.maximum(1.0, states[:, 0] ** 2 + momentum_sq)
    epsilon = np.finfo(np.float64).eps
    rows: dict[str, object] = {}
    for name in ("cylindrical_vectorized_control", "bhsm_boundary_vectorized"):
        delta = np.abs(KERNELS[name](states) - baseline)
        max_epsilon_units = float(np.max(delta / (epsilon * scales)))
        rows[name] = {
            "max_scale_normalized_epsilon_units": max_epsilon_units,
            "within_128_epsilon_bound": bool(max_epsilon_units <= FLOAT64_EPSILON_BOUND),
        }
    return {
        "method": "abs(candidate-baseline)/(float64_epsilon*component_scale)",
        "component_scale": "radius=max(1,abs(r)); unit=1; invariant=max(1,E^2+|p|^2)",
        "epsilon_unit_bound": FLOAT64_EPSILON_BOUND,
        "maximum_input_squared_scale": float(np.max(states[:, 0] ** 2 + momentum_sq)),
        "rows": rows,
        "all_within_bound": all(row["within_128_epsilon_bound"] for row in rows.values()),
    }


def build_report(
    unique_states: np.ndarray,
    manifest: dict[str, object],
    source_sha256: str,
    repeats: int,
    replication_factor: int = 1,
) -> dict[str, object]:
    if replication_factor <= 0:
        raise ValueError("replication_factor must be positive")
    states = (
        unique_states
        if replication_factor == 1
        else np.ascontiguousarray(np.tile(unique_states, (replication_factor, 1)))
    )
    results = benchmark(states, repeats)
    correctness_rows = validate_kernel_equivalence(states)
    backward_error = scale_aware_consistency(states)
    direct = results["bhsm_boundary_vectorized"]["median_seconds"]
    control = results["cylindrical_vectorized_control"]["median_seconds"]
    scalar = results["branchy_cylindrical_scalar"]["median_seconds"]
    return {
        "status": REAL_DATA_STATUS,
        "source": {
            "record_id": manifest["record_id"],
            "title": manifest["title"],
            "doi": manifest["doi"],
            "record_url": manifest["record_url"],
            "license": manifest["license"],
            "source_sha256": source_sha256,
            "portal_checksum": manifest["file"]["portal_checksum"],
        },
        "configuration": {
            "unique_event_count": len(unique_states) // 2,
            "unique_four_vector_count": len(unique_states),
            "replication_factor": replication_factor,
            "processed_four_vectors_per_pass": len(states),
            "repeats": repeats,
            "platform": platform.platform(),
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "boundary_diagnostics": boundary_diagnostics(states),
        "results": results,
        "comparisons": {
            "speedup_vs_scalar": scalar / direct,
            "speedup_vs_vectorized_control": control / direct,
        },
        "correctness": {
            "rows": correctness_rows,
            "maximum_absolute_difference": max(
                row["max_absolute_difference"] for row in correctness_rows.values()
            ),
            "all_kernels_equivalent": all(
                row["allclose_rtol_1e_12_atol_1e_12"] for row in correctness_rows.values()
            ),
            "strict_synthetic_tolerance_applied": True,
            "scale_aware_float64_consistency": backward_error,
        },
        "claim_boundaries": [
            "real published CMS collision-derived four-vectors",
            "coordinate transformation only",
            "not track fitting or track reconstruction",
            "derived education dataset not suitable for a full physics analysis",
            "no CMS or CERN endorsement",
            "no frozen BHSM prediction changes",
        ],
    }


def markdown(report: dict[str, object]) -> str:
    lines = [
        "# CERN Open Data Coordinate Benchmark",
        "",
        f"Status: `{report['status']}`.",
        "",
        f"Source: [{report['source']['title']}]({report['source']['record_url']}), DOI `{report['source']['doi']}`.",
        "",
        f"Unique four-vectors: `{report['configuration']['unique_four_vector_count']:,}`; timed four-vectors per pass: `{report['configuration']['processed_four_vectors_per_pass']:,}`; replication factor: `{report['configuration']['replication_factor']}`.",
        "",
        "> This benchmark uses published CMS collision-derived muon four-vectors. It tests coordinate",
        "> transformation throughput, not track fitting, detector propagation, or reconstruction.",
        "",
        "| Kernel | Median seconds | Four-vectors/s |",
        "| --- | ---: | ---: |",
    ]
    for name, row in report["results"].items():
        lines.append(f"| `{name}` | {row['median_seconds']:.6f} | {row['vectors_per_second']:,.0f} |")
    lines.extend(
        [
            "",
            "## Measured deltas",
            "",
            f"- Direct map versus scalar control: `{report['comparisons']['speedup_vs_scalar']:.3f}x`.",
            f"- Direct map versus vectorized control: `{report['comparisons']['speedup_vs_vectorized_control']:.3f}x`.",
            f"- Maximum absolute numerical delta: `{report['correctness']['maximum_absolute_difference']:.3e}`.",
            f"- Strict synthetic `rtol=atol=1e-12` check: `{report['correctness']['all_kernels_equivalent']}`.",
            f"- Scale-aware 128-epsilon backward-error check: `{report['correctness']['scale_aware_float64_consistency']['all_within_bound']}`.",
            "",
            "## Scope",
            "",
            "The source is a CC0 derived education dataset and is not suitable for a full physics analysis.",
            "Neither CMS nor CERN endorses this benchmark. Frozen BHSM predictions are unchanged.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--replication-factor", type=int, default=10)
    parser.add_argument("--output", type=Path, default=Path("artifacts/cern_open_data_benchmark/results.json"))
    parser.add_argument("--markdown", type=Path, default=Path("docs/cern_open_data_benchmark.md"))
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    manifest = load_manifest(args.manifest)
    if args.download and not args.data.exists():
        download_open_data(manifest, args.data)
    vectors = load_cms_dimuon_vectors(args.data, manifest)
    report = build_report(
        vectors.states,
        manifest,
        vectors.source_sha256,
        args.repeats,
        args.replication_factor,
    )
    write_json(args.output, report)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.write_text(markdown(report), encoding="utf-8")
    if args.summary:
        print(
            f"status={report['status']} unique_vectors={len(vectors.states):,} "
            f"processed_per_pass={report['configuration']['processed_four_vectors_per_pass']:,} "
            f"speedup_vs_vectorized_control={report['comparisons']['speedup_vs_vectorized_control']:.3f}x "
            f"max_delta={report['correctness']['maximum_absolute_difference']:.3e}"
        )
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
