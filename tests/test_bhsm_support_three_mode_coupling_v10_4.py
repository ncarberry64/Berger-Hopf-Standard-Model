from __future__ import annotations

from bhsm.interface.envelopment.support_orbit_gate_v10_4 import support_orbit_payload
from bhsm.interface.envelopment.support_three_mode_coupling_v10_4 import support_three_mode_payload


def test_three_mode_matrices_are_hermitian_ledgers_and_fail_closed():
    payload = support_three_mode_payload()
    assert payload["validation_passed"] is True
    assert payload["K_3m"][2][2]["status"] == "DERIVED_CONDITIONAL"
    assert payload["mixed_block_classification"]["K_CD"] == "OPEN"
    assert payload["mixed_block_classification"]["H_WD"] == "OPEN"
    assert payload["stable_eigenmode"] is None
    assert payload["seam_is_physical_mode"] is False
    assert payload["three_modes_identified_with_generations"] is False


def test_orbit_and_quantum_core_interfaces_remain_null():
    payload = support_orbit_payload()
    assert payload["validation_passed"] is True
    assert payload["orbit"] is None
    assert payload["physical_floquet_spectrum"] is None
    assert payload["quantum_core_interface"]["transition_amplitude"] is None
    assert payload["quantum_core_interface"]["quantum_mechanics_derived"] is False
