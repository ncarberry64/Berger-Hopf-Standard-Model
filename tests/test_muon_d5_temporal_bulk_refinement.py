"""Refined time products, complete carrier blocks and saved-field corrections."""
import numpy as np
import pytest

from bhsm.interface.muon_d5_temporal_bulk_refinement import (
    time_evaluation_matrix,RefinedCanonicalHistory,carrier_components,
    component_offblock_max,_rectangular_collocation,_factor_solution,
    apply_refined_fundamental,_factor_at,_saved_factor_guess,
)
from bhsm.interface.muon_d5_complement_bulk_response import _collocation_rule
from bhsm.interface.muon_birth_trace_enriched_action import generic_coordinate_lift
from bhsm.interface.muon_parent_maxwell_full_weak import FIELD_ORDER


def test_time_evaluation_uses_independent_times_and_rejects_extrapolation():
    t=np.array([-1.,-.93,-.67,-.33,-.07,0.])*1e-5
    p=np.array([-.87,-.413,-.029])*1e-5
    V=time_evaluation_matrix(t,p);Dt=time_evaluation_matrix(t,p,1)
    for k in range(6):
        np.testing.assert_allclose(V@(t/1e-5)**k,(p/1e-5)**k,atol=2e-15)
        target=np.zeros(len(p)) if not k else k*(p/1e-5)**(k-1)/1e-5
        np.testing.assert_allclose(Dt@(t/1e-5)**k,target,atol=2e-9,rtol=2e-14)
    with pytest.raises(ValueError):time_evaluation_matrix(t,[1e-8])


def _canonical_fixture():
    labels=[dict(field=f) for _ in range(4) for f in FIELD_ORDER for _ in range(4)]
    coordinates=generic_coordinate_lift(labels);P=coordinates['lift'];n=coordinates['x_count']
    t=np.linspace(-1.,0.,6);eta=np.zeros((6,P.shape[1]));rates=eta.copy()
    eta[:,0]=t**3;eta[:,n]=3*t**2;rates[:,0]=3*t**2;rates[:,n]=6*t
    eta[:,2*n]=2+t;rates[:,2*n]=1
    return t,eta@P.T,rates@P.T,coordinates


def test_canonical_history_preserves_kinematics_and_names_legacy_source_separately():
    t,raw,rates,c=_canonical_fixture();history=RefinedCanonicalHistory(t,raw,rates,c)
    P=c['lift'];n=c['x_count']
    for q in [-.91,-.47,-.013]:
        a,at=history.value(q);a=a@P;at=at@P
        np.testing.assert_allclose(a[0],q**3,atol=1e-15)
        np.testing.assert_allclose(a[n],3*q*q,atol=1e-15)
        np.testing.assert_allclose(at[:n],a[n:2*n],atol=1e-15)
        np.testing.assert_allclose(at[n],6*q,atol=5e-14)
        xi,xit=history.source(q)
        np.testing.assert_allclose(xi@P,at,atol=5e-14)
    with pytest.raises(ValueError):history.value(.01)
    assert history.diagnostics()['legacy_source_kinematic_tangent_defect_max']<1e-13
    q=-.47;eps=1e-12
    np.testing.assert_allclose(history.source(q+1j*eps)[0].imag/eps,history.source(q)[1],atol=5e-13)


def test_exact_carrier_decomposition_keeps_even_tiny_source_couplings():
    a=np.zeros((2,3,64,64),complex)
    a[...,0,1]=1;a[...,2,3]=1
    b=a*0;b[...,1,2]=1e-300
    components=carrier_components(dict(value=a,source=b))
    assert any(np.array_equal(c,np.arange(4)) for c in components)
    assert len(np.concatenate(components))==64
    assert component_offblock_max(dict(value=a,source=b),components)==0
    b[...,0,4]=1e-200
    assert component_offblock_max(dict(value=a,source=b),components)>0


def test_nonzero_initializer_is_corrected_by_original_stages_with_all_columns():
    _,_,_,A=_collocation_rule(3)
    rng=np.random.default_rng(2038);gs=rng.normal(size=(3,4,4))*.1
    gxs=rng.normal(size=gs.shape)*.02;initial=rng.normal(size=(4,7));initialx=initial*.07
    guess=rng.normal(size=(3,4,7));guessx=rng.normal(size=guess.shape)
    direct=_rectangular_collocation(gs,gxs,initial,initialx,-.03,A)
    corrected=_rectangular_collocation(gs,gxs,initial,initialx,-.03,A,guess,guessx)
    np.testing.assert_allclose(corrected[0],direct[0],atol=3e-16)
    np.testing.assert_allclose(corrected[1],direct[1],atol=1e-16)
    assert corrected[2]<3e-15 and corrected[3]<2e-15
    assert corrected[4]['correction_norm']>1
    assert corrected[4]['initializer_residual']>1


