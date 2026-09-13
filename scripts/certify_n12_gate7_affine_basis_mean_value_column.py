"""Consume paired 75-direction Hessians for one uniform derivative column.

No new physical action evaluations. Rebuild geometry and numerical support,
and verify the paired same-family smoothness prerequisites before use.
"""
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
import diagnose_n12_gate7_affine_basis_uniform_hessian as producer
from bhsm.interface.affine_segment_family import validate_segment_family


def evaluate(pilot):
    ctx.prec = 512
    p = producer.engine.p
    path = pilot/'record.json'
    record = json.loads(path.read_bytes())
    receipt_path = pilot/'reproduction.json'
    receipt = json.loads(receipt_path.read_bytes())
    if (receipt.get('byte_identical') is not True or receipt.get('independent_recomputation') is not True
            or receipt.get('fresh_process') is not True
            or receipt.get('endpoint') != record['endpoint'] or receipt.get('column') != record['column']):
        raise ValueError('independently paired identical endpoint and input column required')
    for name in ('record.json', 'hessian.npz'):
        if receipt['files_SHA256'].get(name) != p.values.sha(pilot/name):
            raise ValueError('paired input changed: ' + name)
    if record['data_SHA256'] != p.values.sha(pilot/'hessian.npz'):
        raise ValueError('Hessian data changed')
    source = producer.engine.load_inputs(record['endpoint'])
    report = record['report']
    for key in ('all_75_scaled_affine_tube_directions_enclosed', 'all_75_point_columns_contained',
                'complete_original_seven_solve_graph_used', 'complete_original_scalar_contractions_used'):
        if report.get(key) is not True:
            raise ValueError('complete physical Hessian required: ' + key)
    for key in ('point_eigenpair_checks', 'point_derivative_checks'):
        checks = report.get(key, [])
        if len(checks) != 1 or not p.proof_valid(checks[0]):
            raise ValueError('verified identical point family required: ' + key)
    if report.get('physical_input_columns') != [record['column']]:
        raise ValueError('physical input column report mismatch')
    for key, value in source['binding'].items():
        if key == 'files':
            if any(record['binding']['files'].get(name) != digest for name, digest in value.items()):
                raise ValueError('Hessian and paired source family differ')
        elif record['binding'].get(key) != value:
            raise ValueError('Hessian and paired input binding differ: ' + key)
    p.verify_sources(record['binding'])
    value_module = producer.engine.values
    eigen_module = value_module.midpoint.values.eq
    eigen = json.loads((eigen_module.WORK/f"endpoint_{record['endpoint']:03d}"/'record.json').read_bytes())
    value = json.loads((value_module.WORK/f"endpoint_{record['endpoint']:03d}"/'record.json').read_bytes())
    family = validate_segment_family(eigen['report'], value['report'])
    tube = source['tube']
    _, weights, _, _, _ = p.values.operands()
    w = np.array([arb(float(v)) for v in weights], dtype=object)
    residual = p.geometry.residual
    with np.load(residual.center.JACOBIAN.with_suffix('.npz'), allow_pickle=False) as a:
        frame = residual.center.cert._frame(a['endpoint_physical_tangent_action'][record['endpoint']],
                                            residual.center.cert.TRIAL_DESCRIPTOR_SCALE)
    if frame.shape != (99, 74):
        raise ValueError('complete frozen augmented frame required')
    directions = np.empty((99, 75), dtype=object)
    directions[:, 0] = tube['raw_longitudinal_direction']*tube['radius_longitudinal']
    directions[:98, 0] *= w
    directions[:, 1:] = np.array([arb(float(v)) for v in frame.flat], dtype=object).reshape(frame.shape)*tube['radius_transverse']
    axis = np.full(99, arb(0), dtype=object)
    if not 0 <= record['column'] < 99:
        raise ValueError('physical input column out of range')
    axis[record['column']] = arb(1)
    with np.load(pilot/'hessian.npz', allow_pickle=False) as a:
        for name, expected in (('weighted_tube_directions', directions), ('weighted_input_axis', axis),
                               ('raw_domain', source['raw_domain'])):
            mid, rad = p.hs.rational_balls(expected)
            if not np.array_equal(mid, a[name+'_mid_q']) or not np.array_equal(rad, a[name+'_rad_q']):
                raise ValueError('saved affine geometry differs: ' + name)
        def read(name):
            return p.hs.restore_balls(a[name+'_mid_q'], a[name+'_rad_q'])
        physical, line, response = read('normalized_hessian'), read('uniform_solve_5')[:61], read('uniform_solve_6')
        point_df, point_line, point_response = read('point_derivative'), read('point_solve_1')[:61], read('point_solve_2')
        if physical.shape != (99, 75) or line.shape != (61, 75) or response.shape != (62, 75):
            raise ValueError('all 75 Hessian columns required')
        # Outward restoration may enlarge source balls. Recompute support from
        # the restored enclosures; do not copy or shrink to historical candidates.
        arrays = {}
        for name, hessian, anchor in (('derivative', physical, point_df),
                                      ('line', line, point_line), ('response', response, point_response)):
            if anchor.shape != (hessian.shape[0], 1):
                raise ValueError('complete verified point anchor required')
            bound = producer.support(hessian)
            arrays[name+'_support'] = bound
            arrays[name] = anchor+np.array([arb(0, v) for v in bound], dtype=object)[:, None]
    if not all(v.is_finite() for a in arrays.values() for v in a.flat):
        raise ArithmeticError('finite uniform column enclosures required')
    files = dict(record['binding']['files'])
    for file in (path, pilot/'hessian.npz', receipt_path, Path(__file__), Path(producer.__file__),
                 Path(sys.modules[validate_segment_family.__module__].__file__),
                 ROOT/'theory/n12_gate7_affine_basis_mean_value.md'):
        residual.merge(files, {p.df.file_key(file): p.values.sha(file)})
    binding = dict(record['binding'], files=files)
    p.verify_sources(binding)
    report = dict(family, same_family_segment_smoothness_established=True,
                  all_75_scaled_directions_verified=True, uniform_derivative_column_enclosed=True,
                  physical_input_columns=[record['column']], full_physical_input_basis=False,
                  full_path_uniform_contraction=False, candidates_consumed_by_production=False,
                  maximum_derivative_radius=float(max(v.rad() for v in arrays['derivative'].flat)),
                  maximum_line_radius=float(max(v.rad() for v in arrays['line'].flat)),
                  maximum_response_radius=float(max(v.rad() for v in arrays['response'].flat)),
                  independent_recomputation=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    return arrays, binding, report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    try:
        arrays, binding, report = evaluate(args.pilot)
        encoded = {}
        for name, a in arrays.items():
            encoded[name+'_mid_q'], encoded[name+'_rad_q'] = producer.engine.p.hs.rational_balls(a)
        data = args.out/'column.npz'
        np.savez_compressed(data, **encoded)
        producer.engine.p.verify_sources(binding)
        record = dict(binding=binding, report=report, data_SHA256=producer.engine.p.values.sha(data), FULL_BHSM_COMPLETE=False)
        (args.out/'record.json').write_bytes(producer.engine.p.geometry.encoded(record))
        print(json.dumps(report), flush=True)
    except BaseException as error:
        (args.out/'failure.json').write_text(json.dumps(dict(error=repr(error), FULL_BHSM_COMPLETE=False)), encoding='utf-8')
        raise


if __name__ == '__main__':
    main()
