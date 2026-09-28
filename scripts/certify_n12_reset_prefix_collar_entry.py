"""Test only the first local portion of the saved nine-step connection guess.

No historical interval action or prefix is regenerated. Failed domain
inclusions are retained as local diagnostics, never physical failure.
"""
import os
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb, arb_mat, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
import solve_n12_gate7_fiber_constrained_center as owner
from build_n12_current_incoming_response import CANDIDATE, POINT
from evaluate_n12_gate7_current_contractions import packet, scalar, BASE
from checkpoint_n12_gate7_66d_tangent_binding import restore, digest, encoded
from certify_n12_gate7_coupled_center_neighborhood import load
from differentiate_n12_gate7_fiber_constrained_center import save_arrays
from recenter_n12_gate7_current_history_box import recentered_eigenline
from bhsm.interface.indexed_eigenpair_proposal import indexed_proposal
from bhsm.interface.physical_hs_value import verified_eigenline
from bhsm.interface.current_action_response_capture import evaluate_shared_rate


def calculate(out, divisor):
    ctx.prec = 512
    if out.exists(): raise ValueError('new output directory required')
    if divisor < 1: raise ValueError('positive subdivision divisor required')
    predictor = BASE/'gate7_current_reset_connection_20260927/arb_predictor'
    record = json.loads((predictor/'report.json').read_bytes())
    if digest(predictor/'path.npz') != record['path_SHA256']:
        raise ValueError('saved connection guess changed')
    boxpath = BASE/'gate7_current_history_20260927/flow_box'
    boxrecord = json.loads((boxpath/'report.json').read_bytes())
    if digest(boxpath/'arrays.npz') != boxrecord['arrays_SHA256']:
        raise ValueError('target prefix domain changed')
    target = load(boxpath/'arrays.npz')
    pr, p = packet(POINT)
    key = CANDIDATE.relative_to(ROOT).as_posix()
    if {k.replace('\\', '/'):v for k,v in pr['source_SHA256'].items()}[key] != digest(CANDIDATE):
        raise ValueError('current selected descriptor uses another reset state')
    with np.load(CANDIDATE) as z:
        raw = [arb(float(v)) for v in z['joint_state_raw'][:98]]
        weights = z['state_weights']; reference = z['branch_reference']
    start = [v*arb(float(w)) for v,w in zip(raw, weights)]
    s0 = restore(p, 'C2_eigenvalue')[0, 0]
    with np.load(predictor/'path.npz') as z:
        difference = z['action_displacement'][-2]-z['action_displacement'][-1]
        fraction = arb(float(z['descriptor_fraction'][-2]))/divisor
    ds = target['center'][98].mid()*fraction
    dy = [arb(float(v))/divisor for v in difference]
    # A symmetric first-exit box avoids assuming component monotonicity.
    radii = [abs(v)*arb('1.25')+arb(2)**-90 for v in dy]
    action_box = [v+arb(0, r.upper()) for v,r in zip(start, radii)]
    raw_box = np.array([v/arb(float(w)) for v,w in zip(action_box, weights)], dtype=object)
    sbox = s0+ds/2+arb(0,(ds/2).upper())
    checks = []; A=owner.action; original=A._eigenline
    def proposal(h, mid, ref): return indexed_proposal(h[37:,37:], 24, ref)
    A._eigenline = recentered_eigenline(proposal)
    arrays = dict(initial_action=arb_mat(99,1,start+[s0]),
        state_domain=arb_mat(98,1,action_box), descriptor_domain=arb_mat([[sbox]]),
        target_prefix_domain=arb_mat(99,1,list(target['domain'])))
    report = dict(status='LOCAL_COLLAR_ENTRY_ATTEMPT', divisor=divisor,
        initial_descriptor=scalar(s0), descriptor_increment=scalar(ds),
        predictor_steps_reused=9, prefix_cells_rebuilt=0,
        certificate_tolerances_changed=False, physical_failure_claim=False,
        Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    failures = [i for i in range(99) if not target['domain'][i].contains((start+[s0])[i])]
    report['initial_target_domain_failures'] = failures
    report['first_initial_failure'] = dict(coordinate=failures[0],
        displacement=scalar(start[failures[0]]-target['center'][failures[0]]),
        target_radius=scalar(target['domain'][failures[0]].rad())) if failures else None
    print('Testing first fixed-s collar segment, subdivision', divisor, flush=True)
    try:
        with owner.sparse.use_optimized_mixed(A), owner.factored.use_ball_factored_integrand(A,raw_box):
            with verified_eigenline(A,checks,expected_index=24,normalize_proposal_center=True):
                rate, internal=evaluate_shared_rate(A,raw_box,sbox,weights,reference,None)
        if not rate.value[98]>0: raise ArithmeticError('descriptor speed does not exclude zero')
        fs=[rate.value[i]/rate.value[98] for i in range(98)]
        excursions=[(abs(ds)*abs(v).upper()/r).upper() for v,r in zip(fs,radii)]
        report['first_exit_ratios']=[float(v) for v in excursions]
        failed=[i for i,v in enumerate(excursions) if not v<1]
        if failed:
            report.update(status='LOCAL_COLLAR_FIRST_EXIT_INCLUSION_FAILED',first_failing_coordinate=failed[0])
        else:
            endpoint=[start[i]+ds*fs[i] for i in range(98)]+[s0+ds]
            arrays['endpoint_action']=arb_mat(99,1,endpoint)
            report.update(status='FIRST_LOCAL_COLLAR_SEGMENT_ENCLOSED',
                endpoint_in_target_domain=all(target['domain'][i].contains(endpoint[i]) for i in range(99)),
                first_variation_transported=False,
                positive_operator_history_certified=False)
        arrays['augmented_rate_domain']=arb_mat(99,1,list(rate.value))
        report['eigenpair_proof']=checks[0]
    except (ArithmeticError,ValueError,ZeroDivisionError) as error:
        report.update(status='LOCAL_COLLAR_FIELD_CHART_FAILED',first_failing_operand='normalized selected-line / bordered rate domain',
            error_type=type(error).__name__,error=str(error))
    finally: A._eigenline=original
    sources=[Path(__file__),CANDIDATE,POINT/'arrays.npz',POINT/'report.json',
        predictor/'path.npz',predictor/'report.json',boxpath/'arrays.npz',boxpath/'report.json',Path(A.__file__)]
    out.mkdir(parents=True);save_arrays(out/'arrays.npz',arrays)
    report.update(source_SHA256={v.relative_to(ROOT).as_posix():digest(v) for v in sources},arrays_SHA256=digest(out/'arrays.npz'))
    (out/'report.json').write_bytes(encoded(report));p.close()
    print(report['status'],report.get('error',report.get('first_failing_coordinate')),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--divisor',type=int,default=1024)
    a=parser.parse_args();calculate(a.out,a.divisor)
