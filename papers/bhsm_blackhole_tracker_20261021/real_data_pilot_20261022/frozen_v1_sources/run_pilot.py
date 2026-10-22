"""Freeze and execute the supplied 100-event native-observation pilot.

Only `freeze` writes protocol_v1.json. `run` verifies that frozen protocol and
kernel/driver hashes before any measured-light-curve fit. All raw observations
remain external, immutable and hash-verified. Full replay inputs stay private.
"""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import csv
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import platform
import shutil
import sys
import traceback

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BASE = Path(__file__).resolve().parent
PRODUCT = BASE.parents[2] / "product"
sys.path.insert(0, str(PRODUCT))
from bhtracker import __version__
from bhtracker.observations import (load_ogle_catalog, load_ogle_photometry,
    load_benchmark_photometry, reproduce_pilot_selection)
from bhtracker.astrometry import load_hst_astrometry
from bhtracker.photometry import FIT_PROTOCOL, FIT_PROTOCOL_SHA256, fit_photometry, profile_timescale


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf8")


def kernel_hashes():
    return {name: digest(PRODUCT / "bhtracker" / name) for name in
            ("observations.py", "photometry.py", "astrometry.py")}


def integrity(data_root):
    manifest = json.loads((data_root / "download_manifest.json").read_text(encoding="utf8"))
    for item in manifest["files"]:
        path = data_root / item["relative_path"]
        if path.stat().st_size != item["bytes"] or digest(path) != item["sha256"]:
            raise ValueError("immutable raw file mismatch: " + item["relative_path"])
        if item.get("publisher_md5") and hashlib.md5(path.read_bytes()).hexdigest() != item["publisher_md5"]:
            raise ValueError("publisher MD5 mismatch: " + item["relative_path"])
    catalog = load_ogle_catalog(data_root / "raw/ogle3/catalogA-full.table")
    selection = json.loads((data_root / "pilot_selection.json").read_text(encoding="utf8"))
    reproduced = reproduce_pilot_selection(catalog, selection)
    return manifest, catalog, selection, reproduced


