from __future__ import annotations

from bhsm.interface.envelopment.cosmic_unit_anchor_v10_4 import ANCHOR_VERDICT, cosmic_anchor_payload
from bhsm.interface.envelopment.global_equilibrium_v10_4 import GLOBAL_VERDICT, global_equilibrium_payload


def test_no_global_equilibrium_or_unit_anchor_is_promoted():
    global_result = global_equilibrium_payload()
    anchor = cosmic_anchor_payload()
    assert global_result["stationary_background"] is None
    assert global_result["unique_dimensionless_shape"] is False
    assert global_result["residual_scale_symmetry"] is True
    assert global_result["verdict"] == GLOBAL_VERDICT
    assert anchor["maximum_anchor_count"] == 1
    assert anchor["anchor_count_used"] == 0
    assert anchor["particle_inputs_used"] == []
    assert anchor["absolute_scale"] is None
    assert anchor["verdict"] == ANCHOR_VERDICT
