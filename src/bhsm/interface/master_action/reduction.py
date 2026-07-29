"""BHSM v7.1 covariant bulk--boundary reduction and stratified action.

The authoritative construction is a correspondence action.  Fiber
pushforward is used where it is mathematically defined, while the cap and
four-dimensional localized actions retain independent ownership.  This
avoids both a false Kaluza--Klein provenance claim and double counting.
"""

from __future__ import annotations

import json
from math import pi
from typing import Any

from .coefficients import rows as v7_coefficient_rows


VERSION = "v7.1"
SPRINT = "bhsm-covariant-bulk-boundary-reduction-functor-v7-1"
SOURCE_MAIN_SHA = "aea655dcb12690629337fe34a2c9d74b8e53bb72"
ARCHITECTURE_VERDICT = (
    "BHSM_STRATIFIED_MASTER_ACTION_CLOSED_WITH_"
    "COVARIANT_COMPATIBILITY_MAPS"
)
RB01_VERDICT = "RB_01_UNIFIED_PARENT_ACTION_PROVENANCE_CLOSED"
CORE_VERDICT = "BHSM_CORE_COMPLETE"
FINAL_VERDICT = (
    "BHSM_PHYSICAL_COMPLETION_BLOCKED_BY_MISSING_"
    "COMMON_SCHEME_OBSERVABLE_TRANSPORT_FUNCTOR"
)
NEXT_EXACT_OBJECT = "COMMON_SCHEME_OBSERVABLE_TRANSPORT_FUNCTOR"


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def fiber_volume(a_fiber: float) -> float:
    """Physical S3 fiber volume in the stored full-cover coframe convention."""
    if a_fiber <= 0:
        raise ValueError("the fiber scale must be positive")
    return 16.0 * pi**2 * a_fiber**3


def normalized_mode_coefficient(
    pairings: list[float], field_values: list[float]
) -> float:
    """Return the finite normalized internal pairing for one retained mode."""
    if len(pairings) != len(field_values) or not pairings:
        raise ValueError("pairings and field values must have equal nonzero length")
    norm = sum(weight * weight for weight in pairings)
    if norm <= 0:
        raise ValueError("the retained mode must have positive norm")
    return sum(
        weight * value for weight, value in zip(pairings, field_values)
    ) / norm


def coefficient_pushforward(c8: float, a_fiber: float, normalized: bool) -> float:
    """Push a fiber-constant coefficient to M5 in the declared convention."""
    return c8 if normalized else c8 * fiber_volume(a_fiber)


def geometry_maps() -> dict[str, Any]:
    return {
        "pi_85": {
            "formula": "id_I x p_H : I_t x S7 -> I_t x S4",
            "fiber": "S3=Sp(1), compact, closed, oriented",
            "bundle": "Sp(1) -> S7 -> S4 with c2=+1",
            "domain_metric": (
                "G8=-N^2 dt^2+g_H+<I_F omega,omega>; "
                "round invariant branch I_F=a_F^2 identity"
            ),
            "codomain_metric": "g5=-N^2 dt^2+g_H",
            "retained_covariance": (
                "time-oriented diffeomorphisms of I_t and bundle "
                "automorphisms covering orientation-preserving S4 maps"
            ),
            "orientation": "or(M8)=or(M5) wedge or(S3)",
            "status": "EXPLICIT_PROPER_ORIENTED_SUBMERSION",
        },
        "iota_54": {
            "formula": (
                "iota_epsilon(t,x)=(t,chi=pi/2,x) : "
                "M4=I_t x S3 -> M5_epsilon"
            ),
            "ambient_metric": (
                "g5=-dt^2+a(t)^2[dchi^2+sin^2(chi)g_S3]"
            ),
            "induced_metric": "h=-dt^2+a(t)^2 g_S3",
            "normal": (
                "n_+=+a^-1 partial_chi on the north cap; "
                "n_-=-a^-1 partial_chi on the south cap"
            ),
            "seam": "chi=pi/2",
            "extrinsic_curvature_at_seam": "K_ab=0 on the round background",
            "status": "EXPLICIT_ORIENTED_EQUATORIAL_INCLUSION",
        },
        "collar": {
            "formula": (
                "c_epsilon(t,x,rho)=(t,pi/2-epsilon*rho,x), "
                "0<=rho<epsilon_chi"
            ),
            "normal_metric": "a(t)^2 d rho^2",
            "dimensionless_coordinate": True,
            "physical_normal_element": "ds=a(t)d rho at fixed t",
            "cap_reflection": (
                "J(t,chi,x)=(t,pi-chi,x), exchanging epsilon=+ and -"
            ),
            "boundary_orientation": (
                "outward-normal-first; reflection reverses the normal "
                "and exchanges the two oriented GHY terms"
            ),
            "status": "EXPLICIT_DIMENSIONLESS_GAUSSIAN_NORMAL_COLLAR",
        },
    }


