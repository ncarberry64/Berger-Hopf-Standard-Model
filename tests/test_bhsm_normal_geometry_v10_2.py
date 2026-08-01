from __future__ import annotations

import numpy as np
import pytest

from bhsm.interface.envelopment import normal_geometry_v10_2 as geometry


def test_unit_normal_and_induced_projector_identities():
    normal = np.array([0.0, 1.0, 0.0, 0.0])
    row = geometry.induced_geometry(np.diag([-1.0, 1.0, 1.0, 1.0]), normal)
    projector = row["mixed_projector"]
    assert row["normal_norm"] == pytest.approx(1.0)
    assert np.allclose(projector @ projector, projector)
    assert np.allclose(projector @ normal, 0.0)


def test_collar_jacobian_and_domain_dimensions():
    assert geometry.gaussian_collar_jacobian(2.0, np.diag([-1.0, 4.0])) == pytest.approx(4.0)
    assert [row["dimension"] for row in geometry.domain_ledger()] == [8, 7, 5, 4]


def test_normal_displacement_fails_closed_on_fixed_embedding():
    row = geometry.normal_variation_ledger()
    assert row["embedding_fixed"] is True
    assert row["psi_in_configuration_space"] is False
    assert row["delta_S_delta_psi"] is None
    assert row["shape_equation_from_current_action"] is None
    assert row["coordinate_rho_shift_is_physical_displacement"] is False


def test_geometry_payload_validates_without_adopting_metric_ansatz():
    payload = geometry.geometry_payload()
    assert payload["validation_passed"] is True
    assert payload["metric_ansatz"]["adopted_as_global_parent_metric"] is False
