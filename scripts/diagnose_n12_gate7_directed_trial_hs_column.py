"""Paired pilot of a frozen trial direction inside the complete physical graph."""
import os
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb, arb_mat, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
import certify_n12_gate7_primal_uniform_physical_local_defects as reader
import n12_gate7_directed_physical_variation as directed
import bhsm_immutable_input_hash_cache as cache
from diagnose_n12_gate7_mean_value_bootstrap_hessian import select_first_variation
from bhsm.interface import directed_physical_hs_column as chain

p = reader.p
THEORY = ROOT/'theory/n12_gate7_directed_trial_hs_column.md'
ALGORITHM = 'DIRECTED_FROZEN_TRIAL_HS_COLUMN_ARB512_V1'


def bind(source, *files):
    for file in files:
        p.geometry.residual.merge(source['binding']['files'], {p.df.file_key(file): p.values.sha(file)})


def array(matrix):
    return np.array(matrix.entries(), dtype=object).reshape(matrix.nrows(), matrix.ncols())


def matrix(values):
    return arb_mat(*values.shape, list(values.flat))


def read_pair(pair):
    path, data, receipt_path = pair/'first/record.json', pair/'first/column.npz', pair/'reproduction.json'
    record, receipt = json.loads(path.read_bytes()), json.loads(receipt_path.read_bytes())
    if (receipt.get('independent_recomputation') is not True or receipt.get('fresh_process') is not True
            or receipt.get('byte_identical') is not True or path.read_bytes() != p.geometry.encoded(record)
            or record.get('data_SHA256') != p.values.sha(data)):
        raise ValueError('independently paired canonical columns required')
    for file in (path, data):
        if receipt.get('files_SHA256', {}).get(file.name) != p.values.sha(file):
            raise ValueError('paired column bytes changed')
    p.verify_sources(record['binding'])
    with np.load(data, allow_pickle=False) as a:
        arrays = {name[:-6]: p.hs.restore_balls(a[name], a[name[:-6]+'_rad_q'])
                  for name in a.files if name.endswith('_mid_q')}
    return record, arrays, (path, data, receipt_path)


def load_stage(index, stage, pair):
    producer = reader.endpoint if stage == 'endpoint' else reader.midpoint
    baseline = producer.load_inputs(index)
    source, old_df = reader.read_derivative(None, index, stage)
    record, arrays, files = read_pair(pair)
    report = record.get('report', {})
    if (report.get('uniform_primal_psi_and_response_enclosed') is not True
            or report.get('same_family_segment_smoothness_established') is not True):
        raise ValueError('same-family uniform primal proof required')
    for key, value in baseline['binding'].items():
        if key == 'files':
            if any(record['binding']['files'].get(name) != digest for name, digest in value.items()):
                raise ValueError('primal physical-domain source mismatch')
        elif record['binding'].get(key) != value:
            raise ValueError('primal geometry mismatch: '+key)
    kind = 'endpoint' if stage == 'endpoint' else 'interval'
    full_path = ROOT/f'artifacts/flagship_integration/.primal_mean_value_component_centered_{stage}_uniform_df_work/{kind}_{index:03d}/record.json'
    full_record = json.loads(full_path.read_bytes())
    if full_record['report'].get('primal_value_record_SHA256') != p.values.sha(files[0]):
        raise ValueError('pilot must use the exact primal pair used by the paired full derivative')
    psi, response = arrays['psi_value'], arrays['response_value']
    if psi.shape != (61, 1) or response.shape != (62, 1):
        raise ValueError('complete primal columns required')
    source['paired'] = dict(source['paired'])
    source['paired']['eigenbox'] = source['paired']['eigenbox'].copy()
    source['response'] = source['response'].copy()
    selections = dict(psi=select_first_variation(source['paired']['eigenbox'][:61], psi[:, 0]),
                      response=select_first_variation(source['response'], response[:, 0]),
                      eigenvalue_refined=False)
    bind(source, *files)
    return producer, source, old_df, selections


