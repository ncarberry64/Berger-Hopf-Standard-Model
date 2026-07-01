from bhsm.interface.science_hardening import reviewer_manifest


def test_reviewer_commands_and_network_boundary_are_explicit():
    report = reviewer_manifest()
    assert len(report["commands"]) == 7
    assert report["data_requirements"]["reviewer-cern-open-data"] == "requires_network_or_cached_data"
    assert report["data_requirements"]["all_other_commands"] == "offline"

