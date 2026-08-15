from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
import sympy as sp

from bhsm.interface.aether_coupled_skin_selector_v15_16 import (
    EXACT_NEXT_OBJECT,
    FULL_BHSM_COMPLETE,
    SELECTOR_RANK,
    completion_payload,
    coupled_bvp_identifiability_payload,
    coupled_normal_residuals,
    deterministic_json,
    eta_density,
    materialize,
    matter_normal_first_integral,
    naive_coefficient_variation_constraints,
    selector_rank,
    sigma_zero_selector_map,
    sigma_zero_selector_jacobian,
)


ROOT = Path(__file__).resolve().parents[1]


def test_symbolic_coupled_normal_euler_equations() -> None:
    p, pp, s, sp_, k1, g = sp.symbols("p pp s sp k1 g", real=True)
    x = p**2
    momentum = (1 + g * s**2) * (k1 + x**3) * p
    derivative = sp.diff(momentum, p) * pp + sp.diff(momentum, s) * sp_
    expected = (1 + g * s**2) * (k1 + 7 * x**3) * pp + 2 * g * s * sp_ * (k1 + x**3) * p
    assert sp.expand(derivative - expected) == 0


def test_numeric_normal_residuals_include_curved_measure() -> None:
    result = coupled_normal_residuals(
        eta_n=0.7,
        eta_nn=-0.2,
        sigma=0.3,
        sigma_n=-0.1,
        sigma_nn=0.4,
        expansion=0.25,
        kappa1=1.2,
        zsigma=0.8,
        g=0.6,
        a0=-0.4,
        g0=1.7,
    )
    x = 0.7**2
    f = eta_density(1.2, x)
    expected_sigma = -0.8 * (0.4 + 0.25 * -0.1) + (-0.4 + 2 * 0.6 * f) * 0.3 + 1.7 * 0.3**3
    assert result["sigma_Euler_residual"] == pytest.approx(expected_sigma)
    assert np.isfinite(result["eta_Euler_residual"])


def test_normal_first_integral_is_conserved_on_exact_sigma_kink() -> None:
    a0, g0, z = -1.0, 2.0, 1.0
    vacuum = np.sqrt(-a0 / g0)
    width = np.sqrt(2 * z / -a0)
    values = []
    for n in np.linspace(-4.0, 4.0, 41):
        tangent = np.tanh(n / width)
        sigma = vacuum * tangent
        sigma_n = vacuum * (1 - tangent**2) / width
        values.append(
            matter_normal_first_integral(
                eta_n=0.0,
                sigma=sigma,
                sigma_n=sigma_n,
                kappa1=1.0,
                zsigma=z,
                g=1.0,
                a0=a0,
                g0=g0,
            )
        )
    assert max(values) - min(values) < 2e-16


def test_available_physical_selector_jacobian_has_exact_rank_zero() -> None:
    assert np.count_nonzero(sigma_zero_selector_map(-1.0, 1.0, 3.0)) == 0
    assert np.count_nonzero(sigma_zero_selector_map(7.0, -2.0, 0.1)) == 0
    jacobian = sigma_zero_selector_jacobian()
    assert jacobian.shape == (6, 3)
    assert np.count_nonzero(jacobian) == 0
    assert selector_rank() == SELECTOR_RANK == 0
    payload = coupled_bvp_identifiability_payload()
    assert payload["selector_nullity"] == 3
    assert payload["full_metric_skin_BVP_eligible"] is False


def test_naive_global_coefficient_variation_kills_nonzero_skin() -> None:
    zero = naive_coefficient_variation_constraints(
        [0.0, 0.0], [0.0, 1.0], [1.0, 2.0], kappa1=1.0
    )
    wall = naive_coefficient_variation_constraints(
        [-1.0, 0.5], [0.0, 1.0], [1.0, 2.0], kappa1=1.0
    )
    assert zero["stationarity_forces_sigma_zero"] is True
    assert wall["all_nonnegative"] is True
    assert wall["dE_dA0"] > 0.0
    assert wall["dE_dG0"] > 0.0
    assert wall["stationarity_forces_sigma_zero"] is False


def test_completion_stops_at_proved_constitutive_obstruction() -> None:
    payload = completion_payload()
    assert FULL_BHSM_COMPLETE is False
    assert payload["validation_passed"] is True
    assert payload["coupled_skin_system"]["selector_rank"] == 0
    assert payload["A_B_C_full_skin_test"]["eligible_as_one_common_physical_inverse_problem"] is False
    assert payload["contact_impulse"] == "NOT_EVALUABLE"
    assert payload["no_retuning_certificate"]["new_continuous_coefficients"] == []
    assert EXACT_NEXT_OBJECT.startswith("ACTION_OWNED_AETHER_CYCLE_TO_REGULAR_SIGMA_RESPONSE_JET_MAP")


def test_deterministic_materialization_and_repository_artifact(tmp_path: Path) -> None:
    encoded = deterministic_json(completion_payload())
    assert encoded.endswith("\n")
    assert "NaN" not in encoded and "Infinity" not in encoded
    assert json.loads(encoded)["version"] == "v15.16"
    first = materialize(tmp_path / "first")
    second = materialize(tmp_path / "second")
    assert hashlib.sha256(first.read_bytes()).digest() == hashlib.sha256(second.read_bytes()).digest()
    assert first.read_bytes() == (ROOT / "artifacts" / first.name).read_bytes()
