"""Action-owned internal reactions with fixed external environment."""
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb,arb_mat,ctx

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import derive_n12_gate7_slaved_interface as reaction
from certify_n12_gate7_coupled_center_neighborhood import load
from checkpoint_n12_gate7_66d_tangent_binding import digest

OUT=reaction.center.BASE/'gate7_comoving_interface_20260927'


def report(part):return json.loads((OUT/part/'report.json').read_bytes())


def test_attachment_derivatives_match_the_owner_chart():
    ctx.prec=512
    q=np.array([arb(0)]*37,dtype=object);q[25]=arb(1)/7
    raw=np.array([[arb(0)] for _ in range(98)],dtype=object);raw[25,0]=1
    B,signs,t,sech=reaction.attachment(q)
    d=reaction.attachment_variation(raw,signs,t,sech)
    dd=reaction.attachment_variation(raw,signs,t,sech,other=raw[:,0])
    h=arb(2)**-40;qp=q.copy();qm=q.copy();qp[25]+=h;qm[25]-=h
    bp=reaction.attachment(qp)[0];bm=reaction.attachment(qm)[0]
    assert abs((bp[0,25]-bm[0,25])/(2*h)-d[0,25,0])<arb('1e-22')
    assert abs((bp[0,25]-2*B[0,25]+bm[0,25])/(h*h)-dd[0,25,0])<arb('1e-22')
    assert d[0,25,0].mid()==-d[1,25,0].mid()
    assert d[0,25,0].rad()==d[1,25,0].rad()


def test_canonical_lifts_and_dynamics_are_verified_not_raw_eigensolves():
    for part in ('node13','node14'):
        r=report(part)
        for key in ('canonical_q_KKT_residual','canonical_v_KKT_residual',
                    'canonical_q_inverse_defect','canonical_v_inverse_defect',
                    'dynamics_equation_residual','momentum_adjoint_direct_replay'):
            assert r[key]['approximate_upper']<1e-25
        assert not r['finite_difference_used'] and not r['raw_eigensolve_used']
        assert r['reaction_block_rank']==7
        assert r['independent_environment_inputs']==0


def test_boundary_signs_are_the_actual_matching_row_signs():
    ctx.prec=512;a=load(OUT/'binding/arrays.npz')
    S=reaction.mat(a['boundary_target_signs'])
    assert S*S==arb_mat(np.eye(14,dtype=int).tolist())
    assert [float(S[i,i]) for i in range(14)]==([-1]*5+[1]*2)*2
    # The dynamic flux target is force-child_flux-momentum_rate, so its
    # residual has +b_flux while trace and momentum residuals have -b.
    r=report('node13')
    assert 'DP[DX u]' in r['derivative_formula']
    assert 'D2P[X,u]' in r['derivative_formula']


def test_output_graph_solve_keeps_environment_fixed_and_reactions_nonzero():
    r=report('binding');a=load(OUT/'binding/arrays.npz');ctx.prec=512
    assert r['coupled_shape']==[139,139] and r['certified_rank']==139
    assert r['physical_input_dimension']==66
    assert r['environment_variation']==0
    assert r['independent_interface_inputs']==r['independent_environment_inputs']==0
    K=reaction.mat(a['coupled_boundary_Jacobian'])
    V=reaction.mat(a['coupled_response']);F=reaction.mat(a['coupled_forcing'])
    assert all(v.contains(0) for v in (K*V+F).entries())
    assert any(x['approximate_upper']>1e-3 for x in r['reaction_row_norms'])
    assert r['reaction_solution_unique_given_state']
    assert not r['complete_boundary_problem_solved']
    assert not r['physical_tangent_comparison_completed']


def test_state_chart_agreement_is_the_signed_schur_identity():
    ctx.prec=512;r=report('binding');a=load(OUT/'binding/arrays.npz')
    K=reaction.mat(a['coupled_boundary_Jacobian'])
    assert all(K[i,j].is_zero() for i in range(125) for j in range(125,139))
    assert r['output_graph_state_chart_equals_fixed_label_chart']
    assert r['principal_angle_comparison']['maximum_angle_degrees']<1e-7
    assert r['principal_angle_comparison']['original_rank']==66
    assert r['principal_angle_comparison']['owner_consistent_rank']==66
    assert not r['physical_tube_extension_certified']
    assert not r['Gate7_closed'] and not r['FULL_BHSM_COMPLETE']


def test_outputs_reproduce_and_bind_sources():
    for part in ('node13','node14','binding','feedback13'):
        r=report(part);assert digest(OUT/part/'arrays.npz')==r['arrays_SHA256']
        for p,h in r['source_SHA256'].items():assert digest(Path(p))==h
        assert not r['tolerances_changed']
    receipt=json.loads((OUT/'reproduction.json').read_bytes())
    for name,item in receipt['files'].items():
        assert item['byte_identical']
        assert digest(OUT/name)==item['SHA256']


def test_weak_owner_has_state_feedback_and_verified_inverse():
    ctx.prec=512;a=load(OUT/'feedback13/arrays.npz');r=report('feedback13')
    K=reaction.mat(a['weak_bordered_operator'])
    assert K.nrows()==K.ncols()==63
    assert any(not K[i,61].contains(0) for i in range(37))
    for i in range(61):
        for j in range(2):
            assert (K[i,61+j]+K[61+j,i]).contains(0)
    assert r['weak_bordered_inverse_defect']['approximate_upper']<1e-25
    assert r['weak_compliance_inverse_defect']['approximate_upper']<1e-25
    assert all(v.contains(0) for v in a['weak_border_replay'].flat)


def test_fixed_exterior_affine_columns_are_not_new_physical_inputs():
    r=report('feedback13');a=load(OUT/'feedback13/arrays.npz')
    assert r['independent_environment_inputs']==0
    assert r['fixed_external_variation']==0
    assert a['rate_acceleration_affine'].shape==(61,3)
    assert a['rate_acceleration_derivative_affine'].shape==(61,3,98)
    assert a['attachment_acceleration_derivative_affine'].shape==(2,3,98)
    assert not r['environment_value_bound_to_gate7']
    assert not r['complete_66D_tangent_bound']