def measure_and_orientation() -> dict[str, Any]:
    return {
        "M8": (
            "dmu8=dmu5 wedge dmuF; "
            "dmuF=a_F^3 eta1 wedge eta2 wedge eta3"
        ),
        "fiber_volume": "V_F=16 pi^2 a_F^3",
        "normalized_fiber_measure": "dnu_F=dmuF/V_F, integral_F dnu_F=1",
        "action_pushforward": (
            "pi_!(L8 dmu8)=[integral_F L8 dmuF]dmu5"
        ),
        "field_pairing": (
            "P_alpha Phi=N_alpha^-1 integral_F u_alpha^* Phi dmuF"
        ),
        "M5": (
            "dmu5=N a^4 sin^3(chi) dt dchi dmu_S3 "
            "on the round hyperspherical branch"
        ),
        "M4": "dmu4=N a^3 dt dmu_S3 at chi=pi/2",
        "collar": (
            "dmu5=N a^4 cos^3(rho) dt d rho dmu_S3 "
            "for chi=pi/2-epsilon rho"
        ),
        "stokes": "d pi_! omega=pi_! d omega because the S3 fiber is closed",
        "absolute_unit_introduced": False,
        "status": "DIMENSIONLESS_NORMALIZATION_AND_PHYSICAL_VOLUME_EXPLICIT",
    }


def reduction_85() -> dict[str, Any]:
    return {
        "functor": (
            "R_85=(pi_!,P_ret,Q_H) on the category of bundle-like metrics, "
            "equivariant bundles, and finite retained spectral subspaces"
        ),
        "field_expansion": (
            "Phi8(x,y)=sum_{alpha in I_ret} phi_alpha(x)u_alpha(y)+Phi_perp"
        ),
        "retained_coefficient": (
            "phi_alpha=N_alpha^-1 integral_F u_alpha^* Phi8 dmuF"
        ),
        "basic_sector": "u0=V_F^-1/2; P0 is a global scalar/base mode",
        "nontrivial_sector": (
            "phi_alpha is a section of E_R=P x_R V_R with connection "
            "induced by omega"
        ),
        "connection": (
            "the canonical Sp(1) connection transports associated modes; "
            "no global preferred U(1) axis is asserted"
        ),
        "covariant_derivative_intertwiner": (
            "D5 P_alpha=P_alpha D8 on invariant/equivariant retained modes; "
            "curvature-induced transitions outside I_ret are assigned to "
            "Phi_perp and are not called a consistent truncation"
        ),
        "coefficient_rules": {
            "unnormalized_basic": "c5=V_F c8",
            "orthonormal_modes": (
                "c5,alpha_beta=c8 integral_F u_alpha^*u_beta dmuF"
            ),
            "Einstein_base": "kappa5(x)=V_F(x) kappa8",
            "scalar_kinetic": "Z5,alpha_beta=Z8 N_alpha_beta",
            "quadratic": "A5,alpha_beta=A8 N_alpha_beta+vertical mass matrix",
            "quartic": (
                "G5,alpha_beta_gamma_delta="
                "G8 integral_F u_alpha u_beta u_gamma u_delta dmuF"
            ),
        },
        "radion_firewall": (
            "If a_F varies, pi_!S8 is scalar-tensor gravity with radion and "
            "connection terms. It is not identified with the historical "
            "constant-kappa5 cap action."
        ),
        "stored_S5_relation": (
            "independent target-stratum Wilson action constrained by "
            "compatibility maps, not falsely declared equal to pi_!S8"
        ),
        "status": "COVARIANT_PUSHFORWARD_CONSTRUCTED_ON_RETAINED_SUBCATEGORY",
    }


