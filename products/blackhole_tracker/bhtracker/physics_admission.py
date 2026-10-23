"""Computable admission for the retained R1 compact-source exterior.

These are sufficient conditions on a *conditional worldtube exterior*.
They neither select a black-hole scalar charge nor certify a horizon solution.
All boundary coefficients are dimensionless delta(T/Mpl), in orthonormal real
l=2 harmonics [plus, cross, axial]. Distances are pc, velocities are observer
mas/yr. Thresholds are declared approximation budgets, not new constants.
"""
from __future__ import annotations

from functools import lru_cache
import math

import numpy as np

from .theory.radial_response import ScreenedExterior, G_PC_KMS2_MSUN, C_KM_S

N_STF = math.sqrt(15 / (8 * math.pi))
HESSIAN_B = 12 * N_STF
Y_MAX_PER_STATE_NORM = math.sqrt(5 / (4 * math.pi))
MAS_RAD = math.pi / (180 * 3600 * 1000)
C_PC_YR = C_KM_S * (365.25 * 86400) / 3.0856775814913673e13
CONDITIONAL_FLUX_PROVENANCE = frozenset({
    "regular_body_proxy", "supplied_conditional_flux", "supplied_worldtube_flux",
})


@lru_cache(maxsize=128)
def _exterior(mass, z_l, h0, r0, flux):
    return ScreenedExterior(M_msun=mass, z_l=z_l, H0=h0,
                            r0_pc=r0, flux_ratio=flux)


def _number(mapping, keys, default=None):
    for key in keys:
        if key in mapping:
            try:
                value = float(mapping[key])
            except (ValueError, TypeError):
                return None
            return value if math.isfinite(value) else None
    return default


def _distance_pc(geometry, name):
    public_name = {"dl": "D_l", "ds": "D_s", "dls": "D_ls"}[name]
    value = _number(geometry, [public_name + "_pc", name + "_pc"])
    if value is not None:
        return value
    value = _number(geometry, [public_name + "_mpc", public_name + "_Mpc", name + "_mpc", name + "_Mpc"])
    if value is not None:
        return value * 1e6
    value = _number(geometry, [name])
    unit = str(geometry.get("distance_unit", "")).lower()
    if value is not None and unit in {"pc", "mpc"}:
        return value * (1e6 if unit == "mpc" else 1)
    return None


def _redshift_order_ok(z_l, z_s, distances):
    if z_s is None:
        return True
    if z_s > z_l:
        return True
    # Public local-lens contract: geometric distances, rather than Hubble
    # redshifts, determine lensing for Galactic zero/zero data.
    return z_l == z_s == 0 and all(v is not None and v > 0 for v in distances)


def _time_ratio_min(d_over_c):
    """inf Kt / (|p|/(lambda*x)), on the charged branch."""
    if d_over_c >= .75:
        return 6.0
    t = math.sqrt(4 * d_over_c / 3)
    return 6 * t * (2 - t)


def _sound_speed_lower_squared(d_over_c):
    """Exact infimum of min(Kr,Kangular)/Kt on r>0."""
    radial = min(1 / d_over_c, 4 / 3)
    a = 4 * d_over_c - 6
    if a <= 0:
        angular = 1 / 3
    else:
        s = (6 + math.sqrt(36 + 3 * a * a)) / a
        angular = (s * s + 3) / (3 * (s - 1) ** 2 + 4 * d_over_c * s)
        angular = min(angular, 1 / d_over_c, 1 / 3)
    return min(radial, angular)


def _state(parameters, impedance):
    """Parse a prescribed 2- or 3-mode subspace; unseen xz,yz are fixed zero."""
    def vector(key):
        if key not in parameters:
            return None
        arr = np.asarray(parameters[key], dtype=float)
        if arr.ndim != 1 or arr.size not in (2, 3) or not np.all(np.isfinite(arr)):
            raise ValueError(key + " must be a finite length-2 or length-3 vector")
        return np.pad(arr, (0, 3 - arr.size))
    a = vector("boundary_amplitudes")
    q = vector("conormal_coefficients")
    if q is not None:
        aq = q / impedance
        if a is not None and not np.allclose(a, aq, rtol=1e-9, atol=0):
            raise ValueError("Dirichlet and conormal boundary states disagree")
        a = aq
    if a is None:
        a = np.zeros(3)
    if not np.all(np.isfinite(a)):
        raise ValueError("conormal conversion exceeds the finite boundary-state domain")
    return a, impedance * a


