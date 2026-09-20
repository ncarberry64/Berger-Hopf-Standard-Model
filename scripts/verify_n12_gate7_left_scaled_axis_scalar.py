"""Replay fixed-axis scalar coefficients and their original error inclusions."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'scripts')]
import certify_n12_gate7_left_longitudinal_transport as transport
from flint import arb, arb_mat, ctx
import numpy as np


def verify(root, family, folder, parent_folder, adjoint):
    import bhsm.interface
    bhsm.interface.__path__.insert(0, str(root / 'src/bhsm/interface'))
    verified = transport.saved.evaluate(root)
    parent = json.loads((parent_folder / 'record.json').read_bytes())
    if parent['family'] != family:
        raise ValueError('matching original physical family required')
    axis_file = root / 'artifacts/action_extension/BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.npz'
    with np.load(axis_file, allow_pickle=False) as data:
        axes = data['current_center_green_image_unit_mid'].copy()
    axes[1:] /= np.linalg.norm(axes[1:], axis=1)[:, None]
    axis = arb_mat(74, 1, [arb(float(v)) for v in axes[13]])
    domain = transport.TaylorDomain(parent['original_state_groups'], 373 if family == 'midpoint' else 199)
    error_map = transport.error_maps.load_error_map(root, parent, adjoint)
    scalar, scales = transport.load_scalar(folder, parent, domain, axis, error_map, verified)
    if len(scales) != 124:
        raise ValueError('all original directional correction coordinates required')
    import diagnose_n12_gate7_directed_trial_hs_column as base
    # Resolve all modules needed by the final source guard before its heavy run.
    modules = (base, base.reader, base.p, base.p.values, base.p.values.cert)
    module_hashes = {module.__name__: transport.saved.sha(Path(module.__file__)) for module in modules}
    return dict(
        algorithm='LEFT_SCALED_AXIS_SOURCE_AND_COEFFICIENT_REPLAY_V1', family=family,
        all_124_auxiliary_rescalings_verified_against_original_uniform_derivative=True,
        scalar_coefficients_and_bounds_replayed=True,
        record_SHA256=transport.saved.sha(folder / 'record.json'),
        parent_record_SHA256=transport.saved.sha(parent_folder / 'record.json'),
        verifier_SHA256=transport.saved.sha(Path(__file__)),
        transport_loader_SHA256=transport.saved.sha(Path(transport.__file__)),
        resolved_transport_modules=module_hashes,
        scalar_support=transport.upper(scalar.support()),
        scalar_remainder=transport.upper(scalar.r),
        Gate7_closed=False, FULL_BHSM_COMPLETE=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--family', choices=('midpoint', 'endpoint'), required=True)
    for name in ('evidence-root', 'scalar', 'parent', 'adjoint', 'out'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    ctx.prec = 512
    result = verify(args.evidence_root.resolve(), args.family, args.scalar, args.parent, args.adjoint)
    with args.out.open('xb') as stream:
        stream.write(transport.saved.encoded(result))
    print(json.dumps({key: result[key] for key in ('family', 'scalar_support', 'scalar_remainder')}))


if __name__ == '__main__':
    main()
