"""Exact local seam diagnostics for the already selected minimal area action.

These calculations audit conditional trace relations on a regular stratum.
They do not instantiate a physical carrier, attachment, or full-field domain.
"""

from __future__ import annotations

from typing import Any

import sympy as sp

from bhsm.interface.covariant_bubble_interface_mechanics import ACTION_VERSION


AUDIT_VERSION = "COVARIANT-INTERFACE-SEAM-SELECTION-AUDIT-1"
STATUS = "REGULAR_SEAM_VARIATION_AND_CONDITIONAL_LOCAL_SELECTION_AUDITED"
METRIC = sp.diag(-1, 1, 1)


def _rational_matrix(value: Any, shape: tuple[int, int]) -> sp.Matrix:
    """Accept exact rational data, without floating-point rank decisions."""
    matrix = sp.Matrix(value)
    if matrix.shape != shape or any(not entry.is_Rational for entry in matrix):
        raise ValueError(f"expected an exact rational matrix of shape {shape}")
    return matrix


def lorentz_generators() -> tuple[sp.Matrix, ...]:
    """Return the (01 boost, 02 boost, 12 rotation) basis of so(1,2)."""
    return (
        sp.Matrix([[0, 1, 0], [1, 0, 0], [0, 0, 0]]),
        sp.Matrix([[0, 0, 1], [0, 0, 0], [1, 0, 0]]),
        sp.Matrix([[0, 0, 0], [0, 0, 1], [0, -1, 0]]),
    )


def maxwell_selection_jacobian(curvature: Any, flux_covector: Any) -> sp.Matrix:
    """Linearize preservation of f and oriented, lowered canonical flux e.

    Columns are relative Lorentz parameters; rows are (df01, df02, df12,
    de0, de1, de2). The identity denotes a known reference matching only.
    """
    field = _rational_matrix(curvature, (3, 3))
    flux = _rational_matrix(flux_covector, (3, 1))
    if field.T != -field:
        raise ValueError("tangential curvature must be antisymmetric")
    columns = []
    for generator in lorentz_generators():
        variation = generator.T * field + field * generator
        columns.append(sp.Matrix([
            variation[0, 1], variation[0, 2], variation[1, 2],
            *(generator.T * flux),
        ]))
    return sp.Matrix.hstack(*columns)


def maxwell_map_work_covector(curvature: Any, flux_covector: Any) -> sp.Matrix:
    """Return f_ba p^a, the isolated Maxwell relative-map work coefficient.

    This is a stationarity condition only for arbitrary admissible map
    variations after Gauss reduction, with geometry and other terms fixed.
    """
    field = _rational_matrix(curvature, (3, 3))
    flux = _rational_matrix(flux_covector, (3, 1))
    if field.T != -field:
        raise ValueError("tangential curvature must be antisymmetric")
    return field * METRIC.inv() * flux


def cotangent_gluing_graph(transport: Any) -> sp.Matrix:
    """Parameterize q_e=C q_c, p_c=-C.T p_e on finite reduced spaces.

    Row order is (q_e,p_e,q_c,p_c); free coordinates are (q_c,p_e).
    This finite canonical lemma does not construct the physical reduction.
    """
    matrix = sp.Matrix(transport)
    if matrix.rows < 1 or matrix.rows != matrix.cols:
        raise ValueError("transport must be a nonempty square matrix")
    matrix = _rational_matrix(matrix, matrix.shape)
    if matrix.det() == 0:
        raise ValueError("attachment transport must be invertible")
    identity, zero = sp.eye(matrix.rows), sp.zeros(matrix.rows)
    return sp.Matrix.vstack(
        sp.Matrix.hstack(matrix, zero), sp.Matrix.hstack(zero, identity),
        sp.Matrix.hstack(identity, zero), sp.Matrix.hstack(zero, -matrix.T),
    )


def _matrix_json(matrix: sp.Matrix) -> list[list[str]]:
    return [[str(entry) for entry in row] for row in matrix.tolist()]


def _rank_case(field: sp.Matrix, flux: sp.Matrix) -> dict[str, Any]:
    jacobian = maxwell_selection_jacobian(field, flux)
    work = maxwell_map_work_covector(field, flux)
    return {
        "tangential_curvature": _matrix_json(field),
        "lowered_oriented_canonical_flux": _matrix_json(flux),
        "jacobian": _matrix_json(jacobian),
        "exact_rank": jacobian.rank(),
        "kernel_dimension": 3 - jacobian.rank(),
        "kernel_basis": [_matrix_json(vector) for vector in jacobian.nullspace()],
        "isolated_Maxwell_map_work_covector": _matrix_json(work),
        "isolated_Maxwell_free_map_stationary": work == sp.zeros(3, 1),
    }


