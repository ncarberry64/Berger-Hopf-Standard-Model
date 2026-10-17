import numpy as np
from bhsm.interface.muon_holomorphic_magnetic_inherited_cauchy import inherited_prescribed_magnetic_prefix,actual_owner_piecewise_source_germ
from bhsm.interface.muon_holomorphic_n1_magnetic_action import original_field_permutation
from bhsm.interface.muon_holomorphic_magnetic_inherited_cauchy import signed_field_face_source_first
from bhsm.interface.muon_holomorphic_magnetic_birth_matching import signed_field_face_reconstruction


def test_inherited_source_on_action_matches_independent_canonical_flow_not_zero_restart():
    names=('A_tau','A_rho','A_1','A_2','A_3')
    labels=[dict(field=names[f],internal=c,wall_lift=r==3)for r in range(4)for f in range(5)for c in range(4)]
    W=np.zeros((20,80));W[:,60:]=np.eye(20)
    rep=dict(gauge_labels=labels,wall_trace_map=W.reshape(5,4,80),radial_quadrature=np.ones(1),
        gauge_basis=np.zeros((1,80,1,5,4)),gauge_radial_basis=np.zeros((1,80,1,5,4)))
    ids=original_field_permutation(rep);n=336
    M=np.eye(n,dtype=complex);M[:64]=0;M[:,:64]=0
    forms=dict(K=np.eye(n,dtype=complex),M=M,B_forward=np.zeros((n,n),complex),B_reverse=np.zeros((n,n),complex))
    rng=np.random.default_rng(912);initial=.01*(rng.normal(size=(1,392,3))+1j*rng.normal(size=(1,392,3)))
    Q=np.zeros((5,4,4,3),complex);Q[2:]=.02*rng.normal(size=(3,4,4,3))
    s=dict(Q=Q,Q_coordinate_time=np.zeros_like(Q));sources=[s]*5;h=np.array([.002,.002]);knots=np.array([0,.25,.5,.75,1])
    germ=lambda t:actual_owner_piecewise_source_germ(t,knots,sources,sum(h))
    a=inherited_prescribed_magnetic_prefix([forms,forms],h,sources,rep,ids,initial,germ)
    x,p=initial[0,:196],initial[0,196:];T=sum(h)
    exact=np.r_[np.cosh(T)*x+np.sinh(T)*p,np.sinh(T)*x+np.cosh(T)*p]
    np.testing.assert_allclose(a['final_reduced_canonical_state'],exact,rtol=4e-13,atol=4e-15)
    np.testing.assert_array_equal(a['initial_reduced_canonical_state'],initial[0])
    for point in a['point_sources']:
        np.testing.assert_allclose(point['complete_wall_source'],Q,atol=2e-17)
        np.testing.assert_allclose(point['original_full_wall_rows'],0,atol=2e-17)
        np.testing.assert_allclose(point['original_reconstructed_rows'],0,atol=7e-16)
    assert not a['source_restarted_at_zero']


def test_owned_piecewise_Hermite_consumes_exact_birth_and_rates_without_a_shift():
    rng=np.random.default_rng(471);knots=np.array([0,.25,.5,.75,1]);T=.03
    sources=[dict(Q=rng.normal(size=(2,3))+1j*rng.normal(size=(2,3)),
        Q_coordinate_time=rng.normal(size=(2,3))+1j*rng.normal(size=(2,3)))for _ in knots]
    for t,s in zip(knots,sources):
        value,rate,_=actual_owner_piecewise_source_germ(t,knots,sources,T)
        np.testing.assert_allclose(value,s['Q'],atol=4e-16)
        np.testing.assert_allclose(rate,s['Q_coordinate_time'],atol=4e-14)
    t=.41;h=1e-6
    q,qt,qtt=actual_owner_piecewise_source_germ(t,knots,sources,T)
    plus=actual_owner_piecewise_source_germ(t+h,knots,sources,T);minus=actual_owner_piecewise_source_germ(t-h,knots,sources,T)
    np.testing.assert_allclose(qt,(plus[0]-minus[0])/(2*h*T),rtol=2e-9,atol=3e-8)
    np.testing.assert_allclose(qtt,(plus[1]-minus[1])/(2*h*T),rtol=2e-9,atol=2e-5)


def test_source_first_initial_reconstitution_preserves_literal_targets_and_crosses():
    rng=np.random.default_rng(997);draw=lambda s:rng.normal(size=s)+.2j*rng.normal(size=s)
    n,na=6,2;nd=n-na;forms={q:draw((n,n))for q in('K','M','B_forward','B_reverse')}
    forms['K'][:na,:na]+=4*np.eye(na);forms['M'][na:,na:]+=5*np.eye(nd)
    df={q:draw((1,n,n))for q in forms}
    for a in(forms['M'],df['M'][0]):a[:na]=0;a[:,:na]=0
    for a in(forms['B_forward'],df['B_forward'][0]):a[:,:na]=0
    for a in(forms['B_reverse'],df['B_reverse'][0]):a[:na]=0
    S=np.eye(n);L=draw((n,2));wall=[draw((2,3))for _ in range(2)];dw=[draw((1,2,3))for _ in range(2)]
    z=draw((2*nd,3));dz=draw((1,2*nd,3));base=signed_field_face_reconstruction(forms,S,L,wall,z,na)
    a=signed_field_face_source_first(forms,df,S,L,dw,dz,base,na);h=1e-5;values=[]
    for t in(h,-h):
        values.append(signed_field_face_reconstruction({q:v+t*df[q][0]for q,v in forms.items()},S,L,
            [v+t*d[0]for v,d in zip(wall,dw)],z+t*dz[0],na))
    for key in('total_field','canonical_momentum'):
        fd=(values[0][key]-values[1][key])/(2*h)
        np.testing.assert_allclose(a[key+'_first'][0],fd,rtol=3e-9,atol=3e-8)
    np.testing.assert_allclose(a['original_source_first_Gauss_and_momentum_rows'],0,atol=2e-14)