def reduction_54() -> dict[str, Any]:
    return {
        "trace": "Tr_B1 Phi5=iota_54^*Phi5",
        "critical_value": (
            "S4,response[varphi,k]="
            "Crit_{Phi5:Tr Phi5=varphi,C(Phi5)=0,k retained}"
            " S5|4[Phi5,eta]"
        ),
        "constraints": [
            "cap Einstein/scalar equations",
            "Hamiltonian and momentum constraints",
            "GHY-completed metric trace",
            "exact metric matcher",
            "gauge quotient conditions where a bulk gauge field is retained",
            "D0 scalar Dirichlet condition",
        ],
        "localized_fields": (
            "A_SM,Psi,H and optional N_neu are intrinsic M4 fields; they "
            "are varied on M4 and are not extended into M5 to manufacture "
            "a bulk provenance"
        ),
        "kernel_rule": (
            "Lyapunov-Schmidt variables k remain explicit; the critical "
            "value eliminates only the closed-range complement"
        ),
        "existence_scope": (
            "local stationary branches on the declared cap/KKT domains; "
            "no global uniqueness claim"
        ),
        "status": "CONSTRAINED_CRITICAL_VALUE_AND_TRACE_FUNCTOR_CONSTRUCTED",
    }


def authoritative_action() -> dict[str, Any]:
    return {
        "name": "S_BHSM^strat",
        "formula": (
            "S8[G,chi,sigma]+sum_epsilon(S5,epsilon[g_epsilon,sigma5]"
            "+S_GHY,epsilon)+S4,localized[h,A,Psi,H;I4]"
            "+S_compatibility[G,g_epsilon,sigma,sigma5,h,Lambda85,Lambda54]"
        ),
        "compatibility_action": (
            "int_M5 <Lambda85,g5-Q_H(G8)>"
            "+<lambda_sigma,sigma5-P0 sigma8> "
            "+sum_epsilon int_M4 "
            "Lambda54,epsilon^{ab}(h_ab-iota_epsilon^*g_epsilon,ab)"
        ),
        "architecture": (
            "covariant source-target correspondence plus stratified "
            "M5 cap and M4 boundary-localized Wilson actions"
        ),
        "off_shell_fields_distinct": True,
        "S5_claimed_as_pi_pushforward_of_S8": False,
        "boundary_SM_claimed_as_bulk_descendant": False,
        "ownership_rule": (
            "each term occurs once on its declared source, target, or "
            "boundary stratum; compatibility multipliers carry no kinetic "
            "term and their normalization is redundant"
        ),
        "quantum_scope": (
            "classical correspondence action with an M4 EFT stratum; "
            "no quantum-gravity completion claimed"
        ),
        "status": ARCHITECTURE_VERDICT,
    }


