import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_finite_width_overlap_rank as fw  # noqa: E402


def test_sharp_peak_outer_product_limit_is_rank_one_guardrail():
    fw.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_sharp_peak_outer_product_limit.md").read_text()

    assert fw.sharp_peak_rank_bound() == "rank(I)<=1 for strict point-sampling I_ij=a_i^* b_j"
    assert fw.strict_point_sampling_rank_three_derived() is False
    assert "outer product" in text
    assert "does not derive rank three" in text
    assert "SHARP_PEAK_RANK_ONE_LIMIT_DERIVED_CONDITIONAL" in text