def freeze(data_root):
    target = BASE / "protocol_v1.json"
    if target.exists():
        raise ValueError("v1 protocol already frozen; do not overwrite. A changed analysis requires a new version.")
    manifest, _, selection, reproduced = integrity(data_root)
    protocol = {
        "schema": "bhsm_real_data_pilot_protocol/1", "protocol_id": "BHSM-OGLE3-native-pilot-20261022-v1",
        "frozen_utc": datetime.now(timezone.utc).isoformat(), "registration": "Internal frozen protocol; not external preregistration",
        "measured_light_curve_fits_started_before_freeze": False,
        "cohort_id": selection["cohort_id"], "sample_sha256": reproduced["selected_ids_sha256"],
        "download_manifest_sha256": digest(data_root / "download_manifest.json"),
        "selection_manifest_sha256": digest(data_root / "pilot_selection.json"),
        "raw_file_count": len(manifest["files"]), "raw_sha256": {item["relative_path"]: item["sha256"] for item in manifest["files"]},
        "selection": reproduced, "software_version_at_freeze": __version__, "kernel_sha256": kernel_hashes(),
        "driver_sha256": digest(__file__), "fit_protocol": FIT_PROTOCOL, "fit_protocol_sha256": FIT_PROTOCOL_SHA256,
        "baseline": {"starts": 12, "max_nfev": 1500, "noise_scale": 1.0, "allow_negative_blend": False,
                     "equal_instrument_weight": False, "all_100_events": True,
                     "initialization": "Published catalog t0,tE,u0,source fraction and baseline magnitude initialize the first start only; no catalog likelihood term"},
        "observations": {"all_numeric_rows": 76344, "likelihood": "Gaussian native apparent magnitude with explicitly assumed independent errors",
            "time": "HJD relative-day arithmetic only; underlying clock scale remains UNSPECIFIED",
            "native_rows": "retain source line identities, filters, calibrations, errors, aliases and source warning annotations",
            "exclusions": "No clipping, thinning, averaging, duplicate deletion or second application of published error corrections",
            "errors": "Malformed rows cause a retained failure row; no event replacement"},
        "timescale_profiles": {"all_100_events": True, "grid": "17 log-spaced tE values from .25 to 4 times fitted tE, clipped to declared .1..10000-day search bounds; include fitted tE",
            "nuisance_search": "Four deterministic source-fraction seeds, all other nuisance states reoptimized inside the declared photometric domain",
            "reference_level": 1.0, "crossing": "Adjacent admitted, converged grid rows outward from fitted tE bracket a crossing. Refine each bracket by up to16 log-time bisections, genuinely reoptimizing nuisance parameters at every trial, until |delta-1|<=.01 or log bracket width<=.0001. Any unresolved row blocks crossing on that side.",
            "unresolved": "Missing crossing before grid edge, failed reference or search is unresolved; grid truncation is not a physical bound",
            "coverage_claim": False},
        "sensitivity": [{"id": "signed_blend", "all_100_events": True, "allow_negative_blend": True,
                         "meaning": "Calibration-offset phenomenology with source fraction up to10; not negative physical stellar luminosity"},
                        {"id": "noise_scale_1p25", "all_100_events": True, "noise_scale": 1.25,
                         "meaning": "Explicit uniform native-error sensitivity, cannot replace baseline"}],
        "diagnostics": ["native/instrument chi-square and tail probability", "constant and linear-trend BIC screens",
                        "sorted residual runs and lag1 correlation", "seasonal residual offsets", "points above3sigma",
                        "active bounds, rank/null covariance, multistart alternative modes", "signed-blend and noise sensitivity"],
        "further_models": "Flagged periodic variability, binary source/lens or annual parallax need separately validated models/data. Their absence or failed PSPL is not black-hole/BHSM evidence.",
        "followup": {"maximum_recommended": 5,
            "eligibility": ["baseline independent-noise chi-square tail probability >=.01", "multistart confirmed",
                "tE locally identified with finite positive sigma and sigma/tE<.3", "both finite level1 nuisance-profile crossings before grid edges",
                "no runs |z|>3 or seasonal >=10-row |mean/independentSE|>4 flags", "PSPL beats linear trend by deltaBIC>10",
                "no active numerical/model bounds", "both sensitivity fits multistart confirmed and |log(tE_alt/tE_base)|<.2",
                "long-duration stratum or fitted tE>=150days for the compact-lens follow-up shortlist"],
            "ordering": "Lexicographic: abs(log(reduced chi-square)) ascending, profile fractional half-width ascending, fitted tE descending, event ID ascending",
            "meaning": "Archival/modeling/imaging follow-up only; peaks are historical. Long duration is priority context, never a measured mass or black-hole probability.",
            "status": "PHOTOMETRIC_FOLLOWUP_TARGET with MASS_UNRESOLVED; novelty UNRESOLVED until external alias/coordinate literature checks",
            "zero_targets_acceptable": True},
        "benchmark": {"separate_from_100": True, "data_version": "Zenodo6607578 v1.0.0 (2022)",
            "photometric_rows": 61585, "runs": ["joint OGLE/MOA native-noise baseline", "OGLE only", "MOA only", "joint equal-instrument residual-objective sensitivity", "joint signed-blend calibration sensitivity"],
            "initialization": "Literature-independent broad guess t0=5760(HJD-2450000),tE=250days,u0=.05 plus deterministic standard multistart",
            "qualification": "These photometry-only screens are not the published 2022 joint default-weight/equal-weight astrometric analyses and do not recover a mass.",
            "HST": "16 rows at8 shared epochs ingested only. No precision joint inference until original export-time mapping/frame conventions and ephemeris inputs are established; do not guess MJD or reapply filter offsets."},
        "scientific_claims": {"mass_status": "MASS_UNRESOLVED", "distances": None, "absolute_motion": None, "horizon": None,
            "BHSM": "Single ordinary optical potential keeps BHSM Einstein/GHY interpretation schema2. No core, encapsulation or dark-matter mechanism is tested by ordinary PSPL agreement.",
            "novelty": "Events are previously published. No new black-hole interpretation claimed without mass support and primary literature/catalog alias checks.",
            "selection_limits": "Standard-event catalog excluded strong-parallax/exotic cases and pilot enriches long durations; no completeness or population-abundance inference."},
        "output_policy": {"private": "Complete input/native rows, all source-row identities, full fit/prediction/residual JSON and replay inputs in external output directory",
            "git": "Protocol/driver/hashes, compact derived tables/diagnostics, ranking and100 residual plots; third-party raw measurements remain external"}}
    write_json(target, protocol)
    (BASE / "protocol_v1.sha256").write_text(digest(target) + "  protocol_v1.json\n", encoding="ascii")
    print(json.dumps({"status": "FROZEN_BEFORE_REAL_FITS", "protocol": str(target), "sha256": digest(target), "kernel_sha256": kernel_hashes()}), flush=True)


