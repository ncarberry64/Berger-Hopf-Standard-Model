from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from bhsm.interface.aether_event_algebra_state_v15_4 import (
    CAP_REFLECTION,
    DIAMOND_EDGES,
    EXACT_NEXT_OBJECT,
    FORBIDDEN_CORE_PRIMITIVES,
    OBJECTS,
    OUTCOME,
    PRIMARY_VERDICT,
    SECONDARY_OUTCOME,
    GroupoidArrow,
    artifact_payloads,
    automorphism_state_payload,
    basis_element,
    candidate_classification_payload,
    canonical_density_blocks,
    canonical_state_value,
    cyclic_units,
    dagger_payload,
    dirichlet_readiness_payload,
    event_algebra_payload,
    event_dagger,
    event_identity,
    event_product,
    fourier_blocks,
    gns_diagnostics,
    groupoid_basis,
    identity_arrows,
    incidence_reconstruction_payload,
    invariant_state_dimensions,
    killscreen_payload,
    materialize,
    modular_diagnostics,
    nontracial_invariant_density_blocks,
    reverse_arrow,
    state_cone_payload,
    state_invariance_residual,
    state_value,
    transform_element,
    tracial_modular_payload,
    validate_density_blocks,
    seventeen_gate_payload,
    completion_payload,
    compose_arrows,
)


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "primitive",
    [
        "spacetime_coordinate",
        "coordinate_time",
        "metric_tensor",
        "spacetime_volume_measure",
        "ordinary_energy",
        "preferred_frame",
        "measured_particle_count",
    ],
)
def test_pregeometric_firewall_contains_required_primitive(primitive: str) -> None:
    assert primitive in FORBIDDEN_CORE_PRIMITIVES


def test_groupoid_basis_has_expected_dimensions() -> None:
    assert len(groupoid_basis(2)) == 32
    assert len(groupoid_basis(3)) == 48


def test_arrow_composition_and_noncomposable_zero() -> None:
    a = GroupoidArrow(1, 1, 0)
    b = GroupoidArrow(3, 2, 1)
    assert compose_arrows(b, a, 3) == GroupoidArrow(3, 0, 0)
    assert compose_arrows(a, b, 3) is None


def test_arrow_composition_is_associative() -> None:
    a = GroupoidArrow(1, 1, 0)
    b = GroupoidArrow(2, 2, 1)
    c = GroupoidArrow(3, 1, 2)
    left = compose_arrows(compose_arrows(c, b, 3), a, 3)
    right = compose_arrows(c, compose_arrows(b, a, 3), 3)
    assert left == right == GroupoidArrow(3, 1, 0)


def test_object_identities_act_as_identities() -> None:
    arrow = GroupoidArrow(2, 1, 0)
    identities = identity_arrows(3)
    assert compose_arrows(identities[2], arrow, 3) == arrow
    assert compose_arrows(arrow, identities[0], 3) == arrow


@pytest.mark.parametrize("order", [2, 3])
def test_linear_event_identity(order: int) -> None:
    rng = np.random.default_rng(154 + order)
    value = rng.normal(size=(4, order, 4)) + 1j * rng.normal(size=(4, order, 4))
    identity = event_identity(order)
    assert event_product(identity, value, order) == pytest.approx(value)
    assert event_product(value, identity, order) == pytest.approx(value)


@pytest.mark.parametrize("order", [2, 3])
def test_linear_event_product_is_associative(order: int) -> None:
    rng = np.random.default_rng(1540 + order)
    values = [rng.normal(size=(4, order, 4)) + 1j * rng.normal(size=(4, order, 4)) for _ in range(3)]
    left = event_product(event_product(values[0], values[1], order), values[2], order)
    right = event_product(values[0], event_product(values[1], values[2], order), order)
    assert left == pytest.approx(right, abs=1e-11)


@pytest.mark.parametrize("order", [2, 3])
def test_dagger_is_involutive(order: int) -> None:
    rng = np.random.default_rng(1550 + order)
    value = rng.normal(size=(4, order, 4)) + 1j * rng.normal(size=(4, order, 4))
    assert event_dagger(event_dagger(value, order), order) == pytest.approx(value)