def build_payload() -> dict[str, Any]:
    """Evaluate exact illustrative diagnostics with explicit claim limits."""
    field = sp.Matrix([[0, 1, 0], [-1, 0, 0], [0, 0, 0]])
    independent_flux = sp.Matrix([0, 2, 0])
    reference = sp.Matrix([
        [sp.Rational(5, 3), sp.Rational(4, 3), 0],
        [sp.Rational(4, 3), sp.Rational(5, 3), 0], [0, 0, 1],
    ])
    graph = cotangent_gluing_graph(reference.T)
    canonical = sp.Matrix.vstack(
        sp.Matrix.hstack(sp.zeros(3), sp.eye(3)),
        sp.Matrix.hstack(-sp.eye(3), sp.zeros(3)),
    )
    cases = {
        "zero_traces": _rank_case(sp.zeros(3), sp.zeros(3, 1)),
        "curvature_only": _rank_case(field, sp.zeros(3, 1)),
        "aligned_nonzero_flux": _rank_case(field, sp.Matrix([0, 0, 1])),
        "independent_nonzero_flux": _rank_case(field, independent_flux),
    }
    return {
        "artifact": "BHSM_COVARIANT_INTERFACE_SEAM_SELECTION_AUDIT",
        "audit_version": AUDIT_VERSION,
        "action_version": ACTION_VERSION,
        "status": STATUS,
        "classification": "DERIVED_VARIATION_WITH_CONDITIONAL_EXACT_LOCAL_WITNESSES",
        "domain": {
            "stratum": "one regular timelike hypersurface in a four-dimensional stratum",
            "signature": "h=diag(-1,1,1), spacelike outward unit normals",
            "corner_ensemble": "compactly supported variations or fixed corner data",
            "physical_geometry_solved": False,
            "pregeometric_membrane_variables_introduced": False,
        },
        "selected_area_variation": {
            "action": "S_Sigma=-integral gamma sqrt(-det h)",
            "metric_variation": "delta S_Sigma=-integral gamma h^(ab) delta h_ab/2 dmu_h",
            "fixed_gamma_embedding_variation": "delta S_Sigma=integral gamma H_mu V^mu dmu_h + corner",
            "fixed_geometry_direct_F_B_derivative": "0",
            "fixed_geometry_direct_L_s_derivative": "0",
            "direct_gauge_trace_source": "0",
            "meaning": "partial derivatives of the selected density, not total constrained derivatives",
            "generic_no_go": False,
        },
        "Maxwell_boundary_variation": {
            "factored_normalization": "positive action-owned g^(-2), no numerical coupling chosen",
            "canonical_flux": "p^a=-g^(-2) n_mu F^(mu a)",
            "boundary_one_form": "integral p^a delta a_a dmu_h",
            "conditional_trace_glue": "a_e=C(F_B)a_c modulo admitted gauge",
            "conditional_flux_glue": "p_c+C(F_B)^*p_e=0",
            "map_variation": "<p_e,D_F C(F_B)[eta] a_c>",
            "Cartan_identity": "L_eta a=i_eta f+d(i_eta a)",
            "after_Gauss_and_corner_reduction": "integral p^a f_ba eta^b dmu_h",
            "missing_coupled_terms": "shape, other-sector, environment and admissibility-constraint terms",
            "unrestricted_independent_traces_alternative": "p_e=p_c=0 in this gauge-only sector",
            "trace_domain_selected_by_area_alone": False,
        },
        "rank_scope": {
            "unknowns": "three infinitesimal relative SO+(1,2) parameters at one known matching",
            "not_counted": "translations, map integrability, embeddings, gauge/spin lift, physical domains",
            "empirical_comparison": None,
            "relative_error": None,
            "arithmetic": "exact rational SymPy matrices; no rank tolerance",
            "inputs_are_physical_BHSM_traces": False,
        },
        "rank_cases": cases,
        "nonzero_Maxwell_realization": {
            "ambient_metric": "diag(-1,1,1,1) in (t,x,y,z)",
            "seam": "z=0; event outward normal +dz",
            "potential": "A=(t-2z) dx",
            "curvature": "F=dt wedge dx-2 dz wedge dx",
            "source_free": "constant F: dF=0 and partial_mu F^(mu nu)=0",
            "half_F_munu_F_up_munu": "3",
            "factored_lowered_event_flux": "(0,2,0)",
            "coupled_interface_solution": False,
            "isolated_free_map_stationarity_passed": False,
            "why_not_stationary": "f_ba p^a=(2,0,0), so additional coupled terms or restrictions are required",
        },
        "nonidentity_reference_check": {
            "reference_differential": _matrix_json(reference),
            "preserves_metric": reference.T * METRIC * reference == METRIC,
            "determinant": str(reference.det()),
            "curvature_residual": _matrix_json(reference.T * field * reference - field),
            "transported_oriented_flux": _matrix_json(reference.T * independent_flux),
            "identity_flux_residual_against_reference": _matrix_json(
                independent_flux - reference.T * independent_flux
            ),
            "physical_identity_attachment_selected": False,
        },
        "conditional_Lagrangian_graph": {
            "reduced_trace_dimension_per_side": 6,
            "product_dimension": 12,
            "graph_dimension": graph.rank(),
            "restricted_Green_form": _matrix_json(graph.T * sp.diag(canonical, canonical) * graph),
            "physical_reduced_trace_space_constructed": False,
            "physical_L_s_selected": False,
        },
        "VALIDATED": [
            "fixed-geometry area density has zero direct F_B, L_s and gauge-trace derivative",
            "Maxwell boundary and relative-map work terms survive in the total first variation",
            "conditional cotangent transmission graph is Lagrangian on specified finite reduced spaces",
            "nonzero Maxwell traces can algebraically remove three relative Lorentz directions",
            "full-rank illustrative traces fail isolated free-map stationarity and cannot be promoted",
        ],
        "INVALIDATED": [
            "zero direct area derivatives imply total attachment variation vanishes",
            "area density by itself chooses the admissible gauge trace domain",
            "pointwise rank three alone proves a physical attachment or interface solution",
            "matching only tangential curvature certifies complete Maxwell transport",
        ],
        "OPEN": [
            "instantiate action-owned constrained seam trace and embedding domain",
            "evaluate complete reduced stationarity and rank on action-owned nonzero fields",
            "construct coupled interface IVP, first crossing, global F_B and spin/bundle reset",
        ],
        "exact_next_object": (
            "ACTION_OWNED_ADMISSIBLE_SEAM_DOMAIN_AND_COMPLETE_REDUCED_STATIONARITY_"
            "JACOBIAN_ON_NONZERO_PHYSICAL_TRACES"
        ),
        "N12": {"new_independent_rank": 0, "Gate7_result_imported": False},
        "FULL_BHSM_COMPLETE": False,
    }
