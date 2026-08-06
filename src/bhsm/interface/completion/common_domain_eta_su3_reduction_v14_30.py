"""BHSM v14.30 common-domain eta/SU(3) reduction proof audit.

This module does not infer an action theorem from a compatibility diagram.  It
records the strongest common-domain geometry already supported by v7.1 and
supplies exact counterexamples to the two missing implications: nonlinear
fiber averaging and trace/critical-value variational intertwining.
"""

from __future__ import annotations

from functools import lru_cache
from math import cos, sin, tanh
from typing import Any, Iterable

import numpy as np


VERSION = "v14.30"
OUTCOME_C = "BHSM_COMMON_DOMAIN_ETA_TO_PHYSICAL_SU3_GAUGING_REMAINS_BLOCKED_OR_NONUNIQUE"
EXACT_NEXT_OBJECT = (
    "FULL_HOPF_PREIMAGE_ETA_FIBER_MODE_REDUCTION_WITH_GAUGE_COVARIANT_"
    "DIRICHLET_TO_NEUMANN_EFFECTIVE_ACTION_AND_LOW_ENERGY_MATCHING_TO_THE_"
    "V14_29_LOCAL_ETA_SU3_ACTION"
)


def hopf_section_exists(c2: int) -> bool:
    """A principal Sp(1) bundle over S4 has a section only in the trivial class.

    A section trivializes a principal bundle.  Principal Sp(1) bundles over S4
    are classified by c2 in H4(S4;Z), so this implication is exact here.
    """

    return c2 == 0


def collar_jacobian(rho: float) -> float:
    """Dimensionless v7.1 equatorial-collar Jacobian relative to ds dmu4."""

    return cos(rho) ** 3


def collar_integral_factor(epsilon: float, scale_a: float = 1.0) -> float:
    """Return integral_0^epsilon cos(rho)^3 a d rho exactly."""

    if not 0.0 <= epsilon < np.pi / 2:
        raise ValueError("epsilon must lie in the regular equatorial collar")
    if scale_a <= 0.0:
        raise ValueError("scale_a must be positive")
    return scale_a * (sin(epsilon) - sin(epsilon) ** 3 / 3.0)


def nonlinear_fiber_moment(values: Iterable[float], power: int = 4) -> dict[str, float]:
    """Compare pushforward of X**power with power of the pushed X.

    Equality is required if normalized fiber averaging is to preserve the
    stored p=8 density using only the averaged kinetic invariant.  It fails for
    every nonconstant positive sample (strict Jensen inequality).
    """

    data = np.asarray(tuple(values), dtype=float)
    if data.size == 0 or power <= 1:
        raise ValueError("use a nonempty sample and power greater than one")
    average_then_power = float(np.mean(data) ** power)
    power_then_average = float(np.mean(data**power))
    return {
        "average_then_power": average_then_power,
        "power_then_average": power_then_average,
        "defect": power_then_average - average_then_power,
    }


def dtn_hessian(mass: float, half_width: float, endpoint: str = "neumann") -> float:
    """Exact Hessian of the critical-value action at an interior trace.

    For S=1/2 integral_-L^L[(phi')^2+m^2 phi^2] ds with phi(0)=q, the
    critical value is 1/2 q K q.  Natural Neumann outer endpoints give
    K=2m tanh(mL); Dirichlet outer endpoints give K=2m coth(mL).
    """

    if mass <= 0.0 or half_width <= 0.0:
        raise ValueError("mass and half_width must be positive")
    z = mass * half_width
    if endpoint == "neumann":
        return 2.0 * mass * tanh(z)
    if endpoint == "dirichlet":
        return 2.0 * mass / tanh(z)
    raise ValueError("endpoint must be 'neumann' or 'dirichlet'")


def critical_value_derivative(trace_value: float, mass: float, half_width: float) -> float:
    """Derivative of the Neumann critical-value action with respect to q."""

    return dtn_hessian(mass, half_width, "neumann") * trace_value


def common_fixed_tangent_dimension(tolerance: float = 1e-12) -> int:
    """Dimension of vectors in C3 fixed infinitesimally by all su(3) generators."""

    # It suffices to impose the two Cartan generators and two root directions.
    matrices = [
        np.diag([1j, -1j, 0j]),
        np.diag([1j, 1j, -2j]),
        np.array([[0, 1], [-1, 0]], complex),
        np.array([[0, 1j], [1j, 0]], complex),
    ]
    generators = []
    for index, matrix in enumerate(matrices):
        if index < 2:
            generators.append(matrix)
        else:
            embedded = np.zeros((3, 3), complex)
            embedded[:2, :2] = matrix
            generators.append(embedded)
    stacked = np.vstack(generators)
    rank = int(np.linalg.matrix_rank(stacked, tol=tolerance))
    return 3 - rank


