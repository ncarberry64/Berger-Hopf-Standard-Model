"""Original bulk, Jacobi and Green consumption of a D5 field family.

The field may be a coefficient kernel in the independently normalized
right and LR/RL source coordinates.  It is not thereby a selected state.
The radial operator retains the entire supplied time/fibre matrix; its
zero-order part includes the original time differentiation operator.
All pairings here are ordered analytic pairings, without conjugation.
"""
from __future__ import annotations

import numpy as np
from numpy.polynomial.legendre import leggauss
from numpy.polynomial import Polynomial


def _finite(value, shape, name):
    if value is None:
        raise ValueError(name + ' is unassigned; no zero substitution is allowed')
    a = np.asarray(value, complex)
    if a.shape != shape or not np.isfinite(a).all():
        raise ValueError(name + ': explicit finite shape ' + str(shape) + ' required')
    return a


def exact_lagrange_time_pairing(coordinate_times, time_derivative):
    """Exact polynomial mass/SBP relation for the actual six-node chart.

    Endpoints plus four interior Gauss points are not six Lobatto points.
    Their interpolatory diagonal weights do not integrate all products of
    the six degree-five trial functions. Six Gauss points integrate this
    dense degree-ten mass matrix exactly up to binary arithmetic.
    """
    t = np.asarray(coordinate_times, float)
    if (t.ndim != 1 or len(t) != 6 or not np.isfinite(t).all()
            or np.any(np.diff(t) <= 0)):
        raise ValueError('the actual ordered six-node history chart is required')
    Dt = _finite(time_derivative, (6, 6), 'actual time differentiation matrix')
    half = (t[-1]-t[0])/2
    z = (t-(t[-1]+t[0])/2)/half
    points, weights = leggauss(6)
    basis = np.array([Polynomial.fromroots(np.delete(z, i))(points)
                      / np.prod(z[i]-np.delete(z, i)) for i in range(6)])
    mass = half * np.einsum('q,iq,jq->ij', weights, basis, basis)
    endpoint = np.zeros((6, 6))
    endpoint[-1, -1], endpoint[0, 0] = 1., -1.
    sbp = mass @ Dt + Dt.T @ mass-endpoint
    return dict(temporal_pairing=mass, temporal_endpoint_pairing=endpoint,
        exact_polynomial_SBP_rows=sbp,
        variable_coefficient_products_not_claimed_exact=True,
        physical_time_or_moving_face_derivative_selected=False)


