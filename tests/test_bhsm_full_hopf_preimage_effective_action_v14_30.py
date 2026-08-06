from __future__ import annotations

from pathlib import Path

import numpy as np
from scipy.linalg import expm

from bhsm.interface.completion.full_hopf_preimage_effective_action_v14_30 import (
    CAMPAIGN_OBJECT,
    EXACT_NEXT_OBJECT,
    OUTCOME_D,
    completion_payload,
    dtn_low_energy_coefficients,
    dtn_schur_payload,
    dtn_symbol,
    fiber_mode_rows,
    fiber_spectrum_payload,
    full_preimage_density_factor,
    full_preimage_diagram,
    low_energy_matching_payload,
    matrix_dtn,
    measure_hessian_payload,
    parent_constant_background_hessian_eigenvalue,
    peter_weyl_cutoff_dimension,
    prior_work_recall_payload,
    quadratic_chain_hessian,
    representation_obstruction_payload,
    schur_complement,
)


def test_01_full_preimage_dimension_and_commutative_diagram():
    diagram = full_preimage_diagram()
    assert diagram["C_tilde"]["dimension"] == 8
    assert diagram["Sigma_tilde"]["dimension"] == 7
    assert diagram["commutative_identity"].startswith("Pi=")


def test_02_physical_color_pullback_does_not_create_eta_bundle_morphism():
    payload = representation_obstruction_payload()
    assert payload["validation_passed"]
    assert payload["physical_covariant_derivative_on_retained_eta"] is None
    assert payload["classification"] == "ACTION_OWNERSHIP_AND_BUNDLE_PROVENANCE_MISMATCH_UNDER_THE_RETAINED_ACTION"


def test_02a_full_recall_recovers_the_laid_path_without_promoting_it():
    payload = prior_work_recall_payload()
    assert payload["validation_passed"]
    assert "triality branching" in payload["composition_available"]
    assert "Pi^*P_color" in payload["missing_commuting_square"]
    assert payload["validation"]["USB_not_searched_or_modified_under_the_campaign_rule"]


def test_03_parent_and_candidate_tangent_ranks_do_not_match():
    assert representation_obstruction_payload()["vacuum_tangent_counts"] == {
        "retained_parent_eta": 7,
        "v14_29_coset_eta": 6,
    }


def test_04_round_fiber_spectrum_eigenvalues_and_multiplicities():
    rows = fiber_mode_rows(5)
    for row in rows:
        j = row["two_j"] / 2
        assert np.isclose(row["eigenvalue"], j * (j + 1))
        assert row["multiplicity"] == int(2 * j + 1)


def test_05_berger_splitting_depends_on_right_weight():
    rows = [row for row in fiber_mode_rows(2, L1=0.7, L2=1.2) if row["two_j"] == 2]
    values = {row["two_m"]: row["eigenvalue"] for row in rows}
    assert values[-2] == values[2]
    assert values[0] != values[2]


def test_06_peter_weyl_cutoff_dimension_counts_all_matrix_elements():
    assert peter_weyl_cutoff_dimension(0) == 1
    assert peter_weyl_cutoff_dimension(2) == 1 + 4 + 9


def test_07_fiber_modes_do_not_receive_unowned_su3_labels():
    payload = fiber_spectrum_payload()
    assert payload["validation_passed"]
    assert payload["degree_one_eta_mode"] is None
    assert payload["SU3_triplet_antitriplet_modes"] is None
    assert all(row["SU3_representation"] is None for row in payload["rows"])


def test_08_full_preimage_measure_contains_physical_fiber_volume():
    assert np.isclose(full_preimage_density_factor(0.0, 2.0), 16 * np.pi**2 * 8)
    assert full_preimage_density_factor(0.3) < full_preimage_density_factor(0.0)


def test_09_constant_background_parent_hessian_is_positive_and_additive():
    value = parent_constant_background_hessian_eigenvalue(2.0, 3.0, 4.0, weight=1.5, kappa1=2.0)
    assert value == 27.0


def test_10_parent_hessian_preserves_p8_claim_boundary():
    payload = measure_hessian_payload()
    assert payload["validation_passed"]
    assert payload["validation"]["p8_zero_in_constant_background_quadratic_hessian"]
    assert payload["full_preimage_stationary_background"] is None
    assert payload["self_adjoint_domain"] is None


