"""Direct-provider contracts for scale-covariant R1 lens calculations.

Criteria declared before running: 2e-5 relative for runtime projection jets,
monopole phase differences, independent Cartesian potential jets, and the
profiled unit optical response. These are numerical checks of the retained
conditional model, not interval certificates or astrophysical state tests.
No enlarged physical boundary amplitude is propagated through a lens solve.
Run directly to print the numerical receipt; pytest runs the same checks.
"""
from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import sys

import numpy as np
import pytest
from scipy.integrate import quad

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bhtracker.data import load_dataset
from bhtracker.envelope import assess_envelope
from bhtracker.examples import make_example
from bhtracker.forward import LensEngine
from bhtracker.physics_admission import assess_physics
from bhtracker.theory.radial_response import ScreenedExterior

RTOL = 2e-5


def _relative(actual, expected):
    actual, expected = np.asarray(actual), np.asarray(expected)
    denominator = np.maximum(abs(expected), 1e-12 * np.max(abs(expected)))
    return float(np.max(abs(actual - expected) / np.maximum(denominator, 1e-100)))


ANNULI = ["cosmological_short_track", "nearby_motion", "stellar_benchmark"]


@lru_cache(maxsize=3)
def fixture(name="cosmological_short_track"):
    raw, parameters = make_example(name, noise=False)
    data = load_dataset(raw)
    engine = LensEngine(data, family="r1")
    return data, engine, parameters


@lru_cache(maxsize=3)
def runtime_receipt(name="cosmological_short_track"):
    data, engine, _ = fixture(name)
    radii = np.array([.4, 1., 2.])
    maximum = {"monopole_first": 0., "monopole_second": 0.,
               "quadrupole_phase": 0., "quadrupole_first": 0., "quadrupole_second": 0.,
               "axial_phase": 0., "axial_first": 0., "axial_second": 0.,
               "monopole_phase_difference": 0., "monopole_phase_fd_first": 0.,
               "monopole_phase_fd_second": 0.}
    cases = []
    for massratio in [.2, 1., 5.]:
        for flux in [.2, 1., 3.]:
            direct = ScreenedExterior(M_msun=engine.ref_mass * massratio,
                     z_l=data.geometry["z_l"], r0_pc=engine.r0, flux_ratio=flux)
            b = radii * engine.rE
            alpha, alpha_prime, _ = direct.monopole_deflection(b)
            phase, first, second = engine._r1.monopole(radii, massratio, flux)
            expected_first = alpha * engine.rE / (4 * engine.mref_pc)
            expected_second = alpha_prime * engine.rE ** 2 / (4 * engine.mref_pc)
            errors = {"monopole_first": _relative(first, expected_first),
                      "monopole_second": _relative(second, expected_second)}
            for axial, label in [(False, "quadrupole"), (True, "axial")]:
                q, qp, qpp = (direct.projected_axial if axial else direct.projected_quad)(b)
                expected = np.array([q, qp * engine.rE, qpp * engine.rE ** 2]) / (4 * engine.mref_pc)
                actual = engine._r1.quadrupole(radii, massratio, flux, axial=axial)
                for index, suffix in enumerate(["phase", "first", "second"]):
                    errors[label + "_" + suffix] = _relative(actual[index], expected[index])
            integral = quad(lambda x: float(direct.monopole_deflection(x * engine.rE)[0])
                            * engine.rE / (4 * engine.mref_pc), radii[0], radii[-1],
                            epsabs=1e-15, epsrel=1e-10)[0]
            errors["monopole_phase_difference"] = abs((phase[-1] - phase[0]) / integral - 1)
            # Differentiate the runtime phase itself, independently of the
            # analytic alpha/alpha-prime returned alongside it.
            step = radii * 1e-3
            plus = engine._r1.monopole(radii + step, massratio, flux)[0]
            minus = engine._r1.monopole(radii - step, massratio, flux)[0]
            errors["monopole_phase_fd_first"] = _relative((plus - minus) / (2 * step), expected_first)
            errors["monopole_phase_fd_second"] = _relative((plus - 2 * phase + minus) / step ** 2, expected_second)
            for key, value in errors.items():
                maximum[key] = max(maximum[key], value)
            cases.append({"massratio": massratio, "flux_ratio": flux, "relative_errors": errors})
    assert all(value < RTOL for value in maximum.values()), maximum
    # Exact zero-flux harmonic control, independently from the direct provider.
    for massratio in [.2, 1., 5.]:
        zero = ScreenedExterior(M_msun=engine.ref_mass * massratio,
                   z_l=data.geometry["z_l"], r0_pc=engine.r0, flux_ratio=0.)
        b = radii * engine.rE
        direct = np.array(zero.projected_quad(b)) * np.array([1, engine.rE, engine.rE ** 2])[:, None] / (4 * engine.mref_pc)
        np.testing.assert_allclose(engine._r1.quadrupole(radii, massratio, 0), direct, rtol=2e-14)
        np.testing.assert_array_equal(engine._r1.quadrupole(radii, massratio, 0, axial=True), np.zeros((3, 3)))
        np.testing.assert_array_equal(engine._r1.monopole(radii, massratio, 0), np.zeros((3, 3)))
    return {"status": "pass", "annulus": name, "criterion_relative": RTOL, "r_over_rE": radii.tolist(),
            "rE_pc": engine.rE, "mass_reference_msun": engine.ref_mass,
            "maximum_relative_errors": maximum, "cases": cases,
            "runtime_table_report": engine._r1.report,
            "scope": "sampled interpolation and scaling checks; no interval certificate"}


