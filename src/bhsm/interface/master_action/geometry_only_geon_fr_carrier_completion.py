"""BHSM v9.1 geometry-only geon/FR carrier completion audit.

The module works on the actual canonical configuration space of the frozen
eight-dimensional metric-plus-real-scalar action.  It keeps the older v6.6
``Map_*^N(S3,S3)`` FR construction as an adopted comparison and does not
silently identify that mapping space with the action-owned metric quotient.

The decisive result is exact and upstream of the conditional v8.4--v8.9
finite-dimensional flavor functor: quotienting the contractible canonical
field space by the identity component of the framed diffeomorphism group gives
a classifying space with trivial fundamental group.  Large diffeomorphisms can
define a different observer quotient, but the resulting exotic-sphere class
is neither the declared quotient nor an action-selected rotation/exchange
character, and a configuration-space sign line is not a local chiral Clifford
carrier.
"""

from __future__ import annotations

from hashlib import sha256
import json
from math import cosh
from pathlib import Path
from typing import Any

import mpmath as mp
import numpy as np
from scipy.integrate import quad, solve_bvp, solve_ivp
import sympy as sp


VERSION = "v9.1"
SPRINT = "bhsm-geometry-only-geon-fr-carrier-completion-v9-1"
SOURCE_PR207_SHA = "c9d233c10f08b2d238b2c0c1ad8024f6c99fa0fd"
ARTIFACT_NAME = "BHSM_geometry_only_geon_fr_carrier_completion_v9_1"
FINAL_VERDICT = (
    "BHSM_GEOMETRY_ONLY_PARENT_ACTION_CANNOT_GENERATE_THE_REQUIRED_"
    "FR_CHIRAL_FLAVOR_CARRIER"
)
NEXT_MISSING_OBJECT = (
    "ACTION_LEVEL_GLOBAL_TOPOLOGICAL_SECTOR_WITH_LOCAL_CHIRAL_"
    "TRANSGRESSION_AND_COMMON_PARENT_CURRENT_OWNERSHIP"
)
RELEASE_VERDICT = "BHSM_1_0_RELEASE_BLOCKED"


def deterministic_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def configuration_space_definition() -> dict[str, Any]:
    """Return the declared canonical geometry-only configuration space.

    Sobolev order s>dim(S7)/2+1 makes the diffeomorphism action and the
    first-derivative field operations continuous.  An observer point and
    oriented frame remove all metric stabilizers.  Taking the identity
    component after imposing that framing is important: large
    diffeomorphisms are audited separately rather than silently gauged.
    """

    return {
        "spacetime": "M8=I_t x S7",
        "canonical_spatial_manifold": "Sigma=S7 with its standard smooth structure",
        "spatial_boundary": None,
        "history_time_domain": "compact interval I=[t_i,t_f], or R_t after a declared global extension",
        "temporal_endpoint_conditions": "Dirichlet endpoint traces for G,chi,sigma; compactly supported interior variations",
        "orientation": "dt wedge or_S7 with the standard orientation of S7",
        "spin_structure": "unique, since H^1(S7;Z2)=0",
        "frame_bundle": "oriented orthonormal SO(7) frame bundle of each spatial metric",
        "observer_framing": "one fixed p in S7 and one fixed oriented frame at p",
        "regularity": {
            "metrics": "H^s positive-definite spatial metrics, s>9/2",
            "scalars": "H^s(S7,R)_chi x H^s(S7,R)_sigma, s>9/2",
            "diffeomorphisms": "H^(s+1) observer diffeomorphisms",
        },
        "unreduced_field_space": "C_geom^s=Met_+^s(S7) x H^s(S7,R)^2",
        "gauge_group": "Diff^(s+1)_(0,fr)(S7), the identity component fixing p and its oriented frame",
        "internal_gauge_group": "trivial on the active S8 singlets",
        "physical_configuration_space": "Q_geom^0=C_geom^s/Diff^(s+1)_(0,fr)(S7)",
        "large_diffeomorphisms_quotiented": False,
        "admissible_metric_class": "all positive spatial metrics in the fixed S7 smooth topology; Lorentzian lapse/shift belong to histories and constraints",
        "fixed_topology": True,
        "topology_change_allowed": False,
    }


