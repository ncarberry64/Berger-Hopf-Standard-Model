from bhsm.interface.envelopment import global_scale_anchor_v10_3 as scale


def test_cosmic_anchor_policy_is_separate_from_dimensionless_geometry():
    payload = scale.global_scale_payload()
    assert payload["stationary_global_solution"] is None
    assert payload["unique_dimensionless_shape"] is False
    assert payload["cosmic_anchor_allowed"] is True
    assert payload["maximum_cosmic_anchors"] == 1
    assert payload["anchor_used"] is False
    assert payload["anchor_changes_dimensionless_ratios"] is False


def test_no_particle_observable_calibrates_scale():
    payload = scale.global_scale_payload()
    assert payload["particle_inputs_used"] == []
    assert {"particle mass", "CKM", "PMNS", "electroweak value"} <= set(payload["particle_inputs_forbidden"])
    assert payload["absolute_particle_scale"] is None
