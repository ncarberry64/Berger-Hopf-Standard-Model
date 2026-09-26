"""Extract an existing center block; never evaluate actions or nonlinear jets."""
import argparse
import io
from pathlib import Path

import numpy as np
from flint import arb_mat, ctx

from checkpoint_n12_gate7_66d_tangent_binding import (
    ROOT, BASE, PHYSICAL, SCALE, TEST_SCALE, amat, bound, digest, encoded, frame,
)


def extract():
    """Replay only the frozen 74D center matrix, with stored-double authority."""
    ctx.prec = 512
    source = ROOT / BASE / 'BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_BLOCK_NEWTON_PREDICTOR.npz'
    producer = ROOT / 'scripts/materialize_n12_gate7_augmented_fixed_descriptor_block_newton_predictor.py'
    with np.load(source) as z, np.load(ROOT / PHYSICAL) as j:
        matrix = z['reduced_right_Newton_blocks'][13]
        right = z['right_Newton_blocks'][13]
        times = z['action_times']
        tangent = j['endpoint_physical_tangent_action'][14]
        endpoint = j['endpoint_augmented_Jacobian_action'][14]
        midpoint = j['midpoint_augmented_Jacobian_action'][13]
        stored_condition = float(z['reduced_right_block_condition_2'][13])
    if matrix.shape != (74, 74):
        raise ValueError('unexpected center shape')
    trial, test = frame(tangent, SCALE), frame(tangent, TEST_SCALE)
    h = float(times[14] - times[13])
    replay_right = np.eye(99) - h * (4 * midpoint @ (np.eye(99)/2 - h*endpoint/8) + endpoint)/6
    inverse = np.linalg.solve(matrix, np.eye(74))
    eye = arb_mat(np.eye(74, dtype=int).tolist())
    # These certify residual bounds for the exact stored binary64 matrix only.
    left = bound(eye - amat(inverse)*amat(matrix))
    right_residual = bound(eye - amat(matrix)*amat(inverse))
    from flint import arb
    invertible = bool(arb(left['exact_upper']) < 1)
    report = dict(
        authority='STORED_CENTER_MATRIX_ONLY_NOT_UNIFORM_NONLINEAR_AUTHORITY',
        source_SHA256={str(p.relative_to(ROOT)): digest(p) for p in (source, ROOT/PHYSICAL, producer, Path(__file__).resolve())},
        source_key='reduced_right_Newton_blocks[13]', shape=list(matrix.shape), interval=13,
        right_endpoint=14, h=h, condition_2=float(np.linalg.cond(matrix)),
        stored_condition_2=stored_condition,
        floating_HS_right_replay_max_abs=float(np.max(np.abs(right-replay_right))),
        floating_frame_replay_max_abs=float(np.max(np.abs(matrix-test.T@right@trial))),
        exact_stored_frame_replay_error=bound(amat(matrix)-amat(test).transpose()*amat(right)*amat(trial)),
        inverse_left_residual=left, inverse_right_residual=right_residual,
        stored_center_invertible_by_residual=invertible,
        trial_descriptor_scale=SCALE, test_descriptor_scale=TEST_SCALE,
        coordinate_convention='99D action coordinates: first 98 weighted state coordinates, last physical descriptor; columns 0:73 are endpoint-14 physical tangent coefficients; column 73 has physical descriptor = 1e-7 times coefficient. Test frame has descriptor scale 1e6.',
        formula='M_13 = E_test(14)^T R_13 E_trial(14); R_13 = I - h/6 [4 J_mid (I/2 - h J_14/8) + J_14]',
        partition_available=False,
        required_partition_data=[
            'Stage-B 73x66 child coefficients transported into the endpoint-14 physical tangent frame, with retained reprojection residual.',
            'Seven owner-bound boundary/interface complement columns completing the 73D frame, including normalization and conditioning.',
            'Matching boundary residual rows or dual test transformation, with row ownership and descriptor scaling; descriptor is the eighth reaction coordinate.',
            'The existing 99D-to-74D construction records normal residuals; this extraction adds no nonlinear authority for them.',
        ],
        nonlinear_Mqq_variation_proved=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False,
    )
    if not invertible:
        raise ValueError('stored center inverse residual failed')
    return report, dict(M_13=matrix, inverse_proposal=inverse)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    report, arrays = extract()
    args.out.mkdir(parents=True, exist_ok=False)
    buffer = io.BytesIO()
    np.savez_compressed(buffer, **arrays)
    (args.out/'M_13.npz').write_bytes(buffer.getvalue())
    report['arrays_SHA256'] = digest(args.out/'M_13.npz')
    (args.out/'report.json').write_bytes(encoded(report))
    print('M_13:', report['shape'], 'condition:', report['condition_2'], 'inverse residual:', report['inverse_left_residual']['approximate_upper'])


if __name__ == '__main__':
    main()
