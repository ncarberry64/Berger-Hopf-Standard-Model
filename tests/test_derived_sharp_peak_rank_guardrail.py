import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_legacy_geometric_overlap as lg  # noqa: E402


def test_sharp_peak_rank_guardrail_blocks_rank_three_overclaim():
    lg.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_sharp_peak_rank_guardrail.md").read_text()

    assert lg.strict_point_sampling_rank_bound() == "rank(I)<=1 for strict point-sampling outer-product approximation"
    assert lg.rank_three_yukawa_matrix_derived() is False
    assert "rank(I) <= 1" in text
    assert "outer product" in text
    assert "cannot by itself generate three nonzero singular values" in text
    assert "SHARP_PEAK_RANK_GUARDRAIL_DERIVED_CONDITIONAL" in text
