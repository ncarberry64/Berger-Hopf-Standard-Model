"""Exact source-convention controls for the conditional regular D5 pole.

This audit retains both Clifford branches and orientations, checks the
polar spin rotation against differentiated source PW functions, and
evaluates complete scalar-PW blocks through n=4. It does not select a
state, truncate a physical angular solution, or evaluate an outgoing gate.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import sys
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import mpmath as mp
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
from bhsm.interface.muon_intrinsic_scalar_discretization import (
    scalar_angular_derivative_matrices, scalar_basis_values)


def maximum(a):
    return float(np.max(np.abs(a)))


def archive(path, arrays):
    """Stable NPZ order/timestamps, preserving every stored array value."""
    with ZipFile(path, 'w', compression=ZIP_DEFLATED, compresslevel=9) as out:
        for name in sorted(arrays):
            stream = BytesIO()
            np.lib.format.write_array(stream, np.asarray(arrays[name]), allow_pickle=False)
            member = ZipInfo(name + '.npy', date_time=(1980, 1, 1, 0, 0, 0))
            member.compress_type = ZIP_DEFLATED
            member.external_attr = 0o600 << 16
            out.writestr(member, stream.getvalue(), compresslevel=9)


def expected_spectrum(n):
    result = [-(n + 1.5)] * ((n + 1) * (n + 2))
    if n:
        result += [-(n + .5)] * (n * (n + 1))
        result += [n + .5] * (n * (n + 1))
    result += [n + 1.5] * ((n + 1) * (n + 2))
    return np.asarray(result)


def quaternion_components(q, sigma):
    return np.r_[np.array([np.trace(s @ q) / (2j) for s in sigma]), np.trace(q) / 2]


def spin_frame(q, gamma, eps, sigma):
    x = quaternion_components(q, sigma)
    omega = gamma[1] @ gamma[2] @ gamma[3] @ gamma[4]
    pplus = (np.eye(4) + eps * omega) / 2
    pminus = np.eye(4) - pplus
    return pplus + (x[3] * np.eye(4) + eps * sum(
        x[a] * gamma[a + 1] @ gamma[4] for a in range(3))) @ pminus


def evaluate():
    full = full_d5_localized_lepton_trace()
    sigma = np.array([[[0, 1], [1, 0]], [[0, -1j], [1j, 0]], [[1, 0], [0, -1]]], complex)
    raw = np.array([[0, 0, 0, 1], [1, 2, 3, 4], [-2, 1, 3, 1],
                    [3, -4, 1, -2], [0, 1, 0, 0]], float)
    xyz = raw / np.linalg.norm(raw, axis=1)[:, None]
    points = xyz[:, 3, None, None] * np.eye(2) + 1j * np.einsum('pa,aij->pij', xyz[:, :3], sigma)
    phi = scalar_basis_values(points, 1)
    E1 = scalar_angular_derivative_matrices(1)
    # Differentiate the actual source level1 coefficients FIRST; only then
    # reconstruct quaternion coordinates. No guessed coordinate vector field.
    dpoints = np.array([(phi @ E1[a])[:, 1:].reshape(-1, 2, 2).conj() / np.sqrt(2)
                        for a in range(3)])
    arrays = dict(quaternion_points=points, quaternion_components=xyz,
                  source_level1_values=phi, source_level1_E=E1,
                  source_differentiated_quaternion_points=dpoints)
    records = []
    frame_records = []
    for branch in ('particle', 'conjugate'):
        gamma = full['gamma5D_' + branch]
        arrays['gamma_' + branch] = gamma
        for eps in (-1, 1):
            omega = gamma[1] @ gamma[2] @ gamma[3] @ gamma[4]
            pminus = (np.eye(4) - eps * omega) / 2
            ja = np.array([eps * gamma[a + 1] @ gamma[4] @ pminus for a in range(3)])
            for n in range(5):
                start = sum((k + 1) ** 2 for k in range(n))
                h = (n + 1) ** 2
                E = scalar_angular_derivative_matrices(n)[:, start:start + h, start:start + h]
                angular = sum(np.kron(gamma[a + 1], E[a]) for a in range(3))
                K = -eps * np.kron(gamma[4], np.eye(h)) @ (angular
                    - 1.5 * np.kron(gamma[1] @ gamma[2] @ gamma[3], np.eye(h)))
                alpha = np.kron(eps * gamma[0] @ gamma[4], np.eye(h))
                eig = np.linalg.eigvalsh(K)
                expected = expected_spectrum(n)
                prefix = f'{branch}_eps{eps}_n{n}'
                arrays[prefix + '_K'] = K
                arrays[prefix + '_eigenvalues'] = eig
                arrays[f'E_n{n}'] = E
                records.append(dict(branch=branch, sheet_orientation=eps, scalar_PW_level=n,
                    scalar_harmonic_count=h, spin_block_width=4 * h,
                    full_retained_width_at_this_scalar_level=384 * h,
                    Hermitian_defect=maximum(K - K.conj().T),
                    alpha_K_anticommutator=maximum(alpha @ K + K @ alpha),
                    spectrum_error=maximum(eig - expected),
                    angular_gap=float(np.min(abs(eig))),
                    minimum_radial_square_contact=float(np.min(eig * (eig - 1))),
                    exact_expected_eigenvalues=expected.tolist()))
            for p, q in enumerate(points):
                S = spin_frame(q, gamma, eps, sigma)
                dS = []
                literal_errors = []
                for a in range(3):
                    dx = quaternion_components(dpoints[a, p], sigma)
                    derivative = (dx[3] * np.eye(4) + eps * sum(
                        dx[b] * gamma[b + 1] @ gamma[4] for b in range(3))) @ pminus
                    dS.append(derivative)
                    # An independent literal SU2 flow evaluates the unmodified
                    # frame at four points; every step result is retained.
                    for step in (1e-3, 3e-4, 1e-4):
                        def at(t):
                            return spin_frame((np.cos(t) * np.eye(2)
                                - 1j * np.sin(t) * sigma[a]) @ q, gamma, eps, sigma)
                        fd = (at(-2 * step) - 8 * at(-step) + 8 * at(step) - at(2 * step)) / (12 * step)
                        literal_errors.append(dict(axis=a + 1, step=step,
                            derivative_absolute_error=maximum(fd - derivative)))
                dS = np.asarray(dS)
                contact = sum(gamma[a + 1] @ S.conj().T @ dS[a] for a in range(3))
                target = 1.5 * eps * gamma[4] - 1.5 * gamma[1] @ gamma[2] @ gamma[3]
                prefix = f'{branch}_eps{eps}_point{p}'
                arrays[prefix + '_S'] = S
                arrays[prefix + '_source_dS'] = dS
                frame_records.append(dict(branch=branch, sheet_orientation=eps, quaternion_index=p,
                    unitary_defect=maximum(S.conj().T @ S - np.eye(4)),
                    positive_current_pairing_defect=maximum(S.conj().T @ S - np.eye(4)),
                    Gamma0_commutator=maximum(S @ gamma[0] - gamma[0] @ S),
                    coordinate_right_body_identity=max(maximum(dpoints[a, p] + 1j * sigma[a] @ q) for a in range(3)),
                    source_differentiated_frame_identity=maximum(dS + np.array([S @ j for j in ja])),
                    exact_spin_connection_identity=maximum(contact - target),
                    original_round_Dirac_contact_identity=maximum(1j * (contact - 1.5 * eps * gamma[4])
                        + 1.5j * gamma[1] @ gamma[2] @ gamma[3]),
                    oriented_radial_frame_identity=maximum(S @ (eps * gamma[4]) @ S.conj().T
                        - (eps * xyz[p, 3] * gamma[4] - sum(xyz[p, a] * gamma[a + 1] for a in range(3)))),
                    literal_SU2_flow_derivative_steps=literal_errors))
    with mp.workdps(80):
        k = mp.mpf(3) / 2
        x = k / mp.sqrt(2)
        ratio = mp.sqrt(k * k + 4 * x * x) / (k * k + x * x)
        c = 1 - 4 / (3 * mp.sqrt(3))
        coercivity = dict(minimum_angular_gap='3/2', maximizing_x_squared='kappa^2/2',
            maximum_negative_matrix_ratio=mp.nstr(ratio, 70),
            exact_ratio='4/(3*sqrt(3))', uniform_form_lower_constant=mp.nstr(c, 70),
            exact_constant='1-4/(3*sqrt(3))',
            applies_to_all_frozen_angular_and_time_frequencies=True,
            variable_coefficient_extension_requires_regular_cap_remainder_bounds=True)
    source_paths = [Path(__file__).resolve(), ROOT / 'src/bhsm/interface/muon_full_d5_localized_lepton_trace.py',
        ROOT / 'src/bhsm/interface/muon_intrinsic_scalar_discretization.py',
        ROOT / 'src/bhsm/interface/muon_holomorphic_d5_trace_action.py',
        ROOT / 'src/bhsm/interface/muon_local_source_jet.py',
        ROOT / 'src/bhsm/interface/completion/foundational_dirac_spin_glue_v14_45.py',
        ROOT / 'src/bhsm/interface/muon_moving_geometric_action.py',
        ROOT / 'src/bhsm/interface/muon_exact_material_response.py',
        ROOT / 'src/bhsm/interface/muon_combined_f_eta_contact.py']
    result = dict(schema='bhsm-real-d5-polar-center-source-controls-v1',
        source_pins={str(p.relative_to(ROOT)).replace('\\', '/'): sha256(p.read_bytes()).hexdigest() for p in source_paths},
        input_assumptions=dict(regular_combined_f_continuation=True,
            center_radial_coframe_C0_positive=True, center_lapse_N0_positive=True,
            center_f_radial_slope_k_positive=True,
            C_rho_means_radial_coframe_not_derivative=True,
            smooth_cap_source_geometry=True, numerical_coefficients_are_fixed_source_matrices=True),
        angular_records=records, frame_records=frame_records, coercivity=coercivity,
        full_384_carrier_retained_by_exact_internal_and_family_identity=True,
        no_extra_particle_or_spin_multiplicity_inserted=True,
        control_angular_cutoff_n=4, theorem_angular_output_untruncated=True,
        polar_spin_frame_is_unitary=True, scalar_sin_f_similarity_is_unitary=False,
        local_form_domain='H1 closure under the stated regular cap coefficient premises',
        strong_operator_domain_distinct=True,
        strong_operator_examples=dict(kappa_negative_three_halves=dict(
            smooth_constant_U_power='3/2', finite_form=True, strong_P_U_power='-1/2',
            strong_P_U_is_L2=False, regular_operator_root='5/2', excluded_operator_root='-3/2'),
            kappa_positive_three_halves=dict(regular_operator_root='3/2', excluded_operator_root='-1/2')),
        empirical_comparison_used=False, physical_state_or_normal_mode_selected=False,
        global_native_or_outgoing_domain_completed=False, physical_derivative_gate_passed=False,
        matching_correction_count=0, magnetic_moment_prediction=None)
    return result, arrays


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('A new output directory is required; preserve prior controls.')
    args.output.mkdir(parents=True)
    result, arrays = evaluate()
    archive(args.output / 'controls.npz', arrays)
    result['archive_sha256'] = sha256((args.output / 'controls.npz').read_bytes()).hexdigest()
    (args.output / 'result.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(dict(angular_records=len(result['angular_records']),
        frame_records=len(result['frame_records']), archive_sha256=result['archive_sha256'])))


if __name__ == '__main__':
    main()
