import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_finite_width_overlap_rank as fw  # noqa: E402


def test_internal_eigenfunction_independence_condition_remains_open():
    fw.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_internal_eigenfunction_independence_condition.md").read_text()

    assert "three independent matrix structures" in fw.internal_eigenfunction_independence_condition()
    assert fw.internal_eigenfunction_independence_condition() in text
    assert "remains open" in text.lower()
    assert "INTERNAL_EIGENFUNCTION_INDEPENDENCE_REMAINS_OPEN" in text
