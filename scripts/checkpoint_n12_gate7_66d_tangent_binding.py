"""Frozen-operand tangent reconciliation and correctly scaled child binding.

No action evaluation, continuation, or scientific producer is called.
The output distinguishes a fixed first-order proposal from a reduced Hessian.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path

import numpy as np
from flint import arb, arb_mat, ctx
from scipy.linalg import subspace_angles

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT.parent/'BHSM-ae32-crossing-correction'
DOWNLOADS=Path(r'C:\Users\carbe\Downloads')
BASE=Path('artifacts/flagship_integration')
FIXED=BASE/'BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.npz'
PHYSICAL=BASE/'BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_AUGMENTED_JACOBIANS.npz'
CAUSAL=BASE/'BHSM_N12_GATE7_CURRENT_GREEN_SIGNED_TRANSVERSE_CAUSAL_CENTER.npz'
RESET=BASE/'BHSM_N12_GATE7_COMPACT_RESET_QUOTIENT_DOMAIN.npz'
PARENT=BASE/'BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.npz'
MID_DF=BASE/'.primal_mean_value_component_centered_midpoint_uniform_df_work/interval_013/derivative.npz'
RIGHT_DF=BASE/'.primal_mean_value_component_centered_endpoint_uniform_df_work/endpoint_014/derivative.npz'
EIGEN=BASE/'.coupled_midpoint_eigenpair_pilot_work/interval_013/eigenpair.npz'
PAIR=Path('tmp/bhsm_midpoint_center_mean_value_right_pair_20260913/value/first/column.npz')
STAGE=DOWNLOADS/'BHSM_GATE7_STAGEB_RANK_REFINEMENT_20260925_173630.npz'
ADJOINT=ROOT/'tmp/gate7_vector_20260919/full_input_midpoint_adjoint_first.json'
SCALE=1e-7
TEST_SCALE=1e6


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest().upper()
def encoded(x):return (json.dumps(x,sort_keys=True,indent=2)+'\n').encode()
def op(a):return float(np.linalg.norm(a,2))
def amat(x):
    a=np.asarray(x,dtype=object)
    return arb_mat(*a.shape,[arb(float(v)) if isinstance(v,(float,np.floating)) else arb(v) for v in a.flat])
def mid(a):return np.asarray([[float(a[i,j].mid()) for j in range(a.ncols())] for i in range(a.nrows())])
def frob(a):return sum((abs(x).upper()**2 for x in a.entries()),arb(0)).sqrt().upper()
def bound(a):
    v=frob(a);return {'exact_upper':str(v.fmpq()),'approximate_upper':float(v),'method':'Arb512_Frobenius'}
def restore(z,name):
    c=np.asarray(z[name+'_mid_q']);r=np.asarray(z[name+'_rad_q'])
    if c.ndim==1:c=c[:,None];r=r[:,None]
    return arb_mat(*c.shape,[arb(str(x))+arb(0,arb(str(y))) for x,y in zip(c.flat,r.flat)])
def frame(tangent,scale):
    e=np.zeros((99,74));e[:98,:73]=tangent;e[98,73]=scale;return e
def launch_child(family,flow_coeff,physical_descriptor_rate,child_coeff,scale=SCALE):
    if not np.isfinite(scale) or scale<=0:raise ValueError('positive descriptor coordinate scale required')
    state=np.column_stack((family[:73],flow_coeff))
    descriptor=np.r_[family[73],physical_descriptor_rate/scale]
    coordinates=np.linalg.solve(state,child_coeff)
    return np.vstack((child_coeff,descriptor@coordinates)),state,coordinates


def calculate():
    ctx.prec=512
    launch_report=json.loads((DOWNLOADS/'BHSM_GATE7_LAYERC_LAUNCH_TO_CHILD_BINDING_20260926_073134.json').read_bytes())
    expected={ROOT/FIXED:launch_report['sources'][FIXED.as_posix()],ROOT/PHYSICAL:launch_report['sources'][PHYSICAL.as_posix()],
        ROOT/CAUSAL:launch_report['sources'][CAUSAL.as_posix()],ROOT/RESET:launch_report['sources'][RESET.as_posix()],
        STAGE:launch_report['sources']['stageB'],ADJOINT:launch_report['sources']['adjoint'],
        EVIDENCE/MID_DF:'D58D440D259FEEC2AE1FBA518F21508C2716233E772EA8F0F0E0A79A552355B1',
        EVIDENCE/EIGEN:'60CABA68D3C017B5C6F1A605A7474A970EEB914F5A4F49789FD31B7A51032489',
        EVIDENCE/PAIR:'8D9F46D9D7C958FD6D367264C72FA3A02DBA2DF5CB277DC27BA942A4D68BBC8D'}
    adj=json.loads(ADJOINT.read_bytes())
    expected[EVIDENCE/RIGHT_DF]=adj['source_hashes'][RIGHT_DF.as_posix()]
    sources={str(p):digest(p) for p in expected}
    for p,sha in expected.items():
        if sources[str(p)]!=sha:raise ValueError('frozen source hash changed: '+str(p))
    if adj!=json.loads(ADJOINT.with_name('full_input_midpoint_adjoint_repeat.json').read_bytes()):
        raise ValueError('adjoint independent repeat mismatch')
    fields=('family','input_dimension','input_map','point_line_map','point_response_map','base_adjoint_rows','fixed_axis_covectors')
    semantic=hashlib.sha256(json.dumps({k:adj[k] for k in fields},sort_keys=True,separators=(',',':')).encode()).hexdigest().upper()
    if semantic!='320084B8E78737C41C6D24FF4C4C5D07E0DAC858EB893C9E6C50F866F713240A':raise ValueError('adjoint semantic mismatch')
    f=np.load(ROOT/FIXED);p=np.load(ROOT/PHYSICAL);stage=np.load(STAGE);parent=np.load(ROOT/PARENT)
    B=p['endpoint_physical_tangent_action'];A=f['endpoint_constraint_tangent_action']
    seed=np.load(ROOT/RESET)['projected_C2_parameter_lift'];maps=np.load(ROOT/CAUSAL)['causal_maps_center']
    q0=np.linalg.lstsq(B[0],seed,rcond=None)[0];family=np.vstack((q0,np.zeros((1,72))))
    families={}
    for i in range(14):
        family=maps[i]@family
        if i+1 in (13,14):families[i+1]=family.copy()
    rows=[];arrays={};child_maps={}
    for n in (13,14):
        a,b=A[n],B[n];z=stage[f'node_{n:03d}_child_coeff_null_73x66'];t=stage[f'node_{n:03d}_T_child_action_98x66']
        x=np.linalg.lstsq(b,a,rcond=None)[0];y=np.linalg.lstsq(a,b,rcond=None)[0];zphys=x@z
        residual=t-b@zphys
        aa,bb,xx,zz,tt=map(amat,(a,b,x,z,t))
        gramA=frob(aa.transpose()*aa-arb_mat(np.eye(73,dtype=int).tolist()))
        gramB=frob(bb.transpose()*bb-arb_mat(np.eye(73,dtype=int).tolist()))
        if not (gramA<1 and gramB<1):raise ValueError('stored full-rank frames not certified')
        flow=f['exact_endpoint_augmented_rates'][n];qflow=np.linalg.lstsq(b,flow[:98],rcond=None)[0]
        C,S,coordinates=launch_child(families[n],qflow,float(flow[98]),zphys)
        child_maps[n]=C
        lam_gradient=f['descriptor_gradient_action_diagnostic'][n]@t
        row=dict(node=n,classification='B_STORED_FRAME_RELATION_WITH_EXPLICIT_RESIDUAL',
            caveat='Same constraint construction at nearby Newton centers, not identical tangent spaces or merely machine rounding.',
            rank_fixed=int(np.linalg.matrix_rank(a)),rank_physical=int(np.linalg.matrix_rank(b)),
            rank_certified_for_stored_arrays=True,
            gram_error_upper_fixed=float(gramA),gram_error_upper_physical=float(gramB),
            principal_angle_degrees=float(np.degrees(subspace_angles(a,b)).max()),
            projector_difference_op2=op(a@a.T-b@b.T),
            fixed_into_physical_relative_residual=float(np.linalg.norm(b@x-a)/np.linalg.norm(a)),
            physical_into_fixed_relative_residual=float(np.linalg.norm(a@y-b)/np.linalg.norm(b)),
            fixed_to_physical_error=bound(aa-bb*xx),
            child_reprojection_error=bound(tt-bb*amat(zphys)),
            child_change_basis_rounding=bound(amat(zphys)-xx*zz),
            child_reprojection_operator_diagnostic=op(residual),
            child_reprojection_relative_residual=float(np.linalg.norm(residual)/np.linalg.norm(t)),
            stageB_product_rounding=bound(tt-aa*zz),
            center_shift_action_norm=float(np.linalg.norm((f['projected_states'][n]-parent['projected_states'][n])*f['state_weights'])),
            launch_condition=float(np.linalg.cond(S)),child_rank=int(np.linalg.matrix_rank(C)),
            descriptor_response_physical_norm=float(np.linalg.norm(SCALE*C[73])),
            descriptor_vs_diagnostic_eigenvalue_gradient=float(np.linalg.norm(SCALE*C[73]-lam_gradient)),
            descriptor_input_independent=False,
            descriptor_relation_authority='frozen center causal/reset-plus-flow graph; pointwise proposal, not a uniform nonlinear slaving certificate')
        rows.append(row)
        for key,value in dict(fixed_into_physical=x,physical_into_fixed=y,child_coeff_physical=zphys,
                child_state=t,child_reprojection_residual=residual,child_augmented=C,
                launch_state=S,launch_coordinates=coordinates,family=families[n]).items():
            arrays[f'node_{n:03d}_{key}']=value
    U=amat(np.asarray(adj['input_map'],dtype=object));C=amat(child_maps[14]);beta=amat(np.asarray(adj['base_adjoint_rows'],dtype=object))
    # The retained U is a partial derivative in the right endpoint-14 frame.
    right=np.load(EVIDENCE/RIGHT_DF);D=restore(right,'point_derivative')
    h=arb(float(f['collocation_arc_parameters'][14]-f['collocation_arc_parameters'][13]))
    identity=arb_mat(np.eye(99,dtype=int).tolist());M=identity/2-D*(h/8);E=amat(frame(B[14],SCALE))
    deltaU=M*E-U
    corrected_endpoint=amat(np.vstack((stage['node_014_T_child_action_98x66'],SCALE*child_maps[14][73:74])))
    correction=corrected_endpoint-E*C
    midpoint=U*C;midpoint_error=deltaU*C+M*correction
    df=np.load(EVIDENCE/MID_DF);line=restore(df,'selected_line_variation');response=restore(df,'response_variation')
    line_point=amat(np.asarray(adj['point_line_map'],dtype=object));response_point=amat(np.asarray(adj['point_response_map'],dtype=object))
    lp=line_point*C;rp=response_point*C
    binding=dict(input_endpoint=14,input_side='right endpoint partial HS derivative',trial_descriptor_scale=SCALE,test_descriptor_scale=TEST_SCALE,
        h=str(h.fmpq()),input_map_authority='frozen full_input_midpoint_adjoint_first.json',
        saved_input_map_vs_right_HS_formula=bound(deltaU),midpoint_reprojection_allowance=bound(midpoint_error),
        selected_line_uniform_point_difference=bound(line*midpoint-lp),
        response_uniform_point_difference=bound(response*midpoint-rp),
        selected_line_midpoints_only_difference_op2=op(mid(line)@mid(midpoint)-mid(lp)),
        response_midpoints_only_difference_op2=op(mid(response)@mid(midpoint)-mid(rp)),
        selected_line_reprojection_allowance=bound(line*midpoint_error),
        response_reprojection_allowance=bound(response*midpoint_error),
        fixed_adjoint_66x124_operator_diagnostic=op(mid(C.transpose()*beta)),
        full_input_uniform_certificate=adj['full_input_uniform_certificate'],
        base_adjoint_is_fixed_proposal=True,midpoint_child_rank=int(np.linalg.matrix_rank(mid(midpoint))),
        both_endpoint_history_map=False,nonlinear_child_graph_certified=False)
    arrays.update(midpoint_child_99x66=mid(midpoint),fixed_adjoint_rows_66x124=mid(C.transpose()*beta),
        selected_line_point_62x66=mid(lp),response_point_62x66=mid(rp))
    packet=dict(classification='B_WITH_EXPLICIT_STORED_REPROJECTION_ERROR',nodes=rows,binding=binding,
        source_SHA256={**sources,str(ROOT/PARENT):digest(ROOT/PARENT),str(Path(__file__)):digest(Path(__file__))},
        adjoint_semantic_SHA256=semantic,scientific_producers_run=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False,
        interpretation='First-order binding and numerical proposal only. No derivative is inferred from a pointwise affine enclosure.',
        reduced_mixed_contribution=None,reduction_factor=None,contraction_status='BLOCKED_ON_REDUCED_REACTION_AUTHORITY',
        first_blocker='No certified nonlinear slaving map for seven boundary/interface reactions plus descriptor response over the 66D child. The 124-variable eigenline/response fixed adjoint does not eliminate these eight variables.',
        required_reaction_unknowns=dict(boundary_interface=7,descriptor=1),
        prior_constraint_normal_reduction=25,
        required_next_object='Owner-bound Stage-B boundary complement and residual rows in the 74D convention, followed by a certified nonlinear eight-reaction slaving map and mixed residual curvature.')
    return packet,arrays


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    report,arrays=calculate();buffer=io.BytesIO();np.savez_compressed(buffer,**arrays)
    data=buffer.getvalue();report['arrays_SHA256']=hashlib.sha256(data).hexdigest().upper()
    a.out.mkdir(exist_ok=False,parents=True)
    (a.out/'arrays.npz').write_bytes(data);(a.out/'report.json').write_bytes(encoded(report))
    print(json.dumps(dict(nodes=report['nodes'],binding=report['binding']),indent=2))


if __name__=='__main__':main()
