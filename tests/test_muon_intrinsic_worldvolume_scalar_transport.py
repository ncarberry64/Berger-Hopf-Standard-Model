"""Finite transport/weak-pairing controls; no physical field state selected."""
import numpy as np
import pytest
from scipy.linalg import expm

from bhsm.interface.muon_intrinsic_worldvolume_scalar_transport import (
    induced_worldvolume_flow, unit_s3_material_frame,
    worldvolume_scalar_transport_ivp, scalar_birth_transport_application,
    current_scalar_time_and_load_contract,
    unit_quaternion_to_su2, su2_to_unit_quaternion,
)


POINTS=np.concatenate((np.eye(4),-np.eye(4)))
M=np.array([
 [[0,-1,0,0],[1,0,0,0],[0,0,0,-1],[0,0,1,0]],
 [[0,0,-1,0],[0,0,0,1],[1,0,0,0],[0,-1,0,0]],
 [[0,0,0,-1],[0,0,-1,0],[0,1,0,0],[1,0,0,0]],
],float)


def coupled_control():
    c=np.zeros(45);c[:5]=(.23,.17,-.09,.08,-.03)
    c[5:]=np.linspace(-.4,.7,40)
    vp=np.zeros((20,45));vc=np.zeros((20,45))
    vp[:,5:25]=np.eye(20);vc[:,25:45]=np.eye(20)
    return c,vp,vc


def evaluator(nonlinear=False):
    """All control geometry/gauge jets are from this same coefficient vector."""
    def evaluate(t,q,c,v):
        p=len(q);r=np.exp((1-t)*c[3]+t*c[4]);g=r*r
        angular=q[:,0] if nonlinear else np.ones(p)
        b=c[0]*angular
        E=unit_s3_material_frame(q)
        db=c[0]*E[:,0,:] if nonlinear else np.zeros((p,3))
        ddb=np.einsum('aij,pcj->pcai',M,np.einsum('cij,pj->pci',M,q))[:,:,:,0]*c[0] if nonlinear else np.zeros((p,3,3))
        h=np.zeros((p,4,4));h[:,0,0]=1-g*b*b
        h[:,1:,1:]=-g*np.eye(3);h[:,0,1]=h[:,1,0]=g*b
        dh=np.zeros((p,3,4,4));dh[:,:,0,0]=-2*g*b[:,None]*db
        dh[:,:,0,1]=dh[:,:,1,0]=g*db
        ddh=np.zeros((p,3,3,4,4))
        ddh[:,:,:,0,0]=-2*g*(db[:,:,None]*db[:,None,:]+b[:,None,None]*ddb)
        ddh[:,:,:,0,1]=ddh[:,:,:,1,0]=g*ddb
        s2=np.array([[0,-1j],[1j,0]]);s3=np.diag([1.,-1.])
        A=np.zeros((p,4,2,2),complex);A[:,0]=1j*c[1]*s3;A[:,1]=1j*c[2]*s2
        out=dict(metric=h,metric_spatial_derivatives=dh,
                 metric_spatial_second_derivatives=ddh,connection=A)
        if v is not None:
            vg=2*g*((1-t)*v[3]+t*v[4]);vb=v[0]*angular
            vdb=v[0]*E[:,0,:] if nonlinear else np.zeros((p,3))
            vh=np.zeros_like(h);vh[:,0,0]=-vg*b*b-2*g*b*vb
            vh[:,1:,1:]=-vg*np.eye(3);vh[:,0,1]=vh[:,1,0]=vg*b+g*vb
            vdh=np.zeros_like(dh)
            vdh[:,:,0,0]=-2*(vg*b[:,None]*db+g*vb[:,None]*db+g*b[:,None]*vdb)
            vdh[:,:,0,1]=vdh[:,:,1,0]=vg*db+g*vdb
            vA=np.zeros_like(A);vA[:,0]=1j*v[1]*s3;vA[:,1]=1j*v[2]*s2
            out.update(metric_variation=vh,metric_spatial_derivative_variation=vdh,
                       connection_variation=vA,connection_spatial_derivatives=np.zeros((p,3,4,2,2),complex))
        return out
    return evaluate


