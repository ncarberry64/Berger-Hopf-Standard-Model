from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
import sympy as sp

from bhsm.interface.aether_cycle_sigma_coefficient_reconstruction_v15_10 import (
    COEFFICIENT_SELECTION_OUTCOME,
    EXACT_NEXT_OBJECT,
    FULL_BHSM_COMPLETE,
    USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    backward_route_audit_payload,
    completion_payload,
    critical_cycle_compatibility,
    critical_x,
    deterministic_json,
    homogeneous_cycle_inverse,
    materialize,
    normalized_sigma_response_jet,
    reconstruct_invariants_from_response_jet,
    reconstruction_interface_payload,
    retained_nonuniqueness_witness,
    retained_response_derivatives,
    schur_unreduce_canonical_quartic,
    sigma_generator_observables,
)


ROOT = Path(__file__).resolve().parents[1]


def test_claim_boundary_and_exact_next_object() -> None:
    assert FULL_BHSM_COMPLETE is False
    assert USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE is False
    assert COEFFICIENT_SELECTION_OUTCOME.endswith("NONUNIQUENESS")
    assert EXACT_NEXT_OBJECT.startswith("ACTION_OWNED_AETHER_CYCLE_TO_REGULAR_SIGMA_RESPONSE_JET_MAP")


def test_homogeneous_cycle_inverse_reproduces_supplied_formulas() -> None:
    a, h, hd = 2.0, 0.03, -0.01
    result = homogeneous_cycle_inverse(a, h, hd)
    denominator = 5.0 - 6.0 * a**2 * hd
    assert result["kappa1"] == pytest.approx(343.0 / (a**6 * denominator))
    assert result["kappa0"] == pytest.approx(
        7203.0 * (8.0 * a**2 * h**2 + 2.0 * a**2 * hd + 5.0)
        / (4.0 * a**8 * denominator)
    )


def test_cycle_inverse_requires_positive_retained_denominator() -> None:
    with pytest.raises(ValueError, match="positive-kappa1"):
        homogeneous_cycle_inverse(1.0, 0.0, 1.0)


def test_critical_cycle_forces_stationary_identity_locus() -> None:
    result = critical_cycle_compatibility(1.7)
    assert result["same_kappa1_requires"] == "Hdot=0"
    assert result["kappa1_residual"] == pytest.approx(0.0, abs=2e-14)
    assert result["kappa0_residual"] == pytest.approx(0.0, abs=2e-13)


def test_symbolic_critical_compatibility_is_exact() -> None:
    k1, a = sp.symbols("k1 a", positive=True, finite=True)
    hd = sp.symbols("hd", real=True, finite=True)
    inverse_at_critical = sp.Rational(343, 1) / (
        (sp.Rational(343, 5) / k1) * (5 - 6 * a**2 * hd)
    )
    equation = sp.factor(inverse_at_critical - k1)
    assert sp.solve(equation, hd) == [0]
    k0_at_turn = sp.Rational(7203, 4) / a**8
    identity_locus = sp.Rational(15, 4) * k1 * (7 / a**2)
    assert sp.simplify(
        (k0_at_turn - identity_locus).subs(k1, sp.Rational(343, 5) / a**6)
    ) == 0


def test_retained_same_g_integrability_identities() -> None:
    derivatives = retained_response_derivatives(1.3, 2.1, 0.7, -0.4, 3.2)
    assert derivatives["E_XXXX"] == 3.0
    assert derivatives["E_ssXXXX"] == pytest.approx(4.2)
    assert derivatives["g_from_X_integrability"] == pytest.approx(0.7)
    assert derivatives["g_from_X4_integrability"] == pytest.approx(0.7)


@pytest.mark.parametrize(
    "alpha,r,gamma,zsigma", [(-2.0, 0.4, 0.8, 0.7), (-1.0, 1.0, 1.0, 1.0), (-0.25, 2.2, 4.0, 3.0)]
)
def test_minimal_response_inverse_recovers_invariants(
    alpha: float, r: float, gamma: float, zsigma: float
) -> None:
    kappa1 = 1.6
    x0 = critical_x(kappa1)
    coupling = r * zsigma / kappa1
    a0 = alpha * coupling * kappa1 * x0
    g0 = gamma * coupling**2 * x0**4
    jet = normalized_sigma_response_jet(kappa1, x0, zsigma, coupling, a0, g0)
    recovered = reconstruct_invariants_from_response_jet(
        kappa1,
        x0,
        jet["S_sigma"],
        jet["dS_sigma_dX"],
        jet["lambda_sigma_bare_canonical"],
    )
    assert recovered == pytest.approx({"alpha": alpha, "r": r, "gamma": gamma})