def configuration_space_strata() -> list[dict[str, str]]:
    """Keep full, reduced, solution, and collective spaces distinct."""

    return [
        {
            "space": "full field space C_geom^s",
            "meaning": "all admissible metrics and two real scalar sections on fixed S7",
            "topology_use": "contractible total space",
        },
        {
            "space": "small-diffeomorphism quotient Q_geom^0",
            "meaning": "physical canonical configurations with observer framing",
            "topology_use": "the action-owned quotient used for the pi1 theorem",
        },
        {
            "space": "full-diffeomorphism observer quotient",
            "meaning": "a different quotient that also gauges mapping classes",
            "topology_use": "comparison only; not silently substituted for Q_geom^0",
        },
        {
            "space": "symmetry-reduced ansatz space",
            "meaning": "finite functions or collective coordinates retained by a proved truncation",
            "topology_use": "cannot determine the topology of the full quotient",
        },
        {
            "space": "stationary moduli space",
            "meaning": "solutions modulo gauge after equations and boundary conditions",
            "topology_use": "undefined until a stationary branch exists",
        },
        {
            "space": "collective-coordinate space near Phi_*",
            "meaning": "normalizable zero modes around one selected solution",
            "topology_use": "undefined because Phi_* and its zero modes are absent",
        },
    ]


def small_diffeomorphism_pi1_theorem() -> dict[str, Any]:
    """Exact fundamental-group result for the declared physical quotient."""

    return {
        "total_space_contractible": True,
        "metric_space_reason": "the pointwise positive cone is convex",
        "scalar_space_reason": "both scalar Sobolev spaces are real topological vector spaces",
        "action_free": True,
        "free_action_reason": "an isometry fixing a point and its full tangent frame is the identity",
        "principal_fibration": "Diff_(0,fr) -> C_geom^s -> Q_geom^0",
        "homotopy_equivalence": "Q_geom^0 weakly equivalent to B Diff_(0,fr)",
        "long_exact_sequence": "pi1(Q_geom^0)=pi0(Diff_(0,fr))",
        "gauge_group_connected_by_definition": True,
        "pi1_Q_geom_0": "0",
        "nontrivial_order_two_loop": False,
        "nontrivial_FR_character": None,
        "FR_line_bundle": None,
        "result": "BHSM_SMALL_DIFF_GEOMETRY_CONFIGURATION_SPACE_HAS_NO_FR_Z2",
        "scope": "the component and quotient declared by the current S8 gauge doctrine",
    }


def large_diffeomorphism_audit() -> dict[str, Any]:
    """Separate the high-dimensional sphere mapping class from Q_geom^0."""

    return {
        "orientation_preserving_mapping_class_group": "pi0 Diff^+(S7)=Theta_8=Z2",
        "mathematical_origin": "gluing two 8-disks by an S7 diffeomorphism gives the homotopy-8-sphere class",
        "belongs_to_small_diff_quotient": False,
        "if_full_observer_group_is_gauged": "pi1 of the corresponding classifying quotient can inherit this Z2",
        "loop_interpretation": "exotic-sphere gluing mapping class",
        "identified_with_two_pi_rotation": False,
        "identified_with_geon_exchange": False,
        "character_selected_by_S8": False,
        "available_characters_if_adopted": ["trivial", "sign"],
        "action_selects_between_characters": False,
        "local_spinor_bundle_produced": False,
        "conclusion": (
            "enlarging the quotient would add global gauge doctrine and a "
            "quantization choice; it would not derive the requested local carrier"
        ),
    }


def prior_fr_reconciliation() -> dict[str, Any]:
    """Reconcile v9.1 with the exact but adopted v6.6 mapping-space result."""

    return {
        "v6_6_space": "Map_*^N(S3,S3)",
        "v6_6_pi1": "pi4(S3)=Z2",
        "v6_6_status": "ADOPTED_BHSM_IDENTIFICATION_NOT_PARENT_ACTION_THEOREM",
        "v6_6_FR_sign": "(-1)^N after choosing the nontrivial character",
        "equal_to_Q_geom_0": False,
        "action_derived_map_from_Q_geom_0_to_v6_6_space": None,
        "promotion_in_v9_1": False,
        "reason": "the active S8 scalars are R-valued and no S3-valued degree field is present",
    }


