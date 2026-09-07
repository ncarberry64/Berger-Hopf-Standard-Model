"""Exact tests of selection, stationarity, and the conditional graph lemma."""

import hashlib
import json
from pathlib import Path

import pytest
import sympy as sp

from bhsm.interface.covariant_interface_seam_selection import (
    METRIC,
    build_payload,
    cotangent_gluing_graph,
    lorentz_generators,
    maxwell_map_work_covector,
    maxwell_selection_jacobian,
)


ROOT = Path(__file__).resolve().parents[1]
FIELD = sp.Matrix([[0, 1, 0], [-1, 0, 0], [0, 0, 0]])


def test_full_metric_preserving_tangent_space_has_exact_three_generators():
    for generator in lorentz_generators():
        assert generator.T * METRIC + METRIC * generator == sp.zeros(3)
    # Independently count the unrestricted 3x3 metric-compatibility system.
    variables = sp.symbols("b:9")
    unrestricted = sp.Matrix(3, 3, variables)
    equations = unrestricted.T * METRIC + METRIC * unrestricted
    constraint = sp.Matrix(list(equations)).jacobian(variables)
    assert 9 - constraint.rank() == 3


def test_nonzero_curvature_does_not_remove_its_boost_stabilizer():
    jacobian = maxwell_selection_jacobian(FIELD, [0, 0, 0])
    assert jacobian.rank() == 2
    assert jacobian.nullspace() == [sp.Matrix([1, 0, 0])]


def test_full_rank_flux_witness_has_nonzero_exact_minor_and_nonzero_map_work():
    jacobian = maxwell_selection_jacobian(FIELD, [0, 2, 0])
    assert jacobian.extract([1, 2, 3], [0, 1, 2]).det() == 2
    assert jacobian.nullspace() == []
    assert maxwell_map_work_covector(FIELD, [0, 2, 0]) == sp.Matrix([2, 0, 0])


def test_isolated_map_stationarity_alignment_leaves_same_boost_kernel():
    assert maxwell_map_work_covector(FIELD, [0, 0, 3]) == sp.zeros(3, 1)
    assert maxwell_selection_jacobian(FIELD, [0, 0, 3]).nullspace() == [sp.Matrix([1, 0, 0])]


def test_free_map_stationarity_and_surviving_boost_align_for_every_flux():
    e0, e1, e2 = sp.symbols("e0 e1 e2")
    flux = sp.Matrix([e0, e1, e2])
    work = FIELD * METRIC.inv() * flux
    assert work == lorentz_generators()[0].T * flux == sp.Matrix([e1, e0, 0])
    assert sp.linsolve(list(work), (e0, e1, e2)) == {(0, 0, e2)}


def test_actual_source_free_four_dimensional_field_produces_witness_traces():
    coordinates = sp.symbols("t x y z")
    potential = sp.Matrix([0, coordinates[0] - 2 * coordinates[3], 0, 0])
    field = sp.Matrix(4, 4, lambda i, j: (
        sp.diff(potential[j], coordinates[i]) - sp.diff(potential[i], coordinates[j])
    ))
    metric = sp.diag(-1, 1, 1, 1)
    raised = metric * field * metric
    divergence = sp.Matrix([
        sum(sp.diff(raised[i, j], coordinates[i]) for i in range(4))
        for j in range(4)
    ])
    assert divergence == sp.zeros(4, 1)
    assert field[:3, :3] == FIELD
    assert METRIC * sp.Matrix([-raised[3, j] for j in range(3)]) == sp.Matrix([0, 2, 0])
    assert sum(field[i, j] * raised[i, j] for i in range(4) for j in range(4)) / 2 == 3


def test_finite_wrong_identity_passes_curvature_and_fails_nonzero_flux():
    reference = sp.Matrix([[sp.Rational(5, 3), sp.Rational(4, 3), 0],
                           [sp.Rational(4, 3), sp.Rational(5, 3), 0], [0, 0, 1]])
    flux = sp.Matrix([0, 2, 0])
    assert reference.T * METRIC * reference == METRIC
    assert reference.det() == 1 and reference[0, 0] > 0
    assert reference.T * FIELD * reference == FIELD
    transported_flux = reference.T * flux
    assert transported_flux == sp.Matrix([sp.Rational(8, 3), sp.Rational(10, 3), 0])
    assert sp.eye(3).T * flux != transported_flux


def test_cotangent_graph_has_zero_green_form_and_is_maximal_in_reduced_example():
    transport = sp.Matrix([[2, 1], [1, 1]])
    graph = cotangent_gluing_graph(transport)
    canonical = sp.Matrix([[0, 0, 1, 0], [0, 0, 0, 1],
                           [-1, 0, 0, 0], [0, -1, 0, 0]])
    assert graph.T * sp.diag(canonical, canonical) * graph == sp.zeros(4)
    assert graph.rank() == graph.rows / 2 == 4
    # The opposite sign is essential, not an arbitrary graph convention.
    wrong_graph = graph.copy()
    wrong_graph[6:8, 2:4] = transport.T
    assert wrong_graph.T * sp.diag(canonical, canonical) * wrong_graph != sp.zeros(4)


def test_nonexact_or_nonphysical_matrix_inputs_fail_closed():
    with pytest.raises(ValueError):
        maxwell_selection_jacobian(sp.eye(3), [0, 1, 0])
    with pytest.raises(ValueError):
        maxwell_selection_jacobian(FIELD, [0.0, 1, 0])
    with pytest.raises(ValueError):
        cotangent_gluing_graph(sp.zeros(2))


def test_materialized_artifact_matches_computation_and_all_source_hashes():
    artifact = ROOT / "artifacts/action_extension/BHSM_COVARIANT_INTERFACE_SEAM_SELECTION_AUDIT.json"
    payload = json.loads(artifact.read_text(encoding="utf-8"))
    expected = build_payload()
    assert all(payload[key] == value for key, value in expected.items())
    assert payload["validation_passed"] is True
    for name, digest in payload["inputs"].items():
        assert hashlib.sha256((ROOT / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper() == digest
    assert payload["N12"]["new_independent_rank"] == 0
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["rank_scope"]["inputs_are_physical_BHSM_traces"] is False
    assert payload["nonzero_Maxwell_realization"]["isolated_free_map_stationarity_passed"] is False
