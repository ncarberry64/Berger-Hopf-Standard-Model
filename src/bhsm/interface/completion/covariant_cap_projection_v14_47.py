"""BHSM v14.47 covariant compact-cap curvature projection.

This module records a structural theorem for stationary, transverse coexact
shift modes on an ultrastatic compact S^3 cap.  It deliberately keeps overall
normalization constants symbolic: no physical counterterm value is emitted.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

VERSION = "v14.47"
PRIMARY_VERDICT = (
    "BHSM_COVARIANT_R2_AND_RICCI2_COMPACT_CAP_PROJECTION_REMAINS_"
    "RANK_TWO_IN_THE_L2_L3_COEXACT_SECTOR"
)
SECONDARY_VERDICT = (
    "CAP_REGULARITY_AND_ONE_BERGER_MODULUS_EQUATION_DO_NOT_FIX_THE_TWO_"
    "RENORMALIZED_LOCAL_GRAVITATIONAL_COEFFICIENTS"
)
EXACT_NEXT_OBJECT = (
    "MICROSCOPIC_OR_TWO_CONDITION_RENORMALIZATION_PRESCRIPTION_FIXING_THE_"
    "TWO_LOCAL_CURVATURE_COEFFICIENTS_TOGETHER_WITH_NORMALIZED_L2_L3_"
    "KOSMANN_SPECTRAL_SUMS_OR_PREREGISTERED_NEUTRON_STAR_MATCHING"
)


def q_l(level: int) -> int:
    """Round-S3 coexact shift eigenvalue numerator q_L=(L-1)(L+3)."""
    if level < 1:
        raise ValueError("coexact level must be >= 1")
    return (level - 1) * (level + 3)


@dataclass(frozen=True)
class ProjectionColumn:
    level: int
    q: int
    r2: float
    ricci2: float


def projection_row(
    level: int,
    *,
    a_r2: float = 1.0,
    b_ricci2: float = 0.0,
    c_ricci2: float = 1.0,
) -> ProjectionColumn:
    """Return the symbolic-normalized local projection row.

    Structural form:
      H_L[R^2]       = A q_L
      H_L[Ricci^2]   = B q_L + C q_L^2

    A is nonzero on the curved S3 background. C is nonzero because the
    squared first-order mixed Ricci/momentum-constraint block contributes a
    four-spatial-derivative term. B depends on detailed convention and lower
    derivative background terms; it is irrelevant to the rank theorem.
    """
    q = q_l(level)
    return ProjectionColumn(
        level=level,
        q=q,
        r2=a_r2 * q,
        ricci2=b_ricci2 * q + c_ricci2 * q * q,
    )


def two_channel_determinant(
    level_a: int = 2,
    level_b: int = 3,
    *,
    a_r2: float = 1.0,
    b_ricci2: float = 0.0,
    c_ricci2: float = 1.0,
) -> float:
    """Determinant of the two-operator/two-channel projection matrix."""
    row_a = projection_row(
        level_a, a_r2=a_r2, b_ricci2=b_ricci2, c_ricci2=c_ricci2
    )
    row_b = projection_row(
        level_b, a_r2=a_r2, b_ricci2=b_ricci2, c_ricci2=c_ricci2
    )
    return row_a.r2 * row_b.ricci2 - row_b.r2 * row_a.ricci2


def determinant_factor(level_a: int = 2, level_b: int = 3) -> int:
    """Integer factor multiplying A*C in the structural determinant."""
    qa, qb = q_l(level_a), q_l(level_b)
    return qa * qb * (qb - qa)


def solve_local_coefficients(
    target_a: float,
    target_b: float,
    *,
    level_a: int = 2,
    level_b: int = 3,
    a_r2: float = 1.0,
    b_ricci2: float = 0.0,
    c_ricci2: float = 1.0,
) -> tuple[float, float]:
    """Invert the structural projection when A*C is nonzero.

    Targets are local-channel Hessian contributions after subtracting any
    nonlocal polarization. Values are diagnostic only unless a physical
    renormalization prescription supplies the targets.
    """
    det = two_channel_determinant(
        level_a,
        level_b,
        a_r2=a_r2,
        b_ricci2=b_ricci2,
        c_ricci2=c_ricci2,
    )
    if abs(det) < 1e-15:
        raise ValueError("projection is singular")
    ra = projection_row(
        level_a, a_r2=a_r2, b_ricci2=b_ricci2, c_ricci2=c_ricci2
    )
    rb = projection_row(
        level_b, a_r2=a_r2, b_ricci2=b_ricci2, c_ricci2=c_ricci2
    )
    c_r2 = (target_a * rb.ricci2 - target_b * ra.ricci2) / det
    c_ricci2 = (ra.r2 * target_b - rb.r2 * target_a) / det
    return c_r2, c_ricci2


def berger_modulus_constraint(
    derivative_r2: float,
    derivative_ricci2: float,
    derivative_nonlocal: float,
) -> dict[str, object]:
    """One stationarity equation from one dynamical Berger modulus."""
    rank = 0 if abs(derivative_r2) + abs(derivative_ricci2) < 1e-15 else 1
    return {
        "equation": (
            "dA2_da*c_R2 + dA4_da*c_Ricci2 + dPi_nonlocal_da = 0"
        ),
        "coefficients": [derivative_r2, derivative_ricci2],
        "source": -derivative_nonlocal,
        "constraint_rank": rank,
        "remaining_parameter_dimension": 2 - rank,
    }


def covariant_projection_contract() -> dict[str, object]:
    rows = [projection_row(2), projection_row(3)]
    factor = determinant_factor(2, 3)
    return {
        "artifact": "BHSM_covariant_cap_projection_v14_47",
        "version": VERSION,
        "background": "ultrastatic_R_times_round_S3_compact_cap",
        "sector": "stationary_transverse_coexact_shift",
        "operator_basis": ["R_squared", "Ricci_tensor_squared"],
        "structural_projection": {
            "R_squared": "A*q_L",
            "Ricci_tensor_squared": "B*q_L + C*q_L^2",
            "q_L": "(L-1)(L+3)",
            "A_nonzero_reason": (
                "curved S3 background times the second-order scalar-curvature/"
                "Einstein shift form"
            ),
            "C_nonzero_reason": (
                "square of the first-order mixed Ricci momentum-constraint block"
            ),
            "B_role": "lower-derivative convention/background term; rank independent",
        },
        "normalized_witness_rows": [asdict(row) for row in rows],
        "determinant": "A*C*q2*q3*(q3-q2)",
        "determinant_integer_factor_L2_L3": factor,
        "rank_two_when": "A != 0 and C != 0",
        "cap_regularity_fixes_ratio": False,
        "one_berger_modulus_fixes_both": False,
        "primary_verdict": PRIMARY_VERDICT,
        "secondary_verdict": SECONDARY_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "physical_counterterm_values_emitted": False,
    }


def neutron_star_preregistration_contract() -> dict[str, object]:
    return {
        "artifact": "BHSM_neutron_star_matching_preregistration_v14_47",
        "version": VERSION,
        "status": "PROTOCOL_ONLY_NOT_EXECUTED",
        "required_upstream": [
            "physical covariant coefficient normalization and scale",
            "well-posed higher-derivative stellar boundary value problem",
            "EOS family and prior declared before data evaluation",
            "vacuum exterior and junction conditions",
            "radial-stability and tidal-response solvers",
        ],
        "calibration_layer": [
            "predeclared subset of mass-radius likelihoods",
            "predeclared subset of tidal likelihoods",
            "EOS hyperparameters marginalized, not fixed post hoc",
        ],
        "held_out_layer": [
            "unused stellar radius or moment-of-inertia observable",
            "unused tidal-deformability event",
            "maximum-mass and radial-stability checks",
        ],
        "kill_screens": [
            "star-by-star counterterm retuning",
            "EOS choice selected after seeing BHSM residuals",
            "regularity or causality failure",
            "negative fundamental radial mode on the claimed stable branch",
            "failure of held-out observables after coefficient freeze",
            "incompatibility with compact-cap projection normalization",
        ],
        "may_bound_coefficients": True,
        "may_define_declared_renormalization_conditions": True,
        "counts_as_microscopic_derivation": False,
        "observational_values_loaded": False,
    }


def completion_gate() -> dict[str, object]:
    projection = covariant_projection_contract()
    prereg = neutron_star_preregistration_contract()
    return {
        "artifact": "BHSM_completion_gate_v14_47",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "secondary_verdict": SECONDARY_VERDICT,
        "validated": [
            "R2 has no independent q_L^2 column in the stationary transverse sector",
            "Ricci2 retains a nonzero q_L^2 column",
            "L2/L3 local projection is structurally rank two",
            "the determinant factor is 420 independent of the Ricci2 q_L term",
            "one Berger modulus equation has rank at most one",
            "a no-fit neutron-star matching protocol is defined",
        ],
        "invalidated": [
            "the hope that exact covariant projection automatically collapses the two local coefficients",
            "using smooth-cap regularity as a second renormalization condition",
            "calling neutron-star matching a microscopic derivation",
        ],
        "open": [
            "physical A/B/C normalization on the full compact cap",
            "microscopic or two-condition renormalization prescription",
            "normalized L2/L3 Kosmann spectral sums",
            "higher-derivative stellar solver and EOS-marginalized inference",
            "zero crossing, nonlinear branch, CKM and CP",
        ],
        "projection_rank_two": projection["rank_two_when"],
        "neutron_star_protocol_status": prereg["status"],
        "exact_next_object": EXACT_NEXT_OBJECT,
        "BHSM_complete": False,
        "frozen_predictions_changed": False,
        "usb_touched": False,
    }