def original_time_fibre_radial_operator(time_principal, radial_principal,
        body, *, time_principal_first, radial_principal_first, body_first,
        time_derivative, time_derivative_first, density, density_first,
        temporal_pairing, temporal_pairing_first):
    """Assemble original D5 coefficients without compressing time or fibre.

    The derivative of the time differentiation matrix is an explicit
    argument. A held nodal time chart may supply its exact zero; a moving
    domain must supply its actual derivative. The scalar density remains
    a separate weak-pairing matrix rather than a new operator mass.
    """
    T = np.asarray(time_principal, complex)
    if (T.ndim != 4 or T.shape[-2] != T.shape[-1] or not min(T.shape)
            or not np.isfinite(T).all()):
        raise ValueError('complete radial x time x fibre x fibre principal required')
    q, nt, d, _ = T.shape
    R = _finite(radial_principal, T.shape, 'original radial coefficient')
    K = _finite(body, T.shape, 'original D5 body coefficient')
    Tj = _finite(time_principal_first, T.shape, 'original time coefficient source')
    Rj = _finite(radial_principal_first, T.shape, 'original radial coefficient source')
    Kj = _finite(body_first, T.shape, 'original body coefficient source')
    Dt = _finite(time_derivative, (nt, nt), 'actual time differentiation matrix')
    Dtj = _finite(time_derivative_first, Dt.shape, 'time domain derivative')
    Mt = _finite(temporal_pairing, Dt.shape, 'explicit temporal weak pairing')
    Mtj = _finite(temporal_pairing_first, Dt.shape, 'temporal weak pairing source')
    mu = _finite(density, (q, nt), 'actual original scalar density')
    muj = _finite(density_first, mu.shape, 'actual scalar density source')
    eye = np.eye(nt)
    diagonal = lambda A: np.einsum('ab,qaij->qaibj', eye, A).reshape(q, nt*d, nt*d)
    timed = lambda A, D: np.einsum('ab,qaij->qaibj', D, A).reshape(q, nt*d, nt*d)
    mass = np.kron(Mt, np.eye(d))
    massj = np.kron(Mtj, np.eye(d))
    Mu = diagonal(mu[..., None, None] * np.eye(d))
    Muj = diagonal(muj[..., None, None] * np.eye(d))
    fullD, fullDj = np.kron(Dt, np.eye(d)), np.kron(Dtj, np.eye(d))
    A = diagonal(mu[..., None, None] * T)
    Aj = diagonal(muj[..., None, None] * T+mu[..., None, None] * Tj)
    nodal_A_t = np.einsum('ab,qbij->qaij', Dt, mu[..., None, None]*T)
    nodal_A_tj = np.einsum('ab,qbij->qaij', Dtj, mu[..., None, None]*T)
    nodal_A_tj += np.einsum('ab,qbij->qaij', Dt,
        muj[..., None, None]*T+mu[..., None, None]*Tj)
    alias = fullD @ A-A @ fullD-diagonal(nodal_A_t)
    aliasj = fullDj @ A+fullD @ Aj-Aj @ fullD-A @ fullDj-diagonal(nodal_A_tj)
    endpoint = np.zeros((nt, nt))
    endpoint[-1, -1], endpoint[0, 0] = 1., -1.
    boundary = np.kron(endpoint, np.eye(d)) @ A
    boundaryj = np.kron(endpoint, np.eye(d)) @ Aj
    comm = mass @ (A @ fullD-fullD @ A)
    commj = massj @ (A @ fullD-fullD @ A)
    commj += mass @ (Aj @ fullD+A @ fullDj-fullDj @ A-fullD @ Aj)
    sbp = mass @ A @ fullD+fullD.T @ mass @ A-boundary-comm
    sbpj = (massj @ A @ fullD+mass @ Aj @ fullD+mass @ A @ fullDj
        +fullDj.T @ mass @ A+fullD.T @ massj @ A+fullD.T @ mass @ Aj
        -boundaryj-commj)
    return dict(radial_principal=diagonal(R),
        radial_principal_first=diagonal(Rj),
        zero_time_operator=diagonal(K) + timed(T, Dt),
        zero_time_operator_first=diagonal(Kj) + timed(Tj, Dt) + timed(T, Dtj),
        weak_density=mass @ Mu,
        weak_density_first=massj @ Mu+mass @ Muj,
        original_temporal_boundary_current=boundary,
        original_temporal_boundary_current_first=boundaryj,
        complete_temporal_commutator_contact=comm,
        complete_temporal_commutator_contact_first=commj,
        temporal_discrete_Green_assembly_rows=sbp,
        temporal_discrete_Green_assembly_source_rows=sbpj,
        variable_coefficient_time_product_aliasing=alias,
        variable_coefficient_time_product_aliasing_first=aliasj,
        scalar_density_not_operator_mass=True,
        full_supplied_time_and_fibre_rows_retained=True)


def radial_analytic_left_from_inverse(fundamental_inverse,
        fundamental_inverse_first, radial_principal, radial_principal_first,
        weak_density, weak_density_first):
    """Derive the literal discrete radial dual from the solved inverse.

    L=F_inverse (W R)^-1 gives L W R=F_inverse. Therefore its current
    on F is the independently saved product F_inverse F, including that
    product's numerical defect; identity is not enforced afterwards.
    This retains the original Lorentz radial current and source derivative.
    It is a finite radial-adjoint family; it supplies no physical outer
    annihilator, no positive native pairing, and no Hilbert conjugation.
    """
    inverse = np.asarray(fundamental_inverse, complex)
    if (inverse.ndim != 3 or inverse.shape[1] != inverse.shape[2]
            or not min(inverse.shape) or not np.isfinite(inverse).all()):
        raise ValueError('actual full fundamental inverse required')
    inversej = _finite(fundamental_inverse_first, inverse.shape,
                       'actual fundamental inverse source')
    R = _finite(radial_principal, inverse.shape, 'original radial current coefficient')
    Rj = _finite(radial_principal_first, R.shape, 'radial current coefficient source')
    W = _finite(weak_density, R.shape, 'original radial weak density')
    Wj = _finite(weak_density_first, R.shape, 'radial weak density source')
    J = W @ R
    Jj = Wj @ R + W @ Rj
    right_solve = lambda A, B: np.linalg.solve(
        A.swapaxes(-1, -2), B.swapaxes(-1, -2)).swapaxes(-1, -2)
    L = right_solve(J, inverse)
    Lj = right_solve(J, inversej-L @ Jj)
    return dict(independent_left=L, independent_left_first=Lj,
        original_current_recovery_rows=L @ J-inverse,
        original_current_source_recovery_rows=Lj @ J+L @ Jj-inversej,
        analytic_left_or_source_conjugated=False,
        finite_radial_adjoint_only=True, physical_outer_annihilator_selected=False)


