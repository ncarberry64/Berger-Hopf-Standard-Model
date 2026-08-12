from __future__ import annotations

import json

import numpy as np

from bhsm.interface.aether_collective_symplectic_manifold_v15_22 import (
    FULL_BHSM_COMPLETE,
    collective_legendre_rank_certificate,
    collective_legendre_two_form,
    completion_payload,
    configuration_only_symplectic_audit,
    integrated_sigma_instability_strength,
    materialize,
    quadratic_round_branch_geometry,
    round_branch_quotient_dichotomy_payload,
    sigma_response_operator,
)


def test_collective_two_form_is_antisymmetric() -> None:
    form = collective_legendre_two_form(
        [[2.0, 0.2], [0.2, 1.3]], [[0.0, 0.7], [-0.7, 0.0]]
    )
    assert np.allclose(form, -form.T)


def test_legendre_rank_equivalence_regular_and_singular() -> None:
    regular = collective_legendre_rank_certificate([[2.0, 0.1], [0.1, 1.0]])
    singular = collective_legendre_rank_certificate(
        [[1.0, 0.0], [0.0, 0.0]], [[0.0, 3.0], [-3.0, 0.0]]
    )
    assert regular["Legendre_regular"]
    assert regular["two_form_rank"] == 4
    assert not singular["Legendre_regular"]
    assert singular["two_form_rank"] < 4
    assert regular["rank_equivalence_holds"]
    assert singular["rank_equivalence_holds"]


def test_configuration_only_form_is_not_phase_space_test() -> None:
    audit = configuration_only_symplectic_audit(3)
    assert audit["physical_phase_dimension_expected"] == 6
    assert audit["Q_only_form_maximum_rank"] == 2
    assert audit["Q_only_rank_equals_required_phase_rank"] is False


def test_round_d_is_singular_while_s_regularizes_even_map() -> None:
    origin = quadratic_round_branch_geometry(0.0, second_response_norm=2.5)
    flank = quadratic_round_branch_geometry(0.3, second_response_norm=2.5)
    assert origin["d_map_immersion_rank"] == 0
    assert origin["d_phase_rank"] == 0
    assert origin["s_phase_rank"] == 2
    assert flank["d_map_immersion_rank"] == 1
    assert flank["d_phase_rank"] == 2


def test_round_orbifold_choice_is_not_declared() -> None:
    result = round_branch_quotient_dichotomy_payload()
    assert result["background_cap_exchange_present"]
    assert result["moving_covariant_reflection_present"] is False
    assert result["which_case_retained_action_selects"] is None
    assert result["orbifold_claim_allowed"] is False


def test_sigma_response_operator_recovers_gI_and_allows_anisotropy() -> None:
    uniform = sigma_response_operator(np.diag([2.0, 3.0]), np.diag([3.2, 4.8]))
    anisotropic = sigma_response_operator(np.eye(2), np.diag([1.0, 2.0]))
    assert uniform["is_scalar_multiple_of_identity"]
    assert np.isclose(uniform["scalar_projection"], 0.8)
    assert not anisotropic["is_scalar_multiple_of_identity"]
    assert anisotropic["eigenvalues"] == [0.5, 1.0]


def test_integrated_instability_is_zero_below_and_positive_above_threshold() -> None:
    below = integrated_sigma_instability_strength(
        supercriticality=0.4,
        critical_radius=2.0,
        coupling_g=0.8,
        static_curvature=1.0,
        sigma_inertia=1.0,
    )
    above = integrated_sigma_instability_strength(
        supercriticality=1.0,
        critical_radius=2.0,
        coupling_g=2.0,
        static_curvature=1.0,
        sigma_inertia=1.0,
    )
    assert below["integrated_strength"] == 0.0
    assert above["integrated_strength"] > 0.0
    assert above["approximate_linear_amplification_factor"] > 1.0
    assert above["physical_enclosure_claim"] is False


def test_completion_fails_closed_at_the_nonround_state_solution() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert FULL_BHSM_COMPLETE is False
    assert payload["physical_canonical_separation_mode_derived"] is False
    assert payload["collective_state_manifold_contract"]["actual_Phi_star_solution"] is None
    assert len(payload["Hindsight_20_20"]["OPEN"]) == 1


def test_materialization_is_deterministic(tmp_path) -> None:
    path = materialize(tmp_path)
    first = path.read_bytes()
    second = materialize(tmp_path).read_bytes()
    assert first == second
    payload = json.loads(first)
    assert payload["validation_passed"]
    assert payload["FULL_BHSM_COMPLETE"] is False
