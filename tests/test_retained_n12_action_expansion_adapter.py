import numpy as np
import pytest

from bhsm.interface.aether_jax_full_local_action import STATE_DIMENSION
from bhsm.interface.retained_n12_action_expansion_adapter import (
    retained_n12_local_action_expansion,
)


def test_retained_n12_adapter_cross_checks_same_action_before_expansion() -> None:
    state = np.zeros(STATE_DIMENSION)
    frame = np.eye(STATE_DIMENSION)[:, :2]
    expansion, audit = retained_n12_local_action_expansion(
        state,
        frame,
        background_id="round-local-test",
        gate7_closed=False,
        provenance=("unit-test background",),
    )
    assert audit.validation_passed is True
    assert audit.gradient_relative_error < 2.0e-12
    assert audit.hessian_relative_error < 2.0e-12
    assert expansion.quadratic_matrix().shape == (2, 2)
    assert expansion.metadata()["action_version"] == "BHSM-AE-2.0.0"
    assert audit.metadata()["history_and_seam_terms_included"] is False


def test_retained_n12_local_adapter_does_not_promote_open_gate7_background() -> None:
    state = np.zeros(STATE_DIMENSION)
    frame = np.eye(STATE_DIMENSION)[:, :1]
    expansion, _ = retained_n12_local_action_expansion(
        state,
        frame,
        background_id="round-local-test",
        gate7_closed=False,
        provenance=("unit-test background",),
    )
    with pytest.raises(RuntimeError, match="Gate 7 is not closed"):
        expansion.require_physical_promotion()
