"""Frozen p/q Schur decomposition and action-metric tangent comparison.

The q-only replay difference is vertical by construction. Test the complete
shooting response as well, so quotient agreement cannot hide intrinsic forcing.
"""
import argparse
import io
import json
from pathlib import Path

import numpy as np
from flint import arb, arb_mat, ctx
from scipy.linalg import subspace_angles

from checkpoint_n12_gate7_66d_tangent_binding import ROOT, BASE, PHYSICAL, amat, mid, bound, digest, encoded
from diagnose_n12_gate7_eight_reaction_center import block, identity

PACKETS={
    'appended':'gate7_appended_fiber_center_20260926',
    'fiber':'gate7_descriptor_fiber_owner_20260926',
    'owner':'gate7_full_shooting_owner_20260926',
    'split':'gate7_8reaction_center_20260926',
    'binding':'gate7_66d_checkpoint_20260926/binding',
}


def comparison(x,y):
    """Positive stored action norm; never use the indefinite Hessian as metric."""
    qx=np.linalg.qr(x,mode='reduced')[0];qy=np.linalg.qr(y,mode='reduced')[0]
    angles=np.degrees(subspace_angles(x,y))
    projector=qx@qx.T-qy@qy.T
    return dict(principal_angles_degrees=angles.tolist(),maximum_angle_degrees=float(angles.max()),
        projector_operator_residual=float(np.linalg.norm(projector,2)),
        projector_Frobenius_residual=float(np.linalg.norm(projector)),
        original_rank=int(np.linalg.matrix_rank(x)),owner_consistent_rank=int(np.linalg.matrix_rank(y)))


def lower_norm(a):
    return str(sum((x*x for x in a.entries()),arb(0)).sqrt().lower().fmpq())


