"""New cached tail checks; no prior production/replay or native heat solve."""
from pathlib import Path
import json
import numpy as np
import mpmath as mp
import pytest

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'artifacts/muon_retained_tail_core_20261005'


def read(p):
    with np.load(p,allow_pickle=False) as z:
        return {k:np.array(z[k]) for k in z.files}


@pytest.fixture(scope='module')
def saved():
    return dict(terminal=read(REF/'run_1/terminal_core_element.npz'),
        elements=read(REF/'run_1/tail_interior_elements.npz'),
        tail=read(REF/'run_1/tail_response.npz'),
        attached=read(REF/'run_1/partial_system_with_tail_core.npz'),
        coupled=read(REF/'coupled_run_3/source_centered_core_solution.npz'))


def test_terminal_moments_by_independent_gauss_integral(saved):
    t=saved['terminal'];j=float(t['clock_left'])
    x,w=np.polynomial.legendre.leggauss(4);x=(x+1)/2;w=w/2
    K=np.zeros_like(t['K']);M=np.zeros_like(t['M']);f=np.zeros_like(t['f'])
    source=saved['tail']['original_source_trace']
    for xx,ww in zip(x,w):
        A,B,C,MM=[(1-xx)*t['regular_'+k][0]+xx*t['regular_'+k][1] for k in ('A','B','C','M')]
        phi=(1-xx)**2;dp=-2*(1-xx);clock=j*(1-xx)
        # Integrate the defining weak form, independently of beta moments.
        K+=ww*(phi**2*A+phi*dp*(B+B.conj().T)+dp**2*C)/clock
        M+=ww*clock*phi**2*MM;f+=ww*clock*phi*(MM@source)
    for v,expected in ((K,t['K']),(M,t['M']),(f,t['f'])):
        assert np.linalg.norm(v-expected)/np.linalg.norm(expected)<3e-15


def test_actual_tail_states_use_their_own_clock_and_continued_branch():
    h=read(REF/'run_1/retained_tail_points.npz')
    meta=json.loads((REF/'run_1/retained_tail_points.json').read_text())
    for i,node in enumerate(h['node_indices'][1:-1],start=1):
        a=read(REF/'run_1/points'/f'node_{node:02d}.npz')
        state=h['states'][i];Nb=np.exp(state[74:86]@((-1.)**np.arange(1,13)))
        expected=h['action_rates'][i]/(h['state_weights']*h['proper_time_density'][i])
        np.testing.assert_array_equal(a['actual_state'],state)
        np.testing.assert_array_equal(a['Y_tau'],expected)
        assert np.linalg.norm(expected[:37]-state[37:74]/Nb)/np.linalg.norm(expected[:37])<1e-12
        assert meta['point_records'][i]['selected_branch']==24
    assert h['proper_time_density'][-1]==0 and h['signed_descriptors'][-1]==0
    t=read(REF/'run_1/terminal_core_element.npz')
    np.testing.assert_array_equal(t['Y_arc'],h['action_rates'][-1]/h['state_weights'])
    assert np.isfinite(t['K']).all() and np.linalg.norm(t['stop_Areg'])>0


def test_new_point_original_source_contraction_keeps_full_outputs(saved):
    cut=read(ROOT/'artifacts/muon_coupled_cut_forms_20261004/run_1/coupled_cut_source_actions.npz')
    source=saved['tail']['original_source_trace']
    for node in (3,25,46):
        a=read(REF/'run_1/points'/f'node_{node:02d}.npz')
        direct=sum(float((cut['radial_weights']*a['volume'])@
            np.sum(abs(a[f'Dp_n{n}'].reshape(len(a['volume']),-1))**2,axis=1)) for n in (1,3))
        contracted=float(np.vdot(source,a['A']@source).real)
        assert abs(direct-contracted)/direct<2e-14
        assert a['Dp_n3'].shape[1:]==(64,4,4)
        assert np.linalg.norm(a['M']-a['Ms'])>0


