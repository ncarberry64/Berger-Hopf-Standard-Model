"""Exact dual projection for a supplied finite charged self-dual CAR kernel.

This is a quotient theorem in normalized CAR coordinates, not an evaluated
E1 birth operator. No physical covariance is selected and an absent physical
kernel is never replaced by zero. Rational real and imaginary entries make
dimension, zero and moment-span decisions exact within the supplied scope.
"""
from __future__ import annotations

from collections.abc import Mapping
import sympy as sp


SCOPE = "SUPPLIED_FINITE_NORMALIZED_CAR_OPERATOR_ALGEBRA"


def _matrix(value, name):
    if value is None:
        raise ValueError(f"{name} is absent; no zero substitution is allowed")
    try:
        matrix = sp.ImmutableMatrix(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a nonempty square matrix") from exc
    if matrix.rows < 1 or matrix.rows != matrix.cols:
        raise ValueError(f"{name} must be a nonempty square matrix")
    for entry in matrix:
        real, imaginary = sp.expand(entry).as_real_imag()
        if real.is_Rational is not True or imaginary.is_Rational is not True:
            raise ValueError(f"{name} requires exact rational real/imaginary entries")
    return matrix


def _zero(matrix):
    return all(sp.expand(entry) == 0 for entry in matrix)


def _same(left, right):
    return left.shape == right.shape and _zero(left-right)


def _hermitian(matrix):
    return sp.ImmutableMatrix((matrix+matrix.adjoint())/2)


def _data(conjugation, charge_grading, particle_family_projector):
    p = _matrix(particle_family_projector, "particle_family_projector")
    if not _same(p, p.adjoint()) or not _same(p*p, p):
        raise ValueError("particle_family_projector must be Hermitian and idempotent")
    size = p.rows
    identity = sp.eye(2*size)
    g = _matrix(conjugation, "conjugation")
    charge = _matrix(charge_grading, "charge_grading")
    if g.shape != identity.shape or charge.shape != identity.shape:
        raise ValueError("charged Nambu dimensions must be twice the particle dimension")
    expected_charge = sp.diag(sp.eye(size), -sp.eye(size))
    if not _same(charge, expected_charge):
        raise ValueError("charge_grading must declare particle/conjugate blocks as diag(I,-I)")
    if not _same(g*g.adjoint(), identity) or not _same(g*g.conjugate(), identity):
        raise ValueError("conjugation must define an antiunitary involution")
    if not _same(g*charge.conjugate()*g.adjoint(), -charge):
        raise ValueError("conjugation must exchange the two charge sectors")
    q = sp.ImmutableMatrix(sp.diag(p, p.conjugate()))
    if not _same(g*q.conjugate()*g.adjoint(), q):
        raise ValueError("doubled family projector must be Gamma compatible")
    return p, g, charge, q


def _real_vector(matrix):
    values = []
    for entry in matrix:
        real, imaginary = sp.expand(entry).as_real_imag()
        values.extend((real, imaginary))
    return sp.Matrix(values)


def _independent_indices(matrices):
    if not matrices:
        return ()
    vectors = sp.Matrix.hstack(*(_real_vector(matrix) for matrix in matrices))
    return tuple(vectors.rref()[1])


def _particle_hermitian_basis(size):
    basis = []
    for row in range(size):
        value = sp.zeros(size)
        value[row, row] = 1
        basis.append(value)
    for row in range(size):
        for column in range(row+1, size):
            real = sp.zeros(size)
            real[row, column] = real[column, row] = 1
            imaginary = sp.zeros(size)
            imaginary[row, column] = sp.I
            imaginary[column, row] = -sp.I
            basis.extend((real, imaginary))
    return basis


def admissible_charged_nambu_tangent_basis(
    *, conjugation, charge_grading, particle_family_projector
):
    """Return a basis of the entire affine, family-supported tangent space.

    X=X-dagger, Gamma X Gamma=-X, [X,charge]=0 and X=Q X Q.
    Charge compatibility does not insert a fixed-charge expectation, particle
    number, purity, or commutation with the reset. Hadamard smoothing/tails
    belong to an actual continuum realization and cannot be certified here.
    """
    p, g, _, q = _data(conjugation, charge_grading, particle_family_projector)
    size = p.rows
    candidates = []
    for hermitian in _particle_hermitian_basis(size):
        particle = p*hermitian*p
        embedded = sp.diag(particle, sp.zeros(size))
        # Doubling, rather than division by two, chooses the particle block A.
        tangent = q*(embedded-g*embedded.conjugate()*g.adjoint())*q
        candidates.append(sp.ImmutableMatrix(tangent))
    return tuple(candidates[index] for index in _independent_indices(candidates))


def charged_nambu_tangent_projection(
    kernel, *, conjugation, charge_grading, particle_family_projector
):
    """Project a supplied real affine functional onto ALL allowed tangents.

    For the real Hilbert-Schmidt duality, S=Q E_charge P_Gamma- Herm(Delta) Q.
    The symmetry projections commute under the validated intertwining laws.
    Re Tr(X Delta)=Tr(X S) for every X in the stated tangent space. A zero S
    is necessary/sufficient in this finite affine space; it is not a physical
    verdict about an absent E1 operator or unevaluated continuum components.

    The input already includes its originating action's sign and doubling
    convention. In canonical Gamma-swap coordinates, the particle kernel is
    Pi*(Delta_pp-conjugate(Delta_hh))*Pi after Hermitianization.
    """
    p, g, charge, q = _data(conjugation, charge_grading, particle_family_projector)
    delta = _matrix(kernel, "kernel")
    if delta.shape != g.shape:
        raise ValueError("kernel and CAR data dimensions must agree")
    h = _hermitian(delta)
    gamma_odd = (h-g*h.conjugate()*g.adjoint())/2
    positive = (sp.eye(g.rows)+charge)/2
    negative = (sp.eye(g.rows)-charge)/2
    dephased = positive*gamma_odd*positive+negative*gamma_odd*negative
    sensitivity = sp.ImmutableMatrix(q*dephased*q)
    basis = admissible_charged_nambu_tangent_basis(
        conjugation=g, charge_grading=charge, particle_family_projector=p)
    return {
        "scope": SCOPE,
        "projected_kernel": sensitivity,
        "particle_sensitivity_kernel": sp.ImmutableMatrix(2*sensitivity[:p.rows, :p.rows]),
        "tangent_dimension": len(basis),
        "annihilates_all_admissible_tangents": _zero(sensitivity),
        "physical_E1_kernel_evaluated": False,
        "physical_covariance_selected": False,
        "continuum_Hadamard_or_tail_certified": False,
        "purity_or_fixed_occupation_imposed": False,
    }


def minimal_consumed_moments(
    kernels, *, conjugation, charge_grading, particle_family_projector
):
    """Find the exact REAL span of projected consumed row kernels.

    One nonzero scalar row consumes one moment even if its operator rank is
    greater than one. Several rows consume the dimension of their real dual
    span. This identifies relative affine state information, not an absolute
    Wick subtraction or selected value of Tr(C K).
    """
    items = list(kernels.items()) if isinstance(kernels, Mapping) else list(enumerate(kernels))
    if not items:
        raise ValueError("a nonempty supplied kernel ledger is required")
    projections = [charged_nambu_tangent_projection(
        value, conjugation=conjugation, charge_grading=charge_grading,
        particle_family_projector=particle_family_projector) for _, value in items]
    projected = [result["projected_kernel"] for result in projections]
    indices = _independent_indices(projected)
    basis = [projected[index] for index in indices]
    coefficients = []
    if basis:
        vectors = sp.Matrix.hstack(*(_real_vector(value) for value in basis))
        for value in projected:
            solution, parameters = vectors.gauss_jordan_solve(_real_vector(value))
            if parameters.rows:
                raise ValueError("moment basis unexpectedly dependent")
            coefficients.append(tuple(solution))
    else:
        coefficients = [() for _ in projected]
    return {
        "scope": SCOPE,
        "kernel_labels": tuple(label for label, _ in items),
        "span_dimension": len(indices),
        "basis_kernel_indices": indices,
        "basis_projected_kernels": tuple(basis),
        "basis_particle_kernels": tuple(projections[index]["particle_sensitivity_kernel"] for index in indices),
        "kernel_coefficients": tuple(coefficients),
        "all_rows_state_independent_in_supplied_scope": not indices,
        "physical_E1_kernel_evaluated": False,
        "physical_state_moment_values": None,
        "absolute_Wick_subtraction_selected": False,
    }


def reset_pullback_kernel(
    event_kernel, oriented_child_kernel, reset_lift, *,
    conjugation_event, conjugation_child,
    charge_grading_event, charge_grading_child,
    particle_family_projector_event, particle_family_projector_child
):
    """Pull back the child kernel on the reset GRAPH, not a commutant.

    The supplied child kernel already includes outward orientation and its
    geometric/source/domain pullbacks. No cancellation is assumed or imposed.
    Child X=U X_event U-dagger gives Delta=A_event+U-dagger A_child U.
    """
    _, ge, qe, fe = _data(conjugation_event, charge_grading_event,
                         particle_family_projector_event)
    _, gc, qc, fc = _data(conjugation_child, charge_grading_child,
                         particle_family_projector_child)
    event = _matrix(event_kernel, "event_kernel")
    child = _matrix(oriented_child_kernel, "oriented_child_kernel")
    reset = _matrix(reset_lift, "reset_lift")
    if any(value.shape != ge.shape for value in (gc, event, child, reset)):
        raise ValueError("reset/kernel dimensions must agree")
    if not _same(reset.adjoint()*reset, sp.eye(reset.rows)):
        raise ValueError("reset_lift must be exactly unitary")
    if not _same(reset*ge, gc*reset.conjugate()):
        raise ValueError("reset must intertwine CAR conjugations")
    if not _same(reset*qe, qc*reset) or not _same(reset*fe, fc*reset):
        raise ValueError("reset must intertwine charge and doubled family sectors")
    return {
        "pulled_back_kernel": sp.ImmutableMatrix(event+reset.adjoint()*child*reset),
        "reset_graph_law": "X_child=U_R*X_event*U_R_dagger",
        "incoming_reset_commutator_required": False,
        "physical_E1_kernel_evaluated": False,
    }


def occupation_sensitivity_kernel(operator):
    """Ordinary ordered chi-dagger A chi: N=I-C_plus, so Delta_C=-A.

    No self-dual doubling factor or absolute Wick prescription is inferred.
    """
    value = _matrix(operator, "operator")
    if not _same(value, value.adjoint()):
        raise ValueError("ordered real observable requires a Hermitian operator")
    return sp.ImmutableMatrix(-value)


def pure_state_tangent_projection(
    kernel, covariance, *, conjugation, charge_grading, particle_family_projector
):
    """Optional local PURE tangent test on supplied mathematical inputs only.

    C X+X C=X adds the Grassmann tangent restriction. Zero at one C is only
    local stationarity and does not prove constancy across all pure states or
    distinct rank/charge components. The broad affine test chooses no C.
    """
    p, g, charge, family = _data(conjugation, charge_grading, particle_family_projector)
    c = _matrix(covariance, "covariance")
    if c.shape != g.shape or not _same(c, c.adjoint()) or not _same(c*c, c):
        raise ValueError("covariance must be a Hermitian pure projector of matching dimension")
    if not _same(c+g*c.conjugate()*g.adjoint(), sp.eye(c.rows)):
        raise ValueError("pure covariance must obey self-dual CAR")
    if not _zero(c*charge-charge*c) or not _zero(c*family-family*c):
        raise ValueError("pure covariance must preserve charge and family sectors")
    full = charged_nambu_tangent_projection(
        kernel, conjugation=g, charge_grading=charge, particle_family_projector=p)
    sensitivity = full["projected_kernel"]
    complement = sp.eye(c.rows)-c
    local = sp.ImmutableMatrix(c*sensitivity*complement+complement*sensitivity*c)
    return {
        "scope": "SUPPLIED_PURE_COVARIANCE_LOCAL_TANGENT_ONLY",
        "local_projected_kernel": local,
        "local_first_derivative_zero": _zero(local),
        "state_independence_over_all_pure_covariances_proved": False,
        "physical_covariance_selected": False,
    }
