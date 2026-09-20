"""Replay final norm aggregation from the retained common constant matrices.

This verifies the last norm/majorant step, not the action derivatives or the
state-affine coefficient construction. Those require the separately recorded
numerator verification and repeated transport arithmetic.
"""
import argparse
import gzip
import json
from pathlib import Path
import sys
from flint import arb, arb_mat, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'scripts')]
from bhsm.interface.input_linear_taylor import vector_norm
from bhsm.interface.shared_parameter_residual import linear_support
from bhsm.interface.joint_output_support import joint_constant_support
from certify_n12_gate7_endpoint_vector_transport import restore
import evaluate_n12_gate7_coupled_residual_saved as saved


def number(item):
    value = arb(item['exact'])
    if not value.is_exact() or not value.is_finite() or not value >= 0:
        raise ValueError('finite nonnegative exact saved upper bound required')
    if float(value) != item['approximate']:
        raise ValueError('display value differs from exact upper bound')
    return value


def same(actual, item, label):
    if str(actual.upper().fmpq()) != str(number(item).fmpq()):
        raise ArithmeticError(f'{label} failed exact outward replay')


def verify(record, payload):
    if (record['algorithm'] != 'FULL_INPUT_COUPLED_NUMERATOR_HS_TRANSPORT_V1'
            or record['physical_input_columns'] != 74
            or record['projected_output_rows'] != 74
            or record['input_groups'] != [[0, 74, 'euclidean'], [74, 322, 'box']]
            or len(record['rows']) != 74
            or any(record[k] is not False for k in
                   ('full_history_certified', 'Gate7_closed', 'FULL_BHSM_COMPLETE',
                    'two_radius_global_contraction_inferred'))):
        raise ValueError('complete local transport with unchanged claim scope required')
    matrices = {}
    for name, rows in [('original', 74), ('pulled', 74),
                       ('longitudinal_original', 1), ('longitudinal_pulled', 1)]:
        values = payload[name]
        if len(values) != rows * 322:
            raise ValueError('complete common constant matrix required')
        matrices[name] = arb_mat(rows, 322, [restore(pair) for pair in values])
    groups = record['input_groups']
    row_bounds, linear, remainder, axis = [], [], [], []
    for i, row in enumerate(record['rows']):
        if row['component'] != i:
            raise ValueError('ordered complete output rows required')
        c = linear_support([matrices['pulled'][i, j] for j in range(322)], groups)
        a, r = number(row['linear']), number(row['nonlinear'])
        same(c + a + r, row['support'], f'row {i} support')
        row_bounds.append(number(row['support']))
        linear.append(a)
        remainder.append(r)
        axis.append(number(row['longitudinal_input_support']))
    old = joint_constant_support(matrices['original'], groups)
    pulled = joint_constant_support(matrices['pulled'], groups)
    same(old, record['joint_original_constant_support'], 'original joint constants')
    same(pulled, record['joint_pulled_constant_support'], 'pulled joint constants')
    ln, rn = vector_norm(linear), vector_norm(remainder)
    same(ln, record['linear_vector_bound'], 'state-linear vector')
    same(rn, record['nonlinear_vector_bound'], 'nonlinear vector')
    total = min(vector_norm(row_bounds), (min(old, pulled) + ln + rn).upper())
    same(total, record['complete_local_right_block_norm_upper'], 'complete local norm')
    if record['strict_local_gain_below_one'] is not bool(total < 1):
        raise ArithmeticError('local strictness flag differs from exact bound')
    longitudinal = record['longitudinal_output']
    c = linear_support(matrices['longitudinal_pulled'].entries(), groups)
    same(c + number(longitudinal['linear']) + number(longitudinal['nonlinear']),
         longitudinal['support'], 'longitudinal output support')
    on_axis = vector_norm(axis)
    same(on_axis, record['longitudinal_input_transverse_output_norm_upper'],
         'longitudinal input transverse output')
    expected = [[number(longitudinal['longitudinal_input_support']),
                 number(longitudinal['support'])], [on_axis, total]]
    majorant = record['local_fixed_axis_two_radius_majorant']
    if (majorant['row_order'] != ['longitudinal_output', 'transverse_output']
            or majorant['column_order'] !=
            ['longitudinal_input', 'Euclidean_superset_of_transverse_input']
            or majorant['all_history_intervals_covered'] is not False
            or majorant['physical_quotient_identification_inferred'] is not False):
        raise ValueError('unchanged fixed-axis local two-radius scope required')
    radii = [arb(v) for v in majorant['original_trial_radii_exact']]
    if len(radii) != 2 or any(not v.is_exact() or not v > 0 for v in radii):
        raise ValueError('two exact positive original radii required')
    weighted = []
    for i in range(2):
        for j in range(2):
            same(expected[i][j], majorant['bounds'][i][j], f'majorant {i},{j}')
        value = (sum((expected[i][j] * radii[j] for j in range(2)), arb(0)) / radii[i]).upper()
        same(value, majorant['weighted_row_bounds'][i], f'weighted row {i}')
        weighted.append(value)
    if majorant['strict_local_weighted_gain_below_one'] is not bool(max(weighted) < 1):
        raise ArithmeticError('two-radius strictness flag differs from exact bound')
    return dict(all_74_output_supports_replayed=True,
                joint_constant_norms_replayed=True,
                fixed_axis_two_radius_majorant_replayed=True,
                local_norm_upper=float(total),
                local_weighted_rows_upper=[float(v) for v in weighted],
                state_affine_coefficients_recomputed=False,
                action_derivatives_recomputed=False,
                full_history_certified=False, Gate7_closed=False,
                FULL_BHSM_COMPLETE=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--transport', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError('fresh verification receipt required')
    ctx.prec = 512
    record_path = args.transport / 'record.json'
    constants_path = args.transport / 'constants.json.gz'
    record = json.loads(record_path.read_bytes())
    if saved.sha(constants_path) != record['constant_models_SHA256']:
        raise ValueError('exact common constant archive fingerprint required')
    result = verify(record, json.loads(gzip.decompress(constants_path.read_bytes())))
    result.update(record_SHA256=saved.sha(record_path),
                  constants_SHA256=saved.sha(constants_path),
                  verifier_SHA256=saved.sha(Path(__file__)))
    args.out.write_bytes(saved.encoded(result))
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
