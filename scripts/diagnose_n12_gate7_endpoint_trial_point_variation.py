"""Verify trial-action samples at +/- three quarters of the endpoint tube axis."""
import os
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import json
from pathlib import Path
import numpy as np
from flint import arb, ctx
import diagnose_n12_gate7_directed_trial_hs_column as base
from bhsm.interface import verified_point_variation as variation

p = base.p
ALGORITHM = 'VERIFIED_ENDPOINT_TRIAL_POINT_VARIATION_ARB512_V1'
THEORY = base.ROOT/'theory/n12_gate7_endpoint_trial_point_variation.md'


def evaluate(args):
    index = args.interval + (args.side == 'right')
    local = base.reader.load_inputs(args.interval)
    engine, source, old_df, selections = base.load_stage(index, 'endpoint', args.primal_pair)
    record, reference_arrays, files = base.read_pair(args.evidence_root/('endpoint_'+args.side))
    base.validate_directed(record, 'endpoint', args.side, args)
    for key, value in source['binding'].items():
        if key == 'files':
            if any(record['binding']['files'].get(name) != digest for name, digest in value.items()):
                raise ValueError('point probe must use the identical paired endpoint inputs')
        elif record['binding'].get(key) != value:
            raise ValueError('endpoint comparison geometry changed: '+key)
    p.geometry.residual.merge(source['binding']['files'], record['binding']['files'])
    p.geometry.residual.merge(source['binding']['files'], local['binding']['files'])
    base.bind(source, *files, Path(__file__), Path(variation.__file__), THEORY,
              Path(base.__file__), Path(base.directed.__file__))
    trial = np.array([[arb(float(v))] for v in local['trial_'+args.side][:, args.column]], dtype=object)
    if not all(a == b for a, b in zip(trial.flat, reference_arrays['trial'].flat, strict=True)):
        raise ValueError('same exact frozen trial column required')
    _, weights, descriptors, reference, _ = p.values.operands()
    tube = source['tube']
    parameter = arb(args.multiplier)/4
    displacement = tube['raw_longitudinal_direction']*tube['radius_longitudinal']*parameter
    raw_point = np.concatenate((source['paired']['center'].copy(), [arb(float(descriptors[index]))])) + displacement
    if raw_point.shape != (99,) or not all(a.contains(b) for a, b in zip(source['raw_domain'], raw_point, strict=True)):
        raise ArithmeticError('outward point construction must lie in the existing physical domain')
    cert = p.values.cert
    original_solve = cert._verified_solve
    solutions, checks = [], []

    def capture(matrix, rhs):
        result = original_solve(matrix, rhs)
        solutions.append(np.array(result.entries(), dtype=object).reshape(result.nrows(), result.ncols()))
        return result

    p.verify_sources(source['binding'])
    try:
        cert._verified_solve = capture
        with p.df.sparse.use_optimized_mixed(cert), base.directed.use_ball_factored_integrand(cert, raw_point[:98]):
            with p.hs.verified_eigenline(cert, checks, expected_index=24, normalize_proposal_center=True):
                result = cert._rate_enclosure(raw_point[:98], raw_point[98], weights, reference, trial)
    finally:
        cert._verified_solve = original_solve
    if (len(checks) != 1 or not p.proof_valid(checks[0]) or len(solutions) != 3
            or any(v.shape != (62, 1) for v in solutions) or result.derivative.shape != (99, 1)):
        raise ArithmeticError('complete verified physical point graph and all three solves required')
    psi = p.hs.restore_balls(np.array(checks[0]['target_midpoints_rational']),
                             np.array(checks[0]['target_radii_rational']))
    if psi.shape != (62,) or not all(a.contains(b) for a, b in zip(source['paired']['eigenbox'], psi, strict=True)):
        raise ArithmeticError('displaced point eigenpair must belong to the paired normalized branch')
    if not all(a.contains(b) for a, b in zip(source['response'], solutions[0][:, 0], strict=True)):
        raise ArithmeticError('displaced response must belong to the exact paired primal family')
    uniform = reference_arrays['selected']
    if not all(a.contains(b) for a, b in zip(uniform.flat, result.derivative.flat, strict=True)):
        raise ArithmeticError('paired uniform directional action must contain the displaced point action')
    anchor = reference_arrays['point_derivative']
    difference, lower = variation.difference_lower_bounds(result.derivative, anchor)
    row = max(range(99), key=lambda i: lower[i, 0])
    arrays = dict(raw_point=raw_point, raw_displacement=displacement, trial=trial,
        point_derivative=result.derivative, anchor_derivative=anchor, point_field=result.value,
        difference_from_anchor=difference, absolute_difference_lower_bound=lower,
        point_eigenpair=psi, point_response=solutions[0], uniform_action=uniform)
    report = dict(verified_point_eigenpair_checks=checks, paired_branch_containment=True,
        paired_primal_response_containment=True, paired_uniform_action_containment=True,
        complete_original_point_graph=True, verified_linear_solves=3,
        longitudinal_parameter_rational=str(parameter.fmpq()), all_transverse_parameters_zero=True,
        outward_construction_rounding_retained=True, exact_baseline_primal_selection=selections,
        largest_proven_difference_row=row,
        maximum_absolute_difference_lower_rational=str(lower[row, 0].fmpq()),
        necessary_single_coordinate_radius_lower_approx=float(lower[row, 0]/2),
        maximum_absolute_difference_upper_approx=float(max(abs(v).upper() for v in difference.flat)),
        uniform_action_maximum_radius_approx=float(max(v.rad() for v in uniform.flat)),
        sampled_variation_only=True, uniform_upper_bound_established=False,
        local_or_global_contraction_established=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    p.verify_sources(source['binding'])
    return source, arrays, report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', type=int, default=13)
    parser.add_argument('--column', type=int, default=14)
    parser.add_argument('--side', choices=('left', 'right'), default='left')
    parser.add_argument('--multiplier', type=int, choices=(-3, 3), required=True)
    parser.add_argument('--primal-pair', type=Path, required=True)
    parser.add_argument('--evidence-root', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if not 0 < args.interval < 370 or not 0 <= args.column < 74:
        raise ValueError('interior interval and frozen trial column required')
    args.out, args.primal_pair, args.evidence_root = args.out.resolve(), args.primal_pair.resolve(), args.evidence_root.resolve()
    args.out.mkdir(parents=True, exist_ok=False)
    ctx.prec = 512
    residual = p.geometry.residual
    targets = [(p.values, 'sha'), (residual.center, '_sha'), (residual.foundation.coordinate.center, '_sha')]
    with base.cache.cache_hashes(targets, excluded_roots=[args.out]):
        try:
            source, arrays, report = evaluate(args)
            encoded = {}
            for name, values in arrays.items():
                encoded[name+'_mid_q'], encoded[name+'_rad_q'] = p.hs.rational_balls(values)
            data = args.out/'column.npz'
            np.savez_compressed(data, **encoded)
            record = dict(algorithm=ALGORITHM, binding=source['binding'], interval=args.interval,
                trial_column=args.column, side=args.side, multiplier=args.multiplier,
                data_SHA256=p.values.sha(data), report=report, FULL_BHSM_COMPLETE=False)
            (args.out/'record.json').write_bytes(p.geometry.encoded(record))
            print(json.dumps({k: v for k, v in report.items() if k != 'verified_point_eigenpair_checks'}), flush=True)
        except BaseException as error:
            (args.out/'failure.json').write_bytes(p.geometry.encoded(dict(error=repr(error), FULL_BHSM_COMPLETE=False)))
            raise


if __name__ == '__main__':
    main()
