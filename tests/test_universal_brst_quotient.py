import numpy as np
import pytest

from bhsm.interface.universal_brst_quotient import build_brst_physical_quotient


def test_constraint_and_gauge_directions_are_removed_without_inversion() -> None:
    constant = np.diag([0.0, 2.0, 3.0, 5.0])
    linear = np.diag([0.0, 1.0, 1.0, 1.0])
    constraints = np.asarray([[0.0, 1.0, 0.0, 0.0]])
    generators = np.asarray([[1.0], [0.0], [0.0], [0.0]])
    gauge_condition = np.asarray([[1.0, 0.0, 0.0, 0.0]])
    result = build_brst_physical_quotient(
        constant,
        linear,
        constraints,
        generators,
        gauge_condition,
        action_version="BHSM-TEST",
        background_id="background",
        gauge_condition_id="action-owned-test-gauge",
        provenance=("linearized master action",),
    )
    result.require_regular_brst_quotient()
    assert result.physical_dimension == 2
    np.testing.assert_allclose(np.linalg.eigvalsh(result.quotient_constant), [3.0, 5.0])
    assert result.metadata()["explicit_kinetic_inverse_formed"] is False


def test_singular_ghost_operator_blocks_brst_promotion() -> None:
    result = build_brst_physical_quotient(
        np.diag([0.0, 2.0]),
        np.diag([0.0, 1.0]),
        np.zeros((0, 2)),
        np.asarray([[1.0], [0.0]]),
        np.asarray([[0.0, 1.0]]),
        action_version="BHSM-TEST",
        background_id="background",
        gauge_condition_id="singular-gauge",
        provenance=("unit test",),
    )
    with pytest.raises(RuntimeError, match="Faddeev_Popov"):
        result.require_regular_brst_quotient()
