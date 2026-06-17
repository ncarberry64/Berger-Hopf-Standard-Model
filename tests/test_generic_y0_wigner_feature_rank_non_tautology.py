import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_generic_y0_wigner_feature_rank as gy0  # noqa: E402


def test_non_tautology_audit_rejects_fitting_and_rank_promotion():
    text = gy0.render_non_tautology()
    assert "no numeric coordinate fitting" in text
    assert "no rank-three promotion" in text
    assert "no empirical imports" in text
