"""Apply fixed-Y coefficients and both canonical magnetic directions."""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
sys.path.insert(0, str(ROOT/'scripts'))
from bhsm.interface.muon_common_y_current_response import (
    block_bidiagonal, common_y_inverse_action, common_y_rectangular_source_jet,
    polynomial_current_pairing, paired_fixed_y_polynomial,
    exact_stored_inverse_tail, certify_current_pairing)
from evaluate_muon_reached_trace_action import deterministic_archive


def rectangular_midpoint_blocks(values):
    v = np.asarray(values, complex)
    steps, nt, ns = v.shape
    out = np.zeros((steps*nt, steps*ns), complex)
    for j in range(steps):
        out[j*nt:(j+1)*nt, j*ns:(j+1)*ns] = v[j]/2
        if j:
            out[j*nt:(j+1)*nt, (j-1)*ns:j*ns] = v[j]/2
    return out


def literal_midpoint_current(values, weights):
    l = np.asarray(values, complex)*weights[:, None, None]/2
    l = l + np.concatenate((l[1:], np.zeros_like(l[:1])))
    return l.transpose(1, 0, 2).reshape(l.shape[1], -1)


def n1_matrices(data):
    steps = len(data['proper_cell_weights'])
    identity = np.eye(24)
    alpha, E = data['alpha6'], data['n1_right_body_derivatives']
    H0 = np.array([np.kron(h, np.eye(4))-1j*sum(np.kron(a, e) for a, e in zip(alpha, E))/r
        for h, r in zip(data['common_Hcan0'], data['R4'])])
    H1 = np.array([np.kron(h, np.eye(4)) for h in data['common_Hcan1']])
    diagonal = -1j*identity[None]/data['proper_cell_weights'][:, None, None]+H0/2
    lower = 1j*identity[None]/data['proper_cell_weights'][:, None, None]+H0/2
    return (block_bidiagonal(diagonal, lower), block_bidiagonal(H1/2, H1/2),
        np.array([np.kron(x, np.eye(4)) for x in data['source_right_map']]).reshape(steps*24, 24),
        literal_midpoint_current(np.array([np.kron(x, np.eye(4)) for x in data['target_left_map']]),
            data['proper_cell_weights']))


