"""Reorient saved E1 constraint jets after the joint connection/Higgs solve.

The original geometry jets and known action contacts are immutable inputs.
Only the affected constraint coefficients are transported to the new map.
The new Higgs and temporal equations do not acquire a borrowed Hessian.
"""
from __future__ import annotations

import numpy as np

from .muon_d5_event_constraint_twojet import (
    CHART_SIZE, constraint_normal_stationarity_contact,
)
from .muon_d5_spatial_bundle_application import cross_matrix


def _real(a, label):
    a = np.asarray(a)
    if np.iscomplexobj(a) and np.any(a.imag != 0):
        raise ValueError('real '+label+' required; no imaginary projection')
    return np.asarray(a.real, float)


def reorient_saved_constraint_twojet(cached, base_rotation, gauge_rotation):
    """Transport the saved13 exact constraint jets, without a geometry replay.

    The spatial transform is linear in every nonrotation argument. Only
    the parent operand changes under O/R, so its value/first/second
    coefficients can be transported exactly. All rotation placements are
    then rebuilt in the new O=O0 exp(b), R=exp(g) R0 charts.
    """
    O, R = (_real(a, 'new SO3 factor') for a in (base_rotation, gauge_rotation))
    if any(a.shape != (3, 3) for a in (O, R)) or max(
            np.max(abs(a.T@a-np.eye(3))) for a in (O, R)) > 2e-12 or min(
            np.linalg.det(O), np.linalg.det(R)) < 0:
        raise ValueError('actual orientation-preserving orthogonal factors required')
    Op, Rp = cached['base_rotation'], cached['gauge_rotation']
    left, right = O.T@Op, Rp@R.T

    def transport(rows):
        a = np.asarray(rows)
        shape = a.shape
        a = a.reshape(3, 4, -1)
        out = np.empty_like(a)
        out[:, :3] = np.einsum('ab,bck,cd->adk', left, a[:, :3], right)
        out[:, 3] = np.einsum('ab,bk->ak', left, a[:, 3])
        return out.reshape(shape)

    J, H = (np.array(cached[k], copy=True) for k in ('gradient', 'hessian'))
    if J.shape != (13, CHART_SIZE) or H.shape != (13, CHART_SIZE, CHART_SIZE):
        raise ValueError('complete cached13x546 original constraint twojet required')
    # Preserve every child, inherited and reference geometry derivative.
    # The parent geometry/field row blocks alone carry the changed map.
    J[1:, :100] = transport(J[1:, :100])
    J[1:, 508:520] = transport(J[1:, 508:520])
    H[1:, :100, :100] = transport(H[1:, :100, :100])
    J[1:, 540:] = 0
    H[1:, 540:, :] = 0
    H[1:, :, 540:] = 0
    parent = cached['parent_total_spatial_connection']
    target = np.c_[O.T@parent[:, :3]@R.T, O.T@parent[:, 3]]
    value = np.array(cached['value'], copy=True)
    value[1:] = (cached['child_total_spatial_connection']-target).ravel()
    basis = [cross_matrix(e) for e in np.eye(3)]
    for i, L in enumerate(basis):
        J[1:, 540+i] = (L@target).ravel()
        a = np.zeros((3, 4), complex); a[:, :3] = target[:, :3]@L
        J[1:, 543+i] = a.ravel()
        for j, P in enumerate(basis):
            sym = (L@P+P@L)/2
            H[1:, 540+i, 540+j] = (-sym@target).ravel()
            a = np.zeros((3, 4), complex); a[:, :3] = -target[:, :3]@sym
            H[1:, 543+i, 543+j] = a.ravel()
            a = np.zeros((3, 4), complex); a[:, :3] = -L@target[:, :3]@P
            H[1:, 540+i, 543+j] = H[1:, 543+j, 540+i] = a.ravel()
        for column in list(range(100))+list(range(508, 520)):
            dp = -J[1:, column].reshape(3, 4)
            H[1:, 540+i, column] = H[1:, column, 540+i] = (L@dp).ravel()
            a = np.zeros((3, 4), complex); a[:, :3] = dp[:, :3]@L
            H[1:, 543+i, column] = H[1:, column, 543+i] = a.ravel()
    out = {k: np.array(v, copy=True) for k, v in cached.items()}
    out.update(value=value, gradient=J, hessian=H, base_rotation=O, gauge_rotation=R)
    return out