def candidate_loop_ledger() -> list[dict[str, Any]]:
    return [
        {
            "candidate": "large orientation-preserving diffeomorphism",
            "closed_in_Q_geom_0": False,
            "order": 2,
            "status": "different full-diffeomorphism quotient; exotic-sphere class",
        },
        {
            "candidate": "2pi spatial rotation",
            "closed_in_Q_geom_0": True,
            "order": 1,
            "status": "lies in the small gauge orbit and projects to the constant loop",
        },
        {
            "candidate": "exchange of two localized geons",
            "closed_in_Q_geom_0": False,
            "order": None,
            "status": "no two-geon stationary sector or exchange configuration space is action-derived",
        },
        {
            "candidate": "quaternionic Hopf-fibration cycle",
            "closed_in_Q_geom_0": False,
            "order": None,
            "status": "fixed bundle geometry, not an active configuration coordinate",
        },
        {
            "candidate": "G2-compatible-structure path",
            "closed_in_Q_geom_0": False,
            "order": None,
            "status": "G2 structure is not an active S8 field",
        },
        {
            "candidate": "metric-plus-frame rotation",
            "closed_in_Q_geom_0": True,
            "order": 1,
            "status": "the observer frame is gauge fixing, not a physical rotor",
        },
        {
            "candidate": "two-cap exchange or reflection",
            "closed_in_Q_geom_0": False,
            "order": None,
            "status": "belongs to independently owned S5|4 data, not the S8 canonical field space",
        },
        {
            "candidate": "Spin(8) triality permutation",
            "closed_in_Q_geom_0": False,
            "order": 3,
            "status": "discrete representation automorphism, not a metric/scalar loop",
        },
        {
            "candidate": "connected-sum or handle geon",
            "closed_in_Q_geom_0": False,
            "order": None,
            "status": "changes the fixed S7 manifold doctrine and is outside the action domain",
        },
    ]


def g2_selection_no_go() -> dict[str, Any]:
    """No natural or holonomy-selected G2 polarization follows from S8."""

    return {
        "compatible_G2_fiber_for_fixed_metric_orientation": "SO(7)/G2=RP7",
        "metric_selects_unique_point": False,
        "equivariance_obstruction": (
            "an SO(7)-natural selection would be a fixed point of the transitive "
            "SO(7) action on SO(7)/G2, but no such fixed point exists"
        ),
        "torsion_free_G2_on_S7": False,
        "torsion_free_topology_reason": (
            "a torsion-free G2 form is a nonzero harmonic 3-form, while H^3(S7)=0"
        ),
        "nearly_parallel_G2_exists": True,
        "nearly_parallel_selected_by_metric_alone": False,
        "S8_G2_energy_or_constraint_term": None,
        "lowest_spinor_selection": None,
        "round_metric_lowest_spinor_simple": False,
        "eta_phi": None,
        "J_u": None,
        "Pi_10": None,
        "P_chi0": None,
        "P_chi1": None,
        "P_chi2": None,
        "result": "BHSM_ACTION_SELECTED_G2_TRIALITY_POLARIZATION_NOT_DERIVED",
    }


def local_carrier_no_go() -> dict[str, Any]:
    """A global FR sign line cannot replace a local chiral Clifford bundle."""

    return {
        "FR_object_if_available": "flat complex line over global configuration space",
        "local_spacetime_bundle": None,
        "Spin_1_3_Clifford_action": None,
        "left_right_chirality_operator": None,
        "local_principal_symbol": None,
        "self_adjoint_local_domain": None,
        "configuration_to_M4_transgression": None,
        "C3_family_action_from_FR": None,
        "G2_SU3_current_from_FR": None,
        "logical_result": (
            "even an adopted global sign character changes wavefunction holonomy "
            "only; it does not construct a local spinor field, chirality, or a "
            "bifundamental charged current"
        ),
    }


