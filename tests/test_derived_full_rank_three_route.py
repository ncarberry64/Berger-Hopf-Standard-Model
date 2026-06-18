import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_qj_eigenfunction_map as qj  # noqa: E402


def test_full_rank_three_route_lists_mechanisms_without_promoting_them():
    qj.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_full_rank_three_route.md").read_text()

    assert qj.full_rank_three_route() in text
    assert "does not prove that any one of these mechanisms is satisfied" in text
    assert qj.finite_width_rank_three_derived() is False
    assert "FULL_RANK_THREE_ROUTE_CONDITION_DERIVED_CONDITIONAL" in text
