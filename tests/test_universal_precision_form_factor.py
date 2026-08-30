import numpy as np
import pytest

from bhsm.interface.universal_precision_form_factor import (
    MuonGMinus2Readout,
    project_electromagnetic_form_factors,
)


def test_form_factor_projection_recovers_synthetic_F1_F2() -> None:
    dirac = np.asarray([1.0, 0.0, 1.0j, 0.0])
    pauli = np.asarray([0.0, 2.0, 0.0, -1.0j])
    vertex = 1.0 * dirac + 0.00123 * pauli
    result = project_electromagnetic_form_factors(
        vertex, dirac, pauli, q_squared=0.0,
    )
    assert abs(result.F1 - 1.0) < 1.0e-14
    assert abs(result.F2 - 0.00123) < 1.0e-14
    assert result.relative_projection_residual < 1.0e-14


def test_muon_g_minus_two_promotion_is_fail_closed() -> None:
    dirac = np.asarray([1.0, 0.0])
    pauli = np.asarray([0.0, 1.0])
    factors = project_electromagnetic_form_factors(
        dirac + 0.002 * pauli, dirac, pauli, q_squared=0.0,
    )
    provisional = MuonGMinus2Readout(
        factors, "TEST-ACTION", "test-background", None,
        False, False, False,
    )
    with pytest.raises(RuntimeError, match="Gate7_closed_background"):
        provisional.anomalous_magnetic_moment()

    promoted = MuonGMinus2Readout(
        factors, "TEST-ACTION", "test-background", "test-renormalization",
        True, True, True,
    )
    assert promoted.anomalous_magnetic_moment() == pytest.approx(0.002)
    assert promoted.metadata()["experimental_target_used"] is False