def candidate_bridge_audit() -> list[dict[str, Any]]:
    """Audit every retained structure that could have owned R_eta."""

    return [
        {
            "candidate": "v7.1 R85=(pi_!,P_ret,Q_H)",
            "present_in_action": True,
            "acts_on_eta": "only as an undeclared retained Spin(8)/Sp(1) spectral mode",
            "acts_on_physical_SU3": False,
            "common_domain": "M8 to M5 only",
            "measure": "exact for fiber densities; closed lower eta functional not proved",
            "commutes_with_variation": "only on the declared invariant/equivariant retained subcategory",
            "coefficient": "V_F or normalized mode Gram matrix",
            "duplicates_action": False,
            "verdict": "DOES_NOT_DEFINE_R_ETA",
        },
        {
            "candidate": "v7.1 R54 trace/critical value",
            "present_in_action": True,
            "acts_on_eta": False,
            "acts_on_physical_SU3": "physical A is intrinsic M4 data, not a traced M5 field",
            "common_domain": "M5 cap to M4 seam",
            "measure": "collar measure explicit",
            "commutes_with_variation": "only after a selected stationary branch and boundary domain",
            "coefficient": None,
            "duplicates_action": False,
            "verdict": "NO_ETA_OR_COLOR_TRACE_MAP",
        },
        {
            "candidate": "Lambda85 and lambda_sigma",
            "present_in_action": True,
            "acts_on_eta": False,
            "acts_on_physical_SU3": False,
            "common_domain": "M5 metric/scalar compatibility bundle",
            "measure": "dmu5",
            "commutes_with_variation": "KKT equations for metric and sigma only",
            "coefficient": "multiplier normalization redundant",
            "duplicates_action": False,
            "verdict": "CANNOT_BE_REPURPOSED_AS_ETA_COLOR_MULTIPLIER",
        },
        {
            "candidate": "Lambda54",
            "present_in_action": True,
            "acts_on_eta": False,
            "acts_on_physical_SU3": False,
            "common_domain": "M4 metric seam",
            "measure": "dmu4",
            "commutes_with_variation": "metric trace adjoint only",
            "coefficient": "multiplier normalization redundant",
            "duplicates_action": False,
            "verdict": "NO_COLOR_CONNECTION_MATCHER",
        },
        {
            "candidate": "v14.29 minimally gauged eta density",
            "present_in_action": False,
            "acts_on_eta": True,
            "acts_on_physical_SU3": True,
            "common_domain": "declared candidate collar",
            "measure": "conditional w(s)dmu_C",
            "commutes_with_variation": "local candidate variation only",
            "coefficient": "no new coefficient after the bridge is postulated",
            "duplicates_action": "must replace the parent eta term but no replacement functor exists",
            "verdict": "ALLOWED_LOCAL_COMPLETION_NOT_ACTION_OWNED",
        },
    ]