def consume_original_d5_bulk_weak_jacobi(radial_principal, zero_time_operator,
        value, radial_derivative, *, radial_principal_first,
        zero_time_operator_first, value_first, radial_derivative_first,
        independent_left, independent_left_first, weak_density,
        weak_density_first, coordinate_weights, coordinate_weights_first):
    """Apply R V_rho+Q V and its complete supplied source derivative.

    Q contains the original Lorentz time operator as well as its local
    body coefficient.  weak_density is an explicit matrix in that SAME
    represented time/fibre space; it may contain the declared temporal
    integration/pairing matrix.  Dirac-bar conversion belongs in the
    supplied left map exactly once.  Nothing selects an outer condition.
    """
    V = np.asarray(value, complex)
    if V.ndim != 3 or not min(V.shape) or not np.isfinite(V).all():
        raise ValueError('nonempty radial x full-fibre x source field required')
    q, d, n = V.shape
    R = _finite(radial_principal, (q, d, d), 'original radial principal')
    Q = _finite(zero_time_operator, R.shape, 'original body/time operator')
    Rj = _finite(radial_principal_first, R.shape, 'radial principal source')
    Qj = _finite(zero_time_operator_first, R.shape, 'body/time source')
    Vr = _finite(radial_derivative, V.shape, 'actual radial field derivative')
    Vj = _finite(value_first, V.shape, 'actual field source')
    Vrj = _finite(radial_derivative_first, V.shape, 'actual radial field source')
    L = np.asarray(independent_left, complex)
    if L.ndim != 3 or L.shape[0] != q or L.shape[2] != d or not L.shape[1]:
        raise ValueError('independent analytic left full-fibre map required')
    L = _finite(L, L.shape, 'independent analytic left')
    Lj = _finite(independent_left_first, L.shape, 'independent analytic left source')
    W = _finite(weak_density, R.shape, 'original weak density/pairing')
    Wj = _finite(weak_density_first, R.shape, 'weak density/pairing source')
    w = _finite(coordinate_weights, (q,), 'coordinate weights')
    wj = _finite(coordinate_weights_first, (q,), 'coordinate weight source')
    rows = R @ Vr + Q @ V
    vertex = Rj @ Vr + Qj @ V
    response = R @ Vrj + Q @ Vj
    first_rows = vertex + response
    contract = lambda weights, left, density, right: np.einsum(
        'q,qij->ij', weights, left @ (density @ right))
    weak = contract(w, L, W, rows)
    direct = contract(w, L, W, vertex)
    state = contract(w, L, W, response)
    left = contract(w, Lj, W, rows)
    density = contract(w, L, Wj, rows)
    weight = contract(wj, L, W, rows)
    return dict(original_full_D5_rows=rows, original_full_D5_source_rows=first_rows,
        original_direct_operator_source_rows=vertex,
        original_bulk_state_source_rows=response, ordered_weak_action=weak,
        ordered_direct_field_vertex=direct, ordered_bulk_state_response=state,
        ordered_left_contact=left, ordered_density_pairing_contact=density,
        ordered_coordinate_weight_contact=weight,
        complete_ordered_weak_source=direct + state + left + density + weight,
        full_time_and_fibre_operator_retained=True,
        analytic_left_or_source_conjugated=False,
        physical_state_contraction_or_formation_load_selected=False,
        physical_outer_condition_selected=False)


