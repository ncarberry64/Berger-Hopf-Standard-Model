import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_qj_eigenfunction_map as qj  # noqa: E402


def test_internal_feature_independence_condition_remains_open():
    qj.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_internal_feature_independence_condition.md").read_text()

    assert qj.rank_three_support_condition() in text
    assert "not promoted" in text
    assert qj.internal_feature_independence_derived() is False
    assert "INTERNAL_FEATURE_INDEPENDENCE_REMAINS_OPEN" in text
