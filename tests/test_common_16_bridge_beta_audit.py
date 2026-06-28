from fractions import Fraction

from bhsm.interface.common_16 import audit_common_16_bridge_beta


def test_bridge_and_beta_refactorizations_match_exactly() -> None:
    result = audit_common_16_bridge_beta()
    assert result.common_16_bridge_value == Fraction(16, 189)
    assert result.incidence_overlap_bridge_value == Fraction(16, 189)
    assert result.bridge_identity_exact
    assert result.beta_identities_exact
    assert result.common_generator_artifact_backed is False
