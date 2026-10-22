"""Bounded, preregistered follow-up of the original 64-draw mean offset.

The frozen protocol is validation/statistical_risk_protocol.md. No production
inference or original calibration file is edited; no seed/sample is selected
after seeing its result. The correction-confirmation stream stays unused.
"""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys
import time

import numpy as np
import scipy
from scipy.linalg import solve_triangular
from scipy.optimize import least_squares
from scipy.stats import binom, binomtest, chi2, norm

PRODUCT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PRODUCT))
from bhtracker import fit, load_dataset  # noqa: E402
from bhtracker.examples import make_example  # noqa: E402
from bhtracker.forward import LensEngine  # noqa: E402
from bhtracker.inference import ParameterMap  # noqa: E402

ORIGINAL_SEED = 4932026
ORIGINAL_N = 64
HOLDOUT_SEED = 202610210128
HOLDOUT_N = 128
RESERVED_SEED = 202610210129  # Deliberately never instantiated or sampled.
NAMES = ["mass_msun", "center_x_mas", "center_y_mas", "motion_x_mas_yr", "motion_y_mas_yr"]
Z95 = float(norm.ppf(0.975))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def vector(p):
    return np.asarray([p["mass_msun"], *p["center_mas"], *p["proper_motion_mas_yr"]], dtype=float)


def sigma_vector(result):
    u = result["uncertainty"]
    return [u["mass_msun"], *u["center_mas"], *u["proper_motion_mas_yr"]]


def analytic_jacobian(raw, truth):
    """Independent SI point-lens derivatives including image-shift Hessian.

    Basis: log mass, center/theta_ref, motion*T/theta_ref, two shears,
    then independent source/theta_ref coordinates in input row order.
    No production lens functions, derivative routines or constants are used.
    """
    gm, c, pc = 1.3271244e20, 299792458.0, 3.085677581491367e16
    rad_mas = 180.0 * 3600.0 * 1000.0 / np.pi
    g = raw["geometry"]
    mref = raw["analysis"]["reference_mass_msun"]
    length_pc = gm * mref / (c * c * pc)
    theta = np.sqrt(4 * length_pc * g["D_ls_pc"] / (g["D_l_pc"] * g["D_s_pc"])) * rad_mas
    tscale = max(float(np.ptp(raw["epochs_yr"])) / 2.0, 1.0)
    time_scale = 4 * gm * mref * (1 + g["z_l"]) / c**3
    mr = truth["mass_msun"] / mref
    n = len(raw["epochs_yr"])
    J = np.zeros((n, 6, 7 + 2 * n))
    eye = np.eye(2)
    for row, (epoch, source) in enumerate(zip(raw["epochs_yr"], truth["source_mas"])):
        dt = epoch - raw["reference_epoch_yr"]
        center = np.asarray(truth["center_mas"]) + dt * np.asarray(truth["proper_motion_mas_yr"])
        y = (np.asarray(source) - center) / theta
        u = np.linalg.norm(y)
        direction = y / u
        s = np.sqrt(u * u + 4 * mr)
        images = np.asarray([(u + s) / 2 * direction, (u - s) / 2 * direction])
        for col in range(J.shape[2]):
            dc = np.zeros(2)
            dy_source = np.zeros(2)
            if col in (1, 2):
                dc[col - 1] = 1.0
            elif col in (3, 4):
                dc[col - 3] = dt / tscale
            elif col >= 7 and (col - 7) // 2 == row:
                dy_source[(col - 7) % 2] = 1.0
            dy = dy_source - dc
            delta_x, delta_logs, pvalues = [], [], []
            for x in images:
                r2 = float(x @ x)
                xx = np.outer(x, x)
                H0 = mr * (eye / r2 - 2 * xx / r2**2)
                A = eye - H0
                p, grad, Hp = 0.0, np.zeros(2), np.zeros((2, 2))
                if col == 0:
                    p = mr * np.log(np.sqrt(r2))
                    grad, Hp = mr * x / r2, H0
                elif col in (5, 6):
                    G = np.diag([1.0, -1.0]) if col == 5 else np.asarray([[0.0, 1.0], [1.0, 0.0]])
                    p, grad, Hp = float(x @ G @ x / 2), G @ x, G
                dx = np.linalg.solve(A, dy + grad)
                xv = float(x @ dx)
                DH = mr * (-2 * xv * eye / r2**2
                            - 2 * (np.outer(dx, x) + np.outer(x, dx)) / r2**2
                            + 8 * xv * xx / r2**3)
                delta_x.append(dx)
                delta_logs.append(float(np.trace(np.linalg.solve(A, Hp + DH))))
                pvalues.append(p)
            J[row, :4, col] = (theta * (np.asarray(delta_x) + dc)).ravel()
            J[row, 4, col] = delta_logs[0] - delta_logs[1]
            J[row, 5, col] = time_scale * ((images[0] - images[1]) @ dy + pvalues[0] - pvalues[1])
    return J.reshape(6 * n, -1), np.asarray([truth["mass_msun"], theta, theta, theta / tscale, theta / tscale])


