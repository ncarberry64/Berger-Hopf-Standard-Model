"""Enclose endpoint physical fields using their paired complete uniform DF."""
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
import certify_n12_gate7_primal_uniform_physical_local_defects as reader
import bhsm_immutable_input_hash_cache as cache
from bhsm.interface.affine_segment_family import validate_segment_family
from bhsm.interface.grouped_field_mean_value import enclose_field
from diagnose_n12_gate7_mean_value_bootstrap_hessian import select_first_variation


def evaluate(index):
    p = reader.p
    source, D = reader.read_derivative(None, index, 'endpoint')
    values = reader.endpoint.values
    point_module = values.midpoint.values
    point_data = point_module.WORK/f'endpoint_{index:03d}'/'value.npz'
    if source['binding']['files'].get(p.df.file_key(point_data)) != p.values.sha(point_data):
        raise ValueError('verified point field must be part of the paired source binding')
    with np.load(point_data, allow_pickle=False) as a:
        point = p.hs.restore_balls(a['point_rate_mid_q'], a['point_rate_rad_q'])
    if point.shape != (99,) or not all(v.is_finite() for v in point):
        raise ValueError('complete verified point field required')
    eigen = json.loads((point_module.eq.WORK/f'endpoint_{index:03d}'/'record.json').read_bytes())
    value = json.loads((values.WORK/f'endpoint_{index:03d}'/'record.json').read_bytes())
    family = validate_segment_family(eigen['report'], value['report'])
    tube, residual = source['tube'], p.geometry.residual
    with np.load(residual.center.JACOBIAN.with_suffix('.npz'), allow_pickle=False) as a:
        frame = residual.center.cert._frame(a['endpoint_physical_tangent_action'][index],
                                            residual.center.cert.TRIAL_DESCRIPTOR_SCALE)
    if frame.shape != (99, 74):
        raise ValueError('complete frozen augmented frame required')
    weights = np.array([arb(float(v)) for v in p.values.operands()[1]], dtype=object)
    directions = np.empty((99, 75), dtype=object)
    directions[:, 0] = tube['raw_longitudinal_direction']*tube['radius_longitudinal']
    directions[:98, 0] *= weights
    directions[:, 1:] = np.array([arb(float(v)) for v in frame.flat], dtype=object).reshape(frame.shape)*tube['radius_transverse']
    groups = [dict(start=0, stop=1, norm='interval', radius=arb(1)),
              dict(start=1, stop=75, norm='euclidean', radius=arb(1))]
    candidate, support, directional = enclose_field(point, D, directions, groups)
    old = source['coupled_rate']
    selected = old.copy()
    changed = select_first_variation(selected, candidate)
    if not all(a.overlaps(b) for a, b in zip(selected, point, strict=True)):
        raise ArithmeticError('uniform and anchor field enclosures disagree')
    for file in (Path(__file__), Path(reader.__file__), Path(cache.__file__),
                 Path(sys.modules[enclose_field.__module__].__file__),
                 Path(sys.modules[validate_segment_family.__module__].__file__),
                 Path(sys.modules[select_first_variation.__module__].__file__),
                 ROOT/'theory/n12_gate7_physical_field_mean_value.md'):
        p.geometry.residual.merge(source['binding']['files'], {p.df.file_key(file): p.values.sha(file)})
    p.verify_sources(source['binding'])
    arrays = dict(rate_candidate=selected, mean_value_rate=candidate, old_rate=old,
                  point_rate=point, field_support=support, scaled_directional_derivative=directional,
                  weighted_tube_directions=directions, raw_domain=source['raw_domain'])
    report = dict(family, endpoint=index, scope='SELECTED_FROZEN_AFFINE_ENDPOINT_TUBE',
        validation_passed=True, uniform_physical_value_enclosed=True, all_75_scaled_directions_used=True,
        complete_paired_uniform_derivative_used=True, full_verified_point_uncertainty_retained=True,
        coordinates_tightened=changed, original_maximum_radius_approx=float(max(v.rad() for v in old)),
        maximum_radius_approx=float(max(v.rad() for v in selected)),
        original_state_maximum_radius_approx=float(max(v.rad() for v in old[:98])),
        state_maximum_radius_approx=float(max(v.rad() for v in selected[:98])),
        positive_physical_G_norm=True, physical_G_norm_lower_rational=value['report']['physical_G_norm_lower_rational'],
        new_action_derivatives_evaluated=False, full_path_uniform_contraction=False,
        Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    return source, arrays, report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoint', type=int, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    ctx.prec = 512
    p, residual = reader.p, reader.p.geometry.residual
    targets = [(p.values, 'sha'), (residual.center, '_sha'), (residual.foundation.coordinate.center, '_sha')]
    with cache.cache_hashes(targets, excluded_roots=[args.out]):
        try:
            source, arrays, report = evaluate(args.endpoint)
            p.verify_sources(source['binding'])
            encoded = {}
            for name, a in arrays.items():
                encoded[name+'_mid_q'], encoded[name+'_rad_q'] = p.hs.rational_balls(a)
            data = args.out/'column.npz'
            np.savez_compressed(data, **encoded)
            record = dict(binding=source['binding'], endpoint=args.endpoint, report=report,
                          data_SHA256=p.values.sha(data), FULL_BHSM_COMPLETE=False)
            (args.out/'record.json').write_bytes(p.geometry.encoded(record))
            print(json.dumps(report), flush=True)
        except BaseException as error:
            (args.out/'failure.json').write_bytes(p.geometry.encoded(dict(error=repr(error), FULL_BHSM_COMPLETE=False)))
            raise


if __name__ == '__main__':
    main()