def closed_flrw_reduction() -> dict[str, Any]:
    """Lapse-retaining reduction on ``I x S7``.

    The Gibbons--Hawking endpoint term is understood, so the displayed
    minisuperspace Lagrangian contains no second time derivative of ``a``.
    ``V7`` is the unit-sphere volume and is an overall positive factor.
    """

    t, hubble = sp.symbols("t H", real=True, positive=True)
    scale = sp.cosh(hubble * t) / hubble
    exact_constraint = sp.simplify(
        sp.diff(scale, t) ** 2 + 1 - hubble**2 * scale**2
    )
    exact_evolution = sp.simplify(
        sp.diff(scale, t, 2) - hubble**2 * scale
    )
    return {
        "ansatz": "ds8^2=-N(t)^2 dt^2+a(t)^2 g_S7",
        "unit_S7_volume": "pi^4/3",
        "effective_potential": "Ueff(sigma)=kappa0/2+A0 sigma^2/2+G0 sigma^4/4",
        "reduced_action": (
            "S=Vol(S7) int dt[-21 kappa1 a^5 adot^2/N+21 kappa1 N a^5"
            "-N a^7 Ueff+a^7(Kchi+Ksigma)/(2N)]"
        ),
        "kinetic_terms": (
            "Kchi=Zchi(1+g sigma^2) chidot^2; "
            "Ksigma=Zsigma sigmadot^2"
        ),
        "lapse_constraint": (
            "21 kappa1[(adot/(N a))^2+a^-2]="
            "Ueff+(Kchi+Ksigma)/(2N^2)"
        ),
        "scalar_stationarity": [
            "sigma=0",
            "sigma^2=-A0/G0 when real",
            "chi=constant is an unfixed shift modulus",
        ],
        "constant_scalar_solution_condition": "H^2=Ueff/(21 kappa1)>0",
        "constant_scalar_solution": "a(t)=H^-1 cosh(H(t-t0))",
        "exact_constraint_residual": str(exact_constraint),
        "exact_evolution_residual": str(exact_evolution),
        "stationary": False,
        "stationary_reason": (
            "at a closed-slicing turning point a=H^-1, the evolution gives "
            "addot=H rather than zero"
        ),
        "periodic": False,
        "periodic_reason": "for H^2>0 and a>0, addot=H^2 a>0",
        "branch_unique": False,
        "branch_dependence": [
            "kappa0,kappa1,A0,G0",
            "choice of scalar stationary root",
            "time translation t0",
            "constant chi modulus",
        ],
        "Hamiltonian_reduction_supplies_stationary_vacuum": False,
    }


