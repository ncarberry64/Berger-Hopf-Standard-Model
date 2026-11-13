"""Independent spin amplitudes, gamma traces and finite-mass phase space."""
import numpy as np
import pytest

from bhsm.interface.muon_daughter_spin_channel import (
    PAULI, charged_spinor, neutrino_pair_moment, local_joint_spin_kernel,
    local_joint_spin_kernel_first, parent_analyzer, va_tensor,
    va_parent_analyzer, literal_gamma_analyzer, literal_invariant_analyzer,
    pair_momenta, sphere_rule, local_decay_spectrum, va_phase_factor,
    positive_muon_local_joint_spin_kernel, local_joint_spin_kernel_kinematic_first,
    normalized_electron_state,
)


@pytest.mark.parametrize('m,E',[(0.,.37),(.13,.33),(.4,.49)])
def test_literal_gamma_traces_match_invariant_and_exact_pair_moment(m,E):
    M=1.;n=np.array([.36,.48,.8]);u=np.array([.8,0.,.6])
    pn,pa=pair_momenta(M=M,m=m,E=E,n=n,u=u)
    p=np.array([M,0,0,0]);k=np.r_[E,np.sqrt(E*E-m*m)*n]
    literal=literal_gamma_analyzer(p,k,pn,pa,M=M,m=m)
    np.testing.assert_allclose(literal,literal_invariant_analyzer(p,k,pn,pa,M=M),atol=2e-13,rtol=0)
    dirs,w=sphere_rule(4);averaged=np.zeros((2,2),complex)
    for d,weight in zip(dirs,w):
        pn,pa=pair_momenta(M=M,m=m,E=E,n=n,u=d)
        averaged+=weight*literal_gamma_analyzer(p,k,pn,pa,M=M,m=m)
    actual=parent_analyzer(local_joint_spin_kernel(va_tensor(),M=M,m=m,E=E,direction=n))
    np.testing.assert_allclose(actual,averaged,atol=2e-13,rtol=0)
    np.testing.assert_allclose(actual,va_parent_analyzer(M=M,m=m,E=E,direction=n),atol=2e-13,rtol=0)


def test_arbitrary_complex_tensor_joint_spin_map_against_explicit_amplitudes():
    rng=np.random.default_rng(45);C=(rng.normal(size=(2,4,4,2))+1j*rng.normal(size=(2,4,4,2)))/8
    M,m,E=1.,.17,.39;n=np.array([0.,.6,.8]);p=np.sqrt(E*E-m*m)
    U,V=charged_spinor(M,np.zeros(3)),charged_spinor(m,p*n)
    literal=np.zeros((2,2,2,2),complex);dirs,w=sphere_rule(4)
    for d,weight in zip(dirs,w):
        pn,pa=pair_momenta(M=M,m=m,E=E,n=n,u=d)
        # Independent final spin columns via Hermitian spectral square roots.
        factors=[]
        for momentum in (pn,pa):
            rho=momentum[0]*np.eye(2)-np.einsum('i,ijk->jk',momentum[1:],PAULI)
            ev,vec=np.linalg.eigh(rho)
            assert ev.min()>-2e-15
            factors.append(vec@np.diag(np.sqrt(np.maximum(ev,0))))
        a=np.einsum('abcd,ai,bs,cr,dj->rsij',C,factors[0].conj(),U,V.conj(),factors[1])
        literal+=weight*np.einsum('rsij,ltij->rlst',a,a.conj())
    exact=local_joint_spin_kernel(C,M=M,m=m,E=E,direction=n)
    np.testing.assert_allclose(exact,literal,atol=2e-13,rtol=0)
    choi=exact.transpose(0,2,1,3).reshape(4,4)
    assert np.linalg.eigvalsh(choi).min()>-2e-14
    assert np.max(abs(exact[0,1]))>1e-5  # daughter coherence was not discarded


def test_every_real_tensor_axis_derivative_preserves_complete_joint_spin_map():
    rng=np.random.default_rng(83);C=(rng.normal(size=(2,4,4,2))+1j*rng.normal(size=(2,4,4,2)))/8
    kwargs=dict(M=1.,m=.09,E=.31,direction=np.array([.6,0.,.8]))
    # Quadratic polarization identity is independent of the implemented jet,
    # with no tiny-step cancellation and all 128 real coefficient axes.
    for factor in (1.,1j):
        for i in range(C.size):
            d=np.zeros_like(C);d.flat[i]=factor
            literal=(local_joint_spin_kernel(C+d,**kwargs)-local_joint_spin_kernel(C-d,**kwargs))/2
            np.testing.assert_allclose(local_joint_spin_kernel_first(C,d,**kwargs),literal,atol=2e-10,rtol=0)


