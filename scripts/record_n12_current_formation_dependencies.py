"""Numerical endpoint dependency contractions; never a history force solve."""
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb, arb_mat, ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from checkpoint_n12_gate7_66d_tangent_binding import digest,encoded,bound,restore
from differentiate_n12_gate7_fiber_constrained_center import save_arrays
from assemble_n12_current_formation_local_operands import FRAME


def calculate(local,out):
    ctx.prec=512
    local=local.resolve()
    report=json.loads((local/'report.json').read_bytes())
    if digest(local/'arrays.npz')!=report['arrays_SHA256']:
        raise ValueError('current local operands changed')
    with np.load(local/'arrays.npz') as z:
        y=restore(z,'current_incoming_state_raw')
        dx=restore(z,'incoming_log_R4_raw_covector')
        N=restore(z,'incoming_lapse')[0,0]
        rate=restore(z,'incoming_proper_log_radius_rate')[0,0]
    frame_report=json.loads((FRAME/'report.json').read_bytes())
    if digest(FRAME/'arrays.npz')!=frame_report['arrays_SHA256']:
        raise ValueError('frozen formation frame changed')
    with np.load(FRAME/'arrays.npz') as z:Q=restore(z,'Q66_current_raw')
    dlogN=arb_mat(1,98)
    for j in range(12):dlogN[0,74+j]=(-1)**(j+1)
    vb=sum((y[25+j,0]*(-1)**j for j in range(12)),arb(0))
    vdot=sum((y[62+j,0]*(-1)**j for j in range(12)),arb(0))
    t=(2*vb).tanh()
    drate=arb_mat(1,98)
    for i in range(37):drate[0,37+i]=dx[0,i]/N
    for j in range(12):drate[0,25+j]=-2*(1-t*t)*vdot*((-1)**j)/N
    drate-=dlogN*rate
    arrays=dict(endpoint_log_radius_partial_66=dx*Q,
                endpoint_log_lapse_partial_66=dlogN*Q,
                endpoint_proper_radius_rate_partial_66=drate*Q)
    out.mkdir(parents=True,exist_ok=False);save_arrays(out/'arrays.npz',arrays)
    ledger=[
        dict(variable='37 incoming endpoint geometry coordinates',combination='log R4 at the reset',
             status='REDUNDANT',scope='First-order variation on the fixed-child reset-compatible 66D tangent only; follows from the retained trace/attachment rows',
             numerical_replay=bound(arrays['endpoint_log_radius_partial_66'])),
        dict(variable='Incoming coordinate velocities, lapse and geometry',combination='proper radius rate at the endpoint',
             status='SURVIVES',scope='Actual endpoint directional dependence; no full incoming path is inferred from it',
             numerical_replay=bound(arrays['endpoint_proper_radius_rate_partial_66'])),
        dict(variable='Full incoming field history',combination='x(tau)=log R4(tau) and proper durations',
             status='SURVIVES',scope='Sufficient coefficient data for compact fixed-channel scalar/Dirac transfer; not sufficient for the classical attached action'),
        dict(variable='Spatial geometry, eta, fixed inertia, lapse/shift along history',combination='Signed attached-action spatial integrals and Hopf inertia at each history point',
             status='SURVIVES',scope='Classical action still needs finite integration; endpoint density is only a local operand'),
        dict(variable='Descriptor, normalized eigenline, hard response and history internals',combination='Common implicit-history solution and objective adjoint',
             status='SLAVED',scope='Required internal-elimination route; current numerical solve remains uninstantiated'),
        dict(variable='Longitudinal gauge and matching complex ghost modes',combination='Retained graded operator sum',
             status='CANCELS',scope='Existing mode-by-mode BRST identity; transverse gauge, Weyl and HS remain'),
        dict(variable='Independent reset-frame source',combination='Covariant reset transport',
             status='CANCELS',scope='Owned parallel transport identity; physical child/attachment variations remain'),
        dict(variable='Absolute proper-time origin',combination='Intrinsic birth/event labels and duration',
             status='REDUNDANT',scope='Absent from the endpoint-labelled operator representation; does not identify or delete a Q66 column')]
    result=dict(status='CURRENT_ENDPOINT_DEPENDENCY_CONTRACTIONS_EVALUATED',ledger=ledger,
        input_dimension_optimized=False,history_compression_is_sector_specific=True,
        endpoint_data_do_not_determine_the_complete_history_operator=True,
        physical_q66_evaluated=False,physical_H66_evaluated=False,physical_B66x73_evaluated=False,
        source_SHA256={p.relative_to(ROOT).as_posix():digest(p) for p in [Path(__file__),local/'arrays.npz',local/'report.json',FRAME/'arrays.npz',
            ROOT/'src/bhsm/interface/aether_forward_boundary_radius.py',
            ROOT/'src/bhsm/interface/aether_forward_history_weyl_first_jet.py',
            ROOT/'theory/n12_gate7_external_birth_source_role_supersession.md']},
        arrays_SHA256=digest(out/'arrays.npz'))
    (out/'report.json').write_bytes(encoded(result))
    print(json.dumps({name:bound(value)['approximate_upper'] for name,value in arrays.items()},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--local',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();calculate(a.local,a.out)