@pytest.mark.parametrize("order", [2, 3])
def test_dagger_is_anti_multiplicative(order: int) -> None:
    rng = np.random.default_rng(1560 + order)
    left = rng.normal(size=(4, order, 4)) + 1j * rng.normal(size=(4, order, 4))
    right = rng.normal(size=(4, order, 4)) + 1j * rng.normal(size=(4, order, 4))
    actual = event_dagger(event_product(left, right, order), order)
    expected = event_product(event_dagger(right, order), event_dagger(left, order), order)
    assert actual == pytest.approx(expected, abs=1e-11)


def test_dagger_is_antilinear() -> None:
    rng = np.random.default_rng(1570)
    left = rng.normal(size=(4, 3, 4)) + 1j * rng.normal(size=(4, 3, 4))
    right = rng.normal(size=(4, 3, 4)) + 1j * rng.normal(size=(4, 3, 4))
    alpha = 0.3 + 0.7j
    beta = -0.2j
    actual = event_dagger(alpha * left + beta * right, 3)
    expected = np.conj(alpha) * event_dagger(left, 3) + np.conj(beta) * event_dagger(right, 3)
    assert actual == pytest.approx(expected)


@pytest.mark.parametrize("order", [2, 3])
def test_fourier_blocks_intertwine_product_and_dagger(order: int) -> None:
    rng = np.random.default_rng(1580 + order)
    left = rng.normal(size=(4, order, 4)) + 1j * rng.normal(size=(4, order, 4))
    right = rng.normal(size=(4, order, 4)) + 1j * rng.normal(size=(4, order, 4))
    product_blocks = fourier_blocks(event_product(left, right, order), order)
    left_blocks = fourier_blocks(left, order)
    right_blocks = fourier_blocks(right, order)
    dagger_blocks = fourier_blocks(event_dagger(left, order), order)
    for product, a, b, star in zip(product_blocks, left_blocks, right_blocks, dagger_blocks):
        assert product == pytest.approx(a @ b, abs=1e-10)
        assert star == pytest.approx(a.conj().T, abs=1e-10)


@pytest.mark.parametrize("order", [2, 3])
def test_canonical_state_is_normalized_positive_and_faithful(order: int) -> None:
    densities = canonical_density_blocks(order)
    diagnostics = validate_density_blocks(densities, order)
    assert diagnostics["normalized"] is True
    assert diagnostics["positive"] is True
    assert diagnostics["faithful"] is True
    assert canonical_state_value(event_identity(order), order) == pytest.approx(1.0)
    rng = np.random.default_rng(1590 + order)
    value = rng.normal(size=(4, order, 4)) + 1j * rng.normal(size=(4, order, 4))
    square = event_product(event_dagger(value, order), value, order)
    assert canonical_state_value(square, order).real > 0.0


@pytest.mark.parametrize("order", [2, 3])
def test_fixed_nontracial_state_is_positive_faithful_and_nontracial(order: int) -> None:
    densities = nontracial_invariant_density_blocks(order)
    diagnostics = validate_density_blocks(densities, order)
    assert diagnostics["normalized"] and diagnostics["positive"] and diagnostics["faithful"]
    a = basis_element(GroupoidArrow(0, 0, 1), order)
    b = basis_element(GroupoidArrow(1, 0, 0), order)
    assert state_value(event_product(a, b, order), densities, order) != pytest.approx(
        state_value(event_product(b, a, order), densities, order)
    )


@pytest.mark.parametrize("order", [2, 3])
def test_fixed_states_are_invariant_under_cap_and_cyclic_relabeling(order: int) -> None:
    for densities in (canonical_density_blocks(order), nontracial_invariant_density_blocks(order)):
        for unit in cyclic_units(order):
            assert state_invariance_residual(densities, order, loop_multiplier=unit) < 1e-11


def test_transform_rejects_nonautomorphism_multiplier() -> None:
    with pytest.raises(ValueError):
        transform_element(event_identity(2), 2, loop_multiplier=0)


