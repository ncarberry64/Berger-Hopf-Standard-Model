"""Apply paired primal value bounds to all 99 midpoint derivative columns."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
from n12_gate7_component_centered_uniform_derivative_adapter import make_engine
import certify_n12_gate7_coupled_midpoint_uniform_derivatives as baseline
from diagnose_n12_gate7_mean_value_bootstrap_hessian import select_first_variation


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--mean-value-pair', type=Path, required=True)
    args, remaining = parser.parse_known_args()
    engine = make_engine(ROOT, 'midpoint', Path(__file__))
    engine.WORK = ROOT/'artifacts/flagship_integration/.primal_mean_value_component_centered_midpoint_uniform_df_work'
    engine.ALGORITHM = 'PRIMAL_MEAN_VALUE_COMPONENT_CENTERED_MIDPOINT_UNIFORM_DF_ARB512_V1'
    p = engine.p
    baseline.ctx.prec = 512
    first = args.mean_value_pair/'first'
    record_path, data_path = first/'record.json', first/'column.npz'
    receipt_path = args.mean_value_pair/'reproduction.json'
    record = json.loads(record_path.read_bytes())
    receipt = json.loads(receipt_path.read_bytes())
    if (receipt.get('independent_recomputation') is not True or receipt.get('byte_identical') is not True
            or receipt.get('fresh_process') is not True
            or record['report'].get('uniform_primal_psi_and_response_enclosed') is not True
            or record['report'].get('same_family_segment_smoothness_established') is not True):
        raise ValueError('independently paired uniform primal value enclosures required')
    for file in (record_path, data_path):
        if receipt['files_SHA256'].get(file.name) != p.values.sha(file):
            raise ValueError('paired primal input changed')
    if record['data_SHA256'] != p.values.sha(data_path):
        raise ValueError('primal value data changed')
    p.verify_sources(record['binding'])
    with baseline.np.load(data_path, allow_pickle=False) as a:
        psi = p.hs.restore_balls(a['psi_value_mid_q'], a['psi_value_rad_q'])
        response = p.hs.restore_balls(a['response_value_mid_q'], a['response_value_rad_q'])
    if psi.shape != (61, 1) or response.shape != (62, 1):
        raise ValueError('complete primal value columns required')
    original_load, original_evaluate = engine.load_inputs, engine.evaluate
    selections = []

    def load(index):
        reference = baseline.load_inputs(index)
        for key, value in reference['binding'].items():
            if key == 'files':
                if any(record['binding']['files'].get(name) != digest for name, digest in value.items()):
                    raise ValueError('primal and derivative midpoint families differ')
            elif record['binding'].get(key) != value:
                raise ValueError('primal and derivative geometry differs: ' + key)
        source = original_load(index)
        source['paired'] = dict(source['paired'])
        source['paired']['eigenbox'] = source['paired']['eigenbox'].copy()
        source['response'] = source['response'].copy()
        # Both value enclosures use physical K coordinates. Retain lambda.
        count_psi = select_first_variation(source['paired']['eigenbox'][:61], psi[:, 0])
        count_response = select_first_variation(source['response'], response[:, 0])
        selections.append(dict(psi_coordinates_tightened=count_psi,
                               response_coordinates_tightened=count_response, eigenvalue_refined=False))
        p.geometry.residual.merge(source['binding']['files'], record['binding']['files'])
        for file in (record_path, data_path, receipt_path, Path(__file__),
                     Path(sys.modules[select_first_variation.__module__].__file__)):
            p.geometry.residual.merge(source['binding']['files'], {p.df.file_key(file): p.values.sha(file)})
        p.verify_sources(source['binding'])
        return source

    def evaluate(source):
        arrays, report = original_evaluate(source)
        if len(selections) != 1:
            raise ArithmeticError('one same-family primal value source required')
        report.update(paired_uniform_primal_values_used=True, primal_value_selection=selections,
                      primal_value_record_SHA256=p.values.sha(record_path))
        return arrays, report

    engine.load_inputs, engine.evaluate = load, evaluate
    sys.argv = [sys.argv[0]]+remaining
    engine.main()


if __name__ == '__main__':
    main()
