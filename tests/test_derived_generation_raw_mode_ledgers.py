import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_raw_mode_berger_harmonic as rh  # noqa: E402


def _pairs(sector: str):
    return tuple((mode.k, mode.j) for mode in rh.raw_mode_ledgers()[sector])


def test_generation_raw_mode_ledgers_match_canonical_modes():
    rh.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_generation_raw_mode_ledgers.md").read_text()

    assert _pairs("reference_charged") == ((0, 0), (5, 2), (9, 3))
    assert _pairs("reference_neutral") == ((0, 0), (3, 0), (3, 1))
    assert _pairs("cyclic_upper") == ((0, 0), (6, 0), (10, 1))
    assert _pairs("cyclic_lower") == ((0, 0), (6, 3), (8, 2))
    assert "`(10,1)`" in text
    assert "`(6,3)`" in text
