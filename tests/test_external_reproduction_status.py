from bhsm.interface.primitive_charged_incidence import audit_external_reproduction_status


def test_external_reproduction_is_prepared_not_completed():
    report = audit_external_reproduction_status()
    assert report["status"] == "PREPARED_NOT_YET_REPRODUCED_EXTERNALLY"
    assert report["external_contact_performed"] is False
    assert report["independent_result_received"] is False

