import numpy as np
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import _variables
from bhsm.interface.muon_birth_phase_continuation import solve_phase_midpoint,phase_continuation,discrete_action_cotangents,_compressed_npz


def action(eta):
    x,v,y=_variables(np.asarray(eta),0,3)
    L=(1+.2*x*x)*v*v/2-.3*x**4+y*v+.6*y*y
    return dict(value=L.value,gradient=L.gradient,hessian=L.hessian)


def test_phase_reversal_carries_the_actual_canonical_output():
    eta=np.array([.3,.1,-.1/1.2]);p=action(eta)['gradient'][1:2]
    f=solve_phase_midpoint(eta[:1],p,eta,.07,action,tolerance=1e-14)
    a=f['application'];guess=np.r_[a['x_new'],a['v_mid'],a['y_mid']]
    b=solve_phase_midpoint(a['x_new'],a['p_new'],guess,-.07,action,tolerance=1e-14)
    np.testing.assert_allclose(b['application']['x_new'],eta[:1],atol=3e-15,rtol=0)
    np.testing.assert_allclose(b['application']['p_new'],p,atol=3e-15,rtol=0)


def test_discrete_action_endpoint_contacts_match_independent_derivatives():
    x0=np.array([.3]);p0=np.array([.1]);eta=np.r_[x0,.2,-.04];h=.05
    r=solve_phase_midpoint(x0,p0,eta,h,action,tolerance=1e-14)
    a=r['application'];x1=a['x_new'];y=a['y_mid'];c=discrete_action_cotangents(a,h)
    def Ld(left,right):return h*action(np.r_[(left+right)/2,(right-left)/h,y])['value']
    eps=1e-6
    np.testing.assert_allclose(c['initial_face'],(Ld(x0+eps,x1)-Ld(x0-eps,x1))/(2*eps),rtol=2e-9,atol=1e-11)
    np.testing.assert_allclose(c['final_face'],(Ld(x0,x1+eps)-Ld(x0,x1-eps))/(2*eps),rtol=2e-9,atol=1e-11)
    np.testing.assert_allclose(c['initial_face'],-p0,atol=1e-14,rtol=0)
    np.testing.assert_allclose(c['final_face'],a['p_new'],atol=1e-14,rtol=0)


def test_chained_phase_refinement_is_second_order_without_resetting_p():
    eta=np.array([.3,.1,-.1/1.2]);p=action(eta)['gradient'][1:2]
    results=[phase_continuation(eta[:1],p,eta,.2,k,action,tolerance=1e-14) for k in (2,4,8)]
    phases=[np.r_[r['x_final'],r['p_final']] for r in results]
    coarse=np.linalg.norm(phases[0]-phases[1]);fine=np.linalg.norm(phases[1]-phases[2])
    assert 3.8<coarse/fine<4.2
    assert all(r['completed_steps']==k for r,k in zip(results,(2,4,8)))
    assert all(r['actual_canonical_momentum_carried'] for r in results)


def test_accepted_phase_checkpoint_resumes_without_recomputing_canonical_input(tmp_path):
    eta=np.array([.3,.1,-.1/1.2]);p=action(eta)['gradient'][1:2];saved=[]
    def checkpoint(i,z,a,scale,history,status):
        if status=='ACCEPTED_STEP':saved.append((i,z.copy(),scale.copy()))
    full=solve_phase_midpoint(eta[:1],p,eta,.07,action,tolerance=1e-14,checkpoint=checkpoint)
    i,z,scale=saved[0]
    resumed=solve_phase_midpoint(eta[:1],p,eta,.07,action,tolerance=1e-14,
        initial_unknowns=z,row_scale=scale,iteration_offset=i)
    np.testing.assert_array_equal(resumed['unknowns'],full['unknowns'])
    arrays=dict(unknowns=z,row_scale=scale,incoming_p=p)
    for name in ('first.npz','second.npz'):_compressed_npz(tmp_path/name,arrays)
    assert (tmp_path/'first.npz').read_bytes()==(tmp_path/'second.npz').read_bytes()
    with np.load(tmp_path/'first.npz',allow_pickle=False) as f:
        for name in arrays:np.testing.assert_array_equal(f[name],arrays[name])