def verify_protocol(data_root):
    path = BASE / "protocol_v1.json"
    expected = (BASE / "protocol_v1.sha256").read_text().split()[0]
    if digest(path) != expected:
        raise ValueError("frozen protocol digest mismatch")
    protocol = json.loads(path.read_text(encoding="utf8"))
    if kernel_hashes() != protocol["kernel_sha256"] or digest(__file__) != protocol["driver_sha256"]:
        raise ValueError("kernel/driver changed since freeze; preserve v1 and make a new protocol version")
    if FIT_PROTOCOL_SHA256 != protocol["fit_protocol_sha256"]:
        raise ValueError("frozen fitting defaults mismatch")
    if digest(data_root / "download_manifest.json") != protocol["download_manifest_sha256"] or digest(data_root / "pilot_selection.json") != protocol["selection_manifest_sha256"]:
        raise ValueError("manifest changed since freeze")
    return protocol


def profile_crossings(profile, center, dataset, result):
    rows = sorted(profile["rows"], key=lambda row: row["tE_days"])
    middle = min(range(len(rows)), key=lambda k: abs(math.log(rows[k]["tE_days"] / center)))
    admitted = lambda row: row.get("status", "").startswith("ADMITTED_") and row.get("delta_chi_square") is not None
    output = {"reference_delta_chi_square": 1., "lower_days": None, "upper_days": None,
              "coverage_claim": False, "grid_min_days": rows[0]["tE_days"], "grid_max_days": rows[-1]["tE_days"],
              "refinement_rows": []}
    if not admitted(rows[middle]):
        output["status"] = "REFERENCE_OR_PROFILE_UNRESOLVED"
        return output
    for direction, key in ((-1, "lower_days"), (1, "upper_days")):
        previous = rows[middle]
        index = middle + direction
        while 0 <= index < len(rows):
            row = rows[index]
            if not admitted(row):
                output[key + "_reason"] = "UNRESOLVED_NUISANCE_SEARCH_BLOCKS_CROSSING"
                break
            if row["delta_chi_square"] >= 1 and previous["delta_chi_square"] < 1:
                inner, outer = previous, row
                for iteration in range(16):
                    trial = math.sqrt(inner["tE_days"] * outer["tE_days"])
                    trial_row = profile_timescale(dataset, result, [trial])["rows"][0]
                    output["refinement_rows"].append(trial_row)
                    if not admitted(trial_row):
                        output[key + "_reason"] = "UNRESOLVED_REFINEMENT_BLOCKS_CROSSING"
                        break
                    if abs(trial_row["delta_chi_square"] - 1) <= .01 or abs(math.log(outer["tE_days"] / inner["tE_days"])) <= .0001:
                        output[key] = trial
                        break
                    if trial_row["delta_chi_square"] < 1:
                        inner = trial_row
                    else:
                        outer = trial_row
                else:
                    output[key + "_reason"] = "REFINEMENT_TOLERANCE_NOT_ESTABLISHED"
                break
            previous = row; index += direction
        if output[key] is None:
            output.setdefault(key + "_reason", "NO_CROSSING_BEFORE_GRID_EDGE_NOT_A_PHYSICAL_LIMIT")
    output["status"] = "BOTH_REFERENCE_LEVEL_CROSSINGS_FOUND_NOT_COVERAGE" if output["lower_days"] is not None and output["upper_days"] is not None else "GRID_INTERVAL_UNRESOLVED"
    return output


