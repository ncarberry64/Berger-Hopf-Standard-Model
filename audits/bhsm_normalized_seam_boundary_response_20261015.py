"""New fixed-trace seam derivatives using already saved full D5 matrices.

The old D5/normal-profile/history integrations and pole searches are never
replayed. x is the stored unsquared-energy first germ; y is partial ReH2
at fixed geometry, trace and other fields. It is not the magnetic response.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys

import numpy as np
from scipy.linalg import lu_factor, lu_solve

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from bhsm.interface.muon_normalized_seam_schur_jets import normalized_seam_schur_jets
from bhsm.interface.muon_continued_action_reality import _higgs_mass_realified

KEYS = ('value', 'x', 'y', 'xy')


def jet(value, x=None, y=None, xy=None):
    a = np.asarray(value, complex)
    return dict(zip(KEYS, (a, *(np.zeros_like(a) if v is None else np.asarray(v, complex)
                              for v in (x, y, xy)))))


def maxabs(a):
    return float(np.max(abs(a)))


def difference(a, b):
    return dict(absolute=maxabs(a-b), scaled=maxabs(a-b)/max(1., maxabs(a), maxabs(b)))


def materialize(output):
    out = Path(output).resolve()
    if out.exists():
        raise FileExistsError(out)
    folder = ROOT/'artifacts/muon_trial_d5_trace_action_20261012/trial_0000_corrected_sigma_energy_0_run_2'
    pins = {}

    def pin(path, expected=None):
        value = sha256(path.read_bytes()).hexdigest()
        if expected is not None and value != expected:
            raise ValueError('Frozen D5 operand changed: '+path.name)
        pins[path.relative_to(ROOT).as_posix()] = value
        return value

    pin(folder/'result.json')
    report = json.loads((folder/'result.json').read_bytes())

    def read(name):
        path = folder/name
        pin(path, report['archives'][name]['sha256'])
        with np.load(path, allow_pickle=False) as data:
            return {key: data[key].copy() for key in data.files}

    My = _higgs_mass_realified(np.array([0, 1, 0, 0], complex))
    records = []
    for stage in (0, 1):
        a = read(f'stage_{stage:04d}_eta_two_sheet_normalized_field_Gamma.npz')
        c = read(f'stage_{stage:04d}_current_geometry_normal_and_material_trace.npz')
        K, Kx, B, C = (a[key] for key in ('eta_two_sheet_Dirac_bar_bulk_action',
            'eta_two_sheet_Dirac_bar_action_energy', 'normalized_two_sheet_right_trace',
            'normalized_two_sheet_Dirac_bar_left_trace'))
        rho = c['actual_intrinsic_surface_density'].item()
        M = c['fixedY_Higgs_intrinsic_seam_matrix']
        app = normalized_seam_schur_jets(jet(K, x=Kx), jet(B), jet(C), jet(rho), jet(M, y=My))
        nf, nt = len(K), len(B)
        if (nf, nt) != (768, 18):
            raise ValueError('Both full eta sheets and all three lepton families required')
        rhs = np.r_[np.zeros((nf, nt), complex), np.eye(nt)]
        # Independent direct FULL-SEAM factorization, not the bare-border
        # update used in the implementation. Original rows remain visible.
        Q = np.block([[K-rho*C@M@B, C], [B, np.zeros((nt, nt), complex)]])
        Qx = np.block([[Kx, np.zeros_like(C)], [np.zeros_like(B), np.zeros((nt, nt), complex)]])
        Qy = np.zeros_like(Q)
        Qy[:nf, :nf] = -rho*C@My@B
        factor = lu_factor(Q)
        z = lu_solve(factor, rhs)
        zx = lu_solve(factor, -Qx@z)
        zy = lu_solve(factor, -Qy@z)
        zxy = lu_solve(factor, -Qx@zy-Qy@zx)
        direct = dict(zip(KEYS, (z, zx, zy, zxy)))
        comparisons = {
            key: difference(app['full_seam_border_solution_jet'][key], direct[key])
            for key in KEYS}
        gamma = app['Gamma_full']
        G = np.linalg.solve(gamma['value'], np.eye(nt))
        Gx = -G@gamma['x']@G
        Gy = -G@gamma['y']@G
        Gxy = G@gamma['x']@G@gamma['y']@G+G@gamma['y']@G@gamma['x']@G-G@gamma['xy']@G
        # A direct full-field inverse/trace gives the same reduced Green.
        full_inverse_trace = B@np.linalg.solve(Q[:nf, :nf], C)
        mixed_inverse_rows = gamma['value']@Gxy+gamma['x']@Gy+gamma['y']@Gx+gamma['xy']@G
        record = dict(
            stage=stage, full_field_count=nf, normalized_trace_count=nt,
            retained_complementary_field_rows=nf-nt,
            old_saved_Gamma=difference(gamma['value'], a['finite_normalized_field_Gamma']),
            old_saved_Gamma_E=difference(gamma['x'], a['finite_normalized_field_Gamma_energy']),
            old_saved_Poisson=difference(app['full_field_Poisson']['value'], a['full_complementary_field_Poisson']),
            old_saved_seam=difference(app['seam_action_jet']['value'], a['eta_two_sheet_Dirac_bar_Higgs_seam_action']),
            independent_full_seam_solution_comparison=comparisons,
            original_bare_border_rows={key:maxabs(value) for key, value in app['original_bare_border_rows'].items()},
            original_full_seam_border_rows={key:maxabs(value) for key, value in app['original_full_seam_border_rows'].items()},
            original_trace_rows={key:maxabs(value) for key, value in app['original_trace_rows'].items()},
            algebraic_Poisson_invariance={key:maxabs(value) for key, value in app['algebraic_Poisson_invariance_rows'].items()},
            Gamma_partial_H_norm=float(np.linalg.norm(gamma['y'])),
            Gamma_partial_EH_norm=float(np.linalg.norm(gamma['xy'])),
            inverse_partial_H_norm=float(np.linalg.norm(Gy)),
            inverse_partial_EH_norm=float(np.linalg.norm(Gxy)),
            mixed_inverse_original_rows=maxabs(mixed_inverse_rows),
            full_field_inverse_trace_comparison=difference(G, full_inverse_trace),
            preserved_full_carrier_Higgs_spin_terms=True,
        )
        if max(v['scaled'] for v in comparisons.values()) > 2e-10:
            raise ArithmeticError('New seam update differs from literal full-border application')
        if record['Gamma_partial_H_norm'] == 0 or record['inverse_partial_EH_norm'] == 0:
            raise ArithmeticError('The actual nonzero Higgs response was erased')
        records.append(record)

    for name in ('muon_normalized_seam_schur_jets', 'muon_holomorphic_d5_trace_action',
                 'muon_full_d5_localized_lepton_trace', 'muon_continued_action_reality'):
        pin(ROOT/'src/bhsm/interface'/(name+'.py'))
    pin(Path(__file__).resolve())
    result = dict(
        classification='EVALUATED_EXISTING_FULL_NORMALIZED_SEAM_FIXED_TRACE_IDENTITY_AND_SOURCE_JETS',
        records=records, input_hashes=dict(sorted(pins.items())),
        source_coordinates='x=stored unsquared E first germ at E0=0; y=partial ReH2 at fixed geometry, gauge, normalized trace and density',
        unknown_total_source_contacts_assigned_zero=False,
        independent_analytic_left_source_conjugated=False,
        full_point_trace_seam_c45_already_supplied=True,
        new_interface_coupling_or_second_bulk_Higgs_mass=False,
        complex_primal_fields_projected_to_real=False,
        artificial_complex_corner_match_required_for_physical_prediction=False,
        new_D5_profile_source_history_integrations=0, old_completed_campaign_replays=0,
        finite_energy_or_Higgs_control_is_total_outgoing_E_or_B_derivative=False,
        physical_Higgs_quartic_or_vacuum_computed=False,
        finite_c_E1_identified_with_logdet_gluing=False,
        physical_full_outgoing_derivative_at_2e_minus_10_passed=False,
        physical_radial_convergence_established=False,
        coupled_matching_corrections_applied=0,
        physical_two_spin_normalization=None, physical_muon_magnetic_moment=None,
        original_Maxwell_after_correction=None, original226_after_correction=None,
    )
    for path, expected in pins.items():
        if sha256((ROOT/path).read_bytes()).hexdigest() != expected:
            raise RuntimeError('Consumed matrix or source changed during application')
    out.mkdir(parents=True)
    (out/'result.json').write_text(json.dumps(result, sort_keys=True, indent=2,
        allow_nan=False)+'\n', encoding='utf8', newline='\n')
    print(json.dumps(dict(records=records, sha256=sha256((out/'result.json').read_bytes()).hexdigest())))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    materialize(args.output)
