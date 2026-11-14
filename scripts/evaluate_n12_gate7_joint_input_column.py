"""Saved-evidence joint-input enclosure test; never evaluates action derivatives.

This tests a relaxation, not the fully coupled physical graph. See the matching
theory note for the distinction and the missing coupled residual certificate.
"""
import os
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb, arb_mat, ctx


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def matrix(a):
    a = np.asarray(a, dtype=object)
    return arb_mat(*a.shape, list(a.flat))


def balls(path, names):
    with np.load(path, allow_pickle=False) as a:
        return {name: np.array([arb(str(m)) + arb(0, arb(str(r)))
                               for m, r in zip(a[name+'_mid_q'].flat,
                                               a[name+'_rad_q'].flat, strict=True)],
                              dtype=object).reshape(a[name+'_mid_q'].shape)
                for name in names}


def unit_groups(groups, n):
    used = []
    for g in groups:
        if g['norm'] not in ('interval', 'euclidean', 'box'):
            raise ValueError('unknown group norm')
        if not 0 <= g['start'] < g['stop'] <= n:
            raise ValueError('invalid group range')
        if g['norm'] == 'interval' and g['stop']-g['start'] != 1:
            raise ValueError('interval group must be scalar')
        used.extend(range(g['start'], g['stop']))
    if used != list(range(n)):
        raise ValueError('groups must partition every input direction')
    return groups


def row_support(values, groups):
    """Outward support over the product of unit balls; no input dropped."""
    groups = unit_groups(groups, len(values))
    total = arb(0)
    for g in groups:
        v = [abs(x).upper() for x in values[g['start']:g['stop']]]
        total += sum((x*x for x in v), arb(0)).sqrt() if g['norm'] == 'euclidean' else sum(v, arb(0))
    return total.upper()


def witness(groups, n):
    """Exact rational point inside every original unit group."""
    unit_groups(groups, n)
    result = [Fraction(0)]*n
    for g in groups:
        size = g['stop']-g['start']
        if g['norm'] == 'euclidean':
            denominator = 1
            while denominator**2 < size:
                denominator += 1
            value = Fraction(1, denominator)
            assert size*value**2 <= 1
        else:
            value = Fraction(1)
        result[g['start']:g['stop']] = [value]*size
    return result


def summarize(a):
    return dict(lower_exact=str(a.lower().fmpq()), upper_exact=str(a.upper().fmpq()),
                lower=float(a.lower()), upper=float(a.upper()))


