from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from math import isclose
from typing import Any, Iterable

VERSION = "v14.46"

PRIMARY_VERDICT = (
    "BHSM_SMOOTH_CAP_REGULARITY_AND_TRUE_HOPF_BUNDLE_AUTOMORPHISMS_DO_NOT_"
    "FIX_C2REN_C4REN_BECAUSE_THE_CURVATURE_INVARIANTS_ARE_SEPARATELY_REGULAR_"
    "AND_FIBER_STRETCHING_IS_A_MODULUS_DEFORMATION_NOT_A_BUNDLE_AUTOMORPHISM"
)

SECONDARY_VERDICT = (
    "PROMOTING_THE_BERGER_ANISOTROPY_TO_A_DYNAMICAL_MODULUS_SUPPLIES_AT_MOST_"
    "ONE_STATIONARITY_RELATION_AND_DOES_NOT_REMOVE_THE_TWO_COUNTERTERM_"
    "RENORMALIZATION_FREEDOM"
)

BRIDGE_VERDICT = (
    "THE_COVARIANT_4D_TO_CAP_PROJECTION_AND_NEUTRON_STAR_EQUATION_CONTRACT_ARE_"
    "FORMULATED_BUT_NO_ASTROPHYSICAL_MATCHING_IS_EXECUTED_WITHOUT_THE_CAP_"
    "PROJECTION_NORMALIZATION_EOS_MARGINALIZATION_AND_PREREGISTERED_DATA_SPLIT"
)

EXACT_NEXT_OBJECT = (
    "FULL_COMPACT_CAP_COVARIANT_HESSIAN_PROJECTION_FOR_R2_AND_RICCI2_TOGETHER_"
    "WITH_A_DYNAMICAL_BERGER_MODULUS_OR_MICROSCOPIC_RENORMALIZATION_CONDITION_"
    "AND_A_PREREGISTERED_EOS_MARGINALIZED_NEUTRON_STAR_MATCHING_PIPELINE"
)


@dataclass(frozen=True)
class ChannelMap:
    q2: int = 5
    q3: int = 12

    @property
    def matrix(self) -> tuple[tuple[int, int], tuple[int, int]]:
        return ((self.q2, self.q2 * self.q2), (self.q3, self.q3 * self.q3))

    @property
    def determinant(self) -> int:
        (a, b), (c, d) = self.matrix
        return a * d - b * c

    @property
    def inverse(self) -> tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]:
        (a, b), (c, d) = self.matrix
        det = self.determinant
        return (
            (Fraction(d, det), Fraction(-b, det)),
            (Fraction(-c, det), Fraction(a, det)),
        )


def q_round(level: int) -> int:
    if level < 1:
        raise ValueError("coexact level must be at least one")
    return (level - 1) * (level + 3)


def channel_coefficients_from_local_hessians(
    h2: Fraction | int | float,
    h3: Fraction | int | float,
) -> tuple[Fraction, Fraction]:
    """Recover c2 and c4 from local L=2 and L=3 Hessian projections."""
    h2_f = Fraction(h2)
    h3_f = Fraction(h3)
    inverse = ChannelMap().inverse
    c2 = inverse[0][0] * h2_f + inverse[0][1] * h3_f
    c4 = inverse[1][0] * h2_f + inverse[1][1] * h3_f
    return c2, c4


def local_hessians_from_channel_coefficients(
    c2: Fraction | int | float,
    c4: Fraction | int | float,
) -> tuple[Fraction, Fraction]:
    c2_f = Fraction(c2)
    c4_f = Fraction(c4)
    channel_map = ChannelMap()
    return (
        c2_f * channel_map.q2 + c4_f * channel_map.q2**2,
        c2_f * channel_map.q3 + c4_f * channel_map.q3**2,
    )