def linear_setup(raw, truth):
    J, physical_scale = analytic_jacobian(raw, truth)
    C = np.asarray(raw["covariance"])
    L = np.linalg.cholesky(C)
    white_J = solve_triangular(L, J, lower=True)
    U, s, Vt = np.linalg.svd(white_J, full_matrices=False)
    rank = int(np.sum(s > s[0] * 1e-9))
    pinv = (Vt[:rank].T / s[:rank]) @ U[:, :rank].T
    cov = (Vt[:rank].T / s[:rank]**2) @ Vt[:rank]
    physical_cov = cov[:5, :5] * np.outer(physical_scale, physical_scale)
    return {"L": L, "J": white_J, "pinv": pinv, "cov": cov, "physical_cov": physical_cov,
            "physical_scale": physical_scale, "rank": rank, "singular_values": s}


def noise_stream(L, seed, count):
    rng = np.random.default_rng(seed)
    return [L @ rng.standard_normal(L.shape[0]) for _ in range(count)]


def linear_error(setup, noise):
    white = solve_triangular(setup["L"], noise, lower=True)
    return (setup["pinv"] @ white)[:5] * setup["physical_scale"]


def mean_summary(errors, physical_cov, required_count):
    errors = np.asarray(errors)
    if len(errors) != required_count or not np.all(np.isfinite(errors)):
        return {"complete_stream": False, "finite_estimate_count": len(errors), "required_count": required_count}
    average = np.mean(errors, axis=0)
    scatter = np.std(errors, axis=0, ddof=1)
    known_sigma = np.sqrt(np.diag(physical_cov))
    z = np.sqrt(required_count) * average / known_sigma
    joint = float(required_count * average @ np.linalg.solve(physical_cov, average))
    return {"complete_stream": True, "count": required_count,
            "coordinates": {name: {"mean_error": float(average[j]), "scatter_ddof1": float(scatter[j]),
                "empirical_standard_error_of_mean": float(scatter[j] / np.sqrt(required_count)),
                "mean_over_empirical_SE": float(average[j] * np.sqrt(required_count) / scatter[j]),
                "truth_linear_sigma": float(known_sigma[j]),
                "scatter_over_truth_linear_sigma": float(scatter[j] / known_sigma[j]),
                "mean_z_using_known_linear_covariance": float(z[j]),
                "two_sided_gaussian_reference_p": float(2 * norm.sf(abs(z[j]))),
                "bonferroni_mean_guard_rejected": bool(2 * norm.sf(abs(z[j])) < .002)}
                for j, name in enumerate(NAMES)},
            "joint_mean_chi2_reference": joint, "joint_df": 5, "joint_reference_p": float(chi2.sf(joint, 5)),
            "interpretation": "Gaussian references are exact for the linear control and local diagnostics for the nonlinear estimator."}


def paired_summary(nonlinear, linear, setup):
    paired = np.asarray(nonlinear) - np.asarray(linear)
    sem = np.sqrt(np.diag(setup["physical_cov"]) / len(paired))
    means = np.mean(paired, axis=0)
    return {"coordinates": {name: {"mean_nonlinear_minus_linear": float(means[j]),
                "paired_scatter": float(np.std(paired[:, j], ddof=1)),
                "mean_difference_over_analytic_mean_SE": float(means[j] / sem[j]),
                "max_absolute_difference_over_analytic_single_draw_sigma": float(np.max(abs(paired[:, j])) / (sem[j] * np.sqrt(len(paired))))}
                for j, name in enumerate(NAMES)},
            "maximum_absolute_mean_difference_over_SE": float(np.max(abs(means / sem))),
            "material_at_frozen_0_1_SE": bool(np.max(abs(means / sem)) > .1)}


