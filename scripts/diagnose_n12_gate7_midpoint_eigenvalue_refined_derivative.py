"""Measure the paired eigenvalue refinement on midpoint physical input column zero."""
import os
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
import certify_n12_gate7_midpoint_mean_value_eigenvalue as eigenvalue
import diagnose_n12_gate7_component_centered_uniform_derivatives as component


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', type=int, required=True)
    parser.add_argument('--primal-pair', type=Path, required=True)
    parser.add_argument('--eigenvalue-pair', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    ctx.prec = 512
    primal = eigenvalue.primal
    p = primal.engine.p
    r = p.geometry.residual
    targets = [(p.values, 'sha'), (r.center, '_sha'), (r.foundation.coordinate.center, '_sha')]
    with primal.cache.cache_hashes(targets, excluded_roots=[args.out]):
        try:
            source = eigenvalue.load_inputs(args.interval, args.primal_pair)
            first = args.eigenvalue_pair/'first'
            path, data, receipt_path = first/'record.json', first/'column.npz', args.eigenvalue_pair/'reproduction.json'
            record, receipt = json.loads(path.read_bytes()), json.loads(receipt_path.read_bytes())
            report = record.get('report', {})
            if (record.get('binding') != source['binding'] or record.get('interval') != args.interval
                    or report.get('uniform_selected_eigenvalue_enclosed') is not True
                    or report.get('all_249_scaled_directions_verified') is not True
                    or report.get('normalized_symmetric_eigenvalue_derivative_used') is not True
                    or report.get('auxiliary_line_border_used') is not False
                    or report.get('scope') != 'ACTUAL_HS_MIDPOINT_OUTER_DOMAIN'
                    or receipt.get('independent_recomputation') is not True
                    or receipt.get('fresh_process') is not True or receipt.get('byte_identical') is not True
                    or path.read_bytes() != p.geometry.encoded(record)
                    or record.get('data_SHA256') != p.values.sha(data)):
                raise ValueError('paired eigenvalue bound on the identical midpoint domain required')
            for file in (path, data):
                if receipt['files_SHA256'].get(file.name) != p.values.sha(file):
                    raise ValueError('paired eigenvalue evidence changed')
            with np.load(data, allow_pickle=False) as a:
                lam = p.hs.restore_balls(a['eigenvalue_mid_q'], a['eigenvalue_rad_q'])
            primal_data = args.primal_pair/'first/column.npz'
            with np.load(primal_data, allow_pickle=False) as a:
                response = p.hs.restore_balls(a['response_value_mid_q'], a['response_value_rad_q'])
            if lam.shape != (1,) or response.shape != (62, 1):
                raise ValueError('complete scalar eigenvalue and bordered response required')
            selections = dict(
                psi=eigenvalue.select_first_variation(source['paired']['eigenbox'][:61], source['selected_psi']),
                response=eigenvalue.select_first_variation(source['response'], response[:, 0]),
                eigenvalue=eigenvalue.select_first_variation(source['paired']['eigenbox'][-1:], lam))
            old_dir = ROOT/f'artifacts/flagship_integration/.primal_mean_value_component_centered_midpoint_uniform_df_work/interval_{args.interval:03d}'
            old_path, old_data, old_receipt_path = (old_dir/name for name in ('record.json', 'derivative.npz', 'reproduction.json'))
            old_record, old_receipt = json.loads(old_path.read_bytes()), json.loads(old_receipt_path.read_bytes())
            if (old_record.get('interval') != args.interval
                    or old_record.get('algorithm') != 'PRIMAL_MEAN_VALUE_COMPONENT_CENTERED_MIDPOINT_UNIFORM_DF_ARB512_V1'
                    or old_record['report'].get('actual_HS_midpoint_domain_enclosed') is not True
                    or old_record['report'].get('weighted_augmented_basis_columns') != 99
                    or old_record['report'].get('primal_value_record_SHA256') != p.values.sha(args.primal_pair/'first/record.json')
                    or old_record.get('data_SHA256') != p.values.sha(old_data)
                    or old_path.read_bytes() != p.geometry.encoded(old_record)
                    or old_receipt.get('record_SHA256') != p.values.sha(old_path)
                    or old_receipt.get('independent_recomputation') is not True
                    or old_receipt.get('byte_identical') is not True):
                raise ValueError('paired primal-only full derivative comparison required')
            p.verify_sources(old_record['binding'])
            p.geometry.residual.merge(source['binding']['files'], old_record['binding']['files'])
            with np.load(old_data, allow_pickle=False) as a:
                previous = p.hs.restore_balls(a['derivative_mid_q'], a['derivative_rad_q'])[:, :1]
            for file in (path, data, receipt_path, old_path, old_data, old_receipt_path,
                         Path(__file__), Path(eigenvalue.__file__), Path(component.__file__)):
                p.geometry.residual.merge(source['binding']['files'], {p.df.file_key(file): p.values.sha(file)})
            p.verify_sources(source['binding'])
            arrays, proof = component.evaluate(primal.engine, source, 0, 1)
            if arrays['derivative'].shape != (99, 1):
                raise ArithmeticError('complete single physical derivative column required')
            if not all(a.overlaps(b) for a, b in zip(arrays['derivative'].flat, previous.flat, strict=True)):
                raise ArithmeticError('same-family derivative enclosures disagree')
            arrays['primal_only_derivative'] = previous
            report = dict(interval=args.interval, start=0, stop=1, scope='ACTUAL_HS_MIDPOINT_OUTER_DOMAIN',
                complete_physical_column_enclosed=True, selection_counts=selections, variation_proof=proof,
                previous_maximum_radius_approx=float(max(v.rad() for v in previous.flat)),
                maximum_radius_approx=float(max(v.rad() for v in arrays['derivative'].flat)),
                all_99_columns_enclosed=False, full_path_uniform_contraction=False,
                Gate7_closed=False, FULL_BHSM_COMPLETE=False)
            p.verify_sources(source['binding'])
            encoded = {}
            for name, a in arrays.items():
                encoded[name+'_mid_q'], encoded[name+'_rad_q'] = p.hs.rational_balls(a)
            output = args.out/'column.npz'
            np.savez_compressed(output, **encoded)
            record = dict(binding=source['binding'], interval=args.interval, report=report,
                          data_SHA256=p.values.sha(output), FULL_BHSM_COMPLETE=False)
            (args.out/'record.json').write_bytes(p.geometry.encoded(record))
            print(json.dumps({k:v for k,v in report.items() if not isinstance(v, dict)}), flush=True)
        except BaseException as error:
            (args.out/'failure.json').write_bytes(p.geometry.encoded(dict(error=repr(error), FULL_BHSM_COMPLETE=False)))
            raise


if __name__ == '__main__':
    main()
