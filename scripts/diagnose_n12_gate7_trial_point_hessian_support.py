"""Use the paired point Hessian to distinguish longitudinal/transverse sensitivity."""
import os
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import json
from pathlib import Path
import numpy as np
from flint import arb, ctx
import diagnose_n12_gate7_directed_trial_hs_column as base
import certify_n12_gate7_direct_physical_quadratic_sources as point_hessian

p = base.p
ALGORITHM = 'PAIRED_POINT_HESSIAN_TRIAL_TUBE_SENSITIVITY_ARB512_V1'
THEORY = base.ROOT/'theory/n12_gate7_trial_point_hessian_support.md'


def evaluate(args):
    index = args.interval
    local = base.reader.load_inputs(index)
    _, source, _, _ = base.load_stage(index, 'endpoint', args.primal_pair)
    expected = point_hessian.hessian.binding()
    state, descriptor, weights, reference, _, _ = point_hessian.hessian.df.point_inputs('endpoint', index, expected['value_point_binding'])
    ctx.prec = 512
    _, wanted_weights, descriptors, wanted_reference, _ = p.values.operands()
    if (point_hessian.hessian.graph.cert is not p.values.cert
            or not np.array_equal(weights, wanted_weights) or not np.array_equal(reference, wanted_reference)
            or descriptor != arb(float(descriptors[index]))
            or not all(arb(v) == a for v, a in zip(state, source['paired']['center'], strict=True))):
        raise ValueError('paired point Hessian must use the identical anchor, weights, reference, and graph')
    tensor, files, _ = point_hessian.verify_hessian('endpoint', index, expected)
    ctx.prec = 512
    p.geometry.residual.merge(source['binding']['files'], files)
    p.geometry.residual.merge(source['binding']['files'], local['binding']['files'])
    trial = np.array([[arb(float(v))] for v in local['trial_left'][:, args.column]], dtype=object)
    frame = np.array([arb(float(v)) for v in local['trial_left'].flat], dtype=object).reshape(99, 74)
    tube = source['tube']
    directions = np.empty((99, 75), dtype=object)
    directions[:, 0] = tube['raw_longitudinal_direction']*tube['radius_longitudinal']
    directions[:98, 0] *= np.array([arb(float(v)) for v in weights], dtype=object)
    directions[:, 1:] = frame*tube['radius_transverse']
    projected = base.array(tensor.cartesian(trial, directions))
    long_support = np.array([abs(v).upper() for v in projected[:, 0]], dtype=object)
    transverse = np.array([sum((abs(v).upper()**2 for v in row[1:]), arb(0)).sqrt().upper()
                           for row in projected], dtype=object)
    total = long_support+transverse
    arrays = dict(point_hessian_contractions=projected, weighted_tube_directions=directions,
                  trial=trial, longitudinal_linearized_support=long_support,
                  transverse_linearized_support=transverse, total_linearized_support=total)
    sample_reports = {}
    for label, multiplier in (('minus', -3), ('plus', 3)):
        record, values, sample_files = base.read_pair(args.sample_root/label)
        report = record.get('report', {})
        if (record.get('algorithm') != 'VERIFIED_ENDPOINT_TRIAL_POINT_VARIATION_ARB512_V1'
                or record.get('interval') != args.interval or record.get('trial_column') != args.column
                or record.get('side') != 'left' or record.get('multiplier') != multiplier
                or not all(report.get(key) is True for key in ('paired_branch_containment',
                    'paired_primal_response_containment', 'paired_uniform_action_containment', 'complete_original_point_graph'))
                or not all(a == b for a, b in zip(trial.flat, values['trial'].flat, strict=True))):
            raise ValueError('paired matching longitudinal point sample required')
        p.geometry.residual.merge(source['binding']['files'], record['binding']['files'])
        base.bind(source, *sample_files)
        prediction = projected[:, :1]*(arb(multiplier)/4)
        observed = values['difference_from_anchor']
        remainder = observed-prediction
        arrays[label+'_point_linear_prediction'] = prediction
        arrays[label+'_sample_difference_from_linear_prediction'] = remainder
        row = report['largest_proven_difference_row']
        sample_reports[label] = dict(row=row,
            observed_difference_upper_approx=float(abs(observed[row, 0]).upper()),
            same_row_uniform_action_radius_approx=float(values['uniform_action'][row, 0].rad()),
            same_row_longitudinal_linearized_support_approx=float(long_support[row]),
            same_row_transverse_linearized_support_approx=float(transverse[row]),
            same_row_sample_linearization_remainder_upper_approx=float(abs(remainder[row, 0]).upper()),
            maximum_sample_linearization_remainder_upper_approx=float(max(abs(v).upper() for v in remainder.flat)))
    for module in (point_hessian, point_hessian.quadratic, point_hessian.hessian):
        base.bind(source, Path(module.__file__))
    base.bind(source, Path(__file__), THEORY, Path(base.__file__))
    p.verify_sources(source['binding'])
    return source, arrays, dict(paired_complete_point_hessian_used=True,
        exact_anchor_weights_reference_graph_matched=True, all_75_scaled_tube_directions_used=True,
        new_action_derivative_evaluations=0, samples=sample_reports,
        maximum_longitudinal_linearized_support_approx=float(max(long_support)),
        maximum_transverse_linearized_support_approx=float(max(transverse)),
        maximum_total_linearized_support_approx=float(max(total)),
        point_linearization_only=True, neighborhood_remainder_enclosed=False,
        uniform_derivative_enclosure_established=False, local_or_global_contraction_established=False,
        Gate7_closed=False, FULL_BHSM_COMPLETE=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', type=int, default=13)
    parser.add_argument('--column', type=int, default=14)
    parser.add_argument('--primal-pair', type=Path, required=True)
    parser.add_argument('--sample-root', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if not 0 < args.interval < 370 or not 0 <= args.column < 74:
        raise ValueError('interior interval and frozen trial column required')
    args.out, args.primal_pair, args.sample_root = args.out.resolve(), args.primal_pair.resolve(), args.sample_root.resolve()
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
                trial_column=args.column, data_SHA256=p.values.sha(data), report=report, FULL_BHSM_COMPLETE=False)
            (args.out/'record.json').write_bytes(p.geometry.encoded(record))
            print(json.dumps(report), flush=True)
        except BaseException as error:
            (args.out/'failure.json').write_bytes(p.geometry.encoded(dict(error=repr(error), FULL_BHSM_COMPLETE=False)))
            raise


if __name__ == '__main__':
    main()
