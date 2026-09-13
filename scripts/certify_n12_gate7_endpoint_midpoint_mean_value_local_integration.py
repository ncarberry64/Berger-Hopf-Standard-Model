"""Integrate paired endpoint and midpoint-center mean-value actions in the local HS column."""
import os
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import json
from pathlib import Path
import numpy as np
from flint import arb, ctx
import diagnose_n12_gate7_split_directed_trial_hs_column as split_producer
from bhsm.interface import preconditioned_split_hs_column as algebra

base = split_producer.base
p = base.p
THEORY = base.ROOT/'theory/n12_gate7_endpoint_midpoint_mean_value_local_integration.md'
ALGORITHM = 'MEAN_VALUE_ENDPOINT_AND_MIDPOINT_CENTER_LOCAL_COLUMN_ARB512_V1'


def evaluate(args):
    source = base.reader.load_inputs(args.interval)
    previous_record, previous, previous_files = base.read_pair(args.previous_pair)
    if (previous_record.get('algorithm') != 'MEAN_VALUE_ENDPOINT_TRIAL_FIXED_FRAME_LOCAL_COLUMN_ARB512_V1'
            or previous_record.get('interval') != args.interval
            or previous_record.get('trial_column') != args.column
            or previous_record['report'].get('paired_uniform_mean_value_endpoint_actions_used') is not True):
        raise ValueError('paired center-split local comparison required')
    for key, value in source['binding'].items():
        if key == 'files':
            if any(previous_record['binding']['files'].get(name) != digest for name, digest in value.items()):
                raise ValueError('local physical operands changed')
        elif previous_record['binding'].get(key) != value:
            raise ValueError('local frozen geometry changed: '+key)
    p.geometry.residual.merge(source['binding']['files'], previous_record['binding']['files'])
    base.bind(source, *previous_files)
    arrays, reports = {}, {}
    for side, name in (('left', 'DL'), ('right', 'DR')):
        evidence = {}
        for stage in ('endpoint', 'midpoint'):
            if stage == 'endpoint':
                record, values, files = base.read_pair(args.mean_value_root/side)
                report = record.get('report', {})
                if (record.get('algorithm') != 'UNIFORM_FROZEN_TRIAL_MEAN_VALUE_DERIVATIVE_ARB512_V1'
                        or record.get('interval') != args.interval or record.get('trial_column') != args.column
                        or record.get('side') != side
                        or not all(report.get(key) is True for key in ('uniform_derivative_column_enclosed',
                            'same_family_segment_smoothness_established', 'all_75_scaled_directions_verified',
                            'complete_original_seven_solve_graph_used', 'complete_original_scalar_contractions_used',
                            'all_75_point_columns_contained'))):
                    raise ValueError('paired complete same-family trial mean-value enclosure required')
                for key in ('point_eigenpair_checks', 'point_derivative_checks'):
                    checks = report.get(key, [])
                    if len(checks) != 1 or not p.proof_valid(checks[0]):
                        raise ValueError('verified mean-value point anchor required')
            else:
                record, values, files = base.read_pair(args.evidence_root/(stage+'_'+side))
                base.validate_directed(record, stage, side, args)
            p.geometry.residual.merge(source['binding']['files'], record['binding']['files'])
            base.bind(source, *files)
            evidence[stage] = values
        trial = np.array([[arb(float(v))] for v in source['trial_'+side][:, args.column]], dtype=object)
        middle = evidence['midpoint']
        midpoint_pair = args.midpoint_left_pair if side == 'left' else args.midpoint_right_pair
        midpoint_record, midpoint_values, midpoint_files = base.read_pair(midpoint_pair)
        midpoint_report = midpoint_record.get('report', {})
        required = ('uniform_midpoint_center_derivative_enclosed',
                    'same_family_segment_smoothness_established', 'all_249_scaled_directions_verified',
                    'complete_original_seven_solve_graph_used', 'complete_original_scalar_contractions_used',
                    'all_249_point_columns_contained')
        if (midpoint_record.get('algorithm') != 'UNIFORM_ACTUAL_MIDPOINT_CENTER_DIRECTION_MEAN_VALUE_ARB512_V1'
                or midpoint_record.get('interval') != args.interval
                or midpoint_record.get('trial_column') != args.column
                or midpoint_record.get('side') != side
                or not all(midpoint_report.get(key) is True for key in required)):
            raise ValueError('paired complete actual midpoint center-action mean-value bound required')
        for key in ('point_eigenpair_checks', 'point_derivative_checks'):
            checks = midpoint_report.get(key, [])
            if len(checks) != 1 or not p.proof_valid(checks[0]):
                raise ValueError('verified midpoint mean-value point anchor required')
        if (midpoint_values['weighted_input_axis'].shape != (99,)
                or not all(a == b for a,b in zip(midpoint_values['weighted_input_axis'],
                                                middle['center_directions'][:,0], strict=True))):
            raise ValueError('original exact midpoint direction changed')
        center_action = midpoint_values['uniform_center_derivative']
        if center_action.shape != (99,1):
            raise ValueError('complete midpoint center derivative required')
        if not all(a.overlaps(b) for a,b in zip(center_action.flat,middle['center_derivative'].flat,strict=True)):
            raise ValueError('paired midpoint center actions disagree')
        p.geometry.residual.merge(source['binding']['files'], midpoint_record['binding']['files'])
        base.bind(source, *midpoint_files)
        arrays[name+'_old_midpoint_center_action'] = middle['center_derivative']
        arrays[name+'_midpoint_center_action'] = center_action
        middle = dict(middle, center_derivative=center_action)
        endpoint_action = evidence['endpoint']['uniform_derivative']
        if endpoint_action.shape != (99, 1):
            raise ValueError('complete mean-value trial action required')
        if not all(a == b for a, b in zip(evidence['endpoint']['weighted_input_axis'], trial[:, 0], strict=True)):
            raise ValueError('mean-value action and local frozen trial axes differ')
        new_chain = base.array(base.chain.chain_direction(trial, endpoint_action, source['step'], side))
        tail = new_chain-middle['center_directions']
        candidates = algebra.local_columns(trial, endpoint_action,
            middle['center_directions'], middle['center_derivative'], tail,
            source['midpoint_df'], source['step'], source['test'], source['frozen_left'],
            source['frozen_right'], args.column, side)
        selected = previous[name].copy()
        if selected.shape != (74, 1):
            raise ValueError('complete paired local column required')
        methods = {}
        for key, result in candidates.items():
            candidate = base.array(result)
            changed = base.select_first_variation(selected[:, 0], candidate[:, 0])
            arrays[name+'_'+key] = candidate
            methods[key] = dict(maximum_radius=float(max(v.rad() for v in candidate.flat)),
                                coordinates_selected=changed)
        arrays[name] = selected
        arrays[name+'_previous'] = previous[name]
        arrays[name+'_endpoint_action'] = endpoint_action
        arrays[name+'_chain_tail'] = tail
        reports[name] = dict(previous_maximum_radius=float(max(v.rad() for v in previous[name].flat)),
            selected_maximum_radius=float(max(v.rad() for v in selected.flat)), methods=methods,
            coordinates_tightened=sum(a.rad() < b.rad() for a, b in zip(selected.flat, previous[name].flat)))
    base.bind(source, Path(__file__), Path(algebra.__file__), THEORY,
              Path(split_producer.__file__), Path(base.__file__))
    p.verify_sources(source['binding'])
    return source, arrays, dict(columns=reports, paired_center_split_operands_used=True,
        new_action_derivative_evaluations=0, paired_uniform_mean_value_endpoint_actions_used=True,
        paired_uniform_mean_value_midpoint_center_actions_used=True, original_exact_midpoint_center_direction_reused=True, center_rounding_remainder_included=True,
        fixed_preconditioner_before_uncertain_tail=True, shared_endpoint_tail_coefficient_used=True,
        full_trial_basis_enclosed=False, physical_quotient_identified=False,
        state_dependent_frame_derivatives_enclosed=False, complete_causal_Z1_enclosed=False,
        Gate7_closed=False, FULL_BHSM_COMPLETE=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', type=int, default=13)
    parser.add_argument('--column', type=int, default=14)
    parser.add_argument('--evidence-root', type=Path, required=True)
    parser.add_argument('--mean-value-root', type=Path, required=True)
    parser.add_argument('--previous-pair', type=Path, required=True)
    parser.add_argument('--midpoint-left-pair', type=Path, required=True)
    parser.add_argument('--midpoint-right-pair', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if not 0 < args.interval < 370 or not 0 <= args.column < 74:
        raise ValueError('interior interval and valid frozen trial column required')
    args.out, args.evidence_root = args.out.resolve(), args.evidence_root.resolve()
    args.mean_value_root, args.previous_pair = args.mean_value_root.resolve(), args.previous_pair.resolve()
    args.midpoint_left_pair, args.midpoint_right_pair = args.midpoint_left_pair.resolve(), args.midpoint_right_pair.resolve()
    args.out.mkdir(parents=True, exist_ok=False)
    ctx.prec = 512
    residual = p.geometry.residual
    targets = [(p.values, 'sha'), (residual.center, '_sha'), (residual.foundation.coordinate.center, '_sha')]
    with base.cache.cache_hashes(targets, excluded_roots=[args.out]):
        try:
            source, arrays, report = evaluate(args)
            encoded = {}
            for name, values in arrays.items():
                encoded[name+'_mid_q'], encoded[name+'_rad_q'] = p.hs.rational_balls(values)
            data = args.out/'column.npz'
            np.savez_compressed(data, **encoded)
            record = dict(algorithm=ALGORITHM, binding=source['binding'], interval=args.interval,
                trial_column=args.column, data_SHA256=p.values.sha(data), report=report,
                FULL_BHSM_COMPLETE=False)
            (args.out/'record.json').write_bytes(p.geometry.encoded(record))
            print(json.dumps(report), flush=True)
        except BaseException as error:
            (args.out/'failure.json').write_bytes(p.geometry.encoded(dict(error=repr(error), FULL_BHSM_COMPLETE=False)))
            raise


if __name__ == '__main__':
    main()
