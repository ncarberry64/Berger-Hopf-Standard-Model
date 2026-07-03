from bhsm.interface.berger_frame_weighting.universal_quantum_update import audit_universal_quantum_update

def test_quantum_remains_open_without_denominator_attachment():
    assert audit_universal_quantum_update()["status"] == "OPEN_MISSING_UNIVERSAL_GAUGE_COUPLING_QUANTUM"