def draw_dataset(raw, noise, draw, seed, prefix):
    data = deepcopy(raw)
    data["observations"] = (np.asarray(raw["observations"]) + noise.reshape(-1, 6)).tolist()
    if prefix == "original":
        data["provenance"].update({"noise_added": True, "calibration_seed": seed, "calibration_draw": draw})
    else:
        data["provenance"].update({"noise_added": True, "statistical_risk_seed": seed, "statistical_risk_draw": draw})
    return data


def convergence_control(raw, truth, noises, saved):
    records = []
    for index in range(8):
        data = load_dataset(draw_dataset(raw, noises[index], index, ORIGINAL_SEED, "original"))
        record = {"draw": index, "exception": None}
        try:
            standard = fit(data, family="gr", starts=1, nuisance="shear")
            e = LensEngine(data, "gr", reference_mass=standard["model"]["reference_mass_msun"])
            mapping = ParameterMap(e, "shear")
            x = np.asarray(standard["_internal"]["x"])
            def residual(values):
                try:
                    prediction, _ = e.calculate(mapping.decode(values), admit=False)
                    return data.whiten((prediction - data.observations).ravel())
                except (ValueError, FloatingPointError, np.linalg.LinAlgError):
                    return np.full(6 * data.n, 1e8)
            tighter = least_squares(residual, x, bounds=(mapping.lower, mapping.upper), jac="3-point",
                    x_scale="jac", ftol=1e-13, xtol=1e-13, gtol=1e-11, max_nfev=500)
            tight_pars = mapping.decode(tighter.x)
            e.calculate(tight_pars)  # Final public-equivalent physical/branch admission.
            sigma = np.asarray(sigma_vector(standard), dtype=float)
            delta = vector(tight_pars) - vector(standard["estimates"])
            delta_chi = float(standard["chi2"] - tighter.fun @ tighter.fun)
            scaled = delta / sigma
            replay_saved = vector(standard["estimates"]) - vector(saved[index]["result"]["estimates"])
            passed = bool(standard["status"] != "FIT_REJECTED" and tighter.success
                          and np.all(np.isfinite(scaled)) and np.max(abs(scaled)) <= .01 and delta_chi <= 1e-6)
            record.update({"standard_status": standard["status"], "standard_chi2": standard["chi2"],
                    "tight_chi2": float(tighter.fun @ tighter.fun), "chi2_improvement": delta_chi,
                    "tight_success": bool(tighter.success), "tight_nfev": int(tighter.nfev),
                    "parameter_change": delta.tolist(), "parameter_change_over_standard_sigma": scaled.tolist(),
                    "standard_replay_minus_saved": replay_saved.tolist(), "pass": passed})
        except Exception as error:
            record.update({"exception": {"type": type(error).__name__, "message": str(error)}, "pass": False})
        records.append(record)
    return {"pass": all(r["pass"] for r in records), "records": records}


