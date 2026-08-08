"""BHSM v14.49 zeta-spectral-ray and input-compression theorem.

This module records a conditional foundational branch.  It does not claim that
Path B derives a spectral action.  It proves what follows *if* the local
bosonic dimension-four action is selected by the a4 coefficient of the
foundational Dirac-type operator with curvature-independent response
endomorphism in the pure gravitational block.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Any

VERSION = "14.49"
Q_LEVELS = {2: 5, 3: 12}


@dataclass(frozen=True)
class SpectralRay:
    """Representative of the pure Dirac a4 dynamical curvature ray.

    In four dimensions,

        C^2 = E4 + 2 Ric^2 - (2/3) R^2,

    so modulo the Euler density E4 the dynamical coefficients can be represented
    by (-2/3, 2).  Multiplication by an overall spectral normalization is left
    explicit.
    """

    c_r2: Fraction = Fraction(-2, 3)
    c_ricci2: Fraction = Fraction(2, 1)

    @property
    def linear_constraint(self) -> Fraction:
        return 3 * self.c_r2 + self.c_ricci2

    def scaled(self, amplitude: Fraction | int | float) -> tuple[float, float]:
        a = float(amplitude)
        return a * float(self.c_r2), a * float(self.c_ricci2)


def q_level(level: int) -> int:
    """Return q_L=(L-1)(L+3) for a coexact shift level."""

    if level < 1:
        raise ValueError("level must be at least 1")
    return (level - 1) * (level + 3)


def generic_counterterm_matrix() -> tuple[tuple[int, int], tuple[int, int]]:
    """The normalized generic (q,q^2) L=2,3 map."""

    q2, q3 = q_level(2), q_level(3)
    return ((q2, q2 * q2), (q3, q3 * q3))


def determinant_2x2(matrix: tuple[tuple[float, float], tuple[float, float]]) -> float:
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def cap_channel_on_spectral_ray(
    level: int,
    *,
    amplitude: float,
    a_r2: float,
    b_ricci2: float,
    c_ricci2: float,
) -> float:
    """Project the one-parameter spectral curvature ray into one cap channel.

    The v14.47 structural projection is

        H_L[R^2] = A q_L,
        H_L[Ric^2] = B q_L + C q_L^2.

    The pure Dirac a4 ray is c_R2=-2s/3, c_Ric2=2s.
    """

    q = float(q_level(level))
    return amplitude * (
        -Fraction(2, 3) * a_r2 * q
        + 2.0 * (b_ricci2 * q + c_ricci2 * q * q)
    )


def cap_ray_vector(
    *,
    amplitude: float,
    a_r2: float,
    b_ricci2: float,
    c_ricci2: float,
) -> tuple[float, float]:
    return tuple(
        cap_channel_on_spectral_ray(
            level,
            amplitude=amplitude,
            a_r2=a_r2,
            b_ricci2=b_ricci2,
            c_ricci2=c_ricci2,
        )
        for level in (2, 3)
    )  # type: ignore[return-value]


def solve_berger_spectral_amplitude(
    *,
    pi_prime: float,
    local_ray_derivative: float,
) -> float:
    """Solve the single Berger-modulus stationarity equation for the ray amplitude.

        0 = s * dA_ray/dlog(a) + Pi'(a).

    This is only meaningful after both derivatives are evaluated from the same
    action and common self-adjoint domain.
    """

    if local_ray_derivative == 0.0:
        raise ZeroDivisionError("Berger stationarity is degenerate on this spectral ray")
    return -pi_prime / local_ray_derivative


def cutoff_spectral_moment_rank() -> dict[str, Any]:
    """Return the independent moment structure of a generic 4D cutoff action."""

    return {
        "asymptotic_terms": [
            "f4*Lambda^4*a0",
            "f2*Lambda^2*a2",
            "f0*a4",
        ],
        "independent_cutoff_moments": 3,
        "dimension_four_local_terms_share_f0": True,
        "cutoff_function_not_selected_by_current_BHSM_action": True,
    }


def zeta_local_branch_contract() -> dict[str, Any]:
    """Claim-safe contract for the zero-cutoff-moment zeta-local branch."""

    ray = SpectralRay()
    return {
        "version": VERSION,
        "branch_type": "FOUNDATIONAL_CONDITIONAL_ZETA_LOCAL_ACTION",
        "local_action": "S_zeta,local := a4(D_BHSM^2) after collective zero-mode quotient",
        "required_conditions": [
            "a fully specified foundational Dirac-type operator and bundle trace",
            "curvature-independent response endomorphism in the pure gravity coefficient audit",
            "one common parent spin/gauge bundle and common-domain regulator",
            "relative parent/composite subtraction and zero-mode bookkeeping",
            "Euclidean sign convention chosen so the gauge kinetic form is positive",
        ],
        "pure_gravity_dynamic_ray": {
            "c_R2": str(ray.c_r2),
            "c_Ricci2": str(ray.c_ricci2),
            "constraint": "3*c_R2 + c_Ricci2 = 0 modulo Euler density",
        },
        "input_compression": {
            "generic_effective_inputs": [
                "c_R2^ren(mu*)",
                "c_Ricci2^ren(mu*)",
                "c_YM(mu*)",
                "L_* or E_*",
            ],
            "cutoff_spectral_branch": [
                "f0 or equivalent overall dimension-four spectral normalization",
                "f2*Lambda^2 or an independently normalized Einstein scale",
                "physical scale/matching prescription",
            ],
            "canonical_zeta_local_declaration": [
                "physical scale/matching prescription",
            ],
        },
        "not_derived": [
            "the choice of zeta-local action itself",
            "the complete BHSM Dirac endomorphism and species trace",
            "the Berger-modulus nonlocal derivative",
            "the absolute dimensionful scale",
            "the L=2,L=3 zero crossing, nonlinear branch, CKM or CP",
        ],
    }


def status_payload() -> dict[str, Any]:
    ray = SpectralRay()
    generic = generic_counterterm_matrix()
    return {
        "artifact": "BHSM_zeta_spectral_ray_v14_49",
        "version": VERSION,
        "primary_verdict": (
            "BHSM_A_CURVATURE_INDEPENDENT_DIRAC_TYPE_A4_OR_ZETA_LOCAL_ACTION_"
            "COLLAPSES_THE_R2_RICCI2_AND_GAUGE_DIMENSION_FOUR_COEFFICIENTS_"
            "TO_ONE_SPECTRAL_RAY_BUT_THIS_IS_FOUNDATIONAL_DATA_NOT_DERIVED_"
            "FROM_PATH_B"
        ),
        "secondary_verdict": (
            "THE_PURE_DIRAC_GRAVITATIONAL_A4_VARIATION_OBEYS_3_C_R2_PLUS_"
            "C_RICCI2_EQUALS_ZERO_MODULO_GAUSS_BONNET_AND_ONE_NONDEGENERATE_"
            "BERGER_MODULUS_EQUATION_CAN_THEN_FIX_THE_REMAINING_RAY_AMPLITUDE"
        ),
        "generic_counterterm_matrix": [list(row) for row in generic],
        "generic_counterterm_determinant": determinant_2x2(generic),
        "spectral_ray": {
            **asdict(ray),
            "c_r2": str(ray.c_r2),
            "c_ricci2": str(ray.c_ricci2),
            "constraint_value": str(ray.linear_constraint),
        },
        "claim_boundary": {
            "zero_input_BHSM_completed": False,
            "zeta_local_branch_adopted_officially": False,
            "physical_scale_fixed": False,
            "physical_CKM_or_CP_emitted": False,
            "frozen_predictions_changed": False,
        },
        "exact_next_object": (
            "FULL_BHSM_DIRAC_BUNDLE_A4_TRACE_WITH_CURVATURE_RESPONSE_AUDIT_"
            "GAUGE_AND_GRAVITY_COEFFICIENT_RATIOS_BERGER_MODULUS_STATIONARITY_"
            "AND_ABSOLUTE_SCALE_SELECTION"
        ),
    }
