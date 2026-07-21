"""BHSM v6.0.8 twistor-mediated Berger associated-bundle construction."""

from __future__ import annotations

import json
from math import comb
from pathlib import Path
from typing import Any, Iterable


VERSION = "v6.0.8"
SPRINT = "bhsm-twistor-mediated-berger-associated-bundle-v6-0-8"
PRIMARY_RESULT = "BHSM_BERGER_COVARIANT_MULTIPLET_ARCHITECTURE_DERIVED"
METRIC_RESULT = "BHSM_TWISTOR_MEDIATED_BERGER_METRIC_DERIVED"
LINEAR_RESULT = "BHSM_BERGER_COVARIANT_LINEAR_MULTIPLET_REDUCTION_DERIVED"
NONLINEAR_RESULT = "BHSM_GENERIC_NONLINEAR_FINITE_MULTIPLET_REQUIRES_TOWER"
ACTION_RESULT = "BHSM_TWISTOR_MEDIATED_REDUCTION_REQUIRES_ACTION_NORMALIZATION"

ARTIFACT_FILES = {
    "distributions": "BHSM_nested_global_distribution_theorem_v6_0_8.json",
    "reconstruction": "BHSM_twistor_mediated_s3_reconstruction_v6_0_8.json",
    "metric": "BHSM_global_nested_twistor_berger_metric_v6_0_8.json",
    "berger": "BHSM_twistor_berger_fiber_metric_recovery_v6_0_8.json",
    "hilbert": "BHSM_berger_fiberwise_hilbert_bundle_v6_0_8.json",
    "connection": "BHSM_associated_bundle_transition_connection_ledger_v6_0_8.json",
    "operator": "BHSM_berger_covariant_reduced_operator_v6_0_8.json",
    "closure": "BHSM_berger_finite_multiplet_closure_test_v6_0_8.json",
    "branching": "BHSM_so8_sp2_sp1_u1_branching_extension_v6_0_8.json",
    "action": "BHSM_twistor_berger_multiplet_action_reduction_v6_0_8.json",
    "v5": "BHSM_v5_berger_engine_global_reinterpretation_v6_0_8.json",
    "gauge": "BHSM_twistor_berger_gauge_forward_link_v6_0_8.json",
    "scalar": "BHSM_twistor_berger_scalar_topographic_forward_link_v6_0_8.json",
    "scale": "BHSM_twistor_berger_coefficient_scale_ledger_v6_0_8.json",
    "report": "BHSM_twistor_berger_associated_bundle_report_v6_0_8.json",
}

GUARDS = {
    "v6_0_7_topology_theorem_preserved": True,
    "section_of_cp3_to_s4_assumed": False,
    "u1_bundle_over_cp3_confused_with_reduction_over_s4": False,
    "s4_identified_as_physical_spacetime": False,
    "standard_model_gauge_group_derived": False,
    "physical_gauge_coupling_derived": False,
    "particle_or_generation_identification_made": False,
    "measured_input_used": False,
    "v5_number_used_as_parent_input": False,
    "absolute_scale_derived": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "full_bhsm_completion_claimed": False,
}


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "primary_result": PRIMARY_RESULT,
        "metric_result": METRIC_RESULT,
        "linear_multiplet_result": LINEAR_RESULT,
        "nonlinear_closure_result": NONLINEAR_RESULT,
        "action_result": ACTION_RESULT,
        "claim_boundary": (
            "The nested geometry, associated eigenspace bundles, scalar linear operator, "
            "and harmonic branching are mathematical constructions. Parent-action "
            "normalization, nonlinear effective closure, physical gauge interpretation, "
            "particle identification, and absolute units remain separate dependencies."
        ),
        **GUARDS,
    }


def nested_dimensions() -> tuple[int, int, int]:
    """Return ranks of H4, V2, and V1."""

    return (4, 2, 1)


def _positive_scales(*scales: float) -> None:
    if not scales or any(scale <= 0 for scale in scales):
        raise ValueError("all metric scales must be positive")


def berger_metric_coefficients(L2: float, L1: float) -> tuple[float, float, float]:
    _positive_scales(L2, L1)
    return (L2 * L2, L2 * L2, L1 * L1)