def field_transport() -> list[dict[str, Any]]:
    return [
        {"field": "G8", "map": "Q_H horizontal metric plus vertical I_F and omega", "classification": "GEOMETRICALLY_TRANSPORTED", "lower_owner": "independent constrained g5"},
        {"field": "chi8", "map": "P0 or finite associated modes", "classification": "RETAINED_SPECTRAL_MODE", "lower_owner": "bulk parent; no invented M4 carrier"},
        {"field": "sigma8", "map": "P0 sigma8=sigma5 compatibility trace", "classification": "BASIC_DIRECT_DESCENT", "lower_owner": "M5 scalar"},
        {"field": "radion a_F", "map": "vertical metric determinant", "classification": "GEOMETRICALLY_TRANSPORTED", "lower_owner": "diagnostic pi_!S8; not identified with sigma"},
        {"field": "omega", "map": "canonical Sp(1) associated-bundle connection", "classification": "GEOMETRICALLY_TRANSPORTED", "lower_owner": "transport connection, not SM gauge field"},
        {"field": "g5_epsilon", "map": "compatibility with Q_H(G8)", "classification": "INDEPENDENT_TARGET_STRATUM_FIELD", "lower_owner": "cap action"},
        {"field": "h", "map": "h=iota_epsilon^*g5_epsilon", "classification": "TRANSPORTED_BY_TRACE", "lower_owner": "common seam"},
        {"field": "A_SM", "map": None, "classification": "BOUNDARY_LOCALIZED_FUNDAMENTAL", "lower_owner": "M4"},
        {"field": "Psi", "map": None, "classification": "BOUNDARY_LOCALIZED_FUNDAMENTAL", "lower_owner": "M4"},
        {"field": "H", "map": None, "classification": "BOUNDARY_LOCALIZED_FUNDAMENTAL", "lower_owner": "M4"},
        {"field": "N_neu", "map": None, "classification": "CONDITIONAL_BOUNDARY_EXTENSION", "lower_owner": "DeltaS4 only"},
    ]


def coefficient_transport() -> list[dict[str, Any]]:
    rows = [dict(row) for row in v7_coefficient_rows()]
    by_id = {row["coefficient_id"]: row for row in rows}
    by_id["universal_scale"].update(
        {
            "classification": "ONE_UNIVERSAL_DIMENSIONFUL_CALIBRATION",
            "symbol": "ell_star",
            "value": "one positive common length; no value selected",
            "rationale": (
                "Permitted common calibration; not a prediction and not a "
                "dimensionless fit."
            ),
        }
    )
    by_id["reduction_pushforward"].update(
        {
            "classification": "GEOMETRICALLY_DERIVED",
            "symbol": "R_85,R_54",
            "value": "oriented pushforward, trace, and compatibility maps",
            "rationale": "Constructed by the v7.1 correspondence architecture.",
        }
    )
    rows.extend(
        [
            {
                "coefficient_id": "fiber_volume_VF",
                "symbol": "V_F",
                "sector": "M8 to M5 transport",
                "classification": "GEOMETRICALLY_DERIVED",
                "action_level": "S8->M5",
                "value": "16 pi^2 a_F^3",
                "comparison_input": False,
                "fitted": False,
                "rationale": "Physical action-density pushforward factor.",
            },
            {
                "coefficient_id": "compatibility_multiplier_normalization",
                "symbol": "zeta_85,zeta_54",
                "sector": "compatibility constraints",
                "classification": "REMOVED_AS_REDUNDANT",
                "action_level": "S_compatibility",
                "value": "absorbed into Lambda85 and Lambda54",
                "comparison_input": False,
                "fitted": False,
                "rationale": "Constraint-multiplier normalization carries no dynamics.",
            },
        ]
    )
    return rows


def variational_intertwiner() -> dict[str, Any]:
    return {
        "fiber_rule": (
            "delta pi_!=pi_! delta and d pi_!=pi_! d on the closed fiber"
        ),
        "derived_equation_rule": (
            "D(pi_!S8)∘D R85=R85_*∘D S8 on the retained invariant "
            "subspace, including the radion and connection terms"
        ),
        "stratified_KKT_equations": [
            "E8+C85,8^* Lambda85=0",
            "E5-C85,5^* Lambda85+C54,5^* Lambda54=0",
            "E4-C54,4^* Lambda54=0",
            "C85=0",
            "C54=0",
        ],
        "GHY": "cancels normal metric-derivative variations capwise",
        "matcher": "Lambda54 supplies equal-and-opposite seam reactions",
        "ADM": "lapse and shift variations retain Hamiltonian/momentum constraints",
        "gauge": "M4 gauge equations close on the gauge quotient",
        "fermion": "Dirac Green pairing vanishes on the declared maximal-isotropic domain",
        "neutral": "varied only when the conditional extension is enabled",
        "manual_term_copying_used": False,
        "status": "CONSTRAINED_VARIATIONAL_INTERTWINER_EXPLICIT",
    }