def solve(c,variation=None,nonlinear=False):
    kw=dict(coefficients=c,times=np.array([0.,.3,1.]),initial_material_points=POINTS,
            initial_bundle_transport=np.broadcast_to(np.eye(2),(8,2,2)),
            initial_jacobian=np.ones(8),evaluator=evaluator(nonlinear),rtol=2e-11,atol=2e-12)
    if variation is not None:
        kw.update(coefficient_variation=variation,initial_material_points_variation=np.zeros((8,4)),
                  initial_bundle_transport_variation=np.zeros((8,2,2)),initial_jacobian_variation=np.zeros(8))
    return worldvolume_scalar_transport_ivp(**kw)


def basis(side,q,c,v):
    angular=np.column_stack((np.ones(len(q)),2*q))
    fiber=np.array([[1,0,1j,0],[0,1,0,1j]])
    B=np.einsum('pn,id->pind',angular,fiber).reshape(len(q),2,20)
    E=unit_s3_material_frame(q)
    dangular=np.concatenate((np.zeros((len(q),3,1)),2*E.transpose(0,2,1)),axis=2)
    grad=np.einsum('pan,id->paind',dangular,fiber).reshape(len(q),3,2,20)
    return dict(basis=B,basis_variation=np.zeros_like(B),basis_spatial_derivatives=grad)


def density(side,q,c,v):
    index=3 if side=='parent' else 4;mu=np.full(len(q),np.exp(3*c[index]))
    return dict(density=mu,density_variation=np.zeros(len(q)) if v is None else 3*v[index]*mu,
                density_spatial_derivatives=np.zeros((len(q),3)))


def application(solution):
    _,parent,child=coupled_control()
    return scalar_birth_transport_application(transport=solution,parent_birth_points=POINTS,
        birth_parent_time=1.,birth_child_time=1.,quadrature=np.full(8,1/8),
        basis_evaluator=basis,density_evaluator=density,
        parent_coefficient_map=parent,child_coefficient_map=child,
        parent_birth_points_variation=None if solution['coefficient_variation'] is None else np.zeros_like(POINTS))


def test_solved_worldvolume_flow_and_bundle_are_nontrivial_not_identity_defaults():
    c,_,_=coupled_control();s=solve(c)
    expected=POINTS*np.cos(c[0])+np.einsum('ij,pj->pi',M[0],POINTS)*np.sin(c[0])
    np.testing.assert_allclose(s['material_points'][-1],expected,atol=2e-11)
    A=1j*c[1]*np.diag([1.,-1.])+c[0]*1j*c[2]*np.array([[0,-1j],[1j,0]])
    np.testing.assert_allclose(s['bundle_transport'][-1],np.broadcast_to(expm(-A),(8,2,2)),atol=2e-11)
    np.testing.assert_allclose(s['haar_jacobian'],1,atol=2e-12)
    np.testing.assert_allclose(s['normal_proper_clock'][-1],1,atol=2e-12)
    assert s['point_norm_defect']<1e-10 and s['bundle_unitarity_defect']<1e-10
    assert not s['scalar_interior_parallel_transport_claim']


def test_material_chart_derivatives_agree_with_inherited_scalar_coframe():
    from bhsm.interface.muon_intrinsic_scalar_discretization import (
        scalar_angular_derivative_matrices, scalar_basis_values,
    )
    q=np.array([[.31,-.47,.29,.73],[-.62,.11,.57,-.41]])
    q/=np.linalg.norm(q,axis=1)[:,None]
    g=unit_quaternion_to_su2(q)
    np.testing.assert_allclose(su2_to_unit_quaternion(g),q,atol=1e-14)
    values=scalar_basis_values(g,3);derivatives=scalar_angular_derivative_matrices(3)
    eps=2e-6
    for a in range(3):
        direction=np.einsum('ij,pj->pi',M[a],q)
        plus=q*np.cos(eps)+direction*np.sin(eps)
        minus=q*np.cos(eps)-direction*np.sin(eps)
        fd=(scalar_basis_values(unit_quaternion_to_su2(plus),3)
            -scalar_basis_values(unit_quaternion_to_su2(minus),3))/(2*eps)
        np.testing.assert_allclose(fd,values@derivatives[a],atol=4e-10,rtol=3e-9)
    with pytest.raises(ValueError,match='SU2'):
        su2_to_unit_quaternion(np.exp(.2j)*g)


