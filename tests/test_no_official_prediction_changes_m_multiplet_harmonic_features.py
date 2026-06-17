import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_m_multiplet_harmonic_features as mm  # noqa: E402


def test_official_prediction_flags_remain_false():
    payload = mm.build_results_payload()
    assert payload["official_predictions_changed"] is False
    assert payload["frozen_predictions_changed"] is False
