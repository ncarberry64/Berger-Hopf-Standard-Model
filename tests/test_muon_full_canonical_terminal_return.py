"""Independent signed canonical ODE and moving-domain return controls."""
import numpy as np
from numpy.testing import assert_allclose
from scipy.linalg import expm
from scipy.integrate import solve_ivp

from bhsm.interface.muon_full_canonical_terminal_return import (
    full_canonical_jacobi_generator, canonical_terminal_return_two_jet,
    literal_terminal_current_two_jet, full_canonical_jacobi_generator_first)
from bhsm.interface.muon_full_canonical_terminal_return import full_canonical_midpoint_transfer


def _zeros(packet):
    return {k:np.zeros_like(v) for k,v in packet.items()}


def test_full_lyy_signed_ode_mobius_and_literal_dual():
    rng=np.random.default_rng(147)
    n=2;d=5
    raw=rng.normal(size=(d,d))+.25j*rng.normal(size=(d,d))
    H=.12*(raw+raw.T);H[n:,n:]+=np.diag([1.3,1.1,.8])
    g=.1*(rng.normal(size=d)+1j*rng.normal(size=d))
    a=full_canonical_jacobi_generator(H,n,np.zeros((0,3)),g,np.zeros(0))
    # Independently integrate the original constitutive equations; the
    # algebraic block is active and never omitted from the ODE.
    z0=rng.normal(size=4)+.2j*rng.normal(size=4);T=.18
    def original(t,z):
        phase=np.linalg.solve(H[n:,n:],np.r_[z[n:],0]-H[n:,:n]@z[:n]-g[n:])
        return np.r_[phase[:n],H[:n]@np.r_[z[:n],phase]+g[:n]]
    sol=solve_ivp(original,(0,T),z0,rtol=2e-12,atol=2e-13)
    aug=np.zeros((5,5),complex);aug[:4,:4]=a['generator'];aug[:4,-1]=a['forcing']
    E=expm(T*aug);M=E[:4,:4];f=E[:4,-1]
    assert_allclose(sol.y[:,-1],M@z0+f,rtol=4e-11,atol=4e-12)
    assert_allclose(a['original_phase_rows'],0,atol=2e-15)
    Y=np.array([[.3+.07j,.05-.12j],[.09+.03j,-.14+.02j]])
    s=np.array([.04+.02j,-.03+.01j]);packet=dict(transfer=M,forcing=f,terminal_matrix=Y,terminal_source=s)
    zero=_zeros(packet);r=canonical_terminal_return_two_jet(packet,zero,zero,zero)
    # Independent backward Riccati/affine-tail integration.
    J=a['generator'];force=a['forcing']
    def riccati(t,z):
        Q=z[:4].reshape(2,2);b=z[4:]
        return np.r_[(J[2:,:2]+J[2:,2:]@Q-Q@J[:2,:2]-Q@J[:2,2:]@Q).ravel(),
            (J[2:,2:]-Q@J[:2,2:])@b+force[2:]-Q@force[:2]]
    tail=solve_ivp(riccati,(T,0),np.r_[Y.ravel(),s],rtol=2e-12,atol=2e-13)
    assert_allclose(r['value']['birth_momentum_matrix'],tail.y[:4,-1].reshape(2,2),rtol=4e-11,atol=4e-12)
    assert_allclose(r['value']['birth_momentum_source'],tail.y[4:,-1],rtol=4e-11,atol=4e-12)
    Li=rng.normal(size=(3,4))+1j*rng.normal(size=(3,4));Lf=rng.normal(size=(3,4))+1j*rng.normal(size=(3,4))
    target=dict(left_initial=Li,left_final=Lf,direct=np.array([.2,.1j,-.3j]));zt=_zeros(target)
    current=literal_terminal_current_two_jet(packet,zero,zero,zero,target,zt,zt,zt)
    x=np.array([.17+.04j,-.21+.03j]);p=r['value']['birth_momentum_matrix']@x+r['value']['birth_momentum_source']
    zi=np.r_[x,p];zf=M@zi+f
    literal=Li@zi+Lf@zf+target['direct']
    assert_allclose(current['value']['birth_coordinate_target']@x+current['value']['direct_source_current'],literal,atol=2e-15)
    assert_allclose(current['literal_transpose_pairing_rows'],0,atol=2e-15)
    assert_allclose(r['value']['child_initial_outward_conormal_matrix'],-r['value']['birth_momentum_matrix'],atol=0)
    dagger=np.linalg.solve(r['original_graph_operator'][0].conj().T,(Li+Lf@M)[:,2:].T)
    assert np.linalg.norm(dagger-current['literal_transpose_solution'][0])>.01


