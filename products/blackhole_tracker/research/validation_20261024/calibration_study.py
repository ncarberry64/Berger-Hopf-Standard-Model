"""Prospective RC7 calibration machinery; importing this module runs no study.

The generators below use independently written point-lens equations. They do
not import the product's forward model. Native brightness is replaced only in
new, explicitly synthetic documents; authentic files remain immutable.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path

import numpy as np

SOLAR_GM = 1.3271244e20
LIGHT_SPEED = 299792458.0
PARSEC = 3.085677581491367e16
MAS_RADIAN = 180.0 / math.pi * 3_600_000.0
PARAMETERS = ("mass_msun", "center_x_mas", "center_y_mas", "motion_x_mas_yr", "motion_y_mas_yr")


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def rng_for(stream, block, replicate):
    seed = [20261024, 0x524337, int(stream), int(block), int(replicate)]
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(seed))), seed


def lens_scales(mass, geometry):
    length = SOLAR_GM * mass / LIGHT_SPEED**2 / PARSEC
    theta = math.sqrt(4 * length * geometry["D_ls_pc"] /
                      (geometry["D_l_pc"] * geometry["D_s_pc"])) * MAS_RADIAN
    delay = 4 * SOLAR_GM * mass / LIGHT_SPEED**3 * (1 + geometry["z_l"])
    return theta, delay


def image_pair(source, shear):
    """Continue the ordinary two images with an independent 2-D Newton solve.

    y=(I-Gamma)x-x/|x|²; the primary minimum and saddle must retain parity.
    This is a weak-shear primary-pair generator, not a general image finder.
    """
    source = np.asarray(source, dtype=float)
    u = float(np.linalg.norm(source))
    if not math.isfinite(u) or u <= 0:
        raise ValueError("noncritical finite source separation required")
    matrix = np.array([[shear[0], shear[1]], [shear[1], -shear[0]]], dtype=float)
    direction = source / u
    positive = (u + math.sqrt(u*u + 4)) / 2
    seeds = (positive * direction, -direction / positive)
    solutions = []
    for index, seed in enumerate(seeds):
        point = seed.copy()
        for _ in range(60):
            radius2 = float(point @ point)
            if radius2 <= 0:
                raise ValueError("zero image radius")
            residual = point - matrix @ point - point / radius2 - source
            jacobian = np.eye(2) - matrix - np.eye(2) / radius2 + 2*np.outer(point, point) / radius2**2
            if float(np.linalg.norm(residual, ord=np.inf)) <= 2e-13:
                break
            point -= np.linalg.solve(jacobian, residual)
        else:
            raise ValueError("independent image continuation unresolved")
        radius2 = float(point @ point)
        jacobian = np.eye(2) - matrix - np.eye(2) / radius2 + 2*np.outer(point, point) / radius2**2
        determinant = float(np.linalg.det(jacobian))
        if (index == 0 and determinant <= 0) or (index == 1 and determinant >= 0):
            raise ValueError("primary parity changed")
        fermat = .5*float((point-source) @ (point-source)) - .5*math.log(radius2) - .5*float(point @ matrix @ point)
        solutions.append((point, determinant, fermat))
    return solutions


def resolved_mean(raw, truth):
    theta, delay_scale = lens_scales(truth["mass_msun"], raw["geometry"])
    rows = []
    for epoch, source in zip(raw["epochs_yr"], truth["source_mas"]):
        center = np.asarray(truth["center_mas"]) + (epoch-raw["reference_epoch_yr"])*np.asarray(truth["proper_motion_mas_yr"])
        y = (np.asarray(source)-center) / theta
        plus, minus = image_pair(y, truth["shear"])
        image_plus, image_minus = center + theta*plus[0], center + theta*minus[0]
        ratio = math.log(abs(minus[1] / plus[1]))
        delay = delay_scale * (minus[2]-plus[2])
        if ratio <= 0 or delay <= 0:
            raise ValueError("primary flux/delay ordering changed")
        rows.append([*image_plus, *image_minus, ratio, delay])
    return np.asarray(rows)


def resolved_design(spec):
    geometry = {"D_l_pc": 1000., "D_s_pc": 8000., "D_ls_pc": 7000., "z_l": 0., "z_s": 0.}
    theta, delay = lens_scales(spec["mass_msun"], geometry)
    epochs = np.asarray([2025.55, 2025.69, 2025.88, 2026.03, 2026.21, 2026.39, 2026.58])
    if spec.get("repeated_epoch"):
        epochs[:] = 2026.
    reporting_epoch = spec.get("reporting_epoch_yr", 2026.)
    motion = theta*np.asarray(spec.get("motion_over_theta_per_year", [.4, -.2]))
    center_anchor = np.array([12.3, -4.2])
    center_reporting = center_anchor + (reporting_epoch-2026.)*motion
    physical_centers = center_anchor + (epochs-2026.)[:, None]*motion
    phase = np.arange(len(epochs))
    offsets = np.column_stack([.65+.12*np.sin(phase), .55+.07*np.cos(.7*phase)])
    truth = {"mass_msun": spec["mass_msun"], "center_mas": center_reporting.tolist(),
             "proper_motion_mas_yr": motion.tolist(),
             "source_mas": (physical_centers+theta*offsets).tolist(),
             "shear": spec.get("shear", [0., 0.]), "compact_quad": [0., 0.], "convergence": 0.}
    raw = {"schema_version": 1, "geometry": geometry, "reference_epoch_yr": reporting_epoch,
           "epochs_yr": epochs.tolist(), "analysis": {"reference_mass_msun": spec.get("reference_mass_msun", 7.),
           "r0_pc": spec.get("r0_pc", 1e-8), "flux_ratio": 0., "source_policy": "free_per_epoch"},
           "provenance": {"kind": "synthetic", "description": "Independent analytic RC7 calibration; supplied hypothetical errors and distances, not an instrument forecast or observation."}}
    sigma = np.asarray([theta*.003]*4 + [.01, .005*delay])
    within = np.eye(6)
    within[0, 2] = within[2, 0] = .25
    within[1, 3] = within[3, 1] = .25
    within[4, 5] = within[5, 4] = .2
    epoch_correlation = .2**np.abs(phase[:, None]-phase[None, :])
    covariance = np.kron(epoch_correlation, sigma[:, None]*within*sigma[None, :])
    raw["observations"] = resolved_mean(raw, truth).tolist()
    raw["covariance"] = covariance.tolist()
    return raw, truth


def resolved_draw(spec, block, replicate):
    raw, truth = resolved_design(spec)
    rng, seed = rng_for(1, block, replicate)
    state_before = deepcopy(rng.bit_generator.state)
    noise = np.linalg.cholesky(raw["covariance"]) @ rng.standard_normal(6*len(raw["epochs_yr"]))
    raw["observations"] = (np.asarray(raw["observations"]) + noise.reshape(-1, 6)).tolist()
    case_id = hashlib.sha256(canonical(seed)).hexdigest()[:24]
    raw["provenance"]["synthetic_case_id"] = case_id
    return raw, truth, {"case_id": case_id, "seed": seed, "rng_before": state_before,
                        "rng_after": rng.bit_generator.state, "noise_sha256": hashlib.sha256(noise.tobytes()).hexdigest()}


def pspl_flux(times, t0, te, u0):
    u2 = u0*u0 + ((np.asarray(times)-t0)/te)**2
    return (u2+2) / np.sqrt(u2*(u2+4))


def photometry_mean(times, truth, family):
    t0, te, u0 = truth["t0"], truth["tE_days"], truth["u0"]
    a = pspl_flux(times, t0, te, u0)
    if family == "constant":
        return np.full(len(times), truth["baseline_magnitude"])
    if family == "periodic_variable":
        return truth["baseline_magnitude"] - .1*np.cos(2*np.pi*(times-t0)/100.)
    if family == "binary_source":
        second = pspl_flux(times, t0+1.2*te, te, .5)
        return truth["baseline_magnitude"] - 2.5*np.log10(1+truth["source_fraction"]*(.7*a+.3*second-1))
    if family not in ("pspl", "correlated_pspl"):
        raise ValueError("unknown synthetic photometric family")
    return truth["baseline_magnitude"] - 2.5*np.log10(1+truth["source_fraction"]*(a-1))


def photometry_draw(parent, truth, family, block, replicate):
    # Import schema only. The generating magnification above is independent of
    # product photometry/forward functions.
    from bhtracker.observations import UnresolvedPhotometry
    data = UnresolvedPhotometry(parent)
    rng, seed = rng_for(2, block, replicate)
    before = deepcopy(rng.bit_generator.state)
    times, sigma = data.times, data.errors
    innovations = rng.standard_normal((2, len(times)))
    noise = innovations[0].copy()
    if family == "correlated_pspl":
        order = np.argsort(times, kind="stable")
        latent = np.empty(len(times))
        h = innovations[1, order[0]]
        latent[order[0]] = h
        for last, current in zip(order[:-1], order[1:]):
            rho = math.exp(-(times[current]-times[last])/30.)
            h = rho*h + math.sqrt(max(0., 1-rho*rho))*innovations[1, current]
            latent[current] = h
        noise = math.sqrt(.5)*noise + math.sqrt(.5)*latent
    observed = photometry_mean(times, truth, family) + sigma*noise
    case_id = hashlib.sha256(canonical(seed)).hexdigest()[:24]
    document = deepcopy(parent)
    document["metadata"] = {"synthetic": True, "case_id": case_id,
                             "cadence_parent_sha256": data.sha256,
                             "scope": "Generated magnitudes; original time/error sampling only. No empirical lens classification."}
    document["transformations"].append({"operation": "SYNTHETIC_MAGNITUDE_REPLACEMENT", "cadence_parent_sha256": data.sha256,
                                        "all_rows_replaced": True, "native_files_modified": False,
                                        "parent_native_fields": "Retained in the separately hash-pinned parent, omitted from fit input to avoid native-brightness leakage."})
    for row, value in zip(document["rows"], observed):
        original_id = row["source_row_id"]
        row["cadence_parent_source_row_id"] = original_id
        for key in ("source_file", "source_sha256", "source_line"):
            if key in row:
                row["cadence_parent_"+key] = row.pop(key)
        row["source_row_id"] = f"SYNTHETIC:{case_id}:{original_id}"
        row["magnitude"] = float(value)
        row.pop("native_fields", None)
        row["quality_flags"] = [*row.get("quality_flags", []), "SYNTHETIC_MAGNITUDE"]
    return document, deepcopy(truth), {"case_id": case_id, "seed": seed, "rng_before": before,
        "rng_after": rng.bit_generator.state, "noise_sha256": hashlib.sha256((sigma*noise).tobytes()).hexdigest(),
        "parent_sha256": data.sha256, "parent_row_count": len(data.rows)}


def parameter_vector(parameters):
    return np.asarray([parameters["mass_msun"], *parameters["center_mas"], *parameters["proper_motion_mas_yr"]])


def resolved_score(result, truth):
    from scipy.stats import norm
    estimates, target = parameter_vector(result["estimates"]), parameter_vector(truth)
    errors = [result["uncertainty"]["mass_msun"], *result["uncertainty"]["center_mas"], *result["uncertainty"]["proper_motion_mas_yr"]]
    solved = bool(result["optimizer_converged"] and result["physics_admission"]["allowed_physics_models"]["baseline_point_mass"])
    z = float(norm.ppf(.975))
    intervals, cover, available = [], [], []
    for index, (estimate, error, value) in enumerate(zip(estimates, errors, target)):
        valid = bool(solved and error is not None and math.isfinite(error) and error > 0)
        limits = None
        if valid:
            if index == 0:
                exponent = z*error/estimate
                if exponent < 700:
                    limits = [float(estimate*math.exp(-exponent)), float(estimate*math.exp(exponent))]
            else:
                limits = [float(estimate-z*error), float(estimate+z*error)]
        available.append(limits is not None)
        cover.append(bool(limits is not None and limits[0] <= value <= limits[1]))
        intervals.append(limits)
    mass_low = intervals[0][0] if intervals[0] is not None else None
    return {"parameter_order": PARAMETERS, "intervals95": intervals, "interval_available": available,
            "covered_before_goodness_selection": cover,
            "usable_and_covered": [value and result["status"] != "FIT_REJECTED" for value in cover],
            "bias": (estimates-target).tolist(), "status": result["status"],
            "goodness_p": result["goodness_of_fit_p"], "mass_comparator_3msun_lower_crossed": bool(mass_low is not None and mass_low > 3 and result["status"] != "FIT_REJECTED"),
            "comparator_qualification": "Synthetic optical mass comparator only, not a universal neutron-star boundary or a BH classifier.",
            "motion_snr_ge5": bool(result["motion_snr"] is not None and result["motion_snr"] >= 5 and result["status"] == "TRACKED"),
            "motion_covariance_available": result["proper_motion_covariance"] is not None,
            "blackhole_classifier_implemented": False, "blackhole_false_positive_rate": None}


def photometry_score(result, truth, family, profile_row=None):
    from scipy.stats import norm, chi2
    names = ["t0", "tE_days", "u0"]
    z = float(norm.ppf(.975))
    solved = bool(result["numerical_convergence"]["optimizer_success"] and result["numerical_convergence"]["multistart_confirmed"])
    intervals, cover, available = [], [], []
    for name in names:
        estimate, error = result["parameters"][name], result["uncertainty"]["standard_errors"][name]
        valid = bool(family == "pspl" and solved and error is not None and math.isfinite(error) and error > 0)
        limits = [estimate-z*error, estimate+z*error] if valid else None
        intervals.append(limits)
        available.append(valid)
        cover.append(bool(valid and limits[0] <= truth[name] <= limits[1]))
    profile_resolved = bool(profile_row is not None and profile_row.get("status") == "ADMITTED_INTERIOR_OPTIMUM" and
                            profile_row.get("delta_chi_square") is not None)
    physical = result["unresolved_quantities"]
    return {"parameter_order": names, "intervals95": intervals, "interval_available": available,
            "bias": [float(result["parameters"][name]-truth[name]) for name in names] if family == "pspl" else None,
            "covered_before_goodness_selection": cover,
            "usable_and_covered": [value and result["status"] == "PHOTOMETRIC_FIT" for value in cover],
            "status": result["status"], "flags": result["flags"],
            "screen_nonrejection": result["status"] == "PHOTOMETRIC_FIT",
            "profile_truth_point": profile_row,
            "profile_truth_membership_resolved": profile_resolved,
            "profile_truth_member95": bool(profile_resolved and profile_row["delta_chi_square"] <= chi2.ppf(.95, 1)),
            "profile_qualification": "Membership of generating timescale in an interior likelihood-reference set, not endpoints or a calibrated physical mass interval. Boundary/unresolved ordinates do not supply membership.",
            "unresolved_mass_and_distance": physical["mass_msun"] is None and physical["lens_distance_pc"] is None,
            "blackhole_classifier_implemented": False, "blackhole_false_positive_rate": None}


def binomial_summary(covered, attempted, planned):
    from scipy.stats import binomtest
    if not 0 <= covered <= attempted <= planned or planned <= 0:
        raise ValueError("invalid planned/attempted/outcome counts")
    interval = binomtest(covered, planned).proportion_ci(.95, method="exact")
    return {"count": covered, "planned": planned, "attempted": attempted,
            "fraction_of_planned": covered/planned,
            "exact95_binomial_interval_complete_campaign_only": [float(interval.low), float(interval.high)] if attempted == planned else None,
            "completion_bounds": [covered/planned, (covered+planned-attempted)/planned],
            "one_sided95_upper_if_zero_and_complete": float(1-.05**(1/planned)) if covered == 0 and attempted == planned else None}
