"""Freeze the current incoming reset tangent in the owned action metric.

Consumes the certified reset derivative; never reevaluates reset matching,
selects a kernel member, or promotes the tangent to a stationary solution.
"""
import argparse
from pathlib import Path
import json
import sys

import numpy as np
from flint import arb, arb_mat, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'scripts')]
from checkpoint_n12_gate7_66d_tangent_binding import digest, encoded, bound, restore
from differentiate_n12_gate7_fiber_constrained_center import save_arrays

BASE = ROOT / 'artifacts/flagship_integration'
POINT = BASE / 'gate7_current_formation_stationarity_20260927/run1'
CANDIDATE = BASE / 'gate7_current_reset_connection_20260927/reset_match_complete/candidate.npz'


def orthonormal_kernel_frame(projector, seed):
    """Outward Gram-Schmidt of the projected frozen seed, without repivoting.

    Basis orientation is inherited from the saved numerical frame. This is
    a coordinate convention on the entire kernel, not a physical selector.
    """
    if projector.nrows() != projector.ncols() or seed.nrows() != projector.ncols():
        raise ValueError('matching projector and seed required')
    columns = []
    projected = projector * seed
    for j in range(seed.ncols()):
        v = arb_mat(seed.nrows(), 1, [projected[i, j] for i in range(seed.nrows())])
        for q in columns:
            v -= q * (q.transpose() * v)[0, 0]
        square = (v.transpose() * v)[0, 0]
        if not square > 0:
            raise ArithmeticError('projected frozen basis lost certified independence')
        columns.append(v / square.sqrt())
    return arb_mat(seed.nrows(), seed.ncols(),
                   [columns[j][i, 0] for i in range(seed.nrows()) for j in range(seed.ncols())])


def calculate(out):
    ctx.prec = 512
    report = json.loads((POINT / 'report.json').read_bytes())
    if digest(POINT / 'arrays.npz') != report['arrays_SHA256']:
        raise ValueError('frozen current derivative changed')
    source_hashes = {name.replace('\\', '/'): sha for name, sha in report['source_SHA256'].items()}
    if digest(CANDIDATE) != source_hashes[CANDIDATE.relative_to(ROOT).as_posix()]:
        raise ValueError('current candidate changed')
    if (report['incoming_rank']['row_rank'], report['incoming_rank']['nullity']) != (32, 66):
        raise ValueError('current rank-32 / nullity-66 witness required')
    with np.load(POINT / 'arrays.npz') as z:
        J = restore(z, 'incoming_constraint_J')
        projector = restore(z, 'incoming_kernel_projector')
        seed = restore(z, 'incoming_kernel_basis_numerical')
    with np.load(CANDIDATE) as z:
        weights = [arb(float(v)) for v in z['state_weights']]
    if len(weights) != 98 or any(not w > 0 for w in weights):
        raise ValueError('owned positive 98D action-coordinate weights required')
    Q = orthonormal_kernel_frame(projector, seed)
    raw = arb_mat(98, 66, [Q[i, j] / weights[i] for i in range(98) for j in range(66)])
    eye = arb_mat(66, 66, [arb(i == j) for i in range(66) for j in range(66)])
    gram = Q.transpose() * Q
    orthogonality = bound(gram - eye)
    if orthogonality['approximate_upper'] >= 1:
        raise ArithmeticError('basis independence replay failed')
    arrays = dict(Q66_current=Q, Q66_current_raw=raw,
                  action_coordinate_weights=arb_mat(98, 1, weights),
                  reset_annihilator_replay=J * Q, action_gram=gram)
    out.mkdir(parents=True, exist_ok=False)
    save_arrays(out / 'arrays.npz', arrays)
    sources = [Path(__file__), POINT / 'arrays.npz', POINT / 'report.json', CANDIDATE,
               ROOT / 'src/bhsm/interface/aether_full_reset_action_jacobian.py']
    result = dict(status='CURRENT_RESET_COMPATIBLE_ACTION_METRIC_FRAME_FROZEN',
        source_commit='2e0a5fbd001df789e3b0ac0f9dd85659e2f0beb1',
        ambient_dimension=98, reset_rank=32, tangent_dimension=66,
        coordinates='action coordinates a=W*delta_state_raw; J_reset differentiates a',
        metric_raw='W^T W with the unchanged positive state_weights from the current candidate',
        covector_pairing='q_form=Q66_current^T*g_action=Q66_current_raw^T*g_raw',
        frame_convention='Project the saved basis and preserve its column order/orientation; no physical direction discarded',
        reset_annihilator=bound(J * Q), action_orthonormality=orthogonality,
        full_kernel_spanned=True,
        scope='Pointwise tangent enclosure at the saved candidate; not a stationary root or neighborhood certificate',
        physical_null_ownership='All 66 directions retained for formation stationarity; gauge/time ownership not inferred from reset rank',
        stationary_history_solved=False, formation_covector_evaluated=False,
        formation_hessian_evaluated=False, launch_forcing_evaluated=False,
        reset_matching_changed=False, selector_added=False, prefix_rerun=False,
        Gate7_closed=False, FULL_BHSM_COMPLETE=False,
        source_SHA256={p.relative_to(ROOT).as_posix(): digest(p) for p in sources},
        arrays_SHA256=digest(out / 'arrays.npz'))
    (out / 'report.json').write_bytes(encoded(result))
    print(json.dumps({k: result[k] for k in ('status', 'reset_annihilator', 'action_orthonormality')}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    calculate(parser.parse_args().out)
