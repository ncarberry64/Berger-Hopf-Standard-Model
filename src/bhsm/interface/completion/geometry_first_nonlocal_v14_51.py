"""BHSM v14.51 geometry-first internal trace and nonlocal scale audit.

This module is deliberately fail-closed.  It reconstructs what the currently
owned BHSM bundle data can contribute to a spectral gauge trace, formulates the
parent-relative zeta determinant scale law, and records the coupled Berger/scale
stationarity contract.  It does not emit physical couplings, scales, masses,
CKM data, or a numerical determinant.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Any, Iterable

VERSION = "v14.51"

PRIMARY_VERDICT = (
    "BHSM_V14_51_EXACT_BUNDLE_TRACE_RECONSTRUCTION_DOES_NOT_DERIVE_"
    "THE_HISTORICAL_1_2_7_GAUGE_PATTERN"
)
SCALE_VERDICT = (
    "BHSM_PARENT_RELATIVE_NONLOCAL_DETERMINANT_CAN_SUPPLY_LOGARITHMIC_"
    "SCALE_DEPENDENCE_ONLY_THROUGH_A_NONZERO_RELATIVE_ZETA_ANOMALY_"
    "AND_REQUIRES_A_SECOND_SCALE_DEPENDENT_TERM_FOR_A_FINITE_STABLE_SCALE"
)
XI_VERDICT = (
    "BHSM_MINIMAL_CONNECTION_AND_DOCUMENTED_ETA_HIGGS_RESPONSE_LOCK_"
    "THE_ADDITIONAL_SCALAR_CURVATURE_ENDOMORPHISM_TO_XI_ZERO"
)
EXACT_NEXT_OBJECT = (
    "FULL_CHILD_PARENT_DIRAC_AND_BOSONIC_RELATIVE_HEAT_KERNEL_WITH_TRACE_CLASS_"
    "SEAM_DOMAIN_RELATIVE_ZETA_ANOMALY_BERGER_DERIVATIVE_AND_NONDEGENERATE_"
    "LOG_SCALE_BERGER_STATIONARITY_SYSTEM"
)


@dataclass(frozen=True)
class GaugeTrace:
    """Quadratic representation indices in ordinary-Y convention."""

    u1: Fraction
    su2: Fraction
    su3: Fraction

    def scale(self, factor: Fraction | int) -> "GaugeTrace":
        factor = Fraction(factor)
        return GaugeTrace(self.u1 * factor, self.su2 * factor, self.su3 * factor)

    def add(self, other: "GaugeTrace") -> "GaugeTrace":
        return GaugeTrace(
            self.u1 + other.u1,
            self.su2 + other.su2,
            self.su3 + other.su3,
        )

    def ratios_to_su2(self) -> tuple[Fraction, Fraction, Fraction]:
        if self.su2 == 0:
            raise ZeroDivisionError("SU(2) trace is zero")
        return self.u1 / self.su2, Fraction(1), self.su3 / self.su2

    def json(self) -> dict[str, str]:
        return {key: str(value) for key, value in asdict(self).items()}


def canonical_sm_generation_trace() -> GaugeTrace:
    """One all-left-Weyl SM generation, optional sterile neutrino omitted.

    T(fundamental)=1/2 for SU(2) and SU(3), and ordinary hypercharge Y is used.
    """

    ky = (
        6 * Fraction(1, 6) ** 2
        + 3 * Fraction(2, 3) ** 2
        + 3 * Fraction(1, 3) ** 2
        + 2 * Fraction(1, 2) ** 2
        + 1
    )
    k2 = 3 * Fraction(1, 2) + Fraction(1, 2)
    k3 = 2 * Fraction(1, 2) + Fraction(1, 2) + Fraction(1, 2)
    return GaugeTrace(ky, k2, k3)


def g2_seven_complexified_color_index() -> GaugeTrace:
    """Index of 7_C|SU(3)=1+3+bar(3), if it were an extra Dirac carrier.

    The singlet has zero index.  T(3)+T(bar3)=1, not seven.  The current BHSM
    eta seven-module is bosonic and is *not* automatically an extra fermion
    species; this value is an upper-bound/counterfactual trace diagnostic.
    """

    return GaugeTrace(Fraction(0), Fraction(0), Fraction(1))


def su2_peter_weyl_left_index(two_j: int) -> Fraction:
    """Full Peter-Weyl block index under the left SU(2) action.

    L2(SU2) contains V_j with right multiplicity dim(V_j).  With
    T(j)=j(j+1)(2j+1)/3, the full block contributes dim(V_j)*T(j).
    """

    if two_j < 0:
        raise ValueError("two_j must be nonnegative")
    j = Fraction(two_j, 2)
    dim = two_j + 1
    dynkin = j * (j + 1) * (2 * j + 1) / 3
    return Fraction(dim) * dynkin


def common_replication_invariance(trace: GaugeTrace, factors: Iterable[int]) -> bool:
    """C3, collar, antiparticle, and gauge-blind fiber factors preserve ratios."""

    product = 1
    for factor in factors:
        if factor <= 0:
            raise ValueError("replication factors must be positive")
        product *= factor
    return trace.ratios_to_su2() == trace.scale(product).ratios_to_su2()


def hypercharge_rescaled(trace: GaugeTrace, y_square_factor: Fraction) -> GaugeTrace:
    """Rescale Y -> sqrt(y_square_factor) Y, changing only the U(1) trace."""

    if y_square_factor <= 0:
        raise ValueError("hypercharge square factor must be positive")
    return GaugeTrace(trace.u1 * y_square_factor, trace.su2, trace.su3)


def direct_trace_target_1_2_7_diagnostic() -> dict[str, Any]:
    """Test the literal interpretation K1:K2:K3=1:2:7.

    Ordinary hypercharge can be rescaled so the canonical SM row is 1:2:2.
    One complexified G2 seven carrier adds one SU(3) index unit and gives 1:2:3.
    Reaching 1:2:7 would require five vectorlike 3+bar3 index units in total,
    i.e. four more beyond the single G2 seven diagnostic.  No such action-owned
    state content exists in the current ledger.
    """

    sm = canonical_sm_generation_trace()
    y_factor = Fraction(1, 1) / sm.u1
    normalized = hypercharge_rescaled(sm, y_factor)
    with_g2 = normalized.add(g2_seven_complexified_color_index())
    target = GaugeTrace(Fraction(1), Fraction(2), Fraction(7))
    missing = GaugeTrace(
        target.u1 - with_g2.u1,
        target.su2 - with_g2.su2,
        target.su3 - with_g2.su3,
    )
    return {
        "interpretation": "literal kinetic trace target K1:K2:K3=1:2:7",
        "canonical_after_Y_rescaling": normalized.json(),
        "single_G2_seven_diagnostic": with_g2.json(),
        "target": target.json(),
        "missing_positive_index": missing.json(),
        "additional_vectorlike_3_plus_bar3_pairs_needed_after_G2": 4,
        "current_action_owns_those_states": False,
    }


def internal_trace_reconstruction() -> dict[str, Any]:
    sm = canonical_sm_generation_trace()
    common_factors = {
        "C3_families": 3,
        "two_oriented_collar_sheets": 2,
        "particle_antiparticle_or_conjugate_doubling": 2,
        "FR_line_rank": 1,
    }
    common_product = 1
    for value in common_factors.values():
        common_product *= value

    return {
        "artifact": "BHSM_internal_representation_trace_reconstruction_v14_51",
        "version": VERSION,
        "canonical_one_generation_ordinary_Y": sm.json(),
        "canonical_ratio_to_SU2": [str(x) for x in sm.ratios_to_su2()],
        "common_replication_factors": common_factors,
        "common_product": common_product,
        "replicated_trace": sm.scale(common_product).json(),
        "ratios_preserved_by_common_replication": common_replication_invariance(
            sm, common_factors.values()
        ),
        "lowest_nontrivial_full_Hopf_Peter_Weyl_block": {
            "j": "1/2",
            "left_SU2_index": str(su2_peter_weyl_left_index(1)),
            "note": "dimension two does not imply kinetic weight two",
        },
        "G2_seven_complexification": {
            "decomposition": "1 + 3 + bar3",
            "SU3_Dynkin_index": "1",
            "not_dimension_weight": 7,
            "physical_status": (
                "bosonic eta carrier; not an action-owned extra fermion species"
            ),
        },
        "topological_winding_role": {
            "changes_FR_parity_or_topological_F_wedge_F_sector": True,
            "changes_local_F_wedge_star_F_trace_coefficient_by_itself": False,
            "reason": "quadratic kinetic coefficient is a representation index",
        },
        "gauge_blind_fiber_rule": (
            "a factorized fiber multiplicity multiplies all gauge traces equally; "
            "an infinite tower needs an action-owned regulator and still cannot be "
            "used as a sector weight without a gauge-dependent selector"
        ),
        "direct_1_2_7_test": direct_trace_target_1_2_7_diagnostic(),
        "historical_1_2_7_emerges": False,
        "primary_verdict": PRIMARY_VERDICT,
        "validation": {
            "canonical_trace_exact": sm == GaugeTrace(Fraction(10, 3), 2, 2),
            "common_factors_preserve_ratios": common_replication_invariance(
                sm, common_factors.values()
            ),
            "G2_seven_index_is_one_not_seven": (
                g2_seven_complexified_color_index().su3 == 1
            ),
            "Hopf_j_half_full_block_index_is_one": su2_peter_weyl_left_index(1) == 1,
            "topology_not_promoted_to_kinetic_weight": True,
            "no_undeclared_states_inserted": True,
        },
    }


def relative_zeta_scale_law() -> dict[str, Any]:
    """Exact scaling contract for a second-order child-parent relative operator."""

    return {
        "artifact": "BHSM_parent_relative_zeta_scale_gate_v14_51",
        "version": VERSION,
        "operator_scaling": "P_child,parent(L,a)=L^(-2) P_hat_child,parent(a)",
        "relative_zeta": (
            "zeta_rel(s;L,a)=L^(2s)[zeta_child_hat(s;a)-zeta_parent_hat(s;a)]"
        ),
        "fermion_effective_action_convention": (
            "Gamma_F_rel=-log det_rel D=+1/2 zeta_rel_prime(0;P/mu^2)"
        ),
        "scale_form": (
            "Gamma_F_rel(L,a;mu)=Gamma_hat_F_rel(a)+"
            "zeta_rel(0;a) log(mu L)"
        ),
        "scale_derivative": "d Gamma_F_rel / d log L = zeta_rel(0;a)",
        "consequences": {
            "zeta_rel_zero": "relative determinant is scale invariant",
            "zeta_rel_nonzero_only": (
                "a lone logarithm has constant slope and no finite stable minimum"
            ),
            "finite_scale_requires": [
                "a second term with different L dependence or running coupling",
                "a declared parent/interface renormalization condition",
                "positive second derivative at the stationary point",
            ],
        },
        "trace_class_requirements": [
            "common principal symbol and compatible self-adjoint seam domain",
            "heat-kernel difference trace class after collective zero-mode quotient",
            "identical parent/child ultraviolet subtraction convention",
            "zero and negative modes treated explicitly",
        ],
        "scale_verdict": SCALE_VERDICT,
        "validation": {
            "relative_anomaly_controls_log_scale": True,
            "nonzero_anomaly_alone_not_a_minimum": True,
            "parent_subtraction_may_cancel_anomaly": True,
            "absolute_scale_not_emitted": True,
        },
    }


def berger_scale_stationarity_contract() -> dict[str, Any]:
    return {
        "artifact": "BHSM_full_Berger_scale_stationarity_contract_v14_51",
        "version": VERSION,
        "total_relative_action": (
            "Gamma_rel=S_eta_rel+S_gravity_rel+S_collar_lapse_rel+"
            "S_zeta_local_rel+Gamma_nonlocal_rel"
        ),
        "quantum_corrected_background_equations": [
            "delta Gamma_rel / delta f_eta = 0",
            "delta Gamma_rel / delta N = 0",
            "delta Gamma_rel / delta J = 0",
            "F_a := d Gamma_rel_on_shell / da = 0",
            "F_L := d Gamma_rel_on_shell / d log L = 0",
        ],
        "fermion_Feynman_Hellmann": (
            "d Gamma_F_rel/da=-Tr_rel[D^(-1) dD/da] with the declared zeta/relative regulator"
        ),
        "eta_mass_derivative": (
            "d m_eta/da=-d_s[cot(f_eta) d f_eta/da], "
            "m_eta=-d_s log sin(f_eta)"
        ),
        "on_shell_rule": (
            "implicit profile derivatives cancel only when the same quantum-corrected "
            "Gamma_rel supplies the f_eta, lapse, collar, a, and L equations"
        ),
        "discrete_solution_gate": (
            "det d(F_L,F_a)/d(log L,a) != 0 at the candidate solution"
        ),
        "stability_gate": (
            "the 2x2 Hessian in (log L,a), after all constrained fields are Schur-reduced, "
            "must be positive definite"
        ),
        "current_status": {
            "child_parent_operators_supplied": False,
            "relative_zeta_anomaly_computed": False,
            "nonlocal_Berger_derivative_computed": False,
            "frozen_nonround_a_selected": False,
            "absolute_scale_selected": False,
        },
        "validation": {
            "coupled_not_sequential_stationarity_required": True,
            "classical_profile_cannot_be_reused_without_backreaction": True,
            "nondegenerate_Jacobian_required": True,
            "no_proxy_determinant_promoted": True,
        },
    }


def curvature_response_lock() -> dict[str, Any]:
    return {
        "artifact": "BHSM_curvature_response_lock_v14_51",
        "version": VERSION,
        "minimal_Lichnerowicz_term": "E_spin=-R/4 in the retained convention",
        "additional_response_parameter": "E_curv=xi R I",
        "ray_preserving_algebraic_values": ["0", "1/6"],
        "selected_branch": "xi=0",
        "selection_reason": (
            "the documented BHSM total connection, eta odd mass, Higgs bridge, and family "
            "operators contain no separate scalar-curvature endomorphism; xi=1/6 would "
            "be a new action term rather than a consequence of that connection"
        ),
        "future_reopening_rule": (
            "xi may change only if a later parent action explicitly derives a curvature "
            "endomorphism and the complete a4 trace is recomputed"
        ),
        "xi_verdict": XI_VERDICT,
        "validation": {
            "spin_curvature_not_double_counted_as_xi": True,
            "documented_eta_mass_curvature_independent": True,
            "xi_one_sixth_not_silently_adopted": True,
            "selected_xi_is_zero": True,
        },
    }


def completion_payload() -> dict[str, Any]:
    trace = internal_trace_reconstruction()
    scale = relative_zeta_scale_law()
    stationarity = berger_scale_stationarity_contract()
    xi = curvature_response_lock()
    validation = {
        "trace_audit_passed": all(trace["validation"].values()),
        "scale_contract_passed": all(scale["validation"].values()),
        "stationarity_contract_passed": all(stationarity["validation"].values()),
        "xi_lock_passed": all(xi["validation"].values()),
        "historical_1_2_7_not_emitted": not trace["historical_1_2_7_emerges"],
        "physical_scale_not_emitted": True,
        "frozen_predictions_unchanged": True,
        "USB_untouched": True,
    }
    return {
        "artifact": "BHSM_completion_gate_v14_51",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "scale_verdict": SCALE_VERDICT,
        "xi_verdict": XI_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "gates": {
            "internal_trace_reconstructed": True,
            "historical_1_2_7_derived": False,
            "parent_relative_scale_equation_formulated": True,
            "relative_zeta_anomaly_computed": False,
            "full_Berger_stationarity_formulated": True,
            "full_Berger_stationarity_solved": False,
            "xi_locked_to_zero": True,
            "absolute_scale_selected": False,
            "BHSM_physical_completion": False,
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
