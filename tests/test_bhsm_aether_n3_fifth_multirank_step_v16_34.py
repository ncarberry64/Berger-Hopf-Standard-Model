from bhsm.interface.aether_n3_fifth_multirank_step_v16_34 import (
    CLASSIFICATION,
    FULL_BHSM_COMPLETE,
)


def test_fifth_multirank_claim_boundary():
    assert CLASSIFICATION.endswith("MULTIRANK_NONLINEAR_STEP")
    assert FULL_BHSM_COMPLETE is False
