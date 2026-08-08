from math import isclose

import numpy as np
import pytest

from bhsm.interface.completion.full_preimage_cap_inertia_operator_v14_84 import (
    CHARGED_CURRENT_PROVENANCE_GATE,
    EXACT_NEXT_OBJECT,
    NONCENTRAL_CURRENT_GATE,
    completion_payload,
    materialize,
    normalized_shear_operator,
    operator_kinetic_decomposition,
    operator_parallel_sum,
    reflection_inertia_intertwining,
    round_reflection_inertia_factor,
    shear_softening_operator,
)


def noncommuting_inertias() -> tuple[np.ndarray, np.ndarray]:
    plus = np.diag([2.0, 3.0, 5.0]) + 0.2 * np.ones((3, 3))
    minus = np.diag([6.0, 4.0, 2.5]) + 0.1 * np.outer([1.0, -2.0, 0.5], [1.0, -2.0, 0.5])
    assert not np.allclose(plus @ minus, minus @ plus)
    return plus, minus


def test_operator_kinetic_identity_is_exact_for_noncommuting_inertias() -> None:
    plus, minus = noncommuting_inertias()
    result = operator_kinetic_decomposition(
        [0.3, -0.2, 0.7],
        [0.8, -0.4, 0.1],
        [[0.2, 1.0, 0.0], [-0.4, 0.1, 0.3], [0.0, -0.2, 0.5]],
        [[-0.3, 0.0, 0.7], [0.2, 0.4, 0.0], [0.1, -0.5, 0.2]],
        plus,
        minus,
    )
    assert isclose(result["original"], result["decomposed"], abs_tol=1e-12)


def test_parallel_sum_and_shear_operator_are_positive() -> None:
    plus, minus = noncommuting_inertias()
    parallel = operator_parallel_sum(plus, minus)
    assert np.allclose(parallel, parallel.T)
    assert np.min(np.linalg.eigvalsh(parallel)) > 0.0
    a_plus = np.array([[0.0, 1.0, 0.0], [-1.0, 0.0, 0.3], [0.0, -0.3, 0.0]])
    a_minus = np.diag([0.1, -0.2, 0.4])
    shear = shear_softening_operator(a_plus, a_minus, plus, minus)
    normalized = normalized_shear_operator(a_plus, a_minus, plus, minus)
    assert np.min(np.linalg.eigvalsh(shear)) >= -1e-12
    assert np.min(np.linalg.eigvalsh(normalized)) >= -1e-12


def test_reflection_is_an_intertwiner_before_cap_identification() -> None:
    plus = np.array([[3.0, 0.4, 0.0], [0.4, 2.0, 0.2], [0.0, 0.2, 4.0]])
    reflection = np.diag([1.0, -1.0, 1.0])
    minus = reflection @ plus @ reflection.T
    result = reflection_inertia_intertwining(plus, minus, reflection)
    assert result["intertwines"] is True
    assert np.allclose(result["pulled_minus"], plus)
    assert not np.allclose(minus, plus)


def test_round_reflection_derives_one_quarter_independent_of_absolute_inertia() -> None:
    for m0 in (0.2, 1.0, 17.0):
        result = round_reflection_inertia_factor(9, m0)
        assert isclose(result["nu"], 0.25, abs_tol=1e-12)
        assert isclose(result["ell2_isotropic_coefficient_per_R2"], 2.0 / 3.0, abs_tol=1e-12)
        assert result["spread"] < 1e-12


def test_invalid_operator_domains_fail_closed() -> None:
    with pytest.raises(ValueError):
        operator_parallel_sum(np.diag([1.0, 0.0]), np.eye(2))
    with pytest.raises(ValueError):
        operator_parallel_sum([[1.0, 0.2], [0.0, 1.0]], np.eye(2))
    with pytest.raises(ValueError):
        reflection_inertia_intertwining(np.eye(2), np.eye(2), [[1.0, 0.2], [0.0, 1.0]])


def test_payload_preserves_physical_and_flavor_gates() -> None:
    payload = completion_payload()
    assert payload["validation_passed"] is True
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT
    assert payload["open_gates"]["charged_current_kernel"] == CHARGED_CURRENT_PROVENANCE_GATE
    assert payload["open_gates"]["noncentral_left_handed_current"] == NONCENTRAL_CURRENT_GATE
    assert payload["physical_transport_gate"]["ADM_coordinate_shift_is_physical_shear"] is False
    assert payload["reflection_theorem"]["actual_reflection_symmetric_degree_one_background_verified"] is False
    assert payload["completion_status"]["cap_inertia_gate"] == "OPEN"
    assert payload["completion_status"]["BHSM_complete"] is False
    assert payload["completion_status"]["USB_synchronization_eligible"] is False


def test_materialization_is_deterministic(tmp_path) -> None:
    first = materialize(tmp_path).read_bytes()
    second = materialize(tmp_path).read_bytes()
    assert first == second
