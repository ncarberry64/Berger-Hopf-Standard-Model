from bhsm.interface.aether_n3_attachment_canonical_covector_v17_91 import (
    completion_payload,
)


def test_attachment_canonical_covector_validates():
    payload = completion_payload()
    assert payload["validation_passed"]
    result = payload["attachment_canonical_covector"]
    assert len(result["canonical_attachment_momentum"]) == 2
    assert len(result["instantaneous_attachment_action_force"]) == 2
    assert result["canonical_covector"]["F_child_outer"] == "OPEN_NOT_SET_TO_ZERO"
    assert not result["interpretation"]["nonzero_momentum_is_a_defect"]
    assert not result["interpretation"]["nonzero_force_is_a_static_failure"]