def test_full_carrier_application_retains_every_family_and_homogeneous_column():
    # Identity transfer still acts on all384 components and arbitrary columns.
    n=3;d=64;order=3;times=np.array([-1.,-.4,0.]);bounds=np.array([1.,.99])
    arrays=dict(times=times,radial_nodes=bounds,radial_boundaries=bounds,radial_order=np.array(order))
    for branch in ('particle','conjugate'):
        prefix='plus_'+branch+'_';arrays[prefix+'block_count']=np.array(1)
        prefix+='block0_';arrays[prefix+'indices']=np.arange(d)
        arrays[prefix+'initial']=np.eye(n*d)[None].astype(complex)
        arrays[prefix+'initial_source']=np.zeros((1,n*d,n*d),complex)
        arrays[prefix+'slopes']=np.zeros((1,order,n*d,n*d),complex)
        arrays[prefix+'slopes_source']=np.zeros((1,order,n*d,n*d),complex)
    rng=np.random.default_rng(78);wall=rng.normal(size=(n,384,5))+1j*rng.normal(size=(n,384,5))
    source=wall*.13;points=np.array([-.83,-.16]);radii=np.array([.998,.993])
    result=apply_refined_fundamental(arrays,'plus',wall,source,times=points,radii=radii)
    expected=np.einsum('ij,jdk->idk',time_evaluation_matrix(times,points),wall)
    np.testing.assert_allclose(result['value'],np.broadcast_to(expected,result['value'].shape),atol=2e-15)
    np.testing.assert_allclose(result['source'],result['value']*.13,atol=5e-16)
    assert np.count_nonzero(np.sum(abs(result['value'])**2,axis=(0,1,3)))==384
    assert np.max(abs(result['time']))>0


def test_old_transfer_is_actual_refined_stage_initializer_with_higher_modes_retained():
    oldt=np.linspace(-1.,0.,6);newt=np.linspace(-1.,0.,9)
    cn,_,_,_=_collocation_rule(3);r=np.r_[1.,1-.01*cn,.99]
    nr=len(r);size=6*64;indices=np.array([1,3]);ii=(64*np.arange(6)[:,None]+indices).ravel()
    H=np.broadcast_to(np.eye(size),(nr,size,size)).copy();Hx=np.zeros_like(H)
    K=np.eye(12)*.2
    for j,radial in enumerate(r):
        H[j][np.ix_(ii,ii)]+=(radial-1)*K
        Hx[j][np.ix_(ii,ii)]=(radial-1)*K*.03
    saved=dict(times=oldt,radial_nodes=r,radial_node_is_collocation=np.array([False,True,True,True,False]),
        radial_node_step=np.zeros(nr),plus_particle_fundamental=H,plus_particle_fundamental_source=Hx)
    rp=np.array([.9987,.9923]);guess,gx=_saved_factor_guess(saved,'plus_particle',indices,newt,rp)
    E=np.kron(time_evaluation_matrix(oldt,newt),np.eye(2));R=np.kron(time_evaluation_matrix(newt,oldt),np.eye(2))
    np.testing.assert_allclose(guess[0],np.eye(18)+(rp[0]-1)*E@K@R,atol=3e-15)
    np.testing.assert_allclose(gx[1],(rp[1]-1)*E@K@R*.03,atol=1e-17)
    null=np.linalg.svd(R)[2][12:].T
    np.testing.assert_allclose(guess[0]@null,null,atol=1e-15)
    assert np.linalg.norm(guess-np.eye(18))>0


def test_supplied_original_history_protocol_does_not_require_diagnostics(monkeypatch):
    # The recovered source callback protocol predates this representation.
    # Exercise the completed solver report with cheap identity propagation.
    import bhsm.interface.muon_d5_temporal_bulk_refinement as module
    t,raw,rates,coordinates=_canonical_fixture()
    canonical=RefinedCanonicalHistory(t,raw,rates,coordinates)
    class OriginalCallback:
        value=canonical.value
        source=canonical.source
    history=OriginalCallback();history.times=t
    def coefficients(history,times,radii):
        shape=(len(radii),len(times),64,64);zero=np.zeros(shape,complex)
        c={k:zero.copy() for k in ('time','radial','body','time_source','radial_source','body_source')}
        c['radial'][...]=np.eye(64)
        return {label:c for label in ('plus_particle','plus_conjugate','minus_particle','minus_conjugate')},np.ones(shape[:2]),np.zeros(shape[:2])
    def factor(c,D,components,bounds,order,**kwargs):
        result={}
        for i,index in enumerate(components):
            prefix='block'+str(i)+'_';size=len(D)*len(index)
            result[prefix+'indices']=index
            result[prefix+'initial']=np.eye(size,dtype=complex)[None]
            result[prefix+'initial_source']=np.zeros((1,size,size),complex)
            result[prefix+'slopes']=np.zeros((1,order,size,size),complex)
            result[prefix+'slopes_source']=np.zeros((1,order,size,size),complex)
        return result,{}
    def walls(endpoints,full):
        n=len(endpoints);result={}
        for label in ('plus_seed','minus_seed','minus_LR','minus_RL'):
            result[label]=np.zeros((n,384,18*n),complex)
            result[label+'_source']=np.zeros_like(result[label])
        return result
    monkeypatch.setattr(module,'coefficient_rows',coefficients)
    monkeypatch.setattr(module,'_factor_solution',factor)
    monkeypatch.setattr(module,'_fresh_endpoint',lambda *a:None)
    monkeypatch.setattr(module,'_endpoint_from_cache',lambda *a:None)
    monkeypatch.setattr(module,'_wall_maps',walls)
    arrays,report,returned=module.solve_refined_incoming_bulk_family(t,raw,rates,
        saved_endpoint={},saved_application={'computational_strip_width':.001},history=history,
        temporal_count=6,radial_steps=1,radial_order=2)
    assert returned is history
    assert report['history']['callback_type']=='OriginalCallback'
    assert report['homogeneous_wall_unknown_shape']==[6,366]
    assert report['physical_admission'] is False
