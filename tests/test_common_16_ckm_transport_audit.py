from fractions import Fraction

from bhsm.interface.common_16 import audit_common_16_ckm_transport


def test_ckm_reciprocal_identity_does_not_promote_transport() -> None:
    result = audit_common_16_ckm_transport()
    assert result.reciprocal_weight == Fraction(1, 16)
    assert result.same_scale_identity_transport_available
    assert not result.reciprocal_log_transport_theorem_available
    assert not result.cross_scale_transport_available
    assert result.status == "OPEN_MISSING_CKM_EXPONENT_DERIVATION"
    assert result.residual_used_as_theorem_input is False
