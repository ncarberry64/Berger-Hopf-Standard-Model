import numpy as np
import pytest

from bhsm.interface.completion.full_preimage_cap_inertia_operator_v14_84 import EXACT_NEXT_OBJECT
from bhsm.interface.completion.longitudinal_threading_coexact_rotation_gate_v14_86 import (
    NEXT_EXECUTABLE_SUBOBJECT,
    completion_payload,
    exact_coexact_pairing_by_parts,
    materialize,
    reflection_decompose_pair,
    reflection_equivariant_response,
    v6_18_ell2_threading_witness,
)


def test_v6_18_recalled_ell2_source_is_nonzero_reflection_odd_and_nine_dimensional() -> None:
    witness = v6_18_ell2_threading_witness()
    assert witness["multiplicity"] == 9.0
    assert witness["upper_response"] == pytest.approx(-witness["lower_response"])
    assert witness["cap_difference"] != 0.0
    assert witness["threading_kernel_eigenvalue"] == pytest.approx(-16.0)
    assert witness["coexact_projection_norm"] == 0.0
    assert witness["vorticity_norm"] == 0.0


def test_closed_domain_exact_coexact_hodge_pairing_vanishes() -> None:
    assert exact_coexact_pairing_by_parts([1.0, -0.2, 0.4], [0.0, 0.0, 0.0]) == 0.0
    assert exact_coexact_pairing_by_parts([1.0, 2.0], [0.3, -0.1]) != 0.0
    with pytest.raises(ValueError):
        exact_coexact_pairing_by_parts([1.0], [0.0], [-1.0])


def test_reflection_pair_decomposition_recovers_even_and_odd_data() -> None:
    reflection = np.diag([1.0, -1.0, 1.0])
    plus = np.array([2.0, 3.0, -1.0])
    minus = reflection @ np.array([2.0, -3.0, -1.0])
    result = reflection_decompose_pair(plus, minus, reflection)
    assert np.allclose(result["even"], [2.0, 0.0, -1.0])
    assert np.allclose(result["odd"], [0.0, 3.0, 0.0])


def test_even_source_cannot_generate_odd_linear_response_under_equivariant_operator() -> None:
    reflection = np.diag([1.0, -1.0, 1.0, -1.0])
    operator = np.diag([2.0, 3.0, 4.0, 5.0])
    even = np.array([0.4, 0.0, -0.3, 0.0])
    result = reflection_equivariant_response(operator, reflection, even)
    assert np.allclose(result["source_odd"], 0.0)
    assert np.allclose(result["response_odd"], 0.0)


def test_noncommuting_reflection_response_fails_closed() -> None:
    reflection = np.diag([1.0, -1.0])
    with pytest.raises(ValueError):
        reflection_equivariant_response([[2.0, 0.3], [0.3, 2.0]], reflection, [1.0, 0.0])


def test_payload_preserves_physical_and_flavor_boundaries() -> None:
    payload = completion_payload()
    assert payload["validation_passed"] is True
    assert payload["canonical_exact_next_object"] == EXACT_NEXT_OBJECT
    assert payload["next_executable_subobject"] == NEXT_EXECUTABLE_SUBOBJECT
    assert payload["representation_match_boundary"]["abstract_round_representation_matches"] is True
    assert payload["representation_match_boundary"]["physical_parent_action_incidence_identifying_fold_q_with_shape_Q"] is False
    assert payload["completion_status"]["longitudinal_as_rotation_route"] == "CLOSED_AS_NO_GO"
    assert payload["completion_status"]["BHSM_complete"] is False
    assert payload["completion_status"]["USB_synchronization_eligible"] is False


def test_materialization_is_deterministic(tmp_path) -> None:
    first = materialize(tmp_path).read_bytes()
    second = materialize(tmp_path).read_bytes()
    assert first == second
