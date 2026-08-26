from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "certify_n12_c2_1221_full_action_eigenline_ball.py"


def test_full_action_line_ball_closes_without_descriptor_substitution() -> None:
    spec = importlib.util.spec_from_file_location("full_action_line", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    payload = module.build_payload()
    assert payload["validation_passed"] is True
    assert payload["action_coordinate_ball_radius"] == 1.0e-8
    assert payload["bounds"]["eigenline_gap_lower"] > 2.0e-7
    assert payload["bounds"]["relative_complement_ball_perturbation"] < 1.0
    assert payload["bounds"]["selected_line_second_variation_coefficient_upper"] > 0.0
    assert payload["validation"][
        "no_binary64_eigenvalue_used_as_propagated_descriptor"
    ] is True
    assert payload["FULL_BHSM_COMPLETE"] is False

