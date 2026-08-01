from __future__ import annotations

import pytest

from bhsm.interface.envelopment.depth_constraint_reduction_v10_4 import (
    EXTENSION_VERDICT,
    REDUCTION_VERDICT,
    reduction_payload,
)


def test_hamiltonian_reduction_removes_volume_pair_not_shape_modes():
    payload = reduction_payload()
    count = payload["constraint_analysis"]
    kinetic = payload["kinetic_reduction"]
    projection = payload["physical_projection"]
    assert payload["validation_passed"] is True
    assert count["physical_configuration_dimension"] == 2
    assert kinetic["rho_norm"] == -42.0
    assert kinetic["shape_eigenvalues"] == pytest.approx([4 / 7, 2])
    assert kinetic["shape_metric_positive"] is True
    assert kinetic["unreduced_rho_called_ghost"] is False
    assert projection["reduced_physical_q_V_vector_in_beta_gamma_space"] == [0.0, 0.0]
    assert projection["reduced_kinetic_norm"] == 0.0
    assert projection["q_D_nonzero"] is False
    assert payload["existing_action_verdict"] == REDUCTION_VERDICT


def test_multiple_geometric_extensions_remain_unselected():
    payload = reduction_payload()
    assert len(payload["minimal_extension_comparison"]) == 7
    assert not any(row["adopted"] for row in payload["minimal_extension_comparison"])
    assert payload["unique_minimal_extension"] is None
    assert payload["extension_verdict"] == EXTENSION_VERDICT
    assert payload["new_geometric_fields_adopted"] == []
    assert payload["new_continuous_parameters_adopted"] == []
