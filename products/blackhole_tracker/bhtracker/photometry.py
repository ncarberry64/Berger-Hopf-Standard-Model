"""Native-magnitude point-source/point-lens likelihood for unresolved events.

The PSPL formula follows the image-summed point-lens Jacobian, e.g. Paczynski
(1986), ApJ 304, 1, DOI 10.1086/164140. Flux addition is exact; no approximate
Gaussian flux errors are manufactured from the published magnitude errors.
"""
from copy import deepcopy
import hashlib
import json
import math

import numpy as np
from scipy.optimize import least_squares
from scipy.stats import chi2

from .observations import UnresolvedPhotometry

RESULT_SCHEMA = "bhsm_unresolved_photometry_result/1"
FIT_PROTOCOL = {
    "id": "BHSM-native-magnitude-PSPL-20261022-v1",
    "model": "rectilinear point-source point-lens; per-instrument baseline magnitude and source fraction",
    "likelihood": "independent Gaussian in native apparent magnitude, published sigma unchanged",
    "time": "native HJD relative-day arithmetic; clock unspecified unless independently documented",
    "bounds": {"t0": "min(time)-span .. max(time)+span", "tE_days": [0.1, 10000.0],
               "u0": [0.0001, 10.0], "source_fraction": [0.000001, 1.0],
               "signed_blend_sensitivity_source_fraction": [0.000001, 10.0],
               "baseline_magnitude": "per-instrument median - 10 .. median + 10"},
    "starts": 12, "max_nfev": 1500, "seed": 20261022,
    "optimizer": "scipy least_squares trf, analytic Jacobian, linear loss, x_scale=jac",
    "tolerances": {"ftol": 1e-10, "xtol": 1e-10, "gtol": 1e-8},
    "rank_relative_cutoff": 1e-7,
    "exclusions": "none: all finite native positive-error rows retained; exact documented source annotation is provenance, not a measurement",
    "coverage": "local quadratic errors conditional on diagonal magnitude noise; no automatic coverage claim at boundaries or model failure",
    "mass_identification": "unavailable: tE alone supplies neither thetaE nor piE",
}
FIT_PROTOCOL_SHA256 = hashlib.sha256(json.dumps(FIT_PROTOCOL, sort_keys=True,
    separators=(",", ":"), allow_nan=False).encode("utf8")).hexdigest()
MAG_FACTOR = 2.5 / math.log(10)


def pspl_magnification(u):
    u = np.asarray(u, dtype=float)
    if np.any(~np.isfinite(u)) or np.any(u <= 0):
        raise ValueError("PSPL separation u must be positive and finite")
    return (u * u + 2) / (u * np.sqrt(u * u + 4))


def _dataset(dataset):
    return dataset if isinstance(dataset, UnresolvedPhotometry) else UnresolvedPhotometry.from_dict(dataset)


def predict_photometry(dataset, parameters):
    """Return apparent magnitudes in original source-row order.

    t0 is in days relative to dataset.common_origin_jd, not an inferred clock.
    Each instrument has baseline_magnitude and source_fraction f=Fs/(Fs+Fb).
    f>1 is accepted only for the explicitly labelled signed-blend sensitivity.
    """
    dataset = _dataset(dataset)
    t0, te, u0 = [float(parameters[k]) for k in ("t0", "tE_days", "u0")]
    if not all(np.isfinite([t0, te, u0])) or te <= 0 or u0 <= 0:
        raise ValueError("finite t0 and positive finite tE/u0 required")
    u = np.hypot(u0, (dataset.times - t0) / te)
    a = pspl_magnification(u)
    prediction = np.empty(len(u))
    indices = dataset.instrument_indices
    for index, name in enumerate(dataset.instruments):
        p = parameters["instruments"][name]
        fraction, baseline = float(p["source_fraction"]), float(p["baseline_magnitude"])
        if not np.isfinite(baseline) or not np.isfinite(fraction) or fraction <= 0:
            raise ValueError("finite baseline magnitude and positive finite source fraction required")
        if fraction > 1 and not parameters.get("allow_negative_blend", False):
            raise ValueError("negative blend requires explicit calibration-offset sensitivity mode")
        select = indices == index
        prediction[select] = baseline - MAG_FACTOR * np.log1p(fraction * (a[select] - 1))
    return prediction


