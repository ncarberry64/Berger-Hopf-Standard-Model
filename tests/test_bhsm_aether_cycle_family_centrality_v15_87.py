import numpy as np

from bhsm.interface.aether_cycle_family_centrality_v15_87 import (
    completion_payload,
    cycle_family_operator,
    locality_and_triality_intersection,
)


def test_locality_intersected_with_triality_forces_centrality():
    result = locality_and_triality_intersection()
    assert result["intersection"] == "Diagonal(3,C)_intersection_C[C3]=C*I3"
    assert result["generic_diagonal_commutator_norm"] > 0.0
    assert result["central_witness_commutator_norm"] < 1.0e-13
    assert result["off_diagonal_triality_intertwiner_present"] is False


def test_one_cycle_yukawa_is_nonzero_family_central_but_mass_is_zero():
    result = cycle_family_operator()
    matrix = np.asarray(result["family_matrix"])
    assert np.allclose(matrix, result["cycle_canonical_Yukawa"] * np.eye(3))
    assert result["cycle_canonical_Yukawa"] > 23.0
    assert result["rank"] == 3
    assert np.allclose(result["mass_matrix_on_symmetric_cycle"], np.zeros((3, 3)))


def test_payload_is_valid_and_does_not_insert_family_data():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["claim_boundary"]["family_centrality_derived"]
    assert payload["claim_boundary"]["family_hierarchy_predicted_by_current_action"] is False
    assert payload["no_family_hierarchy_theorem"]["new_family_coefficient_inserted"] is False