def resolve_boundary_amplitudes(config: dict, parameters: dict):
    """Canonical Dirichlet state for an R1 forward solve, or None if absent.

    Call before computing optical predictions, using the engine's actual
    worldtube in config.analysis.r0_pc. Supplied conormal coefficients use
    q=Lambda_2*a from the same exterior. This conversion validates source
    consistency; assess_physics separately checks physical admission.
    Neither input mapping is changed. An inconsistent pair raises ValueError.
    """
    if not any(key in parameters for key in ["boundary_amplitudes", "conormal_coefficients"]):
        return None
    geometry = config.get("geometry", config)
    analysis = config.get("analysis", {})
    mass = _number(parameters, ["mass_msun", "M_msun"])
    z_l = _number(geometry, ["z_l", "zl"], .3)
    h0 = _number(geometry, ["H0", "h0"], _number(analysis, ["H0"], 67.4))
    r0 = _number(analysis, ["r0_pc"], 10.)
    flux = _number(parameters, ["flux_ratio"], _number(analysis, ["flux_ratio"], 1.))
    if any(value is None for value in [mass, z_l, h0, r0, flux]):
        raise ValueError("finite source inputs required for boundary conversion")
    exterior = _exterior(mass, z_l, h0, r0, flux)
    impedance = float(exterior.impedance(2))
    if not math.isfinite(impedance) or impedance <= 0:
        raise ValueError("positive finite exterior impedance required")
    amplitudes, _ = _state(parameters, impedance)
    return amplitudes.tolist()


def _baseline_admission(geometry, analysis, parameters, impact_pc):
    """Keep point-mass admission independent of optional R1 model inputs."""
    try:
        mass = _number(parameters, ["mass_msun", "M_msun"])
        zl = _number(geometry, ["z_l", "zl"], .3)
        zs = _number(geometry, ["z_s", "zs"])
        distances = [_distance_pc(geometry, key) for key in ["dl", "ds", "dls"]]
        weak_cap = _number(analysis, ["weak_metric_cap"], .01)
        speed_cap = _number(analysis, ["quasistatic_speed_ratio_cap"], .01)
        if (mass is None or mass <= 0 or zl is None or zl < 0
                or not _redshift_order_ok(zl, zs, distances)
                or any(v is not None and v <= 0 for v in distances)
                or weak_cap is None or weak_cap <= 0 or speed_cap is None or speed_cap <= 0):
            return False
        mu = np.asarray(parameters.get("proper_motion_mas_yr", [0., 0.]), dtype=float)
        if mu.shape != (2,) or np.any(~np.isfinite(mu)):
            return False
        mu_norm = math.hypot(*mu)
        if mu_norm and distances[0] is None:
            return False
        speed = 0. if mu_norm == 0 else mu_norm * MAS_RAD * distances[0] * (1 + zl) / C_PC_YR
        if speed > speed_cap:
            return False
        if impact_pc is not None:
            impact = np.asarray(impact_pc, dtype=float).reshape(-1)
            if impact.size == 0 or np.any(~np.isfinite(impact)) or np.any(impact <= 0):
                return False
            mass_pc = G_PC_KMS2_MSUN * mass / C_KM_S ** 2
            if mass_pc / float(np.min(impact)) > weak_cap:
                return False
        return True
    except (ValueError, TypeError, OverflowError):
        return False


