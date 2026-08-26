from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "derive_n12_gate7_closed_system_zero_external_source_ontology.py"
ARTIFACT = ROOT / "artifacts" / "flagship_integration" / "BHSM_N12_GATE7_CLOSED_SYSTEM_ZERO_EXTERNAL_SOURCE_ONTOLOGY.json"


def test_closed_system_zero_external_source_ontology() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert payload["validation_passed"] is True
    assert payload["provenance"]["category"] == "OWNER_AUTHORIZED_PHYSICAL_ONTOLOGY"
    assert payload["provenance"]["action_derived"] is False
    assert payload["external_internal_partition"]["set_to_zero"] == ["J_ext"]
    assert "M_C2" in payload["external_internal_partition"]["internal_not_zeroed"]
    assert payload["physical_force"]["additional_seam_source_allowed"] is False
    assert payload["matching_audit"]["common_source_incidence"].startswith("VALID_INTERNAL")
    assert payload["adjudication"]["internal_response_zeroing"] == "FORBIDDEN"
    assert payload["adjudication"]["complete_joint_graded_cotangent"] == "OPEN_CURRENT_OPERATOR_OWNER"
    assert payload["claim_boundary"]["finite_1222_core_promoted_to_endpoint"] is False
    assert payload["claim_boundary"]["chord_03_authorized"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_joint_assembly_order_and_no_double_counting() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    order = payload["ordered_evaluation"]
    assert order.index("ASSEMBLE_COMPLETE_JOINT_INTERNAL_OPERATOR_AND_DOMAIN") < order.index(
        "SET_ONLY_EXTERNAL_J_ext_TO_ZERO"
    )
    assert payload["joint_assembly"]["double_count_rule"].endswith("EXACTLY_ONCE")
    assert payload["validation"]["joint_Schur_decomposition_is_counted_exactly_once"] is True
