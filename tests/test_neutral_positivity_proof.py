from __future__ import annotations

from bhsm.interface.neutrino_spectral import prove_neutral_positivity_on_domain


def test_exact_cone_positivity_uses_no_thresholding() -> None:
    proof = prove_neutral_positivity_on_domain()
    assert proof.status == "CONDITIONAL_MEASUREMENT_SUPPORTED_NEUTRAL_POSITIVITY_CANDIDATE"
    assert proof.positivity_proven_without_thresholding is True
    assert proof.thresholding_used is False
    assert proof.minimum_on_admissible_domain == 0.0
    assert "max(" not in " ".join(proof.proof_steps)
    assert "entrywise copositivity" in proof.proof_method
    assert proof.raw_psd is False

