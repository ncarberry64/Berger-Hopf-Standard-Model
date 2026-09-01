import math

import pytest

from bhsm.interface.universal_event_observables import (
    FinalStateMomentum,
    FourMomentum,
    build_event_observables,
)


def event(final, *, complete=True, gate7=True):
    return build_event_observables(
        (FourMomentum(5.0, 0.0, 0.0, 5.0), FourMomentum(5.0, 0.0, 0.0, -5.0)),
        final,
        complete_final_state_ledger=complete,
        gate7_closed=gate7,
        action_version="TEST-ACTION",
        background_id="test-background",
        provenance=("unit-test action event",),
    )


def test_back_to_back_massless_event_observables() -> None:
    result = event((
        FinalStateMomentum("f1", "mode-a", FourMomentum(5.0, 5.0, 0.0, 0.0), True),
        FinalStateMomentum("f2", "mode-b", FourMomentum(5.0, -5.0, 0.0, 0.0), True),
    ))
    assert result.initial_invariant_mass == 10.0
    assert result.final_invariant_mass == 10.0
    assert result.scalar_visible_ht == 10.0
    assert result.missing_transverse_momentum == 0.0
    assert result.pairwise_invariant_masses["f1|f2"] == 10.0
    assert result.pairwise_delta_r_y["f1|f2"] == math.pi
    assert result.four_momentum_conservation_relative_residual == 0.0
    result.require_physical_promotion()


def test_invisible_state_generates_missing_transverse_momentum() -> None:
    result = event((
        FinalStateMomentum("visible", "mode-v", FourMomentum(5.0, 5.0, 0.0, 0.0), True),
        FinalStateMomentum("invisible", "mode-i", FourMomentum(5.0, -5.0, 0.0, 0.0), False),
    ))
    assert result.visible_state_ids == ("visible",)
    assert result.missing_transverse_px == -5.0
    assert result.missing_transverse_py == 0.0
    assert result.missing_transverse_momentum == 5.0


def test_nonconserving_or_incomplete_event_cannot_promote() -> None:
    result = event((
        FinalStateMomentum("f1", "mode-a", FourMomentum(4.0, 4.0, 0.0, 0.0), True),
        FinalStateMomentum("f2", "mode-b", FourMomentum(4.0, -4.0, 0.0, 0.0), True),
    ), complete=False, gate7=False)
    assert result.four_momentum_conservation_relative_residual > 0.0
    with pytest.raises(RuntimeError, match="Gate7_closed_background"):
        result.require_physical_promotion()


def test_spacelike_or_negative_energy_input_is_rejected() -> None:
    with pytest.raises(ValueError, match="nonnegative"):
        FourMomentum(-1.0, 0.0, 0.0, 0.0)
    with pytest.raises(ValueError, match="timelike or null"):
        event((
            FinalStateMomentum("bad", "mode", FourMomentum(1.0, 2.0, 0.0, 0.0), True),
        ))


def test_duplicate_final_state_ids_are_rejected() -> None:
    with pytest.raises(ValueError, match="unique"):
        event((
            FinalStateMomentum("same", "mode-a", FourMomentum(5.0, 5.0, 0.0, 0.0), True),
            FinalStateMomentum("same", "mode-b", FourMomentum(5.0, -5.0, 0.0, 0.0), True),
        ))
