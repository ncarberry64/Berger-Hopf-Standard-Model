from bhsm.interface.science_hardening import ENGINE_PHYSICS_BOUNDARY, engine_physics_status


def test_engine_and_physics_are_explicitly_separated():
    report = engine_physics_status()
    assert report["engine_validated_capabilities"]
    assert report["physics_open_blockers"]
    assert ENGINE_PHYSICS_BOUNDARY in report["claim_boundaries"]
    assert "detector track reconstruction" in report["engine_excluded_capabilities"]

