"""Independent analytic and direct-value spatial controls, not a muon solve."""
import numpy as np
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"audits"))

from bhsm_muon_worldvolume_spatial_one_jet_20261016 import (
    POINTS, _initial, _evaluator, affine_birth_connection, fixture_report,
    spatial_birth_map_one_jet,
)


def test_analytic_rotating_flow_and_wilson_line():
    row=fixture_report(True)
    assert row['analytic_q_U_max_error']<2e-12
    assert max(row['finite_five_point_spatial_derivative_max'].values())<2e-10
    assert row['jacobian_consistency_defect']<2e-12
    assert row['affine_incidence_residual']<2e-12
    assert row['initial_bundle_spatial_jet_norm']>.1
    assert row['interior_Wilson_connection_incidence_defect']>1e-3
    assert row['initial_subtracted_Wilson_connection_memory']>1e-3
    assert not row['physical_outgoing_E_B_derivative']


def test_nonlinear_flow_noncommuting_wilson_line():
    row=fixture_report(False)
    assert max(row['finite_five_point_spatial_derivative_max'].values())<2e-10
    assert row['jacobian_consistency_defect']<2e-12
    assert row['affine_incidence_residual']<2e-12
    assert row['initial_bundle_spatial_jet_norm']>.1
    assert row['interior_Wilson_connection_incidence_defect']>1e-3
    assert row['initial_subtracted_Wilson_connection_memory']>1e-3


def test_initial_bundle_spatial_jet_cannot_be_omitted():
    q,U,J,K,_,dJ=_initial(POINTS,True)
    with pytest.raises(ValueError,match='explicit dU0 required'):
        spatial_birth_map_one_jet(coefficients=np.array([.7]),times=np.array([0.,.27]),
            parent_label_points=POINTS,initial_material_points=q,
            initial_bundle_transport=U,initial_jacobian=J,
            initial_material_point_spatial_derivatives=K,
            initial_bundle_transport_spatial_derivatives=None,
            initial_jacobian_spatial_derivatives=dJ,evaluator=_evaluator(True),
            rtol=3e-14,atol=2e-15)


def test_nonunitary_spatial_bundle_jet_is_rejected():
    with pytest.raises(ValueError,match='tangent to U2'):
        affine_birth_connection(parent_connection=np.zeros((1,3,2,2),complex),
            bundle_transport=np.eye(2)[None],spatial_tangent_map=np.eye(3)[None],
            bundle_spatial_derivatives=np.broadcast_to(np.eye(2),(1,3,2,2)))


def test_complex_spatial_germ_is_not_projected_to_a_real_map():
    with pytest.raises(ValueError,match='complex germs are not projected'):
        affine_birth_connection(parent_connection=np.zeros((1,3,2,2),complex),
            bundle_transport=np.eye(2)[None],
            spatial_tangent_map=(np.eye(3)+1j*np.eye(3))[None],
            bundle_spatial_derivatives=np.zeros((1,3,2,2),complex))


def test_singular_spatial_map_is_rejected():
    with pytest.raises(ValueError,match='nonsingular spatial tangent map'):
        affine_birth_connection(parent_connection=np.zeros((1,3,2,2),complex),
            bundle_transport=np.eye(2)[None],spatial_tangent_map=np.zeros((1,3,3)),
            bundle_spatial_derivatives=np.zeros((1,3,2,2),complex))
