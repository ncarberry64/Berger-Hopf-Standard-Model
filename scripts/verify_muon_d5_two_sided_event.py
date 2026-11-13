"""Verify reproducibility, original saved rows and explicitly open physics."""
from __future__ import annotations
from pathlib import Path
import argparse
import json
import sys
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT)]
from scripts.evaluate_muon_d5_two_sided_event import verified_cores, pin


def verify(first, second):
    first, second = Path(first), Path(second)
    names = sorted(p.name for p in first.iterdir() if p.is_file())
    if names != sorted(p.name for p in second.iterdir() if p.is_file()):
        raise ValueError('materialized file sets differ')
    for name in names:
        if (first / name).read_bytes() != (second / name).read_bytes():
            raise ValueError('materializations differ: ' + name)
    reports, _ = verified_cores()
    result = json.loads((first / 'result.json').read_bytes())
    for rel, h in result['input_sha256'].items():
        if pin(ROOT / rel) != h:
            raise ValueError('input changed: ' + rel)
    if result['parent_head'] != '67c113ea5ba2d1558e694a2db02d9e3b245a1e1b':
        raise ValueError('ancestry changed')
    if pin(first / 'application.npz') != result['arrays']['sha256']:
        raise ValueError('assembled rows changed')
    with np.load(first / 'application.npz', allow_pickle=False) as z:
        if sorted(z.files) != result['arrays']['keys']:
            raise ValueError('array identities changed')
        for key in z.files:
            if z[key].dtype.hasobject or not np.isfinite(z[key]).all():
                raise ValueError('nonfinite/non-numeric array: ' + key)
        for index in (2, 3):
            p = 'candidate_' + str(index) + '_'
            J, K = z[p + 'full17_gradient'], z[p + 'full17_kernel']
            if J.shape != (17, 555) or K.shape != (555, 538):
                raise ValueError('coordinate space changed')
            if np.max(abs(J @ K)) > 1e-12:
                raise ValueError('retained kernel violates original rows')
            if np.max(abs(J @ z[p + 'full17_chart_source'])) > 1e-12:
                raise ValueError('two-sided source constraints changed')
            if z[p + 'known_normal_weak_source_affine_coefficients'].shape != (4, 29):
                raise ValueError('constraint multipliers lost')
    for side in ('plus', 'minus'):
        q = reports['PARENT_H_CONSUMER_v1']['report'][side]
        if q['hcount'] != 3660 or q['h_selected'] or q['delta_h_selected']:
            raise ValueError('homogeneous physical state assigned')
        if not q['original_sparse_h_basis_checks']['old6times']['source_max'] > 2e-10:
            raise ValueError('recorded source nonpass removed')
    for key in ('physical_event_residual', 'physical_outer_residual',
                'normal_profile_normalization', 'full_formation_residual',
                'complete_action_Hessian', 'original_physical_norm_residual'):
        if result[key] is not None:
            raise ValueError('unexecuted physical equation promoted: ' + key)
    for key in ('physical_admission', 'complete_physical_derivative',
                'local_native_accounting_changed', 'homogeneous_state_selected',
                'homogeneous_variation_selected', 'independent_normal_rates_selected'):
        if result[key] is not False:
            raise ValueError('physical scope changed: ' + key)
    if result['physical_guard'] != 2e-10:
        raise ValueError('physical guard changed')
    return dict(schema='bhsm.two-sided-event-verification.v1', byte_identical=True,
                result_sha256=pin(first / 'result.json'),
                arrays_sha256=pin(first / 'application.npz'),
                immutable_application_count=len(reports),
                executed_fixed_point_rank=17, remaining_chart_kernel=538,
                homogeneous_coordinates_retained=3660, physical_admission=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('first', type=Path)
    parser.add_argument('second', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.first, args.second), sort_keys=True, indent=2))