@pytest.mark.parametrize('m',[0.,.07,.3])
def test_massive_total_rate_and_massless_energy_spin_distributions(m):
    a=local_decay_spectrum(va_tensor(),M=1.,m=m,energy_order=48)
    expected=va_phase_factor(m*m)/(1536*np.pi**3)
    np.testing.assert_allclose(a['integrated_parent_analyzer'],expected*np.eye(2),atol=2e-13,rtol=0)
    assert a['full_spin_map_hermiticity_defect']<2e-15
    if m==0:
        assert abs(a['mean_scaled_electron_energy']-.7)<2e-13
        assert abs(a['unpolarized_mean_electron_helicity']+1)<2e-13
        assert abs(a['parent_up_mean_direction_cosine']+1/9)<2e-13
        E=.41;x=2*E
        D=parent_analyzer(local_joint_spin_kernel(va_tensor(),M=1.,m=0.,E=E,direction=np.array([0.,0.,1.])))
        # dGamma/dx/dcos divided by Gamma0; the mu-minus sign is tested.
        observed=E/(64*np.pi**3)*D[0,0].real/4/expected
        assert abs(observed-x*x*((3-2*x)+(1-2*x)))<2e-13


def test_static_pair_moment_does_not_accept_spacelike_q():
    with pytest.raises(ValueError):neutrino_pair_moment([1,2,0,0])
    with pytest.raises(ValueError):neutrino_pair_moment([1,0,0,1j])
    with pytest.raises(ValueError):
        local_joint_spin_kernel(va_tensor(),M=1.,m=0.,E=.3,direction=np.array([0.,0.,1.+1e-4j]))


def test_antimuon_physical_spin_labels_reverse_the_VA_parity_analyzer():
    n=np.array([.6,0.,.8]);kw=dict(M=1.,m=.1,E=.41,direction=n)
    positive=parent_analyzer(positive_muon_local_joint_spin_kernel(va_tensor(),**kw))
    np.testing.assert_allclose(positive,va_parent_analyzer(**kw,charge=1),atol=2e-13,rtol=0)
    negative=parent_analyzer(local_joint_spin_kernel(va_tensor(),**kw))
    assert np.sign((positive[0,0]-positive[1,1]).real)==-np.sign((negative[0,0]-negative[1,1]).real)


def test_joint_kinematic_and_conditional_spin_derivatives_keep_normalization_contacts():
    C=va_tensor(.7+.2j);dC=va_tensor(.03-.04j);n=np.array([.6,0.,.8]);dn=np.array([.08,.03,-.06])
    kw=dict(M=1.,m=.12,E=.35,direction=n)
    dK,phase=local_joint_spin_kernel_kinematic_first(C,dC,**kw,M_first=.04,m_first=-.02,E_first=.03,direction_first=dn)
    def moved(t):
        direction=n+t*dn;direction/=np.linalg.norm(direction)
        return local_joint_spin_kernel(C+t*dC,M=1+.04*t,m=.12-.02*t,E=.35+.03*t,direction=direction)
    h=.001;literal=(-moved(2*h)+8*moved(h)-8*moved(-h)+moved(-2*h))/(12*h)
    np.testing.assert_allclose(dK,literal,atol=2e-10,rtol=0)
    K=local_joint_spin_kernel(C,**kw);rho=np.array([[.6,.12j],[-.12j,.4]]);drho=np.array([[.02,.01],[.01,-.02]])
    state,weight,dstate,dweight=normalized_electron_state(K,rho,kernel_first=dK,parent_first=drho)
    def conditional(t):return normalized_electron_state(moved(t),rho+t*drho)[0]
    literal=(-conditional(2*h)+8*conditional(h)-8*conditional(-h)+conditional(-2*h))/(12*h)
    np.testing.assert_allclose(dstate,literal,atol=2e-10,rtol=0)
    assert abs(np.trace(dstate))<2e-14
    assert abs(np.trace(state)-1)<2e-14 and weight.real>0