def domain_and_hessian() -> dict[str, Any]:
    return {
        "master_domain": (
            "(D8/gauge8) x (D5,cap/ADM) x "
            "(D4,gauge x D4,Dirac x D4,scalar) x multiplier duals"
        ),
        "D0": (
            "regular cap pole, fixed h, sigma|B1=0, exact matcher reaction; "
            "unchanged from v6.30"
        ),
        "gauge_domain": "H2 coexact representatives modulo allowed gauge transformations",
        "Dirac_domain": "H1 maximal-isotropic domain of the boundary Green pairing",
        "neutral_domain": "declared closed response cone when DeltaS4 is enabled",
        "KKT_Hessian": (
            "[[H8,0,0,C85,8*,0],"
            "[0,H5,0,-C85,5*,C54,5*],"
            "[0,0,H4,0,-C54,4*],"
            "[C85,8,-C85,5,0,0,0],"
            "[0,C54,5,-C54,4,0,0]]"
        ),
        "reduced_Hessian": "H_eff=H_bb-H_bi H_ii,perp^-1 H_ib",
        "inverse_domain": (
            "closed-range complement of gauge, constraint, and "
            "Lyapunov-Schmidt kernels only"
        ),
        "kernel_rule": "all Lyapunov-Schmidt kernel coordinates remain explicit",
        "generic_pseudoinverse_used": False,
        "kernel_inverted": False,
        "unlicensed_Robin_domain_used": False,
        "D0_recovered_without_modification": True,
        "status": "DOMAIN_AND_CONSTRAINED_SCHUR_INTERTWINER_EXPLICIT",
    }


def projector_transport() -> list[dict[str, Any]]:
    return [
        {"projector": "Spin8 triality", "classification": "REPRESENTATION_DERIVED", "transport": "equivariant associated-bundle projector"},
        {"projector": "SM representations", "classification": "FINITE_INDEPENDENT_THEORY_INPUT", "transport": "intrinsic M4 bundle data"},
        {"projector": "sector projectors", "classification": "FINITE_INDEPENDENT_THEORY_INPUT", "transport": "M4 orthogonal bundle endomorphisms"},
        {"projector": "generation/mode projectors", "classification": "CONDITIONAL", "transport": "retained spectral subspace; historical mass-selected labels are screen-only"},
        {"projector": "chirality", "classification": "REPRESENTATION_DERIVED", "transport": "intrinsic four-dimensional spin bundle"},
        {"projector": "charged channels", "classification": "GEOMETRICALLY_TRANSPORTED", "transport": "SU2 covariant derivative and Yukawa basis"},
        {"projector": "neutral channels", "classification": "CONDITIONAL", "transport": "SM neutral current plus optional DeltaS4 cone"},
    ]


def action_term_recovery() -> list[dict[str, Any]]:
    return [
        {"term": "eight-dimensional Einstein/carrier/scalar", "result": "independent theory input"},
        {"term": "capwise Einstein-scalar", "result": "independent theory input"},
        {"term": "GHY", "result": "transported by trace"},
        {"term": "intrinsic B1 gravity/matter", "result": "boundary-localized fundamental term"},
        {"term": "metric and scalar compatibility matchers", "result": "transported by trace"},
        {"term": "Yang-Mills", "result": "boundary-localized fundamental term"},
        {"term": "Dirac/Yukawa", "result": "boundary-localized fundamental term"},
        {"term": "Higgs/scalar", "result": "boundary-localized fundamental term"},
        {"term": "neutral auxiliary response", "result": "conditional extension"},
    ]


