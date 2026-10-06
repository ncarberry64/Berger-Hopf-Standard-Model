"""Cache-only visibility of the existing seam witness on a parent response.

No action, source, frame, profile or witness is rebuilt. Ball bounds refer
to the frozen numerical arrays and decimal exports, not physical history.
"""
from decimal import Decimal
import numpy as np
from flint import arb, acb, acb_mat, ctx


def matrix(a):
    a = np.asarray(a)
    if a.ndim == 1:
        a = a[:, None]
    return acb_mat([[acb(float(z.real), float(z.imag)) for z in row] for row in a])


def decimal_export_ball(text):
    """Printed significant-digit rounding, not a bound on the original solve."""
    d = Decimal(text)
    if d == 0:
        return arb(0)
    last_unit = Decimal(1).scaleb(d.as_tuple().exponent)
    return arb(text, str(last_unit/2))


def decimal_vector(rows):
    return acb_mat([[acb(decimal_export_ball(r), decimal_export_ball(i))] for r, i in rows])


def center(a):
    return np.array([complex(float(a[i, 0].real.mid()), float(a[i, 0].imag.mid()))
                     for i in range(a.nrows())])


def subvector(a, first, last):
    return acb_mat([[a[i, 0]] for i in range(first, last)])


def norm_entries(entries):
    """Nonnegative component bounds avoid sqrt of a zero-crossing ball."""
    values = list(entries)
    lo = sum((z.abs_lower()**2 for z in values), arb(0)).sqrt().lower()
    hi = sum((z.abs_upper()**2 for z in values), arb(0)).sqrt().upper()
    mid = (lo+hi)/2
    radius = (hi-lo)/2+mid.rad()
    return arb(mid.mid(), radius.upper())


def norm(a):
    return norm_entries(a[i, j] for i in range(a.nrows()) for j in range(a.ncols()))


def upper(a):
    return float(np.nextafter(float(a.upper()), np.inf))


def interval(a):
    return [float(np.nextafter(float(a.lower()), -np.inf)), upper(a)]


def exported_rounding_error(a, exported):
    return upper(norm(a-matrix(exported)))


def reconstruct_node3(accepted_decimal, attachment, accepted, tail):
    """Actual solved entrance trace and SAME nonzero affine backsubstitution.

    The one small pivot solve bounds the cached recurrence's local equation
    defect. It is an error diagnostic, not a new coupled/source solution.
    """
    ctx.prec = 320
    u = decimal_vector(accepted_decimal['solution'])
    x2 = matrix(attachment['tail_trace_injection'])*u
    y0 = matrix(tail['backsubstitution_y'][0])
    Y0 = matrix(tail['backsubstitution_Y'][0])
    x3 = -Y0*x2+y0
    # No use of tail['solution'][1], whose entrance trace differs.
    D0 = matrix(tail['interior_pivots'][0])
    L0 = matrix(tail['lower'][0])
    reduced_rhs = matrix(tail['rhs'][1])-matrix(tail['upper'][1])*matrix(tail['backsubstitution_y'][1])
    residual = D0*x3+L0*x2-reduced_rhs
    correction = D0.solve(-residual)
    rounded = -tail['backsubstitution_Y'][0]@accepted['solved_node2_trace']+tail['backsubstitution_y'][0]
    return dict(node2=x2, node3=x3, a3=subvector(x3, 0, 12), c3=subvector(x3, 12, 24),
        affine=y0, rounded_node3=rounded, local_residual=residual,
        local_pivot_correction=correction,
        node2_export_error_upper=exported_rounding_error(x2, accepted['solved_node2_trace']),
        node3_binary_reconstruction_error_upper=exported_rounding_error(x3, rounded),
        local_pivot_correction_norm_upper=upper(norm(correction)),
        local_reduced_residual_norm_upper=upper(norm(residual)))


