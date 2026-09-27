"""Differentiate the child output graph; do not assert complete BVP slaving."""
import argparse
import ast
import json
from pathlib import Path
import numpy as np
from flint import arb,arb_mat,ctx

import solve_n12_gate7_fiber_constrained_center as c
from certify_n12_gate7_coupled_center_neighborhood import load
from differentiate_n12_gate7_fiber_constrained_center import save_arrays
from diagnose_n12_gate7_eight_reaction_center import block,identity
from checkpoint_n12_gate7_66d_tangent_binding import amat,bound,digest,encoded
from compare_n12_gate7_reduced_fiber_tangents import comparison

BASE=c.BASE/'gate7_coupled_fiber_center_20260927'
OWNER=c.ROOT/'src/bhsm/interface/aether_cross_resolution_reconnaissance_v21_35.py'


def mat(a):return c.matrix(a)


def calculate(node13,node14,out):
    ctx.prec=512
    packets=[];sources={}
    for directory in (node13,node14):
        report=json.loads((directory/'report.json').read_bytes())
        if digest(directory/'arrays.npz')!=report['arrays_SHA256']:raise ValueError('reaction source changed')
        if report['independent_environment_inputs']!=0:raise ValueError('external parameter scope changed')
        packets.append(load(directory/'arrays.npz'))
        for name in ('report.json','arrays.npz'):sources[str(directory/name)]=digest(directory/name)
    jet=load(BASE/'jet/arrays.npz');root=load(BASE/'neighborhood/arrays.npz')
    J=mat(jet['Jfixed125']);Fp=mat(jet['forcing']);L=mat(root['left_phase_chart'])
    R=c.load_problem()['R']
    JL=arb_mat(98,125);JR=arb_mat(98,125)
    for i in range(98):
        for j in range(26):JL[i,j]=L[i,j]
        for j in range(99):JR[i,26+j]=R[i,j]
    with np.load(c.BASE/'gate7_66d_checkpoint_20260926/binding/arrays.npz') as z:T=amat(z['node_013_child_state'])
    D13,D14=[mat(p['derivative_action']) for p in packets]
    physical_D=arb_mat((D13*JL).tolist()+(D14*JR).tolist())
    direct_p=arb_mat((D13*T).tolist()+[[arb(0)]*66 for _ in range(7)])
    signs=[-1]*5+[1]*2
    S=arb_mat(14,14)
    for i in range(14):S[i,i]=signs[i%7]
    # B=S(b-beta(Y)). The upper residual's boundary action is already
    # evaluated on Y; it has no separately supplied matching-target b.
    lower=-S*physical_D
    F=arb_mat(Fp.tolist()+(-S*direct_p).tolist())
    K=arb_mat(139,139)
    for i in range(125):
        for j in range(125):K[i,j]=J[i,j]
    for i in range(14):
        for j in range(125):K[125+i,j]=lower[i,j]
        for j in range(14):K[125+i,125+j]=S[i,j]
    # Eliminate the actual reaction block before taking any supports.
    core=-J.solve(Fp)
    reactions=physical_D*core+direct_p
    all_response=arb_mat(core.tolist()+reactions.tolist())
    left=JL*core+T;right=JR*core
    fixed_left=mat(jet['fixed_label_left_history'][:98])
    fixed_right=mat(jet['fixed_label_right_history'][:98])
    co_pair=arb_mat(left.tolist()+right.tolist())
    fixed_pair=arb_mat(fixed_left.tolist()+fixed_right.tolist())
    co_projector=co_pair*(co_pair.transpose()*co_pair).inv()*co_pair.transpose()
    fixed_projector=fixed_pair*(fixed_pair.transpose()*fixed_pair).inv()*fixed_pair.transpose()
    # Full inverse is owned algebraically by this block factorization. Do not
    # use the badly scaled physical reaction units to declare a rank loss.
    inv=J.inv();inverse=arb_mat(139,139)
    lower_inverse=physical_D*inv
    for i in range(125):
        for j in range(125):inverse[i,j]=inv[i,j]
    for i in range(14):
        for j in range(125):inverse[125+i,j]=lower_inverse[i,j]
        for j in range(14):inverse[125+i,125+j]=S[i,j]
    midpoint=lambda m:np.array([float(v.mid()) for v in m.entries()]).reshape(m.nrows(),m.ncols())
    angles=comparison(midpoint(fixed_pair),midpoint(co_pair))
    ownertext=OWNER.read_text(encoding='utf-8');lines=ownertext.splitlines()
    names={'_trace_jacobian_at_order','_attachment_jacobian_at_order','_boundary_lift',
        '_canonical_pair_at_order','_metric_radial_flux_covector_at_order',
        '_exact_full_jet_euler_dirac_acceleration','_child_rows_at_order'}
    provenance={f.name:dict(start=f.lineno,end=f.end_lineno,text='\n'.join(lines[f.lineno-1:f.end_lineno]))
        for f in ast.parse(ownertext).body if isinstance(f,ast.FunctionDef) and f.name in names}
    for p in (OWNER,Path(__file__),BASE/'jet/arrays.npz',BASE/'neighborhood/arrays.npz'):
        sources[str(p)]=digest(p)
    save_arrays(out/'arrays.npz',dict(coupled_boundary_Jacobian=K,coupled_forcing=F,
        coupled_response=all_response,reaction_Dphi=reactions,boundary_target_signs=S,
        signed_boundary_state_block=lower,signed_boundary_direct_forcing=-S*direct_p,
        comoving_left_tangent=left,comoving_right_tangent=right,
        reaction_value_node13=packets[0]['reactions'],reaction_value_node14=packets[1]['reactions']))
    report=dict(status='CHILD_BOUNDARY_OUTPUT_GRAPH_DIFFERENTIATED',
        physical_definition='Fixed external environment e0 and boundary-class labels; seven interface quantities must be slaved by the complete boundary problem. The present calculation supplies its child output derivative only.',
        environment_variation=0,independent_environment_inputs=0,independent_interface_inputs=0,
        reaction_coordinates=7,reaction_endpoint_instances=2,physical_input_dimension=66,
        coupled_shape=[139,139],certified_rank=139,
        rank_argument='The verified 125-dimensional core Jacobian and exact invertible S=diag(-I5,+I2) at both endpoints form a lower-triangular coupled operator.',
        coupled_formula='K=[[J,0],[-S*Db*Y_x,S]], Fp=[F_core,p;-S*Db*Y_p], Dphi_b=Db*(Y_p+Y_x*x_p).',
        total_forcing_formula='delta e=0; retain the left and right history/phase/constraint reactions inside Y_p+Y_x*x_p before applying Db.',
        center_boundary_zero='b_star is the same beta(Y_star) object; B(Y_star,b_star;e0)=0 by the exact solved boundary rows, not by setting beta(Y_star) to zero.',
        reaction_solution_unique_given_state=True,output_graph_state_chart_equals_fixed_label_chart=True,
        complete_boundary_problem_solved=False,physical_tangent_comparison_completed=False,
        authority='Exact action-derived child output graph. Its triangular Schur identity does not select the complete fixed-environment physical tangent.',
        equivalence_scope='Solving B(Y,b)=S(b-beta(Y))=0 for outputs at a prescribed state. No opposite-side compatibility is implied by this identity, and the remaining left state complement is not solved by appending these output rows.',
        principal_angle_comparison=angles,projector_difference_outward=bound(co_projector-fixed_projector),
        state_tangent_difference_outward=bound(co_pair-fixed_pair),
        coupled_derivative_replay=bound(K*all_response+F),
        inverse_replay=bound(K*inverse-identity(139)),
        reaction_row_norms=[bound(block(reactions,[i],range(66))) for i in range(14)],
        boundary_sources=provenance,source_SHA256=sources,arrays_SHA256=digest(out/'arrays.npz'),
        physical_tube_extension_certified=False,Layer_C_rebound=False,
        Gate7_closed=False,FULL_BHSM_COMPLETE=False,tolerances_changed=False)
    (out/'report.json').write_bytes(encoded(report));print(json.dumps({k:report[k] for k in
        ('status','coupled_shape','physical_input_dimension','principal_angle_comparison','reaction_row_norms')},indent=2))


def main():
    p=argparse.ArgumentParser();p.add_argument('--node13',type=Path,required=True)
    p.add_argument('--node14',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);calculate(a.node13,a.node14,a.out)


if __name__=='__main__':main()