def test_positive_and_invariant_state_dimensions_are_continuous() -> None:
    assert invariant_state_dimensions(2) == {
        "all_states_affine_dimension": 31,
        "faithful_states_manifold_dimension": 31,
        "cap_reflection_invariant_affine_dimension": 19,
        "cap_and_cyclic_inversion_invariant_affine_dimension": 19,
        "tracial_state_simplex_dimension": 1,
    }
    assert invariant_state_dimensions(3)["all_states_affine_dimension"] == 47
    assert invariant_state_dimensions(3)["cap_reflection_invariant_affine_dimension"] == 29
    assert invariant_state_dimensions(3)["cap_and_cyclic_inversion_invariant_affine_dimension"] == 19


@pytest.mark.parametrize(("order", "dimension"), [(2, 32), (3, 48)])
def test_gns_rank_null_ideal_and_faithfulness(order: int, dimension: int) -> None:
    for canonical in (True, False):
        payload = gns_diagnostics(order, canonical=canonical)
        assert payload["GNS_dimension"] == dimension
        assert payload["GNS_Gram_rank"] == dimension
        assert payload["null_ideal_dimension"] == 0
        assert payload["representation_faithful"] is True
        assert payload["cyclic_span_dimension"] == dimension


def test_left_regular_representation_homomorphism() -> None:
    rng = np.random.default_rng(1600)
    a = rng.normal(size=(4, 2, 4)) + 1j * rng.normal(size=(4, 2, 4))
    b = rng.normal(size=(4, 2, 4)) + 1j * rng.normal(size=(4, 2, 4))
    c = rng.normal(size=(4, 2, 4)) + 1j * rng.normal(size=(4, 2, 4))
    left = event_product(a, event_product(b, c, 2), 2)
    right = event_product(event_product(a, b, 2), c, 2)
    assert left == pytest.approx(right, abs=1e-11)


def test_modular_flow_is_diagnostic_not_time() -> None:
    payload = modular_diagnostics(3)
    assert payload["canonical_trace_modular_operator"] == "IDENTITY"
    assert payload["nontrivial_finite_modular_dynamics_available_conditionally"] is True
    assert payload["modular_flow_is_physical_time"] is False


def test_candidate_classification_retains_category_before_algebra() -> None:
    payload = candidate_classification_payload()
    assert len(payload["candidates"]) == 6
    assert payload["architecture_retained_object"].startswith("complex_linear_category")
    assert payload["physical_event_algebra_selected"] is False
    assert payload["candidates"][5]["candidate"] == "F_reuse_regular_BHSM_finite_algebra"


def test_event_algebra_multiplication_is_derived_but_completion_is_not() -> None:
    payload = event_algebra_payload()
    assert payload["multiplication_architecture_derived"] is True
    assert payload["associative"] is True
    assert payload["physical_allowed_morphism_set_selected"] is False
    assert payload["group_groupoid_or_path_completion_unique"] is False


def test_dagger_exists_conditionally_not_physically() -> None:
    payload = dagger_payload()
    assert payload["compatible_dagger_exists_on_each_groupoid_witness"] is True
    assert payload["event_reversal_functor_action_derived"] is False
    assert payload["physical_dagger_uniquely_selected"] is False
    assert "regular_boundary_Z2" in payload["historical_orientation_Iota_scope"]


def test_state_cones_do_not_select_a_state() -> None:
    payload = state_cone_payload()
    assert payload["positive_state_selected"] is False
    assert payload["faithful_state_selected"] is False
    assert all(row["all_states_affine_dimension"] > 0 for row in payload["witnesses"])


def test_automorphism_invariance_does_not_close_selection() -> None:
    payload = automorphism_state_payload()
    assert payload["symmetry_invariance_uniquely_selects_physical_state"] is False
    assert all(row["BHSM_action_owned_core_automorphism_group"] == "NONE_DERIVED" for row in payload["witnesses"])
    assert all(row["all_star_automorphisms_are_physical_BHSM_symmetries"] is False for row in payload["witnesses"])


