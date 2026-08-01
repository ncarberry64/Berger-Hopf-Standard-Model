import numpy as np
import pytest

from bhsm.interface.envelopment import three_mode_interference_v10_3 as interference


def test_supplied_Hermitian_form_contains_phase_interference():
    v = np.array([1, 1j, 0], dtype=complex)
    operator = np.array([[2, 1j, 0], [-1j, 3, 0], [0, 0, 4]], dtype=complex)
    assert interference.hermitian_energy(v, operator) == pytest.approx(3.0)


def test_non_Hermitian_form_is_rejected_and_no_current_coefficients_exist():
    with pytest.raises(ValueError):
        interference.hermitian_energy(np.ones(3), np.array([[1, 1, 0], [0, 1, 0], [0, 0, 1]]))
    payload = interference.interference_payload()
    assert payload["M_env"] is None
    assert payload["arbitrary_coefficients_inserted"] is False
    assert payload["physical_output_emitted"] is False
