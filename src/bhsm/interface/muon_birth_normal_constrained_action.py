"""Joint constraint-admissible kinetic application of the material trace graph.

This consumes the evaluated two-arm action, including its nonlinear profile
contacts.  The two inherited attachment coordinates on each arm and the two
proper wall-amplitude velocities are prescribed trial coordinates.  Every
multiplier and Gauss derivative is annihilated through the same saddle.
No inverse of the velocity form, positive-minimum assumption, spectral
deletion, or physical formation-mode identification is used.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import numpy as np

from .muon_birth_full_field_attachment import inherited_full_field_boundary
from .muon_birth_trace_enriched_action import generic_coordinate_lift


TRIAL_ORDER = ('incoming attachment0', 'incoming attachment1',
               'child attachment0', 'child attachment1',
               'incoming proper material-normal velocity',
               'child proper material-normal velocity')


def constrained_velocity_trial(velocity_form, constraint_velocity, trial_trace,
                               *, velocity_cotangent=None):
    """Solve literal kinetic stationarity with all constraint reactions.

    For A, C and B, K=(A,G^T;G,0), G=(B;C), and K X=(0;I_B;0).
    The represented kinetic response is ell^T A ell.  It can be indefinite;
    the function makes no minimization or physical inertia claim.
    """
    A, C, B = (np.asarray(x, float) for x in
               (velocity_form, constraint_velocity, trial_trace))
    if A.ndim != 2 or A.shape[0] != A.shape[1] or C.ndim != 2 or B.ndim != 2:
        raise ValueError('same finite velocity form, constraints and trial traces required')
    n = len(A); k = len(B)
    if C.shape[1] != n or B.shape[1] != n or not all(np.isfinite(x).all() for x in (A, C, B)):
        raise ValueError('finite shared velocity coordinates required')
    G = np.vstack((B, C))
    K = np.block([[A, G.T], [G, np.zeros((len(G), len(G)))]])
    rows = np.max(abs(K), axis=1)
    if np.any(rows == 0):
        raise np.linalg.LinAlgError('literal saddle has an unbound row; no conditioning shift applied')
    scale = 1/np.sqrt(rows)
    balanced = scale[:, None]*K*scale[None, :]
    rhs = np.zeros((len(K), k)); rhs[n:n+k] = np.eye(k)
    solution = scale[:, None]*np.linalg.solve(balanced, scale[:, None]*rhs)
    ell = solution[:n]; response = ell.T@A@ell
    p = None if velocity_cotangent is None else np.asarray(velocity_cotangent, float)
    if p is not None and (p.shape != (n,) or not np.isfinite(p).all()):
        raise ValueError('same finite velocity cotangent required')
    return dict(velocity_form=A, constraint_velocity=C, trial_trace=B, saddle=K,
        right_hand_side=rhs, solution=solution, velocity_lift=ell,
        trial_reactions=solution[n:n+k], constraint_reactions=solution[n+k:],
        kinetic_response=response, kinetic_reaction_identity=response+solution[n:n+k],
        trial_momentum=None if p is None else ell.T@p,
        solve_residual=K@solution-rhs, trial_lift_residual=B@ell-np.eye(k),
        constraint_annihilation=C@ell, balanced_condition_number=float(np.linalg.cond(balanced)),
        row_scale=scale, regularizing_shift=0., spectral_directions_removed=0,
        stationarity_not_positive_minimization=True)


def joint_normal_kinetic_application(raw_pair, raw_gradient, raw_hessian, labels,
                                    *, surface_gradient_per_gamma=None,
                                    surface_hessian_per_gamma=None):
    """Apply the joint action to attachment and proper-normal trial velocities.

    Input order is incoming then child.  Both x/v/y charts are lifted from
    the same complete field vector.  Prescribing one normal velocity and
    zero other trial traces defines a conditional application; it does not
    choose a mechanical mode, event projector or temporal endpoint domain.
    """
    raw = np.asarray(raw_pair, float); g = np.asarray(raw_gradient, float)
    h = np.asarray(raw_hessian, float); coordinates = generic_coordinate_lift(labels)
    P = coordinates['lift']; nr, nm = P.shape; n = coordinates['x_count']; m = coordinates['y_count']
    if raw.shape != (2, nr) or g.shape != (2*nr,) or h.shape != (2*nr, 2*nr):
        raise ValueError('complete shared two-arm raw action jet required')
    R = np.zeros((2*nr, 2*nm)); R[:nr, :nm] = P; R[nr:, nm:] = P
    master_g = R.T@g; master_h = R.T@h@R
    vi = np.r_[np.arange(n, 2*n), nm+np.arange(n, 2*n)]
    yi = np.r_[np.arange(2*n, nm), nm+np.arange(2*n, nm)]
    A = master_h[np.ix_(vi, vi)]; C = master_h[np.ix_(yi, vi)]
    B = np.zeros((6, 2*n))
    for arm in range(2):
        B[2*arm:2*arm+2, arm*n:(arm+1)*n] = inherited_full_field_boundary(raw[arm, :37], n, nm)[0]
        B[4+arm, arm*n+37] = 1.
    result = constrained_velocity_trial(A, C, B, velocity_cotangent=master_g[vi])
    common = np.zeros(6); common[4:] = 1.
    result.update(master_lift=R, master_gradient=master_g, master_hessian=master_h,
        velocity_indices=vi, algebraic_indices=yi,
        dynamic_count_per_arm=n, algebraic_count_per_arm=m,
        algebraic_constraint_values=master_g[yi],
        algebraic_values_by_arm=master_g[yi].reshape(2, m),
        raw_velocity_lift=R[:, vi]@result['velocity_lift'],
        common_normal_trial=common,
        common_normal_kinetic=float(common@result['kinetic_response']@common),
        common_normal_momentum=float(common@result['trial_momentum']),
        common_normal_velocity_lift=result['velocity_lift']@common,
        normal_kinetic_block=result['kinetic_response'][4:, 4:],
        normal_trial_momentum=result['trial_momentum'][4:], trial_order=TRIAL_ORDER,
        trial_scope='joint instantaneous two-arm Lagrangian kinetic stationarity; four attachment traces held fixed for the common wall-normal trial',
        normal_scope='conditional lateral proper wall-amplitude velocity; coordinate-time rate; no selected mechanical mode or unit-inertia normalization',
        full_temporal_junction_or_formation_operator=False,
        all_multiplier_and_Gauss_reactions_retained=True)
    if (surface_gradient_per_gamma is None) != (surface_hessian_per_gamma is None):
        raise ValueError('both area jets required together')
    if surface_hessian_per_gamma is not None:
        sg = np.asarray(surface_gradient_per_gamma, float); sh = np.asarray(surface_hessian_per_gamma, float)
        if sg.shape != g.shape or sh.shape != h.shape:
            raise ValueError('same raw area jet required')
        mg = R.T@sg; mh = R.T@sh@R
        a = mh[np.ix_(vi, vi)]; c = mh[np.ix_(yi, vi)]
        G = np.vstack((np.zeros_like(B), c))
        result.update(surface_master_gradient_per_gamma=mg,
            surface_master_hessian_per_gamma=mh,
            surface_saddle_coefficient_per_gamma=np.block([[a, G.T], [G, np.zeros((len(G), len(G)))]]),
            area_family_equation='K(gamma)=K_assigned+gamma*K_area, solve the same RHS; gamma is not assigned to zero physically')
    return result


def materialize_normal_constrained_action(normal_application, output, *, repository=None):
    """Consume pinned evaluated graph values, never a supplied surrogate matrix."""
    from .muon_parent_gauge_geometry_correction import ROOT
    from .muon_birth_attached_phase import load_attached_endpoint
    from .muon_birth_phase_continuation import _compressed_npz
    root = ROOT if repository is None else Path(repository)
    source = Path(normal_application); source = source if source.is_absolute() else root/source
    out = Path(output)
    if out.exists():
        raise FileExistsError('preserve earlier applications')
    receipt_bytes = (source/'result.json').read_bytes(); receipt = json.loads(receipt_bytes)
    expected = 'EVALUATED_EXACT_REACHED_MATERIAL_NORMAL_TRACE_GRAPH_ACTION_APPLICATION'
    if receipt['scope'] != expected or receipt['graph_profile_projected']:
        raise ValueError('consume the actual unprojected trace graph action')
    for path, digest in receipt['input_hashes'].items():
        if sha256((root/path).read_bytes()).hexdigest() != digest:
            raise ValueError('consumed action changed: '+path)
    data = (source/'application.npz').read_bytes()
    if sha256(data).hexdigest() != receipt['numerical_sha256']:
        raise ValueError('evaluated graph numerical values changed')
    with np.load(source/'application.npz', allow_pickle=False) as saved:
        arrays = {name: saved[name] for name in saved.files}
    initial = load_attached_endpoint(receipt['initial_application'], side='incoming', repository=root)
    result = joint_normal_kinetic_application(arrays['raw_pair'], arrays['raw_gradient'], arrays['raw_hessian'],
        initial['representation']['gauge_labels'], surface_gradient_per_gamma=arrays['surface_gradient_per_gamma'],
        surface_hessian_per_gamma=arrays['surface_hessian_per_gamma'])
    out.mkdir(parents=True)
    output_arrays = {name: value for name, value in result.items() if isinstance(value, np.ndarray)}
    output_arrays.update(raw_pair=arrays['raw_pair'], raw_gradient=arrays['raw_gradient'], raw_hessian=arrays['raw_hessian'])
    _compressed_npz(out/'application.npz', output_arrays)
    hashes = dict(receipt['input_hashes'])
    path = 'src/bhsm/interface/muon_birth_normal_constrained_action.py'
    hashes[path] = sha256((root/path).read_bytes()).hexdigest()
    md = dict(scope='EVALUATED_JOINT_CONSTRAINT_ADMISSIBLE_MATERIAL_NORMAL_KINETIC_APPLICATION',
        consumed_graph_path=source.relative_to(root).as_posix(),
        consumed_graph_receipt_sha256=sha256(receipt_bytes).hexdigest(), consumed_graph_numerical_sha256=receipt['numerical_sha256'],
        input_hashes=hashes, numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        action_parameters=receipt['action_parameters'],
        graph_points=receipt['quadrature_refinements'][0]['points'],
        dynamic_count_per_arm=result['dynamic_count_per_arm'], algebraic_count_per_arm=result['algebraic_count_per_arm'],
        saddle_shape=list(result['saddle'].shape), balanced_condition_number=result['balanced_condition_number'],
        max_solve_residual=float(np.max(abs(result['solve_residual']))),
        max_trial_lift_residual=float(np.max(abs(result['trial_lift_residual']))),
        max_constraint_annihilation=float(np.max(abs(result['constraint_annihilation']))),
        max_kinetic_reaction_identity_defect=float(np.max(abs(result['kinetic_reaction_identity']))),
        velocity_lift_norms=np.linalg.norm(result['velocity_lift'], axis=0).tolist(),
        normal_kinetic_block=result['normal_kinetic_block'].tolist(), normal_trial_momentum=result['normal_trial_momentum'].tolist(),
        common_normal_kinetic=result['common_normal_kinetic'], common_normal_momentum=result['common_normal_momentum'],
        algebraic_constraint_norms_by_arm=np.linalg.norm(result['algebraic_values_by_arm'], axis=1).tolist(),
        trial_order=TRIAL_ORDER, trial_scope=result['trial_scope'], normal_scope=result['normal_scope'],
        area_family_equation=result['area_family_equation'],
        no_inverse_velocity_form_or_positive_minimum_assumed=True,
        all_multiplier_and_Gauss_reactions_retained=True, regularizing_shift=0., spectral_directions_removed=0,
        inherited_four_attachment_covectors_retained=True, normal_frame_not_selected_mechanically=True,
        temporal_junction_action_assembled=False, physical_formation_Hessian_evaluated=False,
        physical_unit_inertia_mode_normalization=False, physical_native_heat_closed=False, physical_Pauli_value=False,
        error_scope='binary64 direct balanced saddle solve on saved finite analytic action jet; no producer-rounding or continuum certificate')
    (out/'result.json').write_text(json.dumps(md, indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf8', newline='\n')
    return md


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--normal-application', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(materialize_normal_constrained_action(args.normal_application, args.output), sort_keys=True))
