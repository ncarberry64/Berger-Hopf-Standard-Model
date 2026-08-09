from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from bhsm.interface.aether_generator_selection_v15_2 import (
    physical_equivalence_payload,
)
from bhsm.interface.aether_master_closure_v15_5 import (
    EXACT_NEXT_OBJECT as V15_5_NEXT_OBJECT,
    state_dynamics_fixed_point_payload,
)
from bhsm.interface.aether_norman_cycle_closure_v15_6 import (
    BLOCKED,
    ENCLOSURE,
    EXACT_NEXT_OBJECT,
    FAILURE_CLASSES,
    PARENT,
    PERSISTED_ENCLOSURE,
    UPDATED_PARENT,
    artifact_payloads,
    compose_cycle,
    completion_conditions,
    cycle_morphisms,
    de_envelopment_gate_payload,
    deterministic_json,
    floquet_reconstruction_payload,
    formation_gate_payload,
    full_completion_payload,
    legitimate_cycle_spectrum,
    master_self_reconstruction_payload,
    materialize,
    ontology_payload,
    parent_invariant_ledger_payload,
    primitive_loop_payload,
    state_gns_cycle_selection_payload,
    theorem_package,
    z2_z3_killscreen_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_formation_map_is_typed_from_parent_to_enclosure() -> None:
    formation = cycle_morphisms()[0]
    assert (formation.symbol, formation.source, formation.target) == ("F", PARENT, ENCLOSURE)


def test_formation_depends_on_existing_instability_gate() -> None:
    payload = formation_gate_payload()
    assert payload["threshold"] == "lambda_min(H_sigma^(0)[Phi])=0"
    assert payload["threshold_action_owned"] is True
    assert payload["formation_map_F_action_derived"] is False


def test_linear_threshold_does_not_claim_nonlinear_existence() -> None:
    payload = formation_gate_payload()
    assert payload["threshold_is_formation_map"] is False
    assert payload["nonlinear_continuation_branch_derived"] is False
    assert payload["first_failure"] == "FORMATION_MAP_NOT_ACTION_DERIVED"


def test_persistence_map_is_typed_on_enclosure_domain() -> None:
    persistence = cycle_morphisms()[1]
    assert (persistence.symbol, persistence.source, persistence.target) == (
        "P",
        ENCLOSURE,
        PERSISTED_ENCLOSURE,
    )
    assert persistence.theorem_class_owned is True
    assert persistence.action_derived_map is False


def test_de_envelopment_is_forward_release_to_updated_parent() -> None:
    release = cycle_morphisms()[2]
    assert (release.symbol, release.source, release.target) == (
        "D",
        PERSISTED_ENCLOSURE,
        UPDATED_PARENT,
    )


def test_de_envelopment_is_not_formation_inverse() -> None:
    payload = de_envelopment_gate_payload()
    assert payload["D_equals_F_inverse"] is False
    assert payload["D_type"] != payload["formation_inverse_type"]


def test_de_envelopment_is_not_formation_dagger() -> None:
    payload = de_envelopment_gate_payload()
    assert payload["D_equals_F_dagger"] is False
    assert payload["D_type"] != payload["formation_dagger_type"]


def test_updated_parent_is_not_forced_equal_to_initial_parent() -> None:
    assert compose_cycle()["same_parent_state_assumed"] is False
    assert PARENT != UPDATED_PARENT


def test_cycle_composition_domains_match() -> None:
    result = compose_cycle()
    assert result["typed_composition_exists"] is True
    assert result["source"] == PARENT
    assert result["target"] == UPDATED_PARENT


def test_cycle_domain_mismatch_fails() -> None:
    formation, persistence, release = cycle_morphisms()
    bad = persistence.__class__(
        persistence.symbol,
        "wrong_domain",
        persistence.target,
        persistence.physical_role,
        persistence.theorem_class_owned,
        persistence.action_derived_map,
        persistence.first_failure,
    )
    with pytest.raises(ValueError, match="domain mismatch"):
        compose_cycle((formation, bad, release))


def test_cycle_requires_exactly_three_arrows() -> None:
    with pytest.raises(ValueError, match="exactly F, P, D"):
        compose_cycle(cycle_morphisms()[:2])


def test_parent_to_parent_cycle_exists_only_conditionally() -> None:
    result = compose_cycle()
    assert result["parent_to_updated_parent"] is True
    assert result["physical_operator_exists"] is False


def test_release_domain_and_boundary_law_are_not_owned() -> None:
    payload = de_envelopment_gate_payload()
    assert payload["receiving_parent_domain_action_owned"] is False
    assert payload["release_boundary_condition_action_owned"] is False
    assert payload["status"] == BLOCKED


def test_invariant_ledger_is_honest_and_incomplete() -> None:
    payload = parent_invariant_ledger_payload()
    assert payload["ledger_complete"] is False
    assert payload["first_failure"] == "INVARIANT_LEDGER_INCOMPLETE"
    assert payload["new_parent_content_field_introduced"] is False


def test_no_orphaned_enclosure_dof_is_not_falsely_claimed() -> None:
    status = parent_invariant_ledger_payload()["open_entries"]
    assert status["orphaned_enclosure_degrees_of_freedom"] == "NOT_EXCLUDED"


def test_quasilocal_noether_flux_is_candidate_not_closure() -> None:
    payload = de_envelopment_gate_payload()
    assert payload["quasilocal_Noether_flux_candidate_exists"] is True
    assert payload["quasilocal_Noether_flux_closes_D"] is False


def test_primitive_cycle_has_no_physical_operator_representation() -> None:
    payload = primitive_loop_payload()
    assert payload["typed_parent_to_updated_parent"] is True
    assert payload["physical_operator_representation"] is None
    assert payload["loop_spectrum"] is None


@pytest.mark.parametrize(
    ("owned", "domain", "representation", "message"),
    [
        (False, False, None, "PRIMITIVE_LOOP_OPERATOR_NOT_DEFINED"),
        (True, False, np.eye(2), "DE_ENVELOPMENT_DOMAIN_FAILURE"),
        (True, True, None, "LOOP_SPECTRUM_NOT_DEFINED"),
    ],
)
def test_spectrum_is_blocked_until_representation_is_legitimate(
    owned: bool,
    domain: bool,
    representation: np.ndarray | None,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        legitimate_cycle_spectrum(representation, action_owned=owned, domain_proved=domain)


def test_legitimate_diagnostic_spectrum_works_when_explicitly_owned() -> None:
    values = legitimate_cycle_spectrum(np.diag([1.0, -1.0]), action_owned=True, domain_proved=True)
    assert values == [{"real": 1.0, "imag": 0.0}, {"real": -1.0, "imag": 0.0}]


def test_nonsquare_cycle_representation_is_rejected() -> None:
    with pytest.raises(ValueError, match="square"):
        legitimate_cycle_spectrum(np.ones((2, 3)), action_owned=True, domain_proved=True)


def test_floquet_reconstruction_is_not_claimed_without_both_sides() -> None:
    payload = floquet_reconstruction_payload()
    assert payload["physical_M_BHSM_computed"] is False
    assert payload["primitive_H_A_operator_computed"] is False
    assert payload["intertwining_identity_proved"] is False
    assert payload["first_failure"] == "FLOQUET_RECONSTRUCTION_FAILURE"


@pytest.mark.parametrize("order", [2, 3])
def test_z2_z3_fail_the_full_cycle_at_the_first_physical_gate(order: int) -> None:
    rows = z2_z3_killscreen_payload()["candidates"]
    row = next(item for item in rows if item["candidate"] == f"Z{order}")
    assert row["first_failure"] == "FAILS_FORMATION_CLOSURE"
    assert row["physical_option"] is False
    assert row["disposition"].startswith("SURROGATE_INCOMPLETENESS_WITNESS")


def test_z2_z3_are_not_selected_by_observation_or_minimality() -> None:
    payload = z2_z3_killscreen_payload()
    assert payload["selected_by_generation_count"] is False
    assert payload["selected_by_minimal_dimension"] is False
    assert payload["either_action_eliminated_relative_to_other"] is False


def test_v15_5_reset_semigroup_no_selection_theorem_is_preserved() -> None:
    old = state_dynamics_fixed_point_payload()
    new = state_gns_cycle_selection_payload()
    assert new["v15_5_reset_semigroup_theorem_preserved"] is True
    assert new["fixed_pair_cardinality"] == old["state_dynamics_fixed_pair_cardinality"]
    assert new["cycle_invariant_state_selected"] is False


def test_positive_state_and_gns_handling_remain_fail_closed() -> None:
    payload = state_gns_cycle_selection_payload()
    assert payload["canonical_GNS_class_selected"] is False
    assert "STATE_REMAINS_NONUNIQUE" in payload["failure_classes"]
    assert "GNS_REMAINS_NONUNIQUE" in payload["failure_classes"]


def test_v15_2_physical_equivalence_quotient_is_preserved() -> None:
    payload = physical_equivalence_payload()
    assert payload["unitary_basis_change_is_physical_difference"] is False
    assert payload["preclock_scaling"]["classification"] == "REPARAMETERIZATION_REDUNDANCY_BEFORE_CLOCK_SELECTION"


def test_precock_scaling_and_central_shift_are_not_promoted() -> None:
    payload = physical_equivalence_payload()
    assert payload["central_shift_gate"]["classification"] == "CONDITIONAL_PROJECTIVE_EQUIVALENCE_NOT_UNCONDITIONAL_PHYSICAL_GAUGE"
    assert payload["central_shift_gate"]["block_relative_shift_is_central"] is False


def test_pregeometric_firewalls_and_foundational_interface() -> None:
    ledger = parent_invariant_ledger_payload()
    completion = full_completion_payload()
    assert ledger["primitive_metric_area_used_in_core"] is False
    assert ledger["foundational_interface_capacity_allowed"] is True
    assert completion["primitive_ordinary_time"] is False
    assert completion["primitive_ordinary_energy_units"] is False


def test_no_preferred_frame_empirical_inputs_or_parameters() -> None:
    payload = full_completion_payload()
    assert payload["preferred_frame"] is False
    assert payload["new_empirical_inputs"] is False
    assert payload["new_fitted_parameters"] is False
    assert payload["new_arbitrary_continuous_parameters"] is False
    assert payload["new_primitive_fields"] is False


def test_no_frozen_or_official_prediction_change() -> None:
    payload = full_completion_payload()
    assert payload["frozen_predictions_changed"] is False
    assert payload["official_prediction_logic_changed"] is False


def test_norman_historical_reconciliation_is_a_dependency_map() -> None:
    payload = ontology_payload()
    rows = payload["historical_dependency_map"]
    assert len(rows) == 9
    assert all(set(row) == {"Norman_language", "BHSM_mathematics", "status"} for row in rows)
    assert payload["ontology_consistent"] is True


def test_theorem_package_has_all_22_exact_gates() -> None:
    package = theorem_package()
    assert list(package) == [f"N{index}" for index in range(1, 23)]
    assert package["N4"]["status"] == "DERIVED"
    assert package["N22"]["result"] == "FULL_BHSM_COMPLETE_FALSE"


def test_all_required_failure_classes_are_exact() -> None:
    assert len(FAILURE_CLASSES) == len(set(FAILURE_CLASSES))
    assert "MORE_WORK_NEEDED" not in FAILURE_CLASSES
    assert "DE_ENVELOPMENT_RULE_NOT_ACTION_DERIVED" in FAILURE_CLASSES
    assert "ENCAPSULATION_COMPLETION_NOT_DERIVED" in FAILURE_CLASSES


def test_master_solution_count_remains_undefined_not_zero_or_one() -> None:
    payload = master_self_reconstruction_payload()
    assert payload["physical_master_solution_count"] == "UNDEFINED_MISSING_UPSTREAM_STRUCTURE"
    assert payload["gauge_quotiented_master_solution_count"] == "UNDEFINED_MISSING_UPSTREAM_STRUCTURE"
    assert payload["master_self_reconstruction_map_exists"] is False


def test_completion_gate_has_exactly_30_conditions_and_fails_closed() -> None:
    conditions = completion_conditions()
    assert len(conditions) == 30
    assert conditions["no_empirical_tuning"] is True
    assert conditions["action_derived_formation_map"] is False
    assert full_completion_payload()["FULL_BHSM_COMPLETE"] is False


def test_regular_identity_recovery_is_preserved_without_false_closure() -> None:
    regular = full_completion_payload()["regular_BHSM"]
    assert regular["identity_limit_recovery"] == "EXACT_UNCHANGED"
    assert regular["gauge_normalization"] == BLOCKED
    assert regular["encapsulation"].startswith("BLOCKED_V14_94")


def test_exact_next_object_is_single_and_refines_v15_5_object() -> None:
    payload = full_completion_payload()
    assert payload["Hindsight_20_20"]["OPEN"] == [EXACT_NEXT_OBJECT]
    assert "NORMAN_CYCLE_BOUNDARY_VALUE_PROBLEM" in EXACT_NEXT_OBJECT
    assert "LOOP" in V15_5_NEXT_OBJECT


def test_hindsight_has_exact_required_sections() -> None:
    hindsight = full_completion_payload()["Hindsight_20_20"]
    assert set(hindsight) == {"VALIDATED", "INVALIDATED", "RECLASSIFIED", "OPEN"}
    assert all(hindsight[section] for section in hindsight)


def test_campaign_records_usb_untouched() -> None:
    assert full_completion_payload()["USB_touched_during_campaign"] is False


def test_artifact_package_has_exact_dense_scope_and_strict_json() -> None:
    payloads = artifact_payloads()
    assert len(payloads) == 10
    assert set(payloads) == {
        "BHSM_norman_cycle_ontology_v15_6.json",
        "BHSM_norman_formation_gate_v15_6.json",
        "BHSM_norman_de_envelopment_gate_v15_6.json",
        "BHSM_parent_invariant_ledger_v15_6.json",
        "BHSM_primitive_loop_monodromy_v15_6.json",
        "BHSM_primitive_to_floquet_reconstruction_v15_6.json",
        "BHSM_z2_z3_full_cycle_killscreen_v15_6.json",
        "BHSM_state_gns_cycle_selection_v15_6.json",
        "BHSM_master_self_reconstruction_v15_6.json",
        "BHSM_full_completion_gate_v15_6.json",
    }
    for payload in payloads.values():
        assert json.loads(deterministic_json(payload)) == payload


def test_materialization_is_byte_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    paths_a = materialize(first)
    paths_b = materialize(second)
    hashes_a = [hashlib.sha256(path.read_bytes()).hexdigest() for path in paths_a]
    hashes_b = [hashlib.sha256(path.read_bytes()).hexdigest() for path in paths_b]
    assert [path.name for path in paths_a] == [path.name for path in paths_b]
    assert hashes_a == hashes_b


def test_artifacts_contain_no_prohibited_selection_claims() -> None:
    corpus = "\n".join(deterministic_json(payload) for payload in artifact_payloads().values())
    prohibited = (
        '"selected_by_generation_count": true',
        '"selected_by_minimal_dimension": true',
        '"D_equals_F_inverse": true',
        '"D_equals_F_dagger": true',
        '"FULL_BHSM_COMPLETE": true',
    )
    assert all(token not in corpus for token in prohibited)


def test_frozen_predictions_and_official_logic_remain_byte_exact() -> None:
    paths = (
        ROOT / "artifacts" / "frozen_predictions.json",
        ROOT / "src" / "bhsm" / "prediction_logic.py",
    )
    before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths if path.exists()}
    artifact_payloads()
    after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths if path.exists()}
    assert before == after
