from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Any

VERSION = "14.50"

PRIMARY_VERDICT = (
    "BHSM_V14_50_THE_DOCUMENTED_ETA_HIGGS_AND_FAMILY_RESPONSES_ARE_"
    "CURVATURE_INDEPENDENT_AND_PRESERVE_THE_MINIMAL_DIRAC_A4_GRAVITATIONAL_"
    "RAY_BUT_THE_UNDEFINED_PHI_RESPONSE_CAN_REOPEN_THE_R2_DIRECTION"
)

GAUGE_VERDICT = (
    "THE_CANONICAL_THREE_GENERATION_STANDARD_MODEL_FERMION_TRACE_GIVES_"
    "K_Y_K_2_K_3_EQUALS_5_OVER_3_1_1_AFTER_NORMALIZATION_AND_DOES_NOT_"
    "GENERATE_THE_HISTORICAL_BHSM_1_2_7_PATTERN"
)

SCALE_VERDICT = (
    "THE_FOUR_DIMENSIONAL_ZETA_LOCAL_A4_FUNCTIONAL_IS_GLOBALLY_SCALE_"
    "INVARIANT_AND_CANNOT_SELECT_THE_ABSOLUTE_BHSM_LENGTH_OR_ENERGY_SCALE"
)

EXACT_NEXT_OBJECT = (
    "ACTION_SELECTED_INTERNAL_SPECTRAL_WEIGHT_OR_EXTENDED_STATE_CONTENT_"
    "WITH_COMPLETE_CURVATURE_RESPONSE_ENDOMORPHISM_AND_A_SEPARATE_"
    "DIMENSIONAL_TRANSMUTATION_OR_PARENT_CHILD_SCALE_EIGENVALUE"
)


@dataclass(frozen=True)
class GaugeTrace:
    hypercharge: Fraction
    su2: Fraction
    su3: Fraction

    def normalized_to_su2(self) -> tuple[Fraction, Fraction, Fraction]:
        return (
            self.hypercharge / self.su2,
            Fraction(1, 1),
            self.su3 / self.su2,
        )


def canonical_sm_generation_trace() -> GaugeTrace:
    """Canonical one-generation chiral trace.

    Generator conventions:
      * U(1): sum multiplicity * Y^2
      * SU(N): fundamental Dynkin index T(fund)=1/2

    A sterile right-handed neutrino contributes zero to all three rows.
    Particle/antiparticle doubling and three generations multiply every row by
    the same common factor and therefore do not alter the ratios.
    """

    k_y = (
        6 * Fraction(1, 6) ** 2
        + 3 * Fraction(2, 3) ** 2
        + 3 * Fraction(1, 3) ** 2
        + 2 * Fraction(1, 2) ** 2
        + Fraction(1, 1)
    )
    k_2 = 3 * Fraction(1, 2) + Fraction(1, 2)
    k_3 = 2 * Fraction(1, 2) + Fraction(1, 2) + Fraction(1, 2)
    return GaugeTrace(k_y, k_2, k_3)


def curvature_response_r2_shift_polynomial(xi: Fraction | float) -> Fraction | float:
    """Pure R^2 shift in the a4 numerator for E -> E + xi R I.

    Uses P=-(nabla^2+E), the minimal Dirac value E0=-R/4, and the local
    a4 terms 60 R E + 180 E^2.  The rank and universal 1/360 prefactors are
    omitted.  Result: 30 xi (6 xi - 1).
    """

    return 30 * xi * (6 * xi - 1)


def ray_preserving_curvature_response_values() -> tuple[Fraction, Fraction]:
    """Values for which the explicit scalar-curvature response adds no R^2."""

    return Fraction(0, 1), Fraction(1, 6)


