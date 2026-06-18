from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def omega_neutrino(q: int, j: int) -> int:
    return -q - 2 * j


def k_from_qj(q: int, j: int) -> int:
    return q + 2 * j


def test_neutrino_omega_equals_negative_k_for_nonnegative_modes() -> None:
    for q in range(0, 8):
        for j in range(0, 5):
            assert omega_neutrino(q, j) == -k_from_qj(q, j)


def test_neutrino_candidate_ledger_and_statuses_are_documented() -> None:
    text = (ROOT / "theory" / "neutrino_conjugate_cover_mass_engine.md").read_text(
        encoding="utf-8"
    )
    assert "NEUTRINO_CONJUGATE_COVER_MASS_ENGINE_CANDIDATE" in text
    assert "NEUTRINO_NORMAL_ORDERING_PREFERENCE_CANDIDATE" in text
    assert "PMNS_EQUAL_DEGREE_CONJUGATE_COVER_CANDIDATE" in text
    assert "PMNS_BASE_HOLONOMY_PHASE_CANDIDATE" in text
    assert "Omega_nu = -q - 2j = -k" in text
    assert "(k,j): (0,0), (3,0), (3,1)" in text
    assert "(q,j): (0,0), (3,0), (1,1)" in text


def test_bare_yukawa_note_keeps_constants_open() -> None:
    text = (ROOT / "theory" / "bare_yukawa_spectral_action.md").read_text(
        encoding="utf-8"
    )
    assert "BARE_YUKAWA_SPECTRAL_ACTION_CANDIDATE" in text
    assert "FULL_BHSM_MASS_ENGINE_CANDIDATE_ARCHITECTURE" in text
    assert "epsilon, tau_0, beta_eff, xi" in text
    assert "must not be\nfitted per sector" in text