class _Model:
    def __init__(self, data, noise_scale, equal_instrument_weight, allow_negative_blend):
        self.data = data
        self.t, self.y, self.sigma = data.times, data.magnitudes, data.errors
        self.names, self.index = data.instruments, data.instrument_indices
        self.center = float(np.median(self.t))
        self.span = max(float(np.ptp(self.t)), 1.0)
        self.scale = max(self.span / 4, 1.0)
        self.noise_scale = float(noise_scale)
        if not math.isfinite(self.noise_scale) or self.noise_scale <= 0:
            raise ValueError("noise_scale must be positive and finite")
        self.weights = np.ones(len(self.t)) / (self.sigma * self.noise_scale)
        if equal_instrument_weight:
            # Equal total sum-of-squared residual weight per instrument. This is
            # a declared sensitivity objective, not the published Gaussian PDF.
            counts = np.bincount(self.index)
            self.weights *= np.sqrt(len(self.t) / (len(self.names) * counts[self.index]))
        self.equal_weight = bool(equal_instrument_weight)
        self.allow_negative_blend = bool(allow_negative_blend)
        lower = [(float(np.min(self.t)) - self.span - self.center) / self.scale,
                 math.log(.1), math.log(.0001)]
        upper = [(float(np.max(self.t)) + self.span - self.center) / self.scale,
                 math.log(10000), math.log(10)]
        for k in range(len(self.names)):
            median = float(np.median(self.y[self.index == k]))
            lower.extend([median - 10, .000001])
            upper.extend([median + 10, 10.0 if allow_negative_blend else 1.0])
        self.lower, self.upper = np.asarray(lower), np.asarray(upper)
        self.parameter_names = ["t0", "tE_days", "u0"]
        for name in self.names:
            self.parameter_names.extend([f"{name}.baseline_magnitude", f"{name}.source_fraction"])

    def evaluate(self, x, jac=False):
        t0 = self.center + self.scale * x[0]
        te, u0 = math.exp(x[1]), math.exp(x[2])
        q = (self.t - t0) / te
        u = np.hypot(u0, q)
        a = (u * u + 2) / (u * np.sqrt(u * u + 4))
        base = x[3 + 2 * self.index]
        f = x[4 + 2 * self.index]
        b = 1 + f * (a - 1)
        model = base - MAG_FACTOR * np.log(b)
        if not jac:
            return (model - self.y) * self.weights
        derivative_a = -8 / (u * u * (u * u + 4) ** 1.5)
        derivative_u = -MAG_FACTOR * f / b * derivative_a
        j = np.zeros((len(self.t), len(x)))
        j[:, 0] = derivative_u * (-q * self.scale / (u * te))
        j[:, 1] = derivative_u * (-q * q / u)
        j[:, 2] = derivative_u * (u0 * u0 / u)
        row = np.arange(len(self.t))
        j[row, 3 + 2 * self.index] = 1
        j[row, 4 + 2 * self.index] = -MAG_FACTOR * (a - 1) / b
        return j * self.weights[:, None]

    def encode(self, physical):
        values = [(float(physical["t0"]) - self.center) / self.scale,
                  math.log(float(physical["tE_days"])), math.log(float(physical["u0"]))]
        for name in self.names:
            p = physical.get("instruments", {}).get(name, {})
            values.extend([float(p.get("baseline_magnitude", np.median(self.y[self.index == self.names.index(name)]))),
                           float(p.get("source_fraction", .5))])
        return np.clip(values, self.lower + 1e-9, self.upper - 1e-9)

    def decode(self, x):
        return {"t0": float(self.center + self.scale * x[0]), "tE_days": math.exp(x[1]), "u0": math.exp(x[2]),
                "time_numeric_origin_jd": self.data.common_origin_jd,
                "allow_negative_blend": self.allow_negative_blend,
                "instruments": {name: {"baseline_magnitude": float(x[3 + 2 * k]),
                    "source_fraction": float(x[4 + 2 * k]),
                    "flux_zero_point": "arbitrary common per-instrument reference magnitude 0",
                    "source_flux_relative": float(10 ** (-.4 * x[3 + 2 * k]) * x[4 + 2 * k]),
                    "blend_flux_relative": float(10 ** (-.4 * x[3 + 2 * k]) * (1 - x[4 + 2 * k]))}
                    for k, name in enumerate(self.names)}}

    def seeds(self, initial, starts):
        # Deterministic broad searches include short/long timescale and blending
        # modes. Catalog values only initialize; they never add likelihood terms.
        peak = int(np.argmin(self.y))
        t0 = float(self.t[peak])
        base = {"t0": t0, "tE_days": min(max(self.span / 12, 10), 500), "u0": .3}
        if initial:
            source = initial.get("parameters", initial)
            for key, catalog_key in (("t0", "published_t0_hjd_minus_2450000"),
                                     ("tE_days", "published_tE_days"), ("u0", "published_u0")):
                if key in source:
                    base[key] = source[key]
                elif catalog_key in source:
                    base[key] = source[catalog_key]
            if "instruments" in source:
                base["instruments"] = source["instruments"]
            elif "published_source_flux_fraction" in source:
                base["instruments"] = {name: {"source_fraction": source["published_source_flux_fraction"],
                    "baseline_magnitude": source.get("published_baseline_I_magnitude", float(np.median(self.y[self.index == k])))}
                    for k, name in enumerate(self.names)}
        first = self.encode(base)
        yield first
        factors = [(.5, .15, .95), (2, .6, .3), (1, .05, .05), (4, .1, .15),
                   (.25, 1, .95), (1, 1.5, .95), (2, .03, .02), (.5, .6, .5),
                   (4, .4, .5), (.25, .1, .1), (1, .3, .5)]
        rng = np.random.default_rng(FIT_PROTOCOL["seed"])
        for k in range(max(0, starts - 1)):
            factor, impact, fraction = factors[k % len(factors)]
            x = first.copy()
            x[1] += math.log(factor)
            x[2] = math.log(impact)
            x[4::2] = fraction
            if k >= len(factors):
                x[0] += rng.normal(0, .2)
                x[1] += rng.normal(0, .5)
            yield np.clip(x, self.lower + 1e-9, self.upper - 1e-9)


