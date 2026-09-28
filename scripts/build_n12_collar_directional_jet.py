"""One current fixed-descriptor directional jet for local collar refinement."""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb, arb_mat, ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import solve_n12_gate7_fiber_constrained_center as owner
from build_n12_current_incoming_response import CANDIDATE,POINT
from evaluate_n12_gate7_current_contractions import packet,scalar
from checkpoint_n12_gate7_66d_tangent_binding import restore,bound,digest,encoded
from differentiate_n12_gate7_fiber_constrained_center import save_arrays
from recenter_n12_gate7_current_history_box import recentered_eigenline
from bhsm.interface.indexed_eigenpair_proposal import indexed_proposal
from bhsm.interface.physical_hs_value import verified_eigenline
from bhsm.interface.current_action_response_capture import evaluate_shared_rate
from bhsm.interface.current_incoming_formation_family import local_internal_system


def calculate(out):
    ctx.prec=512
    if out.exists():raise ValueError('new output directory required')
    pr,p=packet(POINT)
    key=CANDIDATE.relative_to(ROOT).as_posix()
    if {k.replace('\\','/'):v for k,v in pr['source_SHA256'].items()}[key]!=digest(CANDIDATE):
        raise ValueError('current reset/selected-line binding failed')
    with np.load(CANDIDATE) as z:
        state=np.array([arb(float(v)) for v in z['joint_state_raw'][:98]],dtype=object)
        weights=z['state_weights'];reference=z['branch_reference']
    s=restore(p,'C2_eigenvalue')[0,0]
    A=owner.action;original=A._eigenline;checks=[]
    def proposal(h,mid,ref):return indexed_proposal(h[37:,37:],24,ref)
    A._eigenline=recentered_eigenline(proposal)
    try:
        with owner.sparse.use_optimized_mixed(A),owner.factored.use_ball_factored_integrand(A,state):
            with verified_eigenline(A,checks,expected_index=24,normalize_proposal_center=True):
                base,internal=evaluate_shared_rate(A,state,s,weights,reference,None)
                speed=base.value[98]
                if not speed>0:raise ArithmeticError('positive current fixed-s chart required')
                direction=np.array(list(base.value[:98]/speed)+[arb(1)],dtype=object)[:,None]
                differentiated,shared=evaluate_shared_rate(A,state,s,weights,reference,direction)
    finally:A._eigenline=original
    system=local_internal_system(shared)
    d=arb_mat(differentiated.derivative.tolist())
    velocity=arb_mat(99,1,list(base.value))
    D=arb_mat(direction.tolist())
    curvature=(d-D*d[98,0])/speed
    eigen_replay=arb_mat([[shared['eigenvalue']-s]])
    fiber_first=arb_mat([[shared['deigenvalue'][0]-1]])
    replays=dict(selected_eigenvalue=eigen_replay,selected_fiber_tangent=fiber_first,
        normal=system['residual'],normal_first=system['first_replay'],
        rate=arb_mat(99,1,list(differentiated.value))-velocity)
    if not all(v.contains(0) for m in replays.values() for v in m.entries()):
        raise ArithmeticError('current directional shared-owner replay failed')
    arrays=dict(current_descriptor=arb_mat([[s]]),augmented_rate=velocity,
        fixed_s_direction=D,rate_directional_first=d,fixed_s_curve_second=curvature,
        internal_scalar_first=arb_mat(shared['scalar_first_dc_dR_db_ddelta'].tolist()),
        local_internal_first=system['internal_first'],local_internal_jacobian=system['internal_jacobian'],
        local_internal_input_partial=system['input_partial'],
        **{'replay_'+k:v for k,v in replays.items()})
    out.mkdir(parents=True);save_arrays(out/'arrays.npz',arrays)
    sources=[Path(__file__),CANDIDATE,POINT/'arrays.npz',POINT/'report.json',Path(A.__file__),
        ROOT/'src/bhsm/interface/current_action_response_capture.py',ROOT/'src/bhsm/interface/current_incoming_formation_family.py']
    report=dict(status='CURRENT_RESET_FIXED_S_COLLAR_DIRECTIONAL_JET_EVALUATED',
        current_descriptor=scalar(s),descriptor_speed=scalar(speed),
        descriptor_speed_derivative_along_s=scalar(d[98,0]),
        first_direction=bound(D),second_curve_direction=bound(curvature),
        replays={k:bound(v) for k,v in replays.items()},
        physical_direction_columns_generated=0,local_proof_direction_columns=1,
        point_jet_only=True,uniform_correlated_remainder=None,
        prefix_overlap_certified=False,negative_initial_descriptor_preserved=True,
        existing_obligation='Same-base reset-to-prefix collar for the joint force contraction',
        next_use='Correlated fixed-s Taylor tube; do not promote a point second jet to a uniform error',
        source_SHA256={v.relative_to(ROOT).as_posix():digest(v) for v in sources},
        arrays_SHA256=digest(out/'arrays.npz'),Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    (out/'report.json').write_bytes(encoded(report));p.close()
    print(json.dumps({k:report[k] for k in ('status','descriptor_speed','descriptor_speed_derivative_along_s','second_curve_direction')},indent=2),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);calculate(p.parse_args().out)