def validate_directed(record, stage, side, args):
    report = record.get('report', {})
    if (record.get('algorithm') != ALGORITHM or record.get('stage') != stage
            or record.get('side') != side or record.get('interval') != args.interval
            or record.get('trial_column') != args.column
            or report.get('complete_original_directional_variation') is not True
            or report.get('verified_point_derivative_contained') is not True):
        raise ValueError('matching paired directed physical evidence required')


def evaluate(args, local):
    index = args.interval + (args.side == 'right' and args.stage == 'endpoint')
    engine, source, old_df, selections = load_stage(index, args.stage, args.primal_pair)
    p.geometry.residual.merge(source['binding']['files'], local['binding']['files'])
    trial = np.array([[arb(float(v))] for v in local['trial_'+args.side][:, args.column]], dtype=object)
    if args.stage == 'endpoint':
        directions = trial
    else:
        record, endpoint_arrays, files = read_pair(args.evidence_root/('endpoint_'+args.side))
        validate_directed(record, 'endpoint', args.side, args)
        p.geometry.residual.merge(source['binding']['files'], record['binding']['files'])
        bind(source, *files)
        directions = array(chain.chain_direction(trial, endpoint_arrays['selected'], local['step'], args.side))
    bind(source, Path(__file__), Path(directed.__file__), Path(chain.__file__), THEORY,
         Path(directed.signed.__file__), Path(directed.normalization.__file__),
         Path(sys.modules[directed.enclose_response.__module__].__file__),
         Path(sys.modules[select_first_variation.__module__].__file__), Path(cache.__file__))
    p.verify_sources(source['binding'])
    if args.preflight:
        return source, {}, dict(inputs_verified=True, numerical_evaluation=False)
    arrays, proof = directed.evaluate(engine, source, directions)
    old_action = array(matrix(old_df)*matrix(directions))
    selected = old_action.copy()
    tightened = select_first_variation(selected[:, 0], arrays['derivative'][:, 0])
    arrays.update(selected=selected, ambient_product=old_action, trial=trial)
    report = dict(complete_original_directional_variation=True, verified_point_derivative_contained=True,
                  same_original_physical_domain=True, exact_baseline_primal_pair_used=True,
                  primal_selection=selections, proof=proof, coordinates_tightened=tightened,
                  old_maximum_radius=float(max(v.rad() for v in old_action.flat)),
                  directed_maximum_radius=float(max(v.rad() for v in arrays['derivative'].flat)),
                  selected_maximum_radius=float(max(v.rad() for v in selected.flat)),
                  interval_input_correlation_relaxed=args.stage == 'midpoint',
                  full_trial_basis_enclosed=False, physical_quotient_identified=False,
                  complete_causal_Z1_enclosed=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    return source, arrays, report


def assemble(args, source):
    arrays, reports = {}, {}
    old_dir = reader.WORK/f'interval_{args.interval:03d}'
    old_path, old_data, old_receipt_path = (old_dir/name for name in ('record.json', 'blocks.npz', 'reproduction.json'))
    old_record, receipt = json.loads(old_path.read_bytes()), json.loads(old_receipt_path.read_bytes())
    if (old_record.get('binding') != source['binding'] or old_record.get('data_SHA256') != p.values.sha(old_data)
            or old_path.read_bytes() != p.geometry.encoded(old_record)
            or receipt.get('record_SHA256') != p.values.sha(old_path)
            or receipt.get('byte_identical') is not True or receipt.get('independent_recomputation') is not True):
        raise ValueError('paired identical fixed-frame baseline required')
    with np.load(old_data, allow_pickle=False) as a:
        previous = {name: p.hs.restore_balls(a[name+'_mid_q'], a[name+'_rad_q'])[:, args.column:args.column+1]
                    for name in ('DL', 'DR')}
    bind(source, old_path, old_data, old_receipt_path)
    for side, name in (('left', 'DL'), ('right', 'DR')):
        evidence = {}
        for stage in ('endpoint', 'midpoint'):
            record, values, files = read_pair(args.evidence_root/(stage+'_'+side))
            validate_directed(record, stage, side, args)
            p.geometry.residual.merge(source['binding']['files'], record['binding']['files'])
            bind(source, *files)
            evidence[stage] = values
        trial = np.array([[arb(float(v))] for v in source['trial_'+side][:, args.column]], dtype=object)
        candidates = chain.local_column(trial, evidence['endpoint']['selected'], evidence['midpoint']['selected'],
            source['step'], source['test'], source['frozen_left'], source['frozen_right'], args.column, side)
        selected = previous[name].copy()
        for key, value in candidates.items():
            candidate = array(value)
            select_first_variation(selected[:, 0], candidate[:, 0])
            arrays[name+'_'+key] = candidate
        arrays[name] = selected
        arrays[name+'_previous'] = previous[name]
        reports[name] = dict(previous_maximum_radius=float(max(v.rad() for v in previous[name].flat)),
                             selected_maximum_radius=float(max(v.rad() for v in selected.flat)),
                             coordinates_tightened=sum(a.rad() < b.rad() for a, b in zip(selected.flat, previous[name].flat)))
    bind(source, Path(__file__), Path(chain.__file__), THEORY)
    return source, arrays, dict(columns=reports, paired_directional_inputs=True,
        full_trial_basis_enclosed=False, state_dependent_frame_derivatives_enclosed=False,
        physical_quotient_identified=False, complete_causal_Z1_enclosed=False,
        Gate7_closed=False, FULL_BHSM_COMPLETE=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', type=int, default=13)
    parser.add_argument('--column', type=int, default=14)
    parser.add_argument('--stage', choices=('endpoint', 'midpoint', 'assemble'), required=True)
    parser.add_argument('--side', choices=('left', 'right'))
    parser.add_argument('--primal-pair', type=Path)
    parser.add_argument('--evidence-root', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--preflight', action='store_true')
    args = parser.parse_args()
    args.out = args.out.resolve()
    args.evidence_root = args.evidence_root.resolve()
    if args.primal_pair is not None:
        args.primal_pair = args.primal_pair.resolve()
    if not 0 < args.interval < 370 or not 0 <= args.column < 74:
        raise ValueError('interior HS interval and frozen trial column required')
    if args.stage != 'assemble' and (args.side is None or args.primal_pair is None):
        raise ValueError('directional stage requires side and primal pair')
    args.out.mkdir(exist_ok=False, parents=True)
    ctx.prec = 512
    residual = p.geometry.residual
    targets = [(p.values, 'sha'), (residual.center, '_sha'), (residual.foundation.coordinate.center, '_sha')]
    with cache.cache_hashes(targets, excluded_roots=[args.out]):
        try:
            local = reader.load_inputs(args.interval)
            source, arrays, report = assemble(args, local) if args.stage == 'assemble' else evaluate(args, local)
            p.verify_sources(source['binding'])
            if args.preflight:
                print(json.dumps(report), flush=True)
                return
            encoded = {}
            for name, values in arrays.items():
                encoded[name+'_mid_q'], encoded[name+'_rad_q'] = p.hs.rational_balls(values)
            data = args.out/'column.npz'
            np.savez_compressed(data, **encoded)
            record = dict(algorithm=ALGORITHM, binding=source['binding'], interval=args.interval,
                trial_column=args.column, stage=args.stage, side=args.side,
                data_SHA256=p.values.sha(data), report=report, FULL_BHSM_COMPLETE=False)
            (args.out/'record.json').write_bytes(p.geometry.encoded(record))
            print(json.dumps({k: v for k, v in report.items() if k != 'proof'}), flush=True)
        except BaseException as error:
            (args.out/'failure.json').write_bytes(p.geometry.encoded(dict(error=repr(error), FULL_BHSM_COMPLETE=False)))
            raise


if __name__ == '__main__':
    main()
