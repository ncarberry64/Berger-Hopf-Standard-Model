from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_bare_engine_triangulation import build_payload  # noqa: E402


def test_candidate_invariant_families_are_nonofficial_and_controls_labeled() -> None:
    payload = build_payload(ROOT)
    families = {row["family"]: row for row in payload["candidate_invariant_families"]}
    expected = {
        "sector_operator_weighted_action",
        "signed_boundary_action_magnitude",
        "cross_coupled_berger_action",
        "branch_gap_action",
        "sector_response_weighted_action",
        "orientation_sensitive_action",
    }
    assert set(families) == expected
    assert all(row["official"] is False for row in families.values())
    assert families["branch_gap_action"]["control"] is True
    assert families["branch_gap_action"]["status"] == "BRANCH_ASSIGNMENT_DIAGNOSTIC"
    assert "constant on fixed target-degree sectors" in families["signed_boundary_action_magnitude"]["limitation"]


def test_invariant_table_contains_required_mode_quantities() -> None:
    invariant = build_payload(ROOT)["missing_invariant_diagnostics"]["mode_invariants"][0]
    required = {
        "q",
        "j",
        "k",
        "N",
        "Omega_f",
        "Omega_star",
        "abs_Omega",
        "q_over_Omega",
        "j_over_Omega",
        "fiber_fraction",
        "base_fraction",
        "sector_operator_norm",
        "orientation_product",
        "cross_term",
        "mode_gap_to_reference",
        "pure_fiber_flag",
        "pure_base_flag",
        "lower_doublet_projector",
        "colored_lift_exponent",
        "channel_dim",
        "active_dim",
    }
    assert required <= set(invariant)


def test_verdicts_identify_missing_structure_without_claiming_closure() -> None:
    labels = set(build_payload(ROOT)["verdict_labels"])
    assert "BARE_ENGINE_TRIANGULATION_AUDIT_COMPLETE" in labels
    assert "SPECTRAL_ACTION_NOT_EXISTING_ENGINE" in labels
    assert "NO_NUMERICAL_CLOSURE" in labels
    assert "REFERENCE_SCHEME_LIMITATION" in labels
    assert not any(label.endswith("_STRONG") for label in labels)
