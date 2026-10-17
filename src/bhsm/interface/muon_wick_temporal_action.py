"""Continue the executed full488 magnetic action and its canonical/Gauss rows.

This acts on the actual corrected-profile Lorentz coefficient/source forms.
It preserves their inherited temporal faces and source-rate image, without
identifying a real-time response with a two-face Dirichlet heat inverse.
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import solve


def _forms(forms):
    values = tuple(np.asarray(a, complex) for a in forms)
    if len(values) != 3 or values[0].ndim != 2 or values[0].shape[0] != values[0].shape[1]:
        raise ValueError('same square M,B,K action forms required')
    if any(a.shape != values[0].shape or not np.isfinite(a).all() for a in values):
        raise ValueError('finite complete action forms required')
    return values


def wick_temporal_forms(forms, gauss_count):
    """L_E(x_E,v_E)=-L_L(R^-1 x_E,i R^-1 v_E).

    R rotates the temporal connection coordinates by -i and leaves spatial
    connections, Higgs and magnetic source amplitudes unchanged.  Source
    amplitudes' TIME derivatives rotate along with all other velocities.
    These are analytic transpose bilinears, not Hermitian conjugations.
    """
    M, B, K = _forms(forms); n = len(M)
    if type(gauss_count) is not int or not 0 < gauss_count < n:
        raise ValueError('explicit full temporal-connection block required')
    rotation = np.ones(n, complex); rotation[:gauss_count] = -1j
    inverse = 1/rotation; outer = inverse[:, None]*inverse[None, :]
    return dict(forms=(outer*M, -1j*outer*B, -outer*K),
        coordinate_rotation=rotation, velocity_rotation=-1j*rotation,
        canonical_dual_rotation=-1j*inverse,
        equation='M_E=R^-T M_L R^-1; B_E=-i R^-T B_L R^-1; K_E=-R^-T K_L R^-1',
        source_rate_rotation_count=1, real_positive_native_operator_identified=False)


def quadratic_action_rows(forms, values, velocities):
    """Literal action, value cotangent and temporal canonical dual applications."""
    M, B, K = _forms(forms); x, v = (np.asarray(a, complex) for a in (values, velocities))
    if x.shape != v.shape or x.ndim != 2 or x.shape[0] != len(M) or not np.isfinite([x, v]).all():
        raise ValueError('same complete coefficient/source columns required')
    momentum = M@v+B.T@x; value_row = K@x+B@v
    return dict(momentum=momentum, value_row=value_row,
        action_pairing=.5*(v.T@M@v+x.T@B@v+v.T@B.T@x+x.T@K@x))


def analytic_gauss_reduction(forms, gauss_count):
    """Solve the continued original algebraic row, with all source columns.

    A general complex solve is required: no real projection, Cholesky,
    eigenvalue deletion or sign repair is used on the continued form.
    """
    M, B, K = _forms(forms); a = gauss_count
    if type(a) is not int or not 0 < a < len(M):
        raise ValueError('explicit Gauss block required')
    scale = max(1., np.max(abs(M)), np.max(abs(B)))
    if max(np.max(abs(M[:a])), np.max(abs(M[:, :a])), np.max(abs(B[:, :a]))) > 1e-12*scale:
        raise ValueError('temporal connection has an unaccounted canonical momentum')
    Y = solve(K[:a, :a], K[:a, a:], assume_a='gen')
    Z = solve(K[:a, :a], B[:a, a:], assume_a='gen')
    return dict(M=M[a:, a:]-B[:a, a:].T@Z,
        B=B[a:, a:]-K[:a, a:].T@Z, K=K[a:, a:]-K[:a, a:].T@Y,
        At_value_map=-Y, At_velocity_map=-Z,
        original_Gauss_matrix=K[:a, :a], original_Gauss_value_row=K[:a, a:],
        original_Gauss_velocity_row=B[:a, a:])


def compare_temporal_action_continuation(forms, values, velocities, gauss_count):
    """Apply actual field/source columns before and after original-row reduction."""
    move = wick_temporal_forms(forms, gauss_count); R = move['coordinate_rotation']
    x, v = (np.asarray(a) for a in (values, velocities))
    l = quadratic_action_rows(forms, x, v)
    e = quadratic_action_rows(move['forms'], R[:, None]*x, -1j*R[:, None]*v)
    gl = analytic_gauss_reduction(forms, gauss_count)
    ge = analytic_gauss_reduction(move['forms'], gauss_count)
    a = gauss_count; residuals = dict(
        action=float(np.max(abs(l['action_pairing']+e['action_pairing']))),
        value_row=float(np.max(abs(e['value_row']+l['value_row']/R[:, None]))),
        canonical_dual=float(np.max(abs(e['momentum']+1j*l['momentum']/R[:, None]))),
        reduced_M=float(np.max(abs(ge['M']-gl['M']))),
        reduced_B=float(np.max(abs(ge['B']+1j*gl['B']))),
        reduced_K=float(np.max(abs(ge['K']+gl['K']))),
        At_value_map=float(np.max(abs(ge['At_value_map']+1j*gl['At_value_map']))),
        At_velocity_map=float(np.max(abs(ge['At_velocity_map']-gl['At_velocity_map']))))
    return dict(**move, lorentz_rows=l, euclidean_rows=e, lorentz_reduced=gl,
        euclidean_reduced=ge, continuation_residuals=residuals,
        original_Lorentz_Gauss_rows=l['value_row'][:a],
        continued_original_Gauss_rows=e['value_row'][:a],
        original_temporal_duals_preserved=True, terminal_Dirichlet_domain_imposed=False,
        native_heat_or_normalized_soft_Pauli_completed=False)


def materialize_wick_temporal_action(output, *, repository=None):
    """Consume and reapply the actual corrected full488 magnetic midpoint forms."""
    from pathlib import Path
    from hashlib import sha256
    import json
    from .muon_birth_candidate_geometry_action import ROOT
    from .muon_profile_preserving_phase_sample import load_profile_preserving_phase
    from .muon_parent_maxwell_full_q_application import retained_full_q_angular_space
    from .muon_corrected_profile_magnetic_response import corrected_magnetic_source_sample
    from .muon_electromagnetic_soft_magnetic_source import magnetic_turn_on_profile
    from .muon_birth_phase_continuation import _compressed_npz

    root = Path(ROOT if repository is None else repository); out = Path(output)
    out = out if out.is_absolute() else root/out
    if out.exists():
        raise FileExistsError('preserve all earlier continuation applications')
    source_folder = root/'artifacts/muon_corrected_profile_magnetic_response_20261011/run_1'
    receipt_path = source_folder/'result.json'; md = json.loads(receipt_path.read_bytes())
    if md['classification'] != 'EVALUATED_CORRECTED_PROFILE_SAME_BIRTH_LOCAL_MAGNETIC_FULL488_RETARDED_RESPONSE':
        raise ValueError('same actual corrected-profile response required')
    refs = dict(md['input_hashes']); refs[receipt_path.relative_to(root).as_posix()] = sha256(receipt_path.read_bytes()).hexdigest()
    if any(sha256((root/p).read_bytes()).hexdigest() != h for p, h in refs.items()):
        raise ValueError('consumed source changed before continuation')
    angular = retained_full_q_angular_space(root); arrays = {}; rows = []
    for side, folder in (('incoming', 'artifacts/muon_finite_normal_phase_20261011/incoming_run_1'),
                          ('outgoing', 'artifacts/muon_inherited_finite_normal_phase_20261011/run_1')):
        phase = load_profile_preserving_phase(folder, repository=root); refs.update(phase['input_hashes'])
        L = abs(phase['receipt']['span']); t = -L/2 if side == 'incoming' else L/2; u = L/2
        actual = corrected_magnetic_source_sample(phase, t, angular, electric_charge=md['electric_charge'])
        values = {}
        for stem in ('phase', 'velocity', 'contacts', 'operator_M', 'operator_B', 'operator_K'):
            path = source_folder/(side+'_'+stem+'.npz'); expected = md['array_archives'][path.name]['sha256']
            if sha256(path.read_bytes()).hexdigest() != expected:
                raise ValueError('actual source/action arrays changed')
            refs[path.relative_to(root).as_posix()] = expected
            with np.load(path, allow_pickle=False) as a:
                data = {k:a[k].copy() for k in a.files}
            hit = np.flatnonzero(data['times'] == u)
            if len(hit) != 1:
                raise ValueError('actual retained action/response midpoint required')
            wanted = {'phase':'state', 'velocity':'velocity', 'contacts':'A_tau'}.get(stem,
                'raw_'+stem.removeprefix('operator_'))
            values[stem] = {wanted:data[wanted][hit[0]]}
        forms = actual['action']['raw_forms']
        saved_defect = max(float(np.max(abs(a-values['operator_'+name]['raw_'+name])))
            for a, name in zip(forms, ('M', 'B', 'K')))
        p, pt, _ = magnetic_turn_on_profile(u, L/4) if side == 'incoming' else (1., 0., 0.)
        x = np.r_[values['contacts']['A_tau'], values['phase']['state'][:400], p*np.eye(8)]
        v = np.r_[np.zeros((80, 8)), values['velocity']['velocity'][:400], pt*np.eye(8)]
        application = compare_temporal_action_continuation(forms, x, v, 80)
        for label, collection in (('L', forms), ('E', application['forms'])):
            for name, a in zip(('M', 'B', 'K'), collection):
                arrays[side+'_'+label+'_'+name] = a
        for label in ('lorentz_rows', 'euclidean_rows', 'lorentz_reduced', 'euclidean_reduced'):
            for key, a in application[label].items():
                if isinstance(a, np.ndarray):
                    arrays[side+'_'+label+'_'+key] = a
        arrays[side+'_field_source_values_L'] = x; arrays[side+'_field_source_rates_L'] = v
        arrays[side+'_coordinate_rotation'] = application['coordinate_rotation']
        arrays[side+'_actual_raw_fields'] = actual['raw_sample']['raw_fields']
        arrays[side+'_Q'] = actual['source']['connection_source']; arrays[side+'_Qdot'] = actual['source']['connection_source_rate']
        rows.append(dict(side=side, coordinate_time=t,
            producer_reapplication_maximum_difference=saved_defect,
            continuation_residuals=application['continuation_residuals'],
            actual_Lorentz_Gauss_maximum=float(np.max(abs(application['original_Lorentz_Gauss_rows']))),
            continued_Gauss_maximum=float(np.max(abs(application['continued_original_Gauss_rows']))),
            saved_canonical_dual_maximum_difference=float(np.max(abs(application['lorentz_rows']['momentum'][80:480]-
                values['phase']['state'][400:]))),
            actual_source_action_pairing_norm=float(np.linalg.norm(application['lorentz_rows']['action_pairing'])),
            original_temporal_dual_norm=float(np.linalg.norm(application['lorentz_rows']['momentum'][80:480])),
            continued_mixed_form_imaginary_norm=float(np.linalg.norm(application['forms'][1].imag))))
        print(json.dumps(dict(stage='actual_full488_temporal_action_continuation', **rows[-1]), sort_keys=True), flush=True)
    for name in ('muon_wick_temporal_action', 'muon_local_wick_action', 'muon_corrected_profile_magnetic_response'):
        p = 'src/bhsm/interface/'+name+'.py'; refs[p] = sha256((root/p).read_bytes()).hexdigest()
    if any(sha256((root/p).read_bytes()).hexdigest() != h for p, h in refs.items()):
        raise RuntimeError('consumed action changed during continuation')
    out.mkdir(parents=True); _compressed_npz(out/'application.npz', arrays)
    result = dict(classification='EVALUATED_CORRECTED_FULL488_TEMPORAL_ACTION_WICK_APPLICATION',
        records=rows, input_hashes=refs, numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        coordinates='At80 algebraic + Ar/Ai320 + intrinsicH80 + actual magnetic source8',
        normalization='parent per-kappa matrices with scalar relative8; common cap conversion is 1/(8V²), not inserted into a canonical dual twice',
        equation='L_E=-L_L(R^-1 x_E,iR^-1 v_E), R=diag(-iI80,I408)',
        original_Gauss_and_moving_Q_Qdot_source_rows_retained=True,
        time_derivative_of_At='zero placeholder in the unused algebraic rate slot; no physical At rate asserted',
        inherited_temporal_faces='incoming final/outgoing initial action dual signs unchanged; existing numerical outer canonical faces retained',
        new_terminal_Dirichlet_domain_or_real_positive_spectrum_selected=False,
        analytic_global_contour_or_exterior_relative_domain_completed=False,
        physical_a_mu=None, physical_g_mu=None,
        error_scope='binary64 actual local action/replay and original-row checks; no full analytic-contour radius, coefficient interpolation or physical Pauli uncertainty enclosure')
    (out/'result.json').write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf8', newline='\n')
    return result
