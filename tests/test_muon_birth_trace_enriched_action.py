from pathlib import Path
import numpy as np
from bhsm.interface.muon_birth_coupled_primal_midpoint import endpoint_raw_from_assigned_application
from bhsm.interface.muon_birth_trace_enriched_action import trace_enriched_representation,pointwise_trace_enriched_action,generic_coordinate_lift
from bhsm.interface.muon_pointwise_full_field_action import pointwise_full_field_action
from bhsm.interface.muon_parent_gauge_geometry_correction import correction_representation,ROOT
from bhsm.interface.muon_parent_mean_causal_action import mean_coordinate_lift
from bhsm.interface.muon_parent_retarded_hypercharge import WALL,regular_radial_basis
from bhsm.interface.muon_parent_maxwell_full_weak import FIELD_ORDER


def pair():
    s=ROOT/'artifacts/muon_parent_gauge_geometry_correction_20261010/two_arm_scalar_run_1'
    return np.array([endpoint_raw_from_assigned_application(s,k)[0] for k in ('incoming','outgoing')])


def test_actual_affine_image_and_radial_derivative_are_reconstructed_without_projection():
    r=trace_enriched_representation(pair(),radial_points=48,cap_points=48)
    assert r['gauge_count']==80 and r['wall_trace_map'].shape==(5,4,80)
    assert r['former_radial_space_L2_complement']>3e-3
    assert r['affine_velocity_multiplier_jet_max']==0
    assert r['affine_trace_reconstruction_max']<2e-17
    assert r['affine_trace_derivative_reconstruction_max']<3e-17
    # Added profile has exactly the inherited wall trace; no invented
    # reflecting flux or extension of the intrinsic Higgs is involved.
    assert not r['wall_trace_map'][:,:,40:60].any()
    assert r['affine_complement_norm']>0


def test_variable_gauge_lift_preserves_the_verified_60_field_coordinate_map():
    r=correction_representation(radial_order=2,include_wall_lift=True)
    a=generic_coordinate_lift(r['gauge_labels']);b=mean_coordinate_lift(r['gauge_labels'])
    np.testing.assert_array_equal(a['lift'],b['lift'])


def test_enlarged_literal_action_restricts_to_every_original_derivative():
    original=correction_representation(radial_points=24,radial_order=2,cap_points=48,include_wall_lift=True,include_scalar_mean=True)
    enriched=trace_enriched_representation(pair(),radial_points=24,cap_points=48)
    raw=pair()[0].copy();raw[100:160]=.002*np.sin(np.arange(60)+.2);raw[160:220]=.003*np.cos(np.arange(60)+.1)
    raw[220:]=[.2,.8,-.1,.3,.03,-.02,.01,.04]
    E=np.zeros((268,228));E[:100,:100]=np.eye(100);E[-8:,-8:]=np.eye(8)
    for j,l in enumerate(original['gauge_labels']):
        radial=3 if l['wall_lift'] else l['radial']
        k=20*radial+4*FIELD_ORDER.index(l['field'])+l['internal']
        E[100+k,100+j]=1;E[180+k,160+j]=1
    a=pointwise_full_field_action(raw,original,nu_squared_action=4.)
    b=pointwise_trace_enriched_action(E@raw,enriched,nu_squared_action=4.)
    np.testing.assert_allclose(b['value'],a['value'],atol=2e-12,rtol=2e-15)
    np.testing.assert_allclose(E.T@b['raw_gradient'],a['raw_gradient'],atol=3e-10,rtol=2e-12)
    np.testing.assert_allclose(E.T@b['raw_hessian']@E,a['raw_hessian'],atol=3e-9,rtol=2e-12)