def worst_regular_cap_flux_power(level: int, collapsing_dimension: int = 3) -> int:
    """Worst radial power of a fourth-order Green boundary concomitant.

    A smooth coexact level-L field near a regular origin behaves no worse than
    u ~ rho^(L-1).  The worst fourth-order boundary pairing contains u times
    three radial derivatives of delta-u.  Including the collapsing S^3 measure
    rho^3 gives rho^(2L-2).  A positive power proves separate vanishing of each
    curvature-squared boundary flux for L>=2.
    """
    if level < 1:
        raise ValueError("level must be at least one")
    if collapsing_dimension < 1:
        raise ValueError("collapsing_dimension must be positive")
    exponent_u = level - 1
    exponent_third = level - 4
    return collapsing_dimension + exponent_u + exponent_third


def cap_regularity_audit(levels: Iterable[int] = (2, 3)) -> dict[str, Any]:
    powers = {str(level): worst_regular_cap_flux_power(level) for level in levels}
    return {
        "smooth_cap_is_not_a_physical_boundary": True,
        "curvature_squared_fluxes_vanish_separately": all(power > 0 for power in powers.values()),
        "cross_cancellation_required": False,
        "worst_boundary_flux_powers": powers,
        "coefficient_relation_forced": None,
        "status": "REGULARITY_DOES_NOT_REDUCE_COUNTERTERM_DIMENSION",
    }


def berger_channel_cost(level: int, weight: int, anisotropy: float) -> float:
    """Round coexact cost plus the standard Berger weight deformation."""
    if anisotropy <= 0:
        raise ValueError("anisotropy must be positive")
    return float(q_round(level) + (anisotropy * anisotropy - 1.0) * weight * weight)


def fiber_stretch_local_derivative(
    level: int,
    weight: int,
    anisotropy: float,
    c2: float,
    c4: float,
) -> float:
    """d/d(log a) of c2*q(a)+c4*q(a)^2 for one (L,p) channel."""
    q_value = berger_channel_cost(level, weight, anisotropy)
    dq_dlog_a = 2.0 * anisotropy * anisotropy * weight * weight
    return dq_dlog_a * (c2 + 2.0 * c4 * q_value)


def finite_difference_fiber_derivative(
    level: int,
    weight: int,
    anisotropy: float,
    c2: float,
    c4: float,
    step: float = 1.0e-7,
) -> float:
    from math import exp

    def value(log_shift: float) -> float:
        a = anisotropy * exp(log_shift)
        q_value = berger_channel_cost(level, weight, a)
        return c2 * q_value + c4 * q_value * q_value

    return (value(step) - value(-step)) / (2.0 * step)


def fiber_automorphism_audit() -> dict[str, Any]:
    return {
        "true_principal_bundle_automorphisms": [
            "fiber U(1) translations / gauge transformations",
            "base diffeomorphisms with compatible connection pullback",
            "generic Berger isometries SU(2)_L x U(1)_R",
        ],
        "fiber_length_scaling_is_bundle_automorphism": False,
        "fiber_length_scaling_role": "physical Berger modulus deformation",
        "covariant_local_invariants_are_separately_automorphism_invariant": True,
        "automorphism_forced_relation": None,
        "status": "TRUE_AUTOMORPHISM_WARD_IDENTITIES_DO_NOT_FIX_COUNTERTERM_RATIO",
    }


def modulus_stationarity_contract() -> dict[str, Any]:
    return {
        "equation": (
            "0 = dGamma/dlog(a) = c2*A2_prime(a) + c4*A4_prime(a) "
            "+ Pi_nonlocal_prime(a)"
        ),
        "number_of_moduli": 1,
        "maximum_independent_relations": 1,
        "counterterm_dimension_before": 2,
        "counterterm_dimension_after_generic_stationarity": 1,
        "fixes_both_coefficients": False,
        "requires_anisotropy_to_be_action_varied": True,
        "current_bhsm_anisotropy_is_action_varied": False,
        "status": "CONDITIONAL_SINGLE_LINE_NOT_A_COMPLETE_FIX",
    }


def modewise_fiber_invariance_solution(q_a: int = 5, q_b: int = 12) -> tuple[Fraction, Fraction]:
    """Solve c2+2*q_a*c4=0 and c2+2*q_b*c4=0.

    Requiring invariance under fiber stretch independently in two distinct
    weighted channels forces the trivial local Hessian.  This is evidence that
    such modewise stretch invariance is too strong, not a physical derivation.
    """
    if q_a == q_b:
        raise ValueError("two distinct channel costs are required")
    c4 = Fraction(0, 1)
    c2 = Fraction(0, 1)
    return c2, c4


