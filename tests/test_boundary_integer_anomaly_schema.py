from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_boundary_integer_anomaly import (  # noqa: E402
    BRANCH,
    VERDICT_LABELS,
    build_results_payload,
    export_outputs,
    physical_field_charge_table_from_integer_primitives,
)


def test_boundary_integer_anomaly_json_schema() -> None:
    payload = export_outputs(ROOT)
    parsed = json.loads(
        (ROOT / "theory" / "boundary_integer_anomaly_closure_results.json").read_text(
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
    assert parsed["verdict_labels"] == VERDICT_LABELS


def test_boundary_integer_anomaly_gate_payload_values() -> None:
    gate = build_results_payload()["anomaly_closure_gate"]
    assert gate["SU3_SU3_U1"] == "0"
    assert gate["SU2_SU2_U1"] == "0"
    assert gate["U1_cubed"] == "0"
    assert gate["gravity_gravity_U1"] == "0"
    assert gate["witten_su2_doublet_count"] == 4
    assert gate["witten_su2_passes"] is True


def test_physical_charge_table_bridge_uses_integer_primitives() -> None:
    table = physical_field_charge_table_from_integer_primitives()
    assert table["u_R"]["Y"].numerator == 4
    assert table["u_R"]["Y"].denominator == 3
    assert table["nu_R"]["Q"] == 0
    assert table["e_R"]["Q"] == -1