def flrw_numerical_crosscheck() -> dict[str, Any]:
    """Two independent numerical checks of the representative closed slicing.

    The representative normalization H=kappa1=1 and Ueff=21 validates the
    reduced equations only.  It is not a selected value of any BHSM input.
    """

    grid = np.linspace(0.0, 1.0, 81)
    exact_a = np.cosh(grid)
    exact_v = np.sinh(grid)

    def rhs(_t: float, y: np.ndarray) -> np.ndarray:
        return np.array([y[1], y[0]])

    ivp = solve_ivp(
        rhs,
        (0.0, 1.0),
        np.array([1.0, 0.0]),
        method="DOP853",
        rtol=1.0e-12,
        atol=1.0e-14,
        dense_output=True,
    )
    ivp_values = ivp.sol(grid)

    def bvp_rhs(_t: np.ndarray, y: np.ndarray) -> np.ndarray:
        return np.vstack((y[1], y[0]))

    def boundary(left: np.ndarray, right: np.ndarray) -> np.ndarray:
        return np.array([left[1], right[0] - cosh(1.0)])

    initial = np.vstack((np.cosh(grid), np.sinh(grid)))
    bvp = solve_bvp(
        bvp_rhs,
        boundary,
        grid,
        initial,
        tol=1.0e-10,
        max_nodes=2000,
    )
    bvp_values = bvp.sol(grid)

    def lagrangian(t_value: float) -> float:
        a_value = np.cosh(t_value)
        velocity = np.sinh(t_value)
        return float(
            -21.0 * a_value**5 * velocity**2
            + 21.0 * a_value**5
            - 21.0 * a_value**7
        )

    scipy_action, scipy_error = quad(
        lagrangian, -1.0, 1.0, epsabs=1.0e-12, epsrel=1.0e-12
    )
    mp.mp.dps = 80
    mpmath_action = mp.quad(
        lambda x: (
            -21 * mp.cosh(x) ** 5 * mp.sinh(x) ** 2
            + 21 * mp.cosh(x) ** 5
            - 21 * mp.cosh(x) ** 7
        ),
        [-1, 0, 1],
    )

    ivp_constraint = ivp_values[1] ** 2 + 1.0 - ivp_values[0] ** 2
    bvp_constraint = bvp_values[1] ** 2 + 1.0 - bvp_values[0] ** 2
    return {
        "classification": "ANSATZ_VALIDATION_ONLY",
        "physical_promotion": False,
        "representative_inputs_are_physical": False,
        "representative_normalization": {"H": 1.0, "kappa1": 1.0, "Ueff": 21.0},
        "methods": [
            "DOP853 initial-value integration",
            "fourth-order collocation boundary-value solve",
        ],
        "ivp_success": bool(ivp.success),
        "bvp_success": bool(bvp.success),
        "ivp_exact_solution_residual": float(
            np.max(np.abs(ivp_values - np.vstack((exact_a, exact_v))))
        ),
        "bvp_exact_solution_residual": float(
            np.max(np.abs(bvp_values - np.vstack((exact_a, exact_v))))
        ),
        "cross_method_residual": float(np.max(np.abs(ivp_values - bvp_values))),
        "ivp_constraint_residual": float(np.max(np.abs(ivp_constraint))),
        "bvp_constraint_residual": float(np.max(np.abs(bvp_constraint))),
        "boundary_residual": float(
            np.max(np.abs(boundary(bvp_values[:, 0], bvp_values[:, -1])))
        ),
        "action_per_unit_S7_scipy": float(scipy_action),
        "action_per_unit_S7_mpmath": float(mpmath_action),
        "action_cross_method_residual": float(abs(scipy_action - mpmath_action)),
        "scipy_quadrature_error_estimate": float(scipy_error),
        "mesh_points_initial": int(grid.size),
        "mesh_points_final": int(bvp.x.size),
        "methods_agree": bool(
            ivp.success
            and bvp.success
            and np.max(np.abs(ivp_values - bvp_values)) < 1.0e-9
            and np.max(np.abs(ivp_constraint)) < 1.0e-9
            and np.max(np.abs(bvp_constraint)) < 1.0e-9
            and abs(scipy_action - mpmath_action) < 1.0e-10
        ),
        "stationary_geon_constructed": False,
    }