def berger_eigenvalue(two_j: int, weight: int, L2: float, L1: float) -> float:
    """Scalar Berger eigenvalue in d sigma_i=-epsilon_ijk sigma_j wedge sigma_k convention.

    ``two_j`` is twice the left spin and ``weight`` is the integral U(1)
    weight, equal to twice the right magnetic number.
    """

    _positive_scales(L2, L1)
    if not isinstance(two_j, int) or isinstance(two_j, bool) or two_j < 0:
        raise ValueError("two_j must be a nonnegative integer")
    if not isinstance(weight, int) or isinstance(weight, bool):
        raise ValueError("weight must be an integer")
    if abs(weight) > two_j or (two_j - weight) % 2:
        raise ValueError("weight must lie in -two_j,-two_j+2,...,two_j")
    j = two_j / 2.0
    m = weight / 2.0
    return j * (j + 1.0) / (L2 * L2) + m * m * (
        1.0 / (L1 * L1) - 1.0 / (L2 * L2)
    )


def mode_bundle_rank(two_j: int) -> int:
    if not isinstance(two_j, int) or isinstance(two_j, bool) or two_j < 0:
        raise ValueError("two_j must be a nonnegative integer")
    return two_j + 1


def sp2_dimension(a: int, b: int) -> int:
    """Dimension of the Sp(2) irrep with Dynkin labels (a,b)."""

    if any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in (a, b)):
        raise ValueError("Sp(2) Dynkin labels must be nonnegative integers")
    return (a + 1) * (b + 1) * (a + b + 2) * (a + 2 * b + 3) // 6


def s7_harmonic_dimension(ell: int) -> int:
    if not isinstance(ell, int) or isinstance(ell, bool) or ell < 0:
        raise ValueError("ell must be a nonnegative integer")
    trace = comb(ell + 5, 7) if ell >= 2 else 0
    return comb(ell + 7, 7) - trace


def branching_row(ell: int) -> dict[str, Any]:
    """Branch degree-ell round-S7 scalar harmonics under Sp(2) x Sp(1)."""

    total = s7_harmonic_dimension(ell)
    summands = []
    for r in range(ell // 2 + 1):
        a, b = ell - 2 * r, r
        sp1_highest_weight = a
        dim_sp2 = sp2_dimension(a, b)
        dim_sp1 = sp1_highest_weight + 1
        summands.append(
            {
                "sp2_dynkin": [a, b],
                "sp2_dimension": dim_sp2,
                "sp1_highest_weight": sp1_highest_weight,
                "sp1_dimension": dim_sp1,
                "u1_weights": list(range(-sp1_highest_weight, sp1_highest_weight + 1, 2)),
                "product_dimension": dim_sp2 * dim_sp1,
            }
        )
    return {
        "ell": ell,
        "so8_harmonic_dimension": total,
        "summands": summands,
        "branch_dimension_sum": sum(row["product_dimension"] for row in summands),
    }


def branching_table(max_ell: int = 6) -> list[dict[str, Any]]:
    if not isinstance(max_ell, int) or isinstance(max_ell, bool) or max_ell < 0:
        raise ValueError("max_ell must be a nonnegative integer")
    return [branching_row(ell) for ell in range(max_ell + 1)]


def nonlinear_closure_test(two_j_values: Iterable[int], polynomial_degree: int) -> dict[str, Any]:
    """Return the generic Clebsch-Gordan closure result for a retained spin set."""

    values = sorted(set(two_j_values))
    if not values or any(not isinstance(v, int) or isinstance(v, bool) or v < 0 for v in values):
        raise ValueError("at least one nonnegative integral two_j is required")
    if not isinstance(polynomial_degree, int) or isinstance(polynomial_degree, bool) or polynomial_degree < 1:
        raise ValueError("polynomial_degree must be a positive integer")
    maximum = values[-1]
    generated_maximum = polynomial_degree * maximum
    generic_exact_closure = maximum == 0 or polynomial_degree == 1
    return {
        "retained_two_j": values,
        "polynomial_degree": polynomial_degree,
        "generated_maximum_two_j": generated_maximum,
        "generic_exact_closure": generic_exact_closure,
        "reason": (
            "constants or a linear operator close exactly"
            if generic_exact_closure
            else "the highest Clebsch-Gordan channel exceeds the retained maximum"
        ),
    }


def distributions_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_nested_global_distribution_theorem_v6_0_8"),
        "status": "BHSM_NESTED_GLOBAL_4_2_1_DISTRIBUTION_DERIVED",
        "maps": {"p_C": "S7->CP3", "tau": "CP3->S4", "p_H": "tau o p_C"},
        "definitions": {
            "V1": "ker(dp_C), the global principal-U(1) vertical line",
            "V2": "the p_C-horizontal lift of ker(d tau), equivalently ker(dp_H) intersect V1-perp",
            "H4": "the orthogonal complement of V1 direct-sum V2 for the declared connection metric",
        },
        "ranks": {"H4": 4, "V2": 2, "V1": 1, "sum": 7},
        "splitting": "TS7=H4 direct-sum V2 direct-sum V1",
        "orthogonal": True,
        "double_counted_direction": False,
        "transition_laws": "V1 is U(1)-vertical; V2 is an associated two-plane; H4 is connection-horizontal; the full splitting is invariant under Sp(2)xU(1)_R",
        "integrability": {
            "V1": "integrable circle orbits",
            "V2": "not integrable alone: [V2,V2] has a V1 component",
            "V2_plus_V1": "integrable quaternionic Hopf S3 fibers",
            "H4": "generically nonintegrable; obstruction measured by the Sp(1) connection curvature",
        },
        "connection_curvature": "Omega=d omega+omega wedge omega, with nonzero c2 and horizontal bracket vertical part -Omega",
        "orientation": "vol7=vol_H4 wedge vol_V2 wedge eta, compatible with fiber-first pushforward after the declared sign",
        "global_section_required": False,
    }