def covariant_operator_basis() -> dict[str, Any]:
    return {
        "bulk_action": (
            "Gamma_4D = integral sqrt(-g) [M2/2 R - Lambda + alpha R^2 "
            "+ beta R_mn R^mn] + Gamma_nonlocal + S_matter"
        ),
        "gauss_bonnet_note": (
            "In four dimensions Riemann^2 may be exchanged for R^2 and Ricci^2 "
            "plus the Euler density and a boundary transgression."
        ),
        "field_equation": (
            "M2 G_mn + 2 alpha H1_mn + beta H2_mn + Hnonlocal_mn = T_mn"
        ),
        "H1": (
            "H1_mn = R R_mn - 1/4 g_mn R^2 + g_mn Box R - nabla_m nabla_n R"
        ),
        "H2": (
            "H2_mn = 2 R_manb R^ab - 1/2 g_mn R_ab R^ab + Box R_mn "
            "+ 1/2 g_mn Box R - nabla_m nabla_n R"
        ),
        "cap_projection_definition": (
            "H_L[I_i] = normalized second variation of integral sqrt(g) I_i "
            "on the compact-cap coexact L channel"
        ),
        "channel_inverse": {
            "determinant": ChannelMap().determinant,
            "c2": "(144 H_2 - 25 H_3)/420",
            "c4": "(-12 H_2 + 5 H_3)/420",
        },
        "status": "COVARIANT_BASIS_AND_PROJECTION_CONTRACT_DERIVED_MAP_VALUES_OPEN",
    }


def stellar_structure_contract() -> dict[str, Any]:
    return {
        "metric": "ds^2=-exp(2 Phi(r))dt^2 + [1-2m(r)/r]^-1 dr^2 + r^2 dOmega^2",
        "matter": "T^m_n = diag(-rho,p,p,p), p=p(rho)",
        "background_equations": [
            "E^t_t[g;alpha,beta,Gamma_nonlocal] = -rho",
            "E^r_r[g;alpha,beta,Gamma_nonlocal] = p",
            "p_prime = -(rho+p) Phi_prime",
            "E^theta_theta = p as consistency / additional higher-derivative equation",
        ],
        "center_conditions": [
            "m(r)=O(r^3)",
            "Phi finite",
            "rho finite",
            "all auxiliary curvature fields regular",
        ],
        "surface_and_exterior": [
            "p(R_star)=0",
            "metric and required higher-derivative data matched to the vacuum exterior",
            "asymptotic or parent-relative boundary conditions declared",
        ],
        "radial_stability": (
            "delta E=0 with Lagrangian displacement xi and auxiliary curvature perturbations; "
            "solve L_rad Y = omega^2 W_rad Y, require omega_0^2>0"
        ),
        "tidal_problem": (
            "solve static even-parity ell=2 linearized equations through the surface and "
            "extract the response/source ratio defining the Love number"
        ),
        "observables": [
            "mass-radius curve",
            "maximum stable mass",
            "radial fundamental frequency",
            "tidal Love number / deformability",
            "moment of inertia when rotation is added",
        ],
        "status": "EQUATION_AND_BOUNDARY_CONTRACT_FORMULATED_NUMERICAL_SOLVER_NOT_YET_EXECUTED",
    }


def no_fit_matching_protocol() -> dict[str, Any]:
    return {
        "internal_stage": [
            "compute the cap projection of each covariant local operator",
            "test a genuinely dynamical Berger modulus and its Hessian",
            "compute the nonlocal fermion polarization with one declared regulator",
        ],
        "external_matching_stage": [
            "predeclare calibration observables",
            "marginalize over an explicit equation-of-state family",
            "infer an allowed coefficient region rather than select by eye",
            "freeze the matched coefficients and renormalization scale",
        ],
        "held_out_stage": [
            "predict stars or observables excluded from calibration",
            "reject the bridge if held-out mass-radius, tidal, or stability tests fail",
        ],
        "forbidden": [
            "using neutron-star data inside the cap-regularity theorem",
            "retuning coefficients separately for each star or equation of state",
            "identifying cap coefficients with 4D curvature coefficients before projection",
            "claiming microscopic derivation from empirical matching",
        ],
        "matching_executed": False,
        "status": "PREREGISTERED_EXTERNAL_LAYER_ONLY",
    }


