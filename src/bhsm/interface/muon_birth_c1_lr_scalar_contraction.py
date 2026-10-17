"""Exact consumed contractions on a supplied real-linear scalar response.

The operator must already contain the actual coupled Jacobi, boundary, gauge
and constraint rows in a common real pairing. This module does not assemble
or choose those physical operands, a scalar branch, or a pseudoinverse. An
exact finite null vector is an ambiguity witness only for the supplied rows;
it is not evidence of physical C1 underdetermination.
"""
from __future__ import annotations

import sympy as sp


SCOPE = "EXACT_SUPPLIED_FINITE_REAL_LINEAR_CONSTRAINED_CONTRACTION"


def _real_matrix(value, name):
    if value is None:
        raise ValueError(name+" is absent; no zero substitution is allowed")
    try:
        matrix = sp.ImmutableMatrix(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(name+" requires a nonempty exact real matrix") from exc
    if matrix.rows == 0 or matrix.cols == 0:
        raise ValueError(name+" requires a nonempty exact real matrix")
    if any(entry.is_Rational is not True for entry in matrix):
        raise ValueError(name+" requires exact real rational entries")
    return matrix


def _zero(value):
    return all(sp.expand(entry) == 0 for entry in value)


def _operands(response_operator, forcing, consumed_covector):
    operator = _real_matrix(response_operator, "response_operator")
    source = _real_matrix(forcing, "forcing")
    covector = _real_matrix(consumed_covector, "consumed_covector")
    if source.rows != operator.rows:
        raise ValueError("forcing must have one row per response equation")
    if covector.shape != (operator.cols, 1):
        raise ValueError("consumed_covector must be a column in the response dual")
    if operator.row_join(source).rank() != operator.rank():
        raise ValueError("forcing is inconsistent with the supplied constrained response")
    return operator, source, covector


def _certificate(operator, source, covector):
    """Use exact nullspace/adjoint elimination without choosing a primal state."""
    nullspace = tuple(sp.ImmutableMatrix(vector) for vector in operator.nullspace())
    couplings = tuple(sp.expand((covector.T*vector)[0]) for vector in nullspace)
    index = next((i for i, value in enumerate(couplings) if value != 0), None)
    common = dict(
        scope=SCOPE,
        response_rank=operator.rank(),
        supplied_response_nullity=len(nullspace),
        supplied_homogeneous_basis=nullspace,
        homogeneous_consumed_couplings=couplings,
        forcing_compatible=True,
        physical_C1_response_operator_evaluated=False,
        physical_C1_homogeneous_witness_certified=False,
        physical_C1_contraction=None,
        physical_scalar_branch_selected=False,
        pseudoinverse_used=False,
        primal_solution_selected=False,
    )
    if index is not None:
        witness = nullspace[index]
        return common | dict(
            classification="EXACT_SUPPLIED_FINITE_CONTRACTION_NOT_IDENTIFIED",
            contraction_identified=False,
            contraction_row=None,
            adjoint_family=None,
            adjoint_free_parameters=(),
            adjoint_homogeneous_basis=(),
            adjoint_pairing_invariant=None,
            homogeneous_witness=dict(
                vector=witness,
                equation_residual=operator*witness,
                contraction_difference=couplings[index],
            ),
        )
    # The entire adjoint affine family is retained. Its free parameters cancel
    # from p^T f because compatibility gives f in range(operator).
    family, parameters = operator.T.gauss_jordan_solve(covector)
    family = sp.ImmutableMatrix(family)
    row = sp.ImmutableMatrix((family.T*source).applyfunc(sp.expand))
    if row.free_symbols or not _zero(operator.T*family-covector):
        raise ValueError("Exact constrained adjoint certificate failed")
    adjoint_nullspace = tuple(sp.ImmutableMatrix(vector) for vector in operator.T.nullspace())
    if any(not _zero(vector.T*source) for vector in adjoint_nullspace):
        raise ValueError("Compatible forcing failed adjoint pairing invariance")
    return common | dict(
        classification="EXACT_SUPPLIED_FINITE_CONTRACTION_IDENTIFIED",
        contraction_identified=True,
        contraction_row=row,
        adjoint_family=family,
        adjoint_free_parameters=tuple(parameters),
        adjoint_homogeneous_basis=adjoint_nullspace,
        adjoint_pairing_invariant=True,
        homogeneous_witness=None,
    )


def constrained_scalar_contraction(response_operator, forcing, consumed_covector):
    """Return ell(h) iff every solution of A h=f gives the same value.

    For compatible f, identifiability is exactly ell|ker(A)=0, equivalently
    ell in range(A^T). Then A^T p=ell and ell(h)=p^T f even when both h and p
    are nonunique. Inconsistent f is rejected. All boundary/source equations
    must be supplied; an omitted physical row is not proved unnecessary here.
    """
    operator, source, covector = _operands(response_operator, forcing, consumed_covector)
    if source.cols != 1:
        raise ValueError("forcing must be one response equation column")
    result = _certificate(operator, source, covector)
    return result | dict(contraction=(result["contraction_row"][0]
                                     if result["contraction_identified"] else None))


def mixed_scalar_source_kernel(response_operator, source_forcing,
                               consumed_covector, explicit_source_kernel):
    """Evaluate direct+ell^T A^{-1} F without requiring an inverse of A.

    F supplies the signed forcing for each admissible source/covariance
    coordinate on the common real domain. Direct contacts are an explicit
    required row. With a singular A, all responses must be compatible and the
    consumed covector must annihilate the full homogeneous kernel. Otherwise
    the complete source kernel remains None with an exact finite witness.

    For constrained stationarity, A can be the Lagrangian KKT derivative,
    F=-[L_hC; R_C], ell=[L_hx; R_x], direct=L_xC. Multiplier curvature is part
    of L_hh; this function neither replaces it by A_action,hh nor zeroes rows.
    """
    operator, source, covector = _operands(response_operator, source_forcing, consumed_covector)
    direct = _real_matrix(explicit_source_kernel, "explicit_source_kernel")
    if direct.shape != (1, source.cols):
        raise ValueError("explicit_source_kernel must be one row over source coordinates")
    result = _certificate(operator, source, covector)
    induced = result["contraction_row"]
    return result | dict(
        explicit_source_kernel=direct,
        induced_source_kernel=induced,
        complete_source_kernel=(sp.ImmutableMatrix(direct+induced)
                                if result["contraction_identified"] else None),
        source_forcing_action_sign_inferred=False,
        physical_complete_E1_kernel=None,
        physical_CAR_verdict=None,
        physical_minimal_moment_rank=None,
    )


def scalar_adjoint_residual_bound(response_operator, forcing, consumed_covector,
                                  adjoint_candidate, response_norm_upper):
    """Conditional Euclidean enclosure for a supplied approximate adjoint.

    Given an independently valid ||h||<=B, r=ell-A^T p gives
    |ell(h)-p^T f|<=||r|| B. The caller's B is an explicit assumption here,
    not a bound obtained from the carrier or certified for the scalar domain.
    """
    operator, source, covector = _operands(response_operator, forcing, consumed_covector)
    if source.cols != 1:
        raise ValueError("forcing must be one response equation column")
    candidate = _real_matrix(adjoint_candidate, "adjoint_candidate")
    if candidate.shape != (operator.rows, 1):
        raise ValueError("adjoint_candidate must be a column in the equation dual")
    if response_norm_upper is None:
        raise ValueError("response_norm_upper is absent; no zero substitution is allowed")
    bound = sp.sympify(response_norm_upper)
    if bound.is_Rational is not True or bound < 0:
        raise ValueError("response_norm_upper must be an exact nonnegative rational")
    residual = sp.ImmutableMatrix(covector-operator.T*candidate)
    return dict(
        scope="CONDITIONAL_SUPPLIED_FINITE_REAL_ADJOINT_RESIDUAL_BOUND",
        adjoint_residual=residual,
        candidate_contraction=sp.expand((candidate.T*source)[0]),
        response_norm_upper_assumption=bound,
        absolute_contraction_error_upper=sp.sqrt((residual.T*residual)[0])*bound,
        supplied_response_norm_bound_certified=False,
        carrier_inverse_substituted_for_scalar_response=False,
        physical_C1_contraction=None,
        physical_scalar_error_enclosure=None,
    )


__all__ = ["constrained_scalar_contraction", "mixed_scalar_source_kernel",
           "scalar_adjoint_residual_bound"]
