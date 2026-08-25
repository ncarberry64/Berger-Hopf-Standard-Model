import json
from pathlib import Path

from bhsm.interface.full_retained_asymptotic_branch import (
    asymptotic_branch_theorem,
    normalized_action_scale_decomposition,
    positive_integer_nonresonance,
)


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FULL_RETAINED_ASYMPTOTIC_BRANCH.json"
)


def test_exact_normalized_scale_decomposition():
    data = normalized_action_scale_decomposition()
    assert data["bulk_scale_weights"] == [7, 5, 3, 1, -1]
    assert data["bulk_epsilon_powers"] == [0, 1, 2, 3, 4]
    assert data["normalized_inverse_inertia_leading_epsilon_power"] == 7
    assert data["boundary_Casimir_epsilon_power"] == 4
    assert data["round_leading_inertia_strictly_positive"] is True


def test_all_positive_integer_recurrences_are_nonresonant():
    data = positive_integer_nonresonance()
    assert data["all_positive_integer_recurrence_pencils_invertible"] is True
    assert "k=7/2" in data["stable_collision"]


def test_briot_bouquet_branch_has_positive_H4_limit():
    theorem = asymptotic_branch_theorem()
    assert theorem["conclusion"]["exists_epsilon_star"] is True
    assert theorem["conclusion"]["positive_limit"].endswith(">0")
    assert theorem["scope"]["mathematical_infinite_branch_only"] is True
    assert theorem["scope"]["physical_particle_observable_promoted"] is False


def test_asymptotic_artifact_closes_only_mathematical_outcome_a():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    consequence = payload["nonlinear_consequence"]
    assert consequence["a_preserves_H4_to_H_inf_positive"] is True
    assert consequence["b_forces_H4_to_zero_with_Osgood_envelope"] is False
    assert consequence[
        "c_drives_event_or_canonical_stop_inside_local_asymptotic_neighborhood"
    ] is False
    assert consequence["physical_particle_statement"] is False
    assert payload["claim_boundary"]["physical_finite_history_zero_source_force"] == "OPEN"
    assert payload["FULL_BHSM_COMPLETE"] is False
