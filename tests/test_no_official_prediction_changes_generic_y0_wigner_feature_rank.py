import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_generic_y0_wigner_feature_rank as gy0  # noqa: E402


def test_official_prediction_flags_remain_false():
    payload = gy0.build_results_payload()
    assert payload["official_predictions_changed"] is False
    assert payload["frozen_predictions_changed"] is False