def reconstruction_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_twistor_mediated_s3_reconstruction_v6_0_8"),
        "status": "BHSM_TWISTOR_MEDIATED_S3_RECONSTRUCTION_DERIVED",
        "base_point": "x in S4",
        "twistor_fiber": "S2_x=tau^-1(x)=Sp(1)/U(1)",
        "reconstructed_fiber": "F_x=p_C^-1(S2_x)",
        "identity": "F_x=p_C^-1(tau^-1(x))=(tau o p_C)^-1(x)=p_H^-1(x)",
        "diffeomorphism_type": "F_x isomorphic to Sp(1) isomorphic to S3",
        "restricted_fibration": "S1=U(1)->F_x=S3->S2_x=Sp(1)/U(1)",
        "operation_replaced": "choose one U(1) orbit in every S3 fiber",
        "valid_operation": "retain the complete S1-over-S2 Hopf fibration in every S3 fiber",
        "section_of_twistor_bundle_used": False,
    }


def metric_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_global_nested_twistor_berger_metric_v6_0_8"),
        "status": METRIC_RESULT,
        "metric": "g7=L4^2 g_H4+L2^2 g_V2+L1^2 eta^2",
        "domain": "L4>0, L2>0, L1>0",
        "global_reason": "H4,V2,V1 are global distributions on total S7 defined by the nested fibrations and canonical connections",
        "generic_invariance": "Sp(2)xU(1)_R",
        "enhancements": {
            "L1_equals_L2": "quaternionic vertical isotropy restores Sp(2)xSp(1) for the canonical-variation family",
            "round_normalized_point": "SO(8), after the fixed reference-metric normalizations also agree",
        },
        "cp3_role": "eta is the global U(1) connection form on S7->CP3, not a U(1) reduction over S4",
        "fiber_restriction": "g_Fx=L2^2 g_S2_x+L1^2 eta^2",
        "no_twistor_section": True,
        "scale_selection": "not supplied by topology or the metric ansatz",
    }


