import numpy as np
import pytest

from bhsm.interface.completion.full_preimage_cap_inertia_operator_v14_84 import EXACT_NEXT_OBJECT
from bhsm.interface.completion.stationary_full_preimage_transport_no_go_v14_85 import (
    NEXT_EXECUTABLE_SUBOBJECT,
    brown_york_surface_momentum,
    canonical_slice_momentum,
    completion_payload,
    materialize,
    pure_repartition_inertia_witness,
    stationary_classical_transport_witness,
)


def test_pure_repartition_has_zero_total_action_inertia() -> None:
    for velocity in (-0.7, 0.0, 1.2):
        witness = pure_repartition_inertia_witness(velocity)
        assert abs(witness["finite_difference_inertia"]) < 1e-8
        assert witness["exact_total_action_independent_of_partition"] is True


def test_time_symmetric_slice_has_zero_canonical_and_brown_york_momentum() -> None:
    metric = np.diag([1.0, 2.0, 3.0])
    curvature = np.zeros((3, 3))
    normal = np.array([1.0, 0.0, 0.0])
    tangent = np.diag([0.0, 1.0, 1.0])
    assert np.allclose(canonical_slice_momentum(metric, curvature), 0.0)
    assert np.allclose(
        brown_york_surface_momentum(metric, curvature, normal, tangent), 0.0
    )


def test_brown_york_momentum_detects_non_time_symmetric_tangential_flux() -> None:
    metric = np.eye(3)
    curvature = np.array([[0.0, 0.4, -0.2], [0.4, 0.0, 0.0], [-0.2, 0.0, 0.0]])
    normal = np.array([1.0, 0.0, 0.0])
    tangent = np.diag([0.0, 1.0, 1.0])
    momentum = brown_york_surface_momentum(metric, curvature, normal, tangent)
    assert np.allclose(momentum, [0.0, -0.4, 0.2])


def test_invalid_brown_york_domain_fails_closed() -> None:
    with pytest.raises(ValueError):
        canonical_slice_momentum(np.diag([1.0, -1.0]), np.zeros((2, 2)))
    with pytest.raises(ValueError):
        brown_york_surface_momentum(np.eye(2), np.zeros((2, 2)), [2.0, 0.0], np.eye(2))


def test_stationary_classical_source_set_gives_zero_relative_transport_and_shear() -> None:
    witness = stationary_classical_transport_witness()
    assert witness["source_free_shift_L2_eigenvalue_R2"] == 5.0
    assert witness["source_free_shift_L3_eigenvalue_R2"] == 12.0
    assert witness["static_eta_YM_momentum_norm"] == 0.0
    assert witness["time_symmetric_brown_york_momentum_norm"] == 0.0
    assert witness["relative_transport_norm"] == 0.0
    assert witness["normalized_shear_operator_norm"] == 0.0


def test_payload_preserves_canonical_gate_and_narrows_executable_object() -> None:
    payload = completion_payload()
    assert payload["validation_passed"] is True
    assert payload["canonical_exact_next_object"] == EXACT_NEXT_OBJECT
    assert payload["next_executable_subobject"] == NEXT_EXECUTABLE_SUBOBJECT
    assert payload["source_audit"]["brown_york"]["status"] == "ZERO_MOMENTUM_NOT_ZERO_ENERGY_THEOREM"
    assert payload["v14_84_evaluation"]["Delta_A_on_present_branch"] == "ZERO"
    assert payload["completion_status"]["BHSM_complete"] is False
    assert payload["completion_status"]["USB_synchronization_eligible"] is False


def test_materialization_is_deterministic(tmp_path) -> None:
    first = materialize(tmp_path).read_bytes()
    second = materialize(tmp_path).read_bytes()
    assert first == second