def _nullable(value):
    if isinstance(value, dict):
        return {k: _nullable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, np.ndarray)):
        return [_nullable(v) for v in value]
    if isinstance(value, (np.floating, float)):
        return float(value) if math.isfinite(value) else None
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.bool_):
        return bool(value)
    return value


def _uncertainty(model, optimum):
    j = model.evaluate(optimum.x, jac=True)
    norms = np.linalg.norm(j, axis=0)
    scales = np.where(norms > 0, norms, 1)
    normalized = j / scales
    _, singular, vt = np.linalg.svd(normalized, full_matrices=False)
    cutoff = FIT_PROTOCOL["rank_relative_cutoff"] * (singular[0] if len(singular) else 1)
    rank = int(np.sum(singular > cutoff))
    null = vt[rank:] / scales[None, :]
    null_norm = np.linalg.norm(null, axis=1)
    null = null / np.where(null_norm[:, None] > 0, null_norm[:, None], 1)
    transform = np.ones(len(optimum.x))
    transform[:3] = [model.scale, math.exp(optimum.x[1]), math.exp(optimum.x[2])]
    covariance = ((vt[:rank].T / singular[:rank] ** 2) @ vt[:rank]) / scales[:, None] / scales[None, :]
    covariance = covariance * transform[:, None] * transform[None, :]
    # Null masking uses dimensionless normalized-Jacobian coordinates. Physical
    # null directions are separately transformed, never exported as zero error.
    null_projector = vt[rank:].T @ vt[rank:]
    identified = np.diag(null_projector) < 1e-6
    physical_null = null * transform[None, :]
    errors = {name: float(math.sqrt(max(covariance[k, k], 0))) if identified[k] else None
              for k, name in enumerate(model.parameter_names)}
    public = [[float(covariance[k, m]) if identified[k] and identified[m] else None
               for m in range(len(transform))] for k in range(len(transform))]
    return {"parameter_order": model.parameter_names, "standard_errors": errors, "covariance": public,
        "rank": rank, "parameter_count": len(transform), "identified_parameters": [n for n, ok in zip(model.parameter_names, identified) if ok],
        "unidentified_parameters": [n for n, ok in zip(model.parameter_names, identified) if not ok],
        "normalized_jacobian_singular_values": singular.tolist(),
        "normalized_coordinate_null_projector": null_projector.tolist(),
        "physical_null_directions": physical_null.tolist(),
        "covariance_contract": "Null-affected public entries are unavailable. Local inverse-information errors use assumed native diagonal magnitude noise, without rescaling by reduced chi-square.",
        "qualification": "Local quadratic approximation; bound-active, multimodal, rank-deficient or inadequate fits require profiles/sensitivity and do not establish frequentist coverage."}


