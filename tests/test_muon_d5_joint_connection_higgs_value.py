"""Joint original connection/associated-section Newton application."""
from pathlib import Path
import json
import numpy as np
import pytest
from scipy.linalg import expm

from bhsm.interface.muon_d5_joint_connection_higgs_value import (
    joint_value_rows_jacobian,solve_joint_connection_higgs_value,
)
from bhsm.interface.muon_d5_spatial_bundle_application import cross_matrix,spatial_bundle_application
from bhsm.interface.muon_d5_event_bundle_incidence import original_event_coefficients
from bhsm.interface.muon_d5_independent_residuals import recovered_export_history


def test_all_seven_analytic_jacobi_columns_differentiate_original_equations():
    rng=np.random.default_rng(937)
    p=rng.normal(size=(3,4));c=rng.normal(size=(3,4))
    hp=rng.normal(size=2)+1j*rng.normal(size=2);hc=rng.normal(size=2)+1j*rng.normal(size=2)
    O=expm(cross_matrix([.1,.2,-.3]));R=expm(cross_matrix([-.3,.1,.2]))
    U=expm(np.array([[.1j,.2],[-.2,.3j]]));x=rng.normal(size=7)*.04
    _,J,_=joint_value_rows_jacobian(p,c,hp,hc,O,R,U,x)
    h=2e-6
    for i in range(7):
        dx=np.eye(7)[i]*h
        plus=joint_value_rows_jacobian(p,c,hp,hc,O,R,U,x+dx)[0]
        minus=joint_value_rows_jacobian(p,c,hp,hc,O,R,U,x-dx)[0]
        np.testing.assert_allclose(J[:,i],(plus-minus)/(2*h),atol=4e-10)


@pytest.fixture(scope='module')
def actual_joint():
    root=Path(__file__).resolve().parents[1];folder=root/'artifacts/muon_retained_response_20261018/inputs'
    md=json.loads((folder/'history_metadata.json').read_bytes());hist=[]
    for side in ('incoming','outgoing'):
        rows=md['sides'][side]
        with np.load(folder/(side+'_history.npz'),allow_pickle=False) as z:
            t=np.array([r['time'] for r in rows]);x=np.array([z[r['label']+'_raw_fields'] for r in rows]);dx=np.array([z[r['label']+'_raw_coordinate_time_derivative'] for r in rows])
        hist.append(recovered_export_history(root,side,t,x,dx)[0])
    coeff=[original_event_coefficients(h,0.,[np.pi/2],side=s) for h,s in zip(hist,('parent','child'))]
    s,_=spatial_bundle_application(*coeff,hist[1])
    return solve_joint_connection_higgs_value(*coeff,s)


def test_actual_joint_value_solve_repairs_Higgs_map_tilt_without_changing_fields(actual_joint):
    a,r=actual_joint
    assert r['background_fields_changed'] is False
    assert r['all7_rotation_phase_coordinates_retained']
    assert r['minimum_norm_physical_choice'] is False
    assert r['physical_admission'] is False
    for i,record in enumerate(r['candidates']):
        assert record['before_Higgs_max']>1e-8
        assert record['after_all16_max']<7e-16
        assert record['pivot_condition']<6
        assert a['coordinates'][i,5]==0
        assert a['full_value_Jacobian'][i].shape==(16,7)
        assert 1e-11<a['full_Jacobian_singular_values'][i,-1]<1e-10
        # The remaining direction is reported with its NONZERO residual,
        # rather than erased or declared a gauge/null direction.
        assert 8e-11<record['reconstructed_free_tangent_all16_max']<1.1e-10
        assert not record['physical_map_selected']
