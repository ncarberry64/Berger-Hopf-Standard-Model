import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_finite_width_overlap_rank as fw  # noqa: E402


def test_rank_three_overlap_condition_is_conditional_not_asserted():
    fw.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_rank_three_overlap_condition.md").read_text()

    assert fw.rank_three_condition() == (
        "rank(I_f)=3 if finite-width moment contributions span three independent row/column structures"
    )
    assert fw.rank_three_condition() in text
    assert "not asserted satisfied" in text
    assert fw.finite_width_rank_three_derived() is False
    assert "RANK_THREE_OVERLAP_CONDITION_DERIVED_CONDITIONAL" in text
