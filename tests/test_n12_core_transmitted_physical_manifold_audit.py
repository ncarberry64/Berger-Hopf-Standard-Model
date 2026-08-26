from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_n12_core_transmitted_physical_manifold.py"
ARTIFACT = ROOT / "artifacts/flagship_integration/BHSM_N12_CORE_TRANSMITTED_PHYSICAL_MANIFOLD_AUDIT.json"


def test_core_transmission_audit_rebuilds_deterministically() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = ARTIFACT.read_bytes()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    assert ARTIFACT.read_bytes() == first


def test_core_transmission_claim_boundary() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["core_transmitted_physical_manifold"] == "OWNER_HYPOTHESIS_NOT_ACTION_DERIVED"
    assert payload["claim_boundary"]["a_equals_1_over_118"] == "OWNER_CANDIDATE_NOT_DERIVED"
    assert payload["dimension_reconciliation"] == {
        "additional_core_transmission_rank_reduction_certified": False,
        "child_directions": "RETAIN_ACCORDING_TO_73_67_66_CONTEXT",
        "child_projection_rank": 73,
        "common_scale": "RETAIN_PHYSICAL",
        "event_directions": "RETAIN_IN_139_MOVING_CORRESPONDENCE",
        "fixed_event_child_fiber": 67,
        "full_moving_event_child_correspondence": 139,
        "post_whole_history_time_quotient": 66,
    }
    assert all(row["usable_as_T_core"] is False for row in payload["typed_provenance_table"])
    assert payload["fine_structure_adjudication"]["alpha_inserted_upstream"] is False

