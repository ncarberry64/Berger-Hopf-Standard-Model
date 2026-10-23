"""One cached propagated-field diagnostic; no parent or witness rebuild."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import sys
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
import numpy as np
from flint import arb


def read(p):
    with np.load(p, allow_pickle=False) as z:
        return {k: np.array(z[k]) for k in z.files}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p, data):
    p.write_bytes((json.dumps(data, indent=2, sort_keys=True, allow_nan=False)+'\n').encode())


def inputs(root):
    a = root/'artifacts'
    tail = a/'muon_retained_tail_core_20261005'
    witness = a/'muon_seam_offmode_identifiability_20261005/run_4'
    return dict(accepted=tail/'coupled_run_3/source_centered_core_solution.npz',
        accepted_decimal=tail/'coupled_run_3/high_precision_solution.json',
        accepted_receipt=tail/'coupled_run_3/result.json', accepted_inputs=tail/'coupled_run_3/input_hashes.json',
        tail=tail/'run_1/tail_response.npz', attachment=tail/'run_1/partial_system_with_tail_core.npz',
        tail_inputs=tail/'run_1/input_hashes.json',
        node3=tail/'run_1/points/node_03.npz', node3_receipt=tail/'run_1/points/node_03.json',
        witness=witness/'offmode_source_witness.npz', witness_result=witness/'result.json', witness_inputs=witness/'input_hashes.json',
        wall=a/'muon_wall_input_attachment_20261005/run_1/node3_projected_intrinsic_kinetic.npz',
        cut=a/'muon_coupled_cut_forms_20261004/run_1/coupled_cut_source_actions.npz',
        contact=a/'muon_parent_source_contact_20261003/replay_reference/parent_source_contact.npz',
        corrected=a/'muon_parent_source_rate_20261003/replay_reference/parent_source_rate_corrected.npz',
        tail_producer=root/'src/bhsm/interface/muon_retained_tail_core.py',
        tail_script=root/'scripts/replay_muon_retained_tail_core.py',
        solve_producer=root/'scripts/solve_muon_tail_source_centered_core.py',
        module=root/'src/bhsm/interface/muon_propagated_seam_visibility.py', script=Path(__file__).resolve())


def calculate(root):
    sys.path.insert(0, str(root/'src'))
    from bhsm.interface.muon_propagated_seam_visibility import (
        reconstruct_node3, existing_witness_actions, chirality_diagnostic, matrix, center, norm, upper, interval)
    refs = inputs(root)
    d = {k: read(refs[k]) for k in ('accepted', 'tail', 'attachment', 'node3', 'witness', 'wall', 'cut', 'contact', 'corrected')}
    wi = json.loads(refs['witness_inputs'].read_text())
    si = json.loads(refs['accepted_inputs'].read_text())
    ti = json.loads(refs['tail_inputs'].read_text())
    for key in ('tail', 'attachment'):
        if si[key]['sha256'] != sha(refs[key]):
            raise ValueError('accepted source solution belongs to a different tail/attachment')
    for key in ('point', 'cut', 'wall'):
        current = {'point':'node3', 'cut':'cut', 'wall':'wall'}[key]
        if wi[key]['sha256'] != sha(refs[current]):
            raise ValueError('witness and response frame/scalar inputs differ')
    for key in ('cut', 'contact', 'corrected'):
        if ti[key]['sha256'] != sha(refs[key]):
            raise ValueError('tail source-column frame differs')
    # Reconstruct the FIXED column coordinates from cached raw source arrays.
    # No photon action, independent frame eigensolve or normalization replay.
    frame_residual = 0.
    for n in (1, 3):
        raw = d['contact'][f'Xi_A_unit_n{n}'][:, :, d['corrected']['source_image_probe_columns']]
        raw = raw.transpose(1, 3, 4, 0, 2).reshape(64, n+1, n+1, 32)
        basis = np.einsum('omki,ij->omkj', raw, d['cut']['independent_source_map'])
        saved = d['wall'][f'normalized_wall_W_input_n{n}']
        frame_residual = max(frame_residual, float(np.max(np.abs(basis-saved))))
        shaped = basis.reshape(4, 16, n+1, n+1, 12)
        left = shaped[:, 6:8].copy(); left[2:] = 0
        frame_residual = max(frame_residual, float(np.max(np.abs(left-d['witness'][f'left_n{n}']))))
    if frame_residual > 3e-15:
        raise ValueError('present witness uses a different source/chiral frame')
    if not np.array_equal(d['cut']['source_coordinates'], d['witness']['source_coordinates']):
        raise ValueError('different prescribed source coordinate')
    if not np.array_equal(d['node3']['actual_state'], d['witness']['actual_state']):
        raise ValueError('different node3 background')
    decimal = json.loads(refs['accepted_decimal'].read_text())
    reconstruction = reconstruct_node3(decimal, d['attachment'], d['accepted'], d['tail'])
    actions = existing_witness_actions(d['witness'], reconstruction)
    chiral = chirality_diagnostic(d['cut'], d['wall'], d['tail'], d['node3'], d['accepted'])
    P = chiral['coefficient_left_projector']
    Xi = d['wall']['Xi_full']
    # Full n1+n3 spin/carrier intertwinement, preserving the saved level order.
    mapped = []
    for n in (1, 3):
        x = d['wall'][f'normalized_wall_W_input_n{n}'].reshape(4, 16, n+1, n+1, 12).copy()
        x[2:] = 0
        mapped.append(x.reshape(-1, 12))
    chiral['actual_array_intertwining_residual'] = float(np.linalg.norm(np.concatenate(mapped)-Xi@P))
    a3, c3 = center(reconstruction['a3']), center(reconstruction['c3'])
    x3 = center(reconstruction['node3'])
    mu4 = float(d['wall']['M4'])
    numeric = dict(
        frame_coordinate_residual=frame_residual,
        node2_distance_from_earlier_tail_entrance=float(np.linalg.norm(center(reconstruction['node2'])-d['tail']['original_source_trace'])),
        node3_distance_from_earlier_tail_solution=float(np.linalg.norm(x3-d['tail']['solution'][1])),
        node3_a_norm=float(np.linalg.norm(a3)), node3_c_norm=float(np.linalg.norm(c3)),
        left_output_norm=interval(actions['left_norm']), unit_higgs_output_norm=interval(actions['higgs_norm']),
        M4_weighted_left_norm=interval(actions['left_norm']*arb(mu4).sqrt()),
        M4_weighted_unit_higgs_norm=interval(actions['higgs_norm']*arb(mu4).sqrt()),
        field_volume_norm=float(np.sqrt(np.real(x3.conj()@d['node3']['M']@x3))),
        field_temporal_Cauchy_norm=float(np.sqrt(np.real(x3.conj()@d['node3']['Ms']@x3))),
        node2_export_error_upper=reconstruction['node2_export_error_upper'],
        node3_binary_reconstruction_error_upper=reconstruction['node3_binary_reconstruction_error_upper'],
        local_reduced_residual_norm_upper=reconstruction['local_reduced_residual_norm_upper'],
        local_pivot_correction_norm_upper=reconstruction['local_pivot_correction_norm_upper'],
        scalar_eta_left_error_upper=actions['scalar_eta_left_error_upper'],
        scalar_eta_higgs_error_upper=actions['scalar_eta_higgs_error_upper'],
        binary_visibility_left_error_upper=actions['binary_visibility_left_error_upper'],
        binary_visibility_higgs_error_upper=actions['binary_visibility_higgs_error_upper'],
        local_pivot_left_error_upper=actions['local_pivot_left_error_upper'],
        local_pivot_higgs_error_upper=actions['local_pivot_higgs_error_upper'])
    return refs, d, reconstruction, actions, chiral, numeric


def run(root, out, computed=None):
    if out.exists():
        raise FileExistsError('new output directory required')
    out.mkdir(parents=True)
    refs, d, r, actions, chiral, numeric = computed or calculate(root)
    from bhsm.interface.muon_propagated_seam_visibility import center
    arrays = dict(node2_trace=center(r['node2']), node3_W_coefficients=center(r['a3']),
        node3_p_coefficients=center(r['c3']), node3_coefficients=center(r['node3']),
        affine_y0=d['tail']['backsubstitution_y'][0], Y0=d['tail']['backsubstitution_Y'][0],
        node3_binary_reconstruction=r['rounded_node3'], local_pivot_error_correction=center(r['local_pivot_correction']),
        coefficient_left_projector=chiral['coefficient_left_projector'],
        original_source_coordinates=d['cut']['source_coordinates'], frozen_eta_interval=d['witness']['eta_interval'],
        actual_node3_state=d['node3']['actual_state'])
    balls = {}
    for key in ('left', 'higgs'):
        for n, x in actions[key].items():
            template = d['witness'][f'{"left" if key=="left" else "forward_h"}_n{n}']
            arrays[f'{key}_output_n{n}'] = center(x).reshape(template.shape[:-1])
            balls[f'{key}_output_n{n}'] = [str(x[i, 0]) for i in range(x.nrows())]
    for key in ('node2', 'node3', 'a3', 'c3', 'local_pivot_correction'):
        balls[key] = [str(r[key][i, 0]) for i in range(r[key].nrows())]
    np.savez_compressed(out/'propagated_visibility.npz', **arrays)
    save(out/'arithmetic_balls.json', balls)
    chiral_receipt = {k:v for k,v in chiral.items() if k != 'coefficient_left_projector'}
    save(out/'chirality_diagnostic.json', chiral_receipt)
    result = dict(classification='existing-witness visibility on accepted source-centered parent-bulk numerical response; NOT a native coupling or Pauli sensitivity',
        continuation='fc612beac32e886ad8d5dde5d33cf4021d082561', node2=2, node3=3, node3_action_arc=6,
        formula='x3=-Y0*x2+y0; x3=(a3,c3); K_L u3=eta Pi_L Xi c3; d3=eta H1dag Pi_L Xi c3',
        SAME_nonzero_affine_source_retained=True, W_contribution_canceled_before_application=True,
        eta_refined=False, witness_changed=False, new_history_points=0, new_field_actions=0,
        new_parent_solve=False, error_diagnostic_local_pivot_solve_only=True,
        native_operator_updated=False, wall_Gram_added=False, lambda_value=None,
        Y_and_physical_Higgs_amplitude='symbolic', reverse_role='preserved distributed bulk Euler witness, not a boundary normal term',
        numeric=numeric,
        error_scope=dict(arithmetic='validated products of frozen binary arrays and accepted decimal exports, with decimal quantization balls; no bound on underlying accepted-solver error inferred',
            scalar='reuse exact frozen-nodal eta enclosure; no refinement',
            local_pivot='bounds difference from exact FIRST cached reduced equation with later saved elimination/affine maps held fixed; not full tail error',
            tail_coefficient_and_reduction_error=None, history_and_interpolation_error=None, continuum_error=None,
            physical_uncertainty=None),
        action_level_target='J_chi,j=D_Psi5 F_b[chi_j] and same-photon derivative, with action-owned trace/volume and reverse role',
        physical_a_mu=None, physical_g_mu=None, native_uncertainty=None)
    save(out/'result.json', result)
    save(out/'input_hashes.json', {k:dict(path=str(p), sha256=sha(p)) for k,p in refs.items()})
    git = lambda *a: subprocess.check_output(['git','-C',str(root),*a],text=True).strip()
    save(out/'workspace.json', dict(head=git('rev-parse','HEAD'), branch=git('branch','--show-current'),
        scientific_reference='524ed90689bd5923c249bba2e699abf627e703cd', status=git('status','--short')))
    save(out/'output_hashes.json', {p.name:sha(p) for p in out.iterdir() if p.is_file()})
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--duplicate-output',type=Path)
    args = p.parse_args()
    root = args.repository.resolve()
    computed = calculate(root)
    run(root,args.output.resolve(),computed)
    if args.duplicate_output:
        run(root,args.duplicate_output.resolve(),computed)
