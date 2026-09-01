from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_TWO_CHORD_PROMOTION_AUDIT.json"
)


def _record() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_two_chord_core_is_certified_but_promotion_fails_closed() -> None:
    record = _record()
    assert record["validation_passed"] is True
    assert record["two_chord_frontier"]["coordinate_interval"] == [0.0, 2e-8]
    assert record["two_chord_frontier"]["certified_hard_subspans"] == 128
    assert record["two_chord_frontier"]["worst_certified_union_ratio"] < 1.0
    theorem = record["promotion_theorem_audited"]
    assert theorem["hypotheses"]["H1_finite_certified_core"]["proved"] is True
    assert theorem["hypotheses"][
        "H2_uniformly_recenterable_invariant_continuation"
    ]["proved"] is False
    assert theorem["hypotheses"][
        "H3_controlled_maximal_endpoint_or_temporal_tail"
    ]["proved"] is False
    assert theorem["conclusion_proved"] is False


def test_chord03_is_not_authorized_as_an_unbounded_campaign() -> None:
    record = _record()
    decision = record["chord03_decision"]
    assert decision["authorized_now"] is False
    assert decision["minimum_additional_chords_sufficient_under_current_estimates"] == (
        "NO_FINITE_NUMBER_DERIVABLE"
    )
    assert record["branch_c_adjudication"]["category"] == (
        "1_MISSING_PROOF_IDENTITY"
    )
    assert record["branch_c_adjudication"][
        "genuine_retained_action_deficiency_proved"
    ] is False
    assert record["claim_boundary"]["Gate7"] == "OPEN"
    assert record["claim_boundary"]["Gate8_plus"] == "LOCKED"


def test_spatial_tail_is_not_promoted_to_temporal_heat_tail() -> None:
    record = _record()
    evidence = record["promotion_theorem_audited"]["hypotheses"][
        "H3_controlled_maximal_endpoint_or_temporal_tail"
    ]["evidence"]
    assert evidence["spatial_Galerkin_tail_is_temporal_heat_tail"] is False
    assert evidence["finite_cover_heat_tail_certified"] is False
    assert evidence["two_chord_temporal_tail_certified"] is False
    assert evidence["two_chord_best_case_endpoint_bound_lower"] > 1.0e7
    assert evidence["forward_relative_reference_operator_available"] is False


def test_two_chord_promotion_audit_is_content_addressable() -> None:
    digest = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest().upper()
    assert digest == "EBAF4727B33374EEFD2EA1CE5543FB66DCD08018B5774A6A7D37835399E4FDF8"
