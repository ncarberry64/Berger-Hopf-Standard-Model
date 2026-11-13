"""Targeted endpoint clock/source tests, without old production replays."""
from pathlib import Path
import copy,json
import numpy as np
from flint import arb,ctx
from bhsm.interface.muon_endpoint_clock_actions import endpoint_rates,Fourier_log_lapse

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'artifacts/muon_endpoint_clock_20261004/replay_reference'
OLD=ROOT/'artifacts/muon_radial_inclusion_action_20261004/replay_reference'
def read(p):
    with np.load(p,allow_pickle=False) as z:return {k:np.array(z[k]) for k in z.files}
def data():
    base=ROOT/'artifacts/flagship_integration'
    return read(base/'BHSM_N12_C2_LOHNER_STEP_1222.npz'),json.loads((base/'BHSM_N12_C2_LOHNER_STEP_1222.json').read_text()),read(base/'BHSM_N12_C2_LOHNER_BORDERED_MATRIX_1221.npz'),json.loads((base/'BHSM_N12_C2_LOHNER_GROWTH_1221.json').read_text()),json.loads((base/'BHSM_N12_C2_LOHNER_RESPONSE_BALL_1221.json').read_text())


def test_endpoint_domain_and_Delta_cancellation_before_intervals():
    args=data();point=endpoint_rates(*args,tube=False);tube=endpoint_rates(*args,tube=True)
    changed=copy.deepcopy(args[1]);changed['domain']['Delta_interval']=[-1e100,1e100]
    independent=endpoint_rates(args[0],changed,*args[2:],tube=True)
    assert independent['result']['m_tau']==tube['result']['m_tau']
    assert float(arb(tube['result']['total_radius']['arb']).upper())<args[1]['domain']['selected_domain_radius']
    assert float(arb(point['result']['sigma']['arb']).mid())>float(args[1]['segment']['signed_descriptor_start'])
    prior=json.loads((ROOT/'artifacts/muon_radial_inclusion_action_20261004/owned_prefix_reference/result.json').read_text())
    assert not point['m'][0].contains(arb(prior['owned_lapse_rates'][0]['arb']))
    assert point['result']['proof_center_substituted'] is False


def test_physical_configuration_and_exact_proper_boundary():
    args=data();point=endpoint_rates(*args,tube=False);y=args[0]['endpoint_predictor_center']
    from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data
    qw,_,_,_=metric_data();sigma=arb(args[1]['segment']['signed_descriptor_end'])
    for k in range(37):
        independently_cancelled=sigma*arb(float(qw[k]))*arb(float(y[37+k]))/(arb(float(qw[k]))*point['Nb']*sigma)
        assert point['q'][k].overlaps(independently_cancelled)
    assert Fourier_log_lapse(np.pi/2,point['m'],proper_boundary=True).is_zero()
    exact_boundary=sum((point['m'][k]*(((k+1)*arb.pi()).cos()-int((-1)**(k+1))) for k in range(12)),arb(0))
    assert exact_boundary.contains(0)
    assert float(exact_boundary.abs_upper())<1e-35
    result=json.loads((REF/'result.json').read_text())
    assert arb(result['proper_boundary_Lnu']['arb']).is_zero()
    assert result['proper_boundary_Lnu']['interval'][0]<=0<=result['proper_boundary_Lnu']['interval'][1]


def test_owned_normalization_derivative_and_propagated_interpolation():
    z=read(REF/'endpoint_clock_source_and_interface.npz');r=json.loads((REF/'result.json').read_text())
    g=read(ROOT/'artifacts/muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz')
    gx,gw=np.polynomial.legendre.leggauss(12);total=0
    for k in range(64):
        l,h=g['rho'][k:k+2];x=(gx+1)/2
        Cdot=z['action_C_tau_nodes'][:,0]/2+z['action_C_tau_nodes'][:,1]/2
        vals=(1-x)*Cdot[k]+x*Cdot[k+1]
        total+=(h-l)*np.sum(gw/2*vals*np.sin((l+(h-l)*x)/2)**2)
    assert abs(total-sum(r['action_I_dot']['interval'])/2)<1e-14
    assert not arb(r['action_I_dot']['arb']).overlaps(arb(r['preserved_nodal_I_dot']['arb']))
    assert r['direct_minus_nodal_max_upper']['interval'][0]>1e9
    for n in (1,3):
        assert r['norms'][f'n{n}']['direct_vs_nodal_action_difference_bound']['interval'][0]>1e9
        assert r['norms'][f'n{n}']['endpoint_tube_lapse_action_error_bound']['interval'][0]>r['norms'][f'n{n}']['coefficient_only_lapse_action_error_bound']['interval'][1]


def test_signed_actual_reached_lapse_action():
    z=read(REF/'endpoint_clock_source_and_interface.npz');old=read(OLD/'radial_source_action_and_interface.npz')
    c=read(ROOT/'artifacts/muon_parent_source_contact_20261003/replay_reference/parent_source_contact.npz')
    a=read(ROOT/'artifacts/muon_parent_source_rate_20261003/replay_reference/parent_source_rate_corrected.npz')
    g0=1j*old['common_parent_Gamma'][0]
    for n in (1,3):
        xi=c[f'Xi_A_unit_n{n}'][:,:,a['source_image_probe_columns']]
        index=np.unravel_index(np.argmax(abs(z[f'lapse_only_action_n{n}'])),z[f'lapse_only_action_n{n}'].shape)
        point,A,o,c0,m,k=index;coef=sum(z['endpoint_lapse_only_D5W_scalar'][point])/2
        expected=coef*(g0@xi[A,:,c0,m,k])[o]
        assert abs(expected-z[f'lapse_only_action_n{n}'][index])<.125
        assert np.linalg.norm(z[f'updated_D5W_source_action_n{n}']-old[f'D5W_actual_source_zero_n{n}']-z[f'all_time_action_delta_n{n}'])<1


def test_independent_complete_local_weak_update_with_pair_terms():
    z=read(REF/'endpoint_clock_source_and_interface.npz');old=read(OLD/'radial_source_action_and_interface.npz')
    p=read(ROOT/'artifacts/muon_wall_source_pairing_20261003/replay_reference/source_reached_pairings.npz')
    g=read(ROOT/'artifacts/muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz')
    from bhsm.interface.muon_radial_inclusion_action import nodal_jets
    j=nodal_jets(g,p['gauss_rho'],p['gauss_cells']);G=old['common_parent_Gamma']
    for n in (1,3):
        Q=z[f'updated_local_K54_zero_n{n}'];A,i,c,m,k=np.unravel_index(np.argmax(abs(Q)),Q.shape)
        value=0j;tv=0j
        for node,w in enumerate(old['source_node_volume_weights']):
            D=np.kron(z['updated_D5W_zero'][node],np.eye(n+1))
            for a in range(3):D+=np.kron(1j*G[a+1],old[f'angular_E_n{n}'][a])*old['radial_u_vol'][node]/j['base_radius'][node]
            dp=z[f'updated_D5p_source_action_n{n}'][node,A,:,c,:,k].ravel()
            value+=w*(D.conj().T@dp)[i*(n+1)+m]
            tau=np.kron(old['D5W_tau_coefficient'][node],np.eye(n+1))
            tv+=w*(tau.conj().T@dp)[i*(n+1)+m]
        assert abs(value-Q[A,i,c,m,k])<.25
        assert abs(tv-z[f'updated_local_K54_tau_n{n}'][A,i,c,m,k])<2e-10
    r=json.loads((REF/'result.json').read_text())
    assert r['physical_current_jet_promoted'] is False and r['native_heat'] is None
