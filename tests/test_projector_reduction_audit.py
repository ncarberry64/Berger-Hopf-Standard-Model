from bhsm.interface.primitive_charged_incidence import audit_projector_reduction


def test_projector_reduction_is_exact_and_normalized():
    report = audit_projector_reduction()
    assert report["primitive_trace"] == 7
    assert report["projectors"] == {"lepton": "1/7", "up": "2/7", "down": "4/7"}
    assert report["projector_sum"] == "1"