def existing_witness_actions(witness, reconstruction):
    """Use K_L W=0 before arithmetic; only c3 enters both extractions."""
    lo, hi = witness['eta_interval']
    mid = (arb(float(lo))+arb(float(hi)))/2
    radius = (arb(float(hi))-arb(float(lo)))/2
    eta = arb(mid.mid(), radius.upper())  # reuse, never refine eta
    nominal_eta = arb(float(witness['eta']))
    left, higgs, left_nom, higgs_nom = {}, {}, {}, {}
    error_left, error_higgs = {}, {}
    binary_left, binary_higgs = {}, {}
    dc = subvector(reconstruction['local_pivot_correction'], 12, 24)
    for n in (1, 3):
        A = matrix(witness[f'left_n{n}'].reshape(-1, 12))
        left[n] = eta*A*reconstruction['c3']
        left_nom[n] = nominal_eta*A*reconstruction['c3']
        error_left[n] = eta*A*dc
        rounded = float(witness['eta'])*(witness[f'left_n{n}'].reshape(-1, 12)
                                           @reconstruction['rounded_node3'][12:])
        binary_left[n] = left[n]-matrix(rounded)
    for n in (0, 2, 4):
        A = matrix(witness[f'forward_h_n{n}'].reshape(-1, 12))
        higgs[n] = eta*A*reconstruction['c3']
        higgs_nom[n] = nominal_eta*A*reconstruction['c3']
        error_higgs[n] = eta*A*dc
        rounded = float(witness['eta'])*(witness[f'forward_h_n{n}'].reshape(-1, 12)
                                           @reconstruction['rounded_node3'][12:])
        binary_higgs[n] = higgs[n]-matrix(rounded)
    combine = lambda rows: norm_entries(z[i, j] for z in rows.values()
        for i in range(z.nrows()) for j in range(z.ncols()))
    scalar_left = combine({n: left[n]-left_nom[n] for n in left})
    scalar_higgs = combine({n: higgs[n]-higgs_nom[n] for n in higgs})
    return dict(left=left, higgs=higgs, left_norm=combine(left), higgs_norm=combine(higgs),
        scalar_eta_left_error_upper=upper(scalar_left), scalar_eta_higgs_error_upper=upper(scalar_higgs),
        binary_visibility_left_error_upper=upper(combine(binary_left)),
        binary_visibility_higgs_error_upper=upper(combine(binary_higgs)),
        local_pivot_left_error_upper=upper(combine(error_left)),
        local_pivot_higgs_error_upper=upper(combine(error_higgs)))


def chirality_diagnostic(cut, wall, tail, point, accepted):
    """Same-column chirality from the saved image quotient, no new eigensolve.

    c_src anticommutes with gamma5, so output-left corresponds to input-right
    on the four saved spin probes. Carrier transport commutes with gamma5.
    """
    S, G = cut['independent_source_map'], cut['source_Haar_Gram']
    right_input = np.diag(np.tile([0., 0., 1., 1.], 8))
    P = np.linalg.solve(wall['wall_Haar_Gram'], S.conj().T@G@right_input@S)
    P24 = np.kron(np.eye(2), P)
    Q24 = np.eye(24)-P24
    return dict(coefficient_left_projector=P,
        projector_idempotency_residual=float(np.linalg.norm(P@P-P)),
        projector_geometric_self_adjoint_residual=float(np.linalg.norm(
            P.conj().T@wall['wall_Haar_Gram']-wall['wall_Haar_Gram']@P)),
        source_original_left_norm=float(np.linalg.norm(P@cut['source_coordinates'])),
        accepted_node2_left_norm=float(np.linalg.norm(P24@accepted['solved_node2_trace'])),
        affine_left_norm=float(np.linalg.norm(P24@tail['backsubstitution_y'][0])),
        recurrence_right_to_left_norm=float(np.linalg.norm(P24@tail['backsubstitution_Y'][0]@Q24)),
        recurrence_chirality_commutator_norm=float(np.linalg.norm(P24@tail['backsubstitution_Y'][0]-tail['backsubstitution_Y'][0]@P24)),
        point_moment_chirality_form_defects={k: float(np.linalg.norm(
            P24.conj().T@point[k]-point[k]@P24)) for k in ('A', 'B', 'C', 'M', 'Ms')},
        invariant_right_subspace_established=False,
        identity_needed_for_decoupling='P24 x2=0, P24 y0=0, P24 Y0(I-P24)=0; these identities do not hold in saved numerical model')
