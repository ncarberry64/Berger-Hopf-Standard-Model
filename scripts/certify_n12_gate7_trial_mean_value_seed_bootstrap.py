"""Bootstrap one frozen trial derivative from independently paired same-family mean-value seeds."""
import os
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import json
from pathlib import Path
import numpy as np
from flint import ctx
import diagnose_n12_gate7_directed_trial_hs_column as base
import n12_gate7_trial_uniform_mixed_variation as mixed
from bhsm.interface.affine_segment_family import validate_segment_family

p = base.p
ALGORITHM = 'BOOTSTRAP_UNIFORM_FROZEN_TRIAL_MEAN_VALUE_DERIVATIVE_ARB512_V1'
THEORY = base.ROOT/'theory/n12_gate7_trial_mean_value_seed_bootstrap.md'


def evaluate(args):
    index = args.interval+(args.side == 'right')
    engine, source, _, selections = base.load_stage(index, 'endpoint', args.primal_pair)
    record, directional, files = base.read_pair(args.evidence_root/('endpoint_'+args.side))
    base.validate_directed(record, 'endpoint', args.side, args)
    for key, value in source['binding'].items():
        if key == 'files':
            if any(record['binding']['files'].get(name) != digest for name, digest in value.items()):
                raise ValueError('directed seed and mixed derivative physical inputs differ')
        elif record['binding'].get(key) != value:
            raise ValueError('directed seed geometry differs: '+key)
    p.geometry.residual.merge(source['binding']['files'], record['binding']['files'])
    base.bind(source, *files)
    full_data = base.ROOT/f'artifacts/flagship_integration/.primal_mean_value_component_centered_endpoint_uniform_df_work/endpoint_{index:03d}/derivative.npz'
    if source['binding']['files'].get(p.df.file_key(full_data)) != p.values.sha(full_data):
        raise ValueError('full first-variation seeds must be in the verified derivative binding')
    with np.load(full_data, allow_pickle=False) as a:
        line = p.hs.restore_balls(a['selected_line_variation_mid_q'], a['selected_line_variation_rad_q'])
        response = p.hs.restore_balls(a['response_variation_mid_q'], a['response_variation_rad_q'])
    if (line.shape != (62, 99) or response.shape != (62, 99)
            or directional['selected_line_variation'].shape != (62, 1)
            or directional['response_variation'].shape != (62, 1)):
        raise ValueError('complete paired first-variation seed matrices required')
    source.update(_axis_seed_line=directional['selected_line_variation'],
                  _axis_seed_response=directional['response_variation'],
                  _full_seed_line=line, _full_seed_response=response)
    value_module = engine.values
    eigen_module = value_module.midpoint.values.eq
    eigen = json.loads((eigen_module.WORK/f'endpoint_{index:03d}'/'record.json').read_bytes())
    value = json.loads((value_module.WORK/f'endpoint_{index:03d}'/'record.json').read_bytes())
    family = validate_segment_family(eigen['report'], value['report'])
    modules = (mixed, mixed.graph, mixed.graph.parent, mixed.graph.parent.original,
               mixed.signed, mixed.mixed_signed, mixed.normalization)
    for module in modules:
        base.bind(source, Path(module.__file__))
    base.bind(source, Path(__file__), THEORY, Path(base.__file__),
              Path(mixed.graph._batch_scalar.__code__.co_filename),
              Path(mixed.enclose_response_rows.__code__.co_filename),
              Path(validate_segment_family.__code__.co_filename))
    seed_record, seed_arrays, seed_files = base.read_pair(args.bootstrap_pair)
    seed_report = seed_record.get('report', {})
    if (seed_record.get('algorithm') != 'UNIFORM_FROZEN_TRIAL_MEAN_VALUE_DERIVATIVE_ARB512_V1'
            or seed_record.get('interval') != args.interval or seed_record.get('side') != args.side
            or seed_record.get('trial_column') != args.column
            or not all(seed_report.get(key) is True for key in ('uniform_derivative_column_enclosed',
                'same_family_segment_smoothness_established', 'all_75_scaled_directions_verified',
                'all_75_point_columns_contained', 'complete_original_seven_solve_graph_used',
                'complete_original_scalar_contractions_used'))):
        raise ValueError('paired complete original trial mean-value seed required')
    for key in ('point_eigenpair_checks','point_derivative_checks'):
        checks=seed_report.get(key,[])
        if len(checks)!=1 or not p.proof_valid(checks[0]):
            raise ValueError('verified bootstrap point anchor required')
    if (seed_arrays['line_candidate'].shape!=(61,1) or seed_arrays['response_candidate'].shape!=(62,1)
            or seed_arrays['weighted_input_axis'].shape!=(99,)
            or not all(a==b for a,b in zip(seed_arrays['weighted_input_axis'],directional['trial'][:,0],strict=True))):
        raise ValueError('bootstrap seeds must cover identical trial direction')
    # Merge verifies every shared physical/source hash; the original direct
    # seed already established matching frozen geometry and primal selection.
    p.geometry.residual.merge(source['binding']['files'],seed_record['binding']['files'])
    for key,value in source['binding'].items():
        if key!='files' and seed_record['binding'].get(key)!=value:
            raise ValueError('bootstrap frozen geometry changed: '+key)
    base.bind(source,*seed_files)
    selected_line=source['_axis_seed_line'].copy()
    selected_response=source['_axis_seed_response'].copy()
    seed_counts=dict(line=base.select_first_variation(selected_line[:61,0],seed_arrays['line_candidate'][:,0]),
        response=base.select_first_variation(selected_response[:,0],seed_arrays['response_candidate'][:,0]))
    source.update(_axis_seed_line=selected_line,_axis_seed_response=selected_response)
    p.verify_sources(source['binding'])
    arrays, report = mixed.evaluate(source, args.column)
    if not all(a == b for a, b in zip(arrays['weighted_input_axis'], directional['trial'][:, 0], strict=True)):
        raise ArithmeticError('mixed and paired direct trial axes differ')
    previous = seed_arrays['uniform_derivative']
    selected = previous.copy()
    changed = base.select_first_variation(selected[:, 0], arrays['derivative_candidate'][:, 0])
    arrays.update(uniform_derivative=selected, previous_mean_value_uniform_derivative=previous)
    report.update(family, paired_mean_value_seed_bootstrap=True, bootstrap_seed_selections=seed_counts, same_family_segment_smoothness_established=True,
        uniform_derivative_column_enclosed=True, exact_baseline_primal_selection=selections,
        all_75_scaled_directions_verified=True, complete_frozen_trial_basis_enclosed=False,
        previous_maximum_radius=float(max(v.rad() for v in previous.flat)),
        selected_maximum_radius=float(max(v.rad() for v in selected.flat)),
        coordinates_tightened=changed, full_path_uniform_contraction=False,
        physical_quotient_identified=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    p.verify_sources(source['binding'])
    return source, arrays, report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', type=int, default=13)
    parser.add_argument('--column', type=int, default=14)
    parser.add_argument('--side', choices=('left', 'right'), default='left')
    parser.add_argument('--primal-pair', type=Path, required=True)
    parser.add_argument('--evidence-root', type=Path, required=True)
    parser.add_argument('--bootstrap-pair', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if not 0 < args.interval < 370 or not 0 <= args.column < 74:
        raise ValueError('interior interval and frozen trial column required')
    args.out, args.primal_pair, args.evidence_root = args.out.resolve(), args.primal_pair.resolve(), args.evidence_root.resolve()
    args.bootstrap_pair=args.bootstrap_pair.resolve()
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
                trial_column=args.column, side=args.side, data_SHA256=p.values.sha(data), report=report,
                FULL_BHSM_COMPLETE=False)
            (args.out/'record.json').write_bytes(p.geometry.encoded(record))
            print(json.dumps({k: v for k, v in report.items() if not isinstance(v, (dict, list))}), flush=True)
        except BaseException as error:
            (args.out/'failure.json').write_bytes(p.geometry.encoded(dict(error=repr(error), FULL_BHSM_COMPLETE=False)))
            raise


if __name__ == '__main__':
    main()