def calculate():
    ctx.prec=512;sources={};r={};a={}
    for name,relative in PACKETS.items():
        directory=ROOT/BASE/relative
        r[name]=json.loads((directory/'report.json').read_bytes())
        for filename in ('report.json','arrays.npz'):
            path=directory/filename;sources[path.relative_to(ROOT).as_posix()]=digest(path)
        if digest(directory/'arrays.npz')!=r[name]['arrays_SHA256']:raise ValueError('frozen packet changed: '+name)
        with np.load(directory/'arrays.npz') as z:a[name]={k:z[k] for k in z.files}
    physical=ROOT/PHYSICAL
    if digest(physical)!=r['binding']['source_SHA256'][str(physical)]:raise ValueError('physical frames changed')
    sources[PHYSICAL.as_posix()]=digest(physical)
    with np.load(physical) as z:B13,B14=map(amat,z['endpoint_physical_tangent_action'][13:15])
    matrix=ROOT/BASE/'gate7_66d_checkpoint_20260926/newton/M_13.npz'
    matrix_report=json.loads(matrix.with_name('report.json').read_bytes())
    if digest(matrix)!=matrix_report['arrays_SHA256']:raise ValueError('M13 changed')
    for p in (matrix,matrix.with_name('report.json'),Path(__file__)):
        sources[p.relative_to(ROOT).as_posix()]=digest(p)
    with np.load(matrix) as z:M=amat(z['M_13'])
    P=amat(a['split']['trial_transform']);Pi=P.inv()
    Pp=block(P,range(74),range(66));Pq=block(P,range(74),range(66,74))
    pp=block(Pi,range(66),range(74));pq=block(Pi,range(66,74),range(74))
    N=amat(a['owner']['left_reduced_block']);n=block(N,range(74),[73])
    delta=amat(a['appended']['left_history_descriptor_adjustment'])
    forcing=Pi*n*delta;mp=Pi*M*P
    Mpp=block(mp,range(66),range(66));Mpq=block(mp,range(66),range(66,74))
    Mqp=block(mp,range(66,74),range(66));Mqq=block(mp,range(66,74),range(66,74))
    fp=block(forcing,range(66),range(66));fq=block(forcing,range(66,74),range(66))
    q_fixed=-Mqq.solve(fq)
    schur=Mpp-Mpq*Mqq.solve(Mqp)
    intrinsic_force=fp-Mpq*Mqq.solve(fq)
    dp=-schur.solve(intrinsic_force)
    dq=-Mqq.solve(fq+Mqp*dp)
    full=-M.solve(n*delta)
    p_component=Pp*dp;q_component=Pq*dq
    raw_error=amat(a['appended']['reaction_fiber_candidate'])-amat(a['appended']['reaction_truth'])
    raw_error_lift=Pq*raw_error
    # Original first-order family and the response enforcing the fiber derivative
    # while preserving its pre-existing shooting derivative residual.
    V0=amat(a['owner']['left_child_history']);V1=amat(a['owner']['right_child_history'])
    V0new=arb_mat(V0.tolist())
    for j in range(66):V0new[73,j]+=delta[0,j]
    V1new=V1+full
    # Build the same declared node-13 split from its already-saved directions.
    left_child=np.vstack((a['binding']['node_013_child_coeff_physical'],np.zeros((1,66))))
    P13=amat(np.column_stack((left_child,a['fiber']['node13_boundary_directions_reduced'],np.eye(74)[:,73])))
    R13=block(P13,range(74),range(66))*block(P13.inv(),range(66),range(74))
    R14=Pp*pp
    def action_state(B,V):return B*block(V,range(73),range(66))
    left0=action_state(B13,R13*V0);left1=action_state(B13,R13*V0new)
    right0=action_state(B14,R14*V1);right1=action_state(B14,R14*V1new)
    paired0=np.vstack((mid(left0),mid(right0)));paired1=np.vstack((mid(left1),mid(right1)))
    endpoint_comparison=comparison(mid(right0),mid(right1))
    paired_comparison=comparison(paired0,paired1)
    pair0=arb_mat(left0.tolist()+right0.tolist());pair1=arb_mat(left1.tolist()+right1.tolist())
    projector0=pair0*(pair0.transpose()*pair0).inv()*pair0.transpose()
    projector1=pair1*(pair1.transpose()*pair1).inv()*pair1.transpose()
    projector_difference=projector1-projector0
    report=dict(
        status='STOP_INTRINSIC_HISTORY_TANGENT_COMPONENT_REMAINS',
        frozen_owner_classification='EULER_DIRAC_DESCRIPTOR_FIBER_OWNER_RECOVERED',
        ownership_and_center_invertibility_preserved=True,center_certificate_promoted=False,
        base_commit='8e52ee75bec0e14cce32f8250dce833fb709291c',source_SHA256=sources,
        metric='Stored positive action norm ||W_state dy_raw||_2. Frames already act in weighted coordinates. Paired history diagnostic uses the direct sum of the two endpoint action norms. H_action defines the oblique complement, not a positive angle metric.',
        decomposition='P=[Pp,Pq], Pi=P^-1, R_p=Pp Pi_p. Use exact inverse of frozen P for algebra; do not replace the action-Hessian boundary complement by an orthogonal one.',
        raw_descriptor_error=r['appended']['descriptor_error'],
        frozen_allowance_exact=r['appended']['descriptor_allowance_exact'],
        raw_norm_excess_diagnostic=r['appended']['descriptor_error']['approximate_upper']-r['appended']['descriptor_allowance_diagnostic'],
        raw_error_lift_intrinsic_residual=bound(pp*raw_error_lift),
        raw_error_lift_vertical_reconstruction=bound(raw_error_lift-Pq*(pq*raw_error_lift)),
        raw_error_scope='The prior replay held right p fixed and changed only Dphi (8x66). Its lift is Pq delta_Dphi by construction. The scalar norm excess is not itself a vector to project.',
        q_only_increment=bound(q_fixed),
        q_only_boundary_increment=bound(block(q_fixed,range(7),range(66))),
        q_only_descriptor_increment=bound(block(q_fixed,[7],range(66))),
        full_response=bound(full),intrinsic_coordinate_response=bound(dp),
        intrinsic_coordinate_response_lower_exact=lower_norm(dp),
        full_reaction_response=bound(dq),
        full_boundary_coordinate_response=bound(block(dq,range(7),range(66))),
        full_descriptor_response=bound(block(dq,[7],range(66))),
        intrinsic_action_response=bound(action_state(B14,p_component)),
        boundary_action_response=bound(action_state(B14,q_component)),
        signed_full_response_decomposition=bound(full-p_component-q_component),
        intrinsic_Schur_forcing=bound(intrinsic_force),intrinsic_Schur_forcing_lower_exact=lower_norm(intrinsic_force),
        Schur_formula='S=Mpp-Mpq Mqq^-1 Mqp; fp_reduced=fp-Mpq Mqq^-1 fq; dp=-S^-1 fp_reduced; dq=-Mqq^-1(fq+Mqp dp)',
        full_linearized_shooting_change=bound(M*full+n*delta),
        fixed_p_q_only_p_equation_residual=bound(fp+Mpq*q_fixed),
        endpoint_reduced_tangent_comparison=endpoint_comparison,
        paired_history_reduced_tangent_comparison=paired_comparison,
        paired_projector_Frobenius_outward=bound(projector_difference),
        paired_projector_Frobenius_lower_exact=lower_norm(projector_difference),
        endpoint_scope='Both reduced right-endpoint bases span Pp after quotienting by Pq; their equal spans do not test the left-to-right history derivative.',
        paired_scope='Compare both endpoint p projections with the same input coordinates. The left projection is unchanged; the right acquires dp. This is a frozen center diagnostic in the product action norm, not a new physical budget norm.',
        left_projected_history_change=bound(left1-left0),right_projected_history_change=bound(right1-right0),
        action_authority='Stage-B state subspace Z with its final normalized seven-row R23 interface, frozen H_T-defined complement L, and Case-B X/B frame bridge. The new fiber derivative still uses diagnostic Dlambda; it is not an outward action-owned 66D history-jet certificate.',
        representation_only_reclassification_allowed=False,
        reason='The q-only error is vertical, but enforcing all shooting derivative rows requires a nonzero intrinsic Schur response. Right-only projector agreement would hide this history component.',
        Layer_C_rebound=False,nonlinear_work_performed=False,scientific_producers_run=False,
        tolerances_changed=False,center_relocated=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    out=dict(p_response=mid(dp),q_response=mid(dq),q_only_response=mid(q_fixed),
        reduced_Schur=mid(schur),intrinsic_forcing=mid(intrinsic_force),full_response=mid(full),
        intrinsic_component=mid(p_component),reaction_component=mid(q_component),
        raw_reaction_error=mid(raw_error),raw_reaction_error_lift=mid(raw_error_lift),
        left_projector=mid(R13),right_projector=mid(R14),
        original_reduced_pair=paired0,owner_consistent_reduced_pair=paired1,
        original_right_history=mid(V1),owner_consistent_right_history=mid(V1new),
        original_left_history=mid(V0),owner_consistent_left_history=mid(V0new))
    return report,out


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();report,arrays=calculate();args.out.mkdir(parents=True,exist_ok=False)
    buffer=io.BytesIO();np.savez_compressed(buffer,**arrays)
    (args.out/'arrays.npz').write_bytes(buffer.getvalue());report['arrays_SHA256']=digest(args.out/'arrays.npz')
    (args.out/'report.json').write_bytes(encoded(report))
    print(report['status']);print(report['paired_history_reduced_tangent_comparison']['maximum_angle_degrees'])


if __name__=='__main__':main()
