from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_n12_gate7_dop853_system_adapter_matching.py"


def _payload():
    spec = importlib.util.spec_from_file_location("gate7_adapter", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.build_payload()


def test_existing_slots_and_actual_missing_adapters() -> None:
    payload = _payload()
    assert payload["validation_passed"] is True
    assert payload["new_theory_choice_required"] is False
    assert payload["actual_missing_adapters"] == [
        "CORRELATED_DOP853_Y_Z1_Z2_AND_FIRST_HIT_DOMAIN_TRANSFER",
        "SINGLE_SIGNED_JOINT_HEAT_MINUS_ZETA_REVERSE_CONTRACTION_PROJECTED_KKT_ROOT_AND_HESSIAN",
    ]
    slots = {row["diagram_slot"]: row for row in payload["matching_audit"]}
    assert slots["JOINT_E1_C2_SEAM_OPERATOR"]["match"] == "VALID_MATCH"
    assert slots["FINITE_C2_GEOMETRY_RESPONSE"]["match"] == "VALID_MATCH_AUXILIARY_GEOMETRY_AND_FIRST_VARIATION_NOT_MATTER_DOMAIN"
    assert slots["FINITE_FIRST_HIT_AND_DOMAIN_TUBE"]["match"].startswith("ACTUALLY_MISSING")
    assert payload["claim_boundary"]["new_C2_operator_theory_required"] is False
    assert payload["claim_boundary"]["FULL_BHSM_COMPLETE"] is False