def berger_hopf_reduction() -> dict[str, Any]:
    """Quaternionic-Hopf two-scale reduction and its static no-go."""

    x = sp.symbols("x", positive=True)
    scalar = 48 + 6 / x - 12 * x
    normalized_scalar = sp.simplify(x ** sp.Rational(3, 7) * scalar)
    numerator = sp.factor(sp.together(sp.diff(normalized_scalar, x))).as_numer_denom()[0]
    roots = sp.solve(numerator, x)
    return {
        "ansatz": (
            "ds8^2=-N^2dt^2+a_H^2 g_S4+a_F^2<omega,omega>"
        ),
        "bundle": "S3 -> S7 -> S4 with the canonical Sp(1) connection",
        "invariant_volume_factor": "a_H^4 a_F^3",
        "spatial_scalar_curvature": (
            "R7=48/a_H^2+6/a_F^2-12 a_F^2/a_H^4"
        ),
        "reduced_gravity_action": (
            "Vol0 int dt a_H^4 a_F^3{(kappa1/(2N))"
            "[-12 H_Hdot^2-6 H_Fdot^2-24 H_Hdot H_Fdot]"
            "+N[kappa1 R7/2-Ueff]}"
        ),
        "velocity_definition": "H_Hdot=adot_H/a_H; H_Fdot=adot_F/a_F",
        "lapse_retained": True,
        "canonical_connection_curvature_included": True,
        "homogeneous_consistency": (
            "the two scale factors exhaust the Sp(2)xSp(1)-invariant diagonal "
            "metrics; compact-group symmetric criticality applies within this sector"
        ),
        "full_nonsinglet_stability_proved": False,
        "volume_normalized_curvature_variable": "x=(a_F/a_H)^2",
        "volume_normalized_curvature": str(normalized_scalar),
        "Einstein_shape_equation": "5 x^2-6 x+1=0",
        "Einstein_shape_roots": [str(root) for root in roots],
        "round_ratio": "x=1",
        "Jensen_squashed_ratio": "x=1/5",
        "static_lapse_constraint": "kappa1 R7/2=Ueff",
        "static_scale_equations_after_constraint": "partial_(a_H)R7=partial_(a_F)R7=0",
        "vertical_derivative": "partial_(a_F)R7=-12/a_F^3-24 a_F/a_H^4<0",
        "positive_scale_static_solution": False,
        "static_product_geon_vacuum": False,
        "scope": "exact for the lapse-retaining homogeneous quaternionic-Hopf two-scale sector",
    }


def cohomogeneity_one_and_localized_audit() -> dict[str, Any]:
    return {
        "cohomogeneity_one_wall": {
            "scalar_target_topological_charge": None,
            "reason": "R_chi x R_sigma is contractible and S7 has no spatial boundary",
            "single_wall_on_compact_S7": False,
            "allowed_non_topological_profiles": "coefficient- and boundary-domain-dependent paired or nodal solutions",
            "unique_reduced_action": None,
            "missing": [
                "declared orbit type and singular-orbit regularity",
                "proved retained metric modes",
                "action-selected scalar coefficient signs",
                "global lapse/shift gauge and boundary domain",
            ],
        },
        "G2_structured_branch": {
            "stable_three_form_active": False,
            "torsion_free_branch_on_S7": False,
            "nearly_parallel_polarization_selected": False,
        },
        "localized_geon": {
            "connected_sum_sector_in_action_domain": False,
            "topologically_protected_metric_lump": False,
            "stationary_relative_equilibrium_derived": False,
            "two_geon_exchange_space_derived": False,
            "existence_theorem": None,
            "interpretation": "not excluded as a generic PDE solution, but it cannot repair the proved FR and local-carrier obstruction",
        },
    }


def ansatz_ladder_audit() -> list[dict[str, Any]]:
    return [
        {
            "class": "A time-warped closed geometry",
            "reduction": "DERIVED_WITH_LAPSE",
            "result": "coefficient-dependent de Sitter closed slicing; not stationary or periodic",
            "physical_vacuum_selected": False,
        },
        {
            "class": "B Berger/Hopf anisotropic S7",
            "reduction": "DERIVED_IN_HOMOGENEOUS_INVARIANT_SECTOR",
            "result": "no positive-scale static product solution",
            "physical_vacuum_selected": False,
        },
        {
            "class": "C cohomogeneity-one wall/geon",
            "reduction": "NOT_UNIQUE_WITH_CURRENT_DOMAIN_DATA",
            "result": "no topological scalar wall sector on compact S7",
            "physical_vacuum_selected": False,
        },
        {
            "class": "D G2-structured configuration",
            "reduction": "BLOCKED_NO_ACTIVE_G2_STRUCTURE",
            "result": "metric does not canonically select a compatible G2 point",
            "physical_vacuum_selected": False,
        },
        {
            "class": "E localized geon branch",
            "reduction": "OPEN_PDE_BUT_UPSTREAM_TOPOLOGY_AND_CARRIER_BLOCKED",
            "result": "no stable localized or two-geon sector is action-derived",
            "physical_vacuum_selected": False,
        },
    ]