def test_complete_tail_banded_equations_and_affine_return(saved):
    a=saved['tail'];u=a['solution']
    action=np.einsum('nij,nj->ni',a['diagonal'],u)
    action[:-1]+=np.einsum('nij,nj->ni',a['upper'],u[1:])
    action[1:]+=np.einsum('nij,nj->ni',a['lower'],u[:-1])
    residual=action-a['rhs']
    assert np.linalg.norm(residual[1:])<3e-9
    np.testing.assert_allclose(u,a['homogeneous_solution']+a['source_particular'],rtol=1e-15,atol=1e-17)
    assert np.linalg.norm(a['rhs'][1:])>0 and np.linalg.norm(a['r'])>0
    np.testing.assert_allclose(residual[0],a['S']@u[0]-a['r'],rtol=2e-13,atol=4e-11)
    np.testing.assert_allclose(a['node2_Cauchy_pairing']@a['stationary_conormal_Riesz'],residual[0],rtol=4e-13,atol=2e-11)
    assert np.linalg.norm(a['sampled_trial_conormal_dual']-residual[0])>1


def test_tail_attachment_has_correct_signed_affine_load(saved):
    a=saved['attached'];t=saved['tail'];L=a['tail_trace_injection']
    p=read(ROOT/'artifacts/muon_prefix_time_element_20261004/assembly_run_1/partial_coupled_temporal_KM.npz')
    expected=p['K']+a['tail_shift']*p['M']+L.conj().T@t['S']@L
    np.testing.assert_array_equal(a['H'],expected)
    np.testing.assert_array_equal(a['rhs'],p['source_weak_rhs']+L.conj().T@t['r'])
    np.testing.assert_array_equal(a['trace_continuity'],p['trace_continuity'])
    np.testing.assert_array_equal(a['original_source_coefficients'],p['source_coefficients'])


def test_source_centered_solution_preserves_traces_and_stationary_return(saved):
    a=saved['attached'];s=saved['coupled'];C=s['joining'];L=s['incoming_trace_operator']
    assert np.linalg.norm(C@s['scaled_independent_chart'])<1e-15
    assert np.linalg.norm(L@s['scaled_independent_chart'])<1e-15
    assert np.linalg.norm(C@s['solution'])<1e-15
    np.testing.assert_allclose(L@s['solution'],s['incoming_source_trace'],rtol=1e-15,atol=1e-18)
    # Check the source-centered actual solution, not subtraction of separately
    # large source/port responses (the archived run2 failed that evaluation).
    np.testing.assert_array_equal(s['exact_original_source'],a['original_source_coefficients'])
    dual=s['port_injection'].conj().T@(a['H']@s['solution']-a['rhs'])
    np.testing.assert_allclose(dual,s['stationary_model_conormal_dual'],rtol=2e-13,atol=2e-11)
    taildual=saved['tail']['S']@s['solved_node2_trace']-saved['tail']['r']
    np.testing.assert_allclose(taildual,s['node2_stationary_tail_dual'],rtol=3e-13,atol=2e-11)


def test_decimal_solution_satisfies_saved_model_independently(saved):
    j=json.loads((REF/'coupled_run_3/high_precision_solution.json').read_text())
    with mp.workdps(80):
        u=mp.matrix([mp.mpc(*v) for v in j['solution']])
        a=saved['attached'];s=saved['coupled']
        H=mp.matrix([[mp.mpc(float(z.real),float(z.imag)) for z in row] for row in a['H']])
        f=mp.matrix([mp.mpc(float(z.real),float(z.imag)) for z in a['rhs']])
        residual=H*u-f
        # Test an independently reconstructed joining-tangent action. The
        # rounded chart is not used for 80-digit accuracy: recover its exact
        # rational scale from each saved element's binary64 input.
        old=ROOT/'artifacts/muon_prefix_time_element_20261004'
        sp,sb,sf=[mp.mpf(float(read(old/p)['temporal_basis_scale'])) for p in (
            'run_1/prefix_time_element.npz','assembly_run_1/cut_to_future1_element.npz',
            'future_run_2/retained_arc_time_element.npz')]
        d=24
        for i in range(d):
            assert abs(sp*residual[i]/2+residual[d+i]+sp*residual[2*d+i]/2-sp*residual[3*d+i]/sb)<mp.mpf('1e-60')
            assert abs(residual[2*d+i]/2+residual[3*d+i]/sb+residual[4*d+i]/2-residual[5*d+i]/sf)<mp.mpf('1e-60')
            assert abs(residual[4*d+i]/2+residual[5*d+i]/sf)<mp.mpf('1e-60')
        assert json.loads((REF/'coupled_run_3/result.json').read_text())['full_owned_source_solution'] is False
