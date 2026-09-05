from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from bhsm.interface.active_encapsulation_boundary_generator_adjudication import (
    FB_CLASS,
    ONE_OWNER_QUESTION,
    UA_CLASS,
    actualization_status,
    adjudication_payload,
    combined_calderon_response,
    encapsulation_differential_contract,
    harmonic_mode_ledger,
    historical_envelopment_chain,
    mathematical_envelopment_definition,
    n12_fiber_rank_ledger,
    provenance_categories,
)
from scripts.materialize_active_encapsulation_boundary_generator_adjudication import (
    build_payload,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/materialize_active_encapsulation_boundary_generator_adjudication.py"
TARGET = ROOT / (
    "artifacts/action_extension/"
    "BHSM_ACTIVE_ENCAPSULATION_BOUNDARY_GENERATOR_ADJUDICATION.json"
)


def test_historical_components_are_not_falsely_joined() -> None:
    rows = historical_envelopment_chain()
    assert len(rows) == 8
    assert all(row.provenance and row.authority.startswith("RECOVERED_PRIOR_BHSM") for row in rows)
    global_row = next(row for row in rows if row.component == "global_envelopment")
    master = next(row for row in rows if row.component == "master_self_reconstruction")
    old_differential = next(
        row for row in rows if row.component == "energy_geometry_differential_or_envelope"
    )
    incidence = next(
        row for row in rows if row.component == "common_attachment_differential_incidence"
    )
    assert "NOT_HISTORICALLY_WIRED" in global_row.relation_to_clarified_chain
    assert "NO_HISTORICAL_DEPENDENCY" in master.relation_to_clarified_chain
    assert "DIRECT_HISTORICAL_SEMANTIC_ANTECEDENT" in old_differential.relation_to_clarified_chain
    assert "NOT_AN_EVENT_TO_BOUNDARY_GENERATOR" in incidence.relation_to_clarified_chain
    categories = provenance_categories()
    assert set(categories) == {"RECOVERED_PRIOR_BHSM", "OWNER_CLARIFICATION", "NEWLY_DERIVED"}


def test_envelopment_is_typed_relation_and_core_is_not_zero_support_geometry() -> None:
    result = mathematical_envelopment_definition()
    assert result["mathematical_class"] == "TYPED_RELATION_NOT_CURRENTLY_A_SINGLE_VALUED_MAP"
    assert result["route_selected"] is False
    assert result["carrier_selected"] is False
    assert "NOT_THE_LEVEL_SET" in result["C_A_guardrail"]


def test_active_differential_is_covector_without_selected_value() -> None:
    result = encapsulation_differential_contract()
    assert result["definition"] == "Delta_enc=Pi_child+C(F_B)^*Pi_event"
    assert result["type"].startswith("SECTION_OF_THE_BRST")
    assert result["value_derived"] is False
    assert result["historical_response_candidate"]["may_be_used_as_current_J_enc"] is False
    assert "ZERO_TRANSVERSALITY_MAY_NOT_BE_RELABELLED" in result["owner_clarification_result"]


def test_conditional_two_sided_calderon_algebra_only() -> None:
    event = np.diag([2.0, 3.0])
    child = np.diag([5.0, 7.0])
    transfer = np.asarray([[0.0, 1.0], [1.0, 0.0]])
    combined = combined_calderon_response(event, child, transfer)
    assert np.array_equal(combined, child + transfer.T @ event @ transfer)
    with pytest.raises(ValueError):
        combined_calderon_response(event, child, np.ones((3, 2)))


def test_existing_harmonics_do_not_select_event_boundary_coefficients() -> None:
    result = harmonic_mode_ledger()
    assert result["M_rule"] is None
    assert result["selection_class"] == "UNRESOLVED"
    assert "INFINITE_SPECTRAL_SEQUENCE" in result["full_field_free_coefficient_type"]
    assert "NOT_A_CHILD_BOUNDARY_HARMONIC" in result["event_selected_objects"]["N12_ordered_event_eigenline"]


def test_owner_clarification_adds_zero_n12_rank() -> None:
    current = n12_fiber_rank_ledger()
    assert current["existing_fixed_event_rows"] == {
        "attachment_traces": 4,
        "child_constraints": 25,
        "canonical_momentum_mismatch": 2,
        "total": 31,
        "joint_rank": 31,
    }
    assert current["owner_clarification_equation_count"] == 0
    assert current["actual_remaining_fiber_dimension"] == 67
    assert current["actual_after_time_quotient"] == 66
    assert n12_fiber_rank_ledger(12)["remaining_fiber_dimension_hypothesis_only"] == 55
    with pytest.raises(ValueError):
        n12_fiber_rank_ledger(68)


def test_actualization_remains_ua5_and_attachment_fb5() -> None:
    result = actualization_status()
    assert UA_CLASS.startswith("UA5")
    assert FB_CLASS == "FB5"
    assert result["unique_actualization_satisfied"] is False
    assert result["physical_reset_earned"] is False
    assert result["generator_charge_unlocked"] is False
    assert result["ABCD"] == "D_UNCHANGED"


def test_claim_firewall_and_single_owner_question() -> None:
    payload = adjudication_payload()
    claims = payload["claim_boundary"]
    assert not any(claims.values())
    assert ONE_OWNER_QUESTION.count("?") == 1
    assert payload["ONE_SMALLEST_OWNER_QUESTION"] == ONE_OWNER_QUESTION


def test_deterministic_materialization() -> None:
    assert build_payload()["validation_passed"] is True
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    stored = json.loads(TARGET.read_text(encoding="utf-8"))
    assert first == second
    assert stored["validation_passed"] is True
    assert stored["UA_CLASS"].startswith("UA5")
