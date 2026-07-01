from bhsm.interface.ckm_bounded_interface_normalization import audit_normalized_projector_sandwich


def test_normalized_projector_sandwich_requires_all_four_sources():
    payload = audit_normalized_projector_sandwich()
    assert payload["status"] == "OPEN_MISSING_NORMALIZED_PROJECTOR_SANDWICH_ACTION_TERM"
    assert payload["boundary_measure_source"] is None
    assert payload["coefficient_normalization_source"] is None
    assert payload["variational_action_source"] is None
    assert payload["missing_requirements"] == [
        "boundary/action measure",
        "coefficient normalization",
        "sector projector sandwich",
        "action/variational provenance",
    ]