def _runs(residual):
    signs = residual >= 0
    positive, negative = int(np.sum(signs)), int(np.sum(~signs))
    if positive == 0 or negative == 0 or len(signs) < 3:
        return {"runs": 1, "z": None}
    count = 1 + int(np.sum(signs[1:] != signs[:-1]))
    n = positive + negative
    mean = 1 + 2 * positive * negative / n
    variance = 2 * positive * negative * (2 * positive * negative - n) / (n * n * (n - 1))
    return {"runs": count, "z": (count - mean) / math.sqrt(variance) if variance > 0 else None}


def _diagnostics(model, prediction, nparams):
    residual = (model.y - prediction) / (model.sigma * model.noise_scale)
    per_instrument = {}
    constant_chi2 = trend_chi2 = 0.0
    for k, name in enumerate(model.names):
        mask = model.index == k
        order = np.argsort(model.t[mask], kind="stable")
        r, t = residual[mask][order], model.t[mask][order]
        weight = 1 / (model.sigma[mask] * model.noise_scale)
        y = model.y[mask]
        mean = float(np.average(y, weights=weight ** 2))
        cchi = float(np.sum(((y - mean) * weight) ** 2)); constant_chi2 += cchi
        design = np.column_stack([np.ones(len(y)), (model.t[mask] - model.center) / model.scale])
        coefficient = np.linalg.lstsq(design * weight[:, None], y * weight, rcond=None)[0]
        trchi = float(np.sum(((y - design @ coefficient) * weight) ** 2)); trend_chi2 += trchi
        corr = float(np.corrcoef(r[:-1], r[1:])[0, 1]) if len(r) > 3 and np.std(r) > 0 else None
        season = np.cumsum(np.r_[0, np.diff(t) > 100])
        season_data = []
        for sid in np.unique(season):
            sr = r[season == sid]
            season_data.append({"start": float(t[season == sid][0]), "end": float(t[season == sid][-1]),
                "count": len(sr), "mean_standardized_residual": float(np.mean(sr)),
                "mean_over_independent_standard_error": float(np.sum(sr) / math.sqrt(len(sr)))})
        per_instrument[name] = {"count": len(r), "chi_square_native_noise": float(r @ r),
            "rms_standardized_residual": float(np.sqrt(np.mean(r * r))), "median_standardized_residual": float(np.median(r)),
            "absolute_residual_above_3sigma_count": int(np.sum(np.abs(r) > 3)),
            "lag1_correlation_sorted_native_time": corr, "runs_test": _runs(r),
            "seasonal_residuals": season_data, "constant_chi_square": cchi, "linear_trend_chi_square": trchi}
    chi = float(residual @ residual); dof = len(residual) - nparams
    k = len(model.names)
    return {"chi_square_native_noise": chi, "dof": dof, "reduced_chi_square": chi / dof if dof > 0 else None,
        "chi_square_tail_probability_assuming_correct_independent_noise": float(chi2.sf(chi, dof)) if dof > 0 else None,
        "per_instrument": per_instrument,
        "constant_model": {"chi_square": constant_chi2, "parameter_count": k,
                           "delta_bic_constant_minus_pspl": constant_chi2 - chi + (k - nparams) * math.log(len(residual))},
        "linear_trend_model": {"chi_square": trend_chi2, "parameter_count": 2 * k,
                               "delta_bic_trend_minus_pspl": trend_chi2 - chi + (2 * k - nparams) * math.log(len(residual))},
        "qualification": "Residual and chi-square diagnostics depend on diagonal-noise assumptions. Runs/season tests and BIC screens are uncalibrated multiplicity-sensitive diagnostics, not black-hole probabilities."}


