"""BHSM v14.48 completion minimum-input and ownership audit.

This module does not promote BHSM to physical completion.  It records exact
rank statements separating derived constraints from declared renormalization
conditions and inventories the remaining non-algebraic completion gates.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Any

VERSION = "v14.48"

PRIMARY_VERDICT = (
    "BHSM_CANNOT_BE_COMPLETED_AS_A_ZERO_INPUT_PHYSICAL_DERIVATION_FROM_THE_"
    "CURRENT_ACTION_ARTIFACTS_AND_SPECTRAL_DATA"
)
SECONDARY_VERDICT = (
    "BHSM_CAN_BE_CLOSED_AS_A_DECLARED_EFFECTIVE_THEORY_ONLY_AFTER_EXPLICIT_"
    "RENORMALIZATION_GAUGE_AND_SCALE_INPUTS_PLUS_PENDING_NONPERTURBATIVE_"
    "AND_FLAVOR_OPERATOR_CALCULATIONS"
)
EXACT_NEXT_OBJECT = (
    "AUTHOR_OWNED_SELECTION_BETWEEN_A_ZERO_INPUT_UV_COMPLETION_AND_A_"
    "MINIMAL_EFFECTIVE_FOUNDATIONAL_INPUT_SET_FOLLOWED_BY_NORMALIZED_L2_L3_"
    "KOSMANN_SUMS_NONLINEAR_FLAVOR_BRANCH_COLOR_WILSON_STRESS_NEUTRINO_"
    "SCALE_AND_FULL_COUPLED_BVP"
)


@dataclass(frozen=True)
class RankWitness:
    name: str
    matrix: tuple[tuple[int, ...], ...]
    rank: int
    interpretation: str


def matrix_rank_2x2(matrix: tuple[tuple[int, int], tuple[int, int]]) -> int:
    (a, b), (c, d) = matrix
    if a == b == c == d == 0:
        return 0
    return 2 if a * d - b * c != 0 else 1


def channel_counterterm_matrix() -> tuple[tuple[int, int], tuple[int, int]]:
    """Normalized L=2,L=3 witness for q and q^2 columns."""
    return ((5, 25), (12, 144))


def channel_counterterm_determinant() -> int:
    matrix = channel_counterterm_matrix()
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def internal_constraint_witnesses() -> tuple[RankWitness, ...]:
    """Exact rank statements for current geometry-owned constraints.

    The Berger-modulus row is represented symbolically by one nonzero row.
    Its precise coefficients do not matter for the rank upper bound.
    """
    return (
        RankWitness(
            name="smooth_cap_regularity",
            matrix=((0, 0), (0, 0)),
            rank=0,
            interpretation="both curvature invariants are separately regular",
        ),
        RankWitness(
            name="killing_L1_ward_identity",
            matrix=((0, 0), (0, 0)),
            rank=0,
            interpretation="q_1=0 makes the Ward condition identically satisfied",
        ),
        RankWitness(
            name="single_berger_modulus_stationarity",
            matrix=((1, 1), (0, 0)),
            rank=1,
            interpretation="one modulus Euler equation constrains one coefficient direction",
        ),
    )


def einstein_matching_matrix() -> tuple[tuple[int, int], tuple[int, int]]:
    """Two declared no-extra-pole conditions in the (R^2,Ricci^2) basis.

    beta=0 removes the massive spin-2 pole and 3*alpha+beta=0 removes the
    scalar pole in the standard quadratic-gravity linearization.  Together
    they select alpha=beta=0 at a stated matching scale.  This is a
    renormalization prescription, not a theorem of the current BHSM action.
    """
    return ((0, 1), (3, 1))


def solve_einstein_matching() -> tuple[Fraction, Fraction]:
    # beta = 0; 3 alpha + beta = 0.
    beta = Fraction(0)
    alpha = -beta / 3
    return alpha, beta


def continuous_effective_inputs() -> tuple[dict[str, str], ...]:
    return (
        {
            "input": "c_R2^ren(mu_star)",
            "role": "first independent local gravitational renormalization condition",
            "derivation_status": "OPEN_OR_DECLARED",
        },
        {
            "input": "c_Ricci2^ren(mu_star)",
            "role": "second independent local gravitational renormalization condition",
            "derivation_status": "OPEN_OR_DECLARED",
        },
        {
            "input": "c_YM(mu_star)",
            "role": "one common Yang-Mills normalization; trace data fix ratios only",
            "derivation_status": "OPEN_OR_DECLARED",
        },
        {
            "input": "L_star_or_equivalent_scale",
            "role": "one universal dimensionful anchor or dimensional-transmutation condition",
            "derivation_status": "OPEN_OR_DECLARED",
        },
    )


def computation_gates() -> tuple[dict[str, str], ...]:
    return (
        {
            "gate": "normalized_L2_L3_Kosmann_sums",
            "type": "spectral computation",
            "status": "OPEN",
        },
        {
            "gate": "nonlinear_flavor_branch_and_relative_holonomy_orientation",
            "type": "nonlinear PDE/bifurcation computation",
            "status": "OPEN",
        },
        {
            "gate": "action_owned_up_down_wavefunction_embeddings_and_CKM",
            "type": "operator/domain construction",
            "status": "OPEN",
        },
        {
            "gate": "SU3_Wilson_string_tension_and_color_stress",
            "type": "nonperturbative gauge computation",
            "status": "OPEN",
        },
        {
            "gate": "neutrino_dimensionful_response_and_Delta_m2",
            "type": "scale/neutral-response computation",
            "status": "OPEN",
        },
        {
            "gate": "full_coupled_Einstein_eta_Dirac_YM_Higgs_Wilson_BVP",
            "type": "global nonlinear existence/stability computation",
            "status": "OPEN",
        },
    )


def completion_payload() -> dict[str, Any]:
    internal = internal_constraint_witnesses()
    einstein = einstein_matching_matrix()
    alpha, beta = solve_einstein_matching()
    payload: dict[str, Any] = {
        "artifact": "BHSM_completion_minimum_input_v14_48",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "secondary_verdict": SECONDARY_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "counterterm_channel_matrix": channel_counterterm_matrix(),
        "counterterm_channel_determinant": channel_counterterm_determinant(),
        "counterterm_channel_rank": matrix_rank_2x2(channel_counterterm_matrix()),
        "current_internal_constraints": [asdict(item) for item in internal],
        "current_internal_maximum_rank": max(item.rank for item in internal),
        "einstein_matching_candidate": {
            "matrix": einstein,
            "rank": matrix_rank_2x2(einstein),
            "solution": {"c_R2": str(alpha), "c_Ricci2": str(beta)},
            "status": "DECLARED_RENORMALIZATION_CONDITION_NOT_DERIVED_PREDICTION",
        },
        "minimum_continuous_effective_inputs": continuous_effective_inputs(),
        "minimum_continuous_effective_input_count": len(continuous_effective_inputs()),
        "remaining_computation_gates": computation_gates(),
        "physical_completion": False,
        "zero_input_completion_supported": False,
        "effective_completion_available_without_new_author_declarations": False,
        "frozen_predictions_changed": False,
        "usb_touched": False,
    }
    payload["validation"] = {
        "channel_rank_is_two": payload["counterterm_channel_rank"] == 2,
        "channel_determinant_is_420": payload["counterterm_channel_determinant"] == 420,
        "cap_constraint_rank_zero": internal[0].rank == 0,
        "killing_constraint_rank_zero": internal[1].rank == 0,
        "one_modulus_rank_one": internal[2].rank == 1,
        "einstein_matching_rank_two": matrix_rank_2x2(einstein) == 2,
        "einstein_matching_selects_zero": alpha == 0 and beta == 0,
        "completion_remains_false": payload["physical_completion"] is False,
    }
    payload["validation_passed"] = all(payload["validation"].values())
    return payload
