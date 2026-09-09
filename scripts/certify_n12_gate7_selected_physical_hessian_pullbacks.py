"""Aggregate complete selected-point Hessian balls without rerunning the kernel."""
from __future__ import annotations
import os
for name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[name] = '1'
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
import derive_n12_gate7_physical_midpoint_hessian_errors as campaign
from bhsm.interface import physical_hessian_error_pullback as pullback
from bhsm.interface import resolved_midpoint_coordinate_error as resolved
from bhsm.interface import stored_pullback_assembly_error as assembly

RESULT = ROOT/'artifacts/flagship_integration/.physical_midpoint_hessian_pullback_work'


def aggregate_point(interval):
    values, binding, fingerprint = campaign.load_inputs(interval)
    directory = campaign.point_directory(interval)
    if json.loads((directory/'binding.json').read_text()) != binding:
        raise ValueError('saved physical point binding differs from current operands')
    error_mid, error_radius, records = campaign.cache.assemble_rows(directory, fingerprint)
    c = campaign.center
    inputs = c.center._load_inputs()
    axes = c.component._load_axes()
    tangents = inputs['endpoint'][2]
    mid_tangents = inputs['midpoint'][2]
    with np.load(c.ENDPOINT.with_suffix('.npz')) as source:
        times = source['collocation_arc_parameters'].copy()
    with np.load(c.PRECONDITIONER.with_suffix('.npz')) as source:
        right = source['reduced_right_Newton_blocks'][interval].copy()
    h = float(times[interval+1]-times[interval])
    target = c._kinematic_midpoint_map(interval, h, axes, tangents, mid_tangents).augmented
    coordinates = np.linalg.solve(values['basis'], target)
    test = c.cert._frame(tangents[interval+1], c.cert.TEST_DESCRIPTOR_SCALE).T
    output = 2*h*(-np.linalg.solve(right, test))/3
    q = values['tensor']
    coordinate_bound = resolved.bound_resolved_coordinate_pullback_error(
        values['basis'], target, coordinates, q[:,:73,:73], q[:,73:,:73], q[:,73:,73:])
    previous = ctx.prec
    ctx.prec = resolved.PRECISION
    try:
        delta = resolved._float_upper((
            arb(coordinate_bound['retained_coordinate_error_operator_norm_upper'])**2
            + arb(coordinate_bound['complement_coordinate_error_operator_norm_upper'])**2).sqrt())
        correction, report = pullback.pullback_hessian_error(
            output, error_mid, error_radius, coordinates, delta)
        coefficient = resolved._float_upper(2*arb(report['total_error_pullback_frobenius_upper']))
    finally:
        ctx.prec = previous
    arrays = dict(error_mid=error_mid, error_radius=error_radius,
                  correction_center=correction, coordinates=coordinates,
                  target=target, output=output, basis=values['basis'])
    sources = [Path(__file__), Path(pullback.__file__), Path(resolved.__file__),
               Path(assembly.__file__), Path(c.__file__), Path(c.component.__file__),
               Path(c.component.scalar.__file__)]
    payload = dict(
        scope='COMPLETE_SELECTED_MIDPOINT_PHYSICAL_HESSIAN_ERROR_THROUGH_STORED_MAPS',
        interval=interval, rows=99, direction_pairs=4950, input_dimension=99,
        output_dimension=99, physical_row_fingerprint=fingerprint,
        physical_source_binding=binding,
        row_records=records,
        row_metadata_SHA256={f'row_{r:03d}.json':campaign.cache.file_sha(directory/f'row_{r:03d}.json')
                             for r in range(99)},
        aggregation_source_SHA256={p.relative_to(ROOT).as_posix():campaign.sha(p) for p in sources},
        operand_binary64_SHA256={k:campaign.array_sha(v) for k,v in arrays.items()},
        coordinate_bound=coordinate_bound, physical_error_pullback=report,
        local_pair_uniform_quadratic_coefficient_upper=coefficient,
        all_rows_present=True, all_midpoints_covered=False,
        endpoint_hessians_covered=False, kinematic_construction_error_enclosed=False,
        output_map_construction_error_enclosed=False,
        neighborhood_remainder_enclosed=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    # Recheck evidence after aggregation; partial or changed rows never become zero.
    for row, record in enumerate(records):
        if campaign.cache.file_sha(directory/f'row_{row:03d}.npz') != record['data_SHA256']:
            raise RuntimeError('physical row changed during aggregation')
        if campaign.cache.file_sha(directory/f'row_{row:03d}.json') != payload['row_metadata_SHA256'][f'row_{row:03d}.json']:
            raise RuntimeError('physical row metadata changed during aggregation')
    for name, digest in binding['sources'].items():
        if campaign.sha(ROOT/name) != digest:
            raise RuntimeError('physical source changed during aggregation')
    return arrays, payload


def write_point(interval):
    arrays, payload = aggregate_point(interval)
    RESULT.mkdir(parents=True, exist_ok=True)
    stem = RESULT/f'midpoint_{interval:03d}'
    np.savez_compressed(stem.with_suffix('.npz'), **arrays)
    payload['data_SHA256'] = campaign.cache.file_sha(stem.with_suffix('.npz'))
    stem.with_suffix('.json').write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(dict(interval=interval, output=str(stem.with_suffix('.json')),
        local_pair_error=payload['local_pair_uniform_quadratic_coefficient_upper'])),flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--midpoints',required=True)
    args = parser.parse_args()
    for interval in campaign.parse_intervals(args.midpoints):
        write_point(interval)


if __name__ == '__main__':
    main()
