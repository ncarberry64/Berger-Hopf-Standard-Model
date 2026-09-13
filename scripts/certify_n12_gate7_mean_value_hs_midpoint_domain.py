"""Construct an actual HS domain from independently paired mean-value fields."""
import os
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
from pathlib import Path
import json
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
import certify_n12_gate7_coupled_hs_midpoint_domain as base
import bhsm_immutable_input_hash_cache as cache

engine, p = base.engine, base.p
original_load, original_main, original_theory = base.load_inputs, base.main, engine.THEORY
FIELD_WORK = ROOT/'artifacts/flagship_integration/.mean_value_endpoint_field_work'
WORK = engine.WORK = ROOT/'artifacts/flagship_integration/.mean_value_hs_midpoint_domain_work'
THEORY = engine.THEORY = ROOT/'theory/n12_gate7_physical_field_mean_value.md'
ALGORITHM = engine.ALGORITHM = 'MEAN_VALUE_ENDPOINT_FIELD_ACTUAL_HS_DOMAIN_ARB512_V1'


def load_inputs(index):
    source = original_load(index)
    for side, endpoint in (('left', index), ('right', index+1)):
        pair = FIELD_WORK/f'endpoint_{endpoint:03d}'
        path, data, receipt_path = pair/'first/record.json', pair/'first/column.npz', pair/'reproduction.json'
        record, receipt = json.loads(path.read_bytes()), json.loads(receipt_path.read_bytes())
        report = record.get('report', {})
        if (record.get('endpoint') != endpoint or path.read_bytes() != p.geometry.encoded(record)
                or report.get('validation_passed') is not True
                or report.get('uniform_physical_value_enclosed') is not True
                or report.get('scope') != 'SELECTED_FROZEN_AFFINE_ENDPOINT_TUBE'
                or report.get('all_75_scaled_directions_used') is not True
                or report.get('complete_paired_uniform_derivative_used') is not True
                or report.get('full_verified_point_uncertainty_retained') is not True
                or receipt.get('independent_recomputation') is not True
                or receipt.get('byte_identical') is not True or receipt.get('fresh_process') is not True
                or record.get('data_SHA256') != p.values.sha(data)):
            raise ValueError('paired complete physical mean-value field required')
        for file in (path, data):
            if receipt['files_SHA256'].get(file.name) != p.values.sha(file):
                raise ValueError('paired mean-value field evidence changed')
        reference = source[side]['binding']
        for name, value in reference.items():
            if name == 'files':
                if any(record['binding']['files'].get(file) != digest for file, digest in value.items()):
                    raise ValueError('endpoint field physical-domain dependency changed')
            elif name != 'algorithm' and record['binding'].get(name) != value:
                raise ValueError('endpoint field geometry changed: ' + name)
        p.verify_sources(record['binding'])
        p.geometry.residual.merge(source['binding']['files'], record['binding']['files'])
        with np.load(data, allow_pickle=False) as a:
            field = p.hs.restore_balls(a['rate_candidate_mid_q'], a['rate_candidate_rad_q'])
        if field.shape != (99,) or not all(v.is_finite() for v in field):
            raise ValueError('complete finite physical field required')
        if not all(a.overlaps(b) for a, b in zip(field, source[side+'_rate'], strict=True)):
            raise ArithmeticError('same-family endpoint field enclosures disagree')
        source[side+'_rate'] = field
        for file in (path, data, receipt_path):
            p.geometry.residual.merge(source['binding']['files'], {p.df.file_key(file): p.values.sha(file)})
    for file in (Path(__file__), Path(base.__file__), Path(cache.__file__), original_theory, THEORY):
        p.geometry.residual.merge(source['binding']['files'], {p.df.file_key(file): p.values.sha(file)})
    p.verify_sources(source['binding'])
    return source


engine.load_inputs = load_inputs
evaluate = base.evaluate


def main():
    r = p.geometry.residual
    targets = [(p.values, 'sha'), (r.center, '_sha'), (r.foundation.coordinate.center, '_sha')]
    with cache.cache_hashes(targets, excluded_roots=[WORK]):
        original_main()


if __name__ == '__main__':
    main()