def append_joint_map_constraint_application(saved, joint_sources, previous_spatial):
    """Consume new A/H source rows in the saved normal-stationarity chart.

    All7 map-source coordinates remain explicit. The seventh Higgs phase
    acts trivially only in these13 classical rows; its separate Higgs
    equations and their unevaluated Hessians remain obligations.
    """
    out = {k: np.array(saved[k], copy=True) for k in (
        'normal_coordinate_basis', 'geometry_streams', 'independent_wall_connections',
        'parent_wall_gauge_map20x80', 'child_wall_gauge_map20x80')}
    indices = np.asarray(joint_sources['initial_candidate_index'], int)
    out['candidate_indices'] = indices
    B = out['normal_coordinate_basis']
    wall_map = out['child_wall_gauge_map20x80']
    reports = []
    for i, index in enumerate(indices):
        prefix = 'candidate_'+str(index)+'_'
        cached = {k[len(prefix):]: saved[k] for k in saved if k.startswith(prefix)}
        jets = reorient_saved_constraint_twojet(cached,
            joint_sources['base_rotation'][i], joint_sources['gauge_rotation'][i])
        fields = np.asarray(joint_sources['child_raw_field_Higgs_source_correction'][i])
        free_fields = np.asarray(joint_sources['child_raw_field_Higgs_free_rotation_phase_coefficients'][i])
        if fields.shape != (268,) or free_fields.shape != (268, 7):
            raise ValueError('complete new child field/Higgs particular and7 free sources required')
        allowed = np.r_[np.arange(168, 180), np.arange(260, 264)]
        held = np.setdiff1d(np.arange(268), allowed)
        if np.any(fields[held] != 0) or np.any(free_fields[held] != 0):
            raise ValueError('cached action/normal frame reuse requires unchanged geometry and other slots')
        raw = np.array(cached['actual_own_raw_sources'], copy=True)
        raw[1] += fields-previous_spatial['child_raw_field_source_corrections'][index]
        if not np.array_equal(raw[:, :100], cached['actual_own_raw_sources'][:, :100]):
            raise ValueError('same E1 geometry source identity required')
        xi = np.array(cached['actual_chart_source'], copy=True)
        xi[520:540] = wall_map@raw[1, 100:180]
        Bx = cached['normal_basis_source']
        app = constraint_normal_stationarity_contact(jets, B, Bx, xi)
        pivots = cached['constraint_pivot_columns']
        free_columns = cached['constraint_free_columns']
        kernel = np.eye(CHART_SIZE, dtype=complex)[:, free_columns]
        kernel[pivots] = -np.linalg.solve(jets['gradient'][:, pivots], jets['gradient'][:, free_columns])
        free = np.zeros((CHART_SIZE, 7), complex)
        free[540:546, :6] = np.eye(6)
        free[520:540] = wall_map@free_fields[100:180]
        # Keep the old action arrays exactly; neither a local subtraction
        # nor an action-cap call occurs in this map-only append.
        out.update({prefix+k: np.array(v, copy=True) for k, v in cached.items()})
        out.update({prefix+k: v for k, v in jets.items()})
        out.update({prefix+k: v for k, v in app.items()})
        out[prefix+'actual_own_raw_sources'] = raw
        out[prefix+'actual_chart_source'] = xi
        out[prefix+'constraint_kernel_all533_free_coordinates'] = kernel
        out[prefix+'constraint_kernel_original_rows'] = jets['gradient']@kernel
        out[prefix+'free_rotation_phase_chart_source_coefficients'] = free
        out[prefix+'free_rotation_phase_original_constraint_rows'] = jets['gradient']@free
        out[prefix+'normal_multiplier_curvature_free_rotation_phase_coefficients'] = np.einsum(
            'ia,kij,jb->bak', B, jets['hessian'], free)
        # Old6-column map data are retained as historical inputs, explicitly
        # renamed to prevent a consumer from interpreting them as new data.
        for key in ('free_rotation_chart_source_coefficients', 'free_rotation_original_constraint_rows',
                'normal_multiplier_curvature_free_rotation_coefficients'):
            out[prefix+'historical_'+key] = out.pop(prefix+key)
        report = dict(initial_candidate_index=int(index),
            original_constraint_value_max=float(np.max(abs(jets['value']))),
            actual_constraint_source_max=float(np.max(abs(app['normal_constraint_Jacobi_load']))),
            multiplier_curvature_coefficient_max=float(np.max(abs(app['normal_constraint_multiplier_source_curvature']))),
            multiplier_frame_coefficient_max=float(np.max(abs(app['normal_constraint_multiplier_source_frame']))),
            multiplier_complete_source_coefficient_max=float(np.max(abs(app['normal_constraint_multiplier_complete_source']))),
            constraint_kernel_max=float(np.max(abs(jets['gradient']@kernel))),
            all7_free_map_source_constraint_max=float(np.max(abs(jets['gradient']@free))),
            source_geometry_bitwise_unchanged=True, known_geometric_action_arrays_bitwise_reused=True,
            declared13_constraint_rank=13, full546_chart_free_dimension=533)
        reports.append(report)
    report = dict(classification='REORIENTED_SAVED_CONSTRAINT_TWOJET_AT_JOINT_CONNECTION_HIGGS_MAP',
        candidate_reports=reports, action_cap_evaluations=0, geometry_jet_evaluations=0,
        original13_rows='radius squared plus full12 spatial connection rows; new Higgs/time Hessians are not included',
        new_Higgs_constraint_Hessian=None, new_temporal_constraint_Hessian=None,
        multipliers_assigned=False, multiplier_firsts_assigned=False,
        complete_formation_Hessian=None, complete_stationarity_residual=None,
        known_action_scope='same-background raw bare geometry weak coefficients, old reference Casimir absent; no local Maxwell/Higgs functional or new native/state/domain term',
        known_action_reuse_reason='new particular/free field sources have zero geometry and source-time increments; this known bare sector has no A/H argument',
        local_removal_repeated=False, physical_native_field_dependence_set_zero=False,
        normal_basis_source_reused=True, all7_map_source_coordinates_retained=True,
        gauge_nullspace_proved=False, parent_homogeneous_coordinates_retained=3660,
        outer_conditions_solved=False, normal_profile_normalization=None,
        physical_guard=2e-10, physical_admission=False,
        error_scope='finite original constraint coefficients in the declared E1 chart; no physical norm, domain or continuum admission',
        NEXT_OPERAND='combine the saved thirteen-row multiplier curvature with the unevaluated Higgs/time and physical native/state/outer action coefficients once those equations determine their multipliers and boundary data')
    return out, report
