from __future__ import annotations

from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

STATUS_LABELS = {
    "FULL_BHSM_CANDIDATE_ARCHITECTURE",
    "LOCAL_SM_GAUGE_LAYER_PRESERVED",
    "BOUNDARY_FLAVOR_CHANNEL_LAYER",
    "TOPOGRAPHIC_STABILITY_LAYER",
    "RESPONSE_SELECTOR_LAYER",
    "RESPONSE_SELECTOR_STRUCTURAL_CANDIDATE",
    "LEPTON_8_9_CHANNEL_RULE_PARTIAL",
    "PURE_FIBER_MIDDLE_UP_HALF_CANDIDATE_ONLY",
    "LIGHT_UP_THREE_PAIR_AMPLITUDE_PROJECTION_CANDIDATE_ONLY",
    "CKM_1_16_INTERFACE_BLOCK_CANDIDATE_ONLY",
    "GAUGE_COUPLING_ACTIVE_GENERATOR_COUNT_STRUCTURAL_CANDIDATE",
}


def O_q(B: Fraction, L: Fraction) -> Fraction:
    return 3 * B - L


def colored_lower_projector(B: Fraction, T3: Fraction) -> Fraction:
    return 3 * B * (Fraction(1, 2) - T3)


def O_j(B: Fraction, T3: Fraction) -> Fraction:
    return -4 * T3 + 2 * colored_lower_projector(B, T3)


def q_from_kj(k: int, j: int) -> int:
    return k - 2 * j


def k_from_qj(q: int, j: int) -> int:
    return q + 2 * j


def mode_norm(q: int, j: int) -> int:
    return q * q + j * j


def omega(Oq: Fraction, Oj: Fraction, q: int, j: int) -> Fraction:
    return Oq * q + Oj * j


def test_master_theory_line_exists_and_is_candidate_only() -> None:
    path = ROOT / "theory" / "full_bhsm_candidate_theory_line_v0_1.md"
    text = path.read_text(encoding="utf-8")

    assert "S_BHSM = S_SM,local + S_T + S_boundary + S_response" in text
    for label in STATUS_LABELS:
        assert label in text
    assert "candidate-only" in text
    assert "No official prediction is changed" in text


def test_representation_operator_formulas() -> None:
    charged_lepton = (Fraction(0), Fraction(1), Fraction(-1, 2))
    neutrino = (Fraction(0), Fraction(1), Fraction(1, 2))
    up = (Fraction(1, 3), Fraction(0), Fraction(1, 2))
    down = (Fraction(1, 3), Fraction(0), Fraction(-1, 2))

    assert (O_q(charged_lepton[0], charged_lepton[1]), O_j(charged_lepton[0], charged_lepton[2])) == (
        Fraction(-1),
        Fraction(2),
    )
    assert (O_q(neutrino[0], neutrino[1]), O_j(neutrino[0], neutrino[2])) == (
        Fraction(-1),
        Fraction(-2),
    )
    assert (O_q(up[0], up[1]), O_j(up[0], up[2])) == (Fraction(1), Fraction(-2))
    assert (O_q(down[0], down[1]), O_j(down[0], down[2])) == (Fraction(1), Fraction(4))


def test_no_forbidden_overclaims_in_main_theory_line() -> None:
    text = (ROOT / "theory" / "full_bhsm_candidate_theory_line_v0_1.md").read_text(
        encoding="utf-8"
    ).lower()
    forbidden = [
        "derived full standard model",
        "full standard model derivation claim",
        "standard model replacement claim",
        "official prediction update",
        "hidden retuning",
    ]
    for phrase in forbidden:
        assert phrase not in text
