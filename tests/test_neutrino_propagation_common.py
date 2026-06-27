from __future__ import annotations

from bhsm.interface.neutrino_propagation import STATUS_TAXONOMY
from bhsm.interface.neutrino_propagation.propagation_state import normalized_state


def test_status_taxonomy_is_explicit_and_propagation_state_normalizes() -> None:
    assert "CONDITIONAL_NUMERICAL_CLOSURE_CANDIDATE" in STATUS_TAXONOMY
    assert "OPEN_MISSING_NEUTRAL_SCALE" in STATUS_TAXONOMY
    state = normalized_state("test", (3.0, 4.0, 0.0), 0.5)
    assert state.amplitudes == (0.6, 0.8, 0.0)
    assert state.propagation_response == 0.5
    assert state.stopped is False


def test_zero_propagation_is_an_explicit_stopped_state() -> None:
    state = normalized_state("stopped", (1.0, 0.0, 0.0), 0.0)
    assert state.stopped is True
    assert state.propagation_response == 0.0