def berger_payload() -> dict[str, Any]:
    rows = []
    for two_j in range(5):
        for weight in range(-two_j, two_j + 1, 2):
            rows.append(
                {
                    "two_j": two_j,
                    "weight": weight,
                    "bundle_rank": mode_bundle_rank(two_j),
                    "eigenvalue_L2_L1_1": berger_eigenvalue(two_j, weight, 1.0, 1.0),
                }
            )
    return {
        **_common("BHSM_twistor_berger_fiber_metric_recovery_v6_0_8"),
        "status": "BHSM_TWISTOR_MEDIATED_BERGER_FIBER_OPERATOR_DERIVED",
        "fiber_metric": "g_Fx=L2^2(sigma1^2+sigma2^2)+L1^2 sigma3^2",
        "repository_map": {"r_base": "L2", "r_fiber": "L1"},
        "maurer_cartan": "d sigma1=-sigma2 wedge sigma3 cyclically",
        "scalar_eigenvalue": "lambda_(J,m)=J(J+1)/L2^2+m^2(1/L1^2-1/L2^2), with q=2m integral",
        "round_limit": "L1=L2=L gives lambda=J(J+1)/L^2=n(n+2)/(4L^2), n=2J",
        "symmetries": "left Sp(1) times right U(1); the right-U(1) weight commutes with the left multiplet action",
        "sample_round_rows": rows,
        "legacy_k_j_identification": "not asserted; the stored v5 label map still requires an intertwiner",
    }


def hilbert_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_berger_fiberwise_hilbert_bundle_v6_0_8"),
        "status": "BHSM_BERGER_FIBERWISE_HILBERT_BUNDLES_DERIVED",
        "fiber_space": "H_x=L2(F_x,dmu_Berger)",
        "peter_weyl_basis": "Y^J_(n,m), with n the left-Sp(1) component and m the commuting right-U(1) weight",
        "finite_eigenspace": "H_(J,m)(x)=span_n Y^J_(n,m), rank 2J+1 over C",
        "global_bundle": "mathcal H_(J,m)=S7 times_(rho_J) V_J -> S4",
        "intermediate_description": "right-U(1) weights are line-bundle labels over CP3; regrouping the left multiplet gives the Sp(1)-associated bundle over S4",
        "field_expansion": "Phi=sum_(J,m,n) phi^(J,m)_n(x) Y^J_(n,m)(y)",
        "coefficient_type": "section of mathcal H_(J,m), not an ordinary scalar unless J=0",
        "inner_product": "integral_Fx conjugate(Y_a)Y_b dmu_Fx=delta_ab",
        "reality": "for a real parent field, (J,m) and (J,-m) coefficients are paired by Wigner charge conjugation",
        "no_global_basis_required": True,
    }


def connection_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_associated_bundle_transition_connection_ledger_v6_0_8"),
        "status": "BHSM_BERGER_ASSOCIATED_TRANSITION_CONNECTION_DERIVED",
        "overlap": "s_b=s_a h_ab and g_b=h_ab^-1 g_a",
        "basis_transition": "Y_b=rho_J(h_ab^-1)Y_a in the declared column convention",
        "coefficient_transition": "phi_b=rho_J(h_ab^-1)phi_a, with the dual convention used if basis indices are lowered",
        "connection_transition": "A_b=h_ab^-1 A_a h_ab+h_ab^-1 d h_ab",
        "covariant_derivative": "D_A phi=d phi+rho_J*(A) phi",
        "curvature": "[D_mu,D_nu]phi=rho_J*(Omega_mu_nu)phi",
        "metric_compatibility": "rho_J is unitary and preserves the fiberwise inner product",
        "u1_weight_transport": "m is preserved because left Sp(1) transport commutes with the right U(1) Berger symmetry",
        "twistor_section_used": False,
    }