def materialize(output, *, input_folder, refinements=(16, 32, 64), order=4):
    out = ROOT/output
    if out.exists():
        raise FileExistsError('preserve earlier common fixed-Y applications')
    folder = ROOT/input_folder
    md = json.loads((folder/'result.json').read_bytes())
    refs = dict(md['input_hashes'])
    refs[(folder/'result.json').relative_to(ROOT).as_posix()] = sha256((folder/'result.json').read_bytes()).hexdigest()
    records = []
    files = {}
    pending = []
    for side in ('incoming', 'outgoing'):
        previous = None
        for steps in refinements:
            p = folder/f'{side}_{steps}.npz'
            digest = sha256(p.read_bytes()).hexdigest()
            if digest != md['array_archives'][p.name]['sha256']:
                raise ValueError('continued canonical factor changed')
            refs[p.relative_to(ROOT).as_posix()] = digest
            with np.load(p, allow_pickle=False) as a:
                data = {k:a[k].copy() for k in a.files}
            A0 = block_bidiagonal(data['A0_diagonal'], data['A0_lower'])
            A1 = block_bidiagonal(data['A1_diagonal'], data['A1_lower'])
            R = data['source_right_map'].reshape(steps*6, 6)
            L = literal_midpoint_current(data['target_left_map'], data['proper_cell_weights'])
            y = data['family_Y'][1:]
            u = common_y_inverse_action(A0, A1, R[None], order=order)
            current = polynomial_current_pairing(L[None], u['coefficients'])
            paired = paired_fixed_y_polynomial(current, *y)
            print(json.dumps(dict(stage='certifying_actual_common_Y_current', side=side, steps=steps)), flush=True)
            cert = exact_stored_inverse_tail(A0, A1, R, y, order=order, computed_coefficients=u['coefficients'])
            current_cert = certify_current_pairing(L, u['coefficients'], paired, y, cert)
            a = dict(common_response_coefficients=u['coefficients'], original_recurrence_residuals=u['recurrence_residuals'],
                literal_current_coefficients=current, paired_literal_current=paired,
                canonical_Y0_source=R, literal_current_target=L)
            t0, t1, tr, tl = n1_matrices(data)
            tu = common_y_inverse_action(t0, t1, tr[None], order=order)
            forward, reverse = [], []
            for axis in range(3):
                d = np.array([rectangular_midpoint_blocks(data[f'magnetic_right_Y{k}'][:, axis]) for k in (0, 1)])
                dl = np.array([rectangular_midpoint_blocks(data[f'magnetic_left_Y{k}'][:, axis]) for k in (0, 1)])
                f = common_y_rectangular_source_jet(t0, t1, u['coefficients'], d,
                    np.zeros((1, len(t0), 6), complex), order=order)
                r = common_y_rectangular_source_jet(A0, A1, tu['coefficients'], dl,
                    np.zeros((1, len(A0), 24), complex), order=order)
                forward.append(polynomial_current_pairing(tl[None], f['coefficients']))
                reverse.append(polynomial_current_pairing(L[None], r['coefficients']))
                a[f'magnetic_forward_{axis}_original_residuals'] = f['recurrence_residuals']
                a[f'magnetic_reverse_{axis}_original_residuals'] = r['recurrence_residuals']
            a['magnetic_forward_coefficients'] = np.array(forward)
            a['magnetic_reverse_coefficients'] = np.array(reverse)
            a['paired_magnetic_forward'] = np.array([paired_fixed_y_polynomial(c, *y) for c in forward])
            a['paired_magnetic_reverse'] = np.array([paired_fixed_y_polynomial(c, *y) for c in reverse])
            a['fixed_family_Y'] = y.copy()
            a['family_indices'] = data['family_indices'].copy()
            pending.append((f'{side}_{steps}.npz', a))
            row = dict(side=side, steps=steps, order=order,
                paired_current_norm=float(np.linalg.norm(paired)), current_certificate=current_cert,
                response_certificate=cert, common_Y0_current_norm=float(np.linalg.norm(current[0])),
                original_recurrence_residual_norm=float(np.linalg.norm(u['recurrence_residuals'])),
                paired_magnetic_forward_norm=float(np.linalg.norm(a['paired_magnetic_forward'])),
                paired_magnetic_reverse_norm=float(np.linalg.norm(a['paired_magnetic_reverse'])),
                paired_current_refinement_difference=None if previous is None else float(np.linalg.norm(paired-previous)),
                magnetic_coefficient_residual_norm=float(np.sqrt(sum(np.linalg.norm(a[k])**2 for k in a
                    if k.startswith('magnetic_') and k.endswith('_original_residuals')))))
            previous = paired
            records.append(row)
            print(json.dumps(dict(stage='evaluated_actual_common_Y_current', **row), sort_keys=True), flush=True)
    for p in ('src/bhsm/interface/muon_common_y_current_response.py', 'tests/test_muon_common_y_current_response.py',
        Path(__file__).relative_to(ROOT).as_posix()):
        refs[p] = sha256((ROOT/p).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest() != h for p, h in refs.items()):
        raise RuntimeError('consumed canonical action changed')
    out.mkdir(parents=True)
    for name, arrays in pending:
        p = out/name
        deterministic_archive(p, arrays)
        files[name] = dict(bytes=p.stat().st_size, sha256=sha256(p.read_bytes()).hexdigest())
    result = dict(classification='EVALUATED_COMMON_FIXED_Y_CANONICAL_CURRENT_AND_BOTH_MAGNETIC_DIRECTIONS',
        input_hashes=refs, array_archives=files, records=records,
        source_domain='same canonical initial-zero/free-final midpoint inverse; constant C6 and full n1 C6 angular images',
        action='continued A_E=-D_L; physical fixed-family Y0/Y1 coefficient recurrence on identical retained fields',
        common_Y0_cancels_with_provenance='identical action/source/current coefficient, removed algebraically before family evaluation',
        magnetic_contacts='both adjacent nodal values; source and target inverse motion; actual canonical delta-H including temporal -iG/N and fixed-Y delta-Higgs; literal reverse retained',
        current_direction_zeros='in this fixed-geometry gauge/H partial, EM charge maps and proper-clock weights have no field/Y variation',
        higher_Y_terms='order-four polynomial; finite stored uninserted-current arithmetic and tail certified; magnetic tail and entry/temporal errors remain separate',
        both_fermion_inverse_Y_insertions=True, odd_Y_powers_preserved=True,
        no_physical_family_spectral_subtraction=True, no_physical_covariance_selected=True,
        complete_loop_or_overlap_subtracted_Pauli=False, physical_a_mu=None, physical_g_mu=None,
        error_scope='exact stored finite-current arithmetic/Y-tail only; magnetic coefficient binary residuals and temporal refinements are diagnostics; no quantum-loop/relative-completion/physical Pauli enclosure')
    (out/'result.json').write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf8', newline='\n')
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--input-folder', type=Path, default=Path('artifacts/muon_continued_current_factor_20261011/run_1'))
    p.add_argument('--refinements', type=int, nargs='+', default=[16,32,64])
    a = p.parse_args()
    print(json.dumps(materialize(a.output, input_folder=a.input_folder, refinements=tuple(a.refinements)), sort_keys=True))
