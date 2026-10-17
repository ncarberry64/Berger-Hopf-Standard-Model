"""Separate unsquared simple-pole and explicit electromagnetic-probe contractions.

This consumer does not choose a boundary, pole, magnetic field, photon residue,
charge calibration, or quantum vertex. Supplied left modes are analytic rows:
they are never conjugated here. An unprovided probe remains unprovided.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import zipfile

import numpy as np


def _matrix(value, name):
    if value is None:
        raise ValueError(name + ' is required')
    a = np.asarray(value, complex)
    if not np.isfinite(a).all():
        raise ValueError(name + ' must be finite')
    return a


def simple_unsquared_pole_response(gamma, gamma_energy, right, left, *,
                                  pole_energy, probe_rows=None):
    """Res=R(L Gamma_E R)^-1 L; E_a=-L Gamma_a R/(L Gamma_E R).

    One simple pole is consumed at its OWN energy. The full bordered inverse
    retains all boundary fibers and tests the simple-pole complement. A finite
    numerical result does not promote the supplied equation to a physical
    retarded exterior or identify its pole as a muon.
    """
    G, GE, r, l = [_matrix(v, n) for v, n in zip(
        (gamma, gamma_energy, right, left), ('Gamma', 'Gamma_E', 'right', 'left'))]
    E = complex(pole_energy)
    if G.ndim != 2 or G.shape[0] != G.shape[1] or GE.shape != G.shape:
        raise ValueError('same complete square Gamma and Gamma_E required')
    n = len(G)
    if r.shape == (n,): r = r[:, None]
    if l.shape == (n,): l = l[None, :]
    if r.shape != (n, 1) or l.shape != (1, n) or not np.isfinite(E):
        raise ValueError('one independently supplied analytic left/right pair and energy required')
    z = (l @ GE @ r).item()
    if z == 0:
        raise ValueError('simple-pole kinetic pairing is zero')
    residue = r @ l / z
    bordered = np.block([[G, GE @ r], [l @ GE, np.zeros((1, 1), complex)]])
    inv = np.linalg.solve(bordered, np.eye(n+1, dtype=complex))
    comp = inv[:n, :n]
    scale = np.linalg.norm(G, 2)
    right_row_scale = scale*np.linalg.norm(r)
    left_row_scale = scale*np.linalg.norm(l)
    result = dict(
        pole_energy=np.array(E), pole_mass_action=np.array(E.real),
        pole_width_action=np.array(-2*E.imag), pole_kinetic_pairing=np.array(z),
        pole_residue=residue, full_boundary_range_return=comp,
        original_right_pole_rows=G @ r, original_left_pole_rows=l @ G,
        relative_right_pole_rows=np.array(np.linalg.norm(G @ r)/(right_row_scale or 1)),
        relative_left_pole_rows=np.array(np.linalg.norm(l @ G)/(left_row_scale or 1)),
        residue_right_rows=G @ residue, residue_left_rows=residue @ G,
        full_bordered_inverse_rows=bordered @ inv-np.eye(n+1),
        right_complement_rows=G @ comp+GE @ r @ inv[n:, :n]-np.eye(n),
        left_complement_rows=comp @ G+inv[:n, n:] @ l @ GE-np.eye(n),
        normalized_kinetic_pairing=np.array(z/z),
        bordered_condition_number=np.array(np.linalg.cond(bordered)),
        boundary_and_mode_selection_performed=False,
        physical_pole_or_Pauli_admission_inferred=False,
        same_energy_spin_degeneracy_required=False,
        left_mode_conjugated=False, probe_supplied=probe_rows is not None)
    if probe_rows is not None:
        V = _matrix(probe_rows, 'all same-domain probe rows')
        if V.ndim != 3 or V.shape[1:] != G.shape or not len(V):
            raise ValueError('probe rows need (probes,all_boundary_rows,all_boundary_columns)')
        slope = -np.array([(l @ a @ r).item()/z for a in V])
        result.update(pole_probe_energy_first=slope,
                      pole_probe_mass_first=slope.real,
                      pole_probe_width_first=-2*slope.imag)
    return result


def physical_magnetic_probe_conversion(energy_probe_first, magnetic_field_probe_first):
    """Convert actual probe slopes by dE/dlambda=(dB_can/dlambda).grad_B E.

    B_can is measured in the supplied orthonormal physical frame. The caller
    must first apply the action-owned source, geometry, retarded boundary and
    quantum contacts. No direct source normalization is inferred from poles.
    At least three independent physical magnetic directions are required.
    """
    a = _matrix(energy_probe_first, 'energy probe first')
    b = np.asarray(magnetic_field_probe_first)
    if a.ndim != 1 or not np.isrealobj(b) or b.shape != (len(a), 3):
        raise ValueError('probe firsts and real (probes,3) physical magnetic firsts required')
    b = np.asarray(b, float)
    if not np.isfinite(b).all(): raise ValueError('finite magnetic firsts required')
    gradient, _, rank, singular = np.linalg.lstsq(b, a, rcond=None)
    if rank != 3: raise ValueError('three independent magnetic first directions required')
    return dict(energy_magnetic_first=gradient,
                complex_magnetic_moment=-gradient,
                mass_magnetic_first=gradient.real,
                width_magnetic_first=-2*gradient.imag,
                probe_conversion_original_rows=b @ gradient-a,
                probe_conversion_condition_number=float(singular[0]/singular[-1]),
                physical_probe_admission_not_inferred=True,
                quantum_Pauli_not_inferred=True)


def split_spin_longitudinal_response(plus_slope, minus_slope, *,
                                     plus_spin, minus_spin):
    """Read the affine spin coefficient from TWO distinct simple-pole slopes.

    Slopes must be for the SAME actual physical magnetic coordinate and control
    prescription. Supplied spin values are not inferred from energy ordering.
    No common baseline pole mass or zero-field degeneracy is imposed.
    """
    ep, em = complex(plus_slope), complex(minus_slope)
    sp, sm = float(plus_spin), float(minus_spin)
    if not np.isfinite([ep, em, sp, sm]).all() or sp == sm:
        raise ValueError('finite slopes and independently identified distinct spin values required')
    spin_energy = (ep-em)/(sp-sm)
    center = (sp*em-sm*ep)/(sp-sm)
    return dict(spin_energy_response=spin_energy,
                complex_moment_per_spin=-spin_energy,
                spin_independent_energy_response=center,
                original_plus_response_row=center+sp*spin_energy-ep,
                original_minus_response_row=center+sm*spin_energy-em,
                width_response_per_spin=-2*spin_energy.imag,
                common_rest_mass_not_selected=True,
                gyromagnetic_or_F2_promotion_performed=False)


def field_rescaling_identity():
    """One common field normalization cancels in moment/charge, not anisotropy."""
    import sympy as s
    c, mu, q, ct, cs = s.symbols('c mu q ct cs', nonzero=True)
    return dict(common_scale_ratio_residual=str(s.cancel(c*mu/(c*q)-mu/q)),
                unequal_temporal_spatial_scale_ratio=str(s.cancel(cs*mu/(ct*q))),
                absolute_moment_requires_explicit_field_normalization=True,
                common_normalization_cancels_only_with_same_EM_connection_and_clock=True,
                temporal_spatial_residue_mismatch_not_canceled=True,
                Lorentz_soft_limit_quantum_vertex_and_spin_identification_not_supplied=True,
                calibrated_charge_route_remains_a_declared_conditional_component=True,
                native_coupling_not_inferred_from_calibration=True)


def actual_complex_germ_current_normalization(h_realified, lapse, radius):
    """Native full18 source identities on supplied SAME-stage complex fields.

    These fields are an analytic finite coefficient germ, not a real physical
    Higgs/background or a magnetic probe. Both Higgs branches are retained;
    complex h coefficients are NOT conjugated to manufacture a real saddle.
    """
    from bhsm.interface.muon_source_directed_em_normal_current import holomorphic_charge_projection
    from bhsm.interface.muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
    from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
    from bhsm.interface.muon_continued_action_reality import _higgs_mass_realified
    h, N, R = [_matrix(v, n) for v, n in zip(
        (h_realified, lapse, radius), ('same-stage H', 'same-stage lapse', 'same-stage radius'))]
    if h.shape != (4,) or N.ndim != 1 or R.shape != N.shape or np.any(N == 0) or np.any(R == 0):
        raise ValueError('actual homogeneous Hreal4 and same-stage nonzero node lapse/radius required')
    norm = h @ h
    if norm == 0: raise ValueError('nonisotropic analytic Higgs axis required')
    hp, hm = h[:2]+1j*h[2:], h[:2]-1j*h[2:]
    P = np.outer(hp, hm)/norm
    Q = np.zeros((18, 18), complex)
    Q[:12, :12] = -np.kron(P, np.eye(6)); Q[12:, 12:] = -np.eye(6)
    s = holomorphic_charge_projection(h)['unit_Tr16_charge_coefficients']
    G = lepton_unit_trace_gauge_representation()['generators']
    alpha = lepton_current_hilbert_representation()['alpha']
    mass = _higgs_mass_realified(h)
    temporal = -1j*np.einsum('c,cij->ij', s, G)[None]/N[:, None, None]
    spatial = -1j*np.einsum('c,aij,cjk->aik', s, alpha, G)[None]/R[:, None, None, None]
    # An independently recomputed current chart, with the reciprocal field
    # coordinate change. This uses actual supplied fields, not missing B rows.
    scale = 1.7
    scaled_temporal = -1j*np.einsum('c,cij->ij', scale*s, G)[None]/N[:, None, None]
    scaled_spatial = -1j*np.einsum('c,aij,cjk->aik', scale*s, alpha, G)[None]/R[:, None, None, None]
    return dict(analytic_charge=Q, unit_Tr16_charge_coefficients=s,
                actual_temporal_current=temporal, actual_spatial_current=spatial,
                charge_idempotence_rows=Q @ Q+Q,
                generator_reconstruction_rows=1j*np.einsum('c,cij->ij', s, G)-Q,
                fixed_Y_mass_charge_rows=Q @ mass-mass @ Q,
                temporal_coframe_rows=N[:, None, None]*temporal+Q,
                spatial_coframe_rows=R[:, None, None, None]*spatial+alpha @ Q,
                reciprocal_source_field_temporal_rescaling_rows=scaled_temporal/scale-temporal,
                reciprocal_source_field_spatial_rescaling_rows=scaled_spatial/scale-spatial,
                actual_lapse=N, actual_radius=R, actual_H_realified=h,
                neutral_fibers_or_other_families_deleted=False,
                complex_H_branches_conjugated=False,
                physical_field_charge_photon_or_probe_admission=False)


def _json_scalar(z):
    z = complex(z)
    return dict(real=z.real, imag=z.imag)


def _deterministic_npz(path, arrays):
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, value in sorted(arrays.items()):
            b = BytesIO()
            np.lib.format.write_array(b, np.asarray(value), allow_pickle=False)
            info = zipfile.ZipInfo(name+'.npy', date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, b.getvalue())


def _source(path, needle):
    text = path.read_text(encoding='utf8')
    hits = [i for i, line in enumerate(text.splitlines(), 1) if needle in line]
    if not hits: raise ValueError('source anchor absent: '+str(path)+' '+needle)
    return dict(path=str(path), sha256=sha256(path.read_bytes()).hexdigest(),
                lines=hits, exact_anchor=needle)


def run(repository, output, packet=None, manifest=None):
    """Evaluate only explicitly bound pole packets; never create probe arrays."""
    root, out = Path(repository).resolve(), Path(output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    interface = root/'src/bhsm/interface'
    anchors = {
        'muon_unsquared_physical_boundary_pole.py':'Z=L Gamma_E R',
        'muon_retarded_spinor_tail_jet.py':'Every E/B/EB coefficient is',
        'muon_magnetic_open_lepton_vertex.py':'No e is',
        'muon_electromagnetic_soft_magnetic_source.py':'independently measured Thomson e',
        'muon_primal_electromagnetic_source.py':'canonical_EM_conversion=',
        'muon_holomorphic_em_current.py':'J=-Q/N;',
        'muon_local_charge_matching_response.py':'A_R=sqrt(Z_A) A;',
        'universal_precision_form_factor.py':'vertex.require_physical_promotion',
        'muon_source_directed_em_normal_current.py':'def holomorphic_charge_projection(',
        'muon_native_product_factor_graph.py':'def lepton_unit_trace_gauge_representation(',
        'muon_native_dirac_hamiltonian.py':'def lepton_current_hilbert_representation(',
        'muon_continued_action_reality.py':'def _higgs_mass_realified(',
    }
    citations = {f:_source(interface/f, anchor) for f, anchor in anchors.items()}
    arrays, records = {}, []
    inputs = {str(root/'AGENTS.md'):sha256((root/'AGENTS.md').read_bytes()).hexdigest()}
    if (packet is None) != (manifest is None):
        raise ValueError('packet and explicit key manifest must be supplied together')
    if packet is not None:
        packet, manifest = Path(packet).resolve(), Path(manifest).resolve()
        spec = json.loads(manifest.read_bytes())
        if spec.get('scope') != 'ACTUAL_FINITE_UNSQUARED_SPLIT_SIMPLE_POLE_PACKET':
            raise ValueError('explicit actual finite-pole packet scope required')
        inputs[str(manifest)] = sha256(manifest.read_bytes()).hexdigest()
        if packet.is_file():
            if sha256(packet.read_bytes()).hexdigest() != spec['packet_sha256']:
                raise ValueError('pole packet hash mismatch')
        import sys
        sys.path.insert(0, str(root/'src'))
        for j, binding in enumerate(spec['poles']):
            source = packet/binding['packet'] if packet.is_dir() else packet
            digest = sha256(source.read_bytes()).hexdigest()
            if packet.is_dir() and digest != binding['packet_sha256']:
                raise ValueError('individual actual pole packet hash mismatch')
            inputs[str(source)] = digest
            with np.load(source, allow_pickle=False) as data:
                names = ['gamma', 'gamma_energy', 'right', 'left', 'pole_energy']
                args = {name:data[binding[name]].copy() for name in names}
                if 'probe_rows' in binding:
                    args['probe_rows'] = data[binding['probe_rows']].copy()
                response = simple_unsquared_pole_response(**args)
                # Rescaling invariance on the ACTUAL supplied pole, not a toy.
                r, l = args['right'], args['left']
                changed = simple_unsquared_pole_response(**(args | dict(
                    right=r*(.7+.4j), left=l*(-.3+.8j))))
                rr = float(np.linalg.norm(response['pole_residue']-changed['pole_residue'])/
                           (np.linalg.norm(response['pole_residue']) or 1))
                record = dict(label=binding['label'],
                    pole_energy=_json_scalar(args['pole_energy']),
                    kinetic_pairing=_json_scalar(response['pole_kinetic_pairing']),
                    relative_original_right_pole_rows=float(response['relative_right_pole_rows']),
                    relative_original_left_pole_rows=float(response['relative_left_pole_rows']),
                    relative_residue_frame_rescaling_residual=rr,
                    bordered_inverse_maximum=float(np.max(abs(response['full_bordered_inverse_rows']))),
                    same_domain_probe_rows_supplied=response['probe_supplied'])
                if response['probe_supplied']:
                    record['probe_slopes'] = [_json_scalar(z) for z in response['pole_probe_energy_first']]
                    record['probe_frame_rescaling_residual'] = float(np.max(abs(
                        response['pole_probe_energy_first']-changed['pole_probe_energy_first'])))
                for name, value in response.items():
                    if isinstance(value, np.ndarray): arrays[f'pole_{j:03d}_{name}'] = value
                if 'same_stage_fields' in binding:
                    fields = binding['same_stage_fields']
                    normal = actual_complex_germ_current_normalization(*[
                        data[fields[k]].copy() for k in ('h_realified', 'lapse', 'radius')])
                    row_names = ('charge_idempotence_rows', 'generator_reconstruction_rows',
                                 'fixed_Y_mass_charge_rows', 'temporal_coframe_rows', 'spatial_coframe_rows',
                                 'reciprocal_source_field_temporal_rescaling_rows',
                                 'reciprocal_source_field_spatial_rescaling_rows')
                    record['same_stage_complex_germ_current_identity_maxima'] = {
                        name:float(np.max(abs(normal[name]))) for name in row_names}
                    record['source_field_scope'] = 'same-stage analytic finite complex coefficient germ; neither a real physical saddle nor a magnetic probe'
                    for name, value in normal.items():
                        if isinstance(value, np.ndarray): arrays[f'pole_{j:03d}_source_{name}'] = value
                records.append(record)
        _deterministic_npz(out/'actual_pole_contractions.npz', arrays)
    result = dict(
        scope='SEPARATE_SIMPLE_POLE_EM_PROBE_CONSUMER_AND_NORMALIZATION_AUDIT',
        executed_actual_pole_contractions=len(records), actual_poles=records,
        finite_original_reduced_null_rows_meet_2e_minus_10=all(
            max(x['relative_original_right_pole_rows'], x['relative_original_left_pole_rows']) <= 2e-10 for x in records) if records else None,
        finite_current_identity_rows_meet_2e_minus_10=all(
            max(x.get('same_stage_complex_germ_current_identity_maxima', {'not_supplied':float('inf')}).values()) <= 2e-10 for x in records) if records else None,
        actual_probe_contraction_evaluated=any(x['same_domain_probe_rows_supplied'] for x in records),
        physical_magnetic_response_evaluated=False,
        finite_control_is_not_physical_boundary_admission=True,
        physical_muon_moment=None, physical_g_mu=None, physical_a_mu=None,
        simple_pole_formula='E_a=-L Gamma_a R/(L Gamma_E R), evaluated separately at each own unsquared E_s',
        width_formula='Gamma_width=-2 Im(E); dGamma_width/da=-2 Im(dE/da)',
        magnetic_formula='mu_s^complex=-dE_s/dB_can; Re(mu_s)=-dRe(E_s)/dB_can; dwidth/dB_can=2 Im(mu_s)',
        split_spin_formula='mu_per_spin=-(dE_plus/dB-dE_minus/dB)/(S_plus-S_minus)',
        conditional_g_formula='Only on an admitted common rest/soft spin multiplet: g=2 M mu_per_spin/q_signed; a=g/2-1. M, signed charge, spin and pole scheme must be action-bound, not inferred from branch ordering.',
        separate_complex_poles_do_not_require_shared_rank_two_degeneracy=True,
        complex_resonance_response_not_forced_real=True,
        local_matched_Dirac_symbol_does_not_supply_interacting_Pauli=True,
        canonical_current='chi_hat=R4^(3/2)psi/(2pi^2), unit current Gram',
        canonical_connection='Omega_photon=-i e Q_H A_can; temporal material vertex=-Q_H/N; spatial orthonormal conversion uses 1/R4 once',
        no_extra_e_or_Haar_or_LSZ_factor_inserted=True,
        field_scale_identity=field_rescaling_identity(),
        still_required_for_physical_moment=[
            'Action-produced full retarded unsquared exterior boundary at each physical pole, including all energy and applied-field/source/domain/quantum contacts.',
            'Actual canonical magnetic curvature firsts in the selected proper spatial frame, with temporal/spatial normalization consistent on the same EM connection.',
            'Action-identified spin states/control prescription; two different energies alone do not prove a common rest spin multiplet or separate orbital response.',
            'Either declared calibrated EM charge/field units, or native photon residue and Ward charge application for independent BHSM coupling/absolute moment.',
            'For physical F2: complete same-action renormalized quantum vertex, external pole/residue, Ward closure and soft limit, not a local Clifford or matched-symbol projection.'
        ],
        measured_mass_anomaly_or_spin_branch_fit_used=False,
        completed_source_D5_profile_canonical_or_pairing_integrations_restarted=False,
        source_citations=citations, input_hashes=inputs,
        producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    if arrays:
        result['packet_sha256'] = sha256((out/'actual_pole_contractions.npz').read_bytes()).hexdigest()
    encoded = json.dumps(result, sort_keys=True, indent=2, allow_nan=False)+'\n'
    (out/'result.json').write_text(encoded, encoding='utf8', newline='\n')
    (out/'executed_producer.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(dict(path=str(out/'result.json'), sha256=sha256(encoded.encode()).hexdigest(),
                          actual_pole_count=len(records), actual_probe_contraction=result['actual_probe_contraction_evaluated'])))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--packet')
    parser.add_argument('--manifest')
    a = parser.parse_args()
    run(a.repository, a.output, a.packet, a.manifest)
