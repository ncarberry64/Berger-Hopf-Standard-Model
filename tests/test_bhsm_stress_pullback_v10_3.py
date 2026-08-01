import numpy as np

from bhsm.interface.envelopment import stress_pullback_v10_3 as stress


def test_intrinsic_stress_lift_is_tangential():
    intrinsic = np.diag([2.0, 3.0])
    tangents = np.array([[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]])
    lifted = stress.tangential_stress_lift(intrinsic, tangents)
    normal = np.array([0.0, 0.0, 1.0])
    assert np.allclose(lifted[:2, :2], intrinsic)
    assert np.isclose(normal @ lifted @ normal, 0.0)
    assert np.allclose(lifted @ normal, 0.0)


def test_normal_force_occurs_in_distributional_divergence():
    row = stress.component_audit()
    assert row["normal_normal_component"] == 0
    assert "K^I_mu_nu" in row["divergence_identity"]
    assert row["current_shape_equation_present"] is False


def test_common_stress_payload_fails_closed_without_regulator_choice():
    payload = stress.stress_payload()
    assert payload["validation_passed"] is True
    assert payload["ownership"]["one_common_T8_total"] is None
    assert payload["ownership"]["distributional_conservation"] is False
    assert payload["verdict"] == stress.STRESS_VERDICT
