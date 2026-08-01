from __future__ import annotations

from bhsm.interface.envelopment.three_mode_action_v10_4 import ACTION_VERDICT, three_mode_action_payload
from bhsm.interface.envelopment.three_mode_orbit_v10_4 import ORBIT_VERDICT, orbit_payload


def test_three_mode_action_stays_rank_two_and_types_every_missing_block():
    payload = three_mode_action_payload()
    assert payload["mode_status"]["q_D"] == "ABSENT_AFTER_CONSTRAINT_REDUCTION"
    assert payload["physical_rank"] == 2
    assert payload["target_rank_three_reached"] is False
    assert payload["K_0"][0][1]["status"] == "UNDEFINED_CROSS_DOMAIN"
    assert payload["K_0"][2][2]["status"] == "OPEN"
    assert payload["complete_common_source"] is None
    assert payload["verdict"] == ACTION_VERDICT


def test_orbit_interference_and_floquet_outputs_are_fail_closed():
    payload = orbit_payload()
    assert payload["numerical_solve_performed"] is False
    assert payload["amplitudes"] is None
    assert payload["relative_phases"] is None
    assert payload["output_energy"] is None
    assert payload["physical_Floquet_multipliers"] is None
    assert payload["removed_coordinate_seam_modes"] is True
    assert payload["verdict"] == ORBIT_VERDICT
