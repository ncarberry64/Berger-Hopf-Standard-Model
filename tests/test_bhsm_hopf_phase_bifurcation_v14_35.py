from __future__ import annotations

import numpy as np

from bhsm.interface.completion.hopf_phase_bifurcation_completion_gate_v14_35 import (
    all_payloads,
    materialization_hashes,
)
from bhsm.interface.completion.hopf_phase_bifurcation_cp_v14_35 import (
    CABIBBO_CP_COMPONENTS,
    MINIMAL_MIXING_COMPONENTS,
    action_selection_payload,
    bipartite_cycle_rank,
    bridge_component_allowed,
    completion_payload,
    component_support,
    determinant_factor,
    cabibbo_cp_support,
    minimal_mixing_support,
    minimal_texture_payload,
    nonlinear_tower_payload,
    phase_locking_payload,
    plaquette_phase,
    rephase_kernel,
    relative_holonomy_payload,
    signed_seventh_order_weights,
    spontaneous_cp_phase,
    structural_kernel,
)


def test_minimal_components_and_support_graphs() -> None:
    assert MINIMAL_MIXING_COMPONENTS == ((0, 0), (2, 2), (6, 6), (10, 8))
    mixing = minimal_mixing_support()
    assert np.array_equal(
        mixing,
        np.asarray([[0, 1, 1], [1, 1, 1], [0, 0, 1]], dtype=int),
    )
    assert bipartite_cycle_rank(mixing) == 1

    assert CABIBBO_CP_COMPONENTS == ((0, 0), (2, 2), (4, 4), (6, 6), (8, 8))
    cp = cabibbo_cp_support()
    assert np.array_equal(
        cp,
        np.asarray([[1, 1, 0], [1, 1, 1], [0, 0, 1]], dtype=int),
    )
    assert bipartite_cycle_rank(cp) == 1
    assert component_support((6, 6))[1, 1] == 1
    assert component_support((6, 6))[1, 2] == 1


def test_bridge_selection_examples() -> None:
    assert bridge_component_allowed((4, 4), (10, 1), (8, 2))
    assert bridge_component_allowed((8, 8), (10, 1), (6, 3))
    assert not bridge_component_allowed((8, 8), (10, 1), (0, 0))
    assert bridge_component_allowed((0, 0), (0, 0), (0, 0))


def test_structural_determinant_and_cp_witness() -> None:
    kernel = structural_kernel()
    expected = determinant_factor(kernel[0, 0], kernel[0, 1], kernel[1, 0], kernel[1, 1], kernel[2, 2])
    assert abs(np.linalg.det(kernel) - expected) < 1e-12
    payload = minimal_texture_payload()
    assert payload["validation_passed"]
    assert abs(payload["Cabibbo_aligned_CP_texture"]["existence_witness"]["jarlskog"]) > 1e-8


def test_plaquette_phase_is_rephasing_invariant() -> None:
    kernel = structural_kernel()
    shifted = rephase_kernel(kernel, (0.1, 0.2, 0.3), (-0.4, 0.5, -0.6))
    delta = np.angle(np.exp(1j * (plaquette_phase(shifted) - plaquette_phase(kernel))))
    assert abs(delta) < 1e-12


def test_spontaneous_cp_normal_form() -> None:
    assert not spontaneous_cp_phase(1.0, 0.0)["exists"]
    result = spontaneous_cp_phase(1.0, 1.0)
    assert result["exists"]
    assert result["curvature"] > 0.0
    assert 0.0 < result["phi"] < np.pi


def test_p8_weight_tower_growth() -> None:
    generated = signed_seventh_order_weights([0, 2, 4, 6, 8])
    assert generated == list(range(-24, 33, 2))
    assert nonlinear_tower_payload()["validation_passed"]


def test_all_scientific_payloads_validate() -> None:
    for payload in (
        minimal_texture_payload(),
        phase_locking_payload(),
        action_selection_payload(),
        nonlinear_tower_payload(),
        relative_holonomy_payload(),
        completion_payload(),
    ):
        assert payload["validation_passed"]
    assert completion_payload()["BHSM_complete"] is False
    assert completion_payload()["CKM_status"] == "NOT_DERIVED"


def test_deterministic_materialization(tmp_path) -> None:
    first = materialization_hashes(tmp_path / "one")
    second = materialization_hashes(tmp_path / "two")
    assert first == second
    assert len(first) == len(all_payloads()) == 6
