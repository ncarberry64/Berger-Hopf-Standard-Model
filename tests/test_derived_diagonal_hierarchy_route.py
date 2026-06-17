import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_qj_eigenfunction_map as qj  # noqa: E402


def test_diagonal_hierarchy_route_is_separate_from_rank_three_theorem():
    qj.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_diagonal_hierarchy_route.md").read_text()

    assert qj.diagonal_hierarchy_route() in text
    assert "does not by itself prove a full unrestricted rank-three Yukawa matrix" in text
    assert "DIAGONAL_HIERARCHY_ROUTE_IDENTIFIED_CONDITIONAL" in text
