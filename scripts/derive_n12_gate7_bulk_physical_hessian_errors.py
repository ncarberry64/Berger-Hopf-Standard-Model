"""Bounded factored Hessian campaigns using exact bulk Arb matrix transfers."""
from pathlib import Path
import hashlib
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
import derive_n12_gate7_factored_physical_hessian_errors as factored
from bhsm.interface import bulk_arb_matrices as bulk

campaign = factored.campaign
ALGORITHM = 'PHYSICAL_MIDPOINT_HESSIAN_ERROR_ARB256_FACTORED_BULK_MATRICES_V3'
_installed = False


def load_inputs(interval):
    values, binding, _ = factored.load_inputs(interval)
    binding['algorithm'] = ALGORITHM
    for path in (Path(__file__), Path(bulk.__file__)):
        binding['sources'][path.relative_to(ROOT).as_posix()] = campaign.sha(path)
    binding['parent_matrix_converter_SHA256'] = dict(bulk.PARENT_SHA256)
    fingerprint = hashlib.sha256(json.dumps(binding, sort_keys=True).encode()).hexdigest().upper()
    return values, binding, fingerprint


def worker(interval, row, expected):
    install_backend()
    # Preserve the parent computation of base action jets and the eigenline.
    campaign.prepare_worker(interval, expected)
    with bulk.use_bulk_matrices(campaign.graph.cert):
        return factored.worker(interval, row, expected)


def install_backend():
    global _installed
    if _installed:
        return
    factored.install_backend()
    campaign.WORK = ROOT/'artifacts/flagship_integration/.bulk_physical_midpoint_hessian_error_work'
    campaign.load_inputs, campaign.worker = load_inputs, worker
    _installed = True


def integrate():
    """Reuse the physical DF/output consumer in this separate backend directory."""
    import argparse
    import numpy as np
    import certify_n12_gate7_physical_first_hessian_pullbacks as physical
    parser = argparse.ArgumentParser()
    parser.add_argument('--integrate', action='store_true', required=True)
    parser.add_argument('--midpoints', required=True)
    args = parser.parse_args()
    envelope = json.loads(physical.previous.arithmetic.RESULT.read_text())
    if envelope.get('validation_passed') is not True or envelope.get('coverage') != dict(intervals=370, nodes=371, complete=True):
        raise RuntimeError('complete kinematic arithmetic envelope required')
    physical.causal.prior.coordinate._verified_inputs(envelope)
    output = json.loads(physical.causal.prior.output.RESULT.read_text())
    directory = ROOT/'artifacts/flagship_integration/.physical_first_bulk_hessian_pullback_work'
    directory.mkdir(parents=True, exist_ok=True)
    for index in campaign.parse_intervals(args.midpoints):
        arrays, payload = physical.build_point(index, output)
        stem = directory/f'midpoint_{index:03d}'
        np.savez_compressed(stem.with_suffix('.npz'), **arrays)
        payload['data_SHA256'] = campaign.cache.file_sha(stem.with_suffix('.npz'))
        physical.causal.prior.coordinate._verified_inputs({'inputs': payload['source_SHA256']})
        stem.with_suffix('.json').write_text(json.dumps(payload, indent=2, sort_keys=True)+'\n')
        print(json.dumps(dict(interval=index, backend='bulk',
            local_pair_error=payload['local_pair_uniform_quadratic_coefficient_upper'])), flush=True)


def main():
    if '--adopt-first-midpoint' in sys.argv or '--aggregate' in sys.argv:
        raise ValueError('use the separate bulk cache and --integrate consumer')
    install_backend()
    if '--integrate' in sys.argv:
        integrate()
    else:
        campaign.main()


if __name__ == '__main__':
    main()