def test_scalar_image_and_dual_include_endpoint_measure_ratio():
    c,parent,child=coupled_control();s=solve(c);app=application(s)
    np.testing.assert_allclose(app['parent_pairing'],2*np.exp(3*c[3])*np.eye(20),atol=1e-11)
    np.testing.assert_allclose(app['child_pairing'],2*np.exp(3*c[4])*np.eye(20),atol=1e-11)
    np.testing.assert_allclose(app['dual_trace_return'],
        np.exp(3*(c[4]-c[3]))*app['trace_transport'].T,atol=1e-11)
    assert app['image_projection_weighted_norm']<1e-10
    assert not app['finite_scalar_image_invariance_claim']
    Hparent=np.einsum('pid,d->pi',basis('parent',POINTS,c,None)['basis'],parent@c)
    Hchild=np.einsum('pid,d->pi',basis('child',s['material_points'][-1],c,None)['basis'],child@c)
    np.testing.assert_allclose(app['trace_residual'],Hchild-np.einsum('pij,pj->pi',s['bundle_transport'][-1],Hparent))
    x=np.linspace(.2,.7,20);y=np.linspace(-.1,.8,20)
    assert x@app['parent_pairing']@app['dual_trace_return']@y==pytest.approx(
        (app['trace_transport']@x)@app['child_pairing']@y)


@pytest.mark.parametrize('nonlinear',[False,True])
def test_coupled_transport_tangent_keeps_map_bundle_jacobian_and_unknown_field_variation(nonlinear):
    c,_,_=coupled_control();v=np.linspace(-.13,.19,len(c));eps=2e-6
    s=solve(c,v,nonlinear);minus=solve(c-eps*v,nonlinear=nonlinear);plus=solve(c+eps*v,nonlinear=nonlinear)
    for key in ('material_points','bundle_transport','haar_jacobian','normal_proper_clock'):
        np.testing.assert_allclose(s[key+'_variation'],(plus[key]-minus[key])/(2*eps),atol=3e-8,rtol=2e-7)
    a=application(s);am=application(minus);ap=application(plus)
    for key in ('trace_transport','dual_trace_return','parent_pairing','child_pairing','trace_residual','scalar_transport_image'):
        np.testing.assert_allclose(a[key+'_variation'],(ap[key]-am[key])/(2*eps),atol=5e-8,rtol=3e-7)
    if nonlinear:
        assert np.max(abs(s['haar_jacobian'][-1]-1))>.01
        assert a['image_projection_weighted_norm']>.01
        norm_squared=2*np.sum(np.full(8,1/8)[:,None,None]
            *a['child_pulled_pairing_density'][:,None,None]*abs(a['image_projection_residual'])**2)
        assert a['image_projection_weighted_norm']**2==pytest.approx(norm_squared)


def test_induced_adm_flow_sign_and_normal_clock():
    c,_,_=coupled_control();data=evaluator()(0.,POINTS,c,None)
    flow=induced_worldvolume_flow(data['metric'],data['metric_spatial_derivatives'])
    np.testing.assert_allclose(flow['b'],np.tile([c[0],0,0],(8,1)),atol=1e-14)
    np.testing.assert_allclose(flow['lapse'],1,atol=1e-14)


def test_missing_actual_time_connection_is_reached_guard_not_implicit_zero():
    c,_,_=coupled_control()
    def missing(t,q,c,v):
        data=evaluator()(t,q,c,v);data.pop('connection');return data
    with pytest.raises(ValueError,match='bind connection; omitted A_t is not zero'):
        worldvolume_scalar_transport_ivp(coefficients=c,times=[0,1],initial_material_points=POINTS,
            initial_bundle_transport=np.broadcast_to(np.eye(2),(8,2,2)),initial_jacobian=np.ones(8),
            evaluator=missing,rtol=1e-9,atol=1e-10)


