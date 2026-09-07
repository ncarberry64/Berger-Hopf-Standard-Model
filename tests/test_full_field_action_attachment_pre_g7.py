from __future__ import annotations

import hashlib
import importlib.util
import json
from dataclasses import replace
from pathlib import Path

import jax.numpy as jnp
import numpy as np
import pytest

from bhsm.interface.aether_jax_full_local_action import (
    MDIM,
    POINTS,
    QDIM,
    STATE_DIMENSION,
    action_value,
)
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (
    exact_full_action_jet_at_state,
)
from bhsm.interface.full_field_action_attachment_pre_g7 import (
    ActionComponent,
    BackgroundState,
    BoundBackground,
    BlockStatus,
    FullFieldBackgroundBinder,
    MissingActionSourceError,
    PreparedBRSTInterface,
    PreparedHSDirectionInterface,
    PreparedMomentumSymbolInterface,
    PreparedReplacementSaddleInterface,
    UniversalFullFieldAction,
    authoritative_field_registry,
    current_pre_g7_attachment,
    koszul_permutation_sign,
    response_artifact_rejection_witness,
)


ROOT = Path(__file__).resolve().parents[1]
MATERIALIZER = ROOT / "scripts" / "materialize_bhsm_full_field_action_attachment_pre_g7.py"
ARTIFACT = ROOT / "artifacts" / "action_extension" / "BHSM_FULL_FIELD_ACTION_ATTACHMENT_PRE_G7.json"


