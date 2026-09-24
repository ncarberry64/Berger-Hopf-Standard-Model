"""Transport one endpoint Hessian-variation path, without booking a ledger debit.

For endpoint j, the two fixed-midpoint-DF source factors are
R_(j-1)^-1 T_j h_(j-1)/6 (I-h_(j-1) DF_M/2) and
R_j^-1 T_(j+1) h_j/6 (I+h_j DF_M/2).
Their shared endpoint input is joined before subsequent projection/norms.
This isolates the endpoint-Hessian variation factor only. Midpoint-DF
variation, midpoint-Hessian variation, and other input directions remain open.
"""
import os
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import hashlib
import json
from pathlib import Path
import sys


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main(snapshot, diagnostic, budget_path, out):
    sys.path[:0] = [str(snapshot/'scripts'), str(snapshot/'src')]
    import numpy as np
    from flint import arb, arb_mat, ctx, fmpq
    import certify_n12_gate7_direct_physical_local_defects as local
    import derive_n12_gate7_full_direct_physical_jacobians as backend
    import bhsm_immutable_input_hash_cache as cache
    from bhsm.interface.direct_causal_quadratic import projected_norms
    from bhsm.interface.current_green_midpoint_coordinate_error import _float_upper
    from bhsm.interface.stored_causal_arithmetic_envelope import combine_stored_causal_errors, fixed_axis_projection_norms
    record_path = diagnostic/'record.json'
    record = json.loads(record_path.read_bytes())
    data_path = diagnostic/'hessian.npz'
    if record['data_SHA256'] != sha(data_path):
        raise ValueError('Uniform Hessian diagnostic data changed')
    j, column = record['endpoint'], record['column']
    if not 1 <= j < 370 or not 0 <= column < 99:
        raise ValueError('Interior endpoint and complete ambient column required')
    budget = json.loads(budget_path.read_bytes())
    geometry = json.loads((snapshot/'artifacts/flagship_integration/.direct_endpoint_neighborhood_work/endpoints.json').read_bytes())
    from fractions import Fraction
    radii = budget['operands']['original_radius']
    if geometry['radii_exact_binary64_rationals'] != [str(Fraction(v)) for v in radii]:
        raise ValueError('The original endpoint domain must not change')
    ctx.prec = 512
    with np.load(data_path, allow_pickle=False) as a:
        read = lambda name: local.df.values.hs.restore_balls(a[name+'_mid_q'], a[name+'_rad_q'])
        point, uniform = read('point_hessian'), read('uniform_hessian')
    if point.shape != (99, 1) or uniform.shape != point.shape:
        raise ValueError('Complete 99-output mixed variation required')
    delta = arb_mat(99, 1, list((uniform-point).flat))
    backend.install_backend()
    targets = [(local.df.values, 'sha'), (local.residual.center, '_sha')]
    with cache.cache_hashes(targets, excluded_roots=[out.parent]):
        source = local.load_inputs([j-1, j])
        ctx.prec = 512
        cert = local.residual.center.cert
        frame = arb_mat(cert._frame(source['tangents'][j], cert.TRIAL_DESCRIPTOR_SCALE).tolist())
        support = (sum(frame[column, k]**2 for k in range(74)).sqrt()*arb(radii[1])).upper()
        identity = arb_mat(np.eye(99, dtype=int).tolist())
        factors = []
        for i, sign in ((j-1, -1), (j, 1)):
            dependencies = local.df.point_inputs('midpoint', i, source['binding'])[-1]
            ctx.prec = 512
            derivative = local.df.load_cached('midpoint', i, source['binding'], dependencies)[0]
            df = arb_mat(99, 99, list(derivative.flat))
            test = arb_mat(cert._frame(source['tangents'][i+1], cert.TEST_DESCRIPTOR_SCALE).T.tolist())
            right = arb_mat(source['right'][i].tolist())
            h = arb(float(source['steps'][i]))
            factors.append(right.solve(test*(identity+sign*h*df/2))*(h/6))
        foundation, _, maps, axes = local.residual.load_foundation()
        joined = arb_mat(maps[j].tolist())*factors[0]+factors[1]
        suffix = arb_mat(np.eye(74, dtype=int).tolist())
        profile = []
        for node in range(j, 371):
            if node == j:
                operator = factors[0]
            else:
                if node > j+1:
                    suffix = arb_mat(maps[node-1].tolist())*suffix
                operator = suffix*joined
            l, t = projected_norms(operator*delta*support, axes[node])
            profile.append(dict(node=node, L=_float_upper(l), T=_float_upper(t)))
        centers = [max(row[k] for row in profile) for k in ('L', 'T')]
        lifted = combine_stored_causal_errors(centers, [], foundation['frozen_map_perturbation_gain_upper'], fixed_axis_projection_norms(axes))
    costs = lifted['frozen_map_transverse_quadratic_coefficients_upper']
    allowance = arb(fmpq(budget['rows'][1]['remaining_self_map_allowance']['exact']))
    payload = dict(algorithm='ISOLATED_ENDPOINT_MIXED_HESSIAN_VARIATION_TRANSPORT_DIAGNOSTIC_V1',
        endpoint=j, weighted_ambient_column=column,
        scope='ONE_LT_ENDPOINT_HESSIAN_VARIATION_FACTOR_WITH_FIXED_CENTER_MIDPOINT_DF',
        frozen_map_value_cost_upper=costs, transverse_allowance_lower=budget['rows'][1]['remaining_self_map_allowance']['lower'],
        fits_entire_remaining_transverse_allowance=bool(arb(costs[1]) < allowance),
        same_endpoint_operator_factors_joined_before_projection=True,
        longitudinal_radius_already_in_hessian_axis=True,
        transverse_coordinate_support_upper=_float_upper(support),
        mixed_factor_two_cancels_Taylor_half=True,
        maximum_gain_nodes={k: max(profile, key=lambda v: v[k])['node'] for k in ('L', 'T')},
        largest_ambient_remainder_output=max(range(99), key=lambda i: float(abs(delta[i, 0]).upper())),
        diagnostic_independently_reproduced=False, ledger_debit_added=False,
        missing_factors=['Midpoint DF variation and its cross term', 'Midpoint Hessian variation',
                        'Other LL/LT/TT directions and endpoints', 'Derivative remainder'],
        mathematical_inequality_violation_proved=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False,
        source_SHA256={str(p.resolve()): sha(p) for p in (record_path, data_path, budget_path, Path(__file__))},
        profile=profile)
    with out.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(payload, indent=2, sort_keys=True)+'\n')
    print(json.dumps({k: v for k, v in payload.items() if k not in ('profile', 'source_SHA256')}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for key in ('snapshot', 'diagnostic', 'budget', 'out'):
        parser.add_argument('--'+key, type=Path, required=True)
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    main(args.snapshot.resolve(), args.diagnostic.resolve(), args.budget.resolve(), args.out.resolve())
