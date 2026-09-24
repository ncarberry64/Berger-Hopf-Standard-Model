"""Verify the retained left family without changing the right certificate."""
from fractions import Fraction
import json
from pathlib import Path
import numpy as np
import evaluate_n12_gate7_coupled_residual_saved as right
from evaluate_n12_gate7_coupled_residual_saved import encoded, read_matrix, sha


PAIRS = {
    'midpoint': ('bhsm_midpoint_center_mean_value_left_pair_20260913',
        '.coupled_midpoint_eigenpair_pilot_work/interval_013',
        '7CF04181215807C5449E8F47CE6B41933497912F69FAE869E6E523BA460A5691',
        'E2C49D9A0D135B6F4EA35E7605B105802BA787FD56FCA4E7B294FD1AC5F655EF'),
    'endpoint': ('bhsm_endpoint_trial_mean_value_bootstrap_left_pair_20260913',
        '.affine_eigenpair_pilot_work/endpoint_013',
        'CA8CDDDED6F5D87C7FA4D6A277F2008CC40F4DE0C10AA3F674635E3D68F074AD',
        'C94446B438086EC958A9A056AFFA36BF707A25425DC94AB8690283DA89086493'),
}


def evaluate(root):
    original = right.evaluate(root)
    import diagnose_n12_gate7_directed_trial_hs_column as base
    p = base.p
    residual = p.geometry.residual
    sources = dict(original['paired_source_hashes'])
    families = {}
    with base.cache.cache_hashes([(p.values, 'sha'), (residual.center, '_sha'),
                                 (residual.foundation.coordinate.center, '_sha')]):
        for family, (pair, eigenname, record_hash, data_hash) in PAIRS.items():
            directory = root/'tmp'/pair/'value'
            record = json.loads((directory/'first/record.json').read_bytes())
            receipt = json.loads((directory/'reproduction.json').read_bytes())
            if (record.get('side') != 'left' or record.get('interval') != 13
                    or record.get('trial_column') != 14
                    or record.get('data_SHA256') != data_hash
                    or any(receipt.get(k) is not True for k in
                           ('byte_identical', 'fresh_process', 'independent_recomputation'))):
                raise ValueError('matching independently reproduced left family required')
            for filename, expected in [('record.json', record_hash), ('column.npz', data_hash)]:
                first = directory/'first'/filename
                if (sha(first) != expected or sha(directory/'repeat'/filename) != expected
                        or receipt['files_SHA256'].get(filename) != expected):
                    raise ValueError('pinned left source bytes changed')
                sources[first.relative_to(root).as_posix()] = expected
            receipt_path = directory/'reproduction.json'
            sources[receipt_path.relative_to(root).as_posix()] = sha(receipt_path)
            report = record['report']
            if any(report.get(k) is not True for k in (
                    'same_family_segment_smoothness_established',
                    'complete_original_seven_solve_graph_used',
                    'complete_original_scalar_contractions_used')):
                raise ValueError('complete smooth original implicit family required')
            p.verify_sources(record['binding'])
            eigenpath = root/'artifacts/flagship_integration'/eigenname/'eigenpair.npz'
            key = eigenpath.relative_to(root).as_posix()
            if record['binding']['files'].get(key) != sha(eigenpath):
                raise ValueError('left eigenpair outside original source binding')
            sources[key] = sha(eigenpath)
            dimension = 249 if family == 'midpoint' else 75
            with np.load(directory/'first/column.npz', allow_pickle=False) as z:
                shapes = [read_matrix(z, f'point_center_{i}').ncols() for i in range(7)]
                if shapes != [1, 1, 1, dimension, dimension, dimension, dimension]:
                    raise ValueError('all seven left predictor arrays required')
                if family == 'midpoint':
                    other = root/'tmp/bhsm_midpoint_center_mean_value_right_pair_20260913/value/first/column.npz'
                    with np.load(other, allow_pickle=False) as rz:
                        # Only input-independent base data can be reused.
                        names = ('raw_domain', 'weighted_tube_directions', 'point_center_0',
                                 'point_center_3', 'point_center_4', 'uniform_solve_0', 'uniform_solve_4')
                        for name in names:
                            for suffix in ('_mid_q', '_rad_q'):
                                if not np.array_equal(z[name+suffix], rz[name+suffix]):
                                    raise ValueError('midpoint base reuse requires identical exact arrays')
            q = max(Fraction(item['weighted_contraction_upper_rational'])
                    for batch in report['solve_proofs'] for item in batch)
            if not 0 <= q < 1:
                raise ValueError('same-family bordered inclusion required')
            families[family] = dict(parameters=dimension,
                groups=original['families'][family]['groups'],
                original_bordered_contraction_upper_exact=str(q),
                original_bordered_contraction_upper=float(q),
                midpoint_base_arrays_identical_to_right=(family == 'midpoint'))
            p.verify_sources(record['binding'])
    return dict(algorithm='PINNED_LEFT_SHARED_FAMILY_VERIFICATION_V1', side='left',
        interval=13, paired_source_hashes=sources, families=families,
        original_physical_domain_shrunk=False, full_input_bound_certified=False,
        Gate7_closed=False, FULL_BHSM_COMPLETE=False,
        implementation_SHA256=sha(Path(__file__)))
