"""Refine the same 75-direction Hessian using a paired mean-value column.

Both competing boxes enclose the same first variation. Select the smaller
box coordinate by coordinate; preserve every mixed equation and scalar term.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
import diagnose_n12_gate7_affine_basis_uniform_hessian as parent


def select_first_variation(result, candidate, *, response=False):
    """Candidate is in physical K coordinates; result is in J coordinates."""
    candidate = candidate.copy()
    if response:
        candidate[-1] = -candidate[-1]
    changed = 0
    for i, value in enumerate(candidate):
        if not value.is_finite() or not value.overlaps(result[i]):
            raise ArithmeticError('same-family first-variation enclosures disagree')
        if value.rad() < result[i].rad():
            result[i] = value
            changed += 1
    return changed


def main():
    parent.ctx.prec = 512
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--mean-value-pair', type=Path, required=True)
    args, remaining = parser.parse_known_args()
    pair = args.mean_value_pair
    first = pair/'first'
    record_path, data_path = first/'record.json', first/'column.npz'
    receipt_path = pair/'reproduction.json'
    p = parent.engine.p
    record = json.loads(record_path.read_bytes())
    receipt = json.loads(receipt_path.read_bytes())
    if (receipt.get('independent_recomputation') is not True or receipt.get('byte_identical') is not True
            or receipt.get('fresh_process') is not True):
        raise ValueError('independently paired mean-value column required')
    for file in (record_path, data_path):
        if receipt['files_SHA256'].get(file.name) != p.values.sha(file):
            raise ValueError('paired mean-value input changed')
    if record['data_SHA256'] != p.values.sha(data_path):
        raise ValueError('mean-value data hash changed')
    report = record['report']
    if (report.get('uniform_derivative_column_enclosed') is not True
            or report.get('same_family_segment_smoothness_established') is not True
            or report.get('all_75_scaled_directions_verified') is not True):
        raise ValueError('proved same-family uniform mean-value column required')
    p.verify_sources(record['binding'])
    with parent.np.load(data_path, allow_pickle=False) as a:
        line = p.hs.restore_balls(a['line_mid_q'], a['line_rad_q'])
        response = p.hs.restore_balls(a['response_mid_q'], a['response_rad_q'])
    if line.shape != (61, 1) or response.shape != (62, 1):
        raise ValueError('complete paired first-variation columns required')
    original_load, original_evaluate = parent.engine.load_inputs, parent.evaluate
    original_enclose = parent.enclose_response_rows

    def load(index):
        source = original_load(index)
        for key, value in source['binding'].items():
            if key == 'files':
                if any(record['binding']['files'].get(name) != digest for name, digest in value.items()):
                    raise ValueError('bootstrap source and certified family differ')
            elif record['binding'].get(key) != value:
                raise ValueError('bootstrap tube binding differs: ' + key)
        p.geometry.residual.merge(source['binding']['files'], record['binding']['files'])
        for file in (record_path, data_path, receipt_path, Path(__file__)):
            p.geometry.residual.merge(source['binding']['files'], {p.df.file_key(file): p.values.sha(file)})
        p.verify_sources(source['binding'])
        return source

    def evaluate(source, column):
        if report['physical_input_columns'] != [column]:
            raise ValueError('certified first variation must match the fixed input column')
        count = 0
        selected = []

        def enclose(*inputs):
            nonlocal count
            result, proof = original_enclose(*inputs)
            count += 1
            if count in (1, 2):
                candidate = (line if count == 1 else response)[:, 0]
                # The parent converts K to J coordinates before this call and
                # flips the last coordinate back afterwards. Line omits lambda.
                changed = select_first_variation(result, candidate, response=count == 2)
                selected.append(dict(solve=count, coordinates_tightened=changed,
                                     maximum_radius=float(max(v.rad() for v in result[:len(candidate)]))))
            return result, proof

        try:
            parent.enclose_response_rows = enclose
            arrays, result = original_evaluate(source, column)
        finally:
            parent.enclose_response_rows = original_enclose
        if count != 302 or len(selected) != 2:
            raise ArithmeticError('complete 1+1+75+75+75+75 variation solve graph required')
        result.update(paired_mean_value_first_variations_used=True,
                      first_variation_selection=selected,
                      mean_value_record_SHA256=p.values.sha(record_path),
                      no_uncertainty_discarded=True)
        return arrays, result

    try:
        parent.engine.load_inputs = load
        parent.evaluate = evaluate
        sys.argv = [sys.argv[0]]+remaining
        parent.main()
    finally:
        parent.engine.load_inputs = original_load
        parent.evaluate = original_evaluate
        parent.enclose_response_rows = original_enclose


if __name__ == '__main__':
    main()
