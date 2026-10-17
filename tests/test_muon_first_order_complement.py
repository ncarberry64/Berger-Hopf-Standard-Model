"""Checks of the newly saved first-order reduction, without production replay."""
from pathlib import Path
from fractions import Fraction as F
import json
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/muon_first_order_complement_20261006/run_2'


@pytest.fixture(scope='module')
def cached():
    with np.load(OUT/'first_order_compact_reduction.npz') as z:
        a={k:np.array(z[k]) for k in z.files}
    return a,json.loads((OUT/'result.json').read_text())


def test_joint_domain_and_physical_wall_frame(cached):
    a,r=cached;P=a['physical_left_projector']
    assert np.linalg.norm(P@P-P)==0
    assert a['wall_frame_TL'].shape==(12,6)
    assert a['A_QQ'].shape==(24,24) and a['A_QR'].shape==(24,12)
    assert r['source_frame']['wall_input_frame_residual']<2e-14
    assert r['source_frame']['Gamma0_closure_residual']<2e-14
    assert r['source_frame']['dependent_Gamma0_columns_not_added']
    assert not r['source_frame']['physical_e_R_realization']
    for p in r['first_order_column_checks']:
        assert p['coefficient_proof']['radial_probe_end_traces']==[0,0]
    assert r['domain']['complement'].startswith('not p-W Bvol p')


def test_actual_formal_eta_dual_and_reached_complement(cached):
    a,r=cached
    path=ROOT/'artifacts/muon_radial_inclusion_action_20261004/replay_reference/radial_source_action_and_interface.npz'
    with np.load(path) as z:G=z['common_parent_Gamma']
    mass=1j*G[0]@G[4]
    assert np.linalg.norm(mass+mass.conj().T)<2e-14
    for p in r['first_order_column_checks']:
        proof=p['coefficient_proof'];act=p['action_proof']
        assert proof['geometric_formal_dual_time_divergence_residual']<1e-13
        assert proof['geometric_formal_dual_normal_divergence_residual']<1e-13
        assert act['normal_Euler_outside_compact_p_support_L2_norm']>6
        assert act['full_Euler_off_p_frame_L2_norm']>40
        assert act['diagnostic_L2_not_used_as_first_order_inverse']
    for node in (3,4):
        with np.load(ROOT/f'artifacts/muon_retained_tail_core_20261005/run_1/points/node_{node:02}.npz') as z:
            assert abs(z['Ms'][0,0].imag)/abs(z['Ms'][0,0].real)<5*np.finfo(float).eps
            proofs=r['first_order_column_checks'][node-3]['action_proof']['selected_cached_raw_actions']
            for n in (1,3):
                assert proofs[f'n{n}']['raw_p_columns_vs_cache']/np.linalg.norm(z[f'Dp_n{n}'])<5e-15
                assert proofs[f'n{n}']['raw_W_columns_vs_cache']/np.linalg.norm(z[f'DWp_n{n}'])<5e-15


def multiply(a,b):
    c=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):c[i+j]+=x*y
    return c


def integral(p):return sum((x/F(i+1) for i,x in enumerate(p)),F(0))


def test_temporal_element_against_exact_rational_moments(cached):
    a,_=cached
    phi=[[F(0),F(1),F(-1)],[F(0),F(-1),F(3),F(-2)]]
    dp=[[F(1),F(-2)],[F(-1),F(6),F(-6)]]
    d=a['node_moments_S0'].shape[-1];expected=np.zeros((2*d,2*d),complex)
    for i in range(2):
        for j in range(2):
            product=multiply(phi[i],phi[j])
            q=multiply(phi[i],dp[j]);v=multiply(dp[i],phi[j])
            q=[x-y for x,y in zip(q,v)]
            h0=[float(integral(multiply(product,w))) for w in ([F(1),F(-1)],[F(0),F(1)])]
            h1=[float(integral(multiply(q,w))/2) for w in ([F(1),F(-1)],[F(0),F(1)])]
            expected[i*d:(i+1)*d,j*d:(j+1)*d]=sum(h0[k]*a['temporal_jacobians'][k]*a['node_moments_S0'][k]+
                h1[k]*a['node_moments_S1'][k] for k in (0,1))
    assert np.linalg.norm(expected-a['A_full'])/np.linalg.norm(expected)<3e-15


def test_first_order_restricted_solve_and_claim_boundary(cached):
    a,r=cached;QQ=a['A_QQ'];QR=a['A_QR'];RQ=a['A_RQ']
    X=-a['complement_solution_map']
    assert np.linalg.norm(QQ@X-QR)<3e-16
    assert np.linalg.norm(a['restricted_correction']+RQ@X)<3e-16
    spectrum=np.linalg.eigvalsh(QQ)
    assert spectrum[0]<0<spectrum[-1]  # first-order action, not positive square
    assert r['restricted_solve']['A_QQ_condition']<1.01
    assert r['restricted_solve']['restricted_correction_matrix_norm']>.18
    assert r['source_frame']['wall_test_original_load_projection_norm']<2e-14
    assert abs(complex(*r['restricted_solve']['restricted_correction_contraction']))<1e-30
    assert r['matching']['complete_A_eff'] is None
    assert r['source_jet']['physical_source_stationary_return'] is None
    assert not r['restricted_solve']['positive_squared_inverse_used']
    assert not r['native_operator_updated'] and not r['proposal_adopted']
    assert not r['accepted_parent_solution_changed'] and not r['frozen_locals_changed']


def test_once_owned_intrinsic_LL_completion(cached):
    a,_=cached
    out=OUT/'ll_completion'
    with np.load(out/'complete_LL_action.npz') as z:
        c={k:np.array(z[k]) for k in z.files}
    r=json.loads((out/'result.json').read_text())
    assert np.linalg.norm(c['A_RR_complete_LL']-a['A_RR_parent']-c['A_intrinsic_LL_canonical'])<1e-15
    assert np.linalg.norm(c['A_eff_complete_LL_compact']-c['A_RR_complete_LL']-a['restricted_correction'])<1e-15
    # The intrinsic time density has the same physical LL pairing and
    # canonical transformation as the parent. No independent field rescale.
    for k in (0,1):
        S1=c['intrinsic_point_S1'][k]
        gram=(-1j*S1).real
        assert np.linalg.norm(S1+S1.conj().T)<1e-13
        assert np.linalg.eigvalsh(gram)[0]>0
        C=a['canonical_maps'][k,0]
        assert np.linalg.norm(gram/(C*C)-np.eye(6)*np.trace(gram/(C*C))/6)<1e-12
    assert r['QQ_solution_reused'] and not r['QQ_solution_rerun']
    assert not r['interpreted_as_required_nonlocal_zero']
    assert r['kinetic_low_energy_matching_coefficient'] is None
    assert all('e_R component=0' in p['one_owned_LL_Yukawa_block'] for p in r['points'])
    assert r['physical_photon_vertex'] is None and r['full_causal_effective_action'] is None
    assert not r['native_operator_updated']
