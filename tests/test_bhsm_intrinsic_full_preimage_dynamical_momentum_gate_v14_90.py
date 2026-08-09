import json

import numpy as np

from bhsm.interface.completion.intrinsic_full_preimage_dynamical_momentum_gate_v14_90 import (
    NEXT_CANONICAL_OBJECT,
    canonical_gravitational_momentum,
    canonical_variable_provenance,
    completion_payload,
    dynamical_schur_correction,
    extrinsic_curvature,
    homogeneous_cap_momentum_witness,
    materialize,
    oscillator_state_witness,
    reflection_relative_tensor,
    traceless_extrinsic_shear,
)


def test_canonical_provenance_separates_dynamical_and_multiplier_variables() -> None:
    rows = {row["variable"]: row for row in canonical_variable_provenance()}
    assert rows["spatial_metric_h_ij_on_M8_slice"]["action_owned"] is True
    assert rows["spatial_metric_h_ij_on_M8_slice"]["physical_dynamical_mode"].startswith("YES")
    assert rows["lapse_N"]["physical_dynamical_mode"] is False
    assert rows["shift_beta_i"]["physical_dynamical_mode"] is False
    assert rows["seam_embedding_X"]["canonical_momentum"] is None


def test_metric_velocity_is_distinct_from_shift() -> None:
    h = np.eye(2)
    velocity = np.diag([2.0, -2.0])
    assert np.allclose(extrinsic_curvature(h, velocity, 2.0), np.diag([0.5, -0.5]))
    assert np.allclose(extrinsic_curvature(h, velocity, 2.0, velocity), 0.0)


def test_p1_canonical_momentum_is_dynamic_and_time_symmetric_zero() -> None:
    h = np.eye(3)
    assert np.allclose(canonical_gravitational_momentum(h, np.zeros((3, 3))), 0.0)
    momentum = canonical_gravitational_momentum(h, 0.2 * h)
    assert np.linalg.norm(momentum) > 0.0
    assert np.allclose(momentum, -0.4 * h)


def test_dimension_correct_shear_is_traceless() -> None:
    h = np.diag([1.0, 2.0, 3.0, 4.0])
    k = np.diag([0.4, -0.1, 0.7, 0.2])
    shear = traceless_extrinsic_shear(h, k)
    assert abs(float(np.trace(np.linalg.solve(h, shear)))) < 1e-12
    assert np.allclose(traceless_extrinsic_shear(np.eye(4), 0.3 * np.eye(4)), 0.0)


def test_reflection_relative_tensor_distinguishes_common_and_counterpropagating() -> None:
    reflection = np.diag([-1.0, 1.0, 1.0])
    common = np.diag([0.2, -0.1, 0.4])
    assert np.allclose(reflection_relative_tensor(common, common, reflection), 0.0)
    relative = reflection_relative_tensor(common, -common, reflection)
    assert np.allclose(relative, 2.0 * common)


def test_explicit_homogeneous_p1_mode_is_common_not_relative() -> None:
    witness = homogeneous_cap_momentum_witness()
    assert witness["nonzero_common_expansion_momentum"] is True
    assert witness["zero_reflection_relative_momentum"] is True
    assert witness["traceless_shear_norm"] < 1e-12


def test_oscillator_existence_does_not_select_population() -> None:
    witness = oscillator_state_witness()
    assert witness["mode_exists_for_positive_frequency"] is True
    assert witness["classical_ground_state_amplitude"] == 0.0
    assert witness["cycle_mean_momentum"] == 0.0
    assert witness["cycle_mean_momentum_squared"] > 0.0


def test_static_schur_sign_and_dynamic_frequency_dependence() -> None:
    b = np.array([[0.3, -0.2], [0.1, 0.4]])
    k = np.diag([2.0, 3.0])
    static = dynamical_schur_correction(b, k)
    assert np.max(np.linalg.eigvalsh(static)) <= 1e-12
    dynamic = dynamical_schur_correction(b, k, frequency=0.5, inertia=np.eye(2))
    assert not np.allclose(dynamic, static)


def test_payload_and_materialization_preserve_claim_boundary(tmp_path) -> None:
    payload = completion_payload()
    assert payload["validation_passed"] is True
    assert payload["two_cap_momenta"]["physical_reduced_Pi_plus_minus"].startswith("UNDEFINED")
    assert payload["intrinsic_observable"]["B_dyn_L2"].startswith("UNDEFINED_PHYSICALLY")
    assert payload["degree_one_background"] == "NOT_DERIVED"
    assert payload["exact_next_object"] == NEXT_CANONICAL_OBJECT
    assert payload["completion_status"]["FULL_BHSM_COMPLETE"] is False
    target = materialize(tmp_path / "v14_90.json")
    assert json.loads(target.read_text(encoding="utf-8")) == payload
