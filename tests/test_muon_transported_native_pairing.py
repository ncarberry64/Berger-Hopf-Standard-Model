import numpy as np
from bhsm.interface.muon_transported_native_pairing import (
    transported_native_vertices,independent_native_source_images,coframe_pairing_transition,
    finite_native_form_lower_comparison)


def test_complex_source_coefficients_use_fixed_dagger_vertices_without_conjugation():
    rng=np.random.default_rng(759);wall=rng.normal(size=(2,5,4,4))+1j*rng.normal(size=(2,5,4,4))
    H=rng.normal(size=(2,4,4))+1j*rng.normal(size=(2,4,4))
    a=independent_native_source_images(wall,H,radius=.91,lapse=.67,family=1)
    v=transported_native_vertices(.91,.67,.91,.67,family=1)
    c=np.concatenate((wall.reshape(2,20,4),H),axis=1)
    expected=np.einsum('ach,cij->ahij',c,v['native_vertices'].conj().transpose(0,2,1))
    np.testing.assert_allclose(a['Xisharp'],expected,atol=3e-15)
    assert np.linalg.norm(a['Xisharp']-a['Xi'].conj().transpose(0,1,3,2))>1


def test_total_temporal_coordinate_rotation_is_applied_to_both_action_branches():
    v=transported_native_vertices(.9+.03j,.7-.02j,.9-.03j,.7+.02j,family=2)
    np.testing.assert_allclose(v['vertices'][:4],-1j*v['native_vertices'][:4])
    np.testing.assert_allclose(v['vertices_sharp'][:4],1j*v['native_vertices_sharp'][:4])
    np.testing.assert_allclose(v['vertices_sharp'],v['vertices'].conj().transpose(0,2,1),atol=1e-15)


def test_coframe_measure_transport_requires_density_contact_and_retains_original_measure():
    s=.27;w=lambda x:np.exp((.2+.7j)*x);ws=lambda x:np.exp((.2-.7j)*x)
    a=coframe_pairing_transition(w(s),ws(s),.3*w(s),
        right_clock_derivative=(.2+.7j)*w(s),reflected_clock_derivative=(.2-.7j)*ws(s))
    np.testing.assert_allclose(a['native_geometric_measure'],.3*np.exp(.2*s))
    np.testing.assert_allclose(a['dual_density_ratio'],np.exp(.7j*s))
    np.testing.assert_allclose(a['analytic_left_density_connection'],-.7j/ws(s))
    # phi_old=phi_native/rho; its weak derivative generates the extra body.
    phi=lambda x:1+.4*x;eps=1e-5
    f=lambda x:phi(x)/np.exp(.7j*x)
    old_derivative=(f(s+eps)-f(s-eps))/(2*eps)
    transformed=(.4-.7j*phi(s))/np.exp(.7j*s)
    np.testing.assert_allclose(old_derivative,transformed,rtol=2e-10)
    assert not a['original_measure_changed_by_coordinate_relabeling']


def test_finite_lower_comparison_uses_original_variable_coframe_and_initial_only_domain():
    from bhsm.interface.muon_chronological_clifford_graph import chronological_clifford_blocks,chronological_dense_blocks
    from scipy.linalg import eigh
    rng=np.random.default_rng(643);raw=rng.normal(size=(6,6))+1j*rng.normal(size=(6,6))
    H=(raw+raw.conj().T)*.05;E=np.zeros((3,1,1));alpha=np.zeros((3,6,6));q=[]
    points,weights=np.polynomial.legendre.leggauss(4)
    for j in range(4):
        for x,g in zip((points+1)/2,weights/2):
            phase=.2+.07*(j+x);w=np.exp(1j*phase)
            q.append(dict(H=H,Hsharp=H.conj().T,R=1.,Rsharp=1.,
                right_clock=w,reflected_clock=w.conjugate(),measure=.2*g,
                rows=((j,1-x,-5.),(j+1,x,5.))))
    a=finite_native_form_lower_comparison(q,temporal_nodes=5,angular_derivatives=E,alpha=alpha)
    b=chronological_clifford_blocks(q,temporal_nodes=5,angular_derivatives=E,alpha=alpha)
    actual=eigh(chronological_dense_blocks(b),chronological_dense_blocks(b,prefix='M'),eigvals_only=True)[0]
    assert 0<a['product_form_lower_comparison']<=actual
    assert not a['outward_arithmetic_certificate']


def test_complex_analytic_density_dual_recovers_original_weak_pairing_and_conormal():
    # Independent left coefficient, not its complex conjugate. The derivative
    # of bar_old=bar_native/rho is the density contact, including at the face.
    w=1.2+.4j;ws=w.conjugate();m=.13*w;wd=.17+.31j;wsd=wd.conjugate()
    a=coframe_pairing_transition(w,ws,m,right_clock_derivative=wd,reflected_clock_derivative=wsd)
    phi=.7-.2j;dphi=.11+.23j;Hs=.2+.3j;right=-.19+.61j
    rho=a['dual_density_ratio'];mu=a['native_geometric_measure']
    old=m*((dphi-phi*a['logarithmic_dual_density_derivative'])/(rho*ws)+phi/rho*Hs)*right
    new=mu*(dphi/ws+phi*(Hs+a['analytic_left_density_connection']))*right
    np.testing.assert_allclose(old,new,atol=2e-17)
    np.testing.assert_allclose(m*(phi/rho)*right/ws,mu*phi*right/ws,atol=2e-17)
