"""Transport a unit residual in DR[73,14]; do not estimate that residual."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb, arb_mat, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from bhsm.interface.direct_causal_quadratic import projected_norms
from bhsm.interface.current_green_midpoint_coordinate_error import _float_upper
from bhsm.interface.stored_causal_arithmetic_envelope import (
    combine_stored_causal_errors, fixed_axis_projection_norms)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def exact_bound(value):
    return dict(exact=str(value.fmpq()), approximate=float(value))


def evaluate(root, budget_path, out):
    ctx.prec = 512
    base = root/'artifacts/flagship_integration'
    foundation_path = base/'BHSM_N12_GATE7_STORED_CAUSAL_ARITHMETIC_ENVELOPE.json'
    maps_path = base/'BHSM_N12_GATE7_CURRENT_GREEN_SIGNED_TRANSVERSE_CAUSAL_CENTER.npz'
    axes_path = root/'artifacts/action_extension/BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.npz'
    foundation = json.loads(foundation_path.read_bytes())
    budget = json.loads(budget_path.read_bytes())
    with np.load(maps_path, allow_pickle=False) as z:
        maps = z['causal_maps_center'].copy()
    with np.load(axes_path, allow_pickle=False) as z:
        axes = z['current_center_green_image_unit_mid'].copy()
    axes[1:] /= np.linalg.norm(axes[1:], axis=1)[:, None]
    axes[0] = 0
    for values, name in ((maps, 'causal_maps'), (axes, 'axes')):
        digest = hashlib.sha256(np.asarray(values, dtype='<f8').tobytes()).hexdigest().upper()
        if digest != foundation[name+'_SHA256']:
            raise ValueError('Original frozen maps and axes required')
    if maps.shape != (370,74,74) or axes.shape != (371,74):
        raise ValueError('Complete original history required')
    # A derivative residual delta(theta) e_73 e_14^T is injected at node 15.
    current = arb_mat(74, 1, [arb(i == 73) for i in range(74)])
    profile = []
    for node in range(15,371):
        if node > 15:
            current = arb_mat(maps[node-1].tolist())*current
        l, t = projected_norms(current, axes[node])
        profile.append(dict(node=node, L=_float_upper(l), T=_float_upper(t)))
    centers = [max(row[k] for row in profile) for k in ('L','T')]
    lifted = combine_stored_causal_errors(centers, [],
        foundation['frozen_map_perturbation_gain_upper'], fixed_axis_projection_norms(axes))
    gains = lifted['frozen_map_transverse_quadratic_coefficients_upper']
    r = budget['operands']['original_radius']
    rho = (abs(arb(float(axes[15,14])))*arb(r[0])+arb(r[1])).upper()
    # T is relaxed to the existing complete Euclidean input superset. The
    # physical vector is not replaced with an independent coordinate box.
    cost = (rho*arb(gains[1])).upper()
    allowance = arb(budget['rows'][1]['remaining_self_map_allowance']['exact'])
    threshold = (allowance/cost).lower()
    if not threshold > 0:
        raise ArithmeticError('Positive residual allowance required')
    payload = dict(algorithm='INTERVAL14_ENTRY_REMAINDER_TRANSFER_BUDGET_ARB512_V1',
        interval=14, output_coordinate=73, input_coordinate=14, injected_at_node=15,
        scope='CONDITIONAL_RANK_ONE_DERIVATIVE_REMAINDER_SENSITIVITY_NOT_AN_ENTRY_ENCLOSURE',
        source_axis_coordinate=float(axes[15,14]), input_coordinate_support_upper=exact_bound(rho),
        exact_stored_map_projection_gains_upper=centers,
        frozen_map_projection_gains_upper=gains,
        maximum_center_gain_nodes={key:max(profile,key=lambda row:row[key])['node'] for key in ('L','T')},
        transverse_value_cost_per_unit_unaccounted_derivative_entry_upper=exact_bound(cost),
        available_total_transverse_remainder_budget_lower=exact_bound(allowance.lower()),
        sufficient_entry_error_upper_limit_if_entire_budget_assigned=exact_bound(threshold),
        sufficient_entry_error_upper_limit_if_one_tenth_budget_assigned=exact_bound((threshold/10).lower()),
        actual_entry_remainder_bound=None,
        derivative_entry_means='The unaccounted derivative remainder after the already booked center and selected LL/LT terms, not the full DR entry.',
        no_half_factor_assumed=True,
        other_missing_paths_must_share_budget=True,
        rank_one_path_split_may_discard_useful_cross_output_correlations=True,
        local_interval13_reopened=False, Gate7_closed=False,
        profile=profile, map_perturbation=lifted,
        source_SHA256={str(p.resolve()):sha(p) for p in (foundation_path,maps_path,axes_path,budget_path,Path(__file__))})
    with out.open('xb') as stream:
        stream.write((json.dumps(payload,sort_keys=True,indent=2)+'\n').encode())
    print(json.dumps({k:v for k,v in payload.items() if k not in ('profile','source_SHA256','map_perturbation')},indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence-root', type=Path, required=True)
    parser.add_argument('--budget', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    evaluate(args.evidence_root.resolve(), args.budget.resolve(), args.out)
