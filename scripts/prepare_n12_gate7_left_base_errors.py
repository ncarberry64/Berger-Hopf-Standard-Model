"""Retain the original left implicit inclusion without a preliminary scalar run.

The response radius intersects the original inclusion with the saved
same-family mean-value bound. Physical state radii and parameters stay fixed.
"""
import argparse
import os
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
from pathlib import Path
import json
import sys
import numpy as np
from flint import arb, ctx
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src')]
from bhsm.interface.shared_parameter_residual import linear_support
import n12_gate7_left_saved_family as saved


def evaluate(root, family):
    import bhsm.interface
    bhsm.interface.__path__.insert(0, str(root/'src/bhsm/interface'))
    verified = saved.evaluate(root)
    pair, eigenname, _, _ = saved.PAIRS[family]
    groups = verified['families'][family]['groups']
    with np.load(root/'tmp'/pair/'value/first/column.npz', allow_pickle=False) as z, \
         np.load(root/'artifacts/flagship_integration'/eigenname/'eigenpair.npz', allow_pickle=False) as e:
        ep = saved.read_matrix(e, 'eigenpair_center', center=True)
        box = saved.read_matrix(e, 'eigenpair_box')
        line = saved.read_matrix(z, 'point_center_3', center=True)
        response = saved.read_matrix(z, 'point_center_0', center=True)
        response_box = saved.read_matrix(z, 'uniform_solve_0')
        response_derivative = saved.read_matrix(z, 'point_center_4', center=True)
        point_response = saved.read_matrix(z, 'point_solve_0')
        uniform_response_derivative = saved.read_matrix(z, 'uniform_solve_4')
    radius = [(abs(box[i, 0]-ep[i, 0]).upper()+linear_support(
        [line[i, j] for j in range(line.ncols())], groups)).upper() for i in range(61)]
    # A constant eigenvalue predictor is sufficient for this preparatory
    # inclusion. The action producer constructs its Rayleigh predictor and
    # recomputes this radius against the same original eigenvalue box.
    radius.append(abs(box[61, 0]-ep[61, 0]).upper())
    original = list(radius)
    for i in range(62):
        initial = (abs(response_box[i, 0]-response[i, 0]).upper()+linear_support(
            [response_derivative[i, j] for j in range(response_derivative.ncols())], groups)).upper()
        integrated = (abs(point_response[i, 0]-response[i, 0]).upper()+linear_support(
            [uniform_response_derivative[i, j]-response_derivative[i, j]
             for j in range(response_derivative.ncols())], groups)).upper()
        original.append(initial)
        radius.append(min(initial, integrated))
    if any(not r >= 0 or not r.is_finite() or not r.rad().is_zero() for r in radius):
        raise ArithmeticError('finite exact nonnegative correction radii required')
    return dict(algorithm='ORIGINAL_LEFT_BASE_INCLUSION_WITH_RESPONSE_MEAN_VALUE_V1',
        family=family, side='left', interval=13,
        correction_radii_exact=[str(v.fmpq()) for v in radius],
        original_correction_radii_exact=[str(v.fmpq()) for v in original],
        original_state_groups=groups, physical_domain_shrunk=False,
        eigenvalue_predictor='constant; downstream action producer must re-enclose its own predictor',
        response_coordinates_improved=sum(a < b for a, b in zip(radius, original)),
        source_hashes={**verified['paired_source_hashes'],
            'left_source_verifier':saved.sha(Path(saved.__file__)),
            'evaluator':saved.sha(Path(__file__))},
        full_input_bound_certified=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence-root', type=Path, required=True)
    parser.add_argument('--family', choices=('midpoint', 'endpoint'), required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    ctx.prec = 512
    result = evaluate(args.evidence_root.resolve(), args.family)
    with args.out.open('xb') as f:
        f.write(saved.encoded(result))
    print(json.dumps(dict(family=args.family,
        response_coordinates_improved=result['response_coordinates_improved'])), flush=True)


if __name__ == '__main__':
    main()