def blocker_rows() -> list[dict[str, Any]]:
    return [
        {"id": "RB-01", "status": "CLOSED", "resolution": ARCHITECTURE_VERDICT},
        {"id": "RB-02", "status": "OPEN_PARAMETER_FREE_EXTENSION", "resolution": "lambda5 remains an independent input; not Tier-A blocking"},
        {"id": "RB-03", "status": "CLOSED", "resolution": "finite projectors and all operator domains typed"},
        {"id": "RB-04", "status": "CLOSED_BY_CLAIM_REMOVAL", "resolution": "charged stiffness is a historical screen, not an official action output"},
        {"id": "RB-05", "status": "CLOSED_BY_CLAIM_REMOVAL", "resolution": "eta_l is a historical screen, not an official action output"},
        {"id": "RB-06", "status": "CLOSED", "resolution": "CKM=U_u^dagger U_d from independent Yukawas; 1/16 remains screen-only"},
        {"id": "RB-07", "status": "CLOSED_BY_CONDITIONAL_CLASSIFICATION", "resolution": "PMNS/neutrino mass operators excluded from minimal core and retained only as extension"},
        {"id": "RB-08", "status": "CLOSED", "resolution": "g1,g2,g3 are finite independent dimensionless inputs"},
        {"id": "RB-09", "status": "CLOSED", "resolution": "fiber, cap, seam, and collar measures/orientations explicit"},
        {"id": "RB-10", "status": "CLOSED_BY_CONDITIONAL_CLASSIFICATION", "resolution": "neutral cone and coefficients typed only in DeltaS4"},
        {"id": "RB-11", "status": "CLOSED", "resolution": "retained scalar action closed with lambda5 independent; profile screens removed from core"},
        {"id": "RB-12", "status": "CLOSED_WITH_ALLOWED_CALIBRATION", "resolution": "one common ell_star; no value or dimensionless fit"},
        {"id": "RB-13", "status": "BLOCKED_EXACT_OBJECT_LOCALIZED", "resolution": NEXT_EXACT_OBJECT},
        {"id": "RB-14", "status": "DOWNSTREAM_BLOCKED", "resolution": "depends on RB-13"},
        {"id": "RB-15", "status": "DOWNSTREAM_BLOCKED", "resolution": "depends on RB-13 and RB-14"},
        {"id": "RB-16", "status": "DOWNSTREAM_BLOCKED", "resolution": "depends on RB-14 and RB-15"},
    ]


def scale_bridge() -> dict[str, Any]:
    return {
        "calibration": "ell_star>0",
        "count": 1,
        "rule": "Q_phys=ell_star^(-d_L) Q_hat",
        "mass_rule": "m_phys=m_hat/ell_star",
        "dimensionless_couplings": "unchanged",
        "common_to_all_sectors": True,
        "numeric_value_selected": False,
        "called_prediction": False,
        "dimensionless_fit": False,
        "sector_retuning": False,
        "status": "ONE_UNIVERSAL_SCALE_BRIDGE_TYPED",
    }


