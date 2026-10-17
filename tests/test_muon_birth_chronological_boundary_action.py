import numpy as np

from bhsm.interface.muon_birth_chronological_boundary_action import (
    action_hessian_from_midpoint_jacobian, discrete_boundary_two_jet,
    algebraic_boundary_response, assemble_chronological_chain,
    retained_chronological_boundary_application, _read_phase,
)
from bhsm.interface.muon_birth_coupled_primal_midpoint import nonlinear_midpoint_rows
from bhsm.interface.muon_parent_gauge_geometry_correction import ROOT


def test_saved_midpoint_rows_recover_all_mixed_and_algebraic_action_blocks():
    n=2; m=2; rng=np.random.default_rng(702); A=rng.normal(size=(2*n+m,2*n+m)); H=A+A.T
    eta=rng.normal(size=len(H)); linear=rng.normal(size=len(H))
    def action(z): return dict(gradient=H@z+linear,hessian=H)
    x0=np.array([.1,-.2]); p0=np.array([.3,.6]); unknown=rng.normal(size=3*n+m)
    for h in (-.07,.07):
        a=nonlinear_midpoint_rows(unknown,x0,p0,h,action)
        recovered=action_hessian_from_midpoint_jacobian(a['jacobian'],n,h)
        np.testing.assert_allclose(recovered,H,rtol=0,atol=9e-16)
        assert np.linalg.norm(recovered[2*n:,:2*n])>0
        assert np.linalg.norm(recovered[2*n:,2*n:])>0


def test_boundary_hessian_matches_independent_two_face_action_gradient():
    n=2; h=.11; rng=np.random.default_rng(37); A=rng.normal(size=(6,6)); H=A+A.T
    base=rng.normal(size=6); linear=rng.normal(size=6); g=H@base+linear
    a=discrete_boundary_two_jet(H,g,h,n); T=a['coordinate_map']; z=np.linalg.solve(T,base)
    def derivative(v): return h*T.T@(H@(T@v)+linear)
    direction=rng.normal(size=6); eps=1e-5
    np.testing.assert_allclose((derivative(z+eps*direction)-derivative(z-eps*direction))/(2*eps),
        a['hessian']@direction,rtol=2e-10,atol=2e-10)
    np.testing.assert_allclose(a['gradient'][:n],h*g[:n]/2-g[n:2*n],rtol=0,atol=1e-15)
    np.testing.assert_allclose(a['gradient'][n:2*n],h*g[:n]/2+g[n:2*n],rtol=0,atol=1e-15)


def test_algebraic_Schur_retains_far_face_cotangent_and_all_constraints():
    rng=np.random.default_rng(918); n=2; A=rng.normal(size=(7,7)); K=A.T@A+np.eye(7)
    directions=np.zeros((4,1)); directions[2,0]=1
    result=algebraic_boundary_response(K,n,directions)
    variation=np.r_[directions[:,0],result['algebraic_response'][:,0]]
    full=K@variation
    np.testing.assert_allclose(full[4:],0,rtol=0,atol=2e-15)
    np.testing.assert_allclose(full[:4],result['boundary_cotangent_response'][:,0],rtol=0,atol=2e-15)
    assert np.linalg.norm(full[:2])>0
    assert result['full_algebraic_dimension']==3
    assert not result['far_face_fixed_by_this_operation']
    assert result['spectral_directions_removed']==0


def test_chronological_chain_reaches_each_interior_node_and_algebraic_row():
    n=2; m=1; K=np.arange(25,dtype=float).reshape(5,5); K=K+K.T+np.eye(5)
    g=np.arange(5,dtype=float); a=assemble_chronological_chain(np.stack([K,K]),np.stack([g,g]),n)
    np.testing.assert_array_equal(a['gradient'],[0,1,2,4,2,3,4,4])
    np.testing.assert_array_equal(a['endpoint_indices'],[0,1,4,5])
    np.testing.assert_array_equal(a['interior_indices'],[2,3,6,7])
    assert a['hessian'].shape==(8,8)
    assert a['all_cell_Gauss_and_multiplier_rows_retained']


def test_actual_incoming_phase_reversal_retains_signed_birth_contact_and_true_Lyy():
    base=ROOT/'artifacts/muon_parent_gauge_geometry_correction_20261010'
    path=base/'attached_phase_incoming_1steps_run_1'
    result=retained_chronological_boundary_application(path)
    receipt,arrays,_,_=_read_phase(path); n=receipt['dynamic_count']; h=-receipt['span']
    np.testing.assert_allclose(result['cell_gradients'][0,:n],-arrays['stage_final_face'][0],rtol=0,atol=2e-12)
    np.testing.assert_allclose(result['cell_gradients'][0,n:2*n],-arrays['stage_initial_face'][0],rtol=0,atol=2e-12)
    assert result['signed_step']==h
    assert result['stored_oriented_step']<0
    assert np.linalg.norm(result['action_hessians'][0,2*n:,2*n:])>0
    assert np.max(abs(result['cell_algebraic_residual']))<2e-8
    assert result['lateral_wall_conormals'].shape==(1,80)
    assert result['birth_normal_response']['full_algebraic_dimension']==40


def test_lossless_stage_package_works_without_large_original_archive():
    base=ROOT/'artifacts/muon_parent_gauge_geometry_correction_20261010'
    direct=_read_phase(base/'attached_phase_outgoing_2steps_run_1')
    package=_read_phase(base/'attached_phase_outgoing_2steps_run_1_stage_package')
    assert direct[0]==package[0]
    assert direct[3]==package[3]
    for name in direct[1]:np.testing.assert_array_equal(direct[1][name],package[1][name])
