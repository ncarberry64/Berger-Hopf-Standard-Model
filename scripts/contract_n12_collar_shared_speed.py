"""Shared-parameter descriptor speed on the frozen first collar predictor.

This encloses the action on an affine predictor, not the implicit normal
graph or the actual orbit. No prefix actions or physical direction columns
are generated. The stored normal Jacobian recovers its own psi/hard/b center.
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
from build_n12_current_incoming_response import CANDIDATE
from evaluate_n12_gate7_current_contractions import packet, scalar
from checkpoint_n12_gate7_66d_tangent_binding import restore, digest, encoded, bound
from differentiate_n12_gate7_fiber_constrained_center import save_arrays
from bhsm.interface.shared_action_taylor import TaylorDomain, scalar_taylor_action

JET = ROOT/'artifacts/flagship_integration/reset_prefix_collar_20260928/directional1'


def normal_center(jacobian, descriptor):
    """Invert only the declared block layout, without a new eigenvalue solve."""
    if (jacobian.nrows(), jacobian.ncols()) != (124, 124):
        raise ValueError('the frozen 61+1+61+1 normal system is required')
    psi = [jacobian[61, i] for i in range(61)]
    hard = [jacobian[123, i] for i in range(61)]
    b = jacobian[62, 0]
    if any(not (jacobian[62+i, i]-b).contains(0) for i in range(61)):
        raise ValueError('normal b block layout changed')
    if any(not (jacobian[i, 61]+psi[i]).contains(0) for i in range(61)):
        raise ValueError('normal selected-line block layout changed')
    if any(not (jacobian[62+i, 61]+hard[i]).contains(0) for i in range(61)):
        raise ValueError('normal hard-response block layout changed')
    return psi+[descriptor]+hard+[b]


def coefficient_packet(model):
    return arb_mat([[model.c, model.a[0, 0], model.r]])


def shared_speed(A, y, n, s, weights, maps):
    """Same owner contractions, including moving legs and common normalization."""
    domain = y[0].domain
    qw, rw, _, _ = A.metric_data()
    qw, rw = [[arb(float(v)) for v in a] for a in (qw, rw)]
    psi, hard, b = n[:61], n[62:123], n[123]
    p = [domain.affine(0)]*37+psi
    config = [qw[i]*y[37+i] for i in range(37)]
    da = [domain.affine(0)]*37+[rw[i]*psi[i]/weights[37+i] for i in range(61)]
    dh = [config[i]/weights[i] for i in range(37)]+[rw[i]*hard[i]/weights[37+i] for i in range(61)]
    with scalar_taylor_action(A):
        c = A._contracted_action(y, [p, p, da], maps)
        R = A._contracted_action(y, [p, p, dh], maps)
    delta = b*c+s*R
    G = [s*v for v in config]+[rw[i]*(b*psi[i]+s*hard[i]) for i in range(61)]
    norm2 = sum((v*v for v in G), domain.affine(0))
    norm = (norm2.log()/2).exp()
    return dict(c=c, R=R, b=b, delta=delta, norm=norm, speed=delta/norm)


def calculate(out, exponents):
    ctx.prec = 512
    if out.exists():
        raise ValueError('new output directory required')
    report, data = packet(JET)
    sources = {k.replace('\\', '/'): v for k, v in report['source_SHA256'].items()}
    if sources[CANDIDATE.relative_to(ROOT).as_posix()] != digest(CANDIDATE):
        raise ValueError('frozen current-reset binding changed')
    A = owner.action
    if sources[Path(A.__file__).relative_to(ROOT).as_posix()] != digest(Path(A.__file__)):
        raise ValueError('frozen action owner changed')
    with np.load(CANDIDATE) as z:
        state = [arb(float(v)) for v in z['joint_state_raw'][:98]]
        weights = [arb(float(v)) for v in z['state_weights']]
    U = restore(data, 'fixed_s_direction')
    Dn = restore(data, 'local_internal_first')
    s0 = restore(data, 'current_descriptor')[0, 0]
    n0 = normal_center(restore(data, 'local_internal_jacobian'), s0)
    truth = restore(data, 'internal_scalar_first')
    maps = [A._dense_mapping(A._integrand(state, node, 0).maps) for node in range(A.POINTS)]
    arrays = dict(recovered_internal_center=arb_mat(124, 1, n0))
    results = []
    for exponent in exponents:
        h = arb(2)**(-exponent)
        domain = TaylorDomain([(0, 1, 'interval')], 1)
        y = [domain.affine(v, [U[i, 0]*h/weights[i]]) for i, v in enumerate(state)]
        n = [domain.affine(v, [Dn[i, 0]*h]) for i, v in enumerate(n0)]
        s = domain.affine(s0, [h])
        models = shared_speed(A, y, n, s, weights, maps)
        delta, speed = models['delta'], models['speed']
        first_replay = arb_mat(4, 1, [models[k].a[0, 0]/h-truth[i, 0]
                                    for i, k in enumerate(('c', 'R', 'b', 'delta'))])
        value_replay = arb_mat([[speed.c-restore(data, 'augmented_rate')[98, 0]]])
        speed_first_replay = arb_mat([[speed.a[0, 0]/h-restore(data, 'rate_directional_first')[98, 0]]])
        if not all(v.contains(0) for m in (first_replay, value_replay, speed_first_replay) for v in m.entries()):
            raise ArithmeticError('shared predictor differs from frozen directional owner')
        prefix = 'h2m'+str(exponent)
        for name, model in models.items():
            arrays[prefix+'_'+name] = coefficient_packet(model)
        arrays[prefix+'_first_replay'] = first_replay
        arrays[prefix+'_speed_value_replay'] = value_replay
        arrays[prefix+'_speed_first_replay'] = speed_first_replay
        item = dict(step=scalar(h), exponent=exponent,
                    delta=scalar(delta.enclosure()), speed=scalar(speed.enclosure()),
                    speed_constant=scalar(speed.c), speed_linear=scalar(speed.a[0, 0]),
                    speed_remainder=scalar(speed.r),
                    affine_predictor_speed_positive=bool(speed.enclosure()>0),
                    first_replay=bound(first_replay), speed_first_replay=bound(speed_first_replay))
        results.append(item)
        print(json.dumps({k: item[k] for k in ('exponent', 'affine_predictor_speed_positive', 'speed_remainder')}), flush=True)
    out.mkdir(parents=True)
    save_arrays(out/'arrays.npz', arrays)
    source_files = [Path(__file__), CANDIDATE, JET/'arrays.npz', JET/'report.json', Path(A.__file__),
                    ROOT/'src/bhsm/interface/shared_action_taylor.py',
                    ROOT/'src/bhsm/interface/shared_parameter_residual.py',
                    ROOT/'src/bhsm/interface/current_incoming_formation_family.py']
    output = dict(status='CURRENT_RESET_SHARED_AFFINE_PREDICTOR_SPEED_EVALUATED',
                  parameter='one common theta in [-1,1]; s=s0+h*theta',
                  coefficient_columns=['constant', 'signed_linear', 'absolute_remainder'],
                  results=results, actual_normal_graph_included=False,
                  actual_flow_tube_included=False, prefix_overlap_certified=False,
                  physical_direction_columns_generated=0, prefix_cells_rebuilt=0,
                  next_required='Include the implicit normal and flow remainders on this common parameter domain',
                  source_SHA256={p.relative_to(ROOT).as_posix(): digest(p) for p in source_files},
                  arrays_SHA256=digest(out/'arrays.npz'), Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    (out/'report.json').write_bytes(encoded(output))
    data.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--exponents', nargs='+', type=int, default=[45, 55, 65])
    args = parser.parse_args()
    calculate(args.out, args.exponents)