def holdout(raw, truth, setup):
    noises = noise_stream(setup["L"], HOLDOUT_SEED, HOLDOUT_N)
    expected = vector(truth)
    records, errors, linears = [], [], []
    for index, noise in enumerate(noises):
        draw = draw_dataset(raw, noise, index, HOLDOUT_SEED, "holdout")
        record = {"draw": index, "noise_sha256": hashlib.sha256(noise.tobytes()).hexdigest(),
                  "dataset_sha256": load_dataset(draw).sha256, "covered": [False] * 5, "exception": None}
        try:
            result = fit(draw, family="gr", starts=1, nuisance="shear")
            actual = vector(result["estimates"])
            sigma = sigma_vector(result)
            usable = result["status"] != "FIT_REJECTED" and result["optimizer_converged"]
            covered, intervals = [], []
            for j, (value, sd, target) in enumerate(zip(actual, sigma, expected)):
                if not usable or sd is None or not np.isfinite(sd) or sd <= 0:
                    covered.append(False); intervals.append([None, None])
                else:
                    limits = value * np.exp(np.asarray([-1, 1]) * Z95 * sd / value) if j == 0 else np.asarray([value - Z95 * sd, value + Z95 * sd])
                    intervals.append(limits.tolist()); covered.append(bool(limits[0] <= target <= limits[1]))
            err, lin = actual - expected, linear_error(setup, noise)
            if np.all(np.isfinite(err)):
                errors.append(err); linears.append(lin)
            record.update({"status": result["status"], "optimizer_converged": result["optimizer_converged"],
                    "chi2": result["chi2"], "goodness_of_fit_p": result["goodness_of_fit_p"],
                    "estimates": result["estimates"], "uncertainty": result["uncertainty"],
                    "estimate_minus_truth": err.tolist(), "linear_error": lin.tolist(),
                    "interval95": intervals, "covered": covered, "usable_fit": bool(usable),
                    "diagnostics": result["diagnostics"]})
        except Exception as error:
            record["exception"] = {"type": type(error).__name__, "message": str(error)}
        records.append(record)
    coverage = {}
    for j, name in enumerate(NAMES):
        count = sum(r["covered"][j] for r in records)
        test = binomtest(count, HOLDOUT_N, p=.95, alternative="two-sided")
        interval = test.proportion_ci(confidence_level=.95, method="exact")
        coverage[name] = {"covered": count, "total": HOLDOUT_N, "fraction": count / HOLDOUT_N,
                         "exact_binomial_p": float(test.pvalue), "gross_miscalibration_rejected_at_0_01": bool(test.pvalue < .01),
                         "exact95_binomial_interval": [float(interval.low), float(interval.high)]}
    return {"executed": True, "seed": HOLDOUT_SEED, "draws": HOLDOUT_N, "records": records,
            "status_counts": dict(Counter(r.get("status", "EXCEPTION") for r in records)),
            "failed_or_rejected_draws": [r["draw"] for r in records if not r.get("usable_fit", False)],
            "coverage": coverage, "nonlinear_mean": mean_summary(errors, setup["physical_cov"], HOLDOUT_N),
            "linear_mean": mean_summary(linears, setup["physical_cov"], HOLDOUT_N),
            "paired_nonlinear_minus_linear": paired_summary(errors, linears, setup) if len(errors) == HOLDOUT_N else None}