@pytest.mark.parametrize('bad_input',['connection_variation','connection_spatial_derivatives','initial_bundle_variation'])
def test_unitary_transport_tangent_rejects_nonunitary_input_jets(bad_input):
    c,_,_=coupled_control();v=np.ones_like(c)
    def malformed(t,q,c,v):
        data=evaluator()(t,q,c,v)
        if bad_input!='initial_bundle_variation':
            data[bad_input]=data[bad_input].copy();data[bad_input].flat[0]+=1
        return data
    deltaU=np.zeros((8,2,2),complex)
    if bad_input=='initial_bundle_variation':deltaU[:,0,0]=1
    with pytest.raises(ValueError,match='anti-Hermitian|tangent to the unitary'):
        worldvolume_scalar_transport_ivp(coefficients=c,times=[0,1],initial_material_points=POINTS,
            initial_bundle_transport=np.broadcast_to(np.eye(2),(8,2,2)),initial_jacobian=np.ones(8),
            evaluator=malformed,rtol=1e-9,atol=1e-10,coefficient_variation=v,
            initial_material_points_variation=np.zeros_like(POINTS),
            initial_bundle_transport_variation=deltaU,initial_jacobian_variation=np.zeros(8))


def test_nonzero_initial_bundle_identification_tangent_is_propagated():
    c,_,_=coupled_control();generator=1j*np.array([[0,1],[1,0]])
    kwargs=dict(coefficients=c,times=[0,1],initial_material_points=POINTS,
        initial_jacobian=np.ones(8),evaluator=evaluator(),rtol=2e-11,atol=2e-12)
    identity=np.broadcast_to(np.eye(2),(8,2,2));delta=np.broadcast_to(generator,(8,2,2))
    s=worldvolume_scalar_transport_ivp(**kwargs,initial_bundle_transport=identity,
        coefficient_variation=np.zeros_like(c),initial_material_points_variation=np.zeros_like(POINTS),
        initial_bundle_transport_variation=delta,initial_jacobian_variation=np.zeros(8))
    eps=2e-6
    plus=worldvolume_scalar_transport_ivp(**kwargs,initial_bundle_transport=np.broadcast_to(expm(eps*generator),(8,2,2)))
    minus=worldvolume_scalar_transport_ivp(**kwargs,initial_bundle_transport=np.broadcast_to(expm(-eps*generator),(8,2,2)))
    np.testing.assert_allclose(s['bundle_transport_variation'],
        (plus['bundle_transport']-minus['bundle_transport'])/(2*eps),atol=2e-10,rtol=2e-8)
    U=s['bundle_transport'];vU=s['bundle_transport_variation']
    np.testing.assert_allclose(vU.conj().swapaxes(-1,-2)@U+U.conj().swapaxes(-1,-2)@vU,0,atol=2e-10)


def test_birth_has_no_independent_future_offset():
    c,parent,child=coupled_control();s=solve(c)
    with pytest.raises(ValueError,match='same physical E1'):
        scalar_birth_transport_application(transport=s,parent_birth_points=POINTS,
            birth_parent_time=1.,birth_child_time=2.,quadrature=np.full(8,1/8),
            basis_evaluator=basis,density_evaluator=density,
            parent_coefficient_map=parent,child_coefficient_map=child)


def test_time_and_load_rows_keep_primitive_unknowns_and_direct_contact_scope():
    contract=current_scalar_time_and_load_contract()
    assert contract['direct_area_H_contact']==0
    assert contract['direct_material_response_H_contact']==0
    assert contract['direct_material_response_Hs_contact']==0
    assert not contract['physical_time_interval_assigned']
    assert not contract['homogeneous_scalar_Cauchy_component_assigned']
    assert not contract['eliminated_native_term_added_to_classical_force']
