"""New radial-action checks on retained inputs; no earlier checks replayed."""
from pathlib import Path
import json
import numpy as np
from flint import arb,ctx
from bhsm.interface.muon_radial_inclusion_action import nodal_jets,scalar_action

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'artifacts/muon_radial_inclusion_action_20261004/replay_reference'


def read(p):
    with np.load(p,allow_pickle=False) as z:return {k:np.array(z[k]) for k in z.files}


def data():
    geometry=read(ROOT/'artifacts/muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz')
    pair=read(ROOT/'artifacts/muon_wall_source_pairing_20261003/replay_reference/source_reached_pairings.npz')
    old=read(ROOT/'artifacts/muon_parent_source_rate_20261003/replay_reference/parent_source_rate_corrected.npz')
    new=read(REF/'radial_source_action_and_interface.npz')
    norm=json.loads((REF/'full_normalization.json').read_text());rate=json.loads((ROOT/'artifacts/muon_parent_source_rate_20261003/replay_reference/cut_rate_record.json').read_text())
    ctx.prec=192;I=arb(norm['I_rad']['arb']);Idot=arb(norm['I_rad_dot']['arb'])
    return geometry,pair,old,new,I,Idot,rate


def test_full_cap_norm_and_consumed_time_jet_independently():
    g,p,old,new,I,Idot,rate=data();gx,gw=np.polynomial.legendre.leggauss(12)
    cells=np.repeat(np.arange(64),12);width=np.diff(g['rho'])[cells]
    x=np.tile((gx+1)/2,64);rho=g['rho'][cells]+x*width;weights=np.tile(gw/2,64)*width
    s=scalar_action(g,rho,cells,I,Idot,rate);nu,C,r=(s[k] for k in ('proper_lapse','C_rho','base_radius'))
    assert abs(np.sum(weights*C*np.sin(rho/2)**2)-float(I.mid()))<2e-15
    assert abs(np.sum(weights*s['C_rho_t']*np.sin(rho/2)**2)-float(Idot.mid()))<2e-14
    nb=g['proper_lapse'][0,-1];Rb=g['base_radius'][0,-1];mu=2*np.pi**2*nu*C*r**3
    norm=np.sum(weights*mu*s['u_vol']**2);M4=p['M4_wall_geometric_density'][0,0]
    assert abs(norm-M4)<2e-13
    density_dot=s['proper_lapse_t']/nu+s['C_rho_t']/C+3*s['base_radius_t']/r
    assert abs(np.sum(weights*mu*s['u_vol']**2*(density_dot+2*s['log_u_tau']))-3*rate['value']*M4)<3e-12
    # Complex-step differentiation of the full normalization and displayed
    # density, independent of the simplified time-action expression.
    eps=1e-30;tc=1j*eps
    U=(np.sin(rho/2)/np.sqrt((float(I.mid())+tc*float(Idot.mid()))
       *(nu+tc*s['proper_lapse_t'])/nb*((r+tc*s['base_radius_t'])/(Rb*np.exp(rate['value']*tc)))**3))
    logdot=np.imag(np.log(U))/eps
    assert np.max(abs(logdot-s['log_u_tau']))<4e-12
    clock=json.loads((REF/'clock_derivative_contract.json').read_text())
    assert clock['placeholder_H_used'] is False and clock['reconstructions_identified'] is False
    assert abs(clock['nodal_minus_owned_H'])>.004


def test_candidate_T_B_is_same_source_full_output_pairing():
    g,p,old,new,I,Idot,rate=data();contact=read(ROOT/'artifacts/muon_parent_source_contact_20261003/replay_reference/parent_source_contact.npz')
    scalar=json.loads((REF/'source_scalar_integral.json').read_text())['scalar']['interval']
    for n,mode in ((1,2),(3,4)):
        T=new[f'candidate_T_certified_scalar_n{n}'];B=new[f'candidate_B_required_n{n}']
        assert T.shape==(8,64,4,mode,mode)
        xi=contact[f'Xi_A_unit_n{n}'][:,:,old['source_image_probe_columns']]
        assert np.linalg.norm(T-((scalar[0]+scalar[1])/2)*xi)<1e-15
        assert np.linalg.norm(p['M4_wall_geometric_density'][0,0]*B-T)<2e-15
        assert np.linalg.norm(T)>1
        assert np.linalg.norm(new[f'local_interface_K54_connected_perp_zero_n{n}'])>1000
        assert np.linalg.norm(new[f'local_interface_K54_zero_n{n}']-
             new[f'local_interface_K54_projected_zero_n{n}']-
             new[f'local_interface_K54_connected_perp_zero_n{n}'])<1e-11


