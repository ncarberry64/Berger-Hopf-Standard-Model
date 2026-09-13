"""Bound the actual midpoint eigenvalue using its complete scalar derivative."""
import os
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
import certify_n12_gate7_midpoint_primal_direct_variations as primal
from diagnose_n12_gate7_mean_value_bootstrap_hessian import select_first_variation
from bhsm.interface.selected_eigenvalue_variation import eigenvalue_slopes


def load_inputs(index, pair):
    p = primal.engine.p
    source = primal.engine.load_inputs(index)
    first = pair/'first'
    path, data, receipt_path = first/'record.json', first/'column.npz', pair/'reproduction.json'
    record, receipt = json.loads(path.read_bytes()), json.loads(receipt_path.read_bytes())
    report = record.get('report', {})
    if (record.get('interval') != index or path.read_bytes() != p.geometry.encoded(record)
            or receipt.get('independent_recomputation') is not True
            or receipt.get('byte_identical') is not True or receipt.get('fresh_process') is not True
            or report.get('all_249_scaled_directions_verified') is not True
            or report.get('same_family_segment_smoothness_established') is not True
            or report.get('uniform_primal_psi_and_response_enclosed') is not True
            or report.get('scope') != 'ACTUAL_HS_MIDPOINT_OUTER_DOMAIN'):
        raise ValueError('paired complete actual midpoint primal family required')
    for file in (path, data):
        if receipt['files_SHA256'].get(file.name) != p.values.sha(file):
            raise ValueError('paired primal evidence changed')
    if record['data_SHA256'] != p.values.sha(data):
        raise ValueError('primal numerical data changed')
    for key, value in source['binding'].items():
        if key == 'files':
            if any(record['binding']['files'].get(name) != digest for name, digest in value.items()):
                raise ValueError('eigenvalue and primal physical domains differ')
        elif record['binding'].get(key) != value:
            raise ValueError('eigenvalue and primal geometry differ: ' + key)
    p.geometry.residual.merge(source['binding']['files'], record['binding']['files'])
    with np.load(data, allow_pickle=False) as a:
        psi = p.hs.restore_balls(a['psi_value_mid_q'], a['psi_value_rad_q'])
        directions = p.hs.restore_balls(a['weighted_midpoint_directions_mid_q'],
                                        a['weighted_midpoint_directions_rad_q'])
    checks = report.get('point_eigenpair_checks', [])
    if len(checks) != 1 or not p.proof_valid(checks[0]):
        raise ValueError('complete verified normalized point eigenpair required')
    point = p.hs.restore_balls(np.array(checks[0]['target_midpoints_rational']),
                               np.array(checks[0]['target_radii_rational']))
    if psi.shape != (61, 1) or directions.shape != (99, 249) or point.shape != (62,):
        raise ValueError('complete primal box, scaled directions and point witness required')
    if not all(a.contains(b) for a, b in zip(source['paired']['eigenbox'], point, strict=True)):
        raise ArithmeticError('point witness must lie in the paired eigenpair family')
    selected = source['paired']['eigenbox'][:61].copy()
    changed = select_first_variation(selected, psi[:, 0])
    source.update(selected_psi=selected, scaled_directions=directions,
                  point_eigenvalue=point[-1], psi_coordinates_tightened=changed)
    for file in (path, data, receipt_path, Path(__file__), Path(primal.__file__),
                 Path(sys.modules[eigenvalue_slopes.__module__].__file__),
                 Path(sys.modules[select_first_variation.__module__].__file__),
                 ROOT/'theory/n12_gate7_eigenvalue_mean_value.md'):
        p.geometry.residual.merge(source['binding']['files'], {p.df.file_key(file): p.values.sha(file)})
    p.verify_sources(source['binding'])
    return source


def evaluate(source):
    p = primal.engine.p
    cert = p.values.cert
    eq = primal.engine.values.eq
    eigen = json.loads((eq.WORK/f"interval_{source['index']:03d}"/'record.json').read_bytes())
    value = json.loads((primal.engine.values.WORK/f"interval_{source['index']:03d}"/'record.json').read_bytes())
    family = primal.validate_midpoint_segment_family(eigen['report'], value['report'])
    weights = np.array([arb(float(v)) for v in p.values.operands()[1]], dtype=object)
    raw = source['scaled_directions'][:98]/weights[:, None]
    groups = [dict(group, radius=arb(1)) for group in source['groups']]
    primal.grouped.group_row_bounds(raw, groups)
    full = source['paired']['full']
    orders = []

    def action(state, legs, maps):
        if len(legs) != 3:
            raise ArithmeticError('scalar eigenvalue slope uses exactly third action derivatives')
        orders.append(3)
        return cert._contracted_action(state, legs, maps)

    with p.df.sparse.use_optimized_mixed(cert), primal.use_ball_factored_integrand(cert, full):
        maps = cert._arb_action_jets(full).dense_maps
        slopes = eigenvalue_slopes(action, full, source['selected_psi'], raw, maps)
    support = primal.grouped.group_row_bounds(slopes[None, :], groups)[0]
    candidate = source['point_eigenvalue'] + arb(0, support)
    previous = source['paired']['eigenbox'][-1]
    if not candidate.is_finite() or not candidate.overlaps(previous):
        raise ArithmeticError('finite same-family eigenvalue enclosures must overlap')
    arrays = dict(eigenvalue=np.array([candidate]), original_eigenvalue=np.array([previous]),
                  point_eigenvalue=np.array([source['point_eigenvalue']]),
                  eigenvalue_support=np.array([support]), eigenvalue_slopes=slopes)
    report = dict(family, interval=source['index'], scope='ACTUAL_HS_MIDPOINT_OUTER_DOMAIN',
        uniform_selected_eigenvalue_enclosed=True, all_249_scaled_directions_verified=True,
        normalized_symmetric_eigenvalue_derivative_used=True, auxiliary_line_border_used=False,
        contracted_action_orders=orders, psi_coordinates_tightened=source['psi_coordinates_tightened'],
        original_eigenvalue_radius_approx=float(previous.rad()), eigenvalue_radius_approx=float(candidate.rad()),
        eigenvalue_box_narrower=bool(candidate.rad() < previous.rad()),
        full_path_uniform_contraction=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    return arrays, report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', type=int, required=True)
    parser.add_argument('--primal-pair', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    ctx.prec = 512
    p = primal.engine.p
    residual = p.geometry.residual
    targets = [(p.values, 'sha'), (residual.center, '_sha'), (residual.foundation.coordinate.center, '_sha')]
    with primal.cache.cache_hashes(targets, excluded_roots=[args.out]):
        try:
            source = load_inputs(args.interval, args.primal_pair)
            arrays, report = evaluate(source)
            p.verify_sources(source['binding'])
            encoded = {}
            for name, a in arrays.items():
                encoded[name+'_mid_q'], encoded[name+'_rad_q'] = p.hs.rational_balls(a)
            data = args.out/'column.npz'
            np.savez_compressed(data, **encoded)
            record = dict(binding=source['binding'], interval=args.interval, report=report,
                          data_SHA256=p.values.sha(data), FULL_BHSM_COMPLETE=False)
            (args.out/'record.json').write_bytes(p.geometry.encoded(record))
            print(json.dumps(report), flush=True)
        except BaseException as error:
            (args.out/'failure.json').write_bytes(p.geometry.encoded(dict(error=repr(error), FULL_BHSM_COMPLETE=False)))
            raise


if __name__ == '__main__':
    main()
