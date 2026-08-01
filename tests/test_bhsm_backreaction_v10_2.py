from __future__ import annotations

import numpy as np
import pytest

from bhsm.interface.envelopment import backreaction_v10_2 as backreaction


def test_normal_stress_projection_is_exact_on_a_common_domain():
    stress = np.diag([2.0, 3.0, 5.0])
    assert backreaction.normal_stress(stress, np.array([0.0, 1.0, 0.0])) == pytest.approx(3.0)


def test_complete_cross_stratum_stress_and_mixed_blocks_fail_closed():
    row = backreaction.cross_stratum_gate()
    assert row["complete_T_AB_total_on_one_domain"] is None
    assert row["M4_to_M8_stress_pushforward"] is None
    assert row["delta2S_da_F_delta_Psi"] == 0
    assert row["delta2S_da_F_delta_H"] == 0


def test_compactness_and_equilibrium_sign_are_not_inserted():
    row = backreaction.compactness_gate()
    assert row["gauge_invariant_compactness_observable"] is None
    assert row["d_psi_star_d_C_env"] is None
    assert row["d_a_F_star_d_C_env"] is None
    assert row["sign"] == "UNDERDETERMINED"
    assert row["desired_negative_sign_inserted"] is False


def test_backreaction_payload_validates_the_obstruction():
    payload = backreaction.backreaction_payload()
    assert payload["validation_passed"] is True
    assert payload["verdict"] == backreaction.BACKREACTION_VERDICT
