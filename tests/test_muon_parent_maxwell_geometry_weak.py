"""Independent nonlinear-action checks for the common mixed Maxwell block."""
import numpy as np
import pytest

from bhsm.interface.muon_birth_candidate_geometry_action import ROOT
from bhsm.interface.muon_moving_geometric_action import retained_state
from bhsm.interface.muon_matched_mechanical_source import epsilon
from bhsm.interface.muon_parent_retarded_hypercharge import WALL
from bhsm.interface.muon_parent_maxwell_background_euler import (
    _bracket, retained_connection_first_jet, background_weak_application,
)
from bhsm.interface.muon_parent_maxwell_geometry_weak import (
    geometric_connection_coefficient_jets, spatial_maxwell_weak_geometric_jets,
    retained_background_mixed_application,
)


@pytest.fixture(scope='module')
def retained():
    return retained_state(ROOT)


def coefficient_values(data):
    return {name:np.array([row[name].value for row in data['rows']])
            for name in data['rows'][0]}


def coefficient_application(state,rho):
    return geometric_connection_coefficient_jets(12,state[:37],state[37:74],state[74:98],rho,
        source_value=state[98],source_rate=state[99])


def test_exact_owned_profile_and_time_coordinate_conversion(retained):
    q,v,m=retained;rho=np.array([.13,.47,.93,1.38,WALL])
    original=retained_connection_first_jet(rho)
    proper=coefficient_values(geometric_connection_coefficient_jets(12,q,v,m,rho,
        clock='boundary_proper_time'))
    coordinate=coefficient_values(geometric_connection_coefficient_jets(12,q,v,m,rho))
    for name in ('electric','radial','angular','shift','connection_lambda','lambda_tau','lambda_rho'):
        np.testing.assert_allclose(proper[name],original[name],rtol=2e-14,atol=2e-11)
    N=proper['boundary_lapse']
    np.testing.assert_allclose(coordinate['electric'],proper['electric']/N,rtol=3e-15)
    np.testing.assert_allclose(coordinate['electric_radial'],proper['electric_radial']/N,rtol=3e-15)
    for name in ('radial','angular','shift','lambda_tau'):
        np.testing.assert_allclose(coordinate[name],N*proper[name],rtol=3e-15,atol=2e-13)
    np.testing.assert_allclose(coordinate['lambda_rho'],proper['lambda_rho'],rtol=3e-15)


def test_anchored_material_wall_and_advection_are_preserved_through_second_order(retained):
    q,v,m=retained
    data=geometric_connection_coefficient_jets(12,q,v,m,np.array([.2,.7,1.25,WALL]))
    sigma=data['rows'][-1]['sigma']
    assert abs(sigma.value)<1e-15
    assert np.linalg.norm(sigma.gradient)<2e-14
    assert np.linalg.norm(sigma.hessian)<2e-13
    for row in data['rows']:
        pulled=row['lambda_tau']-row['shift']*row['lambda_rho']
        assert abs(pulled.gradient[-1])<1e-13
        assert np.max(abs(pulled.hessian[-1]))<1e-12
        expected=(row['induced_lambda_tau_unadvected']
                  -(row['shift']*row['material_jacobian']-row['material_velocity'])
                  *row['induced_lambda_rho_unadvected'])
        assert pulled.value==pytest.approx(expected.value,rel=2e-15,abs=2e-15)
        np.testing.assert_allclose(pulled.gradient,expected.gradient,atol=2e-12,rtol=2e-14)
    assert data['induced_connection_motion_count']==1


def test_density_shift_and_connection_two_jet_matches_independent_coordinate_difference(retained):
    state=np.r_[*retained,0.,0.];rho=np.array([.23,.68,1.19])
    direction=np.zeros(100)
    direction[[0,4,15,29,39,50,74,80,90,98,99]]=[.04,-.02,.03,-.01,.02,-.01,.015,.01,-.008,.025,.012]
    base=coefficient_application(state,rho)
    step=2e-4
    minus=coefficient_values(coefficient_application(state-step*direction,rho))
    plus=coefficient_values(coefficient_application(state+step*direction,rho))
    middle=coefficient_values(base)
    for name in ('electric','electric_radial','radial','angular','shift','lambda_tau','lambda_rho','connection_lambda'):
        first=np.array([direction@row[name].gradient for row in base['rows']])
        second=np.array([direction@row[name].hessian@direction for row in base['rows']])
        np.testing.assert_allclose(first,(plus[name]-minus[name])/(2*step),rtol=2e-7,atol=2e-7)
        np.testing.assert_allclose(second,(plus[name]+minus[name]-2*middle[name])/step**2,
                                   rtol=8e-5,atol=2e-3)