def test_critical_response_inverse_simplifies_to_six_and_nine_fourths() -> None:
    k1 = 2.0
    x0 = critical_x(k1)
    alpha, r = -1.2, 0.9
    s0 = r * x0 * (alpha + 9.0 / 4.0)
    sx = 6.0 * r
    recovered = reconstruct_invariants_from_response_jet(k1, x0, s0, sx, 0.5)
    assert recovered["r"] == pytest.approx(r)
    assert recovered["alpha"] == pytest.approx(alpha)


def test_schur_unreduction_recovers_bare_quartic() -> None:
    result = schur_unreduce_canonical_quartic(
        physical_quartic=1.25,
        coupling=[1.0, 2.0],
        response_hessian=[[2.0, 0.0], [0.0, 4.0]],
    )
    assert result["Schur_backreaction_correction"] == pytest.approx(0.75)
    assert result["lambda_sigma_bare_canonical"] == pytest.approx(2.0)


def test_schur_unreduction_rejects_unstable_response_block() -> None:
    with pytest.raises(ValueError, match="positive"):
        schur_unreduce_canonical_quartic(1.0, [1.0], [[-1.0]])


def test_sigma_generator_extracts_mass_and_relative_normalization_flow() -> None:
    generator = np.array([[0.0, 1.0], [-2.5, -0.9]])
    fundamental = np.array([[1.0, 0.2], [0.1, 1.0]])
    result = sigma_generator_observables(
        fundamental, generator @ fundamental, hubble=0.1
    )
    assert np.asarray(result["generator"]) == pytest.approx(generator)
    assert result["S_sigma"] == pytest.approx(2.5)
    assert result["d_log_Zsigma_dt"] == pytest.approx(0.2)


def test_constructive_nonuniqueness_survives_partial_response_data() -> None:
    witness = retained_nonuniqueness_witness()
    assert witness["same_eta_metric_parent"] is True
    assert witness["same_sigma_zero_background_and_first_variation"] is True
    assert witness["A_and_B_same_normalized_quadratic_curvature_at_Xc"] is True
    assert witness["A_and_C_same_complete_quadratic_response_jet"] is True
    assert witness["A_and_C_different_nonlinear_response"] is True
    assert all(row["stable_at_Xc"] for row in witness["triples"].values())
    assert all(row["bounded_bare_quartic"] for row in witness["triples"].values())


def test_backward_search_does_not_relabel_metric_shape_as_sigma_response() -> None:
    audit = backward_route_audit_payload()
    assert audit["all_current_owned_routes_exhausted"] is True
    assert audit["new_selector_postulate_adopted"] is False
    metric_route = next(row for row in audit["routes"] if "v14_94" in row["route"])
    assert metric_route["sigma_selection"] is False
    assert "metric_shape" in metric_route["result"]


def test_reconstruction_interface_is_unique_but_not_currently_evaluable() -> None:
    payload = reconstruction_interface_payload()
    assert payload["inverse_is_algebraically_unique_when_jet_exists"] is True
    assert payload["absolute_Zsigma_required_for_invariants"] is False
    assert payload["physical_sigma_propagator_present_in_repository"] is False
    assert payload["X_derivative_present_in_repository"] is False
    assert payload["physical_nonlinear_sigma_response_present_in_repository"] is False
    assert payload["map_action_owned_and_evaluable"] is False


def test_completion_payload_passes_without_promoting_downstream_physics() -> None:
    payload = completion_payload()
    assert payload["validation_passed"] is True
    assert all(payload["validation"].values())
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["eta_to_sigma"]["physical_alpha_selected"] is False
    assert payload["eta_to_sigma"]["physical_a_sigma_selected"] is False
    assert payload["Hopf_child"].startswith("NOT_REACHED")
    assert payload["no_retuning_certificate"]["new_continuous_physical_parameters"] == []


def test_deterministic_materialization_and_committed_artifact(tmp_path: Path) -> None:
    encoded = deterministic_json(completion_payload())
    assert encoded.endswith("\n")
    assert "NaN" not in encoded
    assert json.loads(encoded)["version"] == "v15.10"
    first = materialize(tmp_path / "a")
    second = materialize(tmp_path / "b")
    assert hashlib.sha256(first.read_bytes()).digest() == hashlib.sha256(second.read_bytes()).digest()
    committed = ROOT / "artifacts" / first.name
    assert first.read_bytes() == committed.read_bytes()
