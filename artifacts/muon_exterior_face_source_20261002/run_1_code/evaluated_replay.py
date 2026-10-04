"""One small saved-input source calculation; never rerun an old producer."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf-8')


def run(manifest, output):
    refs = json.loads(manifest.read_text())
    root = HERE.parent if (HERE.parent/'src').is_dir() else Path(refs['repository'])
    sys.path.insert(0, str(root/'src'))
    if (HERE/'muon_exterior_face_source.py').exists():
        sys.path.insert(0, str(HERE))
        import muon_exterior_face_source as impl
    else:
        from bhsm.interface import muon_exterior_face_source as impl
    from bhsm.interface.aether_forward_boundary_radius import (
        boundary_log_radius, proper_time_log_radius_rate)
    if output.exists():
        raise FileExistsError('Use a new output directory; preserve all earlier caches.')
    paths = {}
    for key, row in refs['inputs'].items():
        p = root/row['repository_path']
        if sha(p) != row['sha256']:
            raise ValueError('Changed input: '+key)
        paths[key] = p
    output.mkdir(parents=True)
    save(output/'stage_receipt.json', dict(stage='input_identities_verified',
         scientific_reference=refs['scientific_reference'], inputs=refs['inputs']))
    def load(key):
        with np.load(paths[key], allow_pickle=False) as z:
            return {k: np.array(z[k]) for k in z.files}
    prefix, center, principal, parent, weighted, source, frames = [load(k) for k in
        ('prefix', 'center', 'principal', 'parent', 'weighted', 'source', 'frames')]
    cert = json.loads(paths['prefix_report'].read_text())
    frozen = json.loads(paths['frozen_local'].read_text())
    angular = impl.mechanical_angular_source(source['real_mode_coefficients'],
        weighted['jmath'], weighted['Q'], frames['frame__angular_curl_8'])
    coeff = impl.primitive_angular_coefficient(parent, principal, angular)
    y = prefix['endpoint_predictor_center']
    H = proper_time_log_radius_rate(12, y[:37], y[37:74], y[74:])
    x = boundary_log_radius(12, y[:37])
    H_interval = cert['domain']['D_tau_log_R4_interval']
    if not H_interval[0] <= H <= H_interval[1]:
        raise ValueError('Frontier rate outside saved certified interval')
    corner = impl.face_source_kinematics(x, H, principal['e'][0, -1], principal['shift'][0, -1])
    upstream = []
    for name in ('center_state', 'endpoint_predictor_center'):
        state = prefix[name]
        xp = boundary_log_radius(12, state[:37])
        hp = proper_time_log_radius_rate(12, state[:37], state[37:74], state[74:])
        row = impl.face_source_kinematics(xp, hp, principal['e'][0, -1], principal['shift'][0, -1])
        # Prefix geometry has not been recomputed: only its local M4 source
        # is evaluated here. Do not claim prefix parent traction from row.
        for key in ('temporal_radial_jet_coefficient', 'temporal_known_moving_frame_term'):
            row.pop(key)
        upstream.append(dict(state=name, **row))
    X = np.asarray([r['f_R']*source['Xi_complete'] for r in upstream])
    lam = float(coeff['mechanical_lambda'][0, -1])
    curvature = corner['T_b']*(angular['angular_plain']+lam*angular['angular_connection'])
    complement = corner['T_b']*lam*angular['angular_connection']
    # Fixed coefficients in normalized Wigner/Haar and ordinary Tr16.
    curvature_Gram = np.einsum('acmkij,bcmkij->ab', curvature.conj(), curvature)
    np.savez_compressed(output/'continued_source_and_angular_coefficients.npz',
        **angular, **coeff, upstream_local_Xi=X,
        frontier_curvature=curvature, frontier_charge_complement=complement,
        frontier_curvature_Gram=curvature_Gram,
        frontier_state=y, core_initial_state=center['centers'][0],
        upstream_center_state=prefix['center_state'])
    observed = float(np.linalg.norm((y-center['centers'][0])*prefix['state_weights']))
    # Green orientations are structural; only the known corner term is evaluated.
    e = float(principal['e'][0, -1])
    moving_interval = [-e*H_interval[1]/2, -e*H_interval[0]/2]
    checks = dict(frontier_weighted_center_difference=observed,
        frontier_saved_tube_radius=float(prefix['endpoint_tube_radius']),
        canonical_stop_descriptor=float(center['signed_descriptors'][-1]),
        frontier_logR_saved_profile_difference=x-float(frames['frame__log_radius'][0]),
        charge_complement_Q_trace_residual=float(np.linalg.norm(
            np.einsum('ij,acmkij->acmk', weighted['Q'].conj(), angular['angular_connection']))),
        QQ_cross_norm=float(np.linalg.norm(angular['QQ_cross'])),
        primitive_angular_Hermitian_residual=float(np.linalg.norm(
            coeff['QQ_covariant_angular_matrix']-
            coeff['QQ_covariant_angular_matrix'].conj().swapaxes(-1, -2))),
        upstream_local_source_norm=float(np.linalg.norm(X[0])),
        frontier_charge_complement_norm=float(np.linalg.norm(complement)))
    result = dict(checkpoint='BHSM_MUON_C2_FACE_SAME_SOURCE_ANGULAR_COMPLEMENT_20261002',
        classification='PRIMITIVE_SOURCE_AND_ANGULAR_QQ_COEFFICIENT; EXTERIOR_RESPONSE_NOT_EVALUATED',
        scientific_reference=refs['scientific_reference'], publication_start_HEAD=refs['publication_start_HEAD'],
        coordinate='b; beta=T_b b, A_Q=sqrt(2) beta; source=-i Q T_b Y',
        section='(u,v)=(w,1); omega=lambda*w^-1*dw; lambda=A^2/(A^2+B^2)',
        interval=dict(past='C2 certified step1222 frontier; artificial cut, not E0 or E1 reset',
            future='stored numerical representative of canonical first stop/domain exit',
            material='rho=pi/2; independent spatial boundary',
            proper_time_origin='zero reset at cached frontier',
            retained_duration=float(principal['proper_times'][-1])),
        orientations=impl.cut_orientations(), frontier_source=corner,
        upstream_local_sources=upstream, frontier_H_reused_certified_interval=H_interval,
        known_moving_frame_term_interval_at_fixed_saved_e=moving_interval,
        frozen_parent_H_at_frontier=float(principal['boundary_H'][0, 0]),
        H_reconstruction_scope=dict(parent='endpoint zeros are reconstruction placeholders',
            source_affine_H=float(frames['frame__H_affine_logR'][0]),
            errors_identified=False, old_arrays_modified=False),
        commutator_Tr16_Gram=angular['commutator_Gram'].real.tolist(),
        QQ_connection_Gram_eigenvalues=np.linalg.eigvalsh(angular['QQ_connection']).real.tolist(),
        frontier_lambda=lam,
        angular_QQ_equation='K_Q W nu C_rho/(r R4) * (curl*curl + lambda^2 C_Q); C_Q=<*[jmath(theta),YQ],*[jmath(theta),YQ]>/Tr16 Q^2',
        primitive_weak_form='q_core_QQ=q_principal - integral b^dagger QQ_angular_stiffness b; not full q_AE4',
        checks=checks, frozen_local=frozen,
        error_scope=dict(source_values='binary64 evaluation at retained proof centers',
            H_interval='reused step1222 certification; not a certification of the entire numerical stop history',
            moving_term='propagates certified H at fixed saved electric coefficient; not a full parent error enclosure',
            parent_H_error=None, affine_logR_error=None, geometry_tube_to_source_error=None,
            native_remainder=None, complement_evolution_tail=None, cut_composition_error=None),
        actual_execution=dict(continued_local_source_directions=8, primitive_angular_source_directions=8,
            exterior_source_response_directions=0, parent_weak_solves=0,
            native_E1_evaluations=0, shifted_resolvent_applications=0, physical_transfer_directions=0,
            old_frame_contact_normalization_covariance_calculations_repeated=False),
        first_unresolved_operand=dict(
            name='same-domain mixed charged-complement weak row on the retained prefix',
            equation='q_eff^R(v_perp,E_Q a)=0 with B5 E_Q a=T_b Y_A Q; primitive mixed row contains <d_omega v_perp,W d_omega a_Q> + <F_omega,W(v_perp wedge a_Q+a_Q wedge v_perp)>',
            input='eight supplied Q traces, retained prefix geometry, owned gauge/BRST zero-trace variations',
            output='forced T1/T2 and constraint/complement rows, including the same-owner induced remainder',
            producer='weighted_parent_operator plus inherited mechanical connection and AE4 source Hessian; current frequency assembler supplies only frozen scalar curl2 data',
            consumer='causal prefix stationary solve and its oriented temporal conormal return',
            status='uncomputed action/domain operator application, not an independently unselected photon forcing profile',
            complete_native_operator=False),
        exterior_affine_return=None, exterior_Calderon=None, cut_composition_evaluation=None,
        native_ledger={k:None for k in ('native_bulk_heat','state_variation','contact','domain_boundary','completion_counterterm','strong_within_native')},
        strong_is_native_subset=True, physical_a_mu=None, physical_g_mu=None)
    save(output/'result.json', result)
    save(output/'output_hashes.json', dict(files=[dict(path=p.name,sha256=sha(p)) for p in
        (output/'continued_source_and_angular_coefficients.npz', output/'result.json')]))
    save(output/'stage_receipt.json', dict(stage='new_source_and_primitive_angular_actions_saved',
        inputs=refs['inputs'], module_sha256=sha(Path(impl.__file__)), replay_sha256=sha(Path(__file__))))
    print(json.dumps(dict(output=str(output), checks=checks,
        first_unresolved_operand=result['first_unresolved_operand']['name'])))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    default = HERE/'input_refs.json'
    if not default.exists():
        default = HERE.parent/'artifacts/muon_exterior_face_source_20261002/input_refs.json'
    parser.add_argument('--inputs', type=Path, default=default)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.inputs, args.output)
