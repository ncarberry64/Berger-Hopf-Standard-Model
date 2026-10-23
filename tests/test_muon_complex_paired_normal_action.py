import numpy as np
from bhsm.interface.muon_complex_paired_normal_action import (
    analytic_frequency_polynomial,analytic_normal_frequency_jet,
    frequency_parameter_jet,analytic_frequency_sector_pairings,
    full_joint_canonical_tangent,chronological_jacobi_coefficient_contact)


def test_complex_normal_parameter_and_independent_sector_dual():
    rng=np.random.default_rng(172);n=3;m=2;A=rng.normal(size=(8,8))+1j*rng.normal(size=(8,8))*.2
    H=A.T@A+np.diag([2,3,4,5,6,7,8,9]);dH=rng.normal(size=(8,8))+1j*rng.normal(size=(8,8))*.1;dH=(dH+dH.T)/2
    normal=np.array([1,.2+.1j,-.3+.1j]);C=np.array([[0,1,0,0,0]],complex);lapse=.8+.13j
    app=analytic_normal_frequency_jet(H,normal,C,lapse=lapse);gamma=frequency_parameter_jet(app,dH)
    h=1e-5
    plus=analytic_normal_frequency_jet(H+h*dH,normal,C,lapse=lapse)
    minus=analytic_normal_frequency_jet(H-h*dH,normal,C,lapse=lapse)
    assert np.max(abs((plus['response_taylor']-minus['response_taylor'])/(2*h)-gamma['response_taylor_parameter']))<2e-8
    assert np.max(abs(app['right_original_rows']))<3e-14
    assert np.max(abs(app['left_original_rows']))<3e-14
    assert np.max(abs(gamma['parameter_original_rows']))<3e-14
    sectors=analytic_frequency_sector_pairings(app,{'first':.7*H+.3*dH,'second':.3*H-.3*dH})
    assert np.max(abs(sectors['total_minus_reduced_response']))<3e-14
    # This truly nonreal action must not be silently paired with a dagger.
    z=app['right_taylor'][:5,0]
    assert abs(np.vdot(z,app['action_polynomial'][0]@z)-app['response_taylor'][0])>1e-3
    omega=2e-4;p=app['bordered_polynomial'];rhs=app['bordered_rhs']
    direct=-np.linalg.solve(p[0]+omega*p[1]+omega**2*p[2],rhs)[5]
    fitted=app['response_taylor']@np.array([1,omega,omega**2])
    assert abs(direct-fitted)<1e-10


def test_time_dependent_jacobi_retains_every_euler_coefficient_contact():
    rng=np.random.default_rng(92);n=2;m=1
    X=rng.normal(size=(5,5))+1j*rng.normal(size=(5,5))*.3;H=(X+X.T)/2
    X=rng.normal(size=(5,5))+1j*rng.normal(size=(5,5))*.2;Ht=(X+X.T)/2
    x=rng.normal(size=n)+.2j;v=rng.normal(size=n)-.1j;acc=rng.normal(size=n)+.1j;y=np.array([.4+.2j]);yd=np.array([-.3+.1j])
    # Literal Lx-d_t Lv, with independent complex coefficients.
    eta=np.r_[x,v,y];etad=np.r_[v,acc,yd];g=H@eta
    expected=g[:n]-(Ht@eta+H@etad)[n:2*n]
    contact=chronological_jacobi_coefficient_contact(Ht,n)
    p=analytic_frequency_polynomial(H,n)
    evaluated=(p[0]+contact[0])@np.r_[x,y]
    evaluated[:n]+=(p[1][:n,:n]+contact[1][:n,:n])@v/1j-p[2][:n,:n]@acc-H[n:2*n,2*n:]@yd
    assert np.max(abs(evaluated[:n]-expected))<2e-15
    assert np.linalg.norm(contact[0][:n,n:])>1e-2
    assert np.linalg.norm(contact[1][:n,:n])>1e-2
    def gv(t):return ((H+t*Ht)@(eta+t*etad+np.r_[.5*t*t*acc,np.zeros(n+m)]))[n:2*n]
    h=1e-5;independent=g[:n]-(gv(h)-gv(-h))/(2*h)
    assert np.max(abs(independent-expected))<3e-10


def test_original_joint_canonical_tangent_uses_both_clock_and_frame_rows():
    rng=np.random.default_rng(919);H=np.diag(np.linspace(1,2,504)).astype(complex)
    H+=.01j*np.diag(np.linspace(1,2,504));G=rng.normal(size=504)+1j*rng.normal(size=504)*.1
    eta=rng.normal(size=504)+.2j;gt=rng.normal(size=504)*.05+.03j
    F=np.zeros((4,292));F[np.arange(4),np.arange(288,292)]=1
    a=full_joint_canonical_tangent(G,H,eta,F,gradient_clock_first=gt)
    assert np.max(abs(a['original_rows']))<2e-15
    assert np.max(abs(F@a['phase_acceleration_rate']))<2e-15
    held=full_joint_canonical_tangent(G,H,eta,F)
    assert np.linalg.norm(a['phase_acceleration_rate']-held['phase_acceleration_rate'])>.1
    assert not a['held_reference_clock']
