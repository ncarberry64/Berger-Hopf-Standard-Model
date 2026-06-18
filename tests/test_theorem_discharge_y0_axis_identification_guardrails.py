import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_y0_axis_identification as y0  # noqa: E402


def test_guardrails_keep_y0_axis_identification_partial():
    payload = y0.export_outputs(ROOT)
    assert payload["y0_profile_peak_supported"] is True
    assert payload["y0_group_identity_derived"] is False
    assert payload["y0_hopf_pole_derived"] is False
    assert payload["y0_berger_axis_derived"] is False
    assert payload["y0_canonical_focal_point_derived"] is False
    assert payload["standard_model_fully_derived"] is False


def test_negative_results_are_reported():
    y0.export_outputs(ROOT)
    payload = json.loads((ROOT / "theory" / "theorem_discharge_y0_axis_identification_results.json").read_text())
    joined = "\n".join(payload["negative_results"])
    assert "y0 identity/Hopf-pole/axis identification not derived" in joined
    assert "m=q/2 not promotable" in joined
    assert "CKM values not derived" in joined
    assert "PMNS values not derived" in joined
