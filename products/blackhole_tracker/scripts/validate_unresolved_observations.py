"""Validate native parsers and synthetic injections at supplied actual cadence.

This intentionally fits no measured light curve. Raw measurements are used only
for timing/error sampling of explicitly synthetic validation. Scientific pilot
fits belong to a separately frozen protocol and separately labelled directory.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bhtracker.observations import (UnresolvedPhotometry, load_ogle_catalog,
    load_ogle_photometry, load_benchmark_photometry, reproduce_pilot_selection)
from bhtracker.astrometry import load_hst_astrometry
from bhtracker.photometry import FIT_PROTOCOL, FIT_PROTOCOL_SHA256, fit_photometry, profile_timescale


def synthetic_at_cadence(data, parameters, seed=None):
    document = data.to_dict()
    t = data.times
    u2 = parameters["u0"] ** 2 + ((t - parameters["t0"]) / parameters["tE_days"]) ** 2
    a = (u2 + 2) / np.sqrt(u2 * (u2 + 4))
    mag = parameters["baseline_magnitude"] - 2.5 * np.log10(1 + parameters["source_fraction"] * (a - 1))
    if seed is not None:
        mag += np.random.default_rng(seed).normal(size=len(t)) * data.errors
    document["metadata"]["synthetic"] = True
    document["metadata"]["validation_role"] = "Synthetic magnitudes at authentic cadence/error sampling; not a fit to observed brightness"
    document["metadata"]["synthetic_truth"] = parameters
    document["metadata"]["synthetic_seed"] = seed
    document["transformations"].append({"operation": "SYNTHETIC_MAGNITUDE_REPLACEMENT",
        "definition": "Independent analytic image-summed PSPL, Gaussian native-magnitude noise when seed is not null",
        "cadence_parent_sha256": data.sha256})
    for row, magnitude in zip(document["rows"], mag):
        row["cadence_parent_source_row_id"] = row["source_row_id"]
        row["source_row_id"] = "SYNTHETIC:" + row["source_row_id"]
        row["magnitude"] = float(magnitude)
        row["quality_flags"] = [*row["quality_flags"], "SYNTHETIC_MAGNITUDE"]
    return UnresolvedPhotometry(document)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.data_root
    manifest = json.loads((root / "pilot_selection.json").read_text())
    catalog = load_ogle_catalog(root / "raw/ogle3/catalogA-full.table")
    selected = reproduce_pilot_selection(catalog, manifest)
    ingestions, loaded = [], {}
    for item in manifest["selected"]:
        data = load_ogle_photometry(root / item["relative_path"], metadata=item)
        loaded[item["event_id"]] = data
        source = data.document["sources"][0]
        ingestions.append({"event_id": item["event_id"], "count": len(data.rows), "raw_sha256": source["sha256"],
            "annotation_count": len(source["annotations"]), "strictly_increasing": source["native_order_strictly_increasing"],
            "duplicate_times": source["duplicate_times"]})
    assert sum(row["count"] for row in ingestions) == 76344
    assert sum(row["annotation_count"] for row in ingestions) == 4
    assert "OGLE3-ULENS-0337" in loaded
    benchmark_root = root / "raw/zenodo_6607578"
    benchmark = load_benchmark_photometry({"OGLE": benchmark_root / "OGLE-2011-BLG-0462.dat",
                                         "MOA": benchmark_root / "MOA-2011-BLG-191.dat"})
    assert len(benchmark.rows) == 61585
    hst = load_hst_astrometry({name: benchmark_root / f"OB110462_HST_{name}.dat" for name in ("F606W", "F814W")})
    assert len(hst["rows"]) == 16 and hst["unique_native_visits"] == 8
    chosen = [next(row for row in manifest["selected"] if row["stratum"] == stratum)
              for stratum in ("long_duration", "ordinary_duration_control")]
    validations = []
    for item, timescale in zip(chosen, (200., 25.)):
        cadence = loaded[item["event_id"]]
        truth = {"t0": item["published_t0_hjd_minus_2450000"], "tE_days": timescale,
                 "u0": .3, "source_fraction": .65, "baseline_magnitude": 18.}
        initial = {"t0": truth["t0"] + 2, "tE_days": timescale * 1.3, "u0": .5}
        exact = fit_photometry(synthetic_at_cadence(cadence, truth), initial=initial, starts=4)
        assert abs(exact["parameters"]["tE_days"] / timescale - 1) < 1e-5
        assert exact["diagnostics"]["chi_square_native_noise"] < 1e-12
        trials = []
        for seed in range(49312, 49320):
            noisy = synthetic_at_cadence(cadence, truth, seed)
            result = fit_photometry(noisy, initial=initial, starts=3)
            sigma = result["uncertainty"]["standard_errors"]["tE_days"]
            trials.append({"seed": seed, "status": result["status"], "tE_days": result["parameters"]["tE_days"],
                "sigma_tE_days": sigma, "timescale_pull": (result["parameters"]["tE_days"] - timescale) / sigma if sigma and sigma > 0 else None,
                "flags": result["flags"], "rank": result["uncertainty"]["rank"],
                "chi_square": result["diagnostics"]["chi_square_native_noise"]})
        validations.append({"role": "SYNTHETIC_VALIDATION_ONLY", "cadence_event_id": item["event_id"],
            "cadence_raw_sha256": cadence.document["sources"][0]["sha256"], "count": len(cadence.rows),
            "truth": truth, "noiseless_recovery": {"parameters": exact["parameters"],
                "chi_square": exact["diagnostics"]["chi_square_native_noise"]}, "noise_trials": trials})
    # A faint-source case exercises the genuine nuisance profile rather than
    # interpreting a formal quadratic error as a covered confidence interval.
    cadence = loaded[chosen[0]["event_id"]]
    weak_truth = {"t0": chosen[0]["published_t0_hjd_minus_2450000"], "tE_days": 200.,
                  "u0": .3, "source_fraction": .02, "baseline_magnitude": 18.}
    weak = synthetic_at_cadence(cadence, weak_truth, seed=49320)
    weak_result = fit_photometry(weak, initial={"t0": weak_truth["t0"], "tE_days": 200., "u0": .3}, starts=4)
    weak_profile = profile_timescale(weak, weak_result, [100., 200., 400., 800.])
    result = {"schema": "bhsm_unresolved_validation/1", "role": "INGESTION_AND_SYNTHETIC_VALIDATION_NOT_REAL_DATA_INFERENCE",
        "protocol": FIT_PROTOCOL, "protocol_sha256": FIT_PROTOCOL_SHA256,
        "selection": selected, "pilot_ingestion": ingestions,
        "pilot_numeric_count": 76344, "historical_benchmark_photometric_count": len(benchmark.rows),
        "historical_benchmark_HST_rows": len(hst["rows"]), "historical_benchmark_HST_unique_visits": hst["unique_native_visits"],
        "historical_benchmark_precision_metadata": hst["precision_inference"],
        "synthetic_actual_cadence_injections": validations,
        "weak_source_synthetic_profile": {"truth": weak_truth, "fit": {"parameters": weak_result["parameters"],
            "uncertainty": weak_result["uncertainty"], "flags": weak_result["flags"]}, "profile": weak_profile},
        "qualification": "Sixteen noisy trials assess recoverability and error scaling; they do not establish calibrated coverage, false-discovery rate or black-hole recovery."}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf8")
    print(json.dumps({"status": "PASS", "output": str(args.output), "output_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
                      "pilot_numeric_rows": 76344, "benchmark_photometric_rows": len(benchmark.rows), "synthetic_noisy_trials": 16}))


if __name__ == "__main__":
    main()
