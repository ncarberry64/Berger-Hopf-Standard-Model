from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RECENTER = BASE / "BHSM_N12_C2_1221_EXPANDED_ENDPOINT_RECENTER.json"
STEP = BASE / "BHSM_N12_C2_1221_EXPANDED_ENDPOINT_SHEARED_STEP.json"
TANGENT_SCRIPT = ROOT / "scripts/derive_n12_c2_1221_sheared_descriptor_tangent.py"


def test_n12_c2_1221_expanded_endpoint_recenter_and_sheared_step() -> None:
    recenter = json.loads(RECENTER.read_text(encoding="utf-8"))
    step = json.loads(STEP.read_text(encoding="utf-8"))
    assert recenter["validation_passed"] is True
    assert recenter["endpoint"]["selected_branch"] == 24
    assert (
        recenter["endpoint"]["fresh_chart_radius"]
        > recenter["endpoint"]["incoming_endpoint_tube_radius_upper"]
    )
    assert step["validation_passed"] is True
    assert step["domain"]["Delta_interval"][0] > 0.0
    assert step["segment"]["signed_descriptor_interval_end"][0] > 0.0
    assert (
        step["segment"]["joint_domain_use_upper"]
        < step["domain"]["selected_fresh_radius"]
    )
    assert "D2lambda*Vhard" in step["graph_variation"]["included_terms"]
    assert step["adjudication"]["actual_later_event_or_canonical_stop"] == "NOT_REACHED"
    assert step["FULL_BHSM_COMPLETE"] is False


def test_endpoint_sheared_tangent_replays_from_tracked_recenter() -> None:
    spec = importlib.util.spec_from_file_location("endpoint_sheared_tangent", TANGENT_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    payload = module.build_payload()
    assert payload["validation_passed"] is True
    assert payload["normal_injection_defect"] == 0.0
    assert payload["sheared_graph_tangent_operator_norm"] < 7.0
    assert payload["FULL_BHSM_COMPLETE"] is False