def operator_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_berger_covariant_reduced_operator_v6_0_8"),
        "status": "BHSM_BERGER_COVARIANT_SCALAR_OPERATOR_DERIVED",
        "hypotheses": ["constant positive L4,L2,L1", "declared connection metric", "totally geodesic Hopf fibers", "minimally coupled parent scalar for the exact E=0 statement"],
        "operator": "O_(J,m)=-D_A^*D_A+lambda_(J,m)(L1,L2)+E_(J,m)",
        "vertical_eigenvalue": "J(J+1)/L2^2+m^2(1/L1^2-1/L2^2)",
        "minimal_scalar_endomorphism": "E_(J,m)=0 beyond any explicit parent mass/potential Hessian",
        "general_endomorphism": "forms, spinors, nonminimal curvature couplings, and varying moduli produce action-specific Weitzenbock/O'Neill/curvature endomorphisms",
        "base_connection": "the Sp(1) Hopf connection acts in rho_J",
        "u1_role": "the right-U(1) weight enters the vertical spectrum and the CP3 intermediate description; it is not a U(1) reduction over S4",
        "uncoupled_scalar_required": False,
    }


def closure_payload() -> dict[str, Any]:
    examples = {
        "singlet_quartic_eom": nonlinear_closure_test([0], 3),
        "doublet_linear": nonlinear_closure_test([1], 1),
        "doublet_quadratic": nonlinear_closure_test([0, 1], 2),
        "spin_one_cubic": nonlinear_closure_test([0, 2], 3),
    }
    return {
        **_common("BHSM_berger_finite_multiplet_closure_test_v6_0_8"),
        "status": "BHSM_BERGER_COVARIANT_MULTIPLET_REDUCTION_DERIVED_CONDITIONALLY",
        "linear_operator": "each fixed (J,m) associated multiplet closes exactly",
        "connection_transport": "closes exactly in rho_J and preserves m",
        "nonlinear_rule": "V_J1 tensor V_J2 contains spins |J1-J2| through J1+J2 and right weights add",
        "generic_finite_nontrivial_polynomial_closure": False,
        "exact_reason": "a retained highest spin J>0 produces a higher highest-spin Clebsch-Gordan channel under generic products",
        "generic_requirement": "infinite harmonic tower",
        "constructive_routes": ["linear covariant multiplet theory", "action-selected vanishing overlap tensors", "spectral-gap controlled effective truncation", "adiabatic tower integration", "symmetry-protected finite sector"],
        "examples": examples,
        "standalone_scalar_failure_generalized_to_multiplets": False,
    }


def branching_payload() -> dict[str, Any]:
    rows = branching_table(8)
    return {
        **_common("BHSM_so8_sp2_sp1_u1_branching_extension_v6_0_8"),
        "status": "BHSM_SO8_HOPF_SCALAR_BRANCHING_FORMULA_DERIVED",
        "formula": "H^ell(R8)|_(Sp2 x Sp1)=direct-sum_(r=0..floor(ell/2)) V^(Sp2)_(ell-2r,r) tensor V^(Sp1)_(ell-2r)",
        "u1_branching": "V_n^(Sp1)|U1=direct-sum weights -n,-n+2,...,n",
        "sp2_dimension": "dim(a,b)=(a+1)(b+1)(a+b+2)(a+2b+3)/6",
        "rows": rows,
        "all_dimension_checks_pass": all(row["so8_harmonic_dimension"] == row["branch_dimension_sum"] for row in rows),
        "berger_splitting": "each U(1) weight acquires its exact squashing-dependent vertical eigenvalue",
        "associated_bundle_rank": "n+1 for the left Sp(1) multiplet H_(J,m), J=n/2",
        "physical_particle_map": None,
        "legacy_k_j_map": None,
    }


def action_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_twistor_berger_multiplet_action_reduction_v6_0_8"),
        "status": ACTION_RESULT,
        "parent": "provisional P1 Einstein-Hilbert plus declared scalar carrier; not promoted to the physical BHSM parent",
        "quadratic_scalar_reduction": "S2=1/2 sum_(J,m) integral_S4 [<D phi,D phi>+(M_parent^2+lambda_(J,m))<phi,phi>] dmu4 for a physical-fiber-orthonormal basis",
        "interaction_tensors": "C_(a1...ap)=integral_F Y_a1...Y_ap dmu_F, with representation and U(1)-weight selection rules",
        "fiber_measure": "physical orthonormal modes absorb Vol(F); normalized-Haar conventions instead expose an overall physical Vol(F)",
        "p1_geometry": ["base curvature term weighted by physical fiber volume", "intrinsic Berger curvature/squashing potential", "Sp(1) connection-curvature term from O'Neill tensors", "L1,L2 moduli kinetic terms when scales vary"],
        "p2_p3": "same multiplet architecture with higher curvature contractions; explicit coefficients remain unevaluated",
        "boundary_completion": "included only after a physical B8/spacetime boundary is selected; internal Hopf fibers are not boundaries",
        "v5_values_inserted": False,
        "parent_family_physically_selected": False,
    }