def test_common_factor_eight_weak_row_and_oriented_contacts_match_actual_background(retained):
    out=retained_background_mixed_application(ROOT,points=40,test_order=4,
                                            clock='boundary_proper_time')
    from bhsm.interface.muon_parent_retarded_hypercharge import regular_radial_basis
    h,hr=regular_radial_basis(out['rho'],4)
    data=retained_connection_first_jet(out['rho'])
    original=background_weak_application(data,out['quadrature'],h,hr,np.zeros_like(h))
    app=out['application']
    np.testing.assert_allclose(app['weak']['values'],original['weak_Euler'],rtol=3e-14,atol=1e-8)
    np.testing.assert_allclose(app['temporal_momentum_test']['values'],
                               original['temporal_momentum_test'],rtol=3e-14,atol=1e-9)
    radial=np.einsum('r,rj->j',out['quadrature']*original['radial_momentum_density'],h)
    np.testing.assert_allclose(app['radial_momentum_test']['values'],radial,rtol=3e-14,atol=1e-8)
    assert app['temporal_contact']=='final plus, initial minus'
    assert app['radial_contact']=='wall plus, pole minus'
    assert not app['temporal_radial_Gauss_rows_replaced']
    assert not out['stationary_E1_claim']
    assert not out['physical_Pauli_contraction']


def control_fields(rho):
    """Real independent coefficient/test vectors, not physical primal data."""
    A=np.array([[.2,-.1,.3,.4],[-.3,.1,.2,-.2],[.1,.3,-.2,.1]])
    V=np.array([[.3,.2,-.1,.2],[.2,-.4,.1,.3],[-.2,.1,.4,-.1]])
    a=.04*np.cos(rho)[:,None,None,None]*A[None,None]
    at=.03*np.sin(rho)[:,None,None,None]*A[None,None]
    ar=-.04*np.sin(rho)[:,None,None,None]*A[None,None]
    v=.06*np.sin(rho)[:,None,None,None,None]*V[None,None,None]
    vt=.02*np.cos(rho)[:,None,None,None,None]*V[None,None,None]
    vr=.06*np.cos(rho)[:,None,None,None,None]*V[None,None,None]
    return dict(gauge=a,gauge_tau=at,gauge_rho=ar,gauge_angular=np.zeros((len(rho),1,3,3,4)),
        tests=v,tests_tau=vt,tests_rho=vr,tests_angular=np.zeros((len(rho),1,1,3,3,4)))


def literal_action(coefficients,fields,quadrature,gauge_step=0.):
    """Evaluate F=dA+A^2 directly, independently of the weak polynomial."""
    M=np.sqrt(8)*np.column_stack((np.eye(3),np.zeros(3)))
    a=fields['gauge']+gauge_step*fields['tests'][:,0]
    at=fields['gauge_tau']+gauge_step*fields['tests_tau'][:,0]
    ar=fields['gauge_rho']+gauge_step*fields['tests_rho'][:,0]
    ea=fields['gauge_angular']+gauge_step*fields['tests_angular'][:,0]
    exp=lambda x:x[:,None,None,None]
    A=exp(coefficients['connection_lambda']-1)*M+a
    At=exp(coefficients['lambda_tau'])*M+at
    Ar=exp(coefficients['lambda_rho'])*M+ar
    magnetic=2*A.copy();eps=epsilon()
    for i in range(3):
        for j in range(3):
            for k in range(3):
                magnetic[...,i,:]+=eps[i,j,k]*(ea[...,j,k,:]+.5*_bracket(A[...,j,:],A[...,k,:]).real)
    square=lambda x:np.sum(x*x,axis=(-1,-2))
    value=.5*(coefficients['electric'][:,None]*square(At-exp(coefficients['shift'])*Ar)
        -coefficients['radial'][:,None]*square(Ar)
        -coefficients['angular'][:,None]*square(magnetic))
    return np.einsum('r,rp->',quadrature,value)


def test_full_curvature_weak_and_mixed_geometric_row_are_independent_action_derivatives(retained):
    state=np.r_[*retained,0.,0.];rho=np.array([.28,.64,1.12]);w=np.array([.2,.4,.3])
    fields=control_fields(rho)
    base=coefficient_application(state,rho)
    weak=spatial_maxwell_weak_geometric_jets(base,w,np.ones(1),**fields)['weak']
    step=2e-5;values=coefficient_values(base)
    numerical=(literal_action(values,fields,w,step)-literal_action(values,fields,w,-step))/(2*step)
    assert weak['values'][0]==pytest.approx(numerical,rel=2e-8,abs=1e-6)
    direction=np.zeros(100)
    direction[[0,5,18,28,38,52,74,82,93,98,99]]=[.03,-.01,.02,.015,-.01,.02,.02,-.01,.005,.04,.02]
    delta=4e-4
    plus=coefficient_values(coefficient_application(state+delta*direction,rho))
    minus=coefficient_values(coefficient_application(state-delta*direction,rho))
    mixed=(literal_action(plus,fields,w,delta)-literal_action(plus,fields,w,-delta)
          -literal_action(minus,fields,w,delta)+literal_action(minus,fields,w,-delta))/(4*delta**2)
    actual=weak['geometric_jacobian'][0]@direction
    assert actual==pytest.approx(mixed,rel=3e-7,abs=2e-3)


def test_real_component_convention_does_not_silently_project_complex_fields(retained):
    rho=np.array([.3,.7]);q,v,m=retained
    data=geometric_connection_coefficient_jets(12,q,v,m,rho)
    fields=control_fields(rho);fields['gauge']=fields['gauge'].astype(complex)+1j
    with pytest.raises(ValueError,match='no silent complex projection'):
        spatial_maxwell_weak_geometric_jets(data,np.ones(2),np.ones(1),**fields)
