"""Independent, replayable checks for the retained R1 admission bounds.

Run pytest on this file, or run it directly with --receipt PATH to persist
the numerical receipt. Cartesian differences below use actual scalar-field
values, independently of the Hessian singular-coefficient derivation.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np
import pytest
import scipy

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bhtracker import physics_admission as pa


@lru_cache(maxsize=1)
def checked_receipt():
    exterior = pa.ScreenedExterior()
    amplitude = .001 * exterior.x0 * abs(float(exterior.p(exterior.x0))) / 6
    config = {"geometry": {"D_l_pc": 9e8, "D_s_pc": 1.5e9,
                            "D_ls_pc": 9e8, "z_l": .3, "z_s": 1., "H0": 67.4},
              "analysis": {"r0_pc": 10, "flux_ratio": 1,
                           "flux_provenance": "regular_body_proxy"}}
    parameters = {"mass_msun": 1e9, "proper_motion_mas_yr": [1e-5, 2e-5],
                  "boundary_amplitudes": [amplitude, 0, 0]}
    accepted = pa.assess_physics(config, parameters, [100, 340, 1000])
    for key in ["baseline_point_mass", "r1_spherical_conditional", "r1_boundary_conditional"]:
        assert accepted["allowed_physics_models"][key], accepted
    assert not accepted["allowed_physics_models"]["horizon_matched_r1"]
    assert not pa.assess_physics(config, parameters, [9])["allowed_physics_models"]["r1_boundary_conditional"]
    assert not pa.assess_physics(config, parameters)["allowed_physics_models"]["r1_boundary_conditional"]
    # Every post-fit family must pass its actual weak-field/speed checks;
    # being outside the worldtube alone is not enough.
    too_fast = dict(parameters, proper_motion_mas_yr=[.01, .01])
    fast_assessment = pa.assess_physics(config, too_fast, [100, 340, 1000])
    assert not fast_assessment["allowed_physics_models"]["baseline_point_mass"]
    assert not fast_assessment["allowed_physics_models"]["r1_boundary_conditional"]
    too_large = dict(parameters, boundary_amplitudes=[100 * amplitude, 0, 0])
    large_assessment = pa.assess_physics(config, too_large, [100, 340, 1000])
    assert large_assessment["allowed_physics_models"]["baseline_point_mass"]
    assert not large_assessment["allowed_physics_models"]["r1_boundary_conditional"]
    m_pc = pa.G_PC_KMS2_MSUN * parameters["mass_msun"] / pa.C_KM_S ** 2
    assert math.isclose(accepted["scales"]["m_pc"], m_pc, rel_tol=1e-15)
    assert pa.assess_physics(config, {"mass_msun": 1e9}, [m_pc / .01 * (1 + 1e-10)])["allowed_physics_models"]["baseline_point_mass"]
    assert not pa.assess_physics(config, {"mass_msun": 1e9}, [m_pc / .01 * (1 - 1e-10)])["allowed_physics_models"]["baseline_point_mass"]
    galactic = {"geometry": {"D_l_pc": 1000, "D_s_pc": 8000,
                              "D_ls_pc": 7000, "z_l": 0., "z_s": 0.},
                "analysis": {"r0_pc": 1e-5, "flux_ratio": 1.,
                             "flux_provenance": "regular_body_proxy"}}
    galactic_state = pa.assess_physics(galactic, {"mass_msun": 10.,
                        "proper_motion_mas_yr": [5., 2.]}, [1e-4, 1e-3])
    for key in ["baseline_point_mass", "r1_spherical_conditional", "r1_boundary_conditional"]:
        assert galactic_state["allowed_physics_models"][key], galactic_state
    assert galactic_state["checks"]["impact_outside_worldtube"]
    assert galactic_state["checks"]["worldtube_weak_metric"]
    assert not pa.assess_physics(galactic, {"mass_msun": 10.}, [1e-6])["allowed_physics_models"]["r1_boundary_conditional"]
    local_missing_distances = {"geometry": {"z_l": 0., "z_s": 0.}, "analysis": galactic["analysis"]}
    assert not pa.assess_physics(local_missing_distances, {"mass_msun": 10.}, [1e-3])["allowed_physics_models"]["baseline_point_mass"]
    unselected = {"geometry": config["geometry"], "analysis": {"r0_pc": 10, "flux_ratio": 1}}
    a = pa.assess_physics(unselected, parameters, [100])
    assert a["allowed_physics_models"]["baseline_point_mass"]
    assert not a["allowed_physics_models"]["r1_boundary_conditional"]
    # Optional R1 failure must not disable otherwise valid baseline inference.
    unsupported = {"geometry": dict(config["geometry"], z_l=2.2, z_s=3.),
                   "analysis": config["analysis"]}
    assert pa.assess_physics(unsupported, {"mass_msun": 1e9}, [100])["allowed_physics_models"]["baseline_point_mass"]
    q = exterior.impedance() * np.array([amplitude, 0, 0])
    prescribed_q = dict(parameters)
    prescribed_q.pop("boundary_amplitudes")
    prescribed_q["conormal_coefficients"] = q
    mapped = pa.assess_physics(config, prescribed_q, [100])
    assert np.allclose(mapped["boundary_state"]["amplitudes_plus_cross_axial"],
                       [amplitude, 0, 0], rtol=1e-12, atol=0)
    np.testing.assert_allclose(pa.resolve_boundary_amplitudes(config, prescribed_q),
                               [amplitude, 0, 0], rtol=1e-12, atol=0)
    assert pa.resolve_boundary_amplitudes(config, {"mass_msun": 1e9}) is None
    with pytest.raises(ValueError, match="disagree"):
        pa.resolve_boundary_amplitudes(config, dict(prescribed_q, boundary_amplitudes=[0., 0., 0.]))
    zero_config = {"geometry": config["geometry"],
                   "analysis": {"r0_pc": 10, "flux_ratio": 0,
                                "flux_provenance": "supplied_worldtube_flux"}}
    zero = pa.assess_physics(zero_config, {"mass_msun": 1e9}, [100])
    zero_cap = zero["boundary_state"]["amplitude_norm_max"]
    zero_state = pa.assess_physics(zero_config, {"mass_msun": 1e9,
                      "boundary_amplitudes": [.5 * zero_cap, 0, 0]}, [100])
    assert zero_cap > 0
    assert zero_state["allowed_physics_models"]["r1_boundary_conditional"]
    assert zero_state["boundary_state"]["eta"] is None
    for item in [accepted, mapped, zero_state, a, galactic_state, fast_assessment, large_assessment]:
        json.dumps(item, allow_nan=False)
    # Observer-time conversion uses the lens time-dilation factor exactly once.
    expected_speed = math.hypot(1e-5, 2e-5) * pa.MAS_RAD * 9e8 * 1.3 / pa.C_PC_YR
    assert math.isclose(accepted["scales"]["speed_over_c"], expected_speed, rel_tol=1e-14)
    # Near and far radial comparison and logarithmic slope, evaluated from
    # the actual hypergeometric provider rather than a separate power law.
    radii = np.geomspace(exterior.r0_pc, exterior.rV_pc * 1e8, 501)
    f, fp, _ = exterior.radial_derivatives(radii)
    y = radii * fp / f
    p0 = abs(float(exterior.p(exterior.x0)))
    comparison = abs(exterior.p(radii / exterior.L0_pc)) / p0
    assert np.max(f / comparison) <= 1 + 2e-12
    assert np.min(y) >= -3 - 2e-12 and np.max(y) <= -1 + 2e-12

    rng = np.random.default_rng(1974)
    maximum = {"hessian": 0., "spatial": 0., "time": 0., "gradient": 0.}
    scale = exterior.x0 * p0
    hessian_bound = pa.HESSIAN_B / (math.sqrt(2) * scale)
    spatial_bound = 2 * math.sqrt(2) * pa.HESSIAN_B / scale
    time_bound = 4 * math.sqrt(3) * pa.HESSIAN_B / (pa._time_ratio_min(exterior.D / exterior.C) * scale)
    gradient_bound = math.sqrt(6) * pa.N_STF / scale
    samples = 0
    for radius in np.geomspace(exterior.r0_pc * 1.002, exterior.rV_pc * 100, 31):
        for _ in range(12):
            n = rng.normal(size=3)
            n /= np.linalg.norm(n)
            tensor = rng.normal(size=(3, 3))
            tensor = (tensor + tensor.T) / 2
            tensor -= np.eye(3) * np.trace(tensor) / 3
            tensor /= np.linalg.norm(tensor)
            position = radius * n
            step = radius * 2e-4

            def field(x):
                r = np.linalg.norm(x)
                direction = x / r
                return pa.N_STF * float(exterior.radial(r)) * float(direction @ tensor @ direction)

            hessian = np.zeros((3, 3))
            gradient = np.zeros(3)
            f0 = field(position)
            for i in range(3):
                ei = np.eye(3)[i] * step
                plus, minus = field(position + ei), field(position - ei)
                gradient[i] = (plus - minus) / (2 * step)
                hessian[i, i] = (plus - 2 * f0 + minus) / step ** 2
                for j in range(i):
                    ej = np.eye(3)[j] * step
                    hessian[i, j] = hessian[j, i] = (
                        field(position + ei + ej) - field(position + ei - ej)
                        - field(position - ei + ej) + field(position - ei - ej)) / (4 * step ** 2)
            hessian *= exterior.L0_pc ** 2
            gradient *= exterior.L0_pc
            x = radius / exterior.L0_pc
            p = abs(float(exterior.p(x)))
            kr, ko, kt = map(float, exterior.principal(radius))
            pp = -p / x * (-.5 - 1.5 * exterior.C / kr)
            background_norm = math.sqrt(pp * pp + 2 * (p / x) ** 2)
            hessian_fraction = np.linalg.norm(hessian) / background_norm
            dz = -4 * (np.trace(hessian) * np.eye(3) - hessian) / exterior.lambda_hat
            spatial_fraction = np.linalg.norm(dz, 2) / ko
            time_fraction = 4 * abs(np.trace(hessian)) / (exterior.lambda_hat * kt)
            gradient_fraction = np.linalg.norm(gradient) / p
            maximum["hessian"] = max(maximum["hessian"], hessian_fraction / hessian_bound)
            maximum["spatial"] = max(maximum["spatial"], spatial_fraction / spatial_bound)
            maximum["time"] = max(maximum["time"], time_fraction / time_bound)
            maximum["gradient"] = max(maximum["gradient"], gradient_fraction / gradient_bound)
            samples += 1
    assert all(0 < value < 1 for value in maximum.values()), maximum

    s = 1 + np.geomspace(1e-9, 1e10, 4001)
    margin_time, margin_sound = float("inf"), float("inf")
    for d in np.geomspace(1e-4, 1e4, 401):
        actual_time = 6 - 6 / s + 8 * d / (s - 1)
        margin_time = min(margin_time, float(np.min(actual_time) / pa._time_ratio_min(d)))
        denominator = 3 * (s - 1) ** 2 + 4 * d * s
        actual_sound = np.minimum(4 * s * s / denominator, (s * s + 3) / denominator)
        margin_sound = min(margin_sound, float(np.min(actual_sound) / pa._sound_speed_lower_squared(d)))
    assert margin_time >= 1 - 1e-10 and margin_sound >= 1 - 1e-10
    files = [Path(pa.__file__), Path(sys.modules[pa.ScreenedExterior.__module__].__file__), Path(__file__)]
    return {
        "status": "pass", "python": sys.version, "numpy": np.__version__, "scipy": scipy.__version__,
        "files_sha256": {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in files},
        "default_coefficients": accepted["coefficients"],
        "default_boundary_state": accepted["boundary_state"],
        "default_scales": accepted["scales"],
        "zero_flux_amplitude_cap": zero_cap,
        "galactic_zero_redshift_case": {"geometry": galactic["geometry"],
                   "parameters": {"mass_msun": 10., "proper_motion_mas_yr": [5., 2.]},
                   "impact_pc": [1e-4, 1e-3], "admission": galactic_state},
        "cartesian_fd": {"seed": 1974, "samples": samples, "step_over_radius": 2e-4,
                          "maximum_actual_over_uniform": maximum},
        "radial_comparison": {"radii": 501, "max_f2_over_f1": float(np.max(f / comparison)),
                              "min_log_slope": float(np.min(y)), "max_log_slope": float(np.max(y))},
        "coefficient_grid": {"d_samples": 401, "s_samples": 4001,
                             "minimum_time_bound_ratio": margin_time, "minimum_sound_bound_ratio": margin_sound},
        "api_cases": ["capitalized distance contract", "default admitted", "inner impact rejected",
                      "missing impact conditional pending", "unselected flux independent baseline",
                      "unsupported R1 redshift independent baseline", "conormal source pairing",
                      "zero flux nonzero boundary state", "finite JSON", "observer proper-motion units",
                      "Galactic zero/zero supplied-distance contract", "local zero/zero requires distances",
                      "physical outside-worldtube state", "outside-worldtube fast state rejected",
                      "outside-worldtube excess boundary state rejected", "IAU mass-unit weak-field boundary"],
        "interpretation": "Numerical checks corroborate, but do not replace, the uniform analytic proof.",
    }


def test_admission_and_units():
    assert checked_receipt()["status"] == "pass"


def test_cartesian_hessian_and_gradient_bounds():
    assert all(value < 1 for value in checked_receipt()["cartesian_fd"]["maximum_actual_over_uniform"].values())


def test_principal_coefficient_lower_bounds():
    grid = checked_receipt()["coefficient_grid"]
    assert grid["minimum_time_bound_ratio"] >= 1 - 1e-10
    assert grid["minimum_sound_bound_ratio"] >= 1 - 1e-10


def test_sufficient_cap_exceedance_is_not_a_principal_instability_claim():
    config = {"geometry": {"D_l_pc": 9e8, "D_s_pc": 1.5e9,
                            "D_ls_pc": 9e8, "z_l": .3, "z_s": 1.},
              "analysis": {"r0_pc": 10., "flux_ratio": 1.,
                           "flux_provenance": "regular_body_proxy"}}
    base = pa.assess_physics(config, {"mass_msun": 1e9}, [100.])
    cap = base["boundary_state"]["amplitude_norm_max"]
    larger = pa.assess_physics(config, {"mass_msun": 1e9,
                  "boundary_amplitudes": [2 * cap, 0., 0.]}, [100.])
    assert not larger["checks"]["state_within_sufficient_cap"]
    assert not larger["allowed_physics_models"]["r1_boundary_conditional"]
    # The chosen eta budget fails while stronger analytic sign guarantees
    # still hold. Cap exceedance is therefore not an instability theorem.
    assert larger["checks"]["retained_spatial_principal_positive"]
    assert larger["checks"]["retained_time_principal_positive"]
    assert "not proof of physical impossibility" in larger["boundary_state"]["cap_semantics"]


@pytest.mark.parametrize("location", ["analysis", "parameters"])
@pytest.mark.parametrize("invalid", ["not-a-timescale", None, float("nan"), float("inf"), 0., -1.])
def test_supplied_invalid_evolution_timescale_cannot_become_fixed_state(location, invalid):
    config = {"geometry": {"D_l_pc": 9e8, "D_s_pc": 1.5e9,
                            "D_ls_pc": 9e8, "z_l": .3, "z_s": 1.},
              "analysis": {"r0_pc": 10., "flux_ratio": 1.,
                           "flux_provenance": "regular_body_proxy"}}
    parameters = {"mass_msun": 1e9}
    target = config["analysis"] if location == "analysis" else parameters
    target["intrinsic_timescale_observer_yr"] = invalid
    result = pa.assess_physics(config, parameters, [100.])
    assert result["allowed_physics_models"]["baseline_point_mass"]
    assert not result["allowed_physics_models"]["r1_boundary_conditional"]
    assert not result["checks"]["valid_r1_input"]
    assert any("finite and positive when supplied" in reason for reason in result["reasons"])


def test_valid_evolution_timescale_and_parameter_override():
    config = {"geometry": {"D_l_pc": 9e8, "D_s_pc": 1.5e9,
                            "D_ls_pc": 9e8, "z_l": .3, "z_s": 1.},
              "analysis": {"r0_pc": 10., "flux_ratio": 1.,
                           "flux_provenance": "regular_body_proxy"}}
    fixed = pa.assess_physics(config, {"mass_msun": 1e9}, [100.])
    assert fixed["allowed_physics_models"]["r1_boundary_conditional"]
    assert fixed["scales"]["intrinsic_evolution_assumption"] == "fixed prescribed state"
    config["analysis"]["intrinsic_timescale_observer_yr"] = "inactive-config-value"
    slow = pa.assess_physics(config, {"mass_msun": 1e9,
                    "intrinsic_timescale_observer_yr": 1e12}, [100.])
    fast = pa.assess_physics(config, {"mass_msun": 1e9,
                    "intrinsic_timescale_observer_yr": 1.}, [100.])
    assert slow["allowed_physics_models"]["r1_boundary_conditional"]
    assert slow["scales"]["intrinsic_evolution_assumption"] == "supplied observer timescale"
    assert not fast["checks"]["quasistatic_intrinsic_evolution"]
    assert not fast["allowed_physics_models"]["r1_boundary_conditional"]


@pytest.mark.parametrize("evolution", [False, True])
def test_speed_threshold_uses_state_inclusive_principal_certificate(evolution):
    config = {"geometry": {"D_l_pc": 9e8, "D_s_pc": 1.5e9,
                            "D_ls_pc": 9e8, "z_l": .3, "z_s": 1.},
              "analysis": {"r0_pc": 10., "flux_ratio": 1.,
                           "flux_provenance": "regular_body_proxy"}}
    zero = pa.assess_physics(config, {"mass_msun": 1e9}, [100.])
    amplitude = zero["boundary_state"]["amplitude_norm_max"]
    parameters = {"mass_msun": 1e9, "boundary_amplitudes": [amplitude, 0., 0.]}
    state = pa.assess_physics(config, parameters, [100.])
    background = state["scales"]["background_characteristic_speed_lower_over_c"]
    corrected = state["scales"]["characteristic_speed_lower_over_c"]
    assert 0 < corrected < background
    assert zero["scales"]["characteristic_speed_lower_over_c"] == background
    spatial = state["boundary_state"]["uniform_spatial_principal_fraction_bound"]
    temporal = state["boundary_state"]["uniform_time_principal_fraction_bound"]
    assert corrected == pytest.approx(background * np.sqrt((1-spatial)/(1+temporal)), rel=1e-15)
    cap = state["approximation_budgets"]["quasistatic_speed_ratio_cap"]
    midpoint_speed = cap * (background + corrected) / 2
    if evolution:
        scale = state["scales"]["local_patch_scale_pc"]
        parameters["intrinsic_timescale_observer_yr"] = scale * 1.3 / (pa.C_PC_YR * midpoint_speed)
        key = "quasistatic_intrinsic_evolution"
    else:
        parameters["proper_motion_mas_yr"] = [midpoint_speed * pa.C_PC_YR / (pa.MAS_RAD * 9e8 * 1.3), 0.]
        key = "quasistatic_motion"
    # This lies below the old spherical-background cutoff, above the
    # rigorous state-inclusive cutoff, and inside baseline slow motion.
    assert midpoint_speed / background < cap < midpoint_speed / corrected
    rejected = pa.assess_physics(config, parameters, [100.])
    assert rejected["allowed_physics_models"]["baseline_point_mass"]
    assert not rejected["checks"][key]
    assert not rejected["allowed_physics_models"]["r1_boundary_conditional"]


def test_public_conormal_and_dirichlet_physical_predictions_agree():
    from bhtracker.examples import make_example
    from bhtracker.forward import LensEngine

    raw, parameters = make_example("cosmological_short_track", noise=False)
    engine = LensEngine(raw, family="r1")
    base, branch = engine.calculate(parameters)
    physics = pa.assess_physics(raw, parameters, branch["impact_pc"])
    amplitude = physics["boundary_state"]["amplitude_norm_max"]
    impedance = physics["boundary_state"]["impedance_l2"]
    a_state = dict(parameters, boundary_amplitudes=[amplitude, 0., 0.])
    q_state = dict(parameters, conormal_coefficients=[impedance * amplitude, 0., 0.])
    dirichlet, _ = engine.calculate(a_state)
    conormal, _ = engine.calculate(q_state)
    # The admitted response must be resolvable in floating arithmetic, so a
    # silently ignored conormal input cannot pass an equality-to-zero test.
    assert np.max(abs(dirichlet[:, :4] - base[:, :4])) > 1e-12
    np.testing.assert_allclose(conormal[:, :4], dirichlet[:, :4], rtol=0, atol=1e-12)
    np.testing.assert_allclose(conormal[:, 4:], dirichlet[:, 4:], rtol=0, atol=1e-12)


def test_disagreeing_boundary_pair_rejected_before_optics(monkeypatch):
    from bhtracker.examples import make_example
    from bhtracker.forward import LensEngine

    raw, parameters = make_example("nearby_motion", noise=False)
    engine = LensEngine(raw, family="r1")
    def forbidden(*args, **kwargs):
        raise AssertionError("optical potential evaluated before source validation")
    monkeypatch.setattr(engine, "potential", forbidden)
    parameters = dict(parameters, boundary_amplitudes=[0., 0., 0.],
                      conormal_coefficients=[1e-40, 0., 0.])
    with pytest.raises(ValueError, match="disagree"):
        engine.calculate(parameters)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    receipt = checked_receipt()
    encoded = json.dumps(receipt, indent=2, allow_nan=False)
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)
