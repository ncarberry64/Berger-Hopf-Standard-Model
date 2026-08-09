from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from bhsm.interface.aether_event_algebra_state_v15_4 import (
    GroupoidArrow,
    basis_element,
    canonical_density_blocks,
    event_identity,
    nontracial_invariant_density_blocks,
    state_value,
)
from bhsm.interface.aether_master_closure_v15_5 import (
    BLOCKED,
    CONDITIONAL,
    EXACT_NEXT_OBJECT,
    FORBIDDEN_SELECTION_RULES,
    GAUGE_QUOTIENTED_MASTER_SOLUTION_COUNT,
    NONUNIQUE,
    OUTCOME,
    PHYSICAL_MASTER_SOLUTION_COUNT,
    PRIMARY_VERDICT,
    SECONDARY_OUTCOME,
    UNIQUE_ACTUALIZATION_PRINCIPLE_STATUS,
    artifact_payloads,
    clock_scale_payload,
    commuting_diagram_payload,
    completion_conditions,
    deterministic_json,
    dirichlet_selection_payload,
    fixed_point_stability_payload,
    fixed_point_uniqueness_payload,
    foundational_state_payload,
    full_completion_payload,
    geometry_reconstruction_payload,
    gns_inner_product,
    master_components,
    master_constraint_payload,
    materialize,
    regular_action_ownership_payload,
    reset_dirichlet_form,
    reset_generator,
    reset_semigroup,
    self_reconstruction_payload,
    state_dynamics_diagnostics,
    state_dynamics_fixed_point_payload,
    z2_z3_closure_matrix_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def densities(order: int, kind: str) -> tuple[np.ndarray, ...]:
    if kind == "canonical_trace":
        return canonical_density_blocks(order)
    return nontracial_invariant_density_blocks(order)


@pytest.mark.parametrize("rule", FORBIDDEN_SELECTION_RULES)
def test_forbidden_unique_actualization_cheats_are_explicit(rule: str) -> None:
    assert rule


@pytest.mark.parametrize("order", [2, 3])
@pytest.mark.parametrize("kind", ["canonical_trace", "fixed_nontracial"])
def test_reset_generator_annihilates_identity(order: int, kind: str) -> None:
    rho = densities(order, kind)
    assert np.allclose(reset_generator(event_identity(order), rho, order), 0.0)


@pytest.mark.parametrize("order", [2, 3])
@pytest.mark.parametrize("kind", ["canonical_trace", "fixed_nontracial"])
def test_reset_semigroup_identity_and_state_invariance(order: int, kind: str) -> None:
    rho = densities(order, kind)
    value = basis_element(GroupoidArrow(0, 0, 1), order) + 2j * basis_element(GroupoidArrow(2, 1, 3), order)
    assert np.allclose(reset_semigroup(value, rho, order, 0.0), value)
    evolved = reset_semigroup(value, rho, order, 0.73)
    assert state_value(evolved, rho, order) == pytest.approx(state_value(value, rho, order))
    assert np.allclose(reset_semigroup(event_identity(order), rho, order, 0.73), event_identity(order))


@pytest.mark.parametrize("order", [2, 3])
@pytest.mark.parametrize("kind", ["canonical_trace", "fixed_nontracial"])
def test_reset_semigroup_composition(order: int, kind: str) -> None:
    rho = densities(order, kind)
    value = basis_element(GroupoidArrow(1, 1, 2), order)
    lhs = reset_semigroup(reset_semigroup(value, rho, order, 0.4), rho, order, 0.7)
    rhs = reset_semigroup(value, rho, order, 1.1)
    assert np.allclose(lhs, rhs)


def test_negative_semigroup_parameter_is_rejected() -> None:
    with pytest.raises(ValueError, match="nonnegative"):
        reset_semigroup(event_identity(2), canonical_density_blocks(2), 2, -0.1)


@pytest.mark.parametrize("order", [2, 3])
@pytest.mark.parametrize("kind", ["canonical_trace", "fixed_nontracial"])
def test_reset_dirichlet_form_is_positive(order: int, kind: str) -> None:
    rho = densities(order, kind)
    value = (
        basis_element(GroupoidArrow(0, 0, 1), order)
        + (1.0 + 2.0j) * basis_element(GroupoidArrow(2, 1, 3), order)
        - 0.25 * event_identity(order)
    )
    energy = reset_dirichlet_form(value, value, rho, order)
    assert energy.imag == pytest.approx(0.0, abs=1e-12)
    assert energy.real >= -1e-12
    assert reset_dirichlet_form(event_identity(order), event_identity(order), rho, order) == pytest.approx(0.0)


@pytest.mark.parametrize("order", [2, 3])
@pytest.mark.parametrize("kind", ["canonical_trace", "fixed_nontracial"])
def test_reset_generator_is_gns_symmetric(order: int, kind: str) -> None:
    rho = densities(order, kind)
    left = basis_element(GroupoidArrow(0, 1, 2), order) + event_identity(order)
    right = basis_element(GroupoidArrow(3, 0, 1), order) + 1j * event_identity(order)
    lhs = gns_inner_product(left, reset_generator(right, rho, order), rho, order)
    rhs = gns_inner_product(reset_generator(left, rho, order), right, rho, order)
    assert lhs == pytest.approx(rhs)


@pytest.mark.parametrize("order", [2, 3])
@pytest.mark.parametrize("kind", ["canonical_trace", "fixed_nontracial"])
def test_state_dynamics_diagnostics_are_strong_but_unowned(order: int, kind: str) -> None:
    payload = state_dynamics_diagnostics(order, kind)
    assert payload["state_positive"] is True
    assert payload["state_faithful"] is True
    assert payload["reset_semigroup_completely_positive"] is True
    assert payload["GNS_detailed_balance"] is True
    assert payload["primitive"] is True
    assert payload["unique_invariant_state"] is True
    assert payload["dual_generator_kernel_dimension_on_states"] == 1
    assert payload["dimensionless_spectral_gap"] == 1
    assert payload["semigroup_parameter_is_clock"] is False
    assert payload["generator_action_owned"] is False


def test_master_state_stops_at_first_foundational_arrow() -> None:
    payload = foundational_state_payload()
    assert payload["derived_prefix"] == ["four_object_incidence_grammar", "category_composition", "object_identities"]
    assert payload["first_missing_arrow"] == "event_category_skeleton_to_action_selected_reversible_category_with_loop_spectrum"
    assert payload["foundational_status"]["dagger"] == NONUNIQUE
    assert payload["foundational_status"]["positive_state"] == NONUNIQUE
    assert payload["unique_actualization_principle_status"] == UNIQUE_ACTUALIZATION_PRINCIPLE_STATUS


def test_master_constraint_is_typed_and_fails_closed() -> None:
    payload = master_constraint_payload()
    assert payload["component_count"] == 18
    assert len(master_components()) == 18
    assert payload["all_components_vanish"] is False
    assert payload["first_failed_component"] == "dagger"
    assert payload["master_closure_map_exists"] is False
    assert {row["name"] for row in payload["components"]} >= {"composition", "action", "clock", "self_reconstruction"}


def test_commuting_diagram_has_missing_forward_and_feedback_arrows() -> None:
    payload = commuting_diagram_payload()
    assert payload["forward_chain_complete"] is False
    assert payload["feedback_chain_complete"] is False
    assert payload["master_map_constructible"] is False
    assert any(row == {"source": "regular_BHSM", "target": "reconstructed_event_category", "status": BLOCKED} for row in payload["arrows"])


def test_z2_z3_are_incompleteness_witnesses_not_choices() -> None:
    payload = z2_z3_closure_matrix_payload()
    assert len(payload["candidates"]) == 4
    assert {row["GNS_rank"] for row in payload["candidates"]} == {32, 48}
    assert all(row["is_physical_master_solution"] is False for row in payload["candidates"])
    assert all(row["first_failure_class"] == "UNOWNED_PARAMETER_DEPENDENCE" for row in payload["candidates"])
    assert payload["neither_is_action_eliminated_relative_to_the_other"] is True
    assert payload["interpretation"] == "INCOMPLETENESS_WITNESSES_NOT_PHYSICAL_CHOICES"


def test_joint_state_dynamics_fixed_point_does_not_select() -> None:
    payload = state_dynamics_fixed_point_payload()
    assert len(payload["witnesses"]) == 4
    assert payload["state_dynamics_fixed_pair_cardinality"].startswith("CONTINUOUS")
    assert payload["stationarity_selects_state"] is False
    assert payload["detailed_balance_selects_state"] is False
    assert payload["primitivity_selects_state"] is False
    assert payload["unique_invariant_state_for_each_generator_selects_joint_pair"] is False


def test_dirichlet_gate_distinguishes_existence_from_selection() -> None:
    payload = dirichlet_selection_payload()
    assert payload["finite_dimensional_forms_closed"] is True
    assert payload["forms_positive"] is True
    assert payload["associated_generators_self_adjoint_in_GNS"] is True
    assert payload["Markov_semigroups_completely_positive_unital"] is True
    assert payload["action_owned"] is False
    assert payload["unique_form_selected"] is False


def test_geometry_reconstruction_is_not_bidirectional() -> None:
    payload = geometry_reconstruction_payload()
    assert payload["objects"] == ["M8", "M5_plus", "M5_minus", "M4"]
    assert len(payload["incidence_edges"]) == 4
    assert payload["conditional_forgetful_incidence_quotient"] == "DERIVED"
    assert payload["geometry_core_correspondence_action_owned"] is False
    assert payload["regular_to_foundation_return_functor_action_owned"] is False
    assert payload["bidirectional_reconstruction"] is False


def test_self_reconstruction_and_fixed_point_count_are_undefined_not_zero() -> None:
    reconstruction = self_reconstruction_payload()
    count = fixed_point_uniqueness_payload()
    assert reconstruction["master_map_exists"] is False
    assert reconstruction["self_reconstruction_map_exists"] is False
    assert reconstruction["fixed_points_exist"] == "UNDEFINED_MISSING_UPSTREAM_STRUCTURE"
    assert count["physical_master_solution_count"] == PHYSICAL_MASTER_SOLUTION_COUNT
    assert count["gauge_quotiented_master_solution_count"] == GAUGE_QUOTIENTED_MASTER_SOLUTION_COUNT
    assert count["count_is_one"] is False
    assert count["count_is_zero"] is False


def test_fixed_point_stability_is_not_evaluable() -> None:
    payload = fixed_point_stability_payload()
    assert payload["stability"] == "NOT_EVALUABLE_NO_MASTER_MAP_OR_FIXED_POINT"
    assert payload["reset_witness_semigroup_stable"] is True
    assert payload["reset_witness_stability_is_physical_actualization"] is False


def test_clock_and_scale_remain_unowned() -> None:
    payload = clock_scale_payload()
    assert payload["reference_clock"] == BLOCKED
    assert payload["stable_action_owned_recurrence"] is False
    assert payload["absolute_dimensionful_scale"] == BLOCKED
    assert payload["seconds_meters_eV_GeV_generated_internally"] is False
    assert payload["hbar_is_only_unit_conversion_not_scale_ownership"] is True
    assert payload["failure_classes"] == ["NO_STABLE_CLOCK", "NO_DIMENSIONFUL_SCALE"]


@pytest.mark.parametrize(
    "field",
    [
        "gauge_normalization",
        "scalar_topographic_action_source",
        "mass_bridge",
        "CKM_provenance",
        "PMNS_neutral_provenance",
        "neutrino_scale",
        "encapsulation_bridge",
    ],
)
def test_regular_physics_ownership_remains_blocked(field: str) -> None:
    assert regular_action_ownership_payload()[field].startswith("BLOCKED")


def test_encapsulation_object_is_preserved_exactly() -> None:
    payload = regular_action_ownership_payload()
    assert payload["encapsulation_exact_object"] == "CONSTRAINT_SOLVED_NONHOMOGENEOUS_LORENTZIAN_M8_INCOMING_WAVE_PACKET_WITH_QUASILOCAL_NOETHER_FLUX_TIME_PRESERVED_COMMON_DOMAIN_AND_LOCAL_PHYSICAL_TANGENT_PROPAGATOR"


def test_strict_completion_boolean_fails_if_any_essential_gate_fails() -> None:
    conditions = completion_conditions()
    assert len(conditions) == 25
    assert conditions["no_empirical_fitting"] is True
    assert conditions["frozen_prediction_integrity"] is True
    assert conditions["unique_foundational_event_structure_modulo_gauge"] is False
    assert all(conditions.values()) is False


def test_full_completion_payload_preserves_claim_boundary() -> None:
    payload = full_completion_payload()
    assert payload["primary_verdict"] == PRIMARY_VERDICT
    assert payload["outcome"] == OUTCOME
    assert payload["secondary_outcome"] == SECONDARY_OUTCOME
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["physical_master_solution_count"] == "UNDEFINED_MISSING_UPSTREAM_STRUCTURE"
    assert payload["gauge_quotiented_master_solution_count"] == "UNDEFINED_MISSING_UPSTREAM_STRUCTURE"
    assert payload["master_closure_map_exists"] is False
    assert payload["self_reconstruction_map_exists"] is False
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT
    assert payload["Hindsight_20_20"]["OPEN"] == [EXACT_NEXT_OBJECT]
    assert payload["validation_passed"] is True


def test_integrity_firewalls_add_no_inputs_parameters_fields_or_frame() -> None:
    payload = full_completion_payload()
    assert payload["new_empirical_inputs"] is False
    assert payload["new_fitted_parameters"] is False
    assert payload["new_arbitrary_continuous_parameters"] is False
    assert payload["new_primitive_fields"] is False
    assert payload["preferred_frame"] is False
    assert payload["frozen_predictions_changed"] is False
    assert payload["official_prediction_logic_changed"] is False


def test_artifact_package_has_exact_scope_and_strict_json() -> None:
    payloads = artifact_payloads()
    assert len(payloads) == 13
    assert set(payloads) == {
        "BHSM_master_foundational_state_v15_5.json",
        "BHSM_master_closure_constraint_v15_5.json",
        "BHSM_master_commuting_diagram_v15_5.json",
        "BHSM_master_z2_z3_closure_matrix_v15_5.json",
        "BHSM_master_state_dynamics_fixed_point_v15_5.json",
        "BHSM_master_dirichlet_selection_v15_5.json",
        "BHSM_master_geometry_reconstruction_v15_5.json",
        "BHSM_master_self_reconstruction_v15_5.json",
        "BHSM_master_fixed_point_uniqueness_v15_5.json",
        "BHSM_master_fixed_point_stability_v15_5.json",
        "BHSM_master_clock_scale_gate_v15_5.json",
        "BHSM_master_regular_action_ownership_v15_5.json",
        "BHSM_master_full_completion_gate_v15_5.json",
    }
    for payload in payloads.values():
        assert json.loads(deterministic_json(payload)) == payload


def test_materialization_is_byte_deterministic(tmp_path: Path) -> None:
    first = {path.name: path.read_bytes() for path in materialize(tmp_path)}
    second = {path.name: path.read_bytes() for path in materialize(tmp_path)}
    assert first == second
    assert len(first) == 13
    for name, raw in first.items():
        assert json.loads(raw) == artifact_payloads()[name]


def test_artifacts_do_not_hide_selection_or_empirical_inputs() -> None:
    text = json.dumps(artifact_payloads(), sort_keys=True).lower()
    for forbidden in (
        "three_generations_select_z3",
        "minimum_dimension_selects_z2",
        "measured_ckm",
        "measured_pmns",
        "measured_higgs",
        "external_clock_parameter",
        "preferred_aether_frame",
        "full_bhsm_complete\": true",
    ):
        assert forbidden not in text


def test_frozen_predictions_and_official_logic_remain_byte_exact() -> None:
    expected = {
        "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
        "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
        "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
        "src/bhsm/interface/predictions.py": "ea0539bef06184c619dd028eafafb76ea15e92a444483ff93637593f0eaa1fed",
        "artifacts/CKM_no_fit_operator_output_v1.json": "9c354e8812682c75187c00becb90ff44b5dcc74aef10992103df28b34321d757",
    }
    for relative, digest in expected.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
