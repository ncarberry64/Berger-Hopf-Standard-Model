"""Enclose ambient DF and selected Hessian entries on a paired uniform box.

Use a separate numerical process after the uniform value pilot succeeds.
Preflight verifies the complete paired value pilot without action evaluation.
"""
import os
for name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[name] = '1'
import argparse
import json
from pathlib import Path
import sys
import time
import numpy as np
from flint import arb, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
import certify_n12_gate7_uniform_physical_value_pilot as pilot
import derive_n12_gate7_direct_physical_hessians as hessian

WORK = ROOT/'artifacts/flagship_integration/.uniform_physical_derivative_pilot_work'
THEORY = ROOT/'theory/n12_gate7_uniform_physical_derivative_pilot.md'
ALGORITHM = 'UNIFORM_PHYSICAL_HS_BOX_AMBIENT_DF_AND_HESSIAN_ROW_COLUMNS_ARB512_V1'


def paired_uniform_source(interval):
    """Bind all three independently reproduced uniform rate/domain records."""
    source = pilot.load_inputs()
    directory = pilot.WORK/f'interval_{interval:03d}'
    path, receipt_path = directory/'manifest.json', directory/'reproduction.json'
    manifest = json.loads(path.read_text())
    receipt = json.loads(receipt_path.read_text())
    points = [('endpoint', interval), ('endpoint', interval+1), ('midpoint', interval)]
    required = {pilot.df.file_key(directory/f'{stage}_{i:03d}.{ext}') for stage, i in points for ext in ('json', 'npz')}
    if (manifest.get('algorithm') != pilot.ALGORITHM or manifest.get('interval') != interval
            or manifest.get('selected_two_endpoint_and_actual_midpoint_box_rates_enclosed') is not True
            or set(manifest.get('files', {})) != required or path.read_bytes() != pilot.geometry.encoded(manifest)
            or receipt.get('byte_identical') is not True or receipt.get('independent_recomputation') is not True
            or receipt.get('interval') != interval or receipt.get('points') != 3
            or receipt.get('manifest_SHA256') != pilot.values.sha(path)):
        raise RuntimeError('complete paired three-box uniform value pilot required')
    pilot.values.verify_binding(dict(files=manifest['files']))
    domains = {}
    for stage, index in points:
        _, dependencies = pilot.point_domain(directory, stage, index, source)
        arrays, _ = pilot.read_point(directory, stage, index, source, dependencies)
        domains[(stage, index)] = arrays
    files = dict(source['binding']['files'])
    hessian.merge(files, manifest['files'])
    for p in (path, receipt_path):
        hessian.merge(files, {pilot.df.file_key(p): pilot.values.sha(p)})
    return source, domains, files


def point_context(interval, stage, index):
    if (type(interval) is not int or not 0 <= interval < 370
            or (stage, index) not in (('endpoint', interval), ('endpoint', interval+1), ('midpoint', interval))):
        raise ValueError('point must belong to the selected uniform interval')
    source, domains, files = paired_uniform_source(interval)
    # The graph/base source closure does not require any point Hessian output.
    kernel = hessian.binding()
    if kernel['value_point_binding'] != source['binding']['value_point_binding']:
        raise RuntimeError('uniform values and derivative kernels use different paired centers')
    if hessian.graph.cert is not pilot.values.cert:
        raise RuntimeError('uniform value and derivative physical kernels differ')
    hessian.merge(files, kernel['files'])
    for path in (Path(__file__), THEORY, Path(pilot.__file__), pilot.THEORY):
        hessian.merge(files, {pilot.df.file_key(path): pilot.values.sha(path)})
    ctx.prec = 512
    weighted = domains[(stage, index)]['weighted_domain']
    # Reconstructing either exported box can enlarge it. Evaluate on the
    # unweighting of the canonical reconstructed weighted domain and prove a
    # NEW eigenpair inclusion there; do not transfer an inner-box proof.
    raw = pilot.geometry.neighborhood.unweight_box(weighted, source['weights'])
    binding = dict(algorithm=ALGORITHM, precision_bits=512, interval=interval,
        runtime=source['binding']['runtime'], files=files,
        normalized_inputs=source['binding']['normalized_inputs'],
        uniform_value_binding=source['binding'], trial_radii_rational=source['binding']['trial_radii_rational'])
    pilot.verify_sources(binding)
    return dict(binding=binding, stage=stage, index=index, weighted=weighted, raw=raw,
        state=raw[:98], descriptor=raw[98], weights=source['weights'], reference=source['reference'],
        reference_value=domains[(stage, index)]['value'])