def test_traciality_is_not_derived() -> None:
    payload = tracial_modular_payload()
    assert payload["traciality_action_derived"] is False
    assert payload["nontracial_faithful_invariant_states_survive"] is True
    assert [row["simplex_dimension"] for row in payload["tracial_state_spaces"]] == [1, 2]


def test_incidence_reconstruction_is_shared_but_conditional() -> None:
    payload = incidence_reconstruction_payload()
    assert payload["both_witnesses_reconstruct_same_incidence"] is True
    assert payload["incidence_distinguishes_Z2_from_Z3"] is False
    assert payload["canonical_map_to_regular_BHSM_finite_algebra_exists"] is False
    for row in payload["witnesses"]:
        assert tuple(row["objects"]) == OBJECTS
        assert tuple(tuple(edge) for edge in row["distinguished_incidence_edges"]) == DIAMOND_EDGES
        assert row["exact_BHSM_diamond_grammar_recovered"] is True
        assert row["incidence_reconstruction_map_action_derived"] is False


def test_z2_z3_killscreen_survives_all_legitimate_quotients() -> None:
    payload = killscreen_payload()
    assert payload["both_survive"] is True
    assert payload["star_isomorphic"] is False
    assert payload["event_relabeling_equivalent"] is False
    assert payload["structured_GNS_equivalent"] is False
    assert [row["canonical_GNS_dimension"] for row in payload["witnesses"]] == [32, 48]
    assert payload["outcome"] == OUTCOME


def test_dirichlet_forms_are_ready_but_not_selected() -> None:
    payload = dirichlet_readiness_payload()
    assert payload["closed_invariant_Dirichlet_forms_exist_for_each_witness"] is True
    assert payload["Dirichlet_form_uniqueness"] is False
    assert payload["generator_selected"] is False


def test_seventeen_gates_fail_closed_at_selection() -> None:
    payload = seventeen_gate_payload()
    assert payload["T1_event_composition_algebra"].startswith("CATEGORY_COMPOSITION_DERIVED")
    assert payload["T13_Z2_Z3"].startswith("BOTH_SURVIVE")
    assert payload["T17_foundational_selection"].startswith("UNDEFINED")
    assert payload["outcome"] == OUTCOME
    assert payload["secondary_outcome"] == SECONDARY_OUTCOME


def test_completion_gate_preserves_exact_claim_boundary() -> None:
    payload = completion_payload()
    assert payload["primary_verdict"] == PRIMARY_VERDICT
    assert payload["outcome"] == OUTCOME
    assert payload["secondary_outcome"] == SECONDARY_OUTCOME
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT
    assert payload["event_multiplication_derived"] is True
    assert payload["event_algebra_uniquely_selected"] is False
    assert payload["compatible_dagger_exists"] is True
    assert payload["physical_dagger_uniquely_selected"] is False
    assert payload["distinguished_positive_state_uniquely_selected"] is False
    assert payload["GNS_representation_uniquely_selected"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["validation_passed"] is True


def test_no_parameter_field_frame_or_empirical_input_is_added() -> None:
    payload = completion_payload()
    assert payload["new_continuous_parameter_introduced"] is False
    assert payload["new_fundamental_dynamical_field_introduced"] is False
    assert payload["preferred_frame_introduced"] is False
    assert payload["empirical_inputs_used"] is False


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


def test_artifacts_contain_no_forbidden_physics_or_numerology() -> None:
    text = json.dumps(artifact_payloads(), sort_keys=True).lower()
    for forbidden in (
        "ckm_input",
        "pmns_input",
        "measured_mass",
        "higgs_target",
        "cosmological_fit",
        "three_generations_select_z3",
        "integral_over_core_spacetime",
    ):
        assert forbidden not in text


def test_materialization_is_deterministic_and_strict_json(tmp_path: Path) -> None:
    first_paths = materialize(tmp_path)
    first = {path.name: path.read_bytes() for path in first_paths}
    second_paths = materialize(tmp_path)
    second = {path.name: path.read_bytes() for path in second_paths}
    assert first == second
    assert set(first) == set(artifact_payloads())
    assert len(first) == 10
    for name, raw in first.items():
        assert json.loads(raw) == artifact_payloads()[name]
