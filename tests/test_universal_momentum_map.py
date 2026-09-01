import numpy as np
import pytest

from bhsm.interface.universal_momentum_map import (
    ActionMomentumMap,
    mandelstam_invariants,
)


def momentum_map(promoted: bool = True) -> ActionMomentumMap:
    return ActionMomentumMap(
        inverse_metric=np.diag([1.0, -1.0, -1.0, -1.0]),
        action_version="BHSM-TEST",
        background_id="background",
        chart_id="local-orthonormal-frame",
        provenance=("frozen background tetrad",),
        derived_from_frozen_background=promoted,
    )


def test_massless_center_of_momentum_mandelstam_identity() -> None:
    energy = 2.0
    angle = 0.4
    p1 = np.asarray([energy, 0.0, 0.0, energy])
    p2 = np.asarray([energy, 0.0, 0.0, -energy])
    p3 = np.asarray([energy, energy * np.sin(angle), 0.0, energy * np.cos(angle)])
    p4 = p1 + p2 - p3
    result = mandelstam_invariants(
        momentum_map(),
        (p1, p2),
        (p3, p4),
        mass_squared=(0.0, 0.0, 0.0, 0.0),
    )
    assert result.s == 16.0
    assert result.momentum_conservation_residual == 0.0
    assert result.on_shell_sum_rule_residual < 1.0e-14


def test_provisional_metric_cannot_define_physical_channel_invariants() -> None:
    zero = np.zeros(4)
    with pytest.raises(RuntimeError, match="frozen BHSM background"):
        mandelstam_invariants(momentum_map(False), (zero, zero), (zero, zero))
