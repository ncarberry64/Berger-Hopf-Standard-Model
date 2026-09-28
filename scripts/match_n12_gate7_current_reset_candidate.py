"""Match a new outgoing reset guess in the existing 72+58 proof section.

Numerical initial guess only. Historical Jacobians are preconditioners, never
current physical authority. The 66 omitted reset-kernel directions are fixed
only to choose this old proof section, not declared physically slaved.
"""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from checkpoint_n12_gate7_66d_tangent_binding import digest,encoded
from certify_n12_gate7_coupled_center_neighborhood import load
from audit_n12_finite_terminal_directed_center import _normalization_coordinates
from certify_n12_c2_refined_reset_root_center import _augmented_residual

BASE=ROOT/'artifacts/flagship_integration'


def calculate(predictor,out,max_steps):
    predictor=Path(predictor).resolve();out=Path(out).resolve()
    record=json.loads((predictor/'report.json').read_bytes())
    if not record['reached_descriptor_zero']:
        raise ValueError('completed outgoing reset predictor required')
    if digest(predictor/'endpoint.npz')!=record['endpoint_SHA256']:
        raise ValueError('predictor endpoint changed')
    endpoint=load(predictor/'endpoint.npz')['endpoint_action']
    target=np.array([float(v.mid()) for v in endpoint])
    domain=BASE/'BHSM_N12_GATE7_COMPACT_RESET_QUOTIENT_DOMAIN.npz'
    directed=BASE/'BHSM_N12_FINITE_TERMINAL_DIRECTED_CENTER_DATA.npz'
    checkpoint=BASE/'BHSM_N12_FINITE_TERMINAL_CERTIFICATE_CHECKPOINT.npz'
    refined=BASE/'BHSM_N12_C2_REFINED_RESET_ROOT_CENTER.npz'
    residual_record=ROOT/'artifacts/n12_direct_checkpoint/BHSM_N12_EXACT_ROOT_RESIDUAL.json'
    with np.load(domain) as z:
        center=z['proof_center'];weights=z['state_weights']
        tangent=z['reset_quotient_parameter_lift'];normal=z['terminal_reset_normal_basis']
    with np.load(directed) as z:child_scale=float(z['child_gradient_scale'])
    with np.load(checkpoint) as z:old_J=z['paired_jacobian']
    with np.load(refined) as z:reference=z['branch_reference']
    ordered_scale=json.loads(residual_record.read_bytes())['ordered_scale']
    normalization=_normalization_coordinates();W=np.tile(weights,2)
    basis=np.column_stack((tangent,normal));Q=np.linalg.qr(tangent[:98],mode='reduced')[0]
    old_A=np.vstack((old_J@basis,Q.T@basis[:98]))
    inverse=np.linalg.inv(old_A)
    displacement=target-center[:98]*weights
    z=np.r_[np.linalg.lstsq(tangent[:98],displacement,rcond=None)[0],np.zeros(58)]
    def evaluate(coordinates):
        state=center+(basis@coordinates)/W
        reset=_augmented_residual(state,weights,reference,float(ordered_scale),normalization,child_scale)
        matching=Q.T@(state[:98]*weights-target)
        return np.r_[reset,matching],state
    residual,state=evaluate(z);records=[];failure=None
    for step in range(max_steps):
        correction=inverse@residual
        records.append([step,np.linalg.norm(residual),np.linalg.norm(correction)])
        print('current reset guess iteration',step,'residual',records[-1][1],
              'preconditioned correction',records[-1][2],flush=True)
        if np.linalg.norm(correction)<1e-10:break
        accepted=False
        for power in range(7):
            dz=-correction/(2**power)
            candidate=z+dz;rr,ss=evaluate(candidate)
            if np.linalg.norm(inverse@rr)<np.linalg.norm(correction):
                dy=rr-residual;Hd=inverse@dy
                denominator=float(dz@Hd)
                if abs(denominator)>np.finfo(float).tiny:
                    inverse+=np.outer(dz-Hd,dz@inverse)/denominator
                z,residual,state=candidate,rr,ss;accepted=True;break
        if not accepted:
            failure='NUMERICAL_CHORD_STEP_NOT_DECREASED';break
    else:failure='NUMERICAL_RESET_ITERATION_LIMIT'
    full_match=state[:98]*weights-target
    out.mkdir(parents=True,exist_ok=False)
    np.savez_compressed(out/'candidate.npz',joint_state_raw=state,coordinates=z,
        residual=residual,outgoing_match_action=full_match,iteration_log=np.array(records),
        state_weights=weights,branch_reference=reference)
    report=dict(status='CURRENT_NONLINEAR_RESET_PROOF_SECTION_GUESS_ONLY',failure=failure,
        preconditioned_correction_norm=float(np.linalg.norm(inverse@residual)),
        complete_residual_norm=float(np.linalg.norm(residual)),
        full_outgoing_match_norm=float(np.linalg.norm(full_match)),
        forward_order='C2=old event half [0:98]; E1=incoming parent=old child half [98:196]',
        state_role='Existing proof-section initial guess; not a physically selected or certified reset member',
        current_reset_member_certified=False,hidden_upstream_kernel_slaved=False,
        incoming_parent_history_certified=False,first_73_jet_certified=False,
        source_SHA256={str(p.relative_to(ROOT)):digest(p) for p in [domain,directed,checkpoint,refined,
            residual_record,predictor/'report.json',predictor/'endpoint.npz',Path(__file__)]},
        candidate_SHA256=digest(out/'candidate.npz'),Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    (out/'report.json').write_bytes(encoded(report))
    print(json.dumps({k:report[k] for k in ('failure','preconditioned_correction_norm',
        'complete_residual_norm','full_outgoing_match_norm')},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--predictor',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--max-steps',type=int,default=8)
    a=p.parse_args();calculate(a.predictor,a.out,a.max_steps)