def v5_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_v5_berger_engine_global_reinterpretation_v6_0_8"),
        "status": "BHSM_V5_BERGER_ENGINE_FIBERWISE_ASSOCIATED_BUNDLE_REINTERPRETED",
        "classification": "exact intrinsic fiber metric/operator calculations plus local components of an associated-bundle operator; remaining phenomenological ledger maps stay effective",
        "translations": {
            "local_Berger_harmonic": "component of a section of mathcal H_(J,m)",
            "fiber_U1_label": "commuting covariant right-U(1) weight",
            "mode_degeneracy": "associated multiplet rank",
            "base_variation": "Sp(1)-connection transport",
        },
        "exact_fiberwise_portions": ["metric coefficient form", "volume and intrinsic curvature in the declared coframe", "Berger scalar spectral splitting once (J,m) are supplied"],
        "still_effective": ["legacy (k,j) to parent-representation map", "particle-sector labels", "dressing laws", "parent coefficient values"],
        "mode_ledgers_changed": False,
        "particle_interpretation_promoted": False,
    }


def gauge_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_twistor_berger_gauge_forward_link_v6_0_8"),
        "status": "BHSM_ASSOCIATED_CONNECTION_GAUGE_PRECURSOR_DERIVED",
        "base_transport_group": "Sp(1)",
        "base_curvature": "Omega with c2=1 in the declared orientation",
        "intermediate_circle_group": "U(1) on S7->CP3",
        "u1_curvature": "d eta representing the complex Hopf c1 after normalization",
        "representation_action": "rho_J*(A) on mathcal H_(J,m)",
        "weights": "right-U(1) integral weights -2J,-2J+2,...,2J",
        "kinetic_normalization_source": "symbolic P1 O'Neill/curvature reduction times parent kappa1, metric scales, physical fiber volume, and trace normalization",
        "standard_model_group_identification": None,
        "physical_coupling": None,
        "readiness": ["parent-derived connection kinetic action", "trace/charge normalization", "geometric aperture", "charged-current representation study"],
    }


def scalar_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_twistor_berger_scalar_topographic_forward_link_v6_0_8"),
        "status": "BHSM_SCALAR_TOPOGRAPHIC_ASSOCIATED_BUNDLE_DEPENDENCY_MAP_DERIVED",
        "trivial_mode": "(J,m)=(0,0) is an ordinary scalar singlet on S4",
        "metric_modes": {"squashing": "b=L1/L2", "fiber_volume": "L2^2 L1", "overall_nested_scale": "common scale of L4,L2,L1"},
        "existing_sigma_classification": "unresolved among singlet carrier, squashing modulus, volume modulus, boundary response, or a mixture",
        "v_red_target": "-sigma^2+2 sigma^4",
        "recovery_dependencies": ["parent field identification", "canonical kinetic normalization", "parent Hessian", "quartic overlap tensor", "metric-modulus mixing", "physical measure"],
        "v_red_recovered_without_fit": False,
        "sigma_vacuum_derived": False,
    }


def scale_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_twistor_berger_coefficient_scale_ledger_v6_0_8"),
        "status": "BHSM_TWISTOR_BERGER_DIMENSIONLESS_ARCHITECTURE_DERIVED_SCALE_OPEN",
        "dimensionless_ratios": ["b=L1/L2", "c=L2/L4", "L1/L4=bc", "vertical eigenvalue ratios", "representation weights"],
        "common_rescaling": "(L4,L2,L1)->alpha(L4,L2,L1)",
        "eigenvalue_scaling": "lambda_(J,m)->alpha^-2 lambda_(J,m)",
        "volume_scaling": "Vol(F)->alpha^3 Vol(F), Vol(S7)->alpha^7 Vol(S7)",
        "coefficient_sources": ["parent kappa_k", "physical fiber measure", "connection trace", "mode normalization", "overlap tensors", "metric ratios"],
        "normalization_bridge": "the v6.0.1 standard nested unit-volume convention and v6.0.7 repository Maurer-Cartan convention must be related explicitly before numeric parent coefficients are compared",
        "v5_numbers_on_parent_side": False,
        "absolute_unit_anchor": None,
    }