def audit_existing_receipt():
    """Post-hoc explanation of existing residual tails; no fits or new draws.

    This only reconstructs the already-used stream, checks every noise hash,
    and projects that noise with the independent analytic Jacobian. It does
    not change a preregistered guard or the saved nonlinear experiment.
    """
    output = PRODUCT / "validation/statistical_risk_receipt.json"
    report = json.loads(output.read_text(encoding="utf-8"))
    before_sha = sha(output)
    if not report["holdout"]["executed"]:
        raise ValueError("There is no completed holdout to audit")
    raw, truth = make_example("nearby_motion", noise=False)
    setup = linear_setup(raw, truth)
    noises = noise_stream(setup["L"], HOLDOUT_SEED, HOLDOUT_N)
    records = report["holdout"]["records"]
    rows = []
    dof = setup["J"].shape[0] - setup["rank"]
    for noise, record in zip(noises, records):
        if hashlib.sha256(noise.tobytes()).hexdigest() != record["noise_sha256"]:
            raise ValueError("The saved holdout noise hash does not match")
        white = solve_triangular(setup["L"], noise, lower=True)
        residual = white - setup["J"] @ (setup["pinv"] @ white)
        q = float(residual @ residual)
        rows.append({"draw": record["draw"], "linear_minimized_chi2": q,
                     "linear_goodness_p": float(chi2.sf(q, dof)),
                     "saved_nonlinear_chi2": record.get("chi2"),
                     "nonlinear_minus_linear_chi2": None if record.get("chi2") is None else record["chi2"] - q})
    rejected = [r["draw"] for r in rows if r["linear_goodness_p"] < .001]
    clarification = ("The primary mean-error diagnostic uses all finite returned estimator values, "
        "including returned values from a goodness-of-fit rejection; those rejected decisions still "
        "count as coverage misses and are not valid reported tracks. If an exception or nonfinite "
        "estimate removes any of the128 estimator values, the complete-stream mean test is marked "
        "unavailable rather than silently dropping it; any successful-fit-only mean is labeled conditional. "
        "All five coverage tests and all five mean-bias tests remain visible.")
    protocol = PRODUCT / "validation/statistical_risk_protocol.md"
    text = protocol.read_text(encoding="utf-8")
    reconstructed = text.replace(clarification, "All five coverage tests and all five mean-bias tests remain visible.")
    announced_sha = hashlib.sha256(reconstructed.replace("\n", "\r\n").encode("utf-8")).hexdigest()
    if announced_sha != "bb894b022a88df206a3eb6b3fb6a598c892aaec957eb01ec3698351026ae1136":
        raise ValueError("Pre-experiment protocol-history reconstruction failed")
    report["post_run_existing_noise_audit"] = {
        "performed_utc": datetime.now(timezone.utc).isoformat(),
        "pre_postprocessing_receipt_sha256": before_sha,
        "audit_script_sha256": sha(__file__),
        "classification": "Post-hoc descriptive residual-tail explanation using only the existing noise; no new acceptance criterion",
        "additional_nonlinear_fits": 0, "new_random_streams": 0,
        "all_128_saved_noise_hashes_match": True, "dof": dof,
        "linear_goodness_rejected_draws": rejected,
        "saved_nonlinear_rejected_draws": report["holdout"]["failed_or_rejected_draws"],
        "same_rejected_draws": rejected == report["holdout"]["failed_or_rejected_draws"],
        "probability_of_at_least_this_many_under_ideal_linear_guard": float(binom.sf(len(rejected)-1, HOLDOUT_N, .001)),
        "tail_count_probability_interpretation": "Descriptive and post hoc; not a preregistered test, not grounds to discard draws or move thresholds",
        "records": rows,
        "protocol_history": {
            "first_write_utc": "2026-10-22T00:00:33.939309+00:00",
            "announced_version_tool_result_utc": "2026-10-22T00:00:47.5431666+00:00",
            "announced_sha256": announced_sha,
            "clarification_write_utc": "2026-10-22T00:01:42.203158+00:00",
            "experiment_protocol_sha256": report["protocol_sha256"],
            "change": "Added explicit complete-stream finite-estimator mean policy, including returned rejected fits; exception/nonfinite means unavailable. No model, seed, budget, interval or threshold changed.",
            "exact_announced_hash_reconstructed_by_reversing_clarification": True,
            "experiment_script_created_utc": "2026-10-22T00:03:01.500965+00:00",
            "experiment_tool_call_utc": "2026-10-22T00:03:13.626+00:00",
            "experiment_receipt_written_utc": "2026-10-22T00:03:25.464865+00:00",
            "evidence": "Own timestamped Codex session log plus filesystem times; the initial announced file was revised before experiment generation, not immutable."
        },
        "experiment_source_audit": {
            "git_head": "79c374d6ae3331b63fc50846ef60cabfcdd2eb9f",
            "recorded_data_inference_forward_hashes_exactly_match_head_bytes": True,
            "start_end_hash_check": report["source_unchanged_during_run"],
            "production_inference_modified_by_this_review": False,
            "current_files": {p: {"sha256": sha(PRODUCT / p),
                "modified_utc": datetime.fromtimestamp((PRODUCT / p).stat().st_mtime, timezone.utc).isoformat()}
                for p in ["bhtracker/data.py", "bhtracker/inference.py", "bhtracker/forward.py"]},
            "later_edit_scope": "Subsequent root edits add strict admission/JSON messages, provenance/configuration recording and a max_nfev argument guard; the least-squares algorithm, residual equations and covariance formula are unchanged."
        }
    }
    output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "same_rejected_draws": rejected == report["holdout"]["failed_or_rejected_draws"],
        "linear_rejected_draws": rejected, "rejected_records": [r for r in rows if r["draw"] in rejected],
        "post_hoc_tail_count_probability": float(binom.sf(len(rejected)-1, HOLDOUT_N, .001)),
        "protocol_announced_sha256_reconstructed": announced_sha}, indent=2))
    return 0


