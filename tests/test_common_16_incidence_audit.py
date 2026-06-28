from fractions import Fraction

from bhsm.interface.common_16 import audit_common_16_incidence


def test_common_16_incidence_identities_are_exact_but_conditional() -> None:
    result = audit_common_16_incidence()
    assert result.sector_weights == {"lepton": 1, "up": 2, "down": 4}
    assert result.charged_weight_sum == 7
    assert result.projector_fractions == {
        "lepton": Fraction(1, 7),
        "up": Fraction(2, 7),
        "down": Fraction(4, 7),
    }
    assert result.n_16 == 16
    assert result.epsilon_ckm_candidate == Fraction(1, 16)
    assert result.status == "CONDITIONAL_COMMON_16_GENERATOR_CANDIDATE"
    assert result.rho_ch_source_status == "OPEN_MISSING_RHO_CH_ACTION_DERIVATION"