def test_both_return_contacts_moving_terminal_and_source_mixed_fd():
    rng=np.random.default_rng(214);n=2
    def random(shape,scale=.14):return scale*(rng.normal(size=shape)+.4j*rng.normal(size=shape))
    K0=random((4,4));Ka=random((4,4));Kb=random((4,4));Kab=random((4,4))
    f0=random((4,));fa=random((4,));fb=random((4,));fab=random((4,))
    Y0=random((2,2));Ya=random((2,2));Yb=random((2,2));Yab=random((2,2))
    s0=random((2,));sa=random((2,));sb=random((2,));sab=random((2,))
    li=[random((3,4))for _ in range(4)];lf=[random((3,4))for _ in range(4)];cc=[random((3,))for _ in range(4)]
    def whole(x,y):
        # Independently differentiate the complete exponential flow and
        # terminal shooting solve; no producer inverse-jet formula used.
        J=K0+x*Ka+y*Kb+x*y*Kab;force=f0+x*fa+y*fb+x*y*fab
        aug=np.zeros((5,5),complex);aug[:4,:4]=J;aug[:4,-1]=force
        e=expm(.2*aug);M=e[:4,:4];f=e[:4,-1]
        Y=Y0+x*Ya+y*Yb+x*y*Yab;s=s0+x*sa+y*sb+x*y*sab
        left_i=li[0]+x*li[1]+y*li[2]+x*y*li[3]
        left_f=lf[0]+x*lf[1]+y*lf[2]+x*y*lf[3]
        direct=cc[0]+x*cc[1]+y*cc[2]+x*y*cc[3]
        Q=np.linalg.solve(M[2:,2:]-Y@M[:2,2:],np.c_[Y@M[:2,:2]-M[2:,:2],s+Y@f[:2]-f[2:]])
        L=left_i+left_f@M
        out=np.c_[L[:,:2]+L[:,2:]@Q[:,:2],direct+left_f@f+L[:,2:]@Q[:,2]]
        return dict(transfer=M,forcing=f,terminal_matrix=Y,terminal_source=s),out,Q
    b,expected,_=whole(0,0);h=1e-4
    def diff_packets(pa,pb,den):return {k:(pa[k]-pb[k])/den for k in pa}
    pa=diff_packets(whole(h,0)[0],whole(-h,0)[0],2*h)
    pb=diff_packets(whole(0,h)[0],whole(0,-h)[0],2*h)
    pp=whole(h,h);pm=whole(h,-h);mp=whole(-h,h);mm=whole(-h,-h)
    pab={k:(pp[0][k]-pm[0][k]-mp[0][k]+mm[0][k])/(4*h*h)for k in b}
    ts=[dict(left_initial=li[k],left_final=lf[k],direct=cc[k])for k in range(4)]
    actual=literal_terminal_current_two_jet(b,pa,pb,pab,*ts)
    actual0=np.c_[actual['value']['birth_coordinate_target'],actual['value']['direct_source_current']]
    actualab=np.c_[actual['mixed']['birth_coordinate_target'],actual['mixed']['direct_source_current']]
    expectedab=(pp[1]-pm[1]-mp[1]+mm[1])/(4*h*h)
    assert_allclose(actual0,expected,atol=2e-15)
    assert_allclose(actualab,expectedab,rtol=3e-6,atol=1e-8)
    assert_allclose(actual['return_application']['original_graph_rows'],0,atol=2e-15)
    assert_allclose(actual['literal_transpose_pairing_rows'],0,atol=2e-15)
    missing=dict(b);missing.pop('terminal_matrix')
    import pytest
    with pytest.raises(ValueError,match='explicit transfer'):
        canonical_terminal_return_two_jet(missing,pa,pb,pab)


def test_moving_named_frame_and_original_phase_first_no_dagger():
    rng=np.random.default_rng(423);n=2;d=5
    Q=rng.normal(size=(d,d))+.3j*rng.normal(size=(d,d))
    H=.1*(Q+Q.T);H[n:,n:]+=np.diag([1.7,1.3,1.1])
    R=rng.normal(size=(d,d))+.2j*rng.normal(size=(d,d));dH=.2*(R+R.T)
    F=np.array([[.1+.04j,0,1-.02j]],complex)
    dF=np.array([[.04j,-.03+.02j,.05j]],complex)
    g=.1*(rng.normal(size=d)+.2j*rng.normal(size=d));dg=.2*(rng.normal(size=d)+.3j*rng.normal(size=d))
    fs=np.array([.05+.02j]);dfs=np.array([-.02+.04j])
    a=full_canonical_jacobi_generator_first(H,dH,n,F,dF,g,dg,fs,dfs)
    h=1e-5
    p=full_canonical_jacobi_generator(H+h*dH,n,F+h*dF,g+h*dg,fs+h*dfs)
    m=full_canonical_jacobi_generator(H-h*dH,n,F-h*dF,g-h*dg,fs-h*dfs)
    for key in ('generator','forcing','compatibility_map','compatibility_source'):
        assert_allclose(a[key+'_first'],(p[key]-m[key])/(2*h),rtol=2e-8,atol=1e-10)
    assert_allclose(a['original_phase_first_rows'],0,atol=5e-16)
    assert np.linalg.norm(a['compatibility_map_first'])>.01
    c=full_canonical_midpoint_transfer(H,n,F,g,fs,.015+.002j)
    assert_allclose(c['original358_rows_with_named_reactions'],0,atol=3e-15)
    assert_allclose(c['named_frame_rows'],0,atol=3e-15)
    # Independent full original canonical midpoint bordered equations.
    from bhsm.interface.muon_per_arm_canonical_source import arm_variational_midpoint_map
    x=np.array([.1+.03j,-.04+.02j]);p=np.array([-.2+.01j,.15-.02j])
    old=arm_variational_midpoint_map(H,.015+.002j,x,p,g,F,phase_frame_value=fs)
    assert_allclose(c['transfer']@np.r_[x,p]+c['forcing'],np.r_[old['x_final'],old['Pi_final']],rtol=2e-14,atol=2e-15)