def main():
    start = time.perf_counter()
    validation = PRODUCT / "validation"
    protocol = validation / "statistical_risk_protocol.md"
    original_path = validation / "product_calibration_receipt.json"
    original_sha = sha(original_path)
    original = json.loads(original_path.read_text(encoding="utf-8"))
    saved = original["C7"]["records"]
    raw, truth = make_example("nearby_motion", noise=False)
    paths = ["bhtracker/data.py", "bhtracker/forward.py", "bhtracker/inference.py", "bhtracker/examples.py",
             "tests/statistical_risk_review.py", "validation/statistical_risk_protocol.md"]
    hashes = {p: sha(PRODUCT / p) for p in paths}
    report = {"schema_version": 1, "question": "Original 64-draw y-motion mean: finite sample versus nonlinear/covariance/convergence error",
              "protocol_sha256": sha(protocol), "original_receipt_sha256": original_sha,
              "original_criteria_sha256": original["criteria_sha256"], "source_sha256": hashes,
              "runtime": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
              "production_inference_modified": False, "reserved_confirmation_seed": RESERVED_SEED,
              "reserved_confirmation_stream_generated": False}
    setup = linear_setup(raw, truth)
    noises = noise_stream(setup["L"], ORIGINAL_SEED, ORIGINAL_N)
    noise_matches = [hashlib.sha256(noise.tobytes()).hexdigest() == saved[i]["noise_sha256"] for i, noise in enumerate(noises)]
    baseline_matches = load_dataset(raw).sha256 == original["baseline_dataset_sha256"]
    report["original_audit"] = {"baseline_hash_matches": baseline_matches, "noise_hashes_matching": sum(noise_matches),
            "noise_count": len(noises), "all_noise_hashes_match": all(noise_matches),
            "original_coverage_summary_unchanged": original["C7"]["coverage_summary"]}
    reference = fit(raw, family="gr", starts=1, nuisance="shear")
    production_J = np.asarray(reference["_internal"]["jacobian"])
    production_cov = np.asarray(reference["_internal"]["covariance"])
    Jdiff = float(np.linalg.norm(production_J - setup["J"]) / np.linalg.norm(setup["J"]))
    covdiff = float(np.max(abs(np.diag(production_cov)[:5] / np.diag(setup["cov"])[:5] - 1)))
    report["independent_linear_control"] = {"rank": setup["rank"], "columns": setup["J"].shape[1],
            "singular_values": setup["singular_values"].tolist(), "physical_covariance_five_coordinates": setup["physical_cov"].tolist(),
            "relative_Frobenius_J_discrepancy": Jdiff, "maximum_relative_five_diagonal_covariance_discrepancy": covdiff,
            "pass": bool(setup["rank"] == 25 and Jdiff <= 1e-5 and covdiff <= 1e-4)}
    linear = [linear_error(setup, noise) for noise in noises]
    nonlinear = [r["estimate_minus_truth"] for r in saved]
    report["original_nonlinear_mean"] = mean_summary(nonlinear, setup["physical_cov"], ORIGINAL_N)
    report["original_linear_mean"] = mean_summary(linear, setup["physical_cov"], ORIGINAL_N)
    report["original_paired_nonlinear_minus_linear"] = paired_summary(nonlinear, linear, setup)
    audit_ok = baseline_matches and all(noise_matches) and report["independent_linear_control"]["pass"]
    if audit_ok:
        report["convergence_control"] = convergence_control(raw, truth, noises, saved)
    else:
        report["convergence_control"] = {"pass": False, "executed": False, "reason": "Original audit or independent linear control failed"}
    go = audit_ok and report["convergence_control"]["pass"] and not report["original_paired_nonlinear_minus_linear"]["material_at_frozen_0_1_SE"]
    if go:
        report["holdout"] = holdout(raw, truth, setup)
    else:
        report["holdout"] = {"executed": False, "seed": HOLDOUT_SEED, "stream_generated": False,
                             "reason": "Diagnostic gate failed; notify owner before inference correction"}
    report["original_receipt_unchanged"] = sha(original_path) == original_sha
    report["source_unchanged_during_run"] = all(sha(PRODUCT / p) == h for p, h in hashes.items())
    report["runtime_seconds"] = time.perf_counter() - start
    output = validation / "statistical_risk_receipt.json"
    output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    summary = {"audit": report["original_audit"], "independent_linear_control": report["independent_linear_control"],
               "original_paired_nonlinear_minus_linear": report["original_paired_nonlinear_minus_linear"],
               "convergence_control_pass": report["convergence_control"]["pass"],
               "holdout_executed": report["holdout"]["executed"], "original_receipt_unchanged": report["original_receipt_unchanged"],
               "runtime_seconds": report["runtime_seconds"], "output": str(output)}
    if report["holdout"]["executed"]:
        summary["holdout_coverage"] = report["holdout"]["coverage"]
        summary["holdout_mean"] = report["holdout"]["nonlinear_mean"]
        summary["holdout_status_counts"] = report["holdout"]["status_counts"]
    print(json.dumps(summary, indent=2))
    return 0 if go and report["original_receipt_unchanged"] and report["source_unchanged_during_run"] else 1


if __name__ == "__main__":
    if sys.argv[1:] == ["--audit-existing"]:
        raise SystemExit(audit_existing_receipt())
    if sys.argv[1:]:
        raise SystemExit("Use no arguments for the frozen experiment, or --audit-existing for the saved-noise audit only")
    raise SystemExit(main())