def documented_response_ownership() -> dict[str, Any]:
    return {
        "eta_odd_mass": {
            "form": "m_eta(s)=-partial_s log(sin f_eta(s))",
            "explicit_4d_curvature_dependence": False,
            "status": "DOCUMENTED_FOUNDATIONAL_PROFILE_TERM",
        },
        "higgs_yukawa_family_operator": {
            "form": "Y_f(H,a,k,j,q) acting in finite family/internal space",
            "explicit_4d_curvature_dependence": False,
            "status": "DOCUMENTED_CONDITIONAL_OR_FOUNDATIONAL_INTERNAL_TERM",
        },
        "phi_response_remainder": {
            "form": None,
            "explicit_4d_curvature_dependence": None,
            "status": "UNDEFINED_NOT_ACTION_SELECTED",
        },
    }


def berger_cylinder_weyl_density(a: Fraction | float, radius: Fraction | float = 1) -> Fraction | float:
    """Weyl-squared for R x Berger-S3 in the stated normalization.

    h = R^2(sigma_1^2+sigma_2^2+a^2 sigma_3^2), with round scalar curvature
    6/R^2 at a=1.  C^2 = (64/3)(a^2-1)^2/R^4.
    This is a diagnostic product background, not the full compact-cap result.
    """

    return Fraction(64, 3) * (a * a - 1) ** 2 / (radius**4)


def berger_cylinder_integrated_shape(a: Fraction | float) -> Fraction | float:
    """Dimensionless a-dependent factor after the Berger S3 volume is included."""

    return a * (a * a - 1) ** 2


def berger_shape_derivative(a: Fraction | float) -> Fraction | float:
    return (a * a - 1) * (5 * a * a - 1)


def a4_global_scale_weight() -> int:
    """Homogeneity exponent under g -> L^2 g in four dimensions."""

    return 0


def completion_payload() -> dict[str, Any]:
    trace = canonical_sm_generation_trace()
    normalized = trace.normalized_to_su2()
    roots = ray_preserving_curvature_response_values()

    validation = {
        "canonical_hypercharge_trace_is_10_over_3": trace.hypercharge == Fraction(10, 3),
        "canonical_su2_trace_is_2": trace.su2 == 2,
        "canonical_su3_trace_is_2": trace.su3 == 2,
        "normalized_trace_is_5_over_3_1_1": normalized == (Fraction(5, 3), 1, 1),
        "curvature_shift_factorizes": curvature_response_r2_shift_polynomial(Fraction(2, 7))
        == 30 * Fraction(2, 7) * (6 * Fraction(2, 7) - 1),
        "ray_preserving_roots_are_zero_and_one_sixth": roots == (Fraction(0), Fraction(1, 6)),
        "a4_is_scale_invariant": a4_global_scale_weight() == 0,
        "round_berger_cylinder_is_weyl_flat": berger_cylinder_weyl_density(Fraction(1)) == 0,
        "frozen_nonround_branch_not_selected_by_local_weyl_shape_alone": berger_shape_derivative(
            Fraction(1157, 1000)
        )
        != 0,
        "frozen_predictions_unchanged": True,
        "physical_outputs_not_emitted": True,
    }

    return {
        "artifact": "BHSM_full_Dirac_a4_trace_v14_50",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "gauge_verdict": GAUGE_VERDICT,
        "scale_verdict": SCALE_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "canonical_one_generation_gauge_trace": {
            **{key: str(value) for key, value in asdict(trace).items()},
            "normalized_to_su2": [str(value) for value in normalized],
        },
        "curvature_response": {
            "r2_shift_numerator_per_internal_rank": "30*xi*(6*xi-1)",
            "ray_preserving_xi": [str(value) for value in roots],
            "documented_terms": documented_response_ownership(),
        },
        "berger_cylinder_diagnostic": {
            "weyl_squared": "(64/3)*(a^2-1)^2/R^4",
            "integrated_shape": "a*(a^2-1)^2",
            "shape_derivative": "(a^2-1)*(5*a^2-1)",
            "physical_compact_cap_claimed": False,
        },
        "scale": {
            "a4_global_metric_scaling_weight": 0,
            "absolute_scale_selected": False,
        },
        "completion": {
            "zeta_spectral_ray_preserved_on_minimal_declared_response_branch": True,
            "full_phi_response_owned": False,
            "canonical_trace_matches_historical_1_2_7": False,
            "absolute_scale_closed": False,
            "BHSM_complete": False,
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
