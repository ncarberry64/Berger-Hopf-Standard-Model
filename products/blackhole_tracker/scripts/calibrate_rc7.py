"""Prepare or run the separately frozen current-kernel calibration campaign.

No study executes on import. Preparation parses two hash-verified cadence
parents but fits no measured brightness. Execution requires an exact reviewed
freeze and root admission, writes only a fresh external directory, and retains
all planned cases including exceptions and unattempted cases.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import gzip
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import platform
import sys
import time
import traceback

PRODUCT = Path(__file__).resolve().parents[1]
STUDY = PRODUCT / "research/validation_20261024"
sys.path.insert(0, str(PRODUCT))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def write_json(path, value):
    payload = encoded(value)
    with Path(path).open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    return hashlib.sha256(payload).hexdigest()


def write_gzip(path, value):
    payload = encoded(value)
    compressed = gzip.compress(payload, compresslevel=5, mtime=0)
    with Path(path).open("xb") as stream:
        stream.write(compressed)
        stream.flush()
        os.fsync(stream.fileno())
    return {"path": str(path), "bytes": len(compressed), "sha256": hashlib.sha256(compressed).hexdigest(),
            "canonical_json_sha256": hashlib.sha256(payload).hexdigest()}


def module():
    specification = importlib.util.spec_from_file_location("bhsm_rc7_calibration_study", STUDY / "calibration_study.py")
    value = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(value)
    return value


def pins(paths):
    return [{"path": str(path.resolve()), "bytes": path.stat().st_size, "sha256": sha(path)} for path in paths]


def unchanged(records):
    return all(Path(row["path"]).stat().st_size == row["bytes"] and sha(row["path"]) == row["sha256"] for row in records)


def prepare(data_root, out):
    import numpy as np
    import scipy
    from bhtracker.observations import load_ogle_photometry
    from bhtracker.provenance import VERSION

    out.mkdir(parents=True, exist_ok=False)
    protocol_path = STUDY / "PROTOCOL_v1.json"
    protocol = json.loads(protocol_path.read_bytes())
    selection_path = data_root / "pilot_selection.json"
    download_path = data_root / "download_manifest.json"
    selection, downloaded = json.loads(selection_path.read_bytes()), json.loads(download_path.read_bytes())
    manifest = {row["relative_path"]: row for row in downloaded["files"]}
    originals = [selection_path, download_path]
    parents = []
    for index, stratum in enumerate(("long_duration", "ordinary_duration_control")):
        selected = sorted((r for r in selection["selected"] if r["stratum"] == stratum), key=lambda r: r["event_id"])[0]
        assert selected["event_id"] == protocol["photometric_cadence_selection"]["ids"][index]
        raw = data_root / selected["relative_path"]
        assert sha(raw) == manifest[selected["relative_path"]]["sha256"]
        originals.append(raw)
        parent = load_ogle_photometry(raw, metadata=selected)
        parent_path = out / f"CADENCE_PARENT_{index}.json"
        parent_hash = write_json(parent_path, parent.to_dict())
        assert parent_path.read_bytes() == encoded(parent.to_dict())
        parents.append({"index": index, "event_id": selected["event_id"], "stratum": stratum,
                        "path": str(parent_path.resolve()), "sha256": parent_hash, "rows": len(parent.rows),
                        "raw_path": str(raw.resolve()), "raw_sha256": sha(raw),
                        "truth": {"t0": protocol["photometric_cadence_selection"]["t0_native_relative_days"][index],
                                  "tE_days": protocol["photometric_cadence_selection"]["tE_days"][index],
                                  "u0": .3, "source_fraction": .65, "baseline_magnitude": 18.}})
    package_sources = sorted(p for p in (PRODUCT / "bhtracker").rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc")
    source_paths = package_sources + [Path(__file__).resolve(), STUDY / "calibration_study.py", protocol_path]
    freeze = {"schema": "bhsm.rc7.calibration_execution_freeze.v1", "status": "FROZEN_NOT_EXECUTED",
              "protocol": protocol, "protocol_sha256": sha(protocol_path), "parents": parents,
              "source_pins": pins(source_paths), "original_pins": pins(originals),
              "runtime": {"python": platform.python_version(), "executable": sys.executable,
                          "platform": platform.platform(), "machine": platform.machine(),
                          "numpy": np.__version__, "scipy": scipy.__version__, "product_version": VERSION,
                          "package_import_root": str((PRODUCT / "bhtracker").resolve()),
                          "threads": {key: os.environ.get(key) for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")}},
              "scientific_execution_performed": False,
              "boundary": "Cadence intake only; no raw brightness fit, scientific draw or optimization. Exact source review/admission needed for execution."}
    path = out / "STUDY_EXECUTION_FREEZE_v1.json"
    print(json.dumps({"prepared": True, "freeze": str(path), "sha256": write_json(path, freeze),
                      "cadence_rows": [r["rows"] for r in parents]}), flush=True)


def planned_cases(protocol):
    cases = []
    for spec in protocol["resolved_blocks"]:
        for replicate in range(spec["replicates"]):
            cases.append({"kind": "resolved", "block_id": spec["id"], "block": spec["block"],
                          "role": spec["role"], "replicate": replicate, "spec": spec,
                          "fits": spec["fit_nuisances"]})
    for parent_index in (0, 1):
        for family_index, family in enumerate(protocol["photometric_families"]):
            for replicate in range(family["replicates_per_cadence"]):
                cases.append({"kind": "photometry", "block_id": f"P{parent_index}_{family['family']}",
                              "block": 100 + 10*parent_index + family_index, "parent_index": parent_index,
                              "role": family["role"], "family": family["family"], "replicate": replicate,
                              "fits": ["rectilinear_pspl"]})
    return cases


def summarize(protocol, cases, rows, helper):
    from scipy.stats import binomtest

    groups = {}
    for case in cases:
        for nuisance in case["fits"]:
            key = (case["block_id"], nuisance)
            groups.setdefault(key, {"planned": 0, "rows": [], "case": case})["planned"] += 1
    for row in rows:
        groups[(row["block_id"], row["nuisance"])]["rows"].append(row)
    summaries = []
    local_tests = []
    for (block, nuisance), group in groups.items():
        n = group["planned"]
        records = group["rows"]
        terminal = [row for row in records if row["state"] != "NOT_ATTEMPTED"]
        scored = [row for row in records if row.get("score") is not None]
        summary = {"block_id": block, "nuisance": nuisance, "planned": n, "attempted": len(terminal),
                   "scored": len(scored), "states": dict(Counter(row["state"] for row in records)),
                   "fit_statuses": dict(Counter(row["score"]["status"] for row in scored)),
                   "profile_states": dict(Counter(row.get("profile_state", "NOT_APPLICABLE") for row in records)),
                   "coverage": {}, "role": group["case"]["role"]}
        matching = group["case"]["role"] == "coverage" or group["case"].get("family") == "pspl"
        if matching:
            names = helper.PARAMETERS if group["case"]["kind"] == "resolved" else ("t0", "tE_days", "u0")
            for index, name in enumerate(names):
                count = sum(bool(r["score"]["covered_before_goodness_selection"][index]) for r in scored)
                available = sum(bool(r["score"]["interval_available"][index]) for r in scored)
                usable_cover = sum(bool(r["score"]["usable_and_covered"][index]) for r in scored)
                estimate = helper.binomial_summary(count, len(terminal), n)
                estimate.update(interval_unavailable=n-available,
                                availability_completion_bounds=[count/n, (count+n-available)/n],
                                usable_and_covered=usable_cover)
                errors = [r["score"]["bias"][index] for r in scored
                          if r["score"]["interval_available"][index] and r["score"].get("bias") is not None]
                if errors:
                    import numpy as np
                    estimate["conditional_available_interval_bias"] = float(np.mean(errors))
                    estimate["conditional_available_interval_scatter_ddof1"] = float(np.std(errors, ddof=1)) if len(errors) > 1 else None
                    estimate["conditional_bias_sample_count"] = len(errors)
                if len(terminal) == n:
                    pvalue = float(binomtest(count, n, p=.95).pvalue)
                    estimate["exact_nominal95_test_p"] = pvalue
                    estimate["gross_miscalibration_at_bonferroni_0_01_over_28"] = pvalue < .01/28
                    local_tests.append({"block": block, "parameter": name, "pvalue": pvalue,
                                        "flag": pvalue < .01/28})
                summary["coverage"][name] = estimate
        if group["case"].get("family") == "pspl":
            covered = sum(r["score"]["profile_truth_member95"] for r in scored)
            available = sum(r["score"]["profile_truth_membership_resolved"] for r in scored)
            summary["timescale_reference_set_truth_membership"] = helper.binomial_summary(covered, len(terminal), n)
            summary["timescale_reference_set_truth_membership"].update(unavailable=n-available,
                qualification="Conservative interior truth-point reference-set membership; not complete endpoints/nonregular coverage.")
            if len(terminal) == n:
                pvalue = float(binomtest(covered, n, p=.95).pvalue)
                summary["timescale_reference_set_truth_membership"]["exact_nominal95_test_p"] = pvalue
                local_tests.append({"block": block, "parameter": "tE_reference_set", "pvalue": pvalue,
                                    "flag": pvalue < .01/28})
        for metric in ("screen_nonrejection", "motion_snr_ge5", "mass_comparator_3msun_lower_crossed", "motion_covariance_available", "unresolved_mass_and_distance"):
            if scored and metric in scored[0]["score"]:
                count = sum(bool(r["score"][metric]) for r in scored)
                summary[metric] = helper.binomial_summary(count, len(terminal), n)
        summaries.append(summary)
    return {"blocks": summaries, "local_reference_tests": local_tests,
            "multiplicity": "28prospectively declared tests; Bonferroni family alpha0.01; no post-outcome retuning",
            "blackhole_false_positive_rate": None, "blackhole_false_negative_rate": None,
            "classification_qualification": "No implemented BH classifier is evaluated. Screen nonrejection and synthetic optical mass comparators are distinct conditional metrics, not BH probabilities."}


def residual_plot(path, case, raw, result):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    figure, axes = plt.subplots(2, 1, figsize=(8, 5), constrained_layout=True)
    if case["kind"] == "resolved":
        residual = np.asarray(result["whitened_residuals"])
        axes[0].plot(np.asarray(raw["epochs_yr"]), np.asarray(result["center_track_mas"])[:, 0], "o-")
        axes[0].set(xlabel="Supplied observer Julian year", ylabel="Fitted center X (mas)")
        axes[1].plot(residual, ".")
        axes[1].set(xlabel="Whitened component in supplied row order", ylabel="Whitened residual")
    else:
        from bhtracker.observations import UnresolvedPhotometry
        data = UnresolvedPhotometry(raw)
        order = np.argsort(data.times, kind="stable")
        axes[0].errorbar(data.times, data.magnitudes, yerr=data.errors, fmt=".", ms=2, alpha=.35)
        axes[0].plot(data.times[order], np.asarray(result["predictions_magnitude"])[order], linewidth=1)
        axes[0].invert_yaxis()
        axes[0].set(xlabel="Native relative HJD days; underlying clock unspecified", ylabel="Synthetic I magnitude")
        axes[1].plot(data.times, result["standardized_residuals"], ".", ms=2)
        axes[1].set(xlabel="Native relative HJD days", ylabel="Standardized residual")
    axes[1].axhline(0, color="black", linewidth=.5)
    figure.suptitle(f"SYNTHETIC ONLY | {case['block_id']} | replicate 0 | no BH identification", fontsize=10)
    figure.savefig(path, dpi=140)
    plt.close(figure)


def execute(args):
    if sha(args.freeze) != args.freeze_sha256 or sha(args.admission) != args.admission_sha256:
        raise ValueError("exact freeze/admission hashes required")
    freeze = json.loads(args.freeze.read_bytes())
    admission = json.loads(args.admission.read_bytes())
    if admission.get("execution_admitted") is not True or admission.get("freeze_sha256") != args.freeze_sha256:
        raise ValueError("root execution admission missing")
    if not unchanged(freeze["source_pins"]+freeze["original_pins"]):
        raise ValueError("source/original data changed before execution")
    for parent in freeze["parents"]:
        if sha(parent["path"]) != parent["sha256"]:
            raise ValueError("cadence parent changed")
    import numpy as np
    import scipy
    from bhtracker import fit, load_dataset
    from bhtracker.photometry import fit_photometry, profile_timescale
    from bhtracker.observations import UnresolvedPhotometry
    from bhtracker.provenance import VERSION

    runtime = freeze["runtime"]
    if (platform.python_version(), np.__version__, scipy.__version__, VERSION) != (runtime["python"], runtime["numpy"], runtime["scipy"], runtime["product_version"]):
        raise ValueError("frozen runtime/version mismatch")
    if Path(sys.executable).resolve() != Path(runtime["executable"]).resolve():
        raise ValueError("frozen interpreter path mismatch")
    if {key: os.environ.get(key) for key in runtime["threads"]} != runtime["threads"]:
        raise ValueError("frozen thread configuration mismatch")
    helper = module()
    protocol = freeze["protocol"]
    cases = planned_cases(protocol)
    parents = [json.loads(Path(row["path"]).read_bytes()) for row in freeze["parents"]]
    out = args.output
    if out.resolve().is_relative_to(PRODUCT.resolve()):
        raise ValueError("results must be external to the product")
    out.mkdir(parents=True, exist_ok=False)
    for name in ("generated", "outcomes", "residuals"):
        (out / name).mkdir()
    write_json(out / "FREEZE_COPY.json", freeze)
    write_json(out / "ADMISSION_COPY.json", admission)
    start, saved_bytes, rows, stopped = time.monotonic(), 0, [], None
    plot_failures = []
    with (out / "ATTEMPT_LEDGER.jsonl").open("x", encoding="utf-8", newline="\n") as ledger:
        def log(event):
            ledger.write(encoded(event).decode("utf-8"))
            ledger.flush()
            os.fsync(ledger.fileno())
        for case_index, case in enumerate(cases):
            if time.monotonic()-start > protocol["budgets"]["wall_seconds"]:
                stopped = "WALL_BUDGET_EXHAUSTED"
            if saved_bytes > protocol["budgets"]["saved_bytes"]:
                stopped = "STORAGE_BUDGET_EXHAUSTED"
            if case_index % 32 == 0 and not unchanged(freeze["source_pins"]+freeze["original_pins"]):
                stopped = "FROZEN_SOURCE_OR_RAW_DATA_CHANGED"
            if stopped:
                for pending in cases[case_index:]:
                    for nuisance in pending["fits"]:
                        rows.append({"block_id": pending["block_id"], "nuisance": nuisance, "replicate": pending["replicate"],
                                     "state": "NOT_ATTEMPTED", "error": stopped})
                log({"stage": "CAMPAIGN_STOPPED", "reason": stopped, "next_case_index": case_index})
                break
            record = {"block_id": case["block_id"], "replicate": case["replicate"], "case_index": case_index}
            log({**record, "stage": "GENERATION_STARTED"})
            try:
                def generate():
                    if case["kind"] == "resolved":
                        return helper.resolved_draw(case["spec"], case["block"], case["replicate"])
                    return helper.photometry_draw(parents[case["parent_index"]], freeze["parents"][case["parent_index"]]["truth"],
                                                  case["family"], case["block"], case["replicate"])
                raw, truth, random_audit = generate()
                first = {"dataset": raw, "truth": truth, "random_audit": random_audit, "case": case}
                raw2, truth2, audit2 = generate()
                if encoded(first) != encoded({"dataset": raw2, "truth": truth2, "random_audit": audit2, "case": case}):
                    raise ValueError("generation not reproducible from the same fixed key")
                generated = write_gzip(out / "generated" / (random_audit["case_id"]+".json.gz"), first)
                saved_bytes += generated["bytes"]
                log({**record, "stage": "GENERATED_INPUT_FROZEN_BEFORE_FIT", "input": generated})
            except Exception as error:
                for nuisance in case["fits"]:
                    rows.append({**record, "nuisance": nuisance, "state": "GENERATION_FAILED", "error_type": type(error).__name__, "error": str(error)})
                log({**record, "stage": "GENERATION_FAILED", "error_type": type(error).__name__, "error": str(error)})
                continue
            for nuisance in case["fits"]:
                row = {**record, "nuisance": nuisance, "input": generated, "state": "FIT_STARTED"}
                log({**record, "nuisance": nuisance, "stage": "FIT_STARTED"})
                fit_result, profile_result = None, None
                try:
                    if case["kind"] == "resolved":
                        fit_result = fit(load_dataset(raw), nuisance=nuisance, **protocol["fit_options"]["resolved"])
                        row["score"] = helper.resolved_score(fit_result, truth)
                    else:
                        fit_result = fit_photometry(UnresolvedPhotometry(raw), **protocol["fit_options"]["photometry"])
                        if case["family"] == "pspl":
                            try:
                                profile_result = profile_timescale(UnresolvedPhotometry(raw), fit_result, [truth["tE_days"]],
                                    max_nfev=protocol["fit_options"]["photometry_profile"]["max_nfev"])
                                row["profile_state"] = "RETURNED"
                            except Exception as error:
                                row["profile_state"] = "FAILED"
                                row["profile_error"] = {"type": type(error).__name__, "message": str(error), "traceback": traceback.format_exc()}
                        row["score"] = helper.photometry_score(fit_result, truth, case["family"],
                            profile_result["rows"][0] if profile_result is not None else None)
                    row["state"] = "RETURNED"
                except Exception as error:
                    row.update(state="FIT_OR_SCORE_FAILED", error_type=type(error).__name__, error=str(error), traceback=traceback.format_exc())
                try:
                    artifact = write_gzip(out / "outcomes" / (random_audit["case_id"]+"_"+nuisance+".json.gz"),
                        {"row": row, "result": fit_result, "profile_result": profile_result})
                    saved_bytes += artifact["bytes"]
                    row["outcome"] = artifact
                except Exception as error:
                    row.update(state="OUTCOME_SERIALIZATION_FAILED", error_type=type(error).__name__, error=str(error))
                    row.pop("score", None)
                rows.append(row)
                log({**record, "nuisance": nuisance, "stage": "FIT_TERMINAL", "state": row["state"],
                     "fit_status": row.get("score", {}).get("status"), "outcome": row.get("outcome"), "error": row.get("error")})
                if case["replicate"] == 0 and fit_result is not None:
                    try:
                        plot_path = out / "residuals" / f"{case['block_id']}_{nuisance}.png"
                        residual_plot(plot_path, case, raw, fit_result)
                        saved_bytes += plot_path.stat().st_size
                    except Exception as error:
                        plot_failures.append({**record, "nuisance": nuisance, "error": str(error)})
                        log({**record, "stage": "PLOT_FAILED", "error": str(error)})
            if (case_index+1) % 32 == 0:
                print(json.dumps({"datasets_completed": case_index+1, "planned_datasets": len(cases), "fits_recorded": len(rows),
                                  "elapsed_seconds": time.monotonic()-start, "saved_bytes": saved_bytes}), flush=True)
    source_same = unchanged(freeze["source_pins"]+freeze["original_pins"])
    summary = summarize(protocol, cases, rows, helper)
    report = {"schema": "bhsm.rc7.current_kernel_calibration_result.v1", "status": "COMPLETE" if stopped is None and source_same else "NOT_COMPLETED",
              "freeze_sha256": args.freeze_sha256, "admission_sha256": args.admission_sha256,
              "planned_datasets": len(cases), "planned_fits": sum(len(case["fits"]) for case in cases),
              "fit_rows": len(rows), "source_and_raw_bytes_unchanged": source_same,
              "diagnostic_plot_failures": plot_failures,
              "stop_reason": stopped, "elapsed_seconds": time.monotonic()-start, "saved_payload_bytes": saved_bytes,
              "all_results": rows, **summary,
              "BHSM_interpretation": "Conditional same Einstein/GHY exterior as BHSM hypersurface topography, counted once; no new boundary law, spin, core or horizon measurement.",
              "native_known_system_recovery": "NOT_EVALUATED_BY_THIS_SYNTHETIC_EXPERIMENT",
              "publication_hold_cleared": False}
    report_path = out / "COMPLETE_CALIBRATION_RESULT_v1.json"
    report_hash = write_json(report_path, report)
    with (out / "all_planned_fits.csv").open("x", encoding="utf-8", newline="") as stream:
        fields = ["block_id", "replicate", "nuisance", "state", "fit_status", "error_type", "error", "input_sha256", "outcome_sha256"]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({**{key: row.get(key) for key in fields[:4]+["error_type", "error"]},
                             "fit_status": row.get("score", {}).get("status"),
                             "input_sha256": row.get("input", {}).get("sha256"), "outcome_sha256": row.get("outcome", {}).get("sha256")})
    print(json.dumps({"status": report["status"], "planned_datasets": len(cases), "planned_fits": report["planned_fits"],
                      "fits_retained": len(rows), "source_unchanged": source_same, "report_sha256": report_hash,
                      "gross_local_miscalibration_flags": [r for r in summary["local_reference_tests"] if r["flag"]], "output": str(out)}), flush=True)
    return 0 if report["status"] == "COMPLETE" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    prep = subs.add_parser("prepare")
    prep.add_argument("--data-root", required=True, type=Path)
    prep.add_argument("--output", required=True, type=Path)
    run = subs.add_parser("run")
    run.add_argument("--freeze", required=True, type=Path)
    run.add_argument("--freeze-sha256", required=True)
    run.add_argument("--admission", required=True, type=Path)
    run.add_argument("--admission-sha256", required=True)
    run.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args.data_root, args.output)
        return 0
    return execute(args)


if __name__ == "__main__":
    raise SystemExit(main())
