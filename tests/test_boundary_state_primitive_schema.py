from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_boundary_state_primitives import (  # noqa: E402
    BRANCH,
    VERDICT_LABELS,
    build_results_payload,
    export_outputs,
)


def test_boundary_state_results_schema() -> None:
    payload = export_outputs(ROOT)
    parsed = json.loads(
        (ROOT / "theory" / "boundary_state_primitive_derivation_results.json").read_text(
            encoding="utf-8"
        )
    )
    assert parsed == payload
    assert parsed["status"] == "candidate_only"
    assert parsed["branch"] == BRANCH
    assert parsed["official_predictions_changed"] is False
    assert parsed["frozen_predictions_changed"] is False
    assert parsed["standard_model_fully_derived"] is False
    assert parsed["bhsm_replacement_claim_allowed"] is False
    assert parsed["primitive_derivation_complete"] is False
    assert parsed["boundary_state_classes_derived"] is False
    assert parsed["boundary_state_outputs"] == {
        "C": "from channel_class",
        "ell": "from closure_class",
        "sigma": "from orientation",
        "w": "from interface_activity",
    }
    assert parsed["bridges_confirmed"]["charge_hypercharge_bridge"] is True
    assert parsed["bridges_confirmed"]["anomaly_closure_bridge"] is True
    assert parsed["verdict_labels"] == VERDICT_LABELS


def test_required_boundary_state_docs_exist() -> None:
    export_outputs(ROOT)
    for relative in [
        "theory/boundary_state_primitive_derivation_gate.md",
        "theory/boundary_state_primitive_registry.md",
        "theory/boundary_state_to_sm_bridge.md",
        "theory/boundary_state_primitive_derivation_results.json",
    ]:
        assert (ROOT / relative).exists(), relative