def assess_physics(config: dict, parameters: dict, impact_pc=None) -> dict:
    """Return JSON-compatible conditional-exterior eligibility and bounds.

    Canonical config: geometry.{D_l_pc,D_s_pc,D_ls_pc,z_l,z_s,H0};
    analysis.{r0_pc,flux_ratio,flux_provenance,eta_cap}. Explicit *_mpc keys
    are accepted. Bare dl/ds/dls need geometry.distance_unit='pc' or 'mpc'.
    Optional positive budgets: weak_metric_cap=.01,
    hessian_fraction_cap=.01, principal_fraction_cap=.01,
    quasistatic_speed_ratio_cap=.01, background_drift_cap=.01,
    spatial_gradient_ratio_cap=.01.
    A supplied intrinsic_timescale_observer_yr additionally tests the
    intrinsic boundary-evolution timescale. No supplied timescale means the
    *assumed fixed* boundary coefficients, not a derived relaxation time.

    Missing impact radii leave conditional eligibility available but do not
    set allowed_physics_models for the R1 lens families until verified.
    Baseline point-mass eligibility does not depend on scalar provenance.
    """
    geometry = config.get("geometry", config)
    analysis = config.get("analysis", {})
    baseline_ok = _baseline_admission(geometry, analysis, parameters, impact_pc)
    out = {
        "schema": "bhtracker.physics_admission.v1",
        "scope": "retained weak-metric, frozen-background, quasistatic R1 exterior",
        "horizon_matched_r1": False,
        "eligible_physics_models": {}, "allowed_physics_models": {},
        "checks": {}, "reasons": [],
        "hidden_boundary_components": "xz and yz fixed to zero in this template family",
    }
    checks = out["checks"]
    try:
        mass = _number(parameters, ["mass_msun", "M_msun"])
        z_l = _number(geometry, ["z_l", "zl"], .3)
        h0 = _number(geometry, ["H0", "h0"], _number(analysis, ["H0"], 67.4))
        r0 = _number(analysis, ["r0_pc"], 10.)
        flux = _number(parameters, ["flux_ratio"],
                       _number(analysis, ["flux_ratio"], 1.))
        if any(value is None for value in [mass, z_l, h0, r0, flux]):
            raise ValueError("finite mass, redshift, H0, worldtube and flux required")
        exterior = _exterior(mass, z_l, h0, r0, flux)
        if not np.all(np.isfinite([exterior.rV_pc, exterior.x0, exterior.m_pc,
                                   exterior.epsilon_infty, *exterior.coefficients.values()])):
            raise ValueError("physical scales overflow the numerical exterior domain")
        impedance = float(exterior.impedance(2))
        state, conormal = _state(parameters, impedance)
        amplitude = math.hypot(*state)
        dl = _distance_pc(geometry, "dl")
        ds = _distance_pc(geometry, "ds")
        dls = _distance_pc(geometry, "dls")
        present_distances = [v for v in [dl, ds, dls] if v is not None]
        geometry_ok = all(v > 0 for v in present_distances)
        z_s = _number(geometry, ["z_s", "zs"])
        geometry_ok = geometry_ok and _redshift_order_ok(z_l, z_s, [dl, ds, dls])
        if not geometry_ok:
            raise ValueError("require source redshift above lens, or zero/zero redshifts with three positive supplied distances")
        budgets = {
            "eta_cap": _number(analysis, ["eta_cap"], 1e-3),
            "weak_metric_cap": _number(analysis, ["weak_metric_cap"], .01),
            "hessian_fraction_cap": _number(analysis, ["hessian_fraction_cap"], .01),
            "principal_fraction_cap": _number(analysis, ["principal_fraction_cap"], .01),
            "quasistatic_speed_ratio_cap": _number(analysis, ["quasistatic_speed_ratio_cap"], .01),
            "background_drift_cap": _number(analysis, ["background_drift_cap"], .01),
            "spatial_gradient_ratio_cap": _number(analysis, ["spatial_gradient_ratio_cap"], .01),
        }
        if any(v is None or v <= 0 for v in budgets.values()):
            raise ValueError("approximation budgets must be positive finite numbers")
        if budgets["principal_fraction_cap"] >= 1:
            raise ValueError("principal_fraction_cap must be below one")
        if impact_pc is None:
            impact = np.array([], dtype=float)
        else:
            impact = np.asarray(impact_pc, dtype=float).reshape(-1)
            if impact.size == 0 or np.any(~np.isfinite(impact)) or np.any(impact <= 0):
                raise ValueError("impact_pc must contain positive finite physical radii")
        impact_verified = bool(impact.size)
        exterior_impact = bool(not impact_verified or np.min(impact) >= r0)
        p0 = abs(float(exterior.p(exterior.x0)))
        if not math.isfinite(p0):
            raise ValueError("nonfinite exterior scalar gradient")
        scale = exterior.x0 * p0
        d_ratio = exterior.D / exterior.C
        rt = _time_ratio_min(d_ratio)
        cmin2 = _sound_speed_lower_squared(d_ratio)
        background_cmin = math.sqrt(cmin2)

        # The analytic inequalities cover every exterior radius and every
        # normalized STF orientation, including states beyond the 3-mode UI.
        if scale > 0:
            hessian_relative = HESSIAN_B * amplitude / (math.sqrt(2) * scale)
            spatial_fraction = 2 * math.sqrt(2) * HESSIAN_B * amplitude / scale
            time_fraction = 4 * math.sqrt(3) * HESSIAN_B * amplitude / (rt * scale)
            caps = {
                "eta": budgets["eta_cap"] * scale / 6,
                "relative_hessian": budgets["hessian_fraction_cap"] * math.sqrt(2) * scale / HESSIAN_B,
                "spatial_principal": budgets["principal_fraction_cap"] * scale / (2 * math.sqrt(2) * HESSIAN_B),
                "time_principal": budgets["principal_fraction_cap"] * rt * scale / (4 * math.sqrt(3) * HESSIAN_B),
            }
            eta = 6 * amplitude / scale
            amplitude_cap = min(caps.values())
            bound_kind = "uniform charged-background relative bound"
            nonlinear_fraction = 2 * HESSIAN_B * amplitude / scale
        else:
            hessian_relative = eta = None
            spatial_factor = 4 * math.sqrt(2) * HESSIAN_B / (exterior.lambda_hat * exterior.C * exterior.x0 ** 2)
            time_factor = 4 * math.sqrt(3) * HESSIAN_B / (exterior.lambda_hat * exterior.D * exterior.x0 ** 2)
            spatial_fraction = spatial_factor * amplitude
            time_fraction = time_factor * amplitude
            caps = {
                "eta": None, "relative_hessian": None,
                "spatial_principal": budgets["principal_fraction_cap"] / spatial_factor,
                "time_principal": budgets["principal_fraction_cap"] / time_factor,
            }
            amplitude_cap = min(v for v in caps.values() if v is not None)
            bound_kind = "uniform absolute bound; zero monopole has no relative eta"
            nonlinear_fraction = 4 * HESSIAN_B * amplitude / (exterior.lambda_hat * exterior.C * exterior.x0 ** 2)
        # Boundary and exterior unit-state Hessian singular values sampled
        # independently of the uniform analytic coefficient B.
        radii = np.geomspace(r0, max(r0, exterior.rV_pc) * 1e4, 129)
        f, fr, _ = exterior.radial_derivatives(radii, 2)
        kr, ko, _ = exterior.principal(radii)
        y = radii * fr / f
        k = ko / kr
        sv = np.maximum.reduce([np.full_like(y, 2.), 2 * abs(y - 1),
                               2 / math.sqrt(3) * np.sqrt(1 + 2 * k * k) * (3 - y)])
        unit_hessian = N_STF * f / (radii / exterior.L0_pc) ** 2 * sv
        sampled_relative_per_a = None
        if scale > 0:
            x = radii / exterior.L0_pc
            p = np.abs(exterior.p(x))
            # Stable even where subtracting Kr-C would lose precision.
            px = -p / x * (-.5 - 1.5 * exterior.C / kr)
            background_norm = np.sqrt(px * px + 2 * (p / x) ** 2)
            sampled_relative_per_a = float(np.max(unit_hessian / background_norm))
        out["boundary_state"] = {
            "amplitudes_plus_cross_axial": state.tolist(),
            "conormal_coefficients": conormal.tolist(),
            "amplitude_norm": amplitude, "impedance_l2": impedance,
            "energy_over_Mpl2_L0": .5 * impedance * amplitude ** 2,
            "eta": eta, "eta_definition": "6*||a||/(x0*|p0|)",
            "bound_kind": bound_kind,
            "amplitude_norm_max": amplitude_cap,
            "conormal_norm_max": impedance * amplitude_cap,
            "individual_sufficient_caps": caps,
            "uniform_hessian_absolute_bound": HESSIAN_B * amplitude / exterior.x0 ** 2,
            "uniform_hessian_relative_bound": hessian_relative,
            "uniform_spatial_principal_fraction_bound": spatial_fraction,
            "uniform_time_principal_fraction_bound": time_fraction,
            "uniform_nonlinear_remainder_over_principal_scale": nonlinear_fraction,
            "nonlinear_principal_scale_definition": "Kangular * ||deltaPi||F; residual bound is not a solution-error bound",
            "max_boundary_unit_state_tested_hessian": float(np.max(unit_hessian)),
            "sampled_relative_hessian_per_unit_amplitude": sampled_relative_per_a,
            "sampled_radii": 129,
            "uniform_hessian_coefficient": HESSIAN_B,
            "sampling_is_certificate": False,
            "cap_semantics": "Sufficient retained-model guarantee. Exceeding this cap is outside the declared admitted family, not proof of physical impossibility or a principal-sign change.",
        }
        # Rayleigh bounds on Z0+deltaZ and Kt0+deltaKt give a state-
        # inclusive speed certificate. Zero means this sufficient bound
        # gives no positive speed, not that the actual characteristic is zero.
        cmin = background_cmin * math.sqrt(max(0., 1 - spatial_fraction) / (1 + time_fraction))
        mu = np.asarray(parameters.get("proper_motion_mas_yr", [0., 0.]), dtype=float)
        if mu.shape != (2,) or np.any(~np.isfinite(mu)):
            raise ValueError("proper_motion_mas_yr must be a finite length-2 vector")
        mu_norm = float(np.linalg.norm(mu))
        motion_verified = mu_norm == 0 or dl is not None
        speed = 0. if mu_norm == 0 else (mu_norm * MAS_RAD * dl * (1 + z_l) / C_PC_YR if dl is not None else None)
        speed_ratio = None if speed is None or cmin <= 0 else speed / cmin
        local_scale = max(r0, exterior.rV_pc, float(np.max(impact)) if impact_verified else r0)
        background_drift = max(abs(exterior.H), 2 * abs(exterior.d / exterior.v)) * local_scale / exterior.L0_pc
        timescale_key = "intrinsic_timescale_observer_yr"
        timescale_source = parameters if timescale_key in parameters else analysis
        timescale = None
        if timescale_key in timescale_source:
            # Missing means a prescribed fixed state. A supplied invalid value
            # must not silently select that more restrictive physical model.
            timescale = _number(timescale_source, [timescale_key])
            if timescale is None or timescale <= 0:
                raise ValueError("intrinsic timescale must be finite and positive when supplied")
        intrinsic_ratio = 0.
        if timescale is not None:
            intrinsic_ratio = None if cmin <= 0 else local_scale * (1 + z_l) / (C_PC_YR * cmin * timescale)
        weak_monopole = (1 + exterior.epsilon_infty) * exterior.m_pc / r0
        weak_state = .5 * abs(exterior.beta_hat) * Y_MAX_PER_STATE_NORM * amplitude
        total_spatial_gradient_ratio = ((p0 + math.sqrt(6) * N_STF * amplitude / exterior.x0) / exterior.v) ** 2
        min_impact = float(np.min(impact)) if impact_verified else None
        weak_at_impact = (exterior.m_pc / min_impact) if min_impact is not None else None
        provenance = str(analysis.get("flux_provenance", "unselected"))
        provenance_ok = provenance in CONDITIONAL_FLUX_PROVENANCE
        if provenance == "regular_body_proxy" and not math.isclose(flux, 1., rel_tol=1e-12, abs_tol=1e-14):
            provenance_ok = False
        checks.update({
            "geometry_valid": True,
            "impact_domain_verified": impact_verified,
            "impact_outside_worldtube": exterior_impact,
            "worldtube_weak_metric": weak_monopole + weak_state <= budgets["weak_metric_cap"],
            "weak_at_impacts": weak_at_impact is None or weak_at_impact <= budgets["weak_metric_cap"],
            "state_within_sufficient_cap": amplitude <= amplitude_cap * (1 + 1e-12),
            "retained_spatial_principal_positive": spatial_fraction < 1,
            "retained_time_principal_positive": time_fraction < 1,
            "flux_provenance_selected": provenance_ok,
            "motion_units_verified": motion_verified,
            "quasistatic_motion": speed_ratio is not None and speed_ratio <= budgets["quasistatic_speed_ratio_cap"],
            "quasistatic_intrinsic_evolution": intrinsic_ratio is not None and intrinsic_ratio <= budgets["quasistatic_speed_ratio_cap"],
            "frozen_background": background_drift <= budgets["background_drift_cap"],
            "small_spatial_background_gradient": total_spatial_gradient_ratio <= budgets["spatial_gradient_ratio_cap"],
        })
        checks["baseline_point_mass_admitted"] = baseline_ok
        spherical_ok = all(checks[key] for key in [
            "worldtube_weak_metric", "impact_outside_worldtube", "flux_provenance_selected",
            "motion_units_verified", "quasistatic_motion", "frozen_background", "small_spatial_background_gradient"])
        boundary_ok = spherical_ok and all(checks[key] for key in [
            "state_within_sufficient_cap", "retained_spatial_principal_positive",
            "retained_time_principal_positive", "quasistatic_intrinsic_evolution"])
        eligible = {"baseline_point_mass": baseline_ok,
                    "r1_spherical_conditional": spherical_ok,
                    "r1_boundary_conditional": boundary_ok,
                    "horizon_matched_r1": False}
        out["eligible_physics_models"] = eligible
        out["allowed_physics_models"] = dict(eligible)
        if not impact_verified:
            out["allowed_physics_models"]["r1_spherical_conditional"] = False
            out["allowed_physics_models"]["r1_boundary_conditional"] = False
        out["source_pairing"] = {
            "flux_ratio": flux, "flux_provenance": provenance,
            "accepted_provenance": sorted(CONDITIONAL_FLUX_PROVENANCE),
            "regular_body_proxy_is_bh_horizon_solution": False,
            "boundary_condition": "specified Dirichlet or conormal worldtube state",
        }
        out["scales"] = {
            "mass_msun": mass, "m_pc": exterior.m_pc, "r0_pc": r0,
            "rV_pc": exterior.rV_pc, "L0_pc": exterior.L0_pc,
            "p0": -p0, "x0_abs_p0": scale,
            "weak_metric_bound_at_worldtube": weak_monopole + weak_state,
            "weak_metric_at_minimum_impact": weak_at_impact,
            "spatial_to_temporal_background_gradient_ratio_at_r0": p0 ** 2 / exterior.v ** 2,
            "uniform_total_spatial_to_temporal_gradient_ratio_bound": total_spatial_gradient_ratio,
            "local_patch_scale_pc": local_scale,
            "background_drift_ratio": background_drift,
            "speed_over_c": speed, "characteristic_speed_lower_over_c": cmin,
            "background_characteristic_speed_lower_over_c": background_cmin,
            "characteristic_speed_bound_kind": "state-inclusive retained principal bound; zero means no positive guarantee",
            "quasistatic_advection_ratio": speed_ratio,
            "intrinsic_evolution_ratio": intrinsic_ratio,
            "intrinsic_evolution_assumption": "fixed prescribed state" if timescale is None else "supplied observer timescale",
        }
        out["coefficients"] = dict(exterior.coefficients)
        out["approximation_budgets"] = budgets
        out["limits"] = [
            "Bounds certify the retained local QS principal coefficients and perturbation size, not full covariant stability or observational accuracy.",
            "A false principal-positivity check means the sufficient bound does not guarantee the sign; it is not a calculation of a negative principal coefficient.",
            "Line-of-sight projection is the declared decaying local extension; cosmological matching and time corrections remain separate model errors.",
            "No near-horizon boundary value or black-hole charge follows from regular-body or worldtube proxy provenance.",
        ]
        if not impact_verified:
            out["reasons"].append("Supply post-fit physical impact radii to verify the worldtube domain.")
        for key in ["flux_provenance_selected", "motion_units_verified", "worldtube_weak_metric", "impact_outside_worldtube", "state_within_sufficient_cap", "quasistatic_motion", "quasistatic_intrinsic_evolution", "frozen_background", "small_spatial_background_gradient"]:
            if not checks[key]:
                out["reasons"].append(key)
        return out
    except (ValueError, TypeError, FloatingPointError, OverflowError) as exc:
        out["eligible_physics_models"] = {key: False for key in [
            "baseline_point_mass", "r1_spherical_conditional", "r1_boundary_conditional", "horizon_matched_r1"]}
        out["eligible_physics_models"]["baseline_point_mass"] = baseline_ok
        out["allowed_physics_models"] = dict(out["eligible_physics_models"])
        out["checks"]["valid_r1_input"] = False
        out["checks"]["baseline_point_mass_admitted"] = baseline_ok
        out["reasons"].append(str(exc))
        return out
