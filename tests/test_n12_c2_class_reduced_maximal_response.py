from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from derive_n12_c2_class_reduced_maximal_response import build_payload  # noqa: E402


ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_CLASS_REDUCED_MAXIMAL_RESPONSE.json"
)


def test_class_reduced_maximal_response_replays() -> None:
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    replayed = build_payload()
    assert replayed == stored
    assert replayed["validation_passed"] is True


def test_M_C2_definition_is_instantiated_but_value_not_fabricated() -> None:
    payload = build_payload()
    assert payload["claim_boundary"]["C2_maximal_Weyl_family_definition"] == (
        "INSTANTIATED"
    )
    assert payload["adjudication"][
        "abstract_M_C2_value_definition_exists_and_is_unique"
    ] is True
    assert payload["adjudication"]["actual_numeric_M_C2_family_evaluated"] is False


def test_proof_boxes_are_core_data_not_endpoint_classes() -> None:
    payload = build_payload()
    assert payload["finite_core_evidence"]["segment_count"] == 98
    assert payload["finite_core_evidence"]["role"] == (
        "NESTED_FINITE_FORM_CORE_IN_ONE_CLASS_NOT_A_PHYSICAL_ENDPOINT"
    )
    assert payload["M_C2_maximal_operator_family"]["endpoint_dichotomy"][
        "proof_box_edge"
    ] == "NOT_AN_ENDPOINT_CLASS"


def test_weighted_adjoint_is_exact_remaining_force_route() -> None:
    payload = build_payload()
    route = payload["force_adjoint_route"]
    assert route["all_noncompact_reset_Jacobi_columns_required"] is False
    assert route["actual_weighted_load_status"] == "OPEN"
    assert "integral" in route["sufficient_integrability_condition"]
