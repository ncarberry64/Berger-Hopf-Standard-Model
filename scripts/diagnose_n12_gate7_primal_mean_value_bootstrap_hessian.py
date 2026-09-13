"""Use paired mean-value enclosures for primal values and first variations."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
import diagnose_n12_gate7_mean_value_bootstrap_hessian as bootstrap


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--mean-value-pair', type=Path, required=True)
    args, _ = parser.parse_known_args()
    parent = bootstrap.parent
    parent.ctx.prec = 512
    p = parent.engine.p
    first = args.mean_value_pair/'first'
    record_path, data_path = first/'record.json', first/'column.npz'
    hashes = {file: p.values.sha(file) for file in (record_path, data_path)}
    record = json.loads(record_path.read_bytes())
    if (record['report'].get('uniform_primal_psi_and_response_enclosed') is not True
            or record['report'].get('auxiliary_line_border_used_as_eigenvalue_derivative') is not False
            or record['report'].get('eigenvalue_refined') is not False):
        raise ValueError('certified primal values with original eigenvalue enclosure required')
    with parent.np.load(data_path, allow_pickle=False) as a:
        psi = p.hs.restore_balls(a['psi_value_mid_q'], a['psi_value_rad_q'])
        response = p.hs.restore_balls(a['response_value_mid_q'], a['response_value_rad_q'])
    if psi.shape != (61, 1) or response.shape != (62, 1):
        raise ValueError('complete primal psi and physical response required')
    original_load, original_evaluate = parent.engine.load_inputs, parent.evaluate
    selected = []

    def load(index):
        # The outer bootstrap validates the paired receipt and complete source
        # identity before any physical evaluation consumes these narrower boxes.
        source = original_load(index)
        if any(p.values.sha(file) != digest for file, digest in hashes.items()):
            raise ValueError('primal inputs changed during loading')
        source['paired'] = dict(source['paired'])
        source['paired']['eigenbox'] = source['paired']['eigenbox'].copy()
        source['response'] = source['response'].copy()
        count_psi = bootstrap.select_first_variation(source['paired']['eigenbox'][:61], psi[:, 0])
        # Both primal response boxes are in physical K coordinates; no border
        # conversion is needed here. The base first-variation wrapper handles
        # its own separate J-coordinate conversion.
        count_response = bootstrap.select_first_variation(source['response'], response[:, 0])
        selected.append(dict(psi_coordinates_tightened=count_psi,
                             response_coordinates_tightened=count_response,
                             eigenvalue_refined=False,
                             maximum_psi_radius=float(max(v.rad() for v in source['paired']['eigenbox'][:61])),
                             maximum_response_radius=float(max(v.rad() for v in source['response']))))
        return source

    def evaluate(source, column):
        if len(selected) != 1:
            raise ArithmeticError('one bound paired primal family required')
        p.geometry.residual.merge(source['binding']['files'], {p.df.file_key(Path(__file__)): p.values.sha(Path(__file__))})
        p.verify_sources(source['binding'])
        arrays, report = original_evaluate(source, column)
        report.update(paired_mean_value_primal_values_used=True, primal_value_selection=selected)
        return arrays, report

    try:
        parent.engine.load_inputs = load
        parent.evaluate = evaluate
        bootstrap.main()
    finally:
        parent.engine.load_inputs = original_load
        parent.evaluate = original_evaluate


if __name__ == '__main__':
    main()
