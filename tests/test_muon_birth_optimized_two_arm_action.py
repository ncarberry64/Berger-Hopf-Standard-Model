import numpy as np

from bhsm.interface.muon_birth_optimized_two_arm_action import (
    SIZE,FREE,homogeneous_identification,scalar_boundary_rows,
    optimized_coupled_rows,optimized_coupled_jacobian,solve_checkpointed,
)
from bhsm.interface.muon_parent_gauge_geometry_correction import ROOT,STATE_SOURCE,correction_representation


def fixture():
    with np.load(ROOT/STATE_SOURCE,allow_pickle=False) as f:
        x=f['state'];w=f['state_weights']
    c=np.r_[x[98:],x[:98],[.1,.8,-.03,.04],[.08,.75,.02,-.01],
        [.02,-.01,.01,.005],[-.01,.015,.007,-.006],np.zeros(8),[.03,-.02,.01,.04],np.log(.001)]
    # All 24 retained constraint moments enter the canonical saddle.
    # A 12-node cap rule aliases them and makes that saddle unresolved.
    rep=correction_representation(radial_points=12,radial_order=1,cap_points=48)
    fields={k:np.zeros((12,1,3,5,4) if k=='gauge_angular' else (12,1,5,4)) for k in ('gauge','gauge_tau','gauge_rho','gauge_angular')}
    a=dict(rho=rep['rho'],radial_quadrature=rep['radial_quadrature'],fields=fields,wall_gauge=np.zeros((5,4)),
        lambda_H=rep['scalar_matching']['lambda_H'],nu_squared_action=4.,cap_points=48)
    return c,a,w,x[:37]


def test_unknown_bundle_and_isometry_have_correct_right_frame_graph():
    from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
    z=np.array([.2,-.15,.07,.23]);v=np.array([.1,.02,-.03,.04]);a=homogeneous_identification(z,v)
    j=np.sqrt(8)*higgs_u2_real_representation()['complex_generators'][:3]
    for i in range(3):
        np.testing.assert_allclose(np.einsum('k,kab->ab',a['frame_rotation'][i],j),a['U']@j[i]@a['U'].conj().T,atol=5e-16)
    np.testing.assert_allclose(a['frame_rotation']@a['frame_rotation'].T,np.eye(3),atol=5e-16)
    eps=1e-5;plus=homogeneous_identification(z+eps*v);minus=homogeneous_identification(z-eps*v)
    np.testing.assert_allclose(a['U_variation'],(plus['U']-minus['U'])/(2*eps),rtol=2e-9,atol=2e-11)
    np.testing.assert_allclose(a['child_point_variation'],(plus['child_point']-minus['child_point'])/(2*eps),rtol=2e-9,atol=2e-11)
    assert not a['initial_identification_selected']


def test_actual_scalar_birth_rows_differentiate_unknown_identification_and_density_dual_once():
    c,a,w,q=fixture();v=np.zeros(SIZE);v[196:224]=np.sin(np.arange(28));v[-1]=.2
    r=scalar_boundary_rows(c,v);eps=1e-5
    plus=scalar_boundary_rows(c+eps*v);minus=scalar_boundary_rows(c-eps*v)
    np.testing.assert_allclose(r['residual_variation'],(plus['residual']-minus['residual'])/(2*eps),rtol=3e-7,atol=2e-10)
    np.testing.assert_allclose(r['transport_application']['image_projection_residual'],0,atol=3e-16)
    # Complex p already has metric density; the action dual is 2p.
    c[220:224]=0;c[212:216]=[.01,.03,-.02,.04];c[216:220]=[.03,-.01,.02,.01]
    r=scalar_boundary_rows(c)
    np.testing.assert_allclose(r['momentum_residual'],2*(c[212:216]-c[216:220]),atol=1e-16)
    assert not r['formation_interval_selected']


def test_same_action_free_column_jacobian_matches_full_directional_recalculation():
    c,a,w,q=fixture();base=optimized_coupled_rows(c,a,w,q)
    J,steps=optimized_coupled_jacobian(c,a,w,q,base)
    v=np.zeros(SIZE);v[37]=.002;v[74]=-.003;v[140]=.001;v[174]=.002
    v[196:220]=.01*np.sin(np.arange(24));v[220:225]=[.01,-.02,.03,-.04,.1]
    eps=1e-4;plus=optimized_coupled_rows(c+eps*v,a,w,q);minus=optimized_coupled_rows(c-eps*v,a,w,q)
    np.testing.assert_allclose(J@v,(plus['residual']-minus['residual'])/(2*eps),rtol=3e-4,atol=2e-6)
    np.testing.assert_allclose(base['spatial_connection_graph_residual'],0,atol=5e-16)
    np.testing.assert_array_equal(J[:,-1],0)
    assert not base['physical_birth_solution']


def test_accepted_checkpoint_is_a_resumable_actual_vector_not_proposed_step():
    c=np.zeros(SIZE);c[37]=1.5;c[135]=.7
    def evaluate(x):return dict(residual=np.array([x[37]**2-.81,x[135]-.4]))
    def jac(x,b):
        J=np.zeros((2,SIZE));J[0,37]=2*x[37];J[1,135]=1
        return J,np.zeros(SIZE)
    saved=[]
    def checkpoint(i,x,b,J,eps,scale,history,status,linearization_point):
        saved.append((i,x.copy(),b['residual'].copy(),scale.copy(),status))
    first=solve_checkpointed(c,evaluate,jac,np.ones(len(FREE)),max_iterations=1,checkpoint=checkpoint)
    assert len(saved)==2 and saved[-1][-1]=='ACCEPTED_STEP'
    np.testing.assert_array_equal(saved[-1][1],first['coefficients'])
    np.testing.assert_array_equal(saved[-1][2],evaluate(saved[-1][1])['residual'])
    resumed=solve_checkpointed(saved[-1][1],evaluate,jac,np.ones(len(FREE)),max_iterations=8,row_scale=saved[-1][3],iteration_offset=1)
    full=solve_checkpointed(c,evaluate,jac,np.ones(len(FREE)),max_iterations=9)
    assert resumed['status']=='ASSIGNED_SCALAR_BIRTH_TOLERANCE'
    np.testing.assert_allclose(resumed['coefficients'],full['coefficients'],atol=0,rtol=0)