def original_d5_green_return(radial_principal, value, *, radial_principal_first,
        value_first, independent_left, independent_left_first, weak_density,
        weak_density_first, orientation):
    """Return the original signed weak radial current and all its contacts.

    A first-order Green current is L W R V, rather than a bare normal
    derivative or a stationary native temporal return.  The caller supplies
    the actual outer/inner orientation.  The returned family is retained
    even when its physical outer equation has not yet been imposed.
    """
    sign = int(orientation)
    if sign != orientation or sign not in (-1, 1):
        raise ValueError('actual signed radial face orientation required')
    V = np.asarray(value, complex)
    if V.ndim != 3 or not min(V.shape) or not np.isfinite(V).all():
        raise ValueError('actual face field family required')
    q, d, _ = V.shape
    R = _finite(radial_principal, (q, d, d), 'original face radial principal')
    Rj = _finite(radial_principal_first, R.shape, 'face radial source')
    Vj = _finite(value_first, V.shape, 'face field source')
    L = np.asarray(independent_left, complex)
    if L.ndim != 3 or L.shape[0] != q or L.shape[2] != d or not L.shape[1]:
        raise ValueError('actual independent analytic face left map required')
    L = _finite(L, L.shape, 'analytic face left')
    Lj = _finite(independent_left_first, L.shape, 'analytic face left source')
    W = _finite(weak_density, R.shape, 'actual face weak density/pairing')
    Wj = _finite(weak_density_first, R.shape, 'face density/pairing source')
    current = sign * L @ W @ R @ V
    left = sign * Lj @ W @ R @ V
    density = sign * L @ Wj @ R @ V
    principal = sign * L @ W @ Rj @ V
    field = sign * L @ W @ R @ Vj
    return dict(signed_original_Green_return=current,
        signed_original_Green_return_first=left + density + principal + field,
        Green_left_contact=left, Green_density_pairing_contact=density,
        Green_principal_contact=principal, Green_field_response_contact=field,
        orientation=sign, native_temporal_conormal_substituted=False,
        physical_outer_equation_satisfied=None)


def consume_event_trace_operand(value, value_first, *, coordinate_times,
        event_time_index, fibre_width, branch_identity):
    """Insert an actual interior field family in the AE2 event trace row.

    The full event equation is Gamma0_child-U_R Gamma0_event=0.  Its
    newly evaluated operand below is Gamma0_event throughout the returned
    strip.  U_R, its derivative and the child trace remain separate unknowns;
    a matching array shape does not authorize their identity substitution.
    """
    t = np.asarray(coordinate_times, float)
    f = int(fibre_width)
    k = int(event_time_index)
    if (t.ndim != 1 or not len(t) or not np.isfinite(t).all()
            or np.any(np.diff(t) <= 0) or f != fibre_width or f < 1
            or k != event_time_index or not 0 <= k < len(t)
            or not isinstance(branch_identity, str) or not branch_identity):
        raise ValueError('actual ordered time/fibre/event/branch identities required')
    V = np.asarray(value, complex)
    if (V.ndim != 3 or not min(V.shape) or V.shape[1] != len(t) * f
            or not np.isfinite(V).all()):
        raise ValueError('complete radial x (time*fibre) x source field required')
    Vj = _finite(value_first, V.shape, 'complete event field source')
    trace = V.reshape(len(V), len(t), f, V.shape[2])[:, k].copy()
    first = Vj.reshape(len(V), len(t), f, V.shape[2])[:, k].copy()
    return dict(event_incoming_bulk_trace_operand=trace,
        event_incoming_bulk_trace_operand_first=first,
        event_row_coefficient_of_reset_lift=-trace,
        event_Jacobi_coefficient_of_reset_lift=-first,
        event_Jacobi_coefficient_of_reset_lift_first=-trace,
        event_coordinate_time=float(t[k]), branch_identity=branch_identity,
        original_event_row='Gamma0_child-U_R Gamma0_event=0',
        original_event_Jacobi_row=(
            'delta Gamma0_child-(delta U_R) Gamma0_event-'
            'U_R delta Gamma0_event=0'),
        held_event_residual=None, reset_lift_assigned=False,
        child_trace_assigned=False, physical_section_selected=False,
        two_eta_collars_identified_with_time_histories=False)


