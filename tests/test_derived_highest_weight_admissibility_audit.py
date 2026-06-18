import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_harmonic_highest_weight as hw  # noqa: E402


def test_all_frozen_modes_are_admissible_for_n_q_over_two():
    assert hw.all_admissible() is True
    for labels in hw.highest_weight_ledgers().values():
        for label in labels:
            assert abs(label.n) <= label.ell
            assert hw.admissible_n(label)
            assert (label.ell - label.n).denominator == 1


def test_admissibility_audit_lists_all_sector_ledgers():
    hw.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_highest_weight_admissibility_audit.md").read_text()
    for sector in ["reference_charged", "reference_neutral", "cyclic_upper", "cyclic_lower"]:
        assert sector in text
    assert "All modes satisfy `|n|<=ell` and `ell-n=j`" in text
