from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_boundary_integer_anomaly import (  # noqa: E402
    anomaly_gravity_gravity_u1,
    anomaly_report,
    anomaly_su2_su2_u1,
    anomaly_su3_su3_u1,
    anomaly_u1_cubed,
    one_generation_weyl_fields,
)


def test_one_generation_anomaly_sums_are_exactly_zero_with_optional_nu_r() -> None:
    fields = one_generation_weyl_fields(include_nu_r=True)
    assert anomaly_su3_su3_u1(fields) == Fraction(0, 1)
    assert anomaly_su2_su2_u1(fields) == Fraction(0, 1)
    assert anomaly_u1_cubed(fields) == Fraction(0, 1)
    assert anomaly_gravity_gravity_u1(fields) == Fraction(0, 1)


def test_one_generation_anomaly_sums_are_exactly_zero_without_optional_nu_r() -> None:
    report = anomaly_report(include_nu_r=False)
    assert report["SU3_SU3_U1"] == Fraction(0, 1)
    assert report["SU2_SU2_U1"] == Fraction(0, 1)
    assert report["U1_cubed"] == Fraction(0, 1)
    assert report["gravity_gravity_U1"] == Fraction(0, 1)


def test_optional_nu_r_contributes_zero_to_all_anomaly_sums() -> None:
    with_nu = anomaly_report(include_nu_r=True)
    without_nu = anomaly_report(include_nu_r=False)
    for key in ("SU3_SU3_U1", "SU2_SU2_U1", "U1_cubed", "gravity_gravity_U1"):
        assert with_nu[key] == without_nu[key] == Fraction(0, 1)


def test_left_handed_conjugate_hypercharges_are_used() -> None:
    fields = {field.name: field for field in one_generation_weyl_fields()}
    assert fields["u_R_c"].hypercharge == Fraction(-4, 3)
    assert fields["d_R_c"].hypercharge == Fraction(2, 3)
    assert fields["e_R_c"].hypercharge == Fraction(2, 1)
    assert fields["nu_R_c"].hypercharge == Fraction(0, 1)
