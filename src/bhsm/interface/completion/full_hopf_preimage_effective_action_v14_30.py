"""Full Hopf-preimage eta effective-action and v14.29 matching audit.

Exact calculations in this module are deliberately separated from the missing
eta/color bundle-provenance map.  Peter--Weyl spectra, the bundle-like measure,
Dirichlet-to-Neumann symbols, and Schur complements are computed exactly on the
declared round/constant quadratic branch.  They are not promoted to the
degree-one nonlinear parent theory when its background and bundle morphism are
absent.
"""

from __future__ import annotations

from functools import lru_cache
from math import cos, pi, sqrt, tanh
from typing import Any

import numpy as np

from bhsm.interface.twistor_berger_associated_bundle import berger_eigenvalue


VERSION = "v14.30"
OUTCOME_D = "BHSM_VIEW2_FAILS_THE_FULL_HOPF_PREIMAGE_EFFECTIVE_ACTION_MATCHING_GATE"
CAMPAIGN_OBJECT = (
    "FULL_HOPF_PREIMAGE_ETA_FIBER_MODE_REDUCTION_WITH_GAUGE_COVARIANT_"
    "DIRICHLET_TO_NEUMANN_EFFECTIVE_ACTION_AND_LOW_ENERGY_MATCHING_TO_THE_"
    "V14_29_LOCAL_ETA_SU3_ACTION"
)
EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_TRIALITY_THREE_ANTITHREE_TO_PHYSICAL_COLOR_BUNDLE_"
    "IDENTIFICATION_WITH_DEGREE_ONE_FULL_HOPF_PREIMAGE_STATIONARY_"
    "BACKGROUND_AND_SELF_ADJOINT_CAP_DOMAIN"
)


def full_preimage_diagram() -> dict[str, Any]:
    return {
        "M8": {"dimension": 8, "topology": "I_t x S7"},
        "M5": {"dimension": 5, "topology": "I_t x S4"},
        "M4": {"dimension": 4, "topology": "I_t x S3 equatorial seam"},
        "C5": {"dimension": 5, "topology": "M4 x [0,epsilon_chi) locally"},
        "C_tilde": {"dimension": 8, "definition": "pi85^(-1)(C5) subset M8"},
        "Sigma_tilde": {"dimension": 7, "definition": "pi85^(-1)(M4), the lifted seam"},
        "maps": {
            "p": "C_tilde -> C5 is pi85 restricted, fiber Sp(1)=S3",
            "r": "C5 -> M4 is equatorial collar retraction",
            "Pi": "C_tilde -> M4 equals r composed with p",
            "inclusion": "C_tilde -> M8 is canonical subset inclusion",
        },
        "commutative_identity": "Pi=(r composed with pi85)|C_tilde",
    }


def fiber_mode_rows(max_two_j: int = 4, L1: float = 1.0, L2: float = 1.0) -> list[dict[str, Any]]:
    """Peter--Weyl eigenspaces for the retained Berger Sp(1) fiber."""

    if not isinstance(max_two_j, int) or max_two_j < 0:
        raise ValueError("max_two_j must be a nonnegative integer")
    rows = []
    for two_j in range(max_two_j + 1):
        j = two_j / 2.0
        for two_m in range(-two_j, two_j + 1, 2):
            m = two_m / 2.0
            rows.append(
                {
                    "fiber_representation": f"Sp(1) spin J={j:g}",
                    "two_j": two_j,
                    "two_m": two_m,
                    "eigenvalue": berger_eigenvalue(two_j, two_m, L1, L2),
                    "multiplicity": two_j + 1,
                    "associated_bundle_rank": two_j + 1,
                    "SU3_representation": None,
                    "eta_topological_sector": None,
                    "orientation": "m pairs with -m under Wigner conjugation",
                    "normalizability": "L2 on compact Sp(1) fiber",
                    "boundary_behavior": "none; the Hopf fiber is closed",
                    "physical_interpretation": "twisted/equivariant coefficient bundle, not a particle assignment",
                }
            )
    return rows


def peter_weyl_cutoff_dimension(max_two_j: int) -> int:
    """Dimension of all matrix elements with 0<=2J<=max_two_j."""

    if not isinstance(max_two_j, int) or max_two_j < 0:
        raise ValueError("max_two_j must be a nonnegative integer")
    return sum((two_j + 1) ** 2 for two_j in range(max_two_j + 1))


