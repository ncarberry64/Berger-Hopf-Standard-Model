from bhsm.interface.science_hardening import external_reproduction_packet


def test_external_packet_is_narrow_and_unsent():
    report = external_reproduction_packet()
    assert report["contact_performed"] is False
    assert "detector reconstruction" in report["not_in_scope"]
    assert "four-vector" in report["draft_message"]

