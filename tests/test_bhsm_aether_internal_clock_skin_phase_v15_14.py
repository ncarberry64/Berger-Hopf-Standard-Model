from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pytest

from bhsm.interface.aether_internal_clock_skin_phase_v15_14 import (
    EXACT_NEXT_OBJECT,
    FULL_BHSM_COMPLETE,
    clock_domain_nonselection_witness,
    clock_generalized_force,
    completion_payload,
    deterministic_json,
    generator_logarithm_branches,
    hayward_projected_contact_impulse,
    internal_clock_holonomy,
    materialize,
    maximal_isotropic_trace,
    proper_clock_interval,
    relative_internal_phase,
    scalar_clock_evolve_trace,
    trace_graph_residual,
)


ROOT = Path(__file__).resolve().parents[1]


def test_parent_and_child_proper_clocks_need_not_be_synchronized() -> None:
    assert proper_clock_interval(-4.0, 0.5) == pytest.approx(1.0)
    assert proper_clock_interval(-1.0, 0.5) == pytest.approx(0.5)
    with pytest.raises(ValueError, match="timelike"):
        proper_clock_interval(1.0, 0.5)


def test_internal_clock_holonomy_is_unitary_and_composes() -> None:
    generator = np.array([[1.0, 0.2j], [-0.2j, 2.0]], dtype=complex)
    first = internal_clock_holonomy(generator, 0.3)
    second = internal_clock_holonomy(generator, 0.5)
    combined = internal_clock_holonomy(generator, 0.8)
    assert np.conjugate(first.T) @ first == pytest.approx(np.eye(2), abs=2e-14)
    assert second @ first == pytest.approx(combined, abs=2e-14)


@pytest.mark.parametrize("alpha", [-2.0, -0.5, 0.0, 1.0, 3.0])
def test_clock_evolution_preserves_every_normal_trace_graph(alpha: float) -> None:
    before = maximal_isotropic_trace(alpha, 0.7 - 0.2j)
    after = scalar_clock_evolve_trace(before, energy=1.3, interval=0.8)
    assert trace_graph_residual(before, alpha) < 1e-14
    assert trace_graph_residual(after, alpha) < 1e-14
    assert np.vdot(after, after).real == pytest.approx(np.vdot(before, before).real)


def test_internal_clock_is_not_a_domain_selector() -> None:
    witness = clock_domain_nonselection_witness()
    assert witness["all_domains_preserved"] is True
    assert witness["all_norms_preserved"] is True
    assert witness["continuously_many_alpha_compatible"] is True


def test_common_phase_does_not_change_extension_parameter() -> None:
    alpha = 1.2
    before = maximal_isotropic_trace(alpha, 0.3 + 0.4j)
    after = np.exp(0.71j) * before
    assert trace_graph_residual(before, alpha) < 1e-14
    assert trace_graph_residual(after, alpha) < 1e-14


def test_relative_phase_is_common_shift_invariant_but_needs_inception_data() -> None:
    original = relative_internal_phase(0.2, 0.9, 0.4, 1.1)
    shifted = relative_internal_phase(0.91, 1.61, 0.4, 1.1)
    assert shifted == pytest.approx(original)
    changed_inception = relative_internal_phase(0.2, 1.0, 0.4, 1.1)
    assert changed_inception != pytest.approx(original)


def test_one_endpoint_holonomy_has_multiple_generator_logarithms() -> None:
    branches = generator_logarithm_branches(0.6, 1.7, (-1, 0, 1))
    endpoints = [np.exp(-1j * value * 1.7) for value in branches]
    assert len(set(round(value, 12) for value in branches)) == 3
    assert endpoints == pytest.approx([np.exp(0.6j)] * 3)


def test_hayward_impulse_is_locked_but_needs_embedding_derivatives() -> None:
    impulse = hayward_projected_contact_impulse(
        2.0, joint_measure=3.0, boost_angle=0.5, joint_measure_d=0.4, boost_angle_d=-0.2
    )
    assert impulse == pytest.approx(0.8)
    assert hayward_projected_contact_impulse(2.0, 3.0, 0.5, 0.0, 0.0) == 0.0


def test_phase_continuity_has_no_force_without_shape_dependent_generator() -> None:
    state = np.array([1.0, 1.0j])
    assert clock_generalized_force(state, np.zeros((2, 2))) == 0.0
    assert clock_generalized_force(state, np.diag([1.0, 3.0])) == pytest.approx(-2.0)


def test_completion_stops_at_foundational_domain_and_inception_obstruction() -> None:
    payload = completion_payload()
    assert FULL_BHSM_COMPLETE is False
    assert payload["validation_passed"] is True
    assert payload["phase_nonuniqueness_resolved"] is False
    assert payload["independent_internal_clocks_and_holonomies"][
        "worldtube_holonomy_fixes_change_not_inception_value"
    ] is True
    assert payload["global_and_relative_phase_quotient"][
        "U1_skin_domain_quotiented_by_global_wavefunction_phase"
    ] is False
    assert payload["contact_canonical_impulse"]["total_contact_impulse_sign_selected"] is False
    assert payload["v15_10_selection"]["surviving_witness_count"] == 3
    assert payload["scientific_terminal_condition"].startswith("BOUNDARY_IDENTITY_PLUS_INTERNAL_CLOCK")
    assert EXACT_NEXT_OBJECT.startswith("VARIATION_DERIVED_PARENT_AND_CHILD_SKIN")


def test_deterministic_materialization_and_repository_artifact(tmp_path: Path) -> None:
    encoded = deterministic_json(completion_payload())
    assert encoded.endswith("\n")
    assert "NaN" not in encoded and "Infinity" not in encoded
    assert json.loads(encoded)["version"] == "v15.14"
    first = materialize(tmp_path / "first")
    second = materialize(tmp_path / "second")
    assert hashlib.sha256(first.read_bytes()).digest() == hashlib.sha256(second.read_bytes()).digest()
    assert first.read_bytes() == (ROOT / "artifacts" / first.name).read_bytes()