def fit_photometry(dataset, *, initial=None, starts=12, max_nfev=1500, noise_scale=1.0,
                   equal_instrument_weight=False, allow_negative_blend=False):
    """Fit all native rows; return a standards-compliant versioned JSON result.

    No clipping, thinning, averaging, sigma inflation or catalog-data term is
    implicit. A signed blend is an explicit calibration-offset sensitivity,
    never a physically negative stellar luminosity or a dark-lens detection.
    """
    dataset = _dataset(dataset)
    if isinstance(starts, bool) or isinstance(max_nfev, bool) or not isinstance(starts, int) or starts < 1 or not isinstance(max_nfev, int) or max_nfev < 1:
        raise ValueError("starts and max_nfev must be positive integers")
    model = _Model(dataset, noise_scale, equal_instrument_weight, allow_negative_blend)
    if len(dataset.rows) <= len(model.lower):
        raise ValueError(f"need more than {len(model.lower)} native rows to fit this {len(model.names)}-instrument PSPL model")
    reports, solutions = [], []
    for index, seed in enumerate(model.seeds(initial, starts)):
        try:
            optimum = least_squares(model.evaluate, seed, jac=lambda x: model.evaluate(x, jac=True),
                bounds=(model.lower, model.upper), method="trf", loss="linear", x_scale="jac",
                max_nfev=max_nfev, **FIT_PROTOCOL["tolerances"])
            objective = float(optimum.fun @ optimum.fun)
            reports.append({"start": index, "success": bool(optimum.success), "status": int(optimum.status),
                "objective_chi_square": objective, "nfev": int(optimum.nfev), "optimality": float(optimum.optimality),
                "message": str(optimum.message), "parameters": model.decode(optimum.x)})
            if np.isfinite(objective):
                solutions.append((objective, optimum))
        except (ValueError, FloatingPointError, OverflowError, np.linalg.LinAlgError) as error:
            reports.append({"start": index, "success": False, "message": str(error), "objective_chi_square": None})
    if not solutions:
        raise ValueError("all PSPL starts failed; inspect data/calibration and bounds")
    solutions.sort(key=lambda item: item[0])
    objective, optimum = solutions[0]
    parameters = model.decode(optimum.x)
    prediction = predict_photometry(dataset, parameters)
    uncertainty = _uncertainty(model, optimum)
    diagnostics = _diagnostics(model, prediction, len(optimum.x))
    bound_distance = np.minimum(optimum.x - model.lower, model.upper - optimum.x)
    active = [model.parameter_names[k] for k, value in enumerate(bound_distance)
              if value <= 1e-5 * max(1, model.upper[k] - model.lower[k])]
    flags = []
    if not optimum.success:
        flags.append("NUMERICAL_CONVERGENCE_UNRESOLVED")
    if active:
        flags.append("BOUND_ACTIVE_LOCAL_COVARIANCE_NONREGULAR")
    if uncertainty["rank"] < uncertainty["parameter_count"]:
        flags.append("PARTIALLY_IDENTIFIED_TRAJECTORY")
    if diagnostics["chi_square_tail_probability_assuming_correct_independent_noise"] < .01:
        flags.append("PSPL_OR_DIAGONAL_NOISE_INADEQUATE")
    if any(abs(v["runs_test"]["z"] or 0) > 3 for v in diagnostics["per_instrument"].values()):
        flags.append("TIME_CORRELATED_RESIDUALS")
    if any(abs(s["mean_over_independent_standard_error"]) > 4 for v in diagnostics["per_instrument"].values() for s in v["seasonal_residuals"] if s["count"] >= 10):
        flags.append("SEASONAL_RESIDUAL_SYSTEMATICS")
    if equal_instrument_weight:
        flags.append("EQUAL_INSTRUMENT_OBJECTIVE_SENSITIVITY")
    if allow_negative_blend:
        flags.append("SIGNED_BLEND_CALIBRATION_SENSITIVITY")
    close = [item for item in reports if item.get("success") and item["objective_chi_square"] <= objective + 1]
    well_solved = bool(optimum.success and len(close) >= min(starts, 2))
    if not well_solved:
        flags.append("MULTISTART_CONFIRMATION_UNRESOLVED")
    # A physically admissible photometric curve supplies no angular Einstein
    # radius or microlens parallax. No mass/boundary radius is manufactured.
    from .interpretation import bhsm_interpretation
    interpretation = bhsm_interpretation("ordinary", fit_status="INSUFFICIENT_INFORMATION")
    interpretation["observation_route"] = "unresolved_native_magnitude_pspl_v1"
    interpretation["observational_identification"] = {
        "mass_status": "MASS_UNRESOLVED", "mass_msun": None, "lens_distance_pc": None,
        "theta_E_mas": None, "microlens_parallax": None, "absolute_proper_motion_mas_yr": None,
        "horizon_status": "NOT_INFERRED",
        "reason": "tE=thetaE/mu_rel; thetaE^2=kappa*M*pi_rel. A photometric timescale alone identifies neither mass, distance nor angular proper motion."}
    interpretation["parameter_meanings"] = [
        {"parameter": "t0 / tE_days / u0", "interpretation": "Relative-time trajectory of the single unresolved compact-configuration optical response.",
         "qualification": "These parameters constrain a conditional lensing imprint, interpreted as BHSM surface topography. A fitted or nonrejected light curve alone does not validate its gravitational origin. Physical interface shape, distinct deformation dynamics, core, mass and horizon remain unidentified."},
        {"parameter": "instrument baseline/source fraction", "interpretation": "Photometric calibration and unresolved luminous blending nuisance parameters.",
         "qualification": "Brightness is the image-summed flux; it is not the ratio of resolved images."}]
    status = "PHOTOMETRIC_FIT" if well_solved else "PHOTOMETRIC_FIT_UNRESOLVED"
    if "PSPL_OR_DIAGONAL_NOISE_INADEQUATE" in flags:
        status = "PHOTOMETRIC_MODEL_INADEQUATE"
    protocol = deepcopy(FIT_PROTOCOL)
    actual = {"starts": starts, "max_nfev": max_nfev, "noise_scale": float(noise_scale),
              "equal_instrument_weight": bool(equal_instrument_weight), "allow_negative_blend": bool(allow_negative_blend)}
    result = {"schema": RESULT_SCHEMA, "observation_schema": dataset.document["schema"], "input_sha256": dataset.sha256,
        "protocol": protocol, "protocol_sha256": FIT_PROTOCOL_SHA256, "run_options": actual,
        "status": status, "mass_status": "MASS_UNRESOLVED", "model": "PSPL_RECTILINEAR_NATIVE_MAGNITUDE",
        "parameters": parameters, "uncertainty": uncertainty,
        "timescale_uncertainty": {"sigma_days": uncertainty["standard_errors"]["tE_days"],
            "status": "LOCAL_QUADRATIC_ONLY_NONREGULAR" if active else "LOCAL_QUADRATIC_ONLY",
            "coverage_claim": False, "profile_interval_days": None},
        "numerical_convergence": {"optimizer_success": bool(optimum.success), "multistart_confirmed": well_solved,
                                  "objective_chi_square": objective, "starts": reports, "active_bounds": active},
        "physical_admission": {"status": "ADMITTED_PHOTOMETRIC_MODEL", "positive_source_flux": True,
            "nonnegative_stellar_blend": not allow_negative_blend,
            "qualification": "Admission concerns positive predicted total flux and the declared blending model; angular weak-field, lens distance, horizon and BHSM core conditions are not identified by these data."},
        "observational_adequacy": {"status": "INADEQUATE_OR_NOISE_MISSPECIFIED" if "PSPL_OR_DIAGONAL_NOISE_INADEQUATE" in flags else "NOT_REJECTED_BY_DIAGONAL_CHI_SQUARE_SCREEN",
            "flags": flags, "diagnostics": diagnostics}, "diagnostics": diagnostics, "flags": flags,
        "point_count": len(dataset.rows), "excluded_point_count": 0,
        "predictions_magnitude": prediction.tolist(), "residuals_magnitude": (model.y - prediction).tolist(),
        "standardized_residuals": ((model.y - prediction) / (model.sigma * model.noise_scale)).tolist(),
        "row_ids": [r["source_row_id"] for r in dataset.rows],
        "unresolved_quantities": {"mass_msun": None, "lens_distance_pc": None, "source_distance_pc": None,
            "theta_E_mas": None, "pi_E": None, "absolute_proper_motion_mas_yr": None,
            "resolved_image_positions": None, "image_flux_ratio": None, "interimage_delay_days": None,
            "horizon_status": None, "core_state": None, "boundary_radius_pc": None},
        "bhsm_interpretation": interpretation}
    from . import __version__
    from .provenance import software_provenance
    result["product_version"] = __version__
    result["software_provenance"] = software_provenance()
    result["dataset_input"] = dataset.to_dict()
    result["analysis_configuration"] = {"initial": deepcopy(initial), **actual}
    result = _nullable(result)
    json.dumps(result, allow_nan=False)
    return result