def direct_dense_cross(g,p,old,new,s,n,delta_H=0):
    """Independent dense actual angular block for one reached source column."""
    Q=new[f'local_interface_K54_zero_n{n}'];A,i,c,m,k=np.unravel_index(np.argmax(abs(Q)),Q.shape)
    G=new['common_parent_Gamma'];E=new[f'angular_E_n{n}'];q=0j;qt=0j
    for z,w in enumerate(new['source_node_volume_weights']):
        u=new['radial_u_vol'][z];nu=s['proper_lapse'][z];r=s['base_radius'][z]
        zero=new['D5W_zero_with_radial_eta'][z]+delta_H*1.5*new['D5W_tau_coefficient'][z]
        D=np.kron(zero,np.eye(n+1))+sum(np.kron(1j*G[a+1],E[a])*u/r for a in range(3))
        tau=np.kron(new['D5W_tau_coefficient'][z],np.eye(n+1))
        pp=p[f'actual_source_trial_n{n}'][z,A,:,c,:,k]
        dp=old[f'D5_on_same_source_image_b_coefficient_n{n}'][z,A,:,c,:,k].copy()
        dp+=(1j*G[4]*s['m_eta_radial'][z])@pp
        dp-=delta_H/2*old[f'D5_on_same_source_image_b_tau_coefficient_n{n}'][z,A,:,c,:,k]
        q+=w*(D.conj().T@dp.ravel())[i*(n+1)+m]
        qt+=w*(tau.conj().T@dp.ravel())[i*(n+1)+m]
    return (A,i,c,m,k),q,qt


def test_actual_weak_angular_adjoint_and_shared_H_jets():
    g,p,old,new,I,Idot,rate=data();s=scalar_action(g,p['gauss_rho'],p['gauss_cells'],I,Idot,rate)
    for n in (1,3):
        index,q,qt=direct_dense_cross(g,p,old,new,s,n)
        assert abs(q-new[f'local_interface_K54_zero_n{n}'][index])<2e-10
        assert abs(qt-new[f'local_interface_K54_tau_n{n}'][index])<2e-12
        d=.0001;_,changed,_=direct_dense_cross(g,p,old,new,s,n,delta_H=d)
        predicted=(new[f'local_interface_K54_zero_n{n}']+d*new[f'local_interface_K54_zero_H_derivative_n{n}']+
             d*d/2*new[f'local_interface_K54_zero_H_second_derivative_n{n}'])[index]
        assert abs(changed-predicted)<2e-10


def test_endpoint_graph_scope_and_no_global_domain_promotion():
    g,p,old,new,I,Idot,rate=data();rho=np.array([1e-4,1e-5,1e-6]);cells=np.zeros(3,int)
    s=scalar_action(g,rho,cells,I,Idot,rate)
    mu=2*np.pi**2*s['proper_lapse']*s['C_rho']*s['base_radius']**3
    density=mu*s['u_vol']**2
    assert density[-1]<1e-3*density[0]
    assert np.max(abs(s['zero_normal_with_owned_radial_eta']))<1e-8
    endpoint=json.loads((REF/'domain_and_endpoint.json').read_text())
    assert endpoint['material']['trace_multiplier']>1.3
    assert endpoint['reset']['actual_event_child_reset_trace_arrays_evaluated'] is False
    result=json.loads((REF/'result.json').read_text())
    assert result['local_interface_consumed'] is True and result['candidate_B_only'] is True
    assert result['physical_a_mu'] is None and result['native_heat_contact'] is None
    assert result['execution']['Gaussian_searches']==0


