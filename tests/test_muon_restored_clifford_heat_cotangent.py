import numpy as np
from scipy.linalg import funm
from bhsm.interface.muon_restored_clifford_heat_cotangent import (
    restored_clifford_coefficient_forms,restored_clifford_first_form,
    restored_clifford_heat_field_cotangent)


def test_restored_coefficient_and_gradient_equal_unsquared_action_variation():
    rng=np.random.default_rng(97);rows=((0,.2,-1),(1,.8,1))
    H=np.diag(np.arange(6)/9+1.);Xs=rng.normal(size=(24,6,6))*.07
    q=[dict(rows=rows,measure=.8+.03j,right_clock=.8+.02j,reflected_clock=.8-.02j,
        R=1.2+.01j,Rsharp=1.2-.01j,H=H,Hsharp=H,vertices=Xs,vertices_sharp=Xs.transpose(0,2,1))]
    E=np.zeros((3,1,1));G=np.ones((1,1,1));levels=np.array([0])
    c=restored_clifford_coefficient_forms(q,temporal_nodes=2,angular_derivatives=E,
        mean_source_gaunt=G,angular_levels=levels,starting_loop_max_level=0,family=1)
    z=rng.normal(size=6)+1j*rng.normal(size=6);phi=rng.normal(size=6)+1j*rng.normal(size=6)
    a=q[0];p=.8;d=1.;right=d/a['right_clock']*z+p*H@z
    left=d/a['reflected_clock']*phi+p*H.T@phi
    assert abs(phi@c['K']@z-a['measure']*(left@right))<3e-14
    direction=3;F=restored_clifford_first_form(c,0,direction,0)
    eps=.03
    def changed(t):
        b=dict(a,H=H+t*p*Xs[direction],Hsharp=H+t*p*Xs[direction].T)
        return restored_clifford_coefficient_forms([b],temporal_nodes=2,angular_derivatives=E,
            mean_source_gaunt=G,angular_levels=levels,starting_loop_max_level=0,family=1)['K']
    assert np.max(abs((changed(eps)-changed(-eps))/(2*eps)-F))<3e-14
    result=restored_clifford_heat_field_cotangent(c,.09)
    assert result['heat_cotangent_evaluated']
    Mi=np.linalg.inv(c['M']);P=Mi@c['K']
    density=funm(P,lambda x:-np.exp(-.09*x)/x)@Mi
    assert abs(result['closed_field_cotangent'][0,direction,0]-.5*np.trace(density@F))<2e-14
    assert result['gradient_original_first_form_identity_max']<3e-15


def test_original_nonaccretive_measure_is_rejected_without_a_sign_replacement():
    H=np.zeros((6,6));X=np.zeros((24,6,6))
    q=[dict(rows=((0,.5,-1),(1,.5,1)),measure=1,right_clock=1j,
        reflected_clock=1j,R=1,Rsharp=1,H=H,Hsharp=H,vertices=X,vertices_sharp=X)]
    c=restored_clifford_coefficient_forms(q,temporal_nodes=2,angular_derivatives=np.zeros((3,1,1)),
        mean_source_gaunt=np.ones((1,1,1)),angular_levels=np.array([0]),starting_loop_max_level=0,family=1)
    result=restored_clifford_heat_field_cotangent(c,.1)
    assert result['minimum_real_eigenvalue']<0
    assert not result['heat_cotangent_evaluated']
    assert 'closed_field_cotangent'not in result
