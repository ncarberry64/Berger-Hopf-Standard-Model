from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_n12_dop853_ae2_birth_domain_reconciliation.py"


def _module():
    spec = importlib.util.spec_from_file_location("dop853_ae2_domain_audit", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_action_version_scope_and_dop853_operator_type() -> None:
    payload = _module().build_payload()
    assert payload["validation_passed"] is True
    assert payload["phase_B_outcome"] == "B1_NO_GO_SUPERSEDED_FOR_BHSM_AE_2_0_0_ONLY"
    assert payload["action_version_split"]["unchanged_retained_v6_7"]["result"] == "B2_NO_GO_SURVIVES"
    assert payload["action_version_split"]["owner_selected_BHSM_AE_2_0_0"]["result"] == "B1_DOMAIN_NO_GO_SUPERSEDED"
    type_audit = payload["dop853_type_audit"]
    assert type_audit["bordered_dimension"] == 62
    assert type_audit["temporal_boundary_trace_space_present"] is False
    assert type_audit["normal_matter_domain_parameter_present"] is False
    assert payload["claim_boundary"]["DOP853_closes_canonical_Gate7_by_itself"] is False
    assert payload["claim_boundary"]["unchanged_action_no_go_retracted"] is False
    assert payload["claim_boundary"]["AE2_silently_adopted"] is False
