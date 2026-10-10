"""Focused NEW local-action and arithmetic checks; not native anomaly tests."""
import json
from pathlib import Path
import sys
import numpy as np
import sympy as sp
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface import muon_native_induced_polarization as impl
OUT=ROOT/'artifacts/muon_native_induced_polarization_20261006/run_1'


def load(path):
    with np.load(path) as z:return {k:np.array(z[k]) for k in z.files}


def test_actual_real_frame_contact_and_current_duality():
    a=load(OUT/'affine_source_contacts.npz')
    c=json.loads((OUT/'result.json').read_text())['checks']
    assert a['real_test_frame'].shape==(240,32)
    assert np.linalg.norm(impl.reality(a['real_test_frame'])-a['real_test_frame'])==0
    assert c['same_frozen_span_residual']<4e-13
    assert c['real_frame_M_Gram_residual']<2e-14
    assert c['local_Riesz_identity_residual']<2e-15
    assert c['contact_real_direction_Hermiticity']<2e-15
    assert c['connected_n3_test_source_action_norm']>0
    assert a['local_real_contact_P_vA'].shape==(32,8,64,64)
    assert a['local_Riesz_current_coordinates'].shape==(8,224)


def test_factorized_contact_preserves_all_current_labels():
    a=load(OUT/'affine_source_contacts.npz')
    # One actually reached column, without allocating the full tensor.
    i=int(np.argmax(a['reached_contact_column_norms']))
    column=np.einsum('vaij,a->vij',a['local_real_contact_P_vA'],a['local_Riesz_current_coordinates'][:,i])
    assert np.isclose(np.linalg.norm(column),a['reached_contact_column_norms'][i],rtol=2e-14)
    assert np.allclose(np.trace(column,axis1=1,axis2=2),a['reached_contact_fibre_trace'][:,i],atol=1e-16)
    assert np.count_nonzero(a['reached_contact_column_norms'])==32


def test_compact_weak_first_row_against_actual_direct_coefficient_sum():
    from bhsm.interface.muon_parent_source_contact import parent_insertion
    a=load(OUT/'affine_source_contacts.npz');w=load(OUT/'compact_weak_first_jets.npz')
    parent=load(ROOT/'artifacts/muon_parent_source_contact_20261003/replay_reference/parent_source_contact.npz')
    source=load(ROOT/'artifacts/muon_matched_mechanical_source_20261002/replay_reference/matched_source_and_weak_actions.npz')
    rate=load(ROOT/'artifacts/muon_parent_source_rate_20261003/replay_reference/parent_source_rate_corrected.npz')
    rho=rate['gauss_rho'];nodes=parent['rho'];indices=rate['source_image_probe_columns']
    chi=np.interp(rho,nodes,parent['spinor_probe_hat_nodes'])
    r=np.interp(rho,nodes,parent['base_radius']);kernel=float(parent['T_b'])/r;f=kernel*chi
    value=0j;coeff=impl.split_coefficients(a['real_test_frame'])
    # An actual scalar entry, independently applying the coefficient matrices
    # node by node instead of the implementation's contracted einsums.
    vi=7;Ai=2;ci=1;di=3
    for n in (1,3):
        x=parent_insertion(source['saved_gamma_LR'],coeff[n][vi:vi+1],source['unit_trace_carrier_basis'])[0]
        xa=parent[f'Xi_A_unit_n{n}'][Ai,:,indices[ci]]
        dp=rate[f'D5_on_same_source_image_b_coefficient_n{n}'][:,Ai,:,ci]
        # Source-adjoint is an anti-Hermitian full field in this convention.
        phase=(-1.)**(np.arange(n+1)[None,:]-np.arange(n+1)[:,None])
        xd=x[...,::-1,::-1].conj().transpose(1,0,2,3)*phase
        assert np.linalg.norm(xd+x)<2e-14
        for g in range(64):
            dw=rate['D5_metric_common_A_on_compact_probes'][g,:,indices[di]]
            for m in range(n+1):
                for k in range(n+1):
                    value+=rate['node_volume_quadrature_weights'][g]*(
                        np.vdot(dp[g,:,m,k],f[g]*x[:,indices[di],m,k])+
                        np.vdot(f[g]*xa[:,m,k],kernel[g]*(xd[:,:,m,k]@dw)))
    assert np.allclose(value,w['parent_compact_K_0_v'][vi,Ai,ci,di],rtol=2e-13,atol=2e-15)
    assert np.linalg.norm(w['parent_compact_K_0_J'])>0
    assert np.linalg.norm(w['parent_compact_K_tau0_v'])>0
    assert np.linalg.norm(w['parent_compact_K_0tau_v'])>0