def compact_fit(result):
    excluded = {"dataset_input", "predictions_magnitude", "residuals_magnitude", "standardized_residuals", "row_ids", "software_provenance"}
    return {key: value for key, value in result.items() if key not in excluded}


def residual_plot(data, result, target, title):
    time = data.times
    fig, axes = plt.subplots(2, 1, figsize=(8, 5), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    colors = ["#215c95", "#b16024", "#3c884c"]
    for k, instrument in enumerate(data.instruments):
        select = data.instrument_indices == k
        color = colors[k % len(colors)]
        axes[0].scatter(time[select], data.magnitudes[select], s=3, alpha=.45, color=color, label=instrument)
        order = np.argsort(time[select]); x = time[select][order]
        y = np.asarray(result["predictions_magnitude"])[select][order]
        axes[0].plot(x, y, linewidth=.9, color=color)
        axes[1].scatter(time[select], np.asarray(result["standardized_residuals"])[select], s=3, alpha=.45, color=color)
    axes[0].invert_yaxis(); axes[0].set_ylabel("Native apparent magnitude")
    axes[0].legend(fontsize=7); axes[0].set_title(title + " | real observations; mass unresolved", fontsize=9)
    axes[1].axhline(0, color="black", linewidth=.7); axes[1].axhline(3, color="gray", linewidth=.4)
    axes[1].axhline(-3, color="gray", linewidth=.4); axes[1].set_ylabel("Residual / native sigma")
    axes[1].set_xlabel("HJD - 2450000 [day]; clock scale unspecified")
    fig.tight_layout(); target.parent.mkdir(parents=True, exist_ok=True); fig.savefig(target, dpi=110)
    plt.close(fig)


def write_csv(path, rows):
    if not rows:
        path.write_text("event_id,status,mass_status\n", encoding="utf8"); return
    keys = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="", encoding="utf8") as stream:
        writer = csv.DictWriter(stream, fieldnames=keys); writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(value, separators=(",", ":"), allow_nan=False) if isinstance(value, (dict, list)) else value for key, value in row.items()})