def test_11_scalar_dtn_symbol_is_positive_and_zero_only_at_zero_gap_and_momentum():
    assert dtn_symbol(0.0, 0.0, 1.0) == 0.0
    assert dtn_symbol(0.2, 0.0, 1.0) > 0.0
    assert dtn_symbol(0.0, 0.7, 1.0) > 0.0


def test_12_dtn_low_energy_series_matches_exact_symbol():
    mass, width = 1.1, 0.8
    coefficients = dtn_low_energy_coefficients(mass, width)
    for z in (1e-5, 3e-5, 1e-4):
        approximation = coefficients["mass_term"] + coefficients["Z"] * z + coefficients["c4"] * z**2
        assert abs(dtn_symbol(z, mass**2, width) - approximation) < 2e-12


def test_13_massless_dtn_series_has_no_mass_and_positive_Z():
    coefficients = dtn_low_energy_coefficients(0.0, 0.9)
    assert coefficients["mass_term"] == 0.0
    assert coefficients["Z"] > 0.0
    assert coefficients["c4"] < 0.0


def test_14_matrix_dtn_is_self_adjoint_and_gauge_covariant():
    h = np.array([[2.0, 0.3j], [-0.3j, 1.0]], complex)
    u = expm(np.array([[0.0, 0.41], [-0.41, 0.0]], complex))
    transformed = u.conj().T @ h @ u
    lhs = matrix_dtn(transformed, 0.6)
    rhs = u.conj().T @ matrix_dtn(h, 0.6) @ u
    assert np.allclose(lhs, lhs.conj().T, atol=1e-12)
    assert np.allclose(lhs, rhs, atol=1e-12)


def test_15_schur_complement_equals_explicit_bulk_minimization():
    h = quadratic_chain_hessian(8, 0.9, 0.15)
    heff = schur_complement(h, 1)
    q = np.array([0.37])
    bulk = -np.linalg.solve(h[1:, 1:], h[1:, :1] @ q)
    full = np.concatenate((q, bulk))
    assert np.isclose(full @ h @ full, q @ heff @ q)


def test_16_naive_boundary_block_differs_from_correct_schur_complement():
    payload = dtn_schur_payload()
    assert payload["validation_passed"]
    assert payload["computed_chain_Hpp"] != payload["computed_chain_Heff"]


def test_17_matching_table_audits_every_required_operator_without_tuning():
    payload = low_energy_matching_payload()
    assert payload["validation_passed"]
    assert len(payload["matching_table"]) == 8
    assert payload["classification"] == "NO_MATCH"
    assert payload["primary_outcome"] == OUTCOME_D


def test_18_v14_29_current_remains_conditional_and_no_vector_pole_is_added():
    payload = low_energy_matching_payload()
    assert payload["validation"]["local_current_sign_preserved"]
    assert payload["validation"]["selector_and_pure_wall_zero_current_preserved"]
    assert payload["validation"]["no_new_vector_pole_preserved"]


def test_19_completion_gate_stops_at_the_first_physical_obstruction():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["campaign_object"] == CAMPAIGN_OBJECT
    assert payload["primary_verdict"] == OUTCOME_D
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT
    assert payload["BHSM_complete"] is False
    assert payload["FR_Dirac_matching_gate"] == "NOT_ELIGIBLE"


def test_20_required_full_preimage_reports_exist_and_record_outcome_d():
    root = Path(__file__).parents[1] / "docs"
    names = (
        "BHSM_HOPF_SECTION_AND_BASIC_FIELD_OBSTRUCTION_THEOREM.md",
        "BHSM_FULL_HOPF_PREIMAGE_EFFECTIVE_ACTION_PROOF.md",
        "BHSM_ETA_FIBER_MODE_SPECTRUM.md",
        "BHSM_GAUGE_COVARIANT_DIRICHLET_TO_NEUMANN_MAP.md",
        "BHSM_V14_29_LOW_ENERGY_MATCHING_AUDIT.md",
        "BHSM_FULL_RECALL_PATH_COMPOSITION_AUDIT_v14_30.md",
    )
    for name in names:
        text = (root / name).read_text(encoding="utf-8")
        assert "v14.30" in text
    assert OUTCOME_D in (root / "BHSM_V14_29_LOW_ENERGY_MATCHING_AUDIT.md").read_text(encoding="utf-8")
