"""Compare equivalent local tail associations using only paired physical operands."""
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
THEORY = base.ROOT/'theory/n12_gate7_preconditioned_split_trial_column.md'
ALGORITHM = 'PRECONDITIONED_CENTER_SPLIT_FROZEN_TRIAL_COLUMN_ARB512_V1'


def evaluate(args):
    source = base.reader.load_inputs(args.interval)
    previous_record, previous, previous_files = base.read_pair(args.evidence_root/'local')
    if (previous_record.get('algorithm') != base.ALGORITHM
            or previous_record.get('stage') != 'assemble'
            or previous_record.get('interval') != args.interval
            or previous_record.get('trial_column') != args.column
            or previous_record['report'].get('paired_center_split_midpoint_directions') is not True):
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
            record, values, files = base.read_pair(args.evidence_root/(stage+'_'+side))
            base.validate_directed(record, stage, side, args)
            p.geometry.residual.merge(source['binding']['files'], record['binding']['files'])
            base.bind(source, *files)
            evidence[stage] = values
        trial = np.array([[arb(float(v))] for v in source['trial_'+side][:, args.column]], dtype=object)
        middle = evidence['midpoint']
        candidates = algebra.local_columns(trial, evidence['endpoint']['selected'],
            middle['center_directions'], middle['center_derivative'], middle['direction_tail'],
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
        reports[name] = dict(previous_maximum_radius=float(max(v.rad() for v in previous[name].flat)),
            selected_maximum_radius=float(max(v.rad() for v in selected.flat)), methods=methods,
            coordinates_tightened=sum(a.rad() < b.rad() for a, b in zip(selected.flat, previous[name].flat)))
    base.bind(source, Path(__file__), Path(algebra.__file__), THEORY,
              Path(split_producer.__file__), Path(base.__file__))
    p.verify_sources(source['binding'])
    return source, arrays, dict(columns=reports, paired_center_split_operands_used=True,
        new_action_derivative_evaluations=0, center_rounding_remainder_included=True,
        fixed_preconditioner_before_uncertain_tail=True, shared_endpoint_tail_coefficient_used=True,
        full_trial_basis_enclosed=False, physical_quotient_identified=False,
        state_dependent_frame_derivatives_enclosed=False, complete_causal_Z1_enclosed=False,
        Gate7_closed=False, FULL_BHSM_COMPLETE=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', type=int, default=13)
    parser.add_argument('--column', type=int, default=14)
    parser.add_argument('--evidence-root', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if not 0 < args.interval < 370 or not 0 <= args.column < 74:
        raise ValueError('interior interval and valid frozen trial column required')
    args.out, args.evidence_root = args.out.resolve(), args.evidence_root.resolve()
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
