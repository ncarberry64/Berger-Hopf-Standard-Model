from bhsm.interface.envelopment import seam_projection_v10_3 as seam


def test_raw_seam_is_coordinate_dependent_without_independent_kinetic_mode():
    assert seam.raw_seam_transform(2.0, 0.25) == 2.25
    payload = seam.seam_payload()
    assert payload["independent_physical_mode"] is False
    assert payload["independent_kinetic_term"] is None


def test_historical_support_shift_is_preserved_as_partial_projection():
    payload = seam.seam_payload()
    assert payload["historical_support_work_preserved"] is True
    assert "q_W" in payload["historical_invariant_readout"]
    assert payload["q_W_projection"] == "-(tau*pi*chi_1/16)"
    assert payload["Pi_seam"] is None
