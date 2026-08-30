import numpy as np
import pytest

from bhsm.interface.bhsm_yukawa_vertices import (
    ActionYukawaMatrix,
    fermion_mass_response,
    relative_left_mixing,
)


def yukawa(channel: str, matrix: np.ndarray) -> ActionYukawaMatrix:
    return ActionYukawaMatrix(
        channel=channel,
        matrix=matrix,
        action_version="BHSM-TEST",
        background_id="background",
        hs_direction_id="same-action-lowest-HS-mode",
        provenance=("same-action HS Hessian",),
        selected_by_same_action_hessian=True,
    )


def test_mass_is_hs_response_times_action_selected_yukawa() -> None:
    source = yukawa("up", np.diag([1.0, 2.0, 4.0]))
    result = fermion_mass_response(source, 3.0)
    np.testing.assert_allclose(np.sort(result.singular_masses), [3.0, 6.0, 12.0])
    assert result.simple_spectrum is True
    assert source.invariant_monomial == "Q_H_u_c"


def test_ckm_type_readout_is_relative_left_action_frame() -> None:
    angle = 0.3
    rotation = np.asarray([
        [np.cos(angle), -np.sin(angle), 0.0],
        [np.sin(angle), np.cos(angle), 0.0],
        [0.0, 0.0, 1.0],
    ])
    up = fermion_mass_response(yukawa("up", np.diag([4.0, 2.0, 1.0])), 1.0)
    down = fermion_mass_response(
        yukawa("down", rotation @ np.diag([5.0, 2.5, 1.5])),
        1.0,
    )
    mixing = relative_left_mixing(up, down)
    np.testing.assert_allclose(mixing.conj().T @ mixing, np.eye(3), atol=2.0e-15)
    np.testing.assert_allclose(np.abs(mixing), np.abs(rotation), atol=2.0e-15)


def test_unselected_or_fitted_yukawa_matrix_is_rejected() -> None:
    with pytest.raises(ValueError, match="same-action HS Hessian"):
        ActionYukawaMatrix(
            channel="charged_lepton",
            matrix=np.eye(3),
            action_version="BHSM-TEST",
            background_id="background",
            hs_direction_id="chosen",
            provenance=("guess",),
            selected_by_same_action_hessian=False,
        )


def test_degenerate_response_does_not_define_unique_mixing() -> None:
    degenerate = fermion_mass_response(yukawa("up", np.eye(3)), 1.0)
    simple = fermion_mass_response(yukawa("down", np.diag([1.0, 2.0, 3.0])), 1.0)
    with pytest.raises(RuntimeError, match="degenerate"):
        relative_left_mixing(degenerate, simple)
