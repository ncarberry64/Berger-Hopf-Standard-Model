"""Evaluate the derived delta-seam graph on frozen time/Higgs germs.

This application does not choose that graph as the full physical domain.
It preserves both original eta incidences, their actual spin alignment,
the once-only Dirac-bar conversion and every common-fibre coordinate.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from bhsm.interface.muon_full_d5_localized_lepton_trace import (
    full_d5_localized_lepton_trace, moving_d5_material_trace_frame,
)
from bhsm.interface.muon_continued_action_reality import _higgs_mass_realified
from bhsm.interface.muon_isotropic_seam_transfer import isotropic_seam_transfer_jets


KEYS = ('value', 'x', 'y', 'xy')


def jet(a, x=None, y=None, xy=None):
    a = np.asarray(a, complex)
    return dict(value=a, x=np.zeros_like(a) if x is None else np.asarray(x, complex),
                y=np.zeros_like(a) if y is None else np.asarray(y, complex),
                xy=np.zeros_like(a) if xy is None else np.asarray(xy, complex))


def maxabs(a):
    return float(np.max(abs(a)))


def product(a, b):
    # Independent implementation for the original literal Cayley equations.
    return dict(value=a['value'] @ b['value'],
                x=a['x'] @ b['value'] + a['value'] @ b['x'],
                y=a['y'] @ b['value'] + a['value'] @ b['y'],
                xy=a['xy'] @ b['value'] + a['x'] @ b['y']
                + a['y'] @ b['x'] + a['value'] @ b['xy'])


def literal_solve(a, rhs):
    from scipy.linalg import lu_factor, lu_solve
    lu = lu_factor(a['value'])
    out = dict(value=lu_solve(lu, rhs['value']))
    for k in ('x', 'y'):
        out[k] = lu_solve(lu, rhs[k] - a[k] @ out['value'])
    out['xy'] = lu_solve(lu, rhs['xy'] - a['xy'] @ out['value']
                        - a['x'] @ out['y'] - a['y'] @ out['x'])
    return out


def evaluate(output):
    out = Path(output)
    if not out.is_absolute():
        out = ROOT / out
    if out.exists():
        raise FileExistsError('Preserve each independently executed germ application')
    pins = {}

    def pin(path, expected=None):
        path = Path(path)
        digest = sha256(path.read_bytes()).hexdigest()
        if expected is not None and digest != expected:
            raise ValueError('Frozen input changed: ' + str(path))
        pins[path.relative_to(ROOT).as_posix()] = digest

    old = ROOT / 'artifacts/muon_trial_d5_trace_action_20261012/trial_0000_corrected_sigma_energy_0_run_2'
    old_report = json.loads((old / 'result.json').read_bytes())
    pin(old / 'result.json')
    full = full_d5_localized_lepton_trace()
    G = full['gamma5D_self_dual128']
    lift = lambda m: np.kron(np.eye(3), m)
    G0 = lift(G[0])
    PL = np.diag(np.r_[np.ones(12), np.zeros(6)])
    PR = np.eye(18) - PL
    records = []
    for stage in range(2):
        path = old / f'stage_{stage:04d}_current_geometry_normal_and_material_trace.npz'
        # The old report binds output bytes independently of this application.
        pin(path, old_report['archives'][path.name]['sha256'])
        with np.load(path, allow_pickle=False) as saved:
            a = {name: saved[name] for name in saved.files}
        U = a['material_wall_velocity'][-1]
        dU = a['material_wall_velocity_first'][0, -1]
        plus = moving_d5_material_trace_frame(-U, -dU, full_representation=full)
        minus = moving_d5_material_trace_frame(U, dU, full_representation=full)
        Sp, Sip = plus['spin_boost128'], plus['spin_boost_inverse128']
        Sm, Sim = minus['spin_boost128'], minus['spin_boost_inverse128']
        dSp, dSip = plus['spin_boost_first128'], plus['spin_boost_inverse_first128']
        dSm, dSim = minus['spin_boost_first128'], minus['spin_boost_inverse_first128']
        align = lift(Sm @ Sip)
        align_inv = lift(Sp @ Sim)
        dalign = lift(dSm @ Sip + Sm @ dSip)
        dalign_inv = lift(dSp @ Sim + Sp @ dSim)
        bp, bm = (a[f'eta_{s}_normalized_right_Gamma0'] for s in ('plus', 'minus'))
        dbp, dbm = (a[f'eta_{s}_normalized_right_Gamma0_first'][0] for s in ('plus', 'minus'))
        cp, cm = (a[f'eta_{s}_normalized_Dirac_bar_left_Gamma0'] for s in ('plus', 'minus'))
        dcp, dcm = (a[f'eta_{s}_normalized_Dirac_bar_left_Gamma0_first'][0] for s in ('plus', 'minus'))
        B = PL @ bp + PR @ bm @ align
        dB = PL @ dbp + PR @ (dbm @ align + bm @ dalign)
        # The left field is supplied independently. This analytic pullback
        # equals the real Riesz dual only on its originating real slice.
        C = G0 @ cp @ PL + G0 @ align_inv @ cm @ PR
        dC = G0 @ dcp @ PL + G0 @ (dalign_inv @ cm + align_inv @ dcm) @ PR
        rho = a['actual_intrinsic_surface_density'].item()
        clock = a['surface_proper_clock_rate'][-1]
        dclock = a['surface_proper_clock_rate_first'][0, -1]
        radius, dradius = a['radius'][-1], a['radius_first'][0, -1]
        drho = dclock * radius**3 + 3 * clock * radius**2 * dradius
        GNp = a['eta_plus_original_principal_normal_Clifford128']
        GNm = a['eta_minus_original_principal_normal_Clifford128']
        GTp = a['eta_plus_original_principal_time_Clifford128']
        GTm = a['eta_minus_original_principal_time_Clifford128']
        dGNp = dU * (U * G[4] - G[0]) / (np.sqrt(1 - U * U)**3)
        J0 = 1j * rho * G0 @ lift(GNp)
        Jx = 1j * G0 @ lift(drho * GNp + rho * dGNp)
        M0 = a['fixedY_Higgs_intrinsic_seam_matrix']
        Mx = _higgs_mass_realified(a['intrinsic_H_realified_first'][0])
        My = _higgs_mass_realified([0, 1, 0, 0])
        Jj, Bj, Cj = jet(J0, Jx), jet(B, dB), jet(C, dC)
        Tj = jet(rho * M0, drho * M0 + rho * Mx, rho * My, drho * My)
        result = isotropic_seam_transfer_jets(Jj, Cj, Tj, Bj)
        # A separate solve of (J-V/2)U=(J+V/2), with V=C T B,
        # is a literal check of the transfer and all contact derivatives.
        Vj = product(product(Cj, Tj), Bj)
        lhs = {k: Jj[k] - Vj[k] / 2 for k in KEYS}
        rhs = {k: Jj[k] + Vj[k] / 2 for k in KEYS}
        literal = literal_solve(lhs, rhs)
        transfer = result['transfer']
        comparison = {k: maxabs(transfer[k] - literal[k]) for k in KEYS}
        original = product(lhs, transfer)
        original = {k: maxabs(original[k] - rhs[k]) for k in KEYS}
        trace = product(Bj, transfer)
        trace_errors = {k: maxabs(trace[k] - Bj[k]) for k in KEYS}
        records.append(dict(
            stage=stage, common_full_field_count=384, one_sided_boundary_value_count=768,
            selected_trace_count=18, complementary_common_trace_count=348,
            input_is_complex_off_shell_germ=True,
            jump_orientation='plus outward normal, from plus field to spin-aligned minus field',
            x_axis='saved canonical coordinate-time first germ, with its declared parent/reference lifts',
            y_axis='partial ReH2 at fixed geometry, point traces, normal modes and gauge',
            zero_y_geometry_and_trace_contacts_are_declared_partial=True,
            energy_or_magnetic_source_jets_evaluated=False,
            common_alignment_inverse_max=maxabs(align_inv @ align - np.eye(384)),
            opposite_normal_alignment_max=maxabs(lift(GNm) @ align + align @ lift(GNp)),
            time_frame_alignment_max=maxabs(lift(GTm) @ align - align @ lift(GTp)),
            original_particle_Green_match_max=maxabs(J0[:64, :64] - a['original_Dirac_bar_Green_matrix']),
            original_particle_Green_first_match_max=maxabs(Jx[:64, :64] - a['original_Dirac_bar_Green_matrix_first'][0]),
            surface_density_source_match_abs=float(abs(rho - clock * radius**3)),
            literal_Cayley_comparison_max=comparison,
            original_literal_Cayley_rows_max=original,
            original_selected_trace_continuity_max=trace_errors,
            transfer_value_minus_identity_norm=float(np.linalg.norm(transfer['value'] - np.eye(384))),
            transfer_time_first_norm=float(np.linalg.norm(transfer['x'])),
            transfer_partial_H_first_norm=float(np.linalg.norm(transfer['y'])),
            transfer_mixed_time_H_norm=float(np.linalg.norm(transfer['xy'])),
            source_left_coefficients_conjugated=False,
            physical_Hilbert_current_unitarity_on_complex_germ_claimed=False,
        ))
    for rel in ('audits/bhsm_isotropic_seam_saved_germs_20261016.py',
                'src/bhsm/interface/muon_isotropic_seam_transfer.py',
                'src/bhsm/interface/muon_full_d5_localized_lepton_trace.py',
                'src/bhsm/interface/muon_holomorphic_d5_trace_action.py',
                'src/bhsm/interface/muon_continued_action_reality.py',
                'src/bhsm/interface/completion/foundational_dirac_spin_glue_v14_45.py'):
        pin(ROOT / rel)
    payload = dict(
        classification='DERIVED_NILPOTENT_DELTA_SEAM_ON_SAVED_COMPLEX_TIME_HIGGS_GERMS',
        records=records, input_hashes=dict(sorted(pins.items())),
        adopted_full_physical_domain=False,
        Cayley_comparison_is_algebraic_check_not_an_adopted_wall_average=True,
        older_literal_full_value_continuity_and_nonzero_seam_jump_simultaneously_claimed=False,
        physical_exterior_or_common_positive_master_realized=False,
        physical_energy_or_field_derivatives_evaluated=False,
        full_physical_derivative_at_2e_minus_10_passed=False,
        physical_radial_and_angular_convergence_established=False,
        coupled_matching_corrections_applied=0,
        normalized_physical_spin_states=None, physical_muon_magnetic_moment=None,
        new_profile_D5_source_or_history_integrations=0,
    )
    out.mkdir(parents=True)
    result_path = out / 'result.json'
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + '\n',
                           encoding='utf8', newline='\n')
    print(json.dumps(dict(sha256=sha256(result_path.read_bytes()).hexdigest(), records=records)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    evaluate(parser.parse_args().output)