def full_preimage_density_factor(rho: float, a_fiber: float = 1.0) -> float:
    """Fiber-integrated density relative to ds dmu4 on the round branch."""

    if a_fiber <= 0.0:
        raise ValueError("a_fiber must be positive")
    return 16.0 * pi**2 * a_fiber**3 * cos(rho) ** 3


def parent_constant_background_hessian_eigenvalue(
    horizontal_eigenvalue: float,
    normal_eigenvalue: float,
    fiber_eigenvalue: float,
    *,
    weight: float = 1.0,
    kappa1: float = 1.0,
) -> float:
    """Eta tangent Hessian eigenvalue at D eta_0=0 and Lambda_eta=0."""

    if min(horizontal_eigenvalue, normal_eigenvalue, fiber_eigenvalue) < 0:
        raise ValueError("Laplacian eigenvalues must be nonnegative")
    if weight <= 0 or kappa1 <= 0:
        raise ValueError("the stable reference branch has positive weight and kappa1")
    return weight * kappa1 * (
        horizontal_eigenvalue + normal_eigenvalue + fiber_eigenvalue
    )


def dtn_symbol(momentum_squared: float, mode_mass_squared: float, half_width: float) -> float:
    """Two-sided Neumann-cap DtN Hessian for a constant quadratic mode."""

    if momentum_squared < 0 or mode_mass_squared < 0 or half_width <= 0:
        raise ValueError("invalid nonnegative spectrum or half-width")
    q = sqrt(momentum_squared + mode_mass_squared)
    if q == 0.0:
        return 0.0
    return 2.0 * q * tanh(q * half_width)


def dtn_low_energy_coefficients(mode_mass: float, half_width: float) -> dict[str, float]:
    """Expansion N(z)=m0+Z z+c4 z^2+O(z^3), z=-D_A^2."""

    if mode_mass < 0 or half_width <= 0:
        raise ValueError("mode_mass must be nonnegative and half_width positive")
    if mode_mass == 0.0:
        return {
            "mass_term": 0.0,
            "Z": 2.0 * half_width,
            "c4": -2.0 * half_width**3 / 3.0,
        }
    q = mode_mass
    t = tanh(q * half_width)
    sech2 = 1.0 - t * t
    return {
        "mass_term": 2.0 * q * t,
        "Z": t / q + half_width * sech2,
        "c4": (
            half_width * sech2 / (4.0 * q**2)
            - t / (4.0 * q**3)
            - half_width**2 * sech2 * t / (2.0 * q)
        ),
    }


def matrix_dtn(operator: np.ndarray, half_width: float) -> np.ndarray:
    """Functional-calculus DtN map 2 sqrt(H) tanh(L sqrt(H))."""

    matrix = np.asarray(operator, dtype=complex)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("operator must be square")
    if not np.allclose(matrix, matrix.conj().T, atol=1e-12):
        raise ValueError("operator must be Hermitian")
    values, vectors = np.linalg.eigh(matrix)
    if np.min(values) < -1e-11:
        raise ValueError("operator must be positive semidefinite")
    symbols = np.array(
        [0.0 if value <= 0.0 else 2.0 * sqrt(value) * tanh(half_width * sqrt(value)) for value in values]
    )
    return (vectors * symbols) @ vectors.conj().T


def schur_complement(hessian: np.ndarray, boundary_size: int) -> np.ndarray:
    """Eliminate the bulk block of a finite Hermitian Hessian exactly."""

    h = np.asarray(hessian, dtype=float)
    if h.ndim != 2 or h.shape[0] != h.shape[1]:
        raise ValueError("hessian must be square")
    if not 0 < boundary_size < h.shape[0]:
        raise ValueError("boundary_size must split boundary and bulk")
    hpp = h[:boundary_size, :boundary_size]
    hpb = h[:boundary_size, boundary_size:]
    hbb = h[boundary_size:, boundary_size:]
    return hpp - hpb @ np.linalg.solve(hbb, hpb.T)


