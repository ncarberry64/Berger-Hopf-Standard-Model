from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from bhsm.interface.scalar_wall_quartic_source import (
    ARTIFACT_FILES,
    EXACT_BRANCH_LAMBDA,
    FREEZE_COMMIT,
    G3_GEOMETRY,
    G3_LAMBDA,
    G4_GEOMETRY,
    G4_LAMBDA,
    GUARDS,
    INTRODUCTION_COMMIT,
    PRIMARY_VERDICT,
    STABILITY_THRESHOLD,
    VE4_GEOMETRY,
    VE4_LAMBDA,
    candidate_selection_tests,
    deterministic_json,
    factored_coefficients,
    gate_payload,
    incompatibility_payload,
    invariant_payload,
    lambda5,
    materialize,
    materialized_payloads,
    normalization_payload,
    scalar_redefinition,
    scale_payload,
    selection_payload,
    source_payload,
    stability_payload,
    verdict_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_nonzero_constant_redefinition_group_law():
    first = scalar_redefinition(-2.0, z5=3.0, a5=-5.0, g5=7.0, q=0.4)
    assert first["Z5_hat"] == pytest.approx(0.75)
    assert first["A5_hat"] == pytest.approx(-1.25)
    assert first["G5_hat"] == pytest.approx(7.0 / 16.0)
    assert first["raw_u1_scale"] == -2.0
    assert first["normalized_u1_orientation"] == -1.0
    assert first["q_hat_normalized_mode"] == pytest.approx(0.8)
    assert first["q_hat_fixed_mode_orientation"] == pytest.approx(-0.8)
    with pytest.raises(ValueError):
        scalar_redefinition(0.0)


@pytest.mark.parametrize("c", [-7.0, -0.25, 0.125, 3.5])
def test_mu_c_lambda5_and_canonical_field_are_invariant(c: float):
    transformed = scalar_redefinition(
        c, z5=2.5, a5=-8.0, g5=1.75, kappa1=4.0, q=-0.3
    )
    assert transformed["mu_c_hat"] == pytest.approx(transformed["mu_c"])
    assert transformed["lambda5_hat"] == pytest.approx(
        transformed["lambda5"]
    )
    assert transformed["normalized_KKT_norm"] == 1.0
    assert transformed["raw_KKT_norm"] == pytest.approx(c * c)
    assert transformed["phi_hat_normalized_mode"] == pytest.approx(
        transformed["phi"]
    )


def test_lambda5_rejects_degenerate_kinetic_normalization():
    with pytest.raises(ValueError):
        lambda5(1.0, 1.0, 0.0)


def test_factored_g3_matches_unfactored_v6_30_5_formula():
    z5, kappa1, g5 = 2.25, 1.75, -0.4
    lam = lambda5(kappa1, g5, z5)
    factored = factored_coefficients(lam, z5=z5, kappa1=kappa1)
    unfactored = G3_LAMBDA * g5 / z5 + G3_GEOMETRY * z5 / kappa1
    assert factored["g3"] == pytest.approx(unfactored, rel=2e-15)
    assert factored["Omega3"] == pytest.approx(-unfactored, rel=2e-15)


def test_factored_ve4_matches_unfactored_v6_30_5_formula():
    z5, kappa1, g5 = 2.25, 1.75, -0.4
    lam = lambda5(kappa1, g5, z5)
    factored = factored_coefficients(lam, z5=z5, kappa1=kappa1)
    unfactored = VE4_LAMBDA * g5 + VE4_GEOMETRY * z5**2 / kappa1
    assert factored["VE4"] == pytest.approx(unfactored, rel=2e-15)


def test_factored_canonical_quartic_is_scalar_normalization_invariant():
    z5, kappa1, g5 = 2.25, 1.75, -0.4
    lam = lambda5(kappa1, g5, z5)
    factored = factored_coefficients(lam, z5=z5, kappa1=kappa1)
    unfactored = G4_LAMBDA * g5 / z5**2 + G4_GEOMETRY / kappa1
    assert factored["g4_can"] == pytest.approx(unfactored, rel=2e-15)
    for c in (-3.0, 0.2, 5.0):
        assert lambda5(kappa1, g5 / c**4, z5 / c**2) == pytest.approx(lam)
        assert factored_coefficients(
            lam, z5=z5 / c**2, kappa1=kappa1
        )["g4_can"] == pytest.approx(factored["g4_can"])


def test_normalization_payload_tracks_force_and_potential_covariance():
    group = normalization_payload()["normalization_group"]
    assert group["reduced_force"]["coefficient"] == "g3_hat=g3/c^2"
    assert group["canonical_map"]["k0_hat"] == "k0/c^2"
    assert group["potential_and_quartic"]["VE4_hat"] == "VE4/c^4"
    assert group["potential_and_quartic"]["g4_can_hat"] == "g4_can"


def test_exact_branch_locus_and_stability_threshold_are_incompatible():
    payload = incompatibility_payload()["comparison"]
    assert EXACT_BRANCH_LAMBDA == pytest.approx(-18.1974927890349085)
    assert STABILITY_THRESHOLD == pytest.approx(-13.95809839182684)
    assert EXACT_BRANCH_LAMBDA < STABILITY_THRESHOLD
    assert payload["certified_gap"] > 4.2393943972
    assert payload["g4_bracket_at_branch"] < 0.0
    assert not payload["same_selected_value_can_restore_branch_and_be_minimum"]


def test_provenance_distinguishes_architecture_freeze_and_pushforward():
    provenance = source_payload()["provenance"]
    assert provenance["architecture_entry"]["commit"] == INTRODUCTION_COMMIT
    assert provenance["frozen_parent_entry"]["commit"] == FREEZE_COMMIT
    assert provenance["missing_parent_term"] is False
    assert provenance["missing_geometric_derivation_of_value"] is True
    assert provenance["independent_wilson_coefficient"] is True
    assert provenance["integration_constant"] is False


def test_every_candidate_mechanism_is_tested_without_illicit_promotion():
    rows = candidate_selection_tests()
    mechanisms = {row["mechanism"] for row in rows}
    assert len(rows) >= 14
    assert "boundedness of the actual parent potential" in mechanisms
    assert "cap exchange, two-cap gluing, and matcher consistency" in mechanisms
    assert "exact-branch cancellation" in mechanisms
    assert all(row["result"] != "SELECTED" for row in rows)
    summary = selection_payload()["summary"]
    assert summary["classification"] == "OUTCOME_D"
    assert not summary["unique_value_selected"]
    assert not summary["sign_selected"]


def test_outcome_d_is_exact_and_alternatives_are_explicitly_rejected():
    outcome = verdict_payload()["outcome"]
    assert outcome["classification"] == "D"
    assert outcome["verdict"] == PRIMARY_VERDICT
    assert "term is explicitly present" in outcome["why_not_E"]


def test_unconditional_local_stability_remains_fail_closed():
    permission = stability_payload()["permission"]
    assert not permission["unconditional_local_stability_permitted"]
    assert "lambda5>" in permission["conditional_minimum"]
    assert not permission["global_stability_claimed"]
    assert not permission["physical_mass_claimed"]


def test_scale_phase_is_not_permitted_with_dimensionless_blocker():
    scale = scale_payload()["scale"]
    assert not scale["v6_31_permitted"]
    assert not scale["dimensionless_structure_closed"]
    assert scale["unselected_dimensionless_coefficient"] == "lambda5"
    assert not scale["one_universal_scale_allowance_applies"]


def test_completion_gate_update_stops_at_exact_upstream_blocker():
    update = gate_payload()["gate_update"]
    assert update["blocker"] == "RB-02"
    assert update["blocker_status"] == "OPEN_EXACT_UPSTREAM_SCIENTIFIC_BLOCKER"
    assert update["tier_A"] == "BLOCKED"
    assert update["next_phase"] is None
    assert not update["campaign_may_continue_to_independent_downstream_work"]


def test_no_forbidden_input_action_or_tuning_is_introduced():
    expected_false = {
        "measured_input_used",
        "fitted_parameter_used",
        "empirical_inverse_used",
        "branch_restoration_tuning_used",
        "stability_tuning_used",
        "new_action_term_added",
        "new_primitive_added",
        "new_scale_added",
        "vacuum_subtracted",
        "regulator_changed",
        "frozen_prediction_changed",
    }
    assert expected_false <= GUARDS.keys()
    assert all(GUARDS[key] is False for key in expected_false)
    for payload in materialized_payloads().values():
        assert all(payload[key] is False for key in expected_false)


def test_every_artifact_has_required_hindsight_and_release_fields():
    required = {
        "parent_action_path",
        "original_introduction",
        "exact_term",
        "coefficient_definition",
        "field_normalization",
        "invariant_combinations",
        "candidate_source_tests",
        "rejected_selection_mechanisms",
        "exact_symbolic_result",
        "certified_numerical_consequences",
        "completion_tier_impact",
        "release_blocking_status",
        "frozen_hash_status",
        "validated",
        "invalidated",
        "repaired",
        "open",
        "primary_verdict",
    }
    for payload in materialized_payloads().values():
        assert required <= payload.keys()
        assert payload["release_blocking_status"]["release_blocking"] is True
        assert payload["primary_verdict"] == PRIMARY_VERDICT


def test_invariant_classification_separates_normalization_and_scale():
    classification = invariant_payload()["classification"]
    assert "G5" in classification["normalization_dependent"]
    assert "lambda5" in classification["dimensionless_invariant"]
    assert classification["physical_only_after_scale_closure"]


def test_serialization_is_sorted_utf8_lf_and_round_trips():
    text = deterministic_json(verdict_payload())
    assert text.endswith("\n")
    assert "\r" not in text
    assert json.loads(text) == verdict_payload()
    assert text == deterministic_json(verdict_payload())


def test_double_materialization_is_byte_deterministic(tmp_path: Path):
    first_paths = materialize(tmp_path)
    first = {path.name: path.read_bytes() for path in first_paths}
    second_paths = materialize(tmp_path)
    second = {path.name: path.read_bytes() for path in second_paths}
    assert first == second
    assert set(first) == set(ARTIFACT_FILES.values())
    assert all(data.endswith(b"\n") and b"\r\n" not in data for data in first.values())


def test_checked_in_artifacts_match_materializer(tmp_path: Path):
    materialize(tmp_path)
    for filename in ARTIFACT_FILES.values():
        expected = (tmp_path / "artifacts" / filename).read_bytes()
        actual = (ROOT / "artifacts" / filename).read_bytes()
        assert actual == expected


def test_numeric_constants_are_finite_and_precision_safe():
    constants = [
        G3_LAMBDA,
        G3_GEOMETRY,
        VE4_LAMBDA,
        VE4_GEOMETRY,
        G4_LAMBDA,
        G4_GEOMETRY,
        EXACT_BRANCH_LAMBDA,
        STABILITY_THRESHOLD,
    ]
    assert all(math.isfinite(value) for value in constants)
    assert STABILITY_THRESHOLD - EXACT_BRANCH_LAMBDA > 4.23
