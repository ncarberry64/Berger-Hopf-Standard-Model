from bhsm.interface.aether_n3_sixth_multirank_step_v16_37 import (
    CLASSIFICATION,
    FULL_BHSM_COMPLETE,
)


def test_sixth_multirank_claim_boundary():
    assert CLASSIFICATION.endswith("MULTIRANK_NONLINEAR_STEP")
    assert FULL_BHSM_COMPLETE is False
