from bhsm.interface.aether_n3_post_curvature_compensation_audit_v17_54 import (
    completion_payload,
    v17_53_selected_raw_vector,
)


def test_state_dimension():
    assert v17_53_selected_raw_vector().shape == (376,)


def test_validated_reclassification():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["status"] == "RECLASSIFIED"