def test_all_control_heat_representations_and_moving_mass():
    c=json.loads((OUT/'arithmetic_control.json').read_text())
    assert c['classification']=='ARITHMETIC_CONTROL_ONLY'
    assert c['dimension']==3 and c['control_ell']==.7
    assert c['max_fixed_method_difference']<1e-13
    assert c['rank_factor_application_residual']<1e-14
    assert c['moving_method_difference']<1e-13
    assert c['nonzero_D_vJ_norm']>0
    assert c['moving_two_mass_terms_retained']
    sys.path.insert(0,str(ROOT/'scripts'))
    from control_muon_induced_heat import control_data
    j=impl.generalized_form_jets(*control_data())
    _,_,_,_,M,Mv,Mj,Mvj=control_data()
    rhs=j['K_vJ']-Mvj@j['A']-Mv@j['A_J']-Mj@j['A_v']
    assert np.linalg.norm(M@j['A_vJ']-rhs)<1e-15
    assert np.linalg.norm(Mv@j['A_J'])>0 and np.linalg.norm(Mj@j['A_v'])>0


def test_crossing_rule_does_not_select_mixed_impedance_response():
    q=dict(I=sp.Symbol('E',positive=True),C=sp.Symbol('C'),Ftau=sp.Symbol('Ft',nonzero=True),
        Itau=sp.Symbol('It'),Itautau=sp.Symbol('Itt'),Ftautau=sp.Symbol('Ftt'),
        Iv=sp.Symbol('Iv'),Ij=sp.Symbol('Ij'),Ivj=sp.Symbol('Ivj'),
        Fv=sp.Symbol('Fv'),Fj=sp.Symbol('Fj'),Fvj=sp.Symbol('Fvj'),
        Itauv=sp.Symbol('Itv'),Itauj=sp.Symbol('Itj'),Ftauv=sp.Symbol('Ftv'),Ftauj=sp.Symbol('Ftj'))
    r=impl.owner_length_jet(**q)
    v,j=sp.symbols('v j');t=r['tau_v']*v+r['tau_J']*j+r['tau_vJ']*v*j
    energy=(q['I']+q['Iv']*v+q['Ij']*j+q['Ivj']*v*j+q['Itau']*t+
        q['Itauv']*t*v+q['Itauj']*t*j+q['Itautau']*t*t/2)
    assert sp.simplify(sp.diff(energy,v,j).subs({v:0,j:0})-r['E_vJ'])==0
    assert sp.simplify(sp.diff(1/energy,v,j).subs({v:0,j:0})-r['ell_vJ'])==0
    # Add k*v*j to BOTH I and C: F/crossing remains identical. This is only
    # an insufficiency proof for the displayed owner rule, not a BHSM model.
    k=sp.Symbol('k');q2=dict(q,Ivj=q['Ivj']+k);r2=impl.owner_length_jet(**q2)
    assert sp.simplify(r2['E_vJ']-r['E_vJ']-k)==0
    assert sp.simplify(r2['ell_vJ']-r['ell_vJ']+k/q['I']**2)==0


def test_lower_limit_formula_including_mixed_length():
    v,j=sp.symbols('v j');p,c=sp.symbols('p c',positive=True)
    pv,pj,pvj,cv,cj,cvj=sp.symbols('pv pj pvj cv cj cvj')
    P=p+pv*v+pj*j+pvj*v*j;C=c+cv*v+cj*j+cvj*v*j
    exact=sp.diff(-sp.expint(1,C*P)/2,v,j).subs({v:0,j:0})
    Q=sp.exp(-c*p)/(2*p);Qp=sp.diff(Q,p)
    lower=impl.lower_limit_mixed(c,cv,cj,cvj,sp.exp(-c*p),p*sp.exp(-c*p),pv*sp.exp(-c*p),pj*sp.exp(-c*p))
    assert sp.simplify(exact-Q*pvj-Qp*pv*pj-lower)==0


def test_owned_local_operand_frame_conversion_and_claim_boundary():
    r=json.loads((OUT/'result.json').read_text());c=r['checks']
    assert c['local_subtraction_same_frame_residual']<c['propagated_change_of_frame_allowance']
    assert c['endpoint_H_placeholder_consumed'] is False
    assert r['physical_a_mu'] is None and r['physical_g_mu'] is None
    assert r['bulk_heat']['full'] is None and not r['target_evaluated']
    assert r['execution']['previous_production_replays']==0
    assert r['execution']['previous_shifted_solves']==0
    assert not r['bulk_heat']['physical_default_length_used']
    assert not r['bulk_heat']['primitive_Lorentz_inserted_as_native']
    assert r['relative_completion']['status']=='UNEVALUATED'
    assert r['one_explicit_unprovided_operand']['operand'].startswith('E_vJ')
