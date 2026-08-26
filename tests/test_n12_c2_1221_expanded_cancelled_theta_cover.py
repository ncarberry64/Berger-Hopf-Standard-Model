from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "certify_n12_c2_1221_expanded_cancelled_theta_cover.py"


def test_expanded_cancelled_cover_is_strict_and_not_a_stop() -> None:
    spec = importlib.util.spec_from_file_location("expanded_cover", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    payload = module.build_payload()
    assert payload["validation_passed"] is True
    cover = payload["cover"]
    assert cover["accepted_steps"] == 16
    assert cover["final_signed_descriptor_center"] > cover["initial_signed_descriptor"]
    assert cover["final_signed_descriptor_interval"][0] > 0.0
    assert cover["final_joint_domain_use_upper"] < cover["expanded_ball_radius"]
    assert cover["exhaustion"] == "MAXIMUM_COVER_STEPS_REACHED_WITH_DOMAIN_OPEN"
    assert all(row["proof_center_is_physical_endpoint"] is False for row in cover["rows"])
    assert payload["FULL_BHSM_COMPLETE"] is False