def report_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_twistor_berger_associated_bundle_report_v6_0_8"),
        "status": PRIMARY_RESULT,
        "central_answer": "The nested S1->S7->CP3 and S2->CP3->S4 fibrations construct a global Sp(2)xU(1)-invariant 4+2+1 geometry without a section of CP3->S4. Every quaternionic Hopf fiber is reconstructed as the complete S1->S3->S2 fibration and carries the repository Berger metric. Its fixed-(J,m) eigenspaces assemble into finite-rank Sp(1)-associated bundles over S4, on which the minimally coupled scalar operator is the base connection Laplacian plus the exact Berger eigenvalue. Round-S7 scalar harmonics obey a general Sp(2)xSp(1) branching formula. Linear multiplets close exactly; generic nonlinear polynomial products require a tower or an action-selected effective truncation. Thus the covariant multiplet architecture is derived and the next constructive dependency is parent-action normalization.",
        "architecture_selected": ["global nested fibrations", "Sp(2)xU(1) 4+2+1 metric", "fiberwise Berger eigenspace bundles", "covariant multiplet operator", "tower-aware effective action reduction"],
        "exact_results": ["nested distribution theorem", "S3 preimage identity", "Berger metric and scalar eigenvalues", "associated transition/connection law", "linear covariant closure", "general round-S7 scalar branching formula"],
        "conditional_results": ["P1 action reduction", "finite effective nonlinear truncation", "gauge kinetic normalization", "v5 coefficient recovery", "scalar/topographic identification"],
        "exact_constraints": ["no global fixed U(1) axis over S4", "nontrivial components are not global scalars", "generic nontrivial finite polynomial mode sets are not exactly closed", "ratios do not select an absolute scale"],
        "next_constructive_dependency": "derive the P1 connection, modulus, and overlap normalizations and test a spectral-gap controlled tower integration",
        "completion_gate": "V6_0_8_CONTINUE_TO_TWISTOR_BERGER_ACTION_NORMALIZATION",
        "recommended_next_branch": "bhsm-twistor-berger-action-normalization-v6-0-9",
    }


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    _ = repo_root
    return {
        "distributions": distributions_payload(),
        "reconstruction": reconstruction_payload(),
        "metric": metric_payload(),
        "berger": berger_payload(),
        "hilbert": hilbert_payload(),
        "connection": connection_payload(),
        "operator": operator_payload(),
        "closure": closure_payload(),
        "branching": branching_payload(),
        "action": action_payload(),
        "v5": v5_payload(),
        "gauge": gauge_payload(),
        "scalar": scalar_payload(),
        "scale": scale_payload(),
        "report": report_payload(),
    }


def materialize_artifacts(root: Path) -> list[Path]:
    target = root / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    payloads = build_artifact_payloads(root)
    written = []
    for key, filename in ARTIFACT_FILES.items():
        path = target / filename
        path.write_text(deterministic_json(payloads[key]), encoding="utf-8")
        written.append(path)
    return written


def twistor_berger_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    report = report_payload()
    report["artifacts"] = {key: f"artifacts/{name}" for key, name in ARTIFACT_FILES.items()}
    return report


def twistor_berger_status_to_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# BHSM v6.0.8 Twistor-Mediated Berger Associated-Bundle Construction",
            "",
            f"Primary constructive result: `{report['primary_result']}`.",
            f"Metric result: `{report['metric_result']}`.",
            f"Linear multiplet result: `{report['linear_multiplet_result']}`.",
            f"Action result: `{report['action_result']}`.",
            "",
            report["central_answer"],
            "",
            f"Next gate: `{report['completion_gate']}`.",
        ]
    ) + "\n"