def evaluate(root):
    # Use the unchanged LIVE readers only for source verification and saved
    # operands. None of their evaluate/graph routines is called.
    sys.path[:0] = [str(root/'scripts'), str(root/'src')]
    import diagnose_n12_gate7_directed_trial_hs_column as base
    p = base.p
    residual = p.geometry.residual
    paths = dict(
        midpoint=root/'tmp/bhsm_midpoint_center_mean_value_right_pair_20260913/value',
        endpoint=root/'tmp/bhsm_endpoint_trial_mean_value_bootstrap_right_pair_20260913/value',
        local=root/'tmp/bhsm_bootstrap_endpoint_midpoint_local_pair_20260913/value')
    records = {}
    sources = {}
    targets = [(p.values, 'sha'), (residual.center, '_sha'),
               (residual.foundation.coordinate.center, '_sha')]
    with base.cache.cache_hashes(targets):
        for name, pair in paths.items():
            record = json.loads((pair/'first/record.json').read_bytes())
            receipt = json.loads((pair/'reproduction.json').read_bytes())
            if not all(receipt.get(k) is True for k in
                       ('fresh_process', 'independent_recomputation', 'byte_identical')):
                raise ValueError('independent pair required')
            for filename in ('record.json', 'column.npz'):
                first, repeat = pair/'first'/filename, pair/'repeat'/filename
                if sha(first) != receipt['files_SHA256'][filename] or sha(repeat) != sha(first):
                    raise ValueError('paired evidence changed')
                sources[first.relative_to(root).as_posix()] = sha(first)
            sources[(pair/'reproduction.json').relative_to(root).as_posix()] = sha(pair/'reproduction.json')
            if record['interval'] != 13 or record['trial_column'] != 14:
                raise ValueError('wrong local domain')
            p.verify_sources(record['binding'])
            records[name] = record
        local = base.reader.load_inputs(13)
        # Each record may add provenance, but conflicting shared files or
        # normalized operands forbid reuse.
        combined = {}
        for record in [*records.values(), local]:
            binding = record['binding']
            residual.merge(combined, binding['files'])
            if binding['axes_SHA256'] != local['binding']['axes_SHA256']:
                raise ValueError('axes mismatch')
            if binding['normalized_inputs'] != local['binding']['normalized_inputs']:
                raise ValueError('normalized physical inputs mismatch')
        for name in ('midpoint', 'endpoint'):
            report = records[name]['report']
            if not all(report.get(k) is True for k in (
                'same_family_segment_smoothness_established',
                'complete_original_seven_solve_graph_used',
                'complete_original_scalar_contractions_used')):
                raise ValueError('full same-family physical graph required')
        dpath = root/'artifacts/flagship_integration/.coupled_hs_midpoint_domain_work/interval_013/record.json'
        domain = json.loads(dpath.read_bytes())
        if combined.get(dpath.relative_to(root).as_posix()) != sha(dpath):
            raise ValueError('midpoint group definition outside source binding')
        groups = unit_groups(domain['groups'], 249)
        a = balls(paths['midpoint']/'first/column.npz',
                  ['point_hessian', 'normalized_hessian', 'point_derivative', 'weighted_input_axis'])
        endpoint = balls(paths['endpoint']/'first/column.npz',
                         ['uniform_derivative', 'weighted_input_axis', 'point_derivative',
                          'point_hessian', 'normalized_hessian'])
        middle_path = root/'tmp/bhsm_split_directed_trial13_pair_20260913/midpoint_right/first/column.npz'
        if combined.get(middle_path.relative_to(root).as_posix()) != sha(middle_path):
            raise ValueError('original center direction outside shared binding')
        middle = balls(middle_path, ['center_directions'])
        if not all(x == y for x, y in zip(a['weighted_input_axis'], middle['center_directions'][:, 0], strict=True)):
            raise ValueError('midpoint center direction changed')
        trial = np.array([[arb(float(v))] for v in local['trial_right'][:, 14]], dtype=object)
        if not all(x == y for x, y in zip(trial[:, 0], endpoint['weighted_input_axis'], strict=True)):
            raise ValueError('endpoint trial direction changed')
        P = matrix(local['frozen_right']).solve(matrix(local['test']))
        h = arb(float(local['step']))
        axis_path = root/'artifacts/action_extension/BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.npz'
        with np.load(axis_path, allow_pickle=False) as z:
            raw = z['current_center_green_image_unit_mid']
        axes = np.zeros_like(raw)
        axes[1:] = raw[1:]/np.linalg.norm(raw[1:], axis=1)[:, None]
        digest = hashlib.sha256(np.asarray(axes, dtype='<f8').tobytes()).hexdigest().upper()
        if digest != local['binding']['axes_SHA256']:
            raise ValueError('output axes changed')
        axis = [arb(float(v)) for v in axes[14]]
        Q = arb_mat(74, 74, [arb(i == j)-axis[i]*axis[j] for i in range(74) for j in range(74)])
        S = Q*P*(2*h/3)
        H = matrix(a['normalized_hessian'])
        H0 = arb_mat(99, 249, [v.mid() for v in a['point_hessian'].flat])
        if not all(x.contains(y) for x, y in zip(a['normalized_hessian'].flat, a['point_hessian'].flat, strict=True)):
            raise ValueError('uniform Hessian does not contain verified point anchor')
        # Exact point center plus the full uniform-minus-center remainder.
        # This is the anchored integral form, not a pointwise substitution.
        E = H-H0
        signed_anchor, remaining = S*H0, S*E
        anchor_support = [row_support([signed_anchor[i,j] for j in range(249)], groups) for i in range(74)]
        remainder_support = [row_support([remaining[i,j] for j in range(249)], groups) for i in range(74)]
        norm = lambda v: sum((x*x for x in v), arb(0)).sqrt().upper()
        # Complete local column: keep endpoint uncertainty, full uniform DF,
        # the unchanged original w0, and the chain's center-shift term.
        e, A, w0, M = map(matrix, (trial, endpoint['point_derivative'], middle['center_directions'], local['midpoint_df']))
        a0 = arb_mat(99, 1, [v.mid() for v in A.entries()])
        endpoint_groups = [dict(start=0, stop=1, norm='interval'),
                           dict(start=1, stop=75, norm='euclidean')]
        # Endpoint producer scales its original longitudinal and transverse
        # directions before storing these 75 Hessian columns.
        if not records['endpoint']['report'].get('all_75_scaled_directions_verified'):
            raise ValueError('complete scaled endpoint domain required')
        if not all(x.contains(y) for x,y in zip(endpoint['normalized_hessian'].flat,
                                              endpoint['point_hessian'].flat, strict=True)):
            raise ValueError('endpoint Hessian must contain point anchor')
        HA0 = arb_mat(99, 75, [v.mid() for v in endpoint['point_hessian'].flat])
        EA = matrix(endpoint['normalized_hessian'])-HA0
        coefficient = Q*(P*(h/6)-P*M*(h*h/12))
        Alinear, Aremainder = coefficient*HA0, coefficient*EA
        endpoint_linear = [row_support([Alinear[i,j] for j in range(75)], endpoint_groups) for i in range(74)]
        endpoint_error = [row_support([Aremainder[i,j] for j in range(75)], endpoint_groups) for i in range(74)]
        fixed = arb_mat(74, 1, [arb(i == 14) for i in range(74)])-P*e
        K = Q*(fixed+(P*a0)*(h/6)+(P*matrix(a['point_derivative']))*(2*h/3)
               +(P*(h/6)-P*M*(h*h/12))*(A-a0)
               +(P*M*(e/2-a0*(h/8)-w0))*(2*h/3))
        full_upper = norm([abs(K[i,0]).upper()+anchor_support[i]+remainder_support[i]
                           +endpoint_linear[i]+endpoint_error[i] for i in range(74)])
        # At ONE fixed xi, independent Hessian coefficient errors can still
        # choose +/- row signs. This proves an obstruction for this explicitly
        # defined outer model. It does not assert physical attainability.
        xi = witness(groups, 249)
        # Use exact saved radii, rounded DOWN to a dyadic. Outward ball-loading
        # inflation must not create an artificial member of the source family.
        with np.load(paths['midpoint']/'first/column.npz', allow_pickle=False) as z:
            exact_radii = [[Fraction(str(v)) for v in row] for row in z['normalized_hessian_rad_q']]
        scale = 2**256
        inner = [[Fraction((r*scale).numerator//(r*scale).denominator, scale) for r in row]
                 for row in exact_radii]
        assert all(0 <= x <= r for xs,rs in zip(inner,exact_radii) for x,r in zip(xs,rs))
        radii = [arb(str(sum((v*x for v,x in zip(row,xi)), Fraction(0)))) for row in inner]
        # Choose signs to maximize transverse output coordinate 73.
        signs = [1 if S[73,i].mid() >= 0 else -1 for i in range(99)]
        delta = S*arb_mat(99, 1, [radii[i]*signs[i] for i in range(99)])
        gain = abs(delta[73,0])
        if not gain.lower() > 1:
            verdict = 'JOINT_INPUT_RELAXATION_NOT_DECIDED_BY_THIS_WITNESS'
        else:
            verdict = 'JOINT_INPUT_WITH_INDEPENDENT_HESSIAN_REMAINDER_CANNOT_CERTIFY_CONTRACTION'
        for path in (dpath, axis_path, middle_path):
            sources[path.relative_to(root).as_posix()] = sha(path)
        return dict(algorithm='SAVED_JOINT_INPUT_COLUMN_SUFFICIENCY_ARB512_V1', interval=13,
            trial_column=14, first_affected_output_node=14, claim=verdict,
            paired_source_hashes=sources, all_shared_source_bindings_checked=True,
            axes_SHA256=digest, groups=groups, group_radii_already_scaled_in_hessian=True,
            input_witness_rationals=list(map(str, xi)), row_error_signs=signs,
            signed_point_linearization_norm_upper=summarize(norm(anchor_support)),
            full_uniform_minus_point_remainder_norm_upper=summarize(norm(remainder_support)),
            endpoint_signed_point_linearization_norm_upper=summarize(norm(endpoint_linear)),
            endpoint_uniform_minus_point_remainder_norm_upper=summarize(norm(endpoint_error)),
            anchor_and_center_shift_norm_upper=summarize(norm([abs(K[i,0]).upper() for i in range(74)])),
            complete_local_transverse_column_norm_upper=summarize(full_upper),
            relaxation_gain_lower=summarize(gain),
            relaxation_contraction_margin_upper=summarize(1-gain),
            full_neighborhood_remainder_retained=True, point_anchor_uncertainty_retained=True,
            original_center_shift_retained=True, domain_shrunk=False,
            all_249_midpoint_directions_retained=True,
            all_75_endpoint_directions_retained=True,
            shared_input_across_output_rows_retained=True,
            shared_input_through_implicit_solves_recovered=False,
            midpoint_endpoint_attainability_relation_recovered=False,
            old_cartesian_corner_exclusion_proved=False,
            physical_noncontraction_proved=False, physical_global_margin=None,
            Gate7_closed=False, FULL_BHSM_COMPLETE=False, new_action_derivative_evaluations=0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence-root', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    ctx.prec = 512
    result = evaluate(args.evidence_root.resolve())
    result['evaluator_SHA256'] = sha(Path(__file__))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('xb') as f:
        f.write(encoded(result))
    print(json.dumps({k:result[k] for k in ('claim','signed_point_linearization_norm_upper',
        'full_uniform_minus_point_remainder_norm_upper','complete_local_transverse_column_norm_upper',
        'relaxation_gain_lower','physical_global_margin')}))


if __name__ == '__main__':
    main()