def vacuum_status() -> dict[str, Any]:
    flrw = closed_flrw_reduction()
    numerical = flrw_numerical_crosscheck()
    berger = berger_hopf_reduction()
    return {
        "closed_FLRW": flrw,
        "closed_FLRW_numerical_crosscheck": numerical,
        "Berger_Hopf": berger,
        "cohomogeneity_one_and_localized": cohomogeneity_one_and_localized_audit(),
        "ansatz_ladder": ansatz_ladder_audit(),
        "action_selected_unique_vacuum": False,
        "stationary_geon_vacuum": None,
        "action_value_of_physical_vacuum": None,
        "physical_equation_residual": None,
        "physical_constraint_residual": None,
        "physical_stability_spectrum": None,
        "reason": (
            "the derived homogeneous branches are nonstationary or obstructed; "
            "the remaining PDE branches are not uniquely defined or selected, "
            "and the exact topology/carrier no-go is already upstream"
        ),
        "validation_passed": bool(
            flrw["exact_constraint_residual"] == "0"
            and flrw["exact_evolution_residual"] == "0"
            and numerical["methods_agree"]
            and not berger["positive_scale_static_solution"]
        ),
    }


def topology_status_report() -> dict[str, Any]:
    topology = small_diffeomorphism_pi1_theorem()
    g2 = g2_selection_no_go()
    local = local_carrier_no_go()
    validation = {
        "configuration_space_fully_typed": all(
            configuration_space_definition()[key]
            for key in (
                "spacetime",
                "canonical_spatial_manifold",
                "orientation",
                "spin_structure",
                "regularity",
                "gauge_group",
            )
        ),
        "small_diff_pi1_trivial": topology["pi1_Q_geom_0"] == "0",
        "no_FR_character_fabricated": topology["nontrivial_FR_character"] is None,
        "large_diff_kept_separate": not large_diffeomorphism_audit()[
            "belongs_to_small_diff_quotient"
        ],
        "v6_6_mapping_space_not_promoted": not prior_fr_reconciliation()[
            "promotion_in_v9_1"
        ],
        "G2_selection_fails_closed": g2["eta_phi"] is None,
        "local_chiral_carrier_absent": local["local_spacetime_bundle"] is None,
    }
    return {
        "artifact": ARTIFACT_NAME,
        "version": VERSION,
        "sprint": SPRINT,
        "source_pr207_sha": SOURCE_PR207_SHA,
        "configuration_space": configuration_space_definition(),
        "configuration_space_strata": configuration_space_strata(),
        "small_diffeomorphism_pi1_theorem": topology,
        "large_diffeomorphism_audit": large_diffeomorphism_audit(),
        "prior_FR_reconciliation": prior_fr_reconciliation(),
        "candidate_loop_ledger": candidate_loop_ledger(),
        "G2_selection_no_go": g2,
        "local_carrier_no_go": local,
        "validation": validation,
        "validation_passed": all(validation.values()),
        "frozen_predictions_changed": False,
        "measured_flavor_data_used": False,
        "new_fundamental_fermion_added": False,
        "new_continuous_parameter_added": False,
        "physical_promotion": False,
        "final_verdict": FINAL_VERDICT,
        "next_missing_object": NEXT_MISSING_OBJECT,
    }


def topology_prediction_freeze() -> dict[str, Any]:
    payload = {
        "version": VERSION,
        "FR_line": None,
        "G2_polarization": None,
        "local_chiral_carrier": None,
        "physical_promotion": False,
        "frozen_historical_predictions_changed": False,
        "verdict": FINAL_VERDICT,
    }
    payload["sha256"] = sha256(deterministic_json(payload).encode("utf-8")).hexdigest().upper()
    return payload


__all__ = [
    "ARTIFACT_NAME",
    "FINAL_VERDICT",
    "NEXT_MISSING_OBJECT",
    "candidate_loop_ledger",
    "configuration_space_definition",
    "configuration_space_strata",
    "g2_selection_no_go",
    "large_diffeomorphism_audit",
    "local_carrier_no_go",
    "prior_fr_reconciliation",
    "small_diffeomorphism_pi1_theorem",
    "topology_prediction_freeze",
    "topology_status_report",
]