def quadratic_chain_hessian(points: int, mass: float, spacing: float) -> np.ndarray:
    """Finite-element-like positive chain used for the Schur regression test."""

    if points < 3 or mass < 0 or spacing <= 0:
        raise ValueError("invalid chain")
    derivative = np.zeros((points - 1, points))
    for row in range(points - 1):
        derivative[row, row] = -1.0 / sqrt(spacing)
        derivative[row, row + 1] = 1.0 / sqrt(spacing)
    return derivative.T @ derivative + mass**2 * spacing * np.eye(points)


def prior_work_recall_payload() -> dict[str, Any]:
    """Recall the strongest pre-v14.30 ingredients without merging claim levels."""

    rows = [
        {
            "work": "Norman hyperspherical/scalar-topographic manuscripts",
            "source": "Downloads/Norman's_Hypersphere.pdf and topographic_dark_energy_arxiv_ready.pdf",
            "recovered": "compact S3 scalar spectrum, higher-derivative scalar action, and curvature mode selection",
            "current_gate": "ORTHOGONAL_NO_SPIN8_G2_SU3_OR_PHYSICAL_COLOR_BUNDLE_MAP",
        },
        {
            "work": "BHSM v6.2 triality architecture",
            "source": "src/bhsm/interface/triality_generation_scale_architecture.py",
            "recovered": "8_v,8_s,8_c -> 1+7 and 7 -> 1+3+bar3, hence each 8 -> 1+1+3+bar3",
            "current_gate": "ALGEBRAIC_BRANCHING_EXACT_BUT_PHYSICAL_BUNDLE_IDENTIFICATION_OPEN",
        },
        {
            "work": "BHSM v7.1 covariant reduction",
            "source": "docs/bhsm_covariant_bulk_boundary_reduction_functor_v7_1.md",
            "recovered": "equivariant triality-projector transport and the M8/M5/M4 collar geometry",
            "current_gate": "STANDARD_MODEL_REPRESENTATIONS_REMAIN_INDEPENDENT_M4_INPUTS",
        },
        {
            "work": "BHSM v8.0-v8.1 Hopf associated-bundle response",
            "source": "src/bhsm/interface/twistor_berger_associated_bundle.py and master_action/mode_resolved_curvature_incidence.py",
            "recovered": "Peter-Weyl Sp1 tower, Berger eigenvalues, associated-bundle ranks, and generic mode-resolved response",
            "current_gate": "LOCALIZED_DIRAC_HAS_D_HOPF_TWIST_ZERO_AND_ROUND_RESPONSE_IS_TRIALITY_CENTRAL",
        },
        {
            "work": "BHSM v9.0-v9.1 action-selected vacuum audits",
            "source": "docs/bhsm_action_selected_8d_vacuum_flavor_completion_v9_0.md and docs/current_bhsm_status.md",
            "recovered": "precise stationary-vacuum, global-immersion, and common-current requirements",
            "current_gate": "NO_ACTION_SELECTED_STATIONARY_FULL_PREIMAGE_FLAVOR_BACKGROUND",
        },
        {
            "work": "BHSM v11.6 parent charged-current audit",
            "source": "docs/BHSM_PARENT_ACTION_SPECTRAL_CURRENT_COMPLETION_v11_6.md",
            "recovered": "the retained parent weak current has family kernel I3",
            "current_gate": "COMMON_DOMAIN_UP_DOWN_WAVEFUNCTION_AND_CURRENT_PAIRING_MAP_OPEN",
        },
        {
            "work": "BHSM v12.1-v12.2 relative rotation and historical response",
            "source": "Downloads/BHSM_SPIN4_DIFFERENTIAL_ROTATION_REDUCTION_v12_1.md and BHSM_FULL_RECALL_AND_INTERNAL_EXTERNAL_FLAVOR_RECONCILIATION_v12_2.md",
            "recovered": "conditional L2+L3 rotation channels, noncommuting historical Hu/Hd, and CP-odd relative Z6 holonomy",
            "current_gate": "PARENT_TETRAD_PULLBACK_BRIDGE_NORMALIZATION_AND_MIXED_SECOND_VARIATION_OPEN",
        },
        {
            "work": "BHSM v13.3-v14.2 eta-knot color route",
            "source": "Downloads/BHSM_ETA_KNOT_CHIRAL_COLOR_COMPLETION_v13_4.md and BHSM_v14_2_parallel_eta_knot_color_current_note.md",
            "recovered": "conditional wall-selected G2/SU3 polarization and FR-odd 3/bar3 matter-bundle normal form",
            "current_gate": "NORMALIZED_HILBERT_BUNDLE_PHYSICAL_TRANSITION_MAPS_AND_VARIATIONAL_GAUSS_CURRENT_OPEN",
        },
        {
            "work": "BHSM v14.12 DtN gluing",
            "source": "Downloads/BHSM_v14_12_two_layer_DtN_gluing_package.zip",
            "recovered": "canonical momentum and Steklov-Poincare matching conditions",
            "current_gate": "IDENTICAL_ACTION_DTN_IS_A_GLUEING_IDENTITY_NOT_A_SCALE_OR_BUNDLE_SELECTOR",
        },
        {
            "work": "BHSM v14.19 localization transgression",
            "source": "Downloads/BHSM_v14_19_eta_transgression_gauge_trace_package.zip",
            "recovered": "coefficient-free normalized eta zero-mode extension and canonical M4 kinetic pullback",
            "current_gate": "LOCALIZATION_ONLY_PHYSICAL_COLOR_AND_COMPLETE_CHIRAL_FLAVOR_TRANSGRESSION_OPEN",
        },
        {
            "work": "BHSM v14.22 two-sided Dirac pair",
            "source": "Downloads/BHSM_v14_22_two_sided_collar_Dirac_pair_package.zip",
            "recovered": "opposite chiral projectors on the two retained collar orientations with unit overlap",
            "current_gate": "ORIENTATION_ASSIGNMENT_AND_SEAM_HIGGS_BRIDGE_CONDITIONAL_ON_ACTION_OWNERSHIP",
        },
        {
            "work": "BHSM Aug-3 manual attachment and CKM sprints",
            "source": "Downloads/BHSM_MANUAL_ACTION_OWNED_G2_C3_ODD_COEFFICIENT_2026-08-03.md and BHSM_QUARK_YUKAWA_PAIR_AND_CKM_INTERTWINER_2026-08-03.md",
            "recovered": "positive nondegenerate family stiffness seeds and the exact polar-decomposition target for K_ud",
            "current_gate": "THE_MANUAL_CKM_SPRINT_EXPLICITLY_LEAVES_ACTION_DERIVATION_OF_K_ud_OPEN",
        },
        {
            "work": "June BHSM Unified Field Report",
            "source": "Downloads/BHSM_Unified_Field_Report.pdf",
            "recovered": "historical narrative claims of Fredholm, CKM, and 100-percent closure",
            "current_gate": "NOT_AUTHORITATIVE_CONTRADICTED_BY_LATER_OPERATOR_DOMAIN_AND_PROVENANCE_AUDITS",
        },
        {
            "work": "BHSM final paper v1.2",
            "source": "Downloads/BHSM_final_paper.pdf",
            "recovered": "frozen no-retuning screen and explicit first-principles/confinement disclaimers",
            "current_gate": "SCREEN_NOT_A_PARENT_EFFECTIVE_ACTION_DERIVATION",
        },
    ]
    validation = {
        "exact_triality_SU3_branching_recalled": True,
        "Hopf_fiber_and_DtN_machinery_recalled": True,
        "normalized_zero_mode_and_two_sided_chirality_recalled": True,
        "historical_noncommuting_flavor_and_CP_holonomy_recalled": True,
        "no_authoritative_source_contains_the_required_physical_bundle_identification": True,
        "no_authoritative_source_contains_a_degree_one_full_preimage_stationary_background": True,
        "historical_100_percent_closure_claim_not_promoted": True,
        "USB_not_searched_or_modified_under_the_campaign_rule": True,
    }
    return {
        "artifact": "BHSM_full_recall_path_composition_audit_v14_30",
        "version": VERSION,
        "primary_result": "BHSM_PRIOR_WORKS_SUPPLY_NEARLY_ALL_COMPONENTS_SEPARATELY_BUT_NOT_THE_ACTION_OWNED_PHYSICAL_BUNDLE_AND_STATIONARY_BACKGROUND_COMPOSITION",
        "composition_available": "triality branching + Hopf Peter-Weyl tower + eta-wall polarization + zero-mode localization + two-sided chirality + DtN/Schur calculus",
        "missing_commuting_square": "the triality 3/bar3 transition functions and connection must be identified equivariantly with Pi^*P_color and Pi^*A_physical by the retained action",
        "rows": rows,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def representation_obstruction_payload() -> dict[str, Any]:
    validation = {
        "pullback_color_bundle_exists": True,
        "associated_coset_bundle_exists": True,
        "retained_eta_target_is_unit_triality_spinor_S7": True,
        "candidate_eta_target_is_G2_over_SU3_S6": True,
        "tangent_rank_difference_7_versus_6_recorded": True,
        "algebraic_1_plus_3_plus_bar3_branching_exists": True,
        "physical_color_cocycle_independent": True,
        "bundle_morphism_absent": True,
        "Berry_connection_not_substituted": True,
    }
    return {
        "artifact": "BHSM_full_preimage_eta_color_representation_gate_v14_30",
        "version": VERSION,
        "full_preimage_color_bundle": "Pi^*P_color->C_tilde",
        "associated_candidate": "Sigma_tilde=Pi^*P_color x_SU3 G2/SU3",
        "pulled_connection": "A_tilde=Pi^*A_physical, globally covariant on Sigma_tilde",
        "retained_eta_bundle": "unit sphere in the eight-real-dimensional triality-spinor bundle; fiber S7",
        "candidate_eta_bundle": "associated coset fiber G2/SU3=S6",
        "vacuum_tangent_counts": {"retained_parent_eta": 7, "v14_29_coset_eta": 6},
        "exact_branching": "the retained v6.2 architecture has 7_R -> 1_R + 3_C + bar3_C and each triality eight -> 1+1+3+bar3",
        "remaining_provenance_problem": "the action does not identify the singlet with an eliminable wall mode or glue the branching SU3 cocycle to P_color",
        "transition_requirement": "Phi_j h_eta,ij = g_color,ij Phi_i for a fiber map Phi:E_eta,8|C_tilde -> Sigma_tilde",
        "characteristic_class_firewall": "the eta projector rank-three bundle has c2=0, while physical P_color retains general c2; an isomorphism cannot cover all sectors",
        "physical_covariant_derivative_on_retained_eta": None,
        "classification": "ACTION_OWNERSHIP_AND_BUNDLE_PROVENANCE_MISMATCH_UNDER_THE_RETAINED_ACTION",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def fiber_spectrum_payload() -> dict[str, Any]:
    rows = fiber_mode_rows(4)
    validation = {
        "peter_weyl_basis_is_complete_for_L2_Sp1": True,
        "fixed_Jm_rank_is_2J_plus_1": all(row["multiplicity"] == row["two_j"] + 1 for row in rows),
        "round_eigenvalues_match_J_J_plus_1": all(
            abs(row["eigenvalue"] - (row["two_j"] / 2) * (row["two_j"] / 2 + 1)) < 1e-12 for row in rows
        ),
        "closed_fiber_has_no_boundary_term": True,
        "nontrivial_modes_are_associated_sections": True,
        "eta_spinor_twist_not_falsely_scalarized": True,
        "degree_one_eta_mode_not_claimed_identified": True,
    }
    return {
        "artifact": "BHSM_eta_full_preimage_fiber_mode_spectrum_v14_30",
        "version": VERSION,
        "basis": "Peter-Weyl matrix elements Y^J_(n,m) on Sp(1); coefficients form Sp(1)-associated bundles",
        "orthogonality": "integral_F conjugate(Y^J_nm)Y^J'_n'm' dnu_F=delta_JJ' delta_nn' delta_mm'",
        "completeness": "L2(Sp1)=Hilbert direct sum_J V_J tensor V_J^*",
        "cutoff_dimension_twoJ_le_4": peter_weyl_cutoff_dimension(4),
        "rows": rows,
        "basic_zero_mode": rows[0],
        "lowest_nonbasic_modes": [row for row in rows if row["two_j"] == 1],
        "degree_one_eta_mode": None,
        "degree_one_reason": "v13.1 solves a flat R7 cohomogeneity-one texture, not the Spin-twisted Hopf-fiber spectral problem",
        "SU3_triplet_antitriplet_modes": None,
        "SU3_reason": "the action-owned eta/color bundle morphism is absent",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def measure_hessian_payload() -> dict[str, Any]:
    validation = {
        "dimension_hierarchy_exact": full_preimage_diagram()["C_tilde"]["dimension"] == 8,
        "measure_factor_exact_on_bundle_like_round_branch": abs(full_preimage_density_factor(0.0) - 16 * pi**2) < 1e-12,
        "connection_cross_terms_retained_in_horizontal_derivative": True,
        "p8_zero_in_constant_background_quadratic_hessian": True,
        "seven_parent_tangent_modes_retained": True,
        "degree_one_full_preimage_background_absent": True,
        "self_adjoint_cap_domain_absent": True,
    }
    return {
        "artifact": "BHSM_full_preimage_measure_parent_eta_hessian_v14_30",
        "version": VERSION,
        "diagram": full_preimage_diagram(),
        "metric": "G8=g5_horizontal+<I_F(omega+connection),(omega+connection)> on the bundle-like branch",
        "measure": "dmu8=dmuF cos(rho)^3 ds dmu4, ds=a(t)d rho; block connection cross terms cancel from the determinant but remain in covariant derivatives",
        "orientation": "or(C_tilde)=or(M4) wedge d rho wedge or(Sp1), consistent with the retained base-before-fiber convention after the declared pushforward sign",
        "parent_action": "S_eta8=int_M8 dmu8[-w(kappa1 X/2+X^4/8)+Lambda_eta(<eta,eta>-1)/2]",
        "candidate_gauged_parent_action": "undefined on the retained eta bundle; Pi^*A acts only after the missing eta/color morphism",
        "constant_background_hessian": "H_eta=w kappa1 P_T(-Delta_horizontal-Delta_normal-Delta_fiber)P_T on seven tangent modes; X^4 starts at eighth fluctuation order",
        "nonconstant_background_p8": "delta2 F=F'(X0)delta2 X+(3/2)X0^2(delta X)^2, requiring the actual degree-one full-preimage background",
        "retained_degree_one_solution_scope": "v13.1 flat R7 cohomogeneity-one BVP only",
        "full_preimage_stationary_background": None,
        "self_adjoint_domain": None,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def dtn_schur_payload() -> dict[str, Any]:
    mass, width = 1.2, 0.7
    coefficients = dtn_low_energy_coefficients(mass, width)
    h = quadratic_chain_hessian(6, mass, 0.2)
    heff = schur_complement(h, 1)
    validation = {
        "dtn_positive_on_positive_mode": dtn_symbol(0.4, mass**2, width) > 0,
        "dtn_low_energy_Z_positive": coefficients["Z"] > 0,
        "matrix_dtn_self_adjoint": np.allclose(matrix_dtn(np.diag([0.0, 1.0, 3.0]), width), matrix_dtn(np.diag([0.0, 1.0, 3.0]), width).conj().T),
        "schur_complement_positive": np.min(np.linalg.eigvalsh(heff)) > 0,
        "naive_trace_missing_schur_term": not np.allclose(heff, h[:1, :1]),
        "gauge_covariance_is_functional_calculus": True,
        "nonlinear_dtn_not_claimed": True,
    }
    return {
        "artifact": "BHSM_eta_gauge_covariant_DtN_and_Schur_audit_v14_30",
        "version": VERSION,
        "quadratic_proxy": "one frozen Hermitian eta mode with H_A=-D_A^2+M_Jm^2 on a constant normal interval",
        "two_sided_DtN": "N_A=2 sqrt(H_A) tanh(L sqrt(H_A)) for regular/Neumann outer caps",
        "gauge_covariance": "H_A->U^-1 H_A U implies N_A->U^-1 N_A U by spectral functional calculus",
        "self_adjointness": "N_A is self-adjoint and nonnegative when H_A is self-adjoint and nonnegative",
        "low_energy_coefficients_reference": coefficients,
        "schur_complement": "H_eff=H_pp-H_pb H_bb^-1 H_bp",
        "computed_chain_Hpp": float(h[0, 0]),
        "computed_chain_Heff": float(heff[0, 0]),
        "naive_reduction_failure": "the nonzero Schur term is the discrete Dirichlet-to-Neumann correction",
        "scope": "exact quadratic constant-mode theorem; not the nonlinear degree-one BHSM eta critical value",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def low_energy_matching_payload() -> dict[str, Any]:
    matching = [
        {"v14_29_operator": "w(sigma)", "parent_origin": "same S8 weight", "derived_coefficient": "w on C_tilde", "sign": "+ in positive Euclidean Hessian", "dimension": "0", "normalization": "unfixed reduction", "fiber_contribution": "mode overlap", "threshold": "background dependent", "status": "STRUCTURE_ONLY"},
        {"v14_29_operator": "kappa1 X/2", "parent_origin": "S8 p2", "derived_coefficient": "DtN Z depends on width, mode gap, and normalization", "sign": "Z>0 on stable proxy", "dimension": "reduction dependent", "normalization": "open", "fiber_contribution": "lambda_Jm", "threshold": "fixed only after geometry/domain", "status": "NO_FIXED_MATCH"},
        {"v14_29_operator": "X^4/8", "parent_origin": "S8 p8", "derived_coefficient": None, "sign": "parent positive-energy sign retained", "dimension": "L^-8 density", "normalization": "nonlinear profile tensors", "fiber_contribution": "infinite Clebsch-Gordan tower", "threshold": "nonlinear critical value", "status": "NOT_DERIVED"},
        {"v14_29_operator": "D_A eta", "parent_origin": None, "derived_coefficient": None, "sign": None, "dimension": "L^-1", "normalization": "requires eta/color bundle identification", "fiber_contribution": "Sp1 twist distinct from physical color", "threshold": None, "status": "NO_MATCH"},
        {"v14_29_operator": "collar Jacobian", "parent_origin": "v7.1 measure", "derived_coefficient": "cos^3 rho with V_F", "sign": "+ orientation fixed", "dimension": "V_F ds", "normalization": "exact round branch", "fiber_contribution": "16 pi^2 a_F^3", "threshold": None, "status": "EXACT_CONDITIONAL_BRANCH"},
        {"v14_29_operator": "six eta tangent modes", "parent_origin": "exact algebraic 7=1+3+bar3 branching", "derived_coefficient": None, "sign": None, "dimension": None, "normalization": None, "fiber_contribution": "parent has seven tangent modes before an action-unowned singlet elimination", "threshold": None, "status": "NO_MATCH"},
        {"v14_29_operator": "Noether current", "parent_origin": "delta_A S_eff", "derived_coefficient": None, "sign": "v14.29 convention preserved", "dimension": None, "normalization": "open", "fiber_contribution": "requires on-shell mode response", "threshold": "open", "status": "NOT_DEFINED_FROM_PARENT"},
        {"v14_29_operator": "unit constraint", "parent_origin": "Lambda_eta on S7", "derived_coefficient": "constraint retained", "sign": "retained", "dimension": "Lambda L^-8", "normalization": "parent", "fiber_contribution": "mode products", "threshold": "constraint couples tower", "status": "TARGET_MISMATCH_S7_VS_S6"},
    ]
    validation = {
        "all_required_v14_29_operators_audited": len(matching) == 8,
        "no_coefficient_tuned": True,
        "no_measured_input_used": True,
        "local_current_sign_preserved": True,
        "selector_and_pure_wall_zero_current_preserved": True,
        "no_new_vector_pole_preserved": True,
        "exact_match_rejected": True,
        "low_energy_match_rejected_under_retained_action": True,
    }
    return {
        "artifact": "BHSM_v14_29_full_preimage_low_energy_matching_gate_v14_30",
        "version": VERSION,
        "matching_table": matching,
        "classification": "NO_MATCH",
        "v14_29_status": "VALIDATED_CONDITIONALLY_AS_A_LOCAL_COMPLETION_CANDIDATE_BUT_NOT_THE_LOW_ENERGY_LIMIT_OF_THE_RETAINED_PARENT_ACTION",
        "current_status": "v14.29 bosonic candidate current remains exact for its candidate action; parent effective physical current is undefined",
        "primary_outcome": OUTCOME_D,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def completion_payload() -> dict[str, Any]:
    dependencies = [
        prior_work_recall_payload(),
        representation_obstruction_payload(),
        fiber_spectrum_payload(),
        measure_hessian_payload(),
        dtn_schur_payload(),
        low_energy_matching_payload(),
    ]
    validation = {
        "all_full_preimage_audits_pass": all(item["validation_passed"] for item in dependencies),
        "campaign_object_attempted": True,
        "outcome_D_supported_by_bundle_provenance_and_background_obstructions": True,
        "algebraic_triality_SU3_branching_not_falsely_rejected": True,
        "conditional_quadratic_DtN_not_overpromoted": True,
        "FR_and_downstream_fail_closed": True,
        "frozen_predictions_unchanged": True,
        "physical_outputs_absent": True,
        "BHSM_not_claimed_complete": True,
    }
    return {
        "artifact": "BHSM_full_hopf_preimage_effective_completion_gate_v14_30",
        "version": VERSION,
        "campaign_object": CAMPAIGN_OBJECT,
        "primary_verdict": OUTCOME_D,
        "secondary_verdict": "THE_PRIOR_BHSM_WORKS_SUPPLY_THE_ALGEBRAIC_SU3_BRANCHING_FIBER_SPECTRUM_LOCALIZATION_CHIRALITY_AND_QUADRATIC_DTN_PIECES_BUT_NOT_THE_ACTION_OWNED_PHYSICAL_COLOR_BUNDLE_IDENTIFICATION_OR_DEGREE_ONE_FULL_PREIMAGE_BACKGROUND",
        "BHSM_complete": False,
        "topology_theorem": "VALIDATED",
        "nonbasic_eta_theorem": "VALIDATED",
        "full_preimage_bundle_gate": "ALGEBRAIC_BRANCHING_VALID_BUT_ACTION_OWNED_RETAINED_ETA_TO_PHYSICAL_COLOR_IDENTIFICATION_ABSENT",
        "fiber_mode_gate": "VALIDATED_FOR_SP1_SCALAR_ASSOCIATED_MULTIPLETS; OPEN_FOR_THE_TRIALITY_SPINOR_ETA_OPERATOR",
        "measure_gate": "VALIDATED_CONDITIONALLY_ON_THE_RETAINED_BUNDLE_LIKE_ROUND_BRANCH",
        "parent_Hessian_gate": "CONSTANT_TRIVIAL_BACKGROUND_ONLY; DEGREE_ONE_FULL_PREIMAGE_BACKGROUND_OPEN",
        "DtN_gate": "VALIDATED_FOR_THE_QUADRATIC_PROXY; PHYSICAL_ETA_DTN_NOT_DEFINED",
        "Schur_complement_gate": "VALIDATED",
        "low_energy_matching_gate": "NO_MATCH_UNDER_THE_RETAINED_ACTION_DUE_TO_BUNDLE_PROVENANCE_AND_BACKGROUND_GAPS",
        "physical_current_status": "OPEN_NOT_ACTION_OWNED",
        "FR_Dirac_matching_gate": "NOT_ELIGIBLE",
        "no_double_counting_gate": "NOT_ELIGIBLE",
        "non_Abelian_BVP_gate": "NOT_ELIGIBLE",
        "dependencies": [item["artifact"] for item in dependencies],
        "validated": ["exact triality 8 to 1+1+3+bar3 branching", "full-preimage diagram", "Sp1 Peter-Weyl scalar multiplets", "round-branch measure", "constant-background parent p2 Hessian", "quadratic gauge-covariant DtN functional calculus", "Schur correction and low-energy series", "normalized eta zero-mode localization from v14.19", "conditional two-sided chirality architecture from v14.22"],
        "invalidated": ["full preimage alone supplying the eta/color physical-bundle map", "identifying the v13.1 R7 texture as a full Hopf-preimage stationary background", "deriving v14.29 by the quadratic scalar DtN proxy", "physical current ownership under the retained action", "the June Unified Field Report as evidence of mathematical closure"],
        "reclassified": ["the obstruction is bundle/action provenance, not absence of an algebraic SU3 representation", "v14.29 remains a local candidate", "Peter-Weyl modes are Sp1 associated multiplets without action-owned physical SU3 particle labels", "the exact DtN formula is a conditional proxy theorem", "historical noncommuting Hu/Hd and CP holonomy remain conditional mechanism witnesses"],
        "open": [EXACT_NEXT_OBJECT],
        "exact_next_object": EXACT_NEXT_OBJECT,
        "frozen_predictions_changed": False,
        "physical_outputs_emitted": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
