from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_boundary_integer_anomaly import (  # noqa: E402
    one_generation_weyl_fields,
    witten_su2_doublet_count,
    witten_su2_passes,
)


def test_witten_su2_doublet_count_is_four_and_even() -> None:
    fields = one_generation_weyl_fields(include_nu_r=True)
    assert witten_su2_doublet_count(fields) == 4
    assert witten_su2_passes(fields) is True


def test_witten_su2_count_unchanged_without_optional_nu_r() -> None:
    fields = one_generation_weyl_fields(include_nu_r=False)
    assert witten_su2_doublet_count(fields) == 4
    assert witten_su2_passes(fields) is True
