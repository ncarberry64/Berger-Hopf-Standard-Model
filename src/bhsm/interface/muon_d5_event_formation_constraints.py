"""Original event compatibility rows in the constrained formation chart.

The normal columns are derivatives in the action's proper material-graph
coordinate. They do not select a mechanical mode or a fermion boundary
state. Curvature compatibility is a primal constraint, not an extra force
chosen to cancel an action residual. Its multiplier remains unknown.
"""
from __future__ import annotations

import numpy as np

from .muon_actual_normal_shape_source import proper_normal_shape_coefficient
from .muon_d5_event_bundle_incidence import original_event_coefficients, wall_event_incidence
from .muon_parent_retarded_hypercharge import WALL


NORMAL_COLUMNS = ('parent_psi', 'parent_coordinate_psi_first',
                  'child_psi', 'child_coordinate_psi_first')
CONSTRAINT_ROWS = ('wall_radius_squared', 'Higgs2_curvature_trace',
                  'Higgs2_curvature_trace_square', 'Higgs2_curvature_determinant',
                  'SM16_curvature_trace', 'SM16_curvature_trace_square',
                  'SM16_curvature_determinant')


def proper_normal_coordinate_columns(raw, coordinate_rate, phase_lift):
    """Execute b_s=a psi, b_v=(D_t a)psi+a D_t psi in original raw268.

    These are actual coordinate directions for a still unknown normal
    function. The full phase-rate dependence is retained in D_t a. A
    coordinate-time rate is not renamed a proper-time derivative.
    """
    r, rt, P = map(np.asarray, (raw, coordinate_rate, phase_lift))
    if r.shape != (268,) or rt.shape != r.shape or P.shape != (268, 252):
        raise ValueError('same original raw268, coordinate rate and phase252 lift required')
    if not all(np.isfinite(x).all() for x in (r, rt, P)):
        raise ValueError('finite original normal coordinate operands required')
    a = proper_normal_shape_coefficient(r, P)
    value = complex(a['value'])
    first = complex(a['raw_gradient'] @ rt[:100])
    b = np.zeros((268, 2), complex)
    b[98, 0], b[99, 0], b[99, 1] = value, first, value
    return dict(raw_normal_columns=b, proper_graph_coefficient=np.array(value),
        proper_graph_coefficient_time_first=np.array(first),
        proper_graph_raw_gradient=a['raw_gradient'],
        proper_graph_raw_hessian=a['raw_hessian'],
        coordinate_variation='delta raw98=a*psi; delta raw99=(D_t a)*psi+a*D_t psi',
        physical_mode_selected=False)


def _first_slot(coefficients, index):
    """Select an explicitly supplied tangent; no missing slot becomes zero."""
    out = {}
    for key, value in coefficients.items():
        if key.endswith('_first') and isinstance(value, np.ndarray):
            if value.ndim < 1 or not 0 <= index < len(value):
                raise ValueError('original coefficient tangent index is out of range: '+key)
            out[key] = value[index:index+1]
        else:
            out[key] = value
    return out


def _constraint_vector(application, *, first):
    metric = 'spatial_metric_Xi_row' if first else 'spatial_metric_row'
    suffix = 'curvature_invariant_Xi_rows' if first else 'curvature_invariant_rows'
    # The represented metric row is an isotropic 3x3 matrix: its one
    # independent coefficient is retained once, with no norm rescaling.
    return np.r_[application[metric][0, 0],
        application['Higgs2_'+suffix], application['SM16_'+suffix]]


def corrected_original_event_source_directions(history, raw_correction, *, side):
    """Add an explicit own-field correction to the original Xi slots.

    The inherited born-parent/reference Xi directions are reconstructed
    from their original affine geometry germs, exactly as the coefficient
    owner does. Their additional correction slots are held explicitly in
    this provisional application, rather than inferred from equal arrays.
    """
    d = np.asarray(raw_correction)
    if d.shape != (268,) or not np.isfinite(d).all():
        raise ValueError('finite explicit original raw268 source correction required')
    if side not in ('parent', 'child'):
        raise ValueError('explicit original parent or inherited child required')
    source, _ = history.source(0.)
    own = (source+d)[:, None]
    if side == 'parent':
        # The parent operator consumes only its own mechanical profile.
        # Other API slots are unused placeholders, not physical references.
        return dict(raw=own, parent=own, references=np.array([own, own]))
    operands = history.original_phase_operands
    pair, refs = (np.asarray(operands[k]) for k in ('initial_pair', 'reference_pair'))
    def original_germ_rate(x):
        r = np.zeros_like(x)
        r[:37], r[98] = x[37:74], x[99]
        return r
    return dict(raw=own,
        parent=original_germ_rate(pair[0])[:, None],
        references=np.array([original_germ_rate(x)[:, None] for x in refs]))


