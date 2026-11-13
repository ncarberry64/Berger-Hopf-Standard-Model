"""Checks of the direct source/adjoint phase contraction and its contacts."""
from pathlib import Path
import json
import numpy as np
import pytest
from scipy.linalg import solve

from bhsm.interface.muon_birth_trace_enriched_phase import load_enriched_endpoint
from bhsm.interface.muon_primal_native_phase_adjoint import (
    native_phase_midpoint_map,native_phase_load_rows,native_phase_named_border,
    contract_phase_native_target,chronological_native_phase_jacobian,
)

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def representation():
    return load_enriched_endpoint(
        'artifacts/muon_parent_gauge_geometry_correction_20261010/paired_field_endpoint_enriched_run_1',
        side='incoming',repository=ROOT)['representation']


def test_complete_oriented_action_rows_and_pair_axes(representation):
    maps=native_phase_midpoint_map(representation);P=maps['coordinates']['lift']
    n=maps['coordinates']['x_count'];rng=np.random.default_rng(342)
    load=rng.normal(size=(268,2,3));b=P.T@load.reshape(268,-1)
    h=-.000031;F=native_phase_load_rows(load,representation,h).reshape(358,-1)
    assert np.array_equal(F[:n],np.zeros((n,6)))
    assert np.array_equal(F[n:2*n],-h*b[:n])
    assert np.array_equal(F[2*n:3*n],b[n:2*n])
    assert np.array_equal(F[3*n:],b[2*n:])
    assert np.array_equal(maps['raw_from_phase'],P@maps['master_from_phase'])


@pytest.mark.parametrize('frame',['temporal','radial'])
def test_direct_adjoint_agrees_with_complete_forward_and_retains_reactions(representation,frame):
    rng=np.random.default_rng(197);J=np.diag(np.linspace(.7,2.1,358))
    J+=.00003*rng.normal(size=J.shape)
    # The algebra test connects the temporal/radial frame bands strongly.
    # An unrelated diagonal control has an almost singular radial border.
    temporal=native_phase_named_border(J,representation,frame='temporal')
    radial=native_phase_named_border(J,representation,frame='radial')
    Qt=np.linalg.qr(temporal['frame_matrix'].T)[0]
    Qr=np.linalg.qr(radial['frame_matrix'].T)[0]
    J+=.2*Qr@Qt.T
    target=rng.normal(size=268);load=rng.normal(size=(268,2,3));h=.000027
    a=contract_phase_native_target(J,representation,h,target,load,frame=frame)
    border=native_phase_named_border(J,representation,frame=frame)
    rhs=np.vstack((-a['phase_source_rows'].reshape(358,6),np.zeros((2,6))))
    forward=solve(border['matrix'],rhs)
    expected=a['phase_target_row']@forward[:358]
    assert np.allclose(a['native_mean_response_pair'].ravel(),expected,rtol=3e-12,atol=3e-12)
    assert np.allclose(a['auxiliary_Gauss_reactions'].reshape(2,6),forward[358:],rtol=3e-12,atol=3e-12)
    residual=J@forward[:358]+a['phase_source_rows'].reshape(358,6)
    reaction_rows=a['original_Euler_Gauss_reaction_rows'].reshape(358,6)
    residual_scale=np.linalg.norm(J)*np.linalg.norm(forward[:358])+np.linalg.norm(rhs[:358])
    assert np.linalg.norm(residual-reaction_rows)<2e-14*residual_scale
    assert a['auxiliary_Gauss_reaction_norm']>0
    assert a['original_adjoint_defect_norm']>0
    adjoint_scale=np.linalg.norm(border['matrix'])*np.linalg.norm(a['target_adjoint'])+np.linalg.norm(a['phase_target_row'])
    assert np.linalg.norm(border['matrix'].T@a['target_adjoint']-np.r_[a['phase_target_row'],0.,0.])<2e-14*adjoint_scale
    assert not a['full_forward_mean_response_materialized']


def test_actual_saved_cell_target_consumer_matches_forward_application(representation):
    folder=ROOT/'artifacts/muon_parent_gauge_geometry_correction_20261010/enriched_phase_outgoing_1steps_run_1'
    md=json.loads((folder/'result.json').read_text())
    with np.load(folder/'application.npz',allow_pickle=False) as f:J=f['stage_jacobian'][0]
    from bhsm.interface.muon_primal_cell_native_heat import actual_cell_heat_polynomial,actual_cell_even_y_target
    with np.load(folder/'application.npz',allow_pickle=False) as f:raw=f['stage_midpoint_raw'][0]
    polynomial=actual_cell_heat_polynomial(raw,representation,length=abs(md['span']))
    target=actual_cell_even_y_target(polynomial,1e-11)['paired_middle_minus_light_raw_cotangent']
    # Exact manufactured equation image tests the consumer on the stored
    # physical Jacobian, while avoiding an invented physical mean load.
    border=native_phase_named_border(J,representation,frame='temporal')
    rhs=np.zeros(360);rhs[:358]=border['midpoint_maps']['raw_from_phase'].T@target
    adjoint=solve(border['matrix'].T,rhs)
    rng=np.random.default_rng(931);dz=rng.normal(size=358)*1e-4
    forcing=-J@dz
    assert abs(adjoint[:358]@forcing+rhs[:358]@dz)<1e-18
    assert np.linalg.norm(border['matrix'].T@adjoint-rhs)<1e-20


def test_missing_cotangent_or_action_load_is_rejected(representation):
    J=np.eye(358)
    with pytest.raises(ValueError,match='cotangent'):
        contract_phase_native_target(J,representation,1e-5,None,np.zeros((268,8,8)))
    with pytest.raises(ValueError,match='load'):
        native_phase_load_rows(None,representation,1e-5)


def test_chronological_incoming_is_same_literal_action_cell(representation):
    from bhsm.interface.muon_birth_coupled_primal_midpoint import nonlinear_midpoint_rows
    rng=np.random.default_rng(507);n=106;m=40
    A=rng.normal(size=(252,252));H=(A+A.T)/2
    def action(eta):
        return dict(gradient=H@eta,hessian=H)
    x0=rng.normal(size=n);p0=rng.normal(size=n)
    x1=rng.normal(size=n);p1=rng.normal(size=n)
    v=rng.normal(size=n);y=rng.normal(size=m);h=-.000053
    original=nonlinear_midpoint_rows(np.r_[x1,p1,v,y],x0,p0,h,action)
    forward=nonlinear_midpoint_rows(np.r_[x0,p0,v,y],x1,p1,-h,action)
    reused=chronological_native_phase_jacobian(original['jacobian'],representation,h)
    assert np.array_equal(reused['jacobian'],forward['jacobian'])
    assert np.array_equal(original['midpoint_coefficients'],forward['midpoint_coefficients'])
    assert np.array_equal(-original['residual'][:2*n],forward['residual'][:2*n])
    assert np.array_equal(original['residual'][2*n:],forward['residual'][2*n:])
    assert reused['step']==-h
    assert reused['incoming_time_direction_reversed']
