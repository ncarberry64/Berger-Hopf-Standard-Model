"""Actual retained intrinsic-Higgs conormal, separate from algebraic HS.

Read the frozen full536 derivative packet; do not rerun its action/source
campaign. Reconstruct scalar wall weights from literal geometry primitives,
and temporal connection directly from the actual stored gauge basis and raw
gauge coefficients. Compare independent conormal and directional derivatives
against the saved action gradient/Hessian. No physical worldvolume F/U is
fabricated for the retained complex analytic germ.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys


def evaluate(repository, output):
    import numpy as np
    root, out = Path(repository).resolve(), Path(output).resolve()
    if out.exists():
        raise FileExistsError('Preserve every earlier application.')
    sys.path.insert(0, str(root / 'src'))
    from bhsm.interface.muon_holomorphic_normal_geometry import (
        _geometry_variables, _fields, _sqrt,
    )
    from bhsm.interface.muon_literal_euclidean_wall_action import VOLUME
    from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz

    rel = 'artifacts/muon_action_domain_construction_20261015/run_3/literal_action_and_directional_contacts.npz'
    candidate_rel = 'artifacts/muon_fixed_parent_finite_shooting_20261012/run_1/trial_0000/candidate.npz'
    basis_rel = 'artifacts/muon_parent_gauge_geometry_correction_20261010/finite_moving_trace_run_1/application.npz'
    basis_receipt_rel = basis_rel.replace('application.npz','result.json')
    comparison_receipt_rel = rel.replace('literal_action_and_directional_contacts.npz','result.json')
    basis_receipt = json.loads((root/basis_receipt_rel).read_bytes())
    comparison_receipt = json.loads((root/comparison_receipt_rel).read_bytes())
    basis_sha = sha256((root/basis_rel).read_bytes()).hexdigest()
    if basis_sha != basis_receipt['numerical_sha256']:
        raise ValueError('Recorded gauge basis changed.')
    if basis_sha != comparison_receipt['input_hashes'][basis_rel]:
        raise ValueError('Not the basis used in the saved full536 derivative.')
    if basis_receipt['gauge_count'] != 80:
        raise ValueError('Full 80-coefficient gauge representation required.')
    with np.load(root/basis_rel,allow_pickle=False) as archive:
        wall_map = archive['wall_trace_map'].copy()
    if wall_map.shape != (5,4,80):
        raise ValueError('Original complete wall trace map required.')
    generators = higgs_u2_real_representation()['real_generators']
    with np.load(root / rel, allow_pickle=False) as archive:
        raw = archive['raw_pair'].copy()
        reference = archive['reference_pair'].copy()
        gradient = archive['raw_gradient'].reshape(2, 268).copy()
        hessian = archive['raw_hessian'].copy()
        directions = archive['directions'].copy()
    with np.load(root / candidate_rel, allow_pickle=False) as archive:
        if not np.array_equal(raw, archive['raw_pair']):
            raise ValueError('Saved derivative packet is not this retained candidate.')
        if not np.array_equal(reference, archive['reference_pair']):
            raise ValueError('Anchored reference differs.')

    records, arrays = [], dict(raw_pair=raw, reference_pair=reference,
        actual_wall_trace_map=wall_map, real4_Higgs_gauge_generators=generators)
    direct_momenta, direct_connections, saved_connections, weights = [], [], [], []
    direct_jets, saved_jets, wall_coefficients = [], [], []
    for arm in range(2):
        q, v, m, delta, rate, wall, _ = _geometry_variables(
            raw[arm, :100], differentiate=True)
        field = _fields(12, q, v, m, wall)
        a, b, lapse0 = (field[key] for key in ('A', 'B', 'N'))
        radius = a * b / _sqrt(a*a+b*b)
        speed = field['C'] * (rate+field['beta']) / lapse0
        lapse = lapse0 * _sqrt(1-speed*speed)
        wt_jet = radius**3/lapse
        wt = wt_jet.value
        scale = 2*wt/VOLUME
        hd = slice(268*arm+264, 268*arm+268)
        hh = slice(268*arm+260, 268*arm+264)
        # Reconstruct O_t from the ORIGINAL full five-component wall map.
        # The parent/reference mechanical source enters spatial components
        # only, per holomorphic_two_arm_action; it cannot be put into A_tau.
        wall_coeff = np.einsum('fcj,j->fc',wall_map,raw[arm,100:180])
        connection = np.einsum('c,cij->ij',wall_coeff[0],generators)
        saved_connection = hessian[hd, hh]/scale
        dh = raw[arm, 264:]+connection@raw[arm, 260:264]
        direct = scale*dh
        direct_momenta.append(direct)
        direct_connections.append(connection)
        saved_connections.append(saved_connection)
        wall_coefficients.append(wall_coeff)
        weights.append([wt, lapse.value, radius.value])
        arm_jets, arm_saved_jets = [], []
        for direction in directions:
            d = direction[arm]
            wall_direction = np.einsum('fcj,j->fc',wall_map,d[100:180])
            dconnection = np.einsum('c,cij->ij',wall_direction[0],generators)
            dwt = wt_jet.gradient@d[:100]
            ddh = d[264:]+dconnection@raw[arm,260:264]+connection@d[260:264]
            arm_jets.append((2/VOLUME)*(dwt*dh+wt*ddh))
            arm_saved_jets.append((hessian@direction.ravel()).reshape(2,268)[arm,264:])
        direct_jets.append(arm_jets)
        saved_jets.append(arm_saved_jets)
        records.append(dict(
            arm=('parent', 'child')[arm],
            scalar_H_norm=float(np.linalg.norm(raw[arm, 260:264])),
            ordinary_Hdot_norm=float(np.linalg.norm(raw[arm, 264:])),
            covariant_Hdot_norm=float(np.linalg.norm(dh)),
            temporal_connection_real4_generator_norm=float(np.linalg.norm(connection)),
            direct_vs_saved_temporal_connection_max_absolute_error=float(np.max(abs(connection-saved_connection))),
            coordinate_cotangent_norm=float(np.linalg.norm(direct)),
            momentum_identity_max_absolute_error=float(np.max(abs(direct-gradient[arm,264:]))),
            Legendre_Hdot_block_max_absolute_error=float(np.max(abs(hessian[hd,hd]-scale*np.eye(4)))),
            independent_conormal_first_jet_max_absolute_error=float(np.max(abs(np.asarray(arm_jets)-arm_saved_jets))),
            independent_conormal_first_jet_relative_error=float(np.linalg.norm(np.asarray(arm_jets)-arm_saved_jets)/max(np.linalg.norm(arm_saved_jets),1e-300)),
            metric_radius_and_lapse_complex=True,
        ))
    arrays.update(
        direct_coordinate_Hdot_cotangent=np.asarray(direct_momenta),
        saved_coordinate_Hdot_cotangent=gradient[:, 264:],
        direct_raw_coefficient_temporal_connection_generators=np.asarray(direct_connections),
        saved_action_temporal_connection_generators=np.asarray(saved_connections),
        direct_wall_gauge_coefficients=np.asarray(wall_coefficients),
        direct_scalar_cotangent_directional_jets=np.asarray(direct_jets).transpose(1,0,2),
        wall_wT_lapse_radius=np.asarray(weights),
        saved_H_trace_difference=raw[1,260:264]-raw[0,260:264],
        saved_coordinate_cotangent_difference=gradient[1,264:]-gradient[0,264:],
        saved_scalar_cotangent_directional_jets=np.asarray(saved_jets).transpose(1,0,2),
        saved_H_trace_directional_jets=directions[:,1,260:264]-directions[:,0,260:264],
    )
    source_files = [
        'src/bhsm/interface/muon_holomorphic_normal_geometry.py',
        'src/bhsm/interface/muon_nonlinear_n0_field_action.py',
        'src/bhsm/interface/muon_intrinsic_higgs_gauge_action.py',
        'src/bhsm/interface/muon_holomorphic_two_arm_action.py',
        'src/bhsm/interface/muon_birth_attached_phase.py',
        'src/bhsm/interface/muon_birth_trace_enriched_action.py',
        'src/bhsm/interface/muon_intrinsic_scalar_birth_rows.py',
        'src/bhsm/interface/muon_intrinsic_worldvolume_scalar_transport.py',
        'src/bhsm/interface/covariant_bubble_interface_mechanics.py',
        'src/bhsm/interface/ae31_c2_gauge_composite_hs_action.py',
        'src/bhsm/interface/ae31_c2_lepton_composite_mixing_structure.py',
        'src/bhsm/interface/ae32_c2_einstein_cartan_lr_action.py',
        'theory/ae31_c2_intrinsic_m4_lepton_action.md',
        'theory/ae31_c2_full_scalar_derivative_pole.md',
    ]
    pins = {p: sha256((root/p).read_bytes()).hexdigest() for p in [rel,candidate_rel,basis_rel,basis_receipt_rel,comparison_receipt_rel,*source_files]}
    result = dict(
        classification='ACTUAL_RETAINED_INTRINSIC_SCALAR_DIRECT_CONORMAL_AND_COEFFICIENT_JET',
        producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        input_hashes=pins,
        records=records,
        saved_coordinate_H_trace_difference_max=float(np.max(abs(arrays['saved_H_trace_difference']))),
        saved_coordinate_Hdot_cotangent_difference_max=float(np.max(abs(arrays['saved_coordinate_cotangent_difference']))),
        retained_geometry_max_imaginary=float(np.max(abs(raw[:,:100].imag))),
        actual_worldvolume_flow_F_and_bundle_U=None,
        actual_transport_Jacobian_and_remainders=None,
        physical_F_U_energy_field_jets=None,
        why_physical_transport_not_instantiated='Retained complex analytic germ is not real timelike/anti-Hermitian worldvolume IVP data; no owned physical initial identification/time interval or coupled real history is supplied.',
        intrinsic_scalar_birth_law='H_child(F(x))=U_H(x)H_parent(x); p_parent-F^*(U_H^dagger p_child)=0 at fixed geometry with canonical density paired once.',
        geometric_momentum_dependence='Retain F,U and material Jacobian variations and the unrepresented angular image in scalar_birth_action_rows; no projection or zero At.',
        bare_gauge_HS_constitutive_law='K_HS^(-1) H_HS=O, K_HS=G_C2 diag(14/5,13/5,3/5) in up/down/charged-lepton order on admitted positive coexact mode.',
        bare_HS_jets='H_a=K_a O+K O_a; H_ab=K_ab O+K_a O_b+K_b O_a+K O_ab, with all nonlocal and domain dependence retained.',
        bare_HS_child_value_scope='Given admitted child kernel and fermion bilinear the on-shell auxiliary value is fixed. Event HS trace alone does not provide the child nonlocal bilinear/kernel.',
        intrinsic_Higgs_is_bare_HS=False,
        EC_global_endpoint_failure_bypassed=False,
        induced_HS_kinetic_scope='Universal derivative pole does not provide finite renormalized kinetic/mixing/domain data; no bare canonical partner manufactured.',
        temporal_connection_scope='Direct contraction of pinned original wall trace map, retained raw gauge coefficients and original real4 representation generators. Saved Hessian supplies comparison only; no connection/gradient/Hessian result enters direct value or first-jet construction.',
        directional_jets_scope='Four saved analytic coefficient directions; conormal jets freshly differentiated from original wall-geometry primitives and linear gauge map. These are not physical energy/magnetic/domain directions.',
        source_gauge_profile_scope='Mechanical source enters only spatial wall components, as in original full536 action; original A_tau and its coefficient derivatives remain nonzero.',
        empirical_scalar_quartic_or_mass_or_magnetic_value_consumed=False,
        same_coordinate_equalities_are_actual_F_U_matching=False,
        complex_to_real_projection_performed=False,
        saved_nonzero_H_and_temporal_connection_preserved=True,
        physical_outgoing_derivative_pass_2e10=False,
        physical_two_spin_normalization=None,
        physical_muon_magnetic_moment=None,
        coupled_matching_corrections_applied=0,
        original_Maxwell_all226_new_pass_claimed=False,
        completed_source_campaign_replayed=False,
    )
    out.mkdir(parents=True)
    _compressed_npz(out/'actual_scalar_conormal_contacts.npz', arrays)
    result['array_archive_sha256'] = sha256((out/'actual_scalar_conormal_contacts.npz').read_bytes()).hexdigest()
    (out/'result.json').write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(records=records, result_sha256=sha256((out/'result.json').read_bytes()).hexdigest()),sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    evaluate(args.repository,args.output)
