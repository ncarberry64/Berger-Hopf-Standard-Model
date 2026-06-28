from __future__ import annotations

import pytest

from bhsm.interface.neutrino_propagation.curvature_threshold import (
    build_background_coupling,
    build_curvature_threshold,
    threshold_response,
)
from bhsm.interface.neutrino_propagation.neutral_kernel import load_neutral_kernel
from bhsm.interface.neutrino_propagation.propagation_state import normalized_state


def test_threshold_and_background_coupling_are_artifact_backed() -> None:
    kernel = load_neutral_kernel()
    threshold = build_curvature_threshold(kernel)
    background = build_background_coupling(kernel)
    assert threshold.value == pytest.approx(1.0 / 6.0)
    assert background.value == pytest.approx(1.0 / 3.0)
    assert threshold.status == "ESTABLISHED_ARTIFACT_BACKED"
    assert background.status == "ESTABLISHED_ARTIFACT_BACKED"


def test_threshold_response_is_deterministic_and_nonnegative() -> None:
    kernel = load_neutral_kernel()
    threshold = build_curvature_threshold(kernel)
    background = build_background_coupling(kernel)
    state = normalized_state("channel", (0.0, 1.0, 0.0), 1.0)
    first = threshold_response(kernel, state, threshold, background)
    second = threshold_response(kernel, state, threshold, background)
    assert first == second
    assert first[2] >= 0.0
