from __future__ import annotations

from bhsm.interface.neutrino_spectral import load_neutral_mass_gap_action


def test_mass_gap_action_is_loaded_offline_with_conditional_neutral_generalization() -> None:
    result = load_neutral_mass_gap_action()
    assert result.status == "ARTIFACT_BACKED_MASS_GAP_ACTION"
    assert result.scalar_action_artifact_backed is True
    assert result.neutral_action_generalization_conditional is True
    assert result.spectral_gap_formula == "mu_nu = sqrt(A_nu/Z_nu) K_neutral,eff"
    assert result.empirical_derivation_inputs_used is False