def evaluate(context, row, columns):
    """Reprove the whole box, then evaluate exact ambient directions in Arb."""
    if (type(row) is not int or not 0 <= row < 99 or not columns or len(set(columns)) != len(columns)
            or any(type(i) is not int or not 0 <= i < 99 for i in columns)):
        raise ValueError('valid row and distinct explicit ambient columns required')
    ctx.prec = 512
    with hessian.df.sparse.use_optimized_mixed(hessian.graph.cert):
        prepared = hessian.base.VerifiedHessianBase(hessian.graph.cert, context['state'], context['reference'])
    if not pilot.proof_valid(prepared.eigenpair_verification):
        raise ArithmeticError('new uniform normalized index24 eigenpair proof required')
    identity = np.array([[arb(int(i == j)) for j in range(99)] for i in range(99)], dtype=object)
    with prepared.use(), hessian.df.sparse.use_optimized_mixed(hessian.graph.cert):
        rate = hessian.graph.cert._rate_enclosure(context['state'], context['descriptor'], context['weights'],
                                                context['reference'], identity)
    values = pilot.hs.finite_vector(rate.value, 99)
    derivative = np.asarray(rate.derivative, dtype=object)
    if derivative.shape != (99, 99) or not all(isinstance(v, arb) and v.is_finite() for v in derivative.flat):
        raise ArithmeticError('complete finite uniform ambient Jacobian required')
    if not all(a.overlaps(b) for a, b in zip(values, context['reference_value'], strict=True)):
        raise ArithmeticError('uniform derivative value does not overlap paired box value')
    axis = np.array([arb(int(i == row)) for i in range(99)], dtype=object)
    directions = identity[:, columns]
    with prepared.use(), hessian.df.sparse.use_optimized_mixed(hessian.graph.cert), \
            hessian.bulk.use_bulk_matrices(hessian.graph.cert), \
            hessian.factored.use_ball_factored_integrand(hessian.graph.cert, context['state']):
        second = hessian.graph.batched_axis_map(context['state'], context['descriptor'], context['weights'],
                                               context['reference'], axis, directions)
    if second.shape != (99, len(columns)) or not all(isinstance(v, arb) and v.is_finite() for v in second.flat):
        raise ArithmeticError('complete finite selected uniform Hessian entries required')
    return dict(value=values, DF=derivative, H=second), prepared.eigenpair_verification


def metadata(context, row, columns):
    return dict(algorithm=ALGORITHM, scope='UNIFORM_SELECTED_HS_BOX_AMBIENT_DF_AND_HESSIAN_ROW_COLUMNS',
        binding=context['binding'], stage=context['stage'], index=context['index'], row=row, columns=columns,
        uniform_ambient_Jacobian_enclosed=True, uniform_selected_Hessian_entries_enclosed=True,
        canonical_weighted_domain_reconstruction_used=True, new_uniform_eigenpair_inclusion_required=True,
        weighted_augmented_identity_directions=True, state_uncertainty_retained=True,
        value_overlaps_paired_uniform_value=True, full_point_Hessian_enclosed=False,
        full_history_uniform_derivatives_enclosed=False, neighborhood_remainder_enclosed=False,
        intrinsic_constraint_chart_certified=False, physical_quotient_identified=False,
        physical_contraction_proved=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False)


def output_path(context, row, columns):
    return WORK/f"interval_{context['binding']['interval']:03d}"/(
        f"{context['stage']}_{context['index']:03d}_row_{row:03d}_columns_"+'-'.join(map(str, columns))+'.npz')


def read_result(path, context, row, columns):
    record_path = path.with_suffix('.json')
    record = json.loads(record_path.read_text())
    expected = metadata(context, row, columns)
    expected.update(data_SHA256=pilot.values.sha(path), eigenpair_verification=record.get('eigenpair_verification', {}))
    if (record != expected or record_path.read_bytes() != pilot.geometry.encoded(record)
            or not pilot.proof_valid(expected['eigenpair_verification'])):
        raise RuntimeError('uniform derivative result binding or proof changed')
    shapes = dict(value=(99,), DF=(99, 99), H=(99, len(columns)), weighted_domain=(99,), raw_domain=(99,))
    wanted = {key+suffix for key in shapes for suffix in ('_mid_q', '_rad_q')}
    with np.load(path, allow_pickle=False) as arrays:
        if set(arrays.files) != wanted or any(arrays[k+s].shape != shape for k, shape in shapes.items() for s in ('_mid_q', '_rad_q')):
            raise RuntimeError('complete rational uniform derivative and domain arrays required')
        for key in shapes:
            pilot.hs.restore_balls(arrays[key+'_mid_q'], arrays[key+'_rad_q'])
    return record


