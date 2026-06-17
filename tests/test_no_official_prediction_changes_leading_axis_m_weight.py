import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "theory"))

from bhsm_v1 import compare_bhsm_v1_branches  # noqa: E402
import candidate_theorem_discharge_leading_axis_m_weight as la  # noqa: E402


def test_official_prediction_branches_remain_unchanged():
    la.export_outputs(ROOT)
    comparison = compare_bhsm_v1_branches()
    rows = {row["quantity"]: row for row in comparison["rows"]}

    assert comparison["branches"] == ("BHSM_BARE_V1", "BHSM_DRESSED_V1_CANDIDATE")
    assert [row["quantity"] for row in comparison["rows"] if row["changed"]] == ["c/t"]
    assert rows["u/t"]["changed"] is False
    assert rows["sin_theta_13"]["changed"] is False