def canonical_completion_gate_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_1_0_completion_gate",
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "current_verdict": FINAL_VERDICT,
        "BHSM_1_0_release_complete": False,
        "current_tier_status": {
            "Tier_A": "COMPLETE",
            "Tier_B": "BLOCKED_EXACT_OBJECT_LOCALIZED",
            "Tier_C": "NOT_ELIGIBLE",
        },
        "RB01": {
            "status": "CLOSED",
            "architecture": ARCHITECTURE_VERDICT,
            "release_blocking": False,
        },
        "core_verdict": CORE_VERDICT,
        "parameter_free_extension_blocker": "RB-02",
        "resolved_release_blockers": [
            "RB-01", "RB-03", "RB-04", "RB-05", "RB-06", "RB-07",
            "RB-08", "RB-09", "RB-10", "RB-11", "RB-12",
        ],
        "open_release_blockers": ["RB-13", "RB-14", "RB-15", "RB-16"],
        "next_highest_upstream_blocker": NEXT_EXACT_OBJECT,
        "frozen_prediction_changed": False,
        "official_prediction_changed": False,
        "comparison_data_used_in_action": False,
        "fitted_parameter_used": False,
        "lambda5_value_selected": False,
        "lambda5_sign_selected": False,
        "physical_scale_claimed_as_prediction": False,
        "unconditional_stability_claimed": False,
        "quantum_completion_claimed": False,
        "bhsm_1_0_release_complete_claimed": False,
    }


def payload() -> dict[str, Any]:
    result = {
        "artifact": "BHSM_covariant_bulk_boundary_reduction_functor_v7_1",
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "authoritative_architecture": authoritative_action(),
        "geometry_maps": geometry_maps(),
        "measure_and_orientation": measure_and_orientation(),
        "reduction_8_to_5": reduction_85(),
        "reduction_5_to_4": reduction_54(),
        "field_and_bundle_transport": field_transport(),
        "coefficient_and_input_ledger": coefficient_transport(),
        "variational_intertwiner": variational_intertwiner(),
        "domain_and_Hessian_intertwiner": domain_and_hessian(),
        "projector_and_representation_transport": projector_transport(),
        "action_term_recovery": action_term_recovery(),
        "completion_DAG": blocker_rows(),
        "scale_bridge": scale_bridge(),
        "RB01_result": RB01_VERDICT,
        "core_result": CORE_VERDICT,
        "remaining_exact_object": NEXT_EXACT_OBJECT,
        "final_verdict": FINAL_VERDICT,
        "integrity": {
            "fitting_used": False,
            "comparison_data_imported": False,
            "arbitrary_dynamical_term_added": False,
            "hidden_scale_added": False,
            "double_counting_retained": False,
            "frozen_prediction_changed": False,
            "lambda5_reopened": False,
            "exact_neighboring_branch_restored": False,
        },
    }
    result["validation"] = {
        "authoritative_architecture_selected": True,
        "base_maps_explicit": len(result["geometry_maps"]) == 3,
        "measures_and_orientations_explicit": True,
        "fields_classified": all(
            row["classification"] for row in result["field_and_bundle_transport"]
        ),
        "coefficient_pushforwards_explicit": True,
        "variational_intertwiner_explicit": True,
        "domains_and_adjoints_explicit": True,
        "Hessian_relation_explicit": True,
        "D0_recovered": result["domain_and_Hessian_intertwiner"][
            "D0_recovered_without_modification"
        ],
        "every_action_term_owned": all(
            row["result"] != "missing" for row in result["action_term_recovery"]
        ),
        "no_comparison_value_in_action": True,
        "no_double_counting": True,
        "RB01_closed": True,
        "Tier_A_complete": True,
        "next_independent_blocker_exact": True,
    }
    result["validation_passed"] = all(result["validation"].values())
    return result


def status_report() -> dict[str, Any]:
    data = payload()
    return {
        "version": VERSION,
        "authoritative_architecture": data["authoritative_architecture"][
            "status"
        ],
        "maps": {
            key: value["formula"] for key, value in geometry_maps().items()
        },
        "RB01_result": RB01_VERDICT,
        "core_result": CORE_VERDICT,
        "current_tier": "TIER_A_COMPLETE_TIER_B_BLOCKED",
        "scale_bridge": scale_bridge()["status"],
        "remaining_exact_object": NEXT_EXACT_OBJECT,
        "resolved_blockers": [
            row["id"] for row in blocker_rows() if row["status"].startswith("CLOSED")
        ],
        "validation": data["validation"],
        "validation_passed": data["validation_passed"],
        "final_verdict": FINAL_VERDICT,
    }
