from __future__ import annotations

from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def O_q(B: Fraction, L: Fraction) -> Fraction:
    return 3 * B - L


def colored_lower_projector(B: Fraction, T3: Fraction) -> Fraction:
    return 3 * B * (Fraction(1, 2) - T3)


def O_j(B: Fraction, T3: Fraction) -> Fraction:
    return -4 * T3 + 2 * colored_lower_projector(B, T3)


def omega(Oq: Fraction, Oj: Fraction, q: int, j: int) -> Fraction:
    return Oq * q + Oj * j


def mode_norm(q: int, j: int) -> int:
    return q * q + j * j


def sector_target_degree(B: Fraction, T3: Fraction) -> int:
    exponent = 3 * B + (3 * B) * (Fraction(1, 2) - T3)
    assert exponent.denominator == 1
    return 3 * (2 ** exponent.numerator)


def _admissible(sector: str, q: int, j: int) -> bool:
    if q == 0 and j == 0:
        return False
    if sector == "charged_lepton":
        return q % 2 == 1 and j > 0
    if sector == "neutrino":
        return q + 2 * j == 3
    if sector == "up":
        return q % 2 == 0 and q >= 6
    if sector == "down":
        return q % 4 == 0
    raise ValueError(sector)


def sector_modes(
    sector: str,
    B: Fraction,
    L: Fraction,
    T3: Fraction,
    omega_star: int,
    max_j: int = 50,
) -> list[tuple[int, int]]:
    Oq = O_q(B, L)
    Oj = O_j(B, T3)
    solutions: list[tuple[int, int]] = []
    for j in range(max_j + 1):
        for q in range(0, 2 * max_j + 1):
            if _admissible(sector, q, j) and abs(omega(Oq, Oj, q, j)) == omega_star:
                solutions.append((q, j))
    if sector == "neutrino":
        ranked = sorted(solutions, key=lambda item: (item[1], mode_norm(*item)))
    else:
        ranked = sorted(solutions, key=lambda item: (mode_norm(*item), item[0], item[1]))
    return [(0, 0)] + [(q + 2 * j, j) for q, j in ranked[:2]]


def sector_qj_modes(
    sector: str,
    B: Fraction,
    L: Fraction,
    T3: Fraction,
    omega_star: int,
    max_j: int = 50,
) -> list[tuple[int, int]]:
    return [(k - 2 * j, j) for k, j in sector_modes(sector, B, L, T3, omega_star, max_j)]


SECTORS = {
    "charged_lepton": (Fraction(0), Fraction(1), Fraction(-1, 2)),
    "neutrino": (Fraction(0), Fraction(1), Fraction(1, 2)),
    "up": (Fraction(1, 3), Fraction(0), Fraction(1, 2)),
    "down": (Fraction(1, 3), Fraction(0), Fraction(-1, 2)),
}


def test_mode_ledgers_from_candidate_rep_rules() -> None:
    expected = {
        "charged_lepton": [(0, 0), (5, 2), (9, 3)],
        "neutrino": [(0, 0), (3, 0), (3, 1)],
        "up": [(0, 0), (6, 0), (10, 1)],
        "down": [(0, 0), (6, 3), (8, 2)],
    }
    for sector, (B, L, T3) in SECTORS.items():
        assert sector_modes(sector, B, L, T3, sector_target_degree(B, T3)) == expected[sector]


def test_qj_ledgers_from_candidate_rep_rules() -> None:
    expected = {
        "charged_lepton": [(0, 0), (1, 2), (3, 3)],
        "neutrino": [(0, 0), (3, 0), (1, 1)],
        "up": [(0, 0), (6, 0), (8, 1)],
        "down": [(0, 0), (0, 3), (4, 2)],
    }
    for sector, (B, L, T3) in SECTORS.items():
        assert sector_qj_modes(sector, B, L, T3, sector_target_degree(B, T3)) == expected[sector]


def test_generation_count_note_keeps_the_stability_rule_structural() -> None:
    text = (ROOT / "theory" / "generation_count_fourth_order_stability.md").read_text(
        encoding="utf-8"
    )
    assert "GENERATION_COUNT_FOURTH_ORDER_STABILITY_STRUCTURAL_CANDIDATE" in text
    assert "This is not yet a proof" in text
    assert "full Hessian" in text