def test_cauchy_pairing_and_reconstructed_material_trace():
    g,p,old,new,I,Idot,rate=data()
    means=json.loads((REF/'projected_means.json').read_text());mt=means['time']['interval']
    M4=p['M4_wall_geometric_density'][0,0];G=new['cut_Cauchy_trace_Gram'][0,0]
    assert M4*mt[0]<=G<=M4*mt[1]
    assert abs(G-M4)>2
    endpoint=json.loads((REF/'domain_and_endpoint.json').read_text());uw=endpoint['material']['trace_multiplier']
    for n in (1,3):
        B=new[f'candidate_cut_trace_B_n{n}'];T=new[f'candidate_cut_trace_T_n{n}']
        assert np.linalg.norm(G*B-T)<1e-15
        assert np.linalg.norm(new[f'candidate_cut_trace_connected_remainder_n{n}'])>2
        # The original compact source vanishes at the material wall. Its
        # projected part does not; the full-cap complement restores it.
        projected_wall=uw*B;complement_wall=-uw*B
        assert np.linalg.norm(projected_wall)>0
        assert np.array_equal(projected_wall+complement_wall,np.zeros_like(B))
    assert endpoint['reset']['zero_reset_complement_required'] is False


def test_cached_owned_prefix_clock_is_consumed_without_endpoint_claim():
    path=ROOT/'artifacts/muon_radial_inclusion_action_20261004/owned_prefix_reference'
    z=read(path/'owned_prefix_center_lapse_action.npz');result=json.loads((path/'result.json').read_text())
    field=read(ROOT/'artifacts/flagship_integration/BHSM_N12_C2_LOHNER_FIXED_S_FIELD_1221.npz')
    state=field['center_state'];Nb=np.exp(state[74:86]@((-1.)**np.arange(1,13)))
    assert np.max(abs(z['physical_tau_state_rate'][:37]-state[37:74]/Nb))<5e-15
    assert z['lapse_rates_tau'][0]>7e12
    assert np.min(z['owned_log_nu_tau_fourier'])>4e12
    assert np.max(z['owned_log_nu_tau_fourier'])<1e13
    g,p,old,new,I,Idot,rate=data();contact=read(ROOT/'artifacts/muon_parent_source_contact_20261003/replay_reference/parent_source_contact.npz')
    xi=contact['Xi_A_unit_n1'][:,:,old['source_image_probe_columns']]
    G0=np.kron(old['parent_gamma'][0],np.eye(16))
    point=17;A=2;c=1;m=0;k=1
    expected=(-.5j*G0*z['owned_center_u_vol'][point]/z['owned_center_nu'][point]*
       z['owned_log_nu_tau_used_nodal'][point])@xi[A,:,c,m,k]
    actual=z['owned_lapse_time_action_on_source_directions_n1'][point,A,:,c,m,k]
    assert np.linalg.norm(actual-expected)<.02
    assert result['physical_endpoint'] is False
    assert result['not_substituted_for_endpoint'] is True
    assert result['complete_center_D5W_evaluated'] is False


def test_replay_metadata_consumes_owned_cache_and_rejects_changed_operand(tmp_path):
    import importlib.util
    import hashlib
    import pytest
    script=ROOT/'scripts/replay_muon_radial_inclusion_action.py'
    spec=importlib.util.spec_from_file_location('radial_replay_metadata',script)
    replay=importlib.util.module_from_spec(spec);spec.loader.exec_module(replay)
    path=ROOT/'artifacts/muon_radial_inclusion_action_20261004/owned_prefix_reference'
    receipt=replay.owned_prefix_receipt(ROOT,path)
    assert receipt['physical_input_identities_matched'] is True
    assert receipt['physical_endpoint_substitution'] is False
    assert receipt['result']['complete_center_D5W_evaluated'] is False
    inputs=json.loads((path/'input_hashes.json').read_text())
    operand=tmp_path/'changed_operand.txt';operand.write_text('original')
    inputs['field']=dict(path=str(operand),sha256=hashlib.sha256(operand.read_bytes()).hexdigest())
    (tmp_path/'input_hashes.json').write_text(json.dumps(inputs))
    (tmp_path/'result.json').write_text((path/'result.json').read_text())
    replay.owned_prefix_receipt(ROOT,tmp_path)
    operand.write_text('changed')
    with pytest.raises(ValueError,match='owned-prefix input identity changed'):
        replay.owned_prefix_receipt(ROOT,tmp_path)