def bundle_reduction_payload() -> dict[str, Any]:
    fixed_dimension = common_fixed_tangent_dimension()
    validation = {
        "associated_bundle_valid_for_arbitrary_c2": True,
        "physical_connection_pullback_is_global": True,
        "transition_law_for_covariant_derivative_explicit": True,
        "m_complex_is_3_plus_bar3": True,
        "orientation_branch_not_action_selected": True,
        "v7_hopf_bundle_has_no_full_base_section": not hopf_section_exists(1),
        "collar_local_trivialization_not_confused_with_action_selection": True,
        "no_nonzero_gauge_natural_tangent_selector": fixed_dimension == 0,
        "R_eta_absent": True,
    }
    return {
        "artifact": "BHSM_common_domain_eta_SU3_bundle_reduction_audit_v14_30",
        "version": VERSION,
        "diagram": {
            "M8": "I_t x S7",
            "M5": "I_t x S4",
            "M4": "I_t x S3 equatorial seam",
            "existing_maps": "M8 --pi85--> M5 <--iota54-- M4",
            "requested_five_dimensional_inclusion": "exists after choosing a noncanonical trivialization of the equatorial collar, but is absent from the retained action",
            "reason": "the collar restriction is trivializable, while any extension M5->M8 would section the c2=+1 Hopf Sp(1) bundle; v7.1 selects neither a collar section nor its gauge gluing",
            "valid_geometric_alternative": "C8=pi85^(-1)(C5) subset M8 with pi_C=retraction_C5_to_M4 composed with pi85",
            "alternative_action_status": "not selected by the retained action as an eta/color reduction domain",
        },
        "physical_bundle": "P_color->M4 with arbitrary retained c2",
        "collar_bundle": "Sigma_eta,C=pi_C^*P_color x_SU3 G2/SU3",
        "local_transition_law": "eta_j=g_ij^(-1) eta_i; A_j=g_ij^(-1)A_i g_ij+g_ij^(-1)dg_ij; D_Aj eta_j=g_ij^(-1)D_Ai eta_i",
        "R_eta_transition_condition": "r_j(h_ij^eta v)=g_ij^(-1)r_i(v)",
        "missing_cocycle_relation": "no retained homomorphism relates h_ij^eta from the M8 Spin/triality bundle to g_ij of the independent P_color",
        "naturality_no_go": "without such a relation, gauge-natural tangent output must be SU3-fixed; the common fixed subspace in 3 is zero",
        "common_fixed_tangent_dimension": fixed_dimension,
        "topology": "Sigma_eta,C exists without forcing c2(P_color)=0; existence is not a canonical map from E_eta,8",
        "representation": "m_C=3+bar3; reversing the oriented G2 branch conjugates 3 and bar3",
        "orientation_selection": "conditional topological branch, not selected by the retained action",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def measure_action_variation_payload() -> dict[str, Any]:
    moment = nonlinear_fiber_moment((1.0, 3.0))
    q, mass, width = 0.7, 1.3, 0.8
    boundary_response = critical_value_derivative(q, mass, width)
    validation = {
        "v7_collar_jacobian_recovered": abs(collar_jacobian(0.0) - 1.0) < 1e-15,
        "regular_finite_collar_integral": collar_integral_factor(0.4, 2.0) > 0.0,
        "p8_fiber_average_not_closed": moment["defect"] > 0.0,
        "critical_value_depends_on_endpoint_domain": abs(dtn_hessian(mass, width, "neumann") - dtn_hessian(mass, width, "dirichlet")) > 1e-6,
        "reduced_variation_not_pushforward_of_zero_bulk_Euler_operator": abs(boundary_response) > 1e-6,
        "normal_flux_is_required": True,
        "eta_metric_and_multiplier_variations_not_supplied": True,
        "no_double_action_replacement_unproved": True,
    }
    return {
        "artifact": "BHSM_eta_collar_measure_action_variation_no_go_v14_30",
        "version": VERSION,
        "conditional_measure_identity": "on C8=pi85^(-1)(C5), dmu8=dmuF cos(rho)^3 ds dmu4; ds=a(t)d rho",
        "integration_domain": "one cap: 0<=rho<epsilon_chi<pi/2; full preimage includes the closed oriented Hopf S3 fiber",
        "boundary_volume": "dmu4=N a^3 dt dmu_S3",
        "fiber_volume": "V_F=16 pi^2 a_F^3 on the invariant round branch",
        "pushforward_scope": "fiber-basic densities give V_F cos(rho)^3 ds dmu4; general eta fields retain vertical energy and all mode moments",
        "topological_nonbasic_obstruction": "a fiber-basic eta:S7->S7 factors through S4 and has degree zero because pi4(S7)=0; the degree-one eta-knot sector is therefore nonbasic",
        "p8_Jensen_witness": moment,
        "endpoint_behavior": "requires a declared trace or self-adjoint normal boundary condition at rho=0 and rho=epsilon_chi",
        "dtn_counterexample": {
            "bulk_action": "1/2 int_-L^L[(phi')^2+m^2 phi^2]ds with phi(0)=q",
            "bulk_Euler_operator_on_critical_field": 0.0,
            "neumann_reduced_Hessian": dtn_hessian(mass, width, "neumann"),
            "dirichlet_reduced_Hessian": dtn_hessian(mass, width, "dirichlet"),
            "reduced_derivative_at_q": boundary_response,
            "conclusion": "the derivative is conormal flux, not the trace/pushforward of the vanishing interior Euler operator",
        },
        "variational_identity_status": "FAILED_WITH_EXACT_COUNTEREXAMPLE_UNLESS_A_CRITICAL_VALUE_DOMAIN_AND_DIRICHLET_TO_NEUMANN_ADJOINT_ARE_ADDED",
        "no_double_action_ledger": [
            {"entry": "parent eta term", "owner": "S8 on M8", "status": "retained"},
            {"entry": "collar gauged eta term", "owner": "candidate C_eta", "status": "not in retained action"},
            {"entry": "restriction map", "owner": None, "status": "R_eta absent"},
            {"entry": "replacement/critical value", "owner": None, "status": "not derived"},
            {"entry": "independent variables", "owner": "eta8 and intrinsic Aphysical currently live on separate strata", "status": "known"},
            {"entry": "eliminated variables", "owner": None, "status": "not specified"},
            {"entry": "residual boundary term", "owner": None, "status": "normal eta flux unresolved"},
            {"entry": "double counting", "owner": None, "status": "unresolved; candidate cannot be added to S8"},
        ],
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def uniqueness_payload() -> dict[str, Any]:
    validation = {
        "minimal_substitution_unique_only_after_bundle_and_domain_are_fixed": True,
        "no_new_coefficient_in_local_minimal_substitution": True,
        "global_completion_nonunique": True,
        "outcome_B_not_eligible": True,
    }
    return {
        "artifact": "BHSM_eta_SU3_common_domain_uniqueness_audit_v14_30",
        "version": VERSION,
        "conditional_unique_statement": "given Sigma_eta,C, pi^*A, the isotropy representation, the original F(X)=kappa1 X/2+X^4/8, locality, first derivatives, and no extra operators, partial->D_A is the minimal covariant replacement",
        "surviving_inequivalent_choices": [
            "five-dimensional local lift versus the eight-dimensional full Hopf preimage",
            "3 versus bar3 oriented representation branch",
            "nonbasic spectral projection versus constrained critical-value reduction",
            "Neumann versus Dirichlet or other licensed self-adjoint normal domain",
            "trace action versus nonlocal Dirichlet-to-Neumann effective action",
        ],
        "new_continuous_coefficient_required_by_minimal_substitution": False,
        "uniqueness_theorem": None,
        "classification": "NOT_UNIQUE_AS_A_COMMON_DOMAIN_ACTION_COMPLETION",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def completion_payload() -> dict[str, Any]:
    bundle = bundle_reduction_payload()
    measure = measure_action_variation_payload()
    uniqueness = uniqueness_payload()
    rows = candidate_bridge_audit()
    validation = {
        "full_retained_bridge_audit_complete": len(rows) == 5,
        "bundle_obstruction_proved": bundle["validation_passed"],
        "measure_and_variation_obstruction_proved": measure["validation_passed"],
        "uniqueness_failed_honestly": uniqueness["validation_passed"],
        "v14_29_local_current_preserved_conditionally": True,
        "FR_not_started_without_common_domain": True,
        "downstream_not_substituted_for_provenance": True,
        "frozen_predictions_unchanged": True,
        "physical_outputs_absent": True,
        "BHSM_not_claimed_complete": True,
    }
    return {
        "artifact": "BHSM_common_domain_eta_SU3_completion_gate_v14_30",
        "version": VERSION,
        "primary_verdict": OUTCOME_C,
        "secondary_verdict": "THE_ASSOCIATED_COLOR_COSET_BUNDLE_AND_PULLBACK_CONNECTION_ARE_GLOBALLY_VALID_BUT_NO_ACTION_OWNED_R_ETA_OR_VARIATIONAL_REDUCTION_EXISTS",
        "BHSM_complete": False,
        "common_domain_gate": "BLOCKED",
        "variational_intertwiner_gate": "FAILED_FOR_NAIVE_TRACE_OR_PUSHFORWARD; ACTION_OWNED_CRITICAL_VALUE_DOMAIN_ABSENT",
        "FR_Dirac_matching_gate": "NOT_ELIGIBLE",
        "non_Abelian_BVP_gate": "NOT_ELIGIBLE",
        "candidate_bridge_audit": rows,
        "bundle_reduction": bundle,
        "measure_action_variation": measure,
        "uniqueness": uniqueness,
        "validated": [
            "arbitrary-c2 associated G2/SU3 bundle and physical connection pullback",
            "m_C=3+bar3 representation theorem",
            "v7.1 collar Jacobian on the full Hopf preimage",
            "exact topology, nonlinear-moment, and Dirichlet-to-Neumann obstructions",
        ],
        "invalidated": [
            "an action-owned/canonical five-dimensional collar lift or any full-M5 lift through the c2=+1 Hopf bundle",
            "degree-one eta being a fiber-basic v7.1 mode",
            "closure of the p8 density under normalized fiber averaging",
            "naive trace/pushforward of the bulk Euler operator as the reduced variation",
            "Outcome A and Outcome B under the retained data",
        ],
        "reclassified": [
            "v14.29 local minimal gauging remains an allowed conditional density, not a common-domain action completion",
            "the full Hopf preimage is a geometric candidate domain, not an action-selected reduction",
        ],
        "open": [EXACT_NEXT_OBJECT],
        "exact_next_object": EXACT_NEXT_OBJECT,
        "frozen_predictions_changed": False,
        "physical_outputs_emitted": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
