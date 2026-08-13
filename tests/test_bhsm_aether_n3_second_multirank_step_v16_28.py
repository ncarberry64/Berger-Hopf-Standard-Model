from bhsm.interface.aether_n3_second_multirank_step_v16_28 import (
    CLASSIFICATION,
    FULL_BHSM_COMPLETE,
)


def test_second_multirank_claim_boundary():
    assert CLASSIFICATION == "BHSM_N3_SECOND_FRESH_MULTIRANK_NONLINEAR_STEP"
    assert FULL_BHSM_COMPLETE is False