def _materializer_module():
    spec = importlib.util.spec_from_file_location("full_field_pre_g7_materializer", MATERIALIZER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _portable_source_sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _geometry_state(registry):
    state = np.zeros(registry.dimension)
    state[0] = 0.02
    state[3] = -0.01
    return state


def _geometry_direction(registry, first: int = 0):
    direction = np.zeros(registry.dimension)
    direction[first] = 1.0
    return direction


def test_registry_is_deterministic_contiguous_and_projectable() -> None:
    first = authoritative_field_registry()
    second = authoritative_field_registry()
    assert first.metadata() == second.metadata()
    assert first.block("constraint_multiplier").stop == STATE_DIMENSION == 98
    assert first.block("gauge").dimension == 12
    assert first.block("fermion").dimension == 48
    assert first.block("HS_scalar").dimension == 4
    assert first.block("geometry").coordinate_labels[:3] == ("scale", "u_1", "u_2")
    assert first.block("geometry").coordinate_labels[-1] == "v_11"
    assert first.block("constraint_multiplier").coordinate_labels[:2] == (
        "lapse_1",
        "lapse_2",
    )
    assert first.block("constraint_multiplier").coordinate_labels[-1] == "shift_11"
    for block in first.blocks:
        restriction = first.restriction(block.name)
        projector = first.projector(block.name)
        assert restriction.shape == (block.dimension, first.dimension)
        assert projector.shape == (first.dimension, first.dimension)
        np.testing.assert_array_equal(projector @ projector, projector)
        np.testing.assert_array_equal(projector, restriction.T @ restriction)
        assert len(block.coordinate_labels) == block.dimension
    family_zero = tuple(
        label for label in first.block("fermion").coordinate_labels if ":family_0:" in label
    )
    family_projector = first.coordinate_projector("fermion", family_zero)
    assert np.trace(family_projector) == 16
    np.testing.assert_array_equal(family_projector @ family_projector, family_projector)
    assert not first.metadata()["physical_discretization_claimed"]
    with pytest.raises(ValueError, match="same mode multiplicity"):
        authoritative_field_registry(gauge_modes=2, ghost_modes=1)


def test_registry_contains_no_mass_or_empirical_standard_model_values() -> None:
    text = json.dumps(authoritative_field_registry().metadata(), sort_keys=True)
    for forbidden in ("measured", "GeV", "PDG", "alpha_em", "Higgs_pole"):
        assert forbidden not in text


def test_action_components_are_owned_and_reject_response_objects() -> None:
    action = current_pre_g7_attachment()
    assert [component.component_id for component in action.components] == [
        "RETAINED_N12_LOCAL_GEOMETRY_ACTION"
    ]
    component = action.components[0]
    assert component.provenance
    assert not component.empirical_input_used
    assert not component.response_object_only
    with pytest.raises(ValueError, match="response objects"):
        replace(component, response_object_only=True)
    decision = response_artifact_rejection_witness()
    assert decision["decision"] == "CASE_B"
    assert decision["response_seeds_are_action_components"] is False


def test_exact_zero_sm_geometry_reduction() -> None:
    action = current_pre_g7_attachment()
    state = _geometry_state(action.registry)
    expected = float(action_value(jnp.asarray(state[:STATE_DIMENSION])))
    assert action.value(state) == expected
    exact = exact_full_action_jet_at_state(
        12,
        state[:QDIM],
        state[QDIM:2 * QDIM],
        state[2 * QDIM:2 * QDIM + MDIM],
        points=POINTS,
    )
    assert action.value(state) == pytest.approx(exact.value, rel=2.0e-13, abs=2.0e-13)


def test_geometry_first_variation_reduction() -> None:
    action = current_pre_g7_attachment()
    state = _geometry_state(action.registry)
    direction = _geometry_direction(action.registry, 1)
    exact = exact_full_action_jet_at_state(
        12,
        state[:QDIM],
        state[QDIM:2 * QDIM],
        state[2 * QDIM:2 * QDIM + MDIM],
        points=POINTS,
    )
    expected = float(exact.gradient @ direction[:STATE_DIMENSION])
    assert action.s1(state, direction) == pytest.approx(expected, rel=2.0e-12, abs=2.0e-12)


def test_derivative_rejects_nonzero_unowned_base_state() -> None:
    action = current_pre_g7_attachment()
    state = _geometry_state(action.registry)
    state[action.registry.block("gauge").start] = 1.0
    with pytest.raises(MissingActionSourceError, match="nonzero fields"):
        action.s1(state, _geometry_direction(action.registry))


@pytest.mark.parametrize("block_name", ["gauge", "ghost", "antighost", "fermion", "antifermion", "HS_scalar"])
def test_unowned_sector_reductions_fail_closed(block_name: str) -> None:
    action = current_pre_g7_attachment()
    state = np.zeros(action.registry.dimension)
    state[action.registry.block(block_name).start] = 1.0
    with pytest.raises(MissingActionSourceError, match="same-action owner"):
        action.value(state)


def test_mixed_derivative_consistency_for_owned_bosonic_geometry() -> None:
    action = current_pre_g7_attachment()
    state = _geometry_state(action.registry)
    first = _geometry_direction(action.registry, 0)
    second = _geometry_direction(action.registry, 2)
    assert action.s2(state, first, second) == pytest.approx(
        action.s2(state, second, first), rel=2.0e-12, abs=2.0e-12
    )


def test_graded_left_derivative_koszul_exchange_convention() -> None:
    registry = authoritative_field_registry()
    fermion = registry.embed("fermion", np.eye(registry.block("fermion").dimension)[0])
    antifermion = registry.embed(
        "antifermion", np.eye(registry.block("antifermion").dimension)[0]
    )
    gauge = registry.embed("gauge", np.eye(registry.block("gauge").dimension)[0])
    parities = tuple(registry.direction_parity(item) for item in (fermion, antifermion))
    assert parities == (1, 1)
    assert koszul_permutation_sign(parities, (1, 0)) == -1
    mixed = tuple(registry.direction_parity(item) for item in (fermion, gauge))
    assert koszul_permutation_sign(mixed, (1, 0)) == 1

    class GradedBilinearOracle:
        def value(self, state):
            return 0.0

        def derivative(self, state, directions):
            if len(directions) != 2:
                return 0.0
            first, second = (np.asarray(item) for item in directions)
            f = registry.block("fermion").start
            bar = registry.block("antifermion").start
            return float(first[f] * second[bar] - first[bar] * second[f])

    component = ActionComponent(
        component_id="TEST_GRADED_FERMION_BILINEAR",
        sectors=frozenset(("fermion",)),
        field_blocks=frozenset(("fermion", "antifermion")),
        oracle=GradedBilinearOracle(),
        action_version="BHSM-AE-2.0.0",
        source_action_version="BHSM-AE-2.0.0",
        source="unit-test",
        source_sha256="A" * 64,
        provenance=("unit-test graded bilinear",),
        background_parametric=True,
        derivative_signatures=frozenset((("fermion", "fermion"),)),
        field_registry_sha256=registry.sha256,
        background_id=None,
        domain_id=None,
        domain_scope="UNIT_TEST",
        graded_left_derivatives=True,
        zero_reference_subtracted=True,
        geometry_reduction_preserved=True,
    )
    action = UniversalFullFieldAction(
        registry,
        FullFieldBackgroundBinder().unbound(),
        (component,),
        {
            (left, right): BlockStatus.MISSING_ACTION_SOURCE
            for left_index, left in enumerate(("geometry", "gauge", "ghost", "fermion", "HS"))
            for right in ("geometry", "gauge", "ghost", "fermion", "HS")[left_index:]
        },
    )
    zero = np.zeros(registry.dimension)
    assert action.s2(zero, fermion, antifermion) == 1.0
    assert action.s2(zero, antifermion, fermion) == -1.0


def test_public_background_dataclass_cannot_self_promote() -> None:
    forged = BoundBackground(
        state=BackgroundState.PHYSICAL_BACKGROUND,
        action_version="BHSM-AE-2.0.0",
    )
    assert forged.physical is False
    with pytest.raises(RuntimeError, match="Gate-7 authority"):
        forged.require_physical()


def test_matrix_free_s3_and_s4_geometry_interfaces() -> None:
    action = current_pre_g7_attachment()
    state = _geometry_state(action.registry)
    first = _geometry_direction(action.registry, 0)
    second = _geometry_direction(action.registry, 1)
    third = _geometry_direction(action.registry, 2)
    fourth = _geometry_direction(action.registry, 3)
    assert np.isfinite(action.s3(state, first, second, third))
    assert np.isfinite(action.s4(state, first, second, third, fourth))
    assert action.metadata()["dense_S3_or_S4_tensor_formed"] is False
    complex_direction = first.astype(complex)
    complex_direction[0] = 1.0j
    with pytest.raises(ValueError, match="must be real"):
        action.s1(state, complex_direction)


def test_separate_self_sector_components_do_not_authorize_a_mixed_derivative() -> None:
    registry = authoritative_field_registry()

    class ZeroOracle:
        def value(self, state):
            return 0.0

        def derivative(self, state, directions):
            return 0.0

    common = {
        "oracle": ZeroOracle(),
        "action_version": "BHSM-AE-2.0.0",
        "source_action_version": "BHSM-AE-2.0.0",
        "source_sha256": "B" * 64,
        "provenance": ("unit-test",),
        "background_parametric": True,
        "field_registry_sha256": registry.sha256,
        "background_id": None,
        "domain_id": None,
        "domain_scope": "UNIT_TEST",
    }
    geometry = ActionComponent(
        component_id="GEOMETRY_SELF",
        sectors=frozenset(("geometry",)),
        field_blocks=frozenset(("geometry", "geometry_velocity", "constraint_multiplier")),
        source="geometry-test",
        derivative_signatures=frozenset((("geometry",), ("geometry", "geometry"))),
        geometry_reduction_preserved=True,
        **common,
    )
    gauge = ActionComponent(
        component_id="GAUGE_SELF",
        sectors=frozenset(("gauge",)),
        field_blocks=frozenset(("gauge",)),
        source="gauge-test",
        derivative_signatures=frozenset((("gauge",), ("gauge", "gauge"))),
        zero_reference_subtracted=True,
        geometry_reduction_preserved=True,
        **common,
    )
    statuses = {
        (left, right): BlockStatus.MISSING_ACTION_SOURCE
        for left_index, left in enumerate(("geometry", "gauge", "ghost", "fermion", "HS"))
        for right in ("geometry", "gauge", "ghost", "fermion", "HS")[left_index:]
    }
    action = UniversalFullFieldAction(
        registry,
        FullFieldBackgroundBinder().unbound(),
        (geometry, gauge),
        statuses,
    )
    zero = np.zeros(registry.dimension)
    with pytest.raises(MissingActionSourceError, match="geometry-gauge"):
        action.s2(
            zero,
            registry.embed("geometry", np.eye(registry.block("geometry").dimension)[0]),
            registry.embed("gauge", np.eye(registry.block("gauge").dimension)[0]),
        )


def test_forged_action_derived_block_without_signature_is_rejected() -> None:
    action = current_pre_g7_attachment()
    statuses = dict(action.block_status)
    statuses[("geometry", "gauge")] = BlockStatus.ACTION_DERIVED
    with pytest.raises(ValueError, match="lacks a component signature"):
        UniversalFullFieldAction(
            action.registry,
            action.background,
            action.components,
            statuses,
        )


def test_structural_zero_and_cross_version_claims_require_certificates() -> None:
    action = current_pre_g7_attachment()
    statuses = dict(action.block_status)
    statuses[("geometry", "geometry")] = BlockStatus.STRUCTURAL_ZERO
    with pytest.raises(ValueError, match="lacks action/BRST provenance"):
        UniversalFullFieldAction(
            action.registry,
            action.background,
            action.components,
            statuses,
        )
    with pytest.raises(ValueError, match="transition certificate"):
        replace(
            action.components[0],
            action_version="BHSM-AE-4.0.0",
        )
    transitioned = replace(
        action.components[0],
        action_version="BHSM-AE-4.0.0",
        version_transition_source="future/ae2_to_ae4.json",
        version_transition_sha256="C" * 64,
    )
    successor = UniversalFullFieldAction(
        action.registry,
        FullFieldBackgroundBinder("BHSM-AE-4.0.0").unbound(),
        (transitioned,),
        action.block_status,
    )
    assert successor.components[0].source_action_version == "BHSM-AE-2.0.0"


def test_unbound_and_mathematical_backgrounds_cannot_promote() -> None:
    binder = FullFieldBackgroundBinder()
    unbound = binder.unbound()
    assert unbound.state is BackgroundState.UNBOUND_BACKGROUND
    with pytest.raises(RuntimeError, match="Gate-7 authority"):
        unbound.require_physical()
    mathematical = binder.bind_mathematical(
        np.zeros(4),
        background_id="proof-center-only",
        domain_id="test-domain",
        provenance=("unit-test",),
    )
    assert mathematical.state is BackgroundState.CERTIFIED_MATHEMATICAL_BACKGROUND
    with pytest.raises(RuntimeError, match="Gate-7 authority"):
        mathematical.require_physical()


def test_physical_binder_validates_hash_and_full_authority_contract(tmp_path: Path) -> None:
    registry = authoritative_field_registry(gauge_modes=2, ghost_modes=2)
    full_state = np.zeros(registry.dimension)
    full_state[0] = 0.1
    geometry_state = full_state[:STATE_DIMENSION]
    dependency = tmp_path / "dependency.bin"
    dependency.write_bytes(b"future-gate7-dependency")
    domain = tmp_path / "domain.bin"
    domain.write_bytes(b"future-domain")
    metric = tmp_path / "metric.bin"
    metric.write_bytes(b"future-metric")
    realization = tmp_path / "realization.bin"
    realization.write_bytes(b"finite-basis-realization")
    authority = tmp_path / "authority.json"
    binder_for_digest = FullFieldBackgroundBinder()
    mathematical = binder_for_digest.bind_mathematical(
        geometry_state,
        background_id="future-g7",
        domain_id="future-domain",
        provenance=("test",),
    )
    authority.write_text(json.dumps({
        "artifact": "BHSM_N12_GATE7_PHYSICAL_BACKGROUND_AUTHORITY",
        "schema_version": 1,
        "validation_passed": True,
        "Gate7_closed": True,
        "physical_background_authorized": True,
        "action_version": binder_for_digest.action_version,
        "background_state_sha256": mathematical.geometry_background_sha256,
        "field_registry_sha256": registry.sha256,
        "background_id": "future-g7",
        "domain_id": "future-domain",
        "domain_artifact": "domain.bin",
        "domain_sha256": hashlib.sha256(domain.read_bytes()).hexdigest(),
        "metric_tetrad_artifact": "metric.bin",
        "metric_tetrad_sha256": hashlib.sha256(metric.read_bytes()).hexdigest(),
        "field_registry_realization_artifact": "realization.bin",
        "field_registry_realization_sha256": hashlib.sha256(realization.read_bytes()).hexdigest(),
        "source_sha256": {
            "dependency.bin": hashlib.sha256(dependency.read_bytes()).hexdigest(),
            "domain.bin": hashlib.sha256(domain.read_bytes()).hexdigest(),
            "metric.bin": hashlib.sha256(metric.read_bytes()).hexdigest(),
            "realization.bin": hashlib.sha256(realization.read_bytes()).hexdigest(),
        },
        "provenance": ["synthetic contract test"],
    }), encoding="utf-8")
    digest = hashlib.sha256(authority.read_bytes()).hexdigest().upper()
    binder = FullFieldBackgroundBinder(
        trusted_authority_path=authority,
        trusted_authority_sha256=digest,
    )
    bound = binder.bind_physical(
        geometry_state,
        authority,
        registry=registry,
        source_root=tmp_path,
    )
    assert bound.state is BackgroundState.PHYSICAL_BACKGROUND
    bound.require_physical()
    action = current_pre_g7_attachment(bound, registry=registry)
    changed = full_state.copy()
    changed[0] += 0.01
    with pytest.raises(RuntimeError, match="does not match"):
        action.value(changed)
    with pytest.raises(RuntimeError, match="no trusted"):
        binder_for_digest.bind_physical(
            geometry_state,
            authority,
            registry=registry,
            source_root=tmp_path,
        )


def test_gate7_authority_alone_does_not_bypass_missing_full_field_blocks(tmp_path: Path) -> None:
    registry = authoritative_field_registry(gauge_modes=2, ghost_modes=2)
    full_state = np.zeros(registry.dimension)
    full_state[0] = 0.1
    geometry_state = full_state[:STATE_DIMENSION]
    binder_for_digest = FullFieldBackgroundBinder()
    digest_state = binder_for_digest.bind_mathematical(
        geometry_state, background_id="b", domain_id="d", provenance=("test",)
    ).geometry_background_sha256
    dependency = tmp_path / "dependency.bin"
    dependency.write_bytes(b"dependency")
    domain = tmp_path / "domain.bin"
    domain.write_bytes(b"domain")
    metric = tmp_path / "metric.bin"
    metric.write_bytes(b"metric")
    realization = tmp_path / "realization.bin"
    realization.write_bytes(b"realization")
    path = tmp_path / "authority.json"
    path.write_text(json.dumps({
        "artifact": "BHSM_N12_GATE7_PHYSICAL_BACKGROUND_AUTHORITY",
        "schema_version": 1,
        "validation_passed": True,
        "Gate7_closed": True,
        "physical_background_authorized": True,
        "action_version": binder_for_digest.action_version,
        "background_state_sha256": digest_state,
        "field_registry_sha256": registry.sha256,
        "background_id": "b",
        "domain_id": "d",
        "domain_artifact": "domain.bin",
        "domain_sha256": hashlib.sha256(domain.read_bytes()).hexdigest(),
        "metric_tetrad_artifact": "metric.bin",
        "metric_tetrad_sha256": hashlib.sha256(metric.read_bytes()).hexdigest(),
        "field_registry_realization_artifact": "realization.bin",
        "field_registry_realization_sha256": hashlib.sha256(realization.read_bytes()).hexdigest(),
        "source_sha256": {
            "dependency.bin": hashlib.sha256(dependency.read_bytes()).hexdigest(),
            "domain.bin": hashlib.sha256(domain.read_bytes()).hexdigest(),
            "metric.bin": hashlib.sha256(metric.read_bytes()).hexdigest(),
            "realization.bin": hashlib.sha256(realization.read_bytes()).hexdigest(),
        },
        "provenance": ["test"],
    }), encoding="utf-8")
    binder = FullFieldBackgroundBinder(
        trusted_authority_path=path,
        trusted_authority_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    )
    background = binder.bind_physical(
        geometry_state,
        path,
        registry=registry,
        source_root=tmp_path,
    )
    action = current_pre_g7_attachment(background, registry=registry)
    with pytest.raises(RuntimeError, match="action owners"):
        action.require_physical_promotion(full_state)


def test_brst_and_momentum_interfaces_are_prepared_but_not_physically_frozen() -> None:
    background = FullFieldBackgroundBinder().bind_mathematical(
        np.zeros(3),
        background_id="math",
        domain_id="domain",
        provenance=("unit-test",),
    )
    quotient = PreparedBRSTInterface(background).build(
        np.diag([0.0, 2.0, 3.0]),
        np.diag([0.0, 1.0, 1.0]),
        np.zeros((0, 3)),
        np.asarray([[1.0], [0.0], [0.0]]),
        np.asarray([[1.0, 0.0, 0.0]]),
        gauge_condition_id="test-gauge",
        provenance=("action-owned test symbols",),
    )
    quotient.require_regular_brst_quotient()
    with pytest.raises(ValueError, match="does not match"):
        PreparedBRSTInterface(background).build(
            np.diag([0.0, 2.0, 3.0]),
            np.diag([0.0, 1.0, 1.0]),
            np.zeros((0, 3)),
            np.asarray([[1.0], [0.0], [0.0]]),
            np.asarray([[1.0, 0.0, 0.0]]),
            action_version="WRONG",
            gauge_condition_id="test-gauge",
            provenance=("action-owned test symbols",),
        )
    momentum = PreparedMomentumSymbolInterface(background).build(
        np.diag([1.0, -1.0, -1.0, -1.0]),
        chart_id="test-chart",
        provenance=("mathematical metric",),
    )
    with pytest.raises(RuntimeError, match="frozen BHSM background"):
        momentum.require_physical_map()
    action = current_pre_g7_attachment(background)
    state = _geometry_state(action.registry)
    directions = (
        _geometry_direction(action.registry, 0),
        _geometry_direction(action.registry, 1),
    )
    symbol = PreparedMomentumSymbolInterface(background).build_conditional_s2_contraction(
        action, state, np.asarray([1.0, 0.0, 0.0, 0.0]), directions
    )
    assert symbol["quadratic_symbol"].shape == (2, 2)
    assert symbol["physical_symbol_derived"] is False


def test_saddle_and_hs_direction_interfaces_propagate_missing_sources() -> None:
    action = current_pre_g7_attachment()
    state = _geometry_state(action.registry)
    with pytest.raises(MissingActionSourceError, match="same-action component signature"):
        PreparedReplacementSaddleInterface(action).stationarity_covector(state)
    with pytest.raises(MissingActionSourceError, match="same-action component signature"):
        PreparedHSDirectionInterface(action).hessian(state)


def test_materialized_authority_is_deterministic_and_preserves_promotion_gates() -> None:
    module = _materializer_module()
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert stored == module.build_payload()
    assert stored["validated"] is True
    assert stored["open"] is True
    assert stored["invalidated"] is False
    assert stored["physical_background_bound"] is False
    assert stored["physical_yukawas_derived"] is False
    assert stored["physical_HS_direction_derived"] is False
    assert stored["physical_replacement_saddle_derived"] is False
    assert stored["geometry_reduction_verified"] is False
    assert stored["geometry_local_kernel_reduction_verified"] is True
    assert stored["geometry_full_history_seam_reduction_open"] is True
    assert stored["yukawa_current_same_action_callable"] is False
    assert stored["FULL_BHSM_COMPLETE"] is False
    assert stored["history_seam_attached"]["nonfermion_Wentzell_or_seam_terms_defaulted_to_zero"] is False
    for relative, digest in stored["source_sha256"].items():
        assert _portable_source_sha256(ROOT / relative) == digest
