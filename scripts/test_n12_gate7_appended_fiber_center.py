"""Append the recovered fiber row to the frozen center linearization only.

Retain its nonzero constant residual and the failed descriptor reaction replay.
No scientific action producers, recentering, or nonlinear proof are performed.
"""
import argparse
import io
import json
from pathlib import Path

import numpy as np
from flint import arb, arb_mat, ctx

from checkpoint_n12_gate7_66d_tangent_binding import ROOT, BASE, amat, mid, bound, digest, encoded
from diagnose_n12_gate7_eight_reaction_center import block, identity

PACKETS = {
    'fiber':'gate7_descriptor_fiber_owner_20260926',
    'local':'gate7_local_child_flow_dimension_20260926',
    'owner':'gate7_full_shooting_owner_20260926',
    'split':'gate7_8reaction_center_20260926',
    'binding':'gate7_66d_checkpoint_20260926/binding',
}


def calculate():
    ctx.prec=512
    sources={};reports={};arrays={}
    for name,relative in PACKETS.items():
        directory=ROOT/BASE/relative
        report=json.loads((directory/'report.json').read_bytes())
        for filename in ('report.json','arrays.npz'):
            path=directory/filename;sources[path.relative_to(ROOT).as_posix()]=digest(path)
        if digest(directory/'arrays.npz')!=report['arrays_SHA256']:raise ValueError('changed frozen '+name)
        reports[name]=report
        with np.load(directory/'arrays.npz') as z:arrays[name]={key:z[key] for key in z.files}
    sources[Path(__file__).relative_to(ROOT).as_posix()]=digest(Path(__file__))
    if reports['fiber']['descriptor_identity']!='SAME_EULER_DIRAC_DESCRIPTOR_PROVED':
        raise ValueError('DESCRIPTOR_IDENTITY_UNPROVEN')
    K=arrays['local']['K_cut']
    # p fixed => left state fixed, so the existing fiber contributes only -ds.
    # The row is R_fiber/1e-7, while the first 74 rows retain their old scaling.
    A=np.vstack((K,np.r_[-1.,np.zeros(74)]))
    aA=amat(A);inverse=aA.inv();inverse_proposal=amat(mid(inverse))
    left=bound(identity(75)-inverse_proposal*aA)
    right=bound(identity(75)-aA*inverse_proposal)
    if not (arb(left['exact_upper'])<1 and arb(right['exact_upper'])<1):
        raise ValueError('appended stored matrix inverse not certified')
    singular=np.linalg.svd(A,compute_uv=False)
    M=amat(K[:,1:]);n=amat(K[:,0:1])
    split=arrays['split'];owner=arrays['owner'];binding=arrays['binding']
    P=amat(split['trial_transform']);Pi=amat(split['trial_transform_inverse'])
    Q=amat(split['M_qq']);Qinv=amat(split['M_qq_inverse'])
    Pi_q=block(Pi,range(66,74),range(74));Pq=block(P,range(74),range(66,74))
    # Reaction block in the (left descriptor, right 8 reactions) coordinates.
    # The upper right zero is structural, not a discarded forcing derivative.
    q_actual=Pi_q*M*Pq
    reaction9=arb_mat(9,9)
    reaction9[0,0]=-1
    nq=Pi_q*n
    for i in range(8):
        reaction9[i+1,0]=nq[i,0]
        for j in range(8):reaction9[i+1,j+1]=q_actual[i,j]
    schur=q_actual  # q_actual - nq*(-1)^-1*0
    schur_defect=bound(schur-Q)
    # Physical eigenvalue covector is only a stored diagnostic first derivative.
    fiber_row=amat(arrays['fiber']['fiber_row_reduced_proof_diagnostic'][None,:])
    V0=amat(owner['left_child_history'])
    delta=fiber_row*V0
    Vnew=arb_mat(V0.tolist())
    for j in range(66):Vnew[73,j]=Vnew[73,j]+delta[0,j]
    delta_forcing=nq*delta
    F0=amat(owner['forcing_total']);Fnew=F0+delta_forcing
    D0=amat(owner['Dphi_total'])
    Dnew=-Qinv*Fnew
    truth=amat(owner['Dphi_truth']);error=Dnew-truth
    descriptor_error=bound(block(error,[7],range(66)))
    descriptor_norm=sum((error[7,j]**2 for j in range(66)),arb(0)).sqrt()
    allowance=arb(reports['owner']['descriptor_frozen_allowance'])
    boundary=[]
    for i,old in enumerate(reports['owner']['boundary_rows']):
        err=bound(block(error,[i],range(66)))
        allowed=arb(old['allowance_upper'])
        boundary.append(dict(channel=old['channel'],error=err,allowance_exact=old['allowance_upper'],
                             allowance_diagnostic=float(allowed),passes=bool(arb(err['exact_upper'])<=allowed)))
    C13=amat(binding['node_013_child_augmented'])
    child_defect=fiber_row*C13
    nnull=aA*amat(arrays['local']['null_vector'][:,None])
    out=dict(appended_matrix=A,inverse_proposal=mid(inverse_proposal),reaction9=mid(reaction9),
        recovered_Schur8=mid(schur),signed_Schur8_defect=mid(schur-Q),
        left_history_old=mid(V0),left_history_fiber_candidate=mid(Vnew),
        left_history_descriptor_adjustment=mid(delta),forcing_old=mid(F0),
        forcing_adjustment=mid(delta_forcing),forcing_fiber_candidate=mid(Fnew),
        reaction_old=mid(D0),reaction_fiber_candidate=mid(Dnew),reaction_truth=mid(truth),
        reaction_error=mid(error),child_fiber_row_defect=mid(child_defect),old_null_image=mid(nnull))
    report=dict(classification='EULER_DIRAC_DESCRIPTOR_FIBER_OWNER_RECOVERED',
        classification_scope='Existing scalar functional and appended linearized row only; the enlarged physical center certificate DOES NOT PASS.',
        center_adjudication='FAIL_FROZEN_FIBER_VALUE_AND_DESCRIPTOR_REACTION_REPLAY',
        base_commit='b4c091f6aff19315039150dc1756c6f5f43e40c5',source_SHA256=sources,
        descriptor_identity=reports['fiber']['descriptor_identity'],
        frozen_fiber_value=reports['fiber']['node13']['residual_physical'],
        frozen_fiber_value_proof=reports['fiber']['node13']['residual_proof'],
        exact_center_on_fiber=False,constant_residual_discarded=False,
        matrix_formula='A75=[[N13 e_s,M13],[-1,0_1x74]], last row R_fiber/1e-7, original first 74 row scales unchanged',
        shape=list(A.shape),numerical_rank=int(np.linalg.matrix_rank(A)),stored_coefficient_rank_certified=75,
        sigma_min_diagnostic=float(singular[-1]),sigma_max_diagnostic=float(singular[0]),
        condition_2_diagnostic=float(singular[0]/singular[-1]),inverse_left_defect=left,inverse_right_defect=right,
        null_eliminated=True,unit_null_fiber_action=reports['fiber']['covector']['null_proof_midpoint'],
        Schur_formula='Eliminate s13 from [[-1,0],[Pi_q N13 e_s,Pi_q M13 P_q]]; Schur8=Pi_q M13 P_q.',
        Schur8_replay_defect=schur_defect,
        Schur_scope='Recover the frozen block with its retained stored-transform rounding defect; do not equate its entries bitwise.',
        state_child_basis_unchanged=True,boundary_complement_unchanged=True,
        augmented_child_tangent_exactly_unchanged=False,child_fiber_defect=bound(child_defect),
        child_tangent_scope='State basis and dimension remain 66; its stored descriptor graph is not exactly tangent to the fiber. No rigorous gradient uncertainty has been added.',
        history_descriptor_adjustment=bound(delta),
        forcing_formula='Vnew=V0+e_s*(fiber_row V0); Fnew=F0+Pi_q N13 e_s*(fiber_row V0); Dnew=-Q_frozen_inverse Fnew',
        original_reaction_replay=bound(-Qinv*F0-D0),
        new_reaction_equation_defect=bound(Q*Dnew+Fnew),
        descriptor_error=descriptor_error,descriptor_allowance_exact=reports['owner']['descriptor_frozen_allowance'],
        descriptor_error_lower_exact=str(descriptor_norm.lower().fmpq()),
        descriptor_error_exceeds_allowance=bool(descriptor_norm>allowance),
        descriptor_allowance_diagnostic=float(allowance),
        descriptor_replay_passes=bool(arb(descriptor_error['exact_upper'])<=allowance),boundary_rows=boundary,
        complete_reaction_replay_passes=bool(arb(descriptor_error['exact_upper'])<=allowance and all(v['passes'] for v in boundary)),
        source_scope='Arb certifies operations on stored coefficients. Diagnostic eigenvalue-gradient error is not promoted to an outward physical derivative enclosure.',
        recentered=False,old_8x8_modified=False,tolerances_changed=False,
        scientific_producers_run=False,nonlinear_work_performed=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    return report,out


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();report,arrays=calculate();args.out.mkdir(parents=True,exist_ok=False)
    buffer=io.BytesIO();np.savez_compressed(buffer,**arrays)
    (args.out/'arrays.npz').write_bytes(buffer.getvalue());report['arrays_SHA256']=digest(args.out/'arrays.npz')
    (args.out/'report.json').write_bytes(encoded(report))
    print(report['classification']);print(report['center_adjudication'])
    print('condition',report['condition_2_diagnostic'],'descriptor error',report['descriptor_error']['approximate_upper'])


if __name__=='__main__':main()