def _direct_phase(direct, engine, points, mode):
    radius = np.linalg.norm(points, axis=-1)
    if mode == 2:
        return direct.projected_axial(radius * engine.rE)[0] / (4 * engine.mref_pc)
    q = direct.projected_quad(radius * engine.rE)[0] / (4 * engine.mref_pc)
    angular = ((points[..., 0] ** 2 - points[..., 1] ** 2) if mode == 0
               else 2 * points[..., 0] * points[..., 1]) / radius ** 2
    return q * angular


def _cartesian_jets(field, points, relative_step=1e-4):
    points = np.asarray(points)
    value = field(points)
    gradient = np.zeros(points.shape)
    hessian = np.zeros(points.shape + (2,))
    step = relative_step * np.linalg.norm(points, axis=-1)
    for i in range(2):
        ei = np.eye(2)[i] * step[..., None]
        plus, minus = field(points + ei), field(points - ei)
        gradient[..., i] = (plus - minus) / (2 * step)
        hessian[..., i, i] = (plus - 2 * value + minus) / step ** 2
        for j in range(i):
            ej = np.eye(2)[j] * step[..., None]
            hessian[..., i, j] = hessian[..., j, i] = (
                field(points + ei + ej) - field(points + ei - ej)
                - field(points - ei + ej) + field(points - ei - ej)) / (4 * step ** 2)
    return value, gradient, hessian


def _direct_cartesian_jets(direct, engine, points, mode):
    """Independent Cartesian product/chain rule from direct radial jets.

    For transverse modes write psi=h(r)*(x.T Q x), h=q/r^2. This avoids
    differentiating quadrature noise in a nearly constant deep phase.
    """
    r = np.linalg.norm(points, axis=-1)
    e = points / r[..., None]
    ee = e[..., :, None] * e[..., None, :]
    eye = np.eye(2)
    radial = direct.projected_axial if mode == 2 else direct.projected_quad
    q, qp, qpp = np.array(radial(r * engine.rE)) * np.array([1, engine.rE, engine.rE ** 2]).reshape((3,) + (1,) * r.ndim) / (4 * engine.mref_pc)
    if mode == 2:
        return q, qp[..., None] * e, qpp[..., None, None] * ee + (qp / r)[..., None, None] * (eye - ee)
    tensor = np.diag([1., -1.]) if mode == 0 else np.array([[0., 1.], [1., 0.]])
    tx = points @ tensor
    quadratic = np.sum(points * tx, axis=-1)
    h = q / r ** 2
    hp = qp / r ** 2 - 2 * q / r ** 3
    hpp = qpp / r ** 2 - 4 * qp / r ** 3 + 6 * q / r ** 4
    value = h * quadratic
    gradient = 2 * h[..., None] * tx + (hp * quadratic)[..., None] * e
    hessian = 2 * h[..., None, None] * tensor
    hessian += 2 * hp[..., None, None] * (tx[..., :, None] * e[..., None, :] + e[..., :, None] * tx[..., None, :])
    hessian += quadratic[..., None, None] * ((hpp - hp / r)[..., None, None] * ee + (hp / r)[..., None, None] * eye)
    return value, gradient, hessian


