from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/materialize_bhsm_gate7_compute_conservation.py"
AUDIT = ROOT / "artifacts/current_semantics/BHSM_COMPUTE_JUSTIFICATION_AUDIT.json"
LEDGER = ROOT / "artifacts/current_semantics/BHSM_COMPUTE_BUDGET_LEDGER.json"


def _module():
    spec = importlib.util.spec_from_file_location("compute_conservation", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_compute_audit_is_valid_deterministic_and_fail_closed() -> None:
    audit, ledger = _module().build_payloads()
    assert audit == json.loads(AUDIT.read_text(encoding="utf-8"))
    assert ledger == json.loads(LEDGER.read_text(encoding="utf-8"))
    assert audit["validation_passed"] is True
    assert audit["authorization"][
        "resume_nodes_128_through_370_at_192_bit"
    ] is True
    assert audit["authorization"]["worker_count"] == 8
    assert audit["authorization"]["automatic_follow_on_global_campaign"] is False
    assert audit["claim_boundary"]["OUTWARD_BILINEAR_EQUIVALENCE_DERIVED"] is False
    assert audit["claim_boundary"]["GATE7_CLOSED"] is False


def test_compute_ledger_does_not_authorize_unestimated_future_work() -> None:
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    entries = {entry["id"]: entry for entry in ledger["entries"]}
    assert entries["G7_MIXED_ENDPOINT_RECONNAISSANCE"][
        "actual_CPU_hours_to_checkpoint_80"
    ] > 0.0
    assert entries["G7_MIXED_ENDPOINT_RECONNAISSANCE"][
        "actual_CPU_hours_complete"
    ] > entries["G7_MIXED_ENDPOINT_RECONNAISSANCE"][
        "actual_CPU_hours_through_node_127"
    ]
    assert entries["G7_MIXED_ENDPOINT_RECONNAISSANCE"][
        "proof_obligation_closed"
    ] is True
    assert entries["G7_DIRECT_BILINEAR_OUTWARD_EQUIVALENCE"][
        "authorization"
    ] == "AUTHORIZED_AND_COMPLETED_BY_POST_RECONNAISSANCE_AUDIT"
    assert entries["G7_DIRECT_BILINEAR_OUTWARD_EQUIVALENCE"][
        "proof_obligation_closed"
    ] is True
    assert entries["G7_TRANSVERSE_TRANSVERSE_OPERATOR_BOUND"][
        "authorization"
    ] == "REQUIRES_SEPARATE_COMPUTE_JUSTIFICATION_AUDIT"
    assert ledger["validation"]["calibration_input_used"] is False