def run(data_root, output):
    protocol = verify_protocol(data_root)
    manifest, catalog, selection, reproduced = integrity(data_root)
    output.mkdir(parents=True, exist_ok=True)
    if (output / "run_started.json").exists():
        raise ValueError("output already contains a started run; preserve it and use a separate explicit run directory")
    write_json(output / "run_started.json", {"started_utc": datetime.now(timezone.utc).isoformat(),
        "protocol_sha256": digest(BASE / "protocol_v1.json"), "python": platform.python_version(),
        "dependencies": {name: importlib.metadata.version(name) for name in ("numpy", "scipy", "matplotlib")},
        "product_version": __version__, "kernel_sha256": kernel_hashes()})
    derived = BASE / "derived_v1"; derived.mkdir(parents=True, exist_ok=True)
    rows = []; candidates = []; private_manifest = []
    for index, item in enumerate(selection["selected"], 1):
        event = item["event_id"]
        event_root = output / "events" / event; event_root.mkdir(parents=True, exist_ok=True)
        record = {"event_id": event, "ra_j2000": item["ra_j2000"], "dec_j2000": item["dec_j2000"],
            "ews_alias": item["ews_alias"], "overlap_alias": item["overlap_alias"], "stratum": item["stratum"],
            "published_tE_days": item["published_tE_days"], "status": "PROCESSING", "mass_status": "MASS_UNRESOLVED",
            "mass_msun": None, "lens_distance_pc": None, "absolute_proper_motion_mas_yr": None,
            "novelty_status": "UNRESOLVED_NO_NEW_INTERPRETATION_CLAIM", "previous_study": "Wyrzykowski et al.2015 ApJS216,12 DOI10.1088/0067-0049/216/1/12"}
        try:
            data = load_ogle_photometry(data_root / item["relative_path"], metadata={**item, "catalog": catalog[event]})
            record.update(point_count=len(data.rows), excluded_point_count=0, raw_sha256=data.document["sources"][0]["sha256"],
                source_annotation_count=len(data.document["sources"][0]["annotations"]), input_sha256=data.sha256)
            baseline = fit_photometry(data, initial=catalog[event], starts=12, max_nfev=1500)
            write_json(event_root / "baseline.json", baseline)
            sensitivity = {}
            for name, options in (("signed_blend", {"allow_negative_blend": True}), ("noise_scale_1p25", {"noise_scale": 1.25})):
                try:
                    value = fit_photometry(data, initial=catalog[event], starts=12, max_nfev=1500, **options)
                    write_json(event_root / (name + ".json"), value)
                    sensitivity[name] = {"status": value["status"], "parameters": value["parameters"],
                        "uncertainty": value["uncertainty"], "flags": value["flags"],
                        "chi_square_native_noise": value["diagnostics"]["chi_square_native_noise"],
                        "multistart_confirmed": value["numerical_convergence"]["multistart_confirmed"]}
                except Exception as error:
                    sensitivity[name] = {"status": "SENSITIVITY_FAILED", "error": str(error)}
                    write_json(event_root / (name + "_failure.json"), sensitivity[name])
            timescale = baseline["parameters"]["tE_days"]
            grid = np.unique(np.clip(np.geomspace(timescale / 4, timescale * 4, 17), .1, 10000))
            profile = profile_timescale(data, baseline, grid.tolist())
            interval = profile_crossings(profile, timescale, data, baseline)
            write_json(event_root / "timescale_profile.json", profile)
            write_json(event_root / "timescale_crossings.json", interval)
            residual_plot(data, baseline, derived / "residuals" / (event + ".png"), event)
            uncertainty = baseline["uncertainty"]["standard_errors"]["tE_days"]
            diagnostic = baseline["diagnostics"]
            flags = baseline["flags"]
            sensitivity_stable = all(value.get("multistart_confirmed") and abs(math.log(value["parameters"]["tE_days"] / timescale)) < .2 for value in sensitivity.values())
            conditions = {
                "adequate_baseline_chi_square": diagnostic["chi_square_tail_probability_assuming_correct_independent_noise"] >= .01,
                "multistart_confirmed": baseline["numerical_convergence"]["multistart_confirmed"],
                "locally_identified_timescale": uncertainty is not None and uncertainty > 0 and uncertainty / timescale < .3,
                "both_profile_crossings": interval["lower_days"] is not None and interval["upper_days"] is not None,
                "no_temporal_or_seasonal_flags": "TIME_CORRELATED_RESIDUALS" not in flags and "SEASONAL_RESIDUAL_SYSTEMATICS" not in flags,
                "PSPL_beats_linear_trend": diagnostic["linear_trend_model"]["delta_bic_trend_minus_pspl"] > 10,
                "no_active_bounds": not baseline["numerical_convergence"]["active_bounds"],
                "sensitivity_stable": sensitivity_stable,
                "long_duration_priority_context": item["stratum"] == "long_duration" or timescale >= 150}
            eligible = all(conditions.values())
            record.update(status=baseline["status"], fitted_t0=baseline["parameters"]["t0"], fitted_tE_days=timescale,
                sigma_tE_days=uncertainty, relative_sigma_tE=uncertainty / timescale if uncertainty is not None else None,
                profile_lower_days=interval["lower_days"], profile_upper_days=interval["upper_days"], profile_status=interval["status"],
                chi_square=diagnostic["chi_square_native_noise"], dof=diagnostic["dof"], reduced_chi_square=diagnostic["reduced_chi_square"],
                chi_square_tail_probability=diagnostic["chi_square_tail_probability_assuming_correct_independent_noise"],
                linear_trend_delta_bic=diagnostic["linear_trend_model"]["delta_bic_trend_minus_pspl"],
                source_fraction=baseline["parameters"]["instruments"]["OGLE-III"]["source_fraction"],
                flags=flags, identified_parameters=baseline["uncertainty"]["identified_parameters"],
                unavailable_quantities=list(baseline["unresolved_quantities"]), sensitivity_stable=sensitivity_stable,
                followup_eligible=eligible, followup_conditions=conditions,
                followup_rationale="; ".join(key for key, value in conditions.items() if not value) or "Passes all frozen photometric follow-up eligibility screens; mass unresolved")
            compact = {"catalog_metadata": item, "baseline": compact_fit(baseline), "sensitivity": sensitivity,
                       "timescale_profile": profile, "timescale_crossings": interval, "followup_conditions": conditions}
            write_json(derived / "diagnostics" / (event + ".json"), compact)
            if eligible:
                width = (interval["upper_days"] - interval["lower_days"]) / (2 * timescale)
                candidates.append((abs(math.log(diagnostic["reduced_chi_square"])), width, -timescale, event, record))
        except Exception as error:
            record.update(status="ANALYSIS_FAILED_OR_UNRESOLVED", error=str(error), followup_eligible=False,
                          followup_rationale="No usable complete baseline/profile solution established; preserved in the sample")
            write_json(event_root / "failure.json", {"error": str(error), "traceback": traceback.format_exc()})
            # Even failed cases receive a diagnostic image rather than silently
            # disappearing from the promised 100-event artifact inventory.
            fig, ax = plt.subplots(figsize=(8, 5)); ax.axis("off")
            ax.text(.05, .8, event + "\nANALYSIS FAILED OR UNRESOLVED\n" + str(error)[:400], transform=ax.transAxes, wrap=True)
            (derived / "residuals").mkdir(parents=True, exist_ok=True); fig.savefig(derived / "residuals" / (event + ".png"), dpi=110); plt.close(fig)
        rows.append(record)
        for path in event_root.glob("*.json"):
            private_manifest.append({"path": str(path.relative_to(output)).replace("\\", "/"), "sha256": digest(path), "bytes": path.stat().st_size})
        print(json.dumps({"completed": index, "of": 100, "event": event, "status": record["status"],
                          "tE_days": record.get("fitted_tE_days"), "eligible": record.get("followup_eligible")}), flush=True)
    candidates.sort(key=lambda row: row[:4])
    ranking = []
    for rank, item in enumerate(candidates[:5], 1):
        record = deepcopy(item[4]); record["followup_rank"] = rank
        record["followup_status"] = "PHOTOMETRIC_FOLLOWUP_TARGET"
        record["followup_scope"] = "Historical event: archival/modeling/high-resolution imaging feasibility; no current peak assumed"
        ranking.append(record)
    write_json(derived / "all_100_results.json", rows); write_csv(derived / "all_100_results.csv", rows)
    write_json(derived / "followup_ranking.json", ranking); write_csv(derived / "followup_ranking.csv", ranking)
    benchmark_directory = data_root / "raw/zenodo_6607578"
    benchmark_paths = {"OGLE": benchmark_directory / "OGLE-2011-BLG-0462.dat", "MOA": benchmark_directory / "MOA-2011-BLG-191.dat"}
    benchmark_results = []
    runs = [("joint_native", benchmark_paths, {}), ("OGLE_only", {"OGLE": benchmark_paths["OGLE"]}, {}),
            ("MOA_only", {"MOA": benchmark_paths["MOA"]}, {}),
            ("joint_equal_instrument_objective", benchmark_paths, {"equal_instrument_weight": True}),
            ("joint_signed_blend", benchmark_paths, {"allow_negative_blend": True})]
    for name, paths, options in runs:
        try:
            data = load_benchmark_photometry(paths, metadata={"role": "historical_known_system_benchmark",
                "event_aliases": ["OGLE-2011-BLG-0462", "MOA-2011-BLG-191"], "data_version": "Zenodo6607578 v1.0.0 (2022)"})
            result = fit_photometry(data, initial={"t0": 5760, "tE_days": 250, "u0": .05}, starts=12, max_nfev=1500, **options)
            target = output / "historical_benchmark" / (name + ".json"); write_json(target, result)
            residual_plot(data, result, derived / "historical_benchmark" / (name + ".png"), "2022 known system: " + name)
            benchmark_results.append({"run": name, "point_count": len(data.rows), "result": compact_fit(result)})
            print(json.dumps({"benchmark": name, "status": result["status"], "point_count": len(data.rows), "tE_days": result["parameters"]["tE_days"]}), flush=True)
        except Exception as error:
            benchmark_results.append({"run": name, "status": "BENCHMARK_UNRESOLVED", "error": str(error)})
            print(json.dumps({"benchmark": name, "status": "BENCHMARK_UNRESOLVED", "error": str(error)}), flush=True)
    hst = load_hst_astrometry({name: benchmark_directory / ("OB110462_HST_" + name + ".dat") for name in ("F606W", "F814W")})
    write_json(output / "historical_benchmark" / "HST_native_ingestion.json", hst)
    write_json(derived / "historical_benchmark" / "summary.json", {"runs": benchmark_results,
        "HST_rows": len(hst["rows"]), "HST_shared_visits": hst["unique_native_visits"], "HST_precision_gate": hst["precision_inference"],
        "mass_status": "MASS_UNRESOLVED", "published_DW_EW_comparison": "Photometry-only native/equal-instrument screens are not the2022 joint astrometry+photometry DW/EW likelihoods. No numerical mass-recovery comparison is made."})
    verify_protocol(data_root); integrity(data_root)
    summary = {"schema": "bhsm_real_data_pilot_summary/1", "completed_utc": datetime.now(timezone.utc).isoformat(),
        "protocol_sha256": digest(BASE / "protocol_v1.json"), "sample_sha256": reproduced["selected_ids_sha256"],
        "event_rows": len(rows), "native_point_count": sum(row.get("point_count", 0) for row in rows),
        "status_counts": dict(Counter(row["status"] for row in rows)),
        "source_annotation_count": sum(row.get("source_annotation_count", 0) for row in rows),
        "event_0337_preserved": any(row["event_id"] == "OGLE3-ULENS-0337" for row in rows),
        "profile_status_counts": dict(Counter(row.get("profile_status", "FAILED") for row in rows)),
        "followup_eligible_count": len(candidates), "recommended_followup_count": len(ranking),
        "mass_supported_black_hole_candidates": 0, "new_black_hole_interpretations": 0,
        "novelty_status": "UNRESOLVED_UNTIL_PRIMARY_ALIAS_COORDINATE_CHECKS; no novelty claimed",
        "private_output": str(output), "raw_bytes_changed": False, "kernel_sha256": kernel_hashes()}
    write_json(derived / "summary.json", summary)
    write_json(output / "private_fit_manifest.json", private_manifest)
    write_json(output / "run_completed.json", summary)
    tracked = [{"path": str(path.relative_to(BASE)).replace("\\", "/"), "sha256": digest(path), "bytes": path.stat().st_size}
               for path in sorted(derived.rglob("*")) if path.is_file()]
    write_json(BASE / "derived_v1_manifest.json", {"protocol_sha256": digest(BASE / "protocol_v1.json"), "files": tracked})
    print(json.dumps(summary), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("freeze", "run"))
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.action == "freeze":
        freeze(args.data_root)
    else:
        if args.output is None:
            parser.error("run requires a separate external --output directory")
        run(args.data_root, args.output)


if __name__ == "__main__":
    main()