def materialize(context, row, columns, recompute=False):
    ctx.prec = 512
    pilot.verify_sources(context['binding'])
    path = output_path(context, row, columns)
    path.parent.mkdir(parents=True, exist_ok=True)
    receipt = path.with_suffix('.reproduction.json')
    previous = None
    if path.exists() or path.with_suffix('.json').exists():
        previous = read_result(path, context, row, columns)
        if not recompute:
            raise RuntimeError('uniform derivative evidence exists; explicit repeat required')
    elif recompute:
        raise RuntimeError('independent repeat requires previous uniform derivative evidence')
    if receipt.exists():
        receipt.replace(path.parent/f'{path.stem}.reproduction.before_attempt_{time.time_ns()}.json')
    arrays = {}
    for name, values in (('weighted_domain', context['weighted']), ('raw_domain', context['raw'])):
        arrays[name+'_mid_q'], arrays[name+'_rad_q'] = pilot.hs.rational_balls(values)
    attempt = path.parent/f'{path.stem}.attempt_{time.time_ns()}.npz'
    np.savez_compressed(attempt, **arrays)
    try:
        result, proof = evaluate(context, row, columns)
        pilot.verify_sources(context['binding'])
        for name, values in result.items():
            arrays[name+'_mid_q'], arrays[name+'_rad_q'] = pilot.hs.rational_balls(values)
        candidate = attempt.with_name(attempt.stem+'.candidate.npz')
        np.savez_compressed(candidate, **arrays)
        record = metadata(context, row, columns)
        record.update(data_SHA256=pilot.values.sha(candidate), eigenpair_verification=proof)
        if previous is not None:
            if record != previous:
                candidate.with_suffix('.json').write_bytes(pilot.geometry.encoded(record))
                raise ArithmeticError('independent uniform derivative differs; candidate preserved')
            candidate.unlink()
            receipt.write_bytes(pilot.geometry.encoded(dict(byte_identical=True, independent_recomputation=True,
                record_SHA256=pilot.values.sha(path.with_suffix('.json')), data_SHA256=pilot.values.sha(path),
                full_point_Hessian_enclosed=False, neighborhood_remainder_enclosed=False, FULL_BHSM_COMPLETE=False)))
        else:
            candidate.replace(path)
            path.with_suffix('.json').write_bytes(pilot.geometry.encoded(record))
        attempt.unlink()
    except BaseException as error:
        attempt.with_suffix('.json').write_bytes(pilot.geometry.encoded(dict(error=repr(error),
            eigenpair_inclusion=getattr(error, 'eigenpair_inclusion', None), binding=context['binding'],
            stage=context['stage'], index=context['index'], row=row, columns=columns,
            input_data_SHA256=pilot.values.sha(attempt), method_failure_does_not_prove_domain_singular=True,
            uniform_derivatives_enclosed=False, FULL_BHSM_COMPLETE=False)))
        raise
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', type=int, default=13)
    parser.add_argument('--stage', choices=['endpoint', 'midpoint'], default='midpoint')
    parser.add_argument('--index', type=int, default=13)
    parser.add_argument('--row', type=int, default=0)
    parser.add_argument('--columns', default='0,98')
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--recompute', action='store_true')
    args = parser.parse_args()
    columns = [int(v) for v in args.columns.split(',')]
    if (not 0 <= args.row < 99 or not columns or len(set(columns)) != len(columns)
            or any(not 0 <= v < 99 for v in columns) or (args.preflight and args.recompute)):
        raise ValueError('valid row and columns; preflight and recompute are exclusive')
    context = point_context(args.interval, args.stage, args.index)
    if args.preflight:
        print(json.dumps(dict(paired_uniform_box_verified=True, stage=args.stage, index=args.index,
            numerical_derivatives_evaluated=False, FULL_BHSM_COMPLETE=False)), flush=True)
        return
    path = materialize(context, args.row, columns, args.recompute)
    print(json.dumps(dict(result=str(path), full_ambient_Jacobian=True, Hessian_row=args.row,
        Hessian_columns=columns, independently_reproduced=args.recompute,
        full_point_Hessian_enclosed=False, FULL_BHSM_COMPLETE=False)), flush=True)


if __name__ == '__main__':
    main()