def consume_solved_bulk_family(arrays):
    """Consume the executed incoming D5 bulk family in original event rows.

    This assembles no new selector or physical outer condition.  Each
    independent a_R/a_LR/a_RL column is retained, together with the
    factorized homogeneous complement.  The returned non-null event
    operands are ACTUAL interior responses of the supplied operator.
    Their physical amplitude relations, unknown reset and child data are
    still part of the joint equations, rather than set to identity/zero.
    """
    t = np.asarray(arrays['times'], float)
    rho = np.asarray(arrays['radial_nodes'], float)
    D = np.asarray(arrays['time_derivative'], complex)
    coll = np.asarray(arrays['radial_node_is_collocation'], bool)
    step_ids = np.asarray(arrays['radial_node_step'], int)
    if (t.shape != (6,) or t[-1] != 0 or rho.ndim != 1 or len(rho) < 3
            or np.any(np.diff(rho) >= 0) or coll.shape != rho.shape
            or step_ids.shape != rho.shape or np.any(step_ids < 0)):
        raise ValueError('same actual incoming six-node and inward radial strip required')
    pair = exact_lagrange_time_pairing(t, D)
    nr, nt = len(rho), len(t)
    mass = pair['temporal_pairing']
    quadrature = np.zeros(nr)
    nsteps = int(np.max(step_ids))+1
    boundaries = np.linspace(rho[0], rho[-1], nsteps+1)
    for step in range(nsteps):
        indices = np.flatnonzero((step_ids == step) & coll)
        if len(indices) < 2:
            raise ValueError('every original radial Gauss stage is required')
        nodes, weights = leggauss(len(indices))
        expected = (boundaries[step]+boundaries[step+1])/2
        expected += (boundaries[step+1]-boundaries[step])*nodes/2
        # rho is of order one and the computational strip can be very
        # narrow. Comparing the actual stored nodes retains that scale.
        if not np.array_equal(rho[indices], expected):
            if np.max(abs(rho[indices]-expected)) > 4*np.spacing(max(abs(rho))):
                raise ValueError('source consumer must use the actual radial Gauss nodes')
        quadrature[indices] = abs(boundaries[step+1]-boundaries[step])*weights/2
    result = dict(radial_integration_weights=quadrature,
        temporal_dense_pairing=mass,
        exact_temporal_polynomial_SBP_rows=pair['exact_polynomial_SBP_rows'])
    reports = {}
    maximum = lambda a: float(np.max(abs(a)))
    norm = lambda a: float(np.linalg.norm(a))
    operator_reports = {}
    for side in ('plus', 'minus'):
        for b, branch in enumerate(('particle', 'conjugate')):
            op_label = side+'_'+branch
            prefix = op_label+'_'
            op = original_time_fibre_radial_operator(
                arrays[prefix+'time64'], arrays[prefix+'radial64'],
                arrays[prefix+'body64'],
                time_principal_first=arrays[prefix+'time_source64'],
                radial_principal_first=arrays[prefix+'radial_source64'],
                body_first=arrays[prefix+'body_source64'],
                time_derivative=D, time_derivative_first=np.zeros_like(D),
                density=2*np.pi**2*arrays['density'],
                density_first=2*np.pi**2*arrays['density_source'],
                temporal_pairing=mass, temporal_pairing_first=np.zeros_like(mass))
            R, Rj, Q, Qj, W, Wj = (op[k] for k in (
                'radial_principal', 'radial_principal_first',
                'zero_time_operator', 'zero_time_operator_first',
                'weak_density', 'weak_density_first'))
            left = radial_analytic_left_from_inverse(
                arrays[prefix+'analytic_inverse'],
                arrays[prefix+'analytic_inverse_source'], R, Rj, W, Wj)
            L, Lj = left['independent_left'], left['independent_left_first']
            operator_reports[op_label] = dict(
                literal_current_recovery_max=maximum(left['original_current_recovery_rows']),
                literal_current_source_recovery_max=maximum(left['original_current_source_recovery_rows']),
                temporal_Green_assembly_max=maximum(op['temporal_discrete_Green_assembly_rows']),
                temporal_Green_source_assembly_max=maximum(op['temporal_discrete_Green_assembly_source_rows']),
                temporal_product_aliasing_norm=norm(op['variable_coefficient_time_product_aliasing']),
                temporal_product_aliasing_source_norm=norm(op['variable_coefficient_time_product_aliasing_first']))
            labels = ('plus_seed',) if side == 'plus' else (
                'minus_seed', 'minus_LR', 'minus_RL')
            for label in labels:
                shape = np.asarray(arrays[label+'_value']).shape
                if len(shape) != 4 or shape[:3] != (nr, nt, 384):
                    raise ValueError('all three full384 carrier families must reach the consumer')
                for family in range(3):
                    block = slice((2*family+b)*64, (2*family+b+1)*64)
                    k = shape[-1]
                    extract = lambda name: np.asarray(arrays[label+'_'+name])[:, :, block].reshape(nr, nt*64, k)
                    V, Vr, Vj, Vrj = (extract(name) for name in (
                        'value', 'radial', 'source', 'radial_source'))
                    a = consume_original_d5_bulk_weak_jacobi(R, Q, V, Vr,
                        radial_principal_first=Rj, zero_time_operator_first=Qj,
                        value_first=Vj, radial_derivative_first=Vrj,
                        independent_left=L, independent_left_first=Lj,
                        weak_density=W, weak_density_first=Wj,
                        coordinate_weights=quadrature,
                        coordinate_weights_first=np.zeros(nr))
                    chi, chir, chij, chirj = (extract(name) for name in (
                        'chi_value', 'chi_radial', 'chi_source', 'chi_radial_source'))
                    E, Er, Ej, Erj = V-chi, Vr-chir, Vj-chij, Vrj-chirj
                    complement = R @ chir+Q @ chi
                    extension = R @ Er+Q @ E
                    complementj = Rj @ chir+Qj @ chi+R @ chirj+Q @ chij
                    extensionj = Rj @ Er+Qj @ E+R @ Erj+Q @ Ej
                    tag = label+'_family'+str(family)+'_'+branch
                    face = lambda index, sign: original_d5_green_return(
                        R[index:index+1], V[index:index+1],
                        radial_principal_first=Rj[index:index+1],
                        value_first=Vj[index:index+1],
                        independent_left=L[index:index+1],
                        independent_left_first=Lj[index:index+1],
                        weak_density=W[index:index+1],
                        weak_density_first=Wj[index:index+1], orientation=sign)
                    wall, inner = face(0, 1), face(nr-1, -1)
                    for key in ('ordered_direct_field_vertex', 'ordered_bulk_state_response',
                                'complete_ordered_weak_source'):
                        result[tag+'_'+key] = a[key]
                    result[tag+'_wall_original_Green'] = wall['signed_original_Green_return'][0]
                    result[tag+'_inner_original_Green'] = inner['signed_original_Green_return'][0]
                    result[tag+'_wall_original_Green_source'] = wall['signed_original_Green_return_first'][0]
                    result[tag+'_inner_original_Green_source'] = inner['signed_original_Green_return_first'][0]
                    # These are coefficients in the SAME finite weak
                    # pairing; they are not additional physical forces.
                    result[tag+'_temporal_endpoint_current'] = np.einsum(
                        'q,qij->ij', quadrature,
                        L @ (op['original_temporal_boundary_current'] @ V))
                    result[tag+'_temporal_commutator_contact'] = np.einsum(
                        'q,qij->ij', quadrature,
                        L @ (op['complete_temporal_commutator_contact'] @ V))
                    for name, matrix, source_matrix in (
                        ('temporal_endpoint_current',
                         op['original_temporal_boundary_current'],
                         op['original_temporal_boundary_current_first']),
                        ('temporal_commutator_contact',
                         op['complete_temporal_commutator_contact'],
                         op['complete_temporal_commutator_contact_first'])):
                        result[tag+'_'+name+'_source'] = np.einsum(
                            'q,qij->ij', quadrature,
                            Lj @ (matrix @ V) + L @ (source_matrix @ V)
                            + L @ (matrix @ Vj))
                    rows, rowsj = a['original_full_D5_rows'], a['original_full_D5_source_rows']
                    reports[tag] = dict(
                        original_full_D5_collocation_max=maximum(rows[coll]),
                        original_full_D5_offnode_max=maximum(rows[~coll]),
                        original_full_D5_source_collocation_max=maximum(rowsj[coll]),
                        original_full_D5_source_offnode_max=maximum(rowsj[~coll]),
                        original_complement_plus_extension_collocation_max=maximum((complement+extension)[coll]),
                        original_complement_plus_extension_source_collocation_max=maximum((complementj+extensionj)[coll]),
                        extension_source_norm=norm(extension),
                        complement_operator_image_norm=norm(complement),
                        weak_direct_vertex_norm=norm(a['ordered_direct_field_vertex']),
                        weak_bulk_state_response_norm=norm(a['ordered_bulk_state_response']),
                        complete_weak_source_max=maximum(a['complete_ordered_weak_source']),
                        weak_left_contact_norm=norm(a['ordered_left_contact']),
                        weak_density_contact_norm=norm(a['ordered_density_pairing_contact']),
                        signed_wall_Green_norm=norm(wall['signed_original_Green_return']),
                        signed_inner_Green_norm=norm(inner['signed_original_Green_return']),
                        signed_wall_plus_inner_Green_max=maximum(
                            wall['signed_original_Green_return']+inner['signed_original_Green_return']),
                        signed_wall_plus_inner_Green_source_max=maximum(
                            wall['signed_original_Green_return_first']+inner['signed_original_Green_return_first']))
    event_reports = {}
    for label in ('plus_seed', 'minus_seed', 'minus_LR', 'minus_RL'):
        V, Vj = (np.asarray(arrays[label+'_'+name]) for name in ('value', 'source'))
        event = consume_event_trace_operand(V.reshape(nr, nt*384, V.shape[-1]),
            Vj.reshape(nr, nt*384, Vj.shape[-1]), coordinate_times=t,
            event_time_index=nt-1, fibre_width=384,
            branch_identity='incoming_history_'+label)
        for key in ('event_incoming_bulk_trace_operand', 'event_incoming_bulk_trace_operand_first'):
            result[label+'_'+key] = event[key]
        event_reports[label] = dict(
            consumed_in_original_row=event['original_event_row'],
            consumed_in_original_Jacobi_row=event['original_event_Jacobi_row'],
            actual_bulk_event_operand_norm=norm(event['event_incoming_bulk_trace_operand']),
            actual_bulk_event_operand_source_norm=norm(event['event_incoming_bulk_trace_operand_first']),
            held_event_residual=None, reset_lift_assigned=False,
            outgoing_child_field_assigned=False)
    report = dict(classification='EXECUTED_D5_BULK_FAMILY_ORIGINAL_EVENT_JACOBI_GREEN_CONSUMPTION',
        operator_checks=operator_reports, original_bulk_checks=reports,
        actual_event_operand_applications=event_reports,
        exact_dense_temporal_mass_SBP_max=maximum(pair['exact_polynomial_SBP_rows']),
        angular_normalization='original Y0=1 in unit Haar measure; physical S3 volume 2*pi^2 multiplies weak density/current exactly once; point-fibre Ehat/Nhat coefficients unchanged',
        pairing_scope='finite degree5 trial with dense exact polynomial mass times nodal original density; variable-coefficient continuum product errors remain explicit',
        left_scope='complete computational analytic covector basis F_inverse (W R)_inverse; not the normalized physical left state or an outer annihilator',
        Dirac_bar_scope='left covector acts directly on original unsquared D5; its associated left spinor coefficient is L Gamma0, with no second Gamma0 appended',
        radial_orientation='positive integral inner-to-wall; signed wall current plus, held inner current minus',
        derivative_scope='actual common raw-rate source, fixed material time/strip quadrature; physical moving faces, amplitudes and state derivatives remain joint unknowns',
        amplitude_relations_required='a_R=(u_R,+ P_L+u_R,- P_R)g; a_LR=g/u_L,+; a_RL=g/u_L,-; independent factors not assigned',
        homogeneous_relation='Psi_side=particular_family+F_side Q_side h with h(time6,366); F and Q are saved, h and its source remain unassigned',
        physical_normal_profile_normalization_residual=None,
        held_physical_outer_residual=None, held_physical_time_face_residual=None,
        held_physical_event_residual=None, physical_formation_residual=None,
        physical_state_contraction_or_formation_load_selected=False,
        physical_full_outer_event_BVP_solved=False, physical_admission=False,
        native_temporal_corner_or_stationary_return_substituted=False,
        local_Maxwell_Higgs_removed_again=False,
        existing_Higgs_seam_readded_as_bulk_mass=False)
    return result, report
