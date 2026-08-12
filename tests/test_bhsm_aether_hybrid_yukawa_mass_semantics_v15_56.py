import numpy as np

from bhsm.interface import aether_hybrid_yukawa_mass_semantics_v15_56 as mass


def test_wall_and_internal_overlaps_are_exact_identity_factors():
    assert mass.wall_normal_overlap_contract()["two_sheet_Higgs_overlap"] == 1.0
    result = mass.paired_mode_overlap_contract()
    for row in result["vertices"].values():
        assert row["paired_ledgers_identical"]
        assert np.allclose(row["fiber_invariant_Higgs_overlap"], np.eye(3))


def test_yukawa_wilson_operator_is_not_relabelled_geometric_spectrum():
    result = mass.yukawa_operator_factorization()
    assert result["Y_f_entries_fixed_by_wall_normalization"] is False
    assert result["Y_f_entries_fixed_by_round_fiber_Dirac_spectrum"] is False
    assert result["vertical_Dirac_levels_are_mass_matrix_entries"] is False


def test_selected_hybrid_background_has_zero_mass_operators():
    result = mass.reset_mass_spectrum()
    assert result["hybrid_background"]["H_star"] == 0.0
    for matrix in result["fermion_mass_matrices"].values():
        assert np.count_nonzero(matrix) == 0
    mixing = mass.mixing_semantics()
    assert mixing["canonical_triality_basis_transport"] == "I3"
    assert mixing["canonical_transport_is_a_physical_mixing_prediction"] is False


def test_payload_json_is_deterministic_and_valid():
    payload = mass.completion_payload()
    assert payload["validation_passed"]
    assert payload["claim_boundary"]["actual_reset_mass_spectrum_derived"]
    assert payload["claim_boundary"]["observed_fermion_masses_or_mixing_derived"] is False
    assert mass.deterministic_json(payload) == mass.deterministic_json(
        mass.completion_payload()
    )
