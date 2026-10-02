"""Reuse saved source/contact data; evaluate the independent weak-form frame."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import sys
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/'src'))
try:
    import muon_source_weak_extension as impl
except ModuleNotFoundError:
    from bhsm.interface import muon_source_weak_extension as impl


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_bytes((json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n').encode())


def load(path):
    with np.load(path, allow_pickle=False) as z:
        return {k: np.array(z[k]) for k in z.files}


def run(manifest, output, reuse=None, evaluated_module=None):
    if output.exists():
        raise FileExistsError('New output directory required; no checkpoint overwrite.')
    refs = json.loads(manifest.read_text())
    base = HERE.parent if (HERE.parent/'src').is_dir() else Path(refs['standalone_repository'])
    paths = {}
    identities = {}
    for key, row in refs['inputs'].items():
        path = base/row['repository_path']
        if sha(path) != row['sha256']:
            raise ValueError(f'Changed reused input: {key}')
        paths[key] = path
        identities[key] = row
    output.mkdir(parents=True)
    save(output/'stage_receipt.json', dict(stage='reused_inputs_hash_verified',
         module_sha256=sha(Path(impl.__file__)), input_identities=identities))
    d, old, source, parent, weighted = (load(paths[k]) for k in
        ('source_inputs', 'child_forms', 'source_actions', 'parent_fields', 'weighted_density'))
    if reuse:
        if evaluated_module is None:
            raise ValueError('Identity of previously evaluated numerical code required.')
        prefix=lambda p:p.read_text().split('\ndef weak_extension_contract():',1)[0]
        if prefix(evaluated_module)!=prefix(Path(impl.__file__)):
            raise ValueError('Numerical implementation changed; cache not reusable.')
        receipt=json.loads((reuse/'output_hashes.json').read_text())
        old_hashes={r['path']:r['sha256'] for r in receipt['files']}
        for name in ['independent_source_quotient.npz','inherited_parent_weak_coefficients.npz']:
            if sha(reuse/name)!=old_hashes[name]:raise ValueError('Changed evaluated output.')
            shutil.copyfile(reuse/name,output/name)
        all_f=load(output/'independent_source_quotient.npz')
        forms={k:all_f[k] for k in ['M','q_A','q_AB','q_AB_connected','q_A_segments']}
        f={k:v for k,v in all_f.items() if k not in forms}
        actions=f['source_actions_independent_nodes']
        principal=load(output/'inherited_parent_weak_coefficients.npz')
    else:
        f = impl.independent_source_frame(d)
        forms = impl.transport_cached_forms(f, old)
        actions = impl.transport_cached_source_actions(f, source, d)
        principal = impl.inherited_parent_principal_form(parent, weighted)
        np.savez_compressed(output/'independent_source_quotient.npz', **f, **forms,
                        source_actions_independent_nodes=actions,
                        source_output_labels=source['output_labels'],
                        retained_output_indices=source['retained_output_indices'])
        np.savez_compressed(output/'inherited_parent_weak_coefficients.npz', **principal)
    E = d['mixed__external_n0_test_frame_E0']
    W = d['mixed__Gamma_s_unit_source_fermion_boson_external'].reshape(20, 32)
    U, C, J = (f[k] for k in ('angular_frame', 'coefficient_map', 'right_inverse'))
    phi = np.concatenate((np.broadcast_to(E, (48, 20, 4)),
                          old['generated_profile_node_values']), axis=2)
    norm = lambda a: float(np.linalg.norm(a))
    checks = dict(angular_orthonormal_residual=norm(U.conj().T@U-np.eye(16)),
        independent_map_right_inverse_residual=norm(C@J-np.eye(16)),
        profile_reconstruction_residual=norm(f['independent_profile_nodes']@C-phi),
        generated_frame_reconstruction_residual=norm(U[:, 4:]@C[4:, 4:]-W),
        column_gram_reconstruction_residual=norm(C.conj().T@forms['M']@C-old['child_M_test_Gram']),
        old_gram_nullspace_residual=norm(old['child_M_test_Gram']@(np.eye(36)-J@C)),
        reduced_gram_smallest_eigenvalue=float(np.linalg.eigvalsh(forms['M']).min()),
        reduced_gram_condition=float(np.linalg.cond(forms['M'])),
        transported_form_reconstruction_residuals={name: norm(np.einsum('ki,...kl,lj->...ij', C.conj(), forms[name], C)-old[key])
            for name, key in [('q_A','child_q_A_integrated'), ('q_AB','child_q_AB_integrated'), ('q_AB_connected','child_q_AB_connected_complement')]})
    e, r = principal['e'], principal['r']
    interior = (e > 0) & (r > 0)
    S = principal['lorentz_principal_tau_rho_per_kappa1']
    det = S[..., 0, 0]*S[..., 1, 1]-S[..., 0, 1]*S[..., 1, 0]
    checks['principal_determinant_identity_relative_residual'] = float(np.max(np.abs((det+e*r)[interior]/(e*r)[interior])))
    result = dict(classification='EVALUATED_SAVED_SOURCE_QUOTIENT_AND_INHERITED_LORENTZ_PARENT_PRINCIPAL_BLOCK; NOT_NATIVE_EXTENSION_OR_PHYSICAL_MUON_ANOMALY',
        scientific_reference='524ed90689bd5923c249bba2e699abf627e703cd',
        publication_start_HEAD='dd6bfbdad755c280f952e20b9a258090ebdd00e5',
        coordinate='b; beta=T_b b and A_Q=sqrt(2) beta retained; no extra 2/3 in the vertex',
        original_columns=C.shape[1], independent_columns=C.shape[0], nullity=C.shape[1]-C.shape[0],
        function_frame='F(tau)=[E0,f_R(tau) U1]; Phi(tau)=F(tau) C with constant C',
        frame_rank_provenance='established n0 rank4 and generated positive-n1 rank12 representation; factorization residuals are numerical controls, not a fitted rank choice',
        arbitrary_diagonal_regularization=0,
        old_source_angular_contact_normalization_recomputed=False,
        evaluated_arrays_reused=bool(reuse),
        reuse_reason='Nullity metadata corrected to20 and first missing boundary equation clarified; numerical implementation and evaluated arrays unchanged.' if reuse else None,
        connected_n2_contact_transported=True,
        repeated_source_resolvent_heat_tail_bound=None,
        gram_eigenvalues=np.linalg.eigvalsh(forms['M']).real.tolist(),
        checks=checks,
        principal_block_equation='[[e,-e*zeta],[-e*zeta,e*zeta^2-r]]; det=-e*r',
        principal_block_scope='primitive local Lorentz Maxwell derivative block per kappa1 with inherited K_Q and full pointwise W; covariant angular/lower-order/native remainder not replaced by curl^2=9',
        lorentz_regular_grid_points=int(interior.sum()),
        lorentz_signature_on_regular_grid='one positive and one negative direction; determinant identity derived exactly, values sampled at fixed retained inputs',
        first_interior_sample=dict(history_node=0, rho_index=32,
            rho=float(parent['rho'][32]), principal_matrix=S[0, 32].tolist(),
            determinant=float(det[0, 32])),
        flux_equations=['Pi_tau=e*(b_tau-zeta*b_rho-H*b/2)',
                       'Pi_rho=-zeta*Pi_tau-r*b_rho'],
        positive_pairing_sign_flip_performed=False,
        core_time_faces_are_physical_boundaries=False,
        parent_extensions_evaluated=0, native_E1_evaluations=0,
        native_shifted_resolvent_applications=0, physical_transfer_directions=0,
        parent_trace_reset_Clifford_flux_residuals=None,
        physical_a_mu=None, physical_g_mu=None,
        frozen_local_values_changed=False, native_added_to_selected_local=False,
        error_scope='exact retained representation identities and analytic determinant/flux algebra; binary64 contraction residuals at fixed cached inputs. No outward full-form, history, interpolation, quadrature, native matching, domain, or theory uncertainty bound.',
        module_sha256=sha(Path(impl.__file__)), input_identities=identities)
    save(output/'result.json', result)
    save(output/'missing_operand.json', impl.weak_extension_contract())
    save(output/'checkpoint.json', dict(checkpoint_id='BHSM_MUON_FIXED_TRACE_WEAK_BLOCK_QUOTIENT_20261002',
        result=result, one_next_operand=impl.weak_extension_contract(),
        native_ledger={k:None for k in ['native_bulk_heat','state_variation','contact','domain_boundary','completion_counterterm','strong_within_native']},
        frozen_local=json.loads(paths['frozen_local'].read_text())))
    files=[dict(path=p.name, sha256=sha(p)) for p in sorted(output.iterdir())]
    save(output/'output_hashes.json',dict(files=files))
    print(json.dumps(dict(output=str(output), checks=checks, independent_columns=16,
                         parent_extensions_evaluated=0), indent=2))


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    default=HERE/'input_refs.json'
    if not default.exists():
        default=HERE.parent/'artifacts/muon_source_weak_extension_20261002/input_refs.json'
    parser.add_argument('--inputs', type=Path, default=default)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--reuse',type=Path)
    parser.add_argument('--evaluated-module',type=Path)
    args=parser.parse_args()
    run(args.inputs, args.output, args.reuse, args.evaluated_module)
