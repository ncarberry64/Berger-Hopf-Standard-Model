import numpy as np

from bhsm.interface.aether_event_coefficient_naturality_v15_63 import (
    circulant_yukawa,
    completion_payload,
    cyclic_shift_matrix,
    deterministic_json,
    event_naturality_theorem,
    family_symmetry_parameter_count,
    minimal_microscopic_law_signature,
)


def test_general_circulant_yukawa_commutes_with_owned_C3_shift():
    p = cyclic_shift_matrix()
    y = circulant_yukawa(1 + 2j, 3 - 5j, -7 + 11j)
    assert np.linalg.norm(p @ y - y @ p) < 1.0e-13
    assert not np.allclose(y, np.eye(3) * y[0, 0])


def test_owned_C3_and_stronger_central_parameter_counts_are_distinct():
    result = family_symmetry_parameter_count()
    dimensions = result["total_intrinsic_M4_real_dimensions"]
    assert dimensions == {
        "unrestricted": 75,
        "owned_C3_invariant": 27,
        "stronger_family_central_kill_screen": 11,
    }
    assert result["family_centrality_follows_from_owned_C3"] is False


def test_event_naturality_leaves_the_full_constant_coefficient_fiber():
    result = event_naturality_theorem()
    assert result["continuous_event_tangent_dimension"] == 0
    assert result["constant_value_selected_by_naturality"] is False
    assert result["natural_assignment_real_dimension"] == 11


def test_minimal_extension_is_one_selection_law_not_hidden_constants():
    result = minimal_microscopic_law_signature()
    assert result["new_foundational_object_count"] == 1
    assert result["eleven_independent_constants_required_as_new_primitives"] is False
    assert result["arbitrary_quadratic_center_allowed"] is False
    assert result["explicit_formula_derived_from_current_BHSM_structure"] is False


def test_payload_is_deterministic_and_fail_closed():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["FULL_BHSM_COMPLETE"] is False
    first = deterministic_json(payload)
    second = deterministic_json(completion_payload())
    assert first == second
    assert "NaN" not in first and "Infinity" not in first
