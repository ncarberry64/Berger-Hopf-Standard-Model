from __future__ import annotations

from fractions import Fraction
from math import gcd, isclose, sqrt
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def sector_target_degree(B: Fraction, T3: Fraction) -> int:
    exponent = 3 * B + (3 * B) * (Fraction(1, 2) - T3)
    assert exponent.denominator == 1
    return 3 * (2 ** exponent.numerator)


def cover_overlap(N_f: int, N_fp: int) -> float:
    return gcd(N_f, N_fp) / sqrt(N_f * N_fp)


def test_sector_target_degree_law_values() -> None:
    assert sector_target_degree(Fraction(0), Fraction(-1, 2)) == 3
    assert sector_target_degree(Fraction(0), Fraction(1, 2)) == 3
    assert sector_target_degree(Fraction(1, 3), Fraction(1, 2)) == 6
    assert sector_target_degree(Fraction(1, 3), Fraction(-1, 2)) == 12


def test_sector_target_degree_law_documented_as_structural_candidate() -> None:
    text = (ROOT / "theory" / "sector_target_degree_law.md").read_text(encoding="utf-8")
    assert "SECTOR_TARGET_DEGREE_LIFT_LAW_STRUCTURAL_CANDIDATE" in text
    assert "must not be used to update frozen predictions" in text


def test_cover_overlap_checks_for_interface_kernel() -> None:
    assert isclose(cover_overlap(6, 12), 1 / sqrt(2), rel_tol=0.0, abs_tol=1e-15)
    assert cover_overlap(3, 3) == 1.0


def test_pmns_connection_difference_cancels_fiber_component() -> None:
    A_l = (Fraction(-1), Fraction(2))
    A_nu = (Fraction(-1), Fraction(-2))
    diff = (A_l[0] - A_nu[0], A_l[1] - A_nu[1])
    assert diff == (Fraction(0), Fraction(4))


def test_boundary_interface_documentation_contains_unitary_interface() -> None:
    text = (ROOT / "theory" / "boundary_interface_mixing_kernel.md").read_text(
        encoding="utf-8"
    )
    assert "BOUNDARY_INTERFACE_MIXING_KERNEL_STRUCTURAL_CANDIDATE" in text
    assert "C_ud = gcd(6,12)/sqrt(6*12) = 1/sqrt(2)" in text
    assert "V_CKM = U_u^dagger V_ud U_d" in text
