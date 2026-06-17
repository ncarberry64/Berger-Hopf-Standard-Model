import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_m_weight_assignment as mw  # noqa: E402
from bhsm_v1 import compare_bhsm_v1_branches  # noqa: E402


def test_no_official_prediction_changes_m_weight_assignment_payload_and_branches():
    payload = mw.build_results_payload()
    assert payload["official_predictions_changed"] is False
    assert payload["frozen_predictions_changed"] is False

    comparison = compare_bhsm_v1_branches()
    assert tuple(comparison["branches"]) == ("BHSM_BARE_V1", "BHSM_DRESSED_V1_CANDIDATE")
    changed = [row["quantity"] for row in comparison["rows"] if row["changed"]]
    assert changed == ["c/t"]
    rows = {row["quantity"]: row for row in comparison["rows"]}
    assert rows["u/t"]["changed"] is False
    assert rows["sin_theta_13"]["changed"] is False
