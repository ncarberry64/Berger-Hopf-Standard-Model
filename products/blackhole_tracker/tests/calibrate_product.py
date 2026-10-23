"""Frozen small-ensemble nonlinear validation, not an observing forecast.

Run from any directory with `python product/tests/calibrate_product.py`.
All 64 draws, including fit/admission failures, enter the coverage denominator.
The script does not alter the physical R1 state and does not fit an R1 signal.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import platform
import sys
import time

import numpy as np
import scipy
from scipy.stats import binomtest, norm

PRODUCT = Path(__file__).resolve().parents[1]
ROOT = PRODUCT.parent
sys.path.insert(0, str(PRODUCT))
from bhtracker import fit, load_dataset  # noqa: E402
from bhtracker.examples import make_example  # noqa: E402
from bhtracker.inference import initial_parameters  # noqa: E402


SEED = 4932026
DRAWS = 64
LEVEL = 0.95
ALPHA = 0.01
Z95 = float(norm.ppf((1.0 + LEVEL) / 2.0))
PARAMETERS = ["mass_msun", "center_x_mas", "center_y_mas",
              "motion_x_mas_yr", "motion_y_mas_yr"]
CRITERIA = {
    "C6": {"starts_each": 3, "initials": ["data_seed", "high_mass_shift", "low_mass_shift"],
           "chi2_upper_exclusive": 1e-6, "mass_relative_error": 1e-5,
           "center_error_over_theta_reference": 1e-5,
           "motion_error_over_theta_reference_per_span": 1e-5},
    "C7": {"seed": SEED, "draws": DRAWS, "family": "gr", "nuisance": "shear",
           "starts": 1, "coverage_level": LEVEL,
           "mass_interval": "log mass Gaussian, sigma_logM=sigma_M/M",
           "center_motion_interval": "additive local Gaussian",
           "coverage_denominator": DRAWS, "failure_counts_as_miss": True,
           "binomial_null": LEVEL, "binomial_alternative": "two-sided",
           "binomial_alpha_each_parameter": ALPHA,
           "multiple_testing_adjustment": "none; all five tests reported",
           "interval_kind": "local Gaussian with supplied known covariance; no chi2 scaling"},
    "C8": {"fixture": "cosmological_short_track", "noise": False,
           "required": "no TRACKED status and unresolved motion"},
    "C11": {"fixture": "ordinary_shear", "noise": False,
            "omitted_nuisance": "none", "admitted_nuisance": "shear",
            "goodness_of_fit_reject_below": 0.001,
            "required": "omitted shear rejects, admitted shear accepts"},
}


def digest(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def vector(parameters):
    return np.asarray([parameters["mass_msun"], *parameters["center_mas"],
                       *parameters["proper_motion_mas_yr"]], dtype=float)


def brief(result):
    return {key: result[key] for key in ["status", "estimates", "uncertainty", "chi2", "dof",
            "goodness_of_fit_p", "optimizer_converged", "motion_snr", "rank", "diagnostics",
            "multistart_chi2"]}


def safe_fit(raw, **kwargs):
    try:
        result = fit(load_dataset(raw), family="gr", **kwargs)
        return result, None
    except Exception as error:  # Retain every failure rather than stop/drop a draw.
        return None, {"type": type(error).__name__, "message": str(error)}


def c6_recovery(raw, truth):
    data = load_dataset(raw)
    seed = initial_parameters(data)
    # Derive perturbation scales from the measured pair separation, not truth.
    theta = float(np.median(np.linalg.norm(data.observations[:, :2] - data.observations[:, 2:4], axis=1)) / 2.0)
    span = max(float(np.ptp(data.epochs)), 1.0)
    starts = [("data_seed", None)]
    for label, mass_factor, sign in [("high_mass_shift", 1.5, 1.0), ("low_mass_shift", 0.65, -1.0)]:
        initial = deepcopy(seed)
        initial["mass_msun"] *= mass_factor
        initial["center_mas"] = (np.asarray(initial["center_mas"]) + sign * theta * np.asarray([0.2, -0.15])).tolist()
        initial["proper_motion_mas_yr"] = (np.asarray(initial["proper_motion_mas_yr"]) + sign * theta / span * np.asarray([0.1, -0.08])).tolist()
        phase = np.arange(data.n)
        initial["source_mas"] = (np.asarray(initial["source_mas"]) + sign * theta * np.column_stack([0.05 * np.cos(phase), 0.08 * np.sin(phase)])).tolist()
        initial["shear"] = [sign * 0.015, -sign * 0.01]
        starts.append((label, initial))
    records = []
    for label, initial in starts:
        result, error = safe_fit(raw, starts=3, nuisance="shear", initial=initial)
        record = {"initial": label, "error": error, "initial_parameters": initial}
        if result is not None:
            actual = vector(result["estimates"])
            expected = vector(truth)
            theta_ref = float(result["model"]["theta_reference_mas"])
            checks = {"chi2": bool(result["chi2"] < 1e-6),
                      "mass": bool(abs(actual[0] / expected[0] - 1.0) <= 1e-5),
                      "center": bool(np.max(abs(actual[1:3] - expected[1:3])) <= 1e-5 * theta_ref),
                      "motion": bool(np.max(abs(actual[3:5] - expected[3:5])) <= 1e-5 * theta_ref / span),
                      "accepted": result["status"] != "FIT_REJECTED"}
            record.update({"result": brief(result), "checks": checks, "pass": all(checks.values())})
        else:
            record["pass"] = False
        records.append(record)
    return {"pass": all(r["pass"] for r in records), "records": records,
            "perturbation_theta_from_pair_mas": theta, "span_yr": span}


def c7_calibration(raw, truth):
    covariance = np.asarray(raw["covariance"])
    lower = np.linalg.cholesky(covariance)
    exact = np.asarray(raw["observations"])
    expected = vector(truth)
    rng = np.random.default_rng(SEED)
    records = []
    for index in range(DRAWS):
        draw = deepcopy(raw)
        noise = lower @ rng.standard_normal(covariance.shape[0])
        draw["observations"] = (exact + noise.reshape(exact.shape)).tolist()
        draw["provenance"].update({"noise_added": True, "calibration_seed": SEED,
                                   "calibration_draw": index})
        result, error = safe_fit(draw, starts=1, nuisance="shear")
        record = {"draw": index, "dataset_sha256": load_dataset(draw).sha256,
                  "noise_sha256": hashlib.sha256(noise.tobytes()).hexdigest(),
                  "error": error, "covered": [False] * 5}
        if result is not None:
            record["result"] = brief(result)
            actual = vector(result["estimates"])
            unc = result["uncertainty"]
            sigma_raw = [unc["mass_msun"], *unc["center_mas"], *unc["proper_motion_mas_yr"]]
            usable = result["status"] != "FIT_REJECTED" and result["optimizer_converged"]
            intervals = []
            covered = []
            for parameter, (value, sigma, target) in enumerate(zip(actual, sigma_raw, expected)):
                valid = usable and sigma is not None and np.isfinite(sigma) and sigma > 0.0
                if not valid:
                    intervals.append([None, None]); covered.append(False)
                elif parameter == 0:
                    bounds = value * np.exp(np.asarray([-1.0, 1.0]) * Z95 * sigma / value)
                    intervals.append(bounds.tolist()); covered.append(bool(bounds[0] <= target <= bounds[1]))
                else:
                    bounds = [float(value - Z95 * sigma), float(value + Z95 * sigma)]
                    intervals.append(bounds); covered.append(bool(bounds[0] <= target <= bounds[1]))
            record.update({"covered": covered, "interval95": intervals,
                           "estimate_minus_truth": (actual - expected).tolist(), "usable_fit": bool(usable)})
        records.append(record)
    summaries = {}
    for index, name in enumerate(PARAMETERS):
        covered = sum(record["covered"][index] for record in records)
        test = binomtest(covered, DRAWS, p=LEVEL, alternative="two-sided")
        ci = test.proportion_ci(confidence_level=LEVEL, method="exact")
        # Successful-fit summaries are explicitly conditional; failures still
        # remain in the all-draw coverage denominator and are listed separately.
        errors = [r["estimate_minus_truth"][index] for r in records if r.get("usable_fit", False)]
        summaries[name] = {"covered": covered, "total": DRAWS, "coverage": covered / DRAWS,
                           "exact95_binomial_interval": [float(ci.low), float(ci.high)],
                           "exact_two_sided_p": float(test.pvalue),
                           "gross_miscalibration_rejected": bool(test.pvalue < ALPHA),
                           "conditional_valid_fit_count": len(errors),
                           "conditional_bias": float(np.mean(errors)) if errors else None,
                           "conditional_scatter_ddof1": float(np.std(errors, ddof=1)) if len(errors) > 1 else None}
    failures = [r["draw"] for r in records if not r.get("usable_fit", False)]
    statuses = Counter(r["result"]["status"] if "result" in r else "EXCEPTION" for r in records)
    return {"pass": not failures and not any(s["gross_miscalibration_rejected"] for s in summaries.values()),
            "coverage_summary": summaries, "fit_failures": failures,
            "status_counts": dict(statuses), "records": records,
            "interpretation": "64 draws can expose gross local-interval miscalibration; passing is not universal coverage certification."}


def controls():
    cosmic, cosmic_truth = make_example("cosmological_short_track", noise=False)
    cosmic_result, cosmic_error = safe_fit(cosmic, starts=1, nuisance="shear")
    cosmic_pass = cosmic_result is not None and cosmic_result["status"] != "TRACKED" and (
        cosmic_result["motion_snr"] is None or cosmic_result["motion_snr"] < 5.0)
    c8 = {"pass": bool(cosmic_pass), "dataset_sha256": load_dataset(cosmic).sha256,
          "truth": cosmic_truth, "error": cosmic_error,
          "result": brief(cosmic_result) if cosmic_result else None}
    shear, shear_truth = make_example("ordinary_shear", noise=False)
    omitted, omitted_error = safe_fit(shear, starts=1, nuisance="none")
    admitted, admitted_error = safe_fit(shear, starts=1, nuisance="shear")
    omit_pass = omitted is not None and omitted["status"] == "FIT_REJECTED" and omitted["goodness_of_fit_p"] < 0.001
    admit_pass = admitted is not None and admitted["status"] != "FIT_REJECTED" and admitted["optimizer_converged"] and admitted["goodness_of_fit_p"] >= 0.001
    c11 = {"pass": bool(omit_pass and admit_pass), "dataset_sha256": load_dataset(shear).sha256,
           "truth": shear_truth, "omitted": brief(omitted) if omitted else None,
           "omitted_error": omitted_error, "admitted": brief(admitted) if admitted else None,
           "admitted_error": admitted_error}
    return c8, c11


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=PRODUCT / "validation/product_calibration_receipt.json")
    args = parser.parse_args()
    started = time.perf_counter()
    source_paths = ["product/tests/calibrate_product.py", "product/bhtracker/examples.py",
                    "product/bhtracker/data.py", "product/bhtracker/forward.py", "product/bhtracker/inference.py",
                    "product/bhtracker/physics_admission.py"]
    hashes = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in source_paths}
    raw, truth = make_example("nearby_motion", noise=False)
    report = {"schema_version": 1, "criteria": CRITERIA, "criteria_sha256": digest(CRITERIA),
              "source_sha256": hashes, "runtime": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
              "baseline_dataset_sha256": load_dataset(raw).sha256, "baseline_truth": truth,
              "provenance": "Entirely synthetic supplied-covariance calibration; no observations, horizon identification or R1 sensitivity forecast."}
    report["C6"] = c6_recovery(raw, truth)
    report["C7"] = c7_calibration(raw, truth)
    report["C8"], report["C11"] = controls()
    report["pass"] = all(report[key]["pass"] for key in ["C6", "C7", "C8", "C11"])
    report["source_unchanged_during_run"] = all(hashes[path] == hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in source_paths)
    report["runtime_seconds"] = time.perf_counter() - started
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    summary = {key: report[key]["pass"] for key in ["C6", "C7", "C8", "C11"]}
    print(json.dumps({"pass": report["pass"], "checks": summary, "coverage": report["C7"]["coverage_summary"],
                      "fit_failures": report["C7"]["fit_failures"], "status_counts": report["C7"]["status_counts"],
                      "source_unchanged_during_run": report["source_unchanged_during_run"],
                      "output": str(args.output), "runtime_seconds": report["runtime_seconds"]}, indent=2))
    return 0 if report["pass"] and report["source_unchanged_during_run"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
