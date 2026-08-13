from bhsm.interface.aether_n3_third_multirank_step_v16_30 import (
    CLASSIFICATION,
    FULL_BHSM_COMPLETE,
)


def test_third_multirank_claim_boundary():
    assert CLASSIFICATION.endswith("MULTIRANK_NONLINEAR_STEP")
    assert FULL_BHSM_COMPLETE is False