def profile_timescale(dataset, result, values, *, max_nfev=1500):
    """Constrained nuisance profile on declared tE values, with honest failures.

    The baseline is a finite deterministic multistart solution, not a global
    optimality proof. All nuisance states remain in the same photometric domain.
    No automatic interval coverage is claimed, especially for blend boundaries.
    """
    dataset = _dataset(dataset)
    if result.get("schema") != RESULT_SCHEMA or result["input_sha256"] != dataset.sha256:
        raise ValueError("profile result/schema/input mismatch")
    options = result["run_options"]
    model = _Model(dataset, options["noise_scale"], options["equal_instrument_weight"], options["allow_negative_blend"])
    first = model.encode(result["parameters"])
    free = [i for i in range(len(first)) if i != 1]
    reference = result["numerical_convergence"]["objective_chi_square"]
    reference_solved = bool(result["numerical_convergence"].get("optimizer_success") and
                            result["numerical_convergence"].get("multistart_confirmed"))
    output = []
    for value in values:
        value = float(value)
        if not .1 <= value <= 10000 or not np.isfinite(value):
            raise ValueError("profile tE outside declared physical search domain")
        fixed = first.copy(); fixed[1] = math.log(value)
        def state(z):
            x = fixed.copy(); x[free] = z
            return x
        best = None
        for fraction in (float(first[4]), .05, .5, .95):
            seed = first[free].copy()
            for k, parameter in enumerate(free):
                if parameter >= 4 and parameter % 2 == 0:
                    seed[k] = fraction
            solution = least_squares(lambda z: model.evaluate(state(z)), seed,
                jac=lambda z: model.evaluate(state(z), jac=True)[:, free],
                bounds=(model.lower[free], model.upper[free]), max_nfev=max_nfev,
                x_scale="jac", **FIT_PROTOCOL["tolerances"])
            score = float(solution.fun @ solution.fun)
            if solution.success and (best is None or score < best[0]):
                best = score, solution
        if best is None:
            output.append({"tE_days": value, "status": "SEARCH_UNRESOLVED", "delta_chi_square": None,
                           "reason": "No converged admissible nuisance optimum established; this does not prove infeasibility."})
        else:
            score, solution = best
            x = state(solution.x)
            boundary = bool(np.any(np.minimum(x - model.lower, model.upper - x) < 1e-5))
            if not reference_solved or score < reference - 1e-4:
                status, delta = "REFERENCE_MINIMUM_UNRESOLVED", None
            else:
                status, delta = "ADMITTED_BOUNDARY_OPTIMUM" if boundary else "ADMITTED_INTERIOR_OPTIMUM", max(0.0, score - reference)
            output.append({"tE_days": value, "status": status, "objective_chi_square": score,
                "delta_chi_square": delta, "optimizer_success": True, "parameters": model.decode(x)})
    return {"schema": "bhsm_unresolved_timescale_profile/1", "input_sha256": dataset.sha256,
            "reference_objective_chi_square": reference, "coverage_claim": False, "rows": output}