@lru_cache(maxsize=3)
def optical_receipt(name="cosmological_short_track"):
    data, engine, parameters = fixture(name)
    predictions, branch = engine.calculate(parameters)
    massratio = parameters["mass_msun"] / engine.ref_mass
    args = (massratio, parameters["shear"], parameters["compact_quad"],
            parameters["convergence"], parameters["flux_ratio"])
    centers = np.asarray(parameters["center_mas"]) + (data.epochs - data.t0)[:, None] * parameters["proper_motion_mas_yr"] + engine.parallax
    x = (predictions[:, :4].reshape(data.n, 2, 2) - centers[:, None, :]) / engine.theta
    base_p, base_g, base_h = engine.potential(x, *args)
    inverse = np.linalg.inv(np.eye(2) - base_h)
    direct = ScreenedExterior(M_msun=parameters["mass_msun"],
               z_l=data.geometry["z_l"], r0_pc=engine.r0, flux_ratio=parameters["flux_ratio"])
    expected_columns = []
    jet_errors = {"phase": 0., "gradient": 0., "hessian": 0.}
    fd_errors = {"phase": 0., "gradient": 0., "hessian": 0.} if name == "cosmological_short_track" else None
    for mode in range(3):
        unit = np.eye(3)[mode]
        actual = engine.potential(x, *args, boundary=unit)
        actual = (actual[0] - base_p, actual[1] - base_g, actual[2] - base_h)
        expected = _direct_cartesian_jets(direct, engine, x, mode)
        if fd_errors is not None:
            finite_difference = _cartesian_jets(lambda points: _direct_phase(direct, engine, points, mode), x)
            for i, key in enumerate(["phase", "gradient", "hessian"]):
                fd_errors[key] = max(fd_errors[key], float(np.linalg.norm(expected[i] - finite_difference[i]) / np.linalg.norm(expected[i])))
        # Matrix/vector norms avoid meaningless component-wise comparisons
        # at angular nodes while retaining a relative operator criterion.
        for i, key in enumerate(["phase", "gradient", "hessian"]):
            error = float(np.linalg.norm(actual[i] - expected[i]) / np.linalg.norm(expected[i]))
            jet_errors[key] = max(jet_errors[key], error)
        phase, gradient, hessian = expected
        dx = np.einsum("...ij,...j->...i", inverse, gradient)
        # Independently differentiate each Cartesian coordinate of the base
        # Hessian, rather than using the implementation's directional step.
        dh = np.zeros_like(base_h)
        step = 2e-5 * np.linalg.norm(x, axis=-1)
        for axis in range(2):
            delta = np.eye(2)[axis] * step[..., None]
            d_h = (engine.potential(x + delta, *args)[2]
                   - engine.potential(x - delta, *args)[2]) / (2 * step[..., None, None])
            dh += d_h * dx[..., axis, None, None]
        logs = np.einsum("...ij,...ji->...", inverse, hessian + dh)
        column = np.column_stack([(dx * engine.theta).reshape(data.n, 4),
                     logs[:, 0] - logs[:, 1], (phase[:, 0] - phase[:, 1]) * engine.time])
        expected_columns.append(data.whiten(column.ravel()))
    assert all(value < RTOL for value in jet_errors.values()), jet_errors
    if fd_errors is not None:
        assert all(value < RTOL for value in fd_errors.values()), fd_errors
    expected_s = np.column_stack(expected_columns)
    rng = np.random.default_rng(20261022)
    nuisance, _ = np.linalg.qr(rng.normal(size=(6 * data.n, 4)))
    full_nuisance = np.column_stack([nuisance, expected_s[:, 2]])
    q, _ = np.linalg.qr(full_nuisance)
    residual = expected_s[:, :2] - q @ (q.T @ expected_s[:, :2])
    singular = np.linalg.svd(residual, compute_uv=False)
    physics = assess_physics(data.raw, parameters, branch["impact_pc"])
    assert physics["allowed_physics_models"]["r1_boundary_conditional"], physics
    actual = assess_envelope(data, engine, parameters, nuisance, predictions, physics)
    error = _relative(actual["projected_singular_values_per_boundary_amplitude"], singular)
    assert error < RTOL, {"relative_error": error, "actual": actual, "expected_singular_values": singular.tolist()}
    return {"status": "pass", "annulus": name, "criterion_relative": RTOL,
            "direct_cartesian_chain_rule_potential_jet_relative_errors": jet_errors,
            "cartesian_finite_difference_crosscheck_relative_errors": fd_errors,
            "profiled_optical_singular_value_relative_error": error,
            "independent_profiled_singular_values": singular.tolist(),
            "envelope_assessment": actual,
            "scope": "unit linear operator only; no enlarged physical scalar state was lens-propagated"}


@pytest.mark.parametrize("name", ANNULI)
def test_runtime_scaling_against_direct_provider(name):
    assert runtime_receipt(name)["status"] == "pass"


@pytest.mark.parametrize("name", ANNULI)
def test_unit_potential_and_profiled_optical_response(name):
    assert optical_receipt(name)["status"] == "pass"


def test_nondefault_hubble_scale_is_consistent():
    raw, _ = make_example("cosmological_short_track", noise=False)
    raw["geometry"]["H0"] = 73.
    engine = LensEngine(raw, family="r1")
    assert engine._r1.ref.H0 == 73.
    direct = ScreenedExterior(M_msun=engine.ref_mass * .2, H0=73.,
               z_l=raw["geometry"]["z_l"], r0_pc=engine.r0, flux_ratio=.2)
    radius = np.array([.4, 1., 2.])
    alpha, alpha_prime, _ = direct.monopole_deflection(radius * engine.rE)
    actual = engine._r1.monopole(radius, .2, .2)
    expected = [alpha * engine.rE / (4 * engine.mref_pc),
                alpha_prime * engine.rE ** 2 / (4 * engine.mref_pc)]
    assert _relative(actual[1], expected[0]) < RTOL
    assert _relative(actual[2], expected[1]) < RTOL
    q, qp, qpp = direct.projected_quad(radius * engine.rE)
    expected = np.array([q, qp * engine.rE, qpp * engine.rE ** 2]) / (4 * engine.mref_pc)
    for actual_jet, expected_jet in zip(engine._r1.quadrupole(radius, .2, .2), expected):
        assert _relative(actual_jet, expected_jet) < RTOL


if __name__ == "__main__":
    print(json.dumps({name: {"runtime": runtime_receipt(name), "optics": optical_receipt(name)} for name in ANNULI}, indent=2, allow_nan=False))
