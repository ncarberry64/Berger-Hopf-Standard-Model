"""Chronological canonical endpoints and actual transported current jets."""
import json
import numpy as np
import pytest
from bhsm.interface.muon_parent_gauge_geometry_correction import ROOT
from bhsm.interface.muon_birth_attached_phase import load_attached_endpoint
from bhsm.interface.muon_birth_coupled_primal_midpoint import nonlinear_midpoint_rows
from bhsm.interface.muon_charged_current_cell_amputation import (
    variational_cayley_amputation,amputated_charged_current_action_source,
)
from bhsm.interface.muon_chronological_charged_current import chronological_phase_cell


@pytest.fixture(scope='module')
def actual():
    base=ROOT/'artifacts/muon_parent_gauge_geometry_correction_20261010'
    endpoint=load_attached_endpoint(base/'paired_attachment_endpoint_run_1',side='incoming')
    data={}
    for side in ('incoming','outgoing'):
        folder=base/f'attached_phase_{side}_1steps_run_1'
        receipt=json.loads((folder/'result.json').read_bytes())
        with np.load(folder/'application.npz',allow_pickle=False) as a:arrays={k:a[k].copy() for k in a.files}
        cell=chronological_phase_cell(arrays['stage_jacobian'][0],arrays['stage_unknowns'][0],
            arrays['initial_master'],arrays['initial_p'],endpoint['representation'],receipt['span'])
        data[side]=(receipt,arrays,cell)
    return endpoint['representation'],data


@pytest.mark.parametrize('side',['incoming','outgoing'])
def test_actual_full220_endpoints_and_midpoint_rates_are_preserved(actual,side):
    rep,data=actual;receipt,arrays,cell=data[side];n=106
    assert cell['step']==1e-5
    np.testing.assert_array_equal(cell['midpoint_raw'],arrays['stage_midpoint_raw'][0])
    np.testing.assert_array_equal(cell['unknowns'][212:],arrays['stage_unknowns'][0,212:])
    np.testing.assert_array_equal(cell['jacobian'][212:],arrays['stage_jacobian'][0,212:])
    if side=='incoming':
        np.testing.assert_array_equal(cell['initial_x'],arrays['stage_unknowns'][0,:n])
        np.testing.assert_array_equal(cell['initial_p'],arrays['stage_unknowns'][0,n:2*n])
        np.testing.assert_array_equal(cell['unknowns'][:n],arrays['initial_master'][:n])
        np.testing.assert_array_equal(cell['unknowns'][n:2*n],arrays['initial_p'])
        assert cell['incoming_time_direction_reversed']
    else:
        np.testing.assert_array_equal(cell['unknowns'],arrays['stage_unknowns'][0])
        np.testing.assert_array_equal(cell['jacobian'],arrays['stage_jacobian'][0])
        assert not cell['incoming_time_direction_reversed']


def test_endpoint_reversal_is_the_same_literal_nonlinear_action_not_a_rate_reversal_CONTROL_ONLY(actual):
    rep,_=actual;rng=np.random.default_rng(704);n=106;m=40
    H=rng.normal(size=(252,252));H=(H+H.T)/2
    # A nonlinear coupled real action with nonzero velocity/algebraic contacts.
    def action(eta):
        return dict(gradient=H@eta+eta**3,hessian=H+np.diag(3*eta**2))
    eta0=rng.normal(size=252);p0=rng.normal(size=n);z=rng.normal(size=358);h=-.000037
    original=nonlinear_midpoint_rows(z,eta0[:n],p0,h,action)
    cell=chronological_phase_cell(original['jacobian'],z,eta0,p0,rep,h)
    forward=nonlinear_midpoint_rows(cell['unknowns'],cell['initial_x'],cell['initial_p'],cell['step'],action)
    np.testing.assert_array_equal(cell['jacobian'],forward['jacobian'])
    np.testing.assert_array_equal(cell['midpoint_master'],forward['midpoint_coefficients'])
    np.testing.assert_array_equal(forward['residual'][:2*n],-original['residual'][:2*n])
    np.testing.assert_array_equal(forward['residual'][2*n:],original['residual'][2*n:])


def test_cayley_initial_frame_change_conjugates_the_entire_noncommuting_source_CONTROL_ONLY():
    K=np.array([[2,1+2j],[1-2j,-3]],complex)
    D=np.array([[[1,3j],[-3j,2]],[[0,2],[2,0]]],complex)
    plus=variational_cayley_amputation(K,D,.31)
    minus=variational_cayley_amputation(K,D,-.31)
    U=plus['propagator']
    np.testing.assert_allclose(minus['propagator'],U.conj().T,atol=5e-16,rtol=4e-16)
    expected=np.einsum('ij,rjk,kl->ril',U,plus['on_shell_action_source_operators'],U.conj().T)
    np.testing.assert_allclose(minus['on_shell_action_source_operators'],expected,atol=8e-16,rtol=7e-16)
    assert np.linalg.norm(expected-plus['on_shell_action_source_operators'])>1


@pytest.mark.parametrize('index',[37,98,100,260])
def test_actual_chronological_incoming_current_matches_direct_propagator_derivative(actual,index):
    rep,data=actual;cell=data['incoming'][2];raw=cell['midpoint_raw'];h=cell['step']
    source=amputated_charged_current_action_source(raw,rep,h)
    epsilon=2e-6;p=raw.copy();m=raw.copy();p[index]+=epsilon;m[index]-=epsilon
    up=amputated_charged_current_action_source(p,rep,h)['amputation']['propagator']
    um=amputated_charged_current_action_source(m,rep,h)['amputation']['propagator']
    derivative=(up-um)/(2*epsilon)
    op=-1j*source['amputation']['propagator'].conj().T@derivative/h
    expected=np.einsum('aij,ji->a',source['current_matrices'],op).real
    np.testing.assert_allclose(source['raw_source'][index],expected,atol=2e-9,rtol=5e-6)
    assert source['reached_fixed_Y_H_source_norm']>1e-13
    assert not source['physical_LSZ_pole_or_local_Fermi_coefficient_assigned']


def test_incomplete_or_nonreal_cell_is_rejected(actual):
    rep,data=actual;receipt,a,_=data['incoming'];args=[a['stage_jacobian'][0],a['stage_unknowns'][0],a['initial_master'],a['initial_p'],rep,receipt['span']]
    for index in (1,2,3):
        bad=list(args);bad[index]=np.asarray(bad[index],complex)
        with pytest.raises(ValueError,match='complete real'):chronological_phase_cell(*bad)
    bad=list(args);bad[0]=bad[0].copy();bad[0][0,0]+=1e-8
    with pytest.raises(ValueError,match='midpoint row contract'):chronological_phase_cell(*bad)