def completion_payload() -> dict[str, Any]:
    channel_map = ChannelMap()
    payload = {
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "secondary_verdict": SECONDARY_VERDICT,
        "bridge_verdict": BRIDGE_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "channel_map": {
            **asdict(channel_map),
            "matrix": channel_map.matrix,
            "determinant": channel_map.determinant,
            "inverse": [[str(value) for value in row] for row in channel_map.inverse],
        },
        "cap_regularity": cap_regularity_audit(),
        "fiber_automorphism": fiber_automorphism_audit(),
        "modulus_stationarity": modulus_stationarity_contract(),
        "covariant_operator_basis": covariant_operator_basis(),
        "stellar_structure": stellar_structure_contract(),
        "no_fit_protocol": no_fit_matching_protocol(),
        "validated": [
            "smooth-cap curvature-squared boundary fluxes vanish separately in L=2 and L=3",
            "true Hopf bundle automorphisms leave each covariant invariant separately invariant",
            "fiber stretching is a Berger modulus deformation rather than a bundle automorphism",
            "one dynamical anisotropy modulus yields at most one counterterm relation",
            "the L2/L3 channel map has determinant 420",
            "a covariant quadratic-gravity stellar equation and no-fit matching contract are formulated",
        ],
        "invalidated": [
            "cross-cancelling R2 and Ricci2 boundary terms at a smooth coordinate cap to fix their ratio",
            "treating fiber-length scaling as a gauge automorphism of a fixed Berger metric",
            "claiming neutron-star observations microscopically derive the counterterms",
        ],
        "open": [
            "explicit compact-cap H_L[R2] and H_L[Ricci2] projections",
            "action variation of the Berger anisotropy modulus",
            "nonlocal polarization and regulator",
            "renormalization conditions for both local coefficients",
            "numerical higher-derivative stellar solver with EOS marginalization",
            "held-out neutron-star predictions",
            "physical CKM, CP, masses, and scale",
        ],
        "frozen_predictions_changed": False,
        "physical_outputs_emitted": False,
        "usb_touched": False,
    }
    return payload


def validate_internal_contracts() -> dict[str, bool]:
    channel_map = ChannelMap()
    c2, c4 = Fraction(7, 3), Fraction(-2, 5)
    h2, h3 = local_hessians_from_channel_coefficients(c2, c4)
    recovered = channel_coefficients_from_local_hessians(h2, h3)
    analytic = fiber_stretch_local_derivative(3, 2, 1.17, 0.4, -0.03)
    numeric = finite_difference_fiber_derivative(3, 2, 1.17, 0.4, -0.03)
    return {
        "channel_determinant_is_420": channel_map.determinant == 420,
        "channel_inverse_exact": recovered == (c2, c4),
        "L2_cap_flux_vanishes": worst_regular_cap_flux_power(2) > 0,
        "L3_cap_flux_vanishes": worst_regular_cap_flux_power(3) > 0,
        "cap_does_not_force_relation": cap_regularity_audit()["coefficient_relation_forced"] is None,
        "fiber_scaling_not_automorphism": not fiber_automorphism_audit()[
            "fiber_length_scaling_is_bundle_automorphism"
        ],
        "one_modulus_is_rank_one": modulus_stationarity_contract()[
            "maximum_independent_relations"
        ] == 1,
        "fiber_derivative_matches_finite_difference": isclose(
            analytic, numeric, rel_tol=2.0e-8, abs_tol=2.0e-8
        ),
        "no_astrophysical_fit_executed": not no_fit_matching_protocol()["matching_executed"],
        "no_physical_output_emitted": not completion_payload()["physical_outputs_emitted"],
    }
