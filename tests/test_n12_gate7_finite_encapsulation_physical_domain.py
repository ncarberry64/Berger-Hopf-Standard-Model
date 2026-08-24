from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

from scripts.audit_n12_gate7_finite_encapsulation_physical_domain import (
    build_payload,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_n12_gate7_finite_encapsulation_physical_domain.py"
TARGET = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_FINITE_ENCAPSULATION_PHYSICAL_DOMAIN_AUDIT.json"
)


def test_infinite_branch_is_preserved_but_not_a_realized_observable() -> None:
    payload = build_payload()
    branch = payload["infinite_branch_reclassification"]
    assert branch["round_expanding_branch_falsified"] is False
    assert branch["infinite_optical_angular_counterexample_falsified"] is False
    assert branch["required_for_realized_Gate7_observable"] is False
    assert branch["G7_07_infinite_angular_uniformity"] == (
        "CLOSED_BY_SCOPE_NOT_BY_ACTION_DYNAMICS"
    )


def test_finite_endpoint_trace_branch_is_already_closed() -> None:
    payload = build_payload()
    theorem = payload["finite_endpoint_operator_provenance"]
    assert theorem["conclusion"] == (
        "FINITE_ENDPOINT_ANGULAR_AND_SOURCE_TRACE_BRANCH_CLOSED"
    )
    assert payload["validation"][
        "finite_endpoint_compact_resolvent_provenance_present"
    ] is True
    assert payload["validation"]["fixed_channel_source_Dini_already_closed"] is True
    assert payload["validation"][
        "high_energy_compact_source_trace_norm_already_closed"
    ] is True


def test_finite_encapsulation_exists_without_post_event_recurrence() -> None:
    payload = build_payload()
    theorem = payload["finite_encapsulation_action_theorem"]
    assert theorem["name"] == "FINITE_POSITIVE_TIME_COMPLETED_ENCAPSULATION_EXISTENCE"
    assert theorem["quantifier"] == "EXISTENCE_OF_AT_LEAST_ONE_NOT_UNIVERSAL_REACHABILITY"
    assert theorem["current_status"] == "CLOSED_BY_DESINGULARIZED_LOCAL_BRANCH"
    assert theorem["owner_ontology_alone_proves_existence"] is False
    assert theorem["action_normal_form_proves_existence"] is True
    assert payload["physical_domain"][
        "post_event_return_to_encapsulation_required"
    ] is False
    assert payload["routing"]["arbitrary_infinite_tail_analysis"] == "DO_NOT_REOPEN"
    assert payload["routing"]["current_owner"] == (
        "FINITE_ENDPOINT_ZERO_SOURCE_WEAK_GEOMETRY_FORCE"
    )
    assert payload["claim_boundary"]["Gate7"] == "ACTIVE_ZERO_SOURCE_FORCE_NEXT"


def test_artifact_is_validated_and_deterministic() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    payload = json.loads(TARGET.read_text(encoding="utf-8"))
    assert first == second
    assert payload["validation_passed"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False