def event_constraint_formation_application(parent_history, child_history):
    """Consume the actual E1 compatibility failure in normal formation rows.

    Born-parent and both reference variations are explicitly HELD for
    these four partial columns. They remain independent uncomputed columns
    of the physical joint derivative. In particular the parent's evolving
    endpoint is not silently identified with the child's born-parent germ.
    All other field and boundary coordinates remain free. No inverse or
    physical boundary state is obtained from this rectangular block.
    """
    normal = []
    for history in (parent_history, child_history):
        raw, rate = history.value(0.)
        normal.append(proper_normal_coordinate_columns(raw, rate,
            history.original_phase_operands['resolved_phase_coordinate_lift']))
    raw_columns = np.zeros((2, 268, 4), complex)
    raw_columns[0, :, :2] = normal[0]['raw_normal_columns']
    raw_columns[1, :, 2:] = normal[1]['raw_normal_columns']
    coefficients = []
    for j, (history, side) in enumerate(zip((parent_history, child_history), ('parent', 'child'))):
        directions = dict(raw=raw_columns[j], parent=np.zeros((268, 4), complex),
            references=np.zeros((2, 268, 4), complex))
        coefficients.append(original_event_coefficients(history, 0., [WALL],
            side=side, directions=directions))
    applications = [wall_event_incidence(_first_slot(coefficients[0], j),
        _first_slot(coefficients[1], j))[0] for j in range(4)]
    C = _constraint_vector(applications[0], first=False)
    J = np.column_stack([_constraint_vector(a, first=True) for a in applications])
    if not all(np.array_equal(C, _constraint_vector(a, first=False)) for a in applications[1:]):
        raise ArithmeticError('a supplied tangent changed the base event equation')
    singular = np.linalg.svd(J, compute_uv=False)
    # Rank is only a finite representation diagnostic; no SVD solution or
    # nullspace coordinate is selected as a physical state.
    rank = int(np.count_nonzero(singular > max(singular, default=0.)*1e-12))
    source_coefficients = [original_event_coefficients(history, 0., [WALL], side=side)
        for history, side in zip((parent_history, child_history), ('parent', 'child'))]
    source_application, _ = wall_event_incidence(*source_coefficients)
    source_load = _constraint_vector(source_application, first=True)
    # The radius and first curvature invariant are actual original rows.
    # Their two displacement pivots are nonsingular here. This is an exact
    # affine elimination, not a minimum-norm selection of a physical mode:
    # both psi-time derivatives and every other coupled coordinate remain
    # free, with their constraint images retained independently.
    pivot_rows, pivot_columns = np.array([0, 1]), np.array([0, 2])
    pivot = J[np.ix_(pivot_rows, pivot_columns)]
    if not np.isfinite(np.linalg.cond(pivot)) or np.linalg.det(pivot) == 0:
        raise np.linalg.LinAlgError('the declared original event-constraint pivots are singular')
    correction = np.linalg.solve(pivot, -source_load[pivot_rows])
    if np.any(correction.imag != 0):
        raise ValueError('the real original event tangency pivots produced a complex correction')
    corrected_source = source_load+J[:, pivot_columns]@correction
    free_columns = np.array([1, 3])
    free_reconstruction = -np.linalg.solve(pivot, J[np.ix_(pivot_rows, free_columns)])
    free_consistency = J[:, free_columns]+J[:, pivot_columns]@free_reconstruction
    raw_source_correction = np.einsum('ari,i->ar', raw_columns[:, :, pivot_columns], correction)
    corrected_coefficients = [original_event_coefficients(history, 0., [WALL],
        side=side, directions=corrected_original_event_source_directions(history, delta, side=side))
        for history, side, delta in zip((parent_history, child_history),
            ('parent', 'child'), raw_source_correction)]
    original_corrected, _ = wall_event_incidence(*corrected_coefficients)
    original_corrected_rows = _constraint_vector(original_corrected, first=True)
    arrays = dict(event_compatibility_residual=C,
        event_normal_coordinate_Jacobian=J,
        event_normal_multiplier_reaction_coefficients=J.T,
        raw_normal_coordinate_columns=raw_columns,
        event_normal_singular_values=singular,
        supplied_Xi_event_constraint_load=source_load,
        normal_displacement_pivot_rows=pivot_rows,
        normal_displacement_pivot_columns=pivot_columns,
        normal_displacement_pivot_matrix=pivot,
        provisional_normal_displacement_source_correction=correction,
        corrected_supplied_Xi_event_constraint_rows=corrected_source,
        provisional_raw_normal_source_correction=raw_source_correction,
        original_callback_corrected_supplied_Xi_rows=original_corrected_rows,
        original_callback_source_reconstruction_rows=original_corrected_rows-corrected_source,
        free_normal_time_derivative_columns=free_columns,
        free_normal_time_derivative_reconstruction=free_reconstruction,
        free_normal_time_derivative_original_rows=free_consistency)
    for side, n in zip(('parent', 'child'), normal):
        arrays.update({side+'_'+key: value for key, value in n.items()
            if isinstance(value, np.ndarray)})
    report = dict(classification='EVALUATED_ORIGINAL_EVENT_COMPATIBILITY_IN_FORMATION_CONSTRAINT_ROWS',
        constraint_row_order=list(CONSTRAINT_ROWS), normal_column_order=list(NORMAL_COLUMNS),
        invariant_row_scope='seven recorded necessary coefficients, including dependent and representation-related audits; only the two named original rows are used as independent pivots',
        original_constraint_equation='C(z)=0, necessary metric and gauge-curvature consequences of the original event base/bundle graph',
        executed_linearized_constraint='C(z)+C_psi*(psi_parent,D_t psi_parent,psi_child,D_t psi_child)+C_other*delta_z_other=0',
        original_KKT_stationarity_contact='C_psi.T*lambda; lambda is an unassigned event-constraint multiplier, not an independently added force',
        original_Jacobi_contact='D C*delta_z=−C; the stationarity Hessian also requires sum(lambda_i*D2 C_i), retained as uncomputed, not zero',
        constraint_residual_max=float(np.max(abs(C))),
        normal_coordinate_Jacobian_max=float(np.max(abs(J))),
        normal_coordinate_Jacobian_rank=rank,
        provisional_source_constraint_equation='C_Xi+C_psi_parent*delta_psi_parent+C_psi_child*delta_psi_child=0 with psi-time derivatives retained free and all other correction slots held explicitly',
        supplied_Xi_constraint_before_max=float(np.max(abs(source_load))),
        supplied_Xi_constraint_after_max=float(np.max(abs(corrected_source))),
        original_callback_corrected_Xi_constraint_max=float(np.max(abs(original_corrected_rows))),
        original_callback_source_reconstruction_max=float(np.max(abs(original_corrected_rows-corrected_source))),
        source_pivot_equations=[CONSTRAINT_ROWS[i] for i in pivot_rows],
        source_pivot_unknowns=[NORMAL_COLUMNS[i] for i in pivot_columns],
        source_pivot_condition=float(np.linalg.cond(pivot)),
        provisional_normal_displacement_source_corrections=correction.real.tolist(),
        free_time_derivative_reconstruction_max=float(np.max(abs(free_consistency))),
        particular_source_correction_is_physical_mode=False,
        correction_scope='two original necessary event Jacobi rows are solved exactly and every invariant row is independently checked; this does not solve original action stationarity or admit the supplied Xi as a complete physical derivative',
        normal_amplitudes_assigned=False, event_multipliers_assigned=False,
        complementary_field_columns_evaluated=False,
        born_parent_and_reference_columns_scope='held explicitly in these four partial derivatives; their independent physical variations remain required',
        homogeneous_coordinates_per_time_node=366, homogeneous_coordinates_assigned=False,
        fermionic_complement_identified_with_mechanical_psi=False,
        normal_profile_normalization=None, outer_equations_solved=False,
        full_formation_Hessian_evaluated=False, formation_crossing_selected=False,
        complete_physical_derivative=False, physical_admission=False,
        error_scope='binary64 analytic event-coefficient directional application at the original E1 wall; finite partial Jacobi block only, no continuum bound or completed coupled state',
        full_constraint_residual_after=None,
        NEXT_OPERAND='solve the full event/base/bundle and outer constraints jointly with the original action stationarity, retaining these nonzero compatibility rows, their remaining field derivatives and multiplier curvature')
    return arrays, report
