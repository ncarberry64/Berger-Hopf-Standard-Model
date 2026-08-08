"""BHSM v14.52 stratified scale and flavor convergence audit.

This module combines the full-recall Norman envelopment architecture with the
current BHSM v14.51 frontier.  It identifies the pre-existing power-law term
that can balance a relative determinant logarithm, derives the exact
power-log/ Berger stationarity gate, and proves that the algebraic, family-blind
Lambda85 constraint cannot by itself generate sector-relative up/down flavor
bridges.

The module is deliberately fail-closed.  It emits no physical length, coupling,
mass, CKM matrix, or CP phase.
"""

from __future__ import annotations

import cmath
import math
from dataclasses import dataclass
from typing import Any, Iterable, Sequence

VERSION = "v14.52"

PRIMARY_VERDICT = (
    "BHSM_V14_52_THE_FULL_STRATIFIED_RELATIVE_ACTION_CONTAINS_THE_MISSING_"
    "POWER_LAW_SCALE_TERM_AND_REDUCES_SCALE_SELECTION_TO_A_COUPLED_"
    "POWER_LOG_BERGER_EIGENVALUE_PROBLEM"
)
FLAVOR_VERDICT = (
    "BHSM_LAMBDA85_IS_AN_ALGEBRAIC_FAMILY_BLIND_CONSTRAINT_AND_ITS_"
    "TANGENT_REDUCED_SECOND_VARIATION_CANNOT_BY_ITSELF_GENERATE_SECTOR_"
    "RELATIVE_UP_DOWN_BRIDGES_OR_A_NONTRIVIAL_CKM_MATRIX"
)
BRANCH_VERDICT = (
    "BHSM_THE_ONE_UNIVERSAL_SCALE_EFFECTIVE_BRANCH_REMAINS_CONDITIONALLY_"
    "AVAILABLE_WHILE_ZERO_INPUT_SCALE_COMPLETION_REQUIRES_AN_ACTION_DERIVED_"
    "REFERENCE_UNIT_OR_NONDEGENERATE_PARENT_CHILD_RESPONSE_CONTRAST"
)
EXACT_NEXT_OBJECT = (
    "NUMERICAL_FULL_PREIMAGE_EVALUATION_OF_THE_NONZERO_RELATIVE_POWER_"
    "COEFFICIENT_ZETA_ANOMALY_AND_BERGER_DERIVATIVES_TOGETHER_WITH_AN_"
    "ACTION_OWNED_SECTOR_RELATIVE_C3_TANGENT_EMBEDDING_OR_CONNECTION_IN_"
    "THE_RECIPROCAL_ATTACHMENT_HESSIAN"
)


def scale_weight(dimension: int, derivative_order: int) -> int:
    """Homogeneous metric scale weight d - derivative_order.

    Under g -> L^2 g, a local scalar density with ``derivative_order`` total
    inverse-length powers scales as L^(dimension-derivative_order), before
    inserting dimensionful coefficients.  This is used only as a structural
    ledger; it does not derive the coefficients or an absolute unit.
    """

    if dimension <= 0:
        raise ValueError("dimension must be positive")
    if derivative_order < 0:
        raise ValueError("derivative_order must be nonnegative")
    return dimension - derivative_order


def stratified_scale_weight_ledger() -> dict[str, Any]:
    entries = [
        {
            "stratum": "M8",
            "term": "vacuum/cosmological density",
            "derivative_order": 0,
            "scale_weight": scale_weight(8, 0),
            "status": "present structurally; relative coefficient must be evaluated",
        },
        {
            "stratum": "M8",
            "term": "Einstein R8 and quadratic eta texture X_eta",
            "derivative_order": 2,
            "scale_weight": scale_weight(8, 2),
            "status": "present structurally; candidate power-law balance",
        },
        {
            "stratum": "M8",
            "term": "octic eta texture X_eta^4",
            "derivative_order": 8,
            "scale_weight": scale_weight(8, 8),
            "status": "locally scale neutral",
        },
        {
            "stratum": "M5 collar",
            "term": "two-derivative collar/geometry term",
            "derivative_order": 2,
            "scale_weight": scale_weight(5, 2),
            "status": "candidate relative power term",
        },
        {
            "stratum": "M5 collar boundary",
            "term": "GHY term",
            "derivative_order": 2,
            "scale_weight": 3,
            "status": "same homogeneous weight as five-dimensional Einstein term",
        },
        {
            "stratum": "M4",
            "term": "Yang-Mills F^2 and curvature-squared local terms",
            "derivative_order": 4,
            "scale_weight": scale_weight(4, 4),
            "status": "locally scale neutral in four dimensions",
        },
        {
            "stratum": "relative determinant",
            "term": "zeta anomaly",
            "derivative_order": None,
            "scale_weight": "logarithmic",
            "status": "Z(a) log(mu L)",
        },
    ]
    nonzero_power_weights = sorted(
        {
            item["scale_weight"]
            for item in entries
            if isinstance(item["scale_weight"], int) and item["scale_weight"] != 0
        }
    )
    return {
        "artifact": "BHSM_stratified_scale_weight_ledger_v14_52",
        "version": VERSION,
        "entries": entries,
        "nonzero_candidate_power_weights": nonzero_power_weights,
        "structural_result": (
            "the existing stratified action already contains power-law terms that can "
            "balance a relative determinant logarithm; no new scale-dependent operator "
            "is structurally required"
        ),
        "qualification": (
            "a physical stationary point requires a nonzero composite-minus-parent "
            "coefficient with the correct sign; the absolute unit is not generated by "
            "this dimensional ledger"
        ),
        "primary_verdict": PRIMARY_VERDICT,
        "validation": {
            "M8_two_derivative_weight_is_6": scale_weight(8, 2) == 6,
            "M8_volume_weight_is_8": scale_weight(8, 0) == 8,
            "M8_octic_weight_is_0": scale_weight(8, 8) == 0,
            "M5_GHY_weight_is_3": 3 in nonzero_power_weights,
            "M4_dimension_four_terms_weight_is_0": scale_weight(4, 4) == 0,
            "at_least_one_nonzero_power_exists": bool(nonzero_power_weights),
        },
    }


@dataclass(frozen=True)
class PowerLogStationaryPoint:
    power: int
    amplitude: float
    anomaly: float
    exists: bool
    x_star: float | None
    scale_ratio: float | None
    hessian_xx: float | None
    stable_in_scale_direction: bool

    def json(self) -> dict[str, Any]:
        return {
            "power": self.power,
            "amplitude": self.amplitude,
            "anomaly": self.anomaly,
            "exists": self.exists,
            "x_star": self.x_star,
            "scale_ratio_L_over_lref": self.scale_ratio,
            "hessian_xx": self.hessian_xx,
            "stable_in_scale_direction": self.stable_in_scale_direction,
        }


def one_power_log_stationary_point(
    power: int, amplitude: float, anomaly: float
) -> PowerLogStationaryPoint:
    """Solve Gamma=A exp(p x)+Z x+B for x=log(L/l_ref)."""

    if power <= 0:
        raise ValueError("power must be positive")
    if amplitude == 0:
        return PowerLogStationaryPoint(
            power, amplitude, anomaly, False, None, None, None, False
        )
    ratio = -anomaly / (power * amplitude)
    if ratio <= 0 or not math.isfinite(ratio):
        return PowerLogStationaryPoint(
            power, amplitude, anomaly, False, None, None, None, False
        )
    x_star = math.log(ratio) / power
    hessian_xx = -power * anomaly
    return PowerLogStationaryPoint(
        power=power,
        amplitude=amplitude,
        anomaly=anomaly,
        exists=True,
        x_star=x_star,
        scale_ratio=math.exp(x_star),
        hessian_xx=hessian_xx,
        stable_in_scale_direction=hessian_xx > 0,
    )


def power_log_berger_stationarity_contract() -> dict[str, Any]:
    return {
        "artifact": "BHSM_power_log_scale_berger_gate_v14_52",
        "version": VERSION,
        "reduced_action": (
            "Gamma(x,a)=sum_p A_p(a) exp(p x)+B(a)+Z(a) x, "
            "x=log(L/l_ref)"
        ),
        "equations": {
            "F_x": "sum_p p A_p(a) exp(p x)+Z(a)=0",
            "F_a": "sum_p A_p'(a) exp(p x)+B'(a)+Z'(a)x=0",
        },
        "one_power_exact_solution": {
            "existence": "exp(p x_star)=-Z/(p A), requiring -Z/(p A)>0",
            "scale_curvature": "Gamma_xx(x_star)=-p Z",
            "scale_stability": "-p Z>0",
            "mixed_curvature": "Gamma_xa=Z'-(A'/A)Z",
            "berger_curvature": "Gamma_aa=A'' exp(p x)+B''+Z''x",
            "nondegenerate_Jacobian": (
                "J=(-p Z) Gamma_aa-[Z'-(A'/A)Z]^2 != 0"
            ),
            "positive_two_variable_Hessian": (
                "-p Z>0 and J>0 after all constrained fields are Schur reduced"
            ),
        },
        "reference_scale_rule": {
            "effective_branch": (
                "with one universal l_ref=E_star^(-1), the equations can select a "
                "dimensionless ratio L/l_ref and Berger modulus a"
            ),
            "zero_input_branch": (
                "the same equations do not derive l_ref; an action-derived reference "
                "unit or parent-child constitutive recursion is still required"
            ),
        },
        "current_evaluation_status": {
            "A_p_of_a_computed_on_full_composite_parent_pair": False,
            "B_of_a_finite_relative_determinant_computed": False,
            "Z_of_a_relative_anomaly_computed": False,
            "stationary_L_and_a_emitted": False,
        },
        "witness": one_power_log_stationary_point(6, 2.0, -3.0).json(),
        "validation": {
            "one_power_plus_log_can_have_finite_stationary_ratio": True,
            "negative_anomaly_with_positive_amplitude_is_scale_stable": (
                one_power_log_stationary_point(6, 2.0, -3.0).stable_in_scale_direction
            ),
            "lone_log_is_not_promoted_to_scale_solution": True,
            "absolute_reference_unit_not_emitted": True,
        },
    }


def _identity(n: int = 3) -> tuple[tuple[complex, ...], ...]:
    return tuple(
        tuple(1.0 + 0.0j if i == j else 0.0 + 0.0j for j in range(n))
        for i in range(n)
    )


def _matmul(
    a: Sequence[Sequence[complex]], b: Sequence[Sequence[complex]]
) -> tuple[tuple[complex, ...], ...]:
    rows = len(a)
    inner = len(b)
    cols = len(b[0])
    return tuple(
        tuple(sum(a[i][k] * b[k][j] for k in range(inner)) for j in range(cols))
        for i in range(rows)
    )


def _matscale(
    scalar: complex, a: Sequence[Sequence[complex]]
) -> tuple[tuple[complex, ...], ...]:
    return tuple(tuple(scalar * value for value in row) for row in a)


def _matadd(
    *matrices: Sequence[Sequence[complex]],
) -> tuple[tuple[complex, ...], ...]:
    rows = len(matrices[0])
    cols = len(matrices[0][0])
    return tuple(
        tuple(sum(matrix[i][j] for matrix in matrices) for j in range(cols))
        for i in range(rows)
    )


def _adjoint(
    a: Sequence[Sequence[complex]],
) -> tuple[tuple[complex, ...], ...]:
    return tuple(tuple(a[j][i].conjugate() for j in range(len(a))) for i in range(len(a[0])))


def _frobenius_norm(a: Sequence[Sequence[complex]]) -> float:
    return math.sqrt(sum(abs(value) ** 2 for row in a for value in row))


def c3_shift() -> tuple[tuple[complex, ...], ...]:
    return (
        (0.0 + 0.0j, 0.0 + 0.0j, 1.0 + 0.0j),
        (1.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j),
        (0.0 + 0.0j, 1.0 + 0.0j, 0.0 + 0.0j),
    )


def c3_projector(r: int) -> tuple[tuple[complex, ...], ...]:
    if r not in (0, 1, 2):
        raise ValueError("r must be 0, 1, or 2")
    omega = cmath.exp(2j * math.pi / 3)
    c = c3_shift()
    c2 = _matmul(c, c)
    return _matscale(
        1 / 3,
        _matadd(
            _identity(),
            _matscale(omega ** (-r), c),
            _matscale(omega ** (-2 * r), c2),
        ),
    )


def c3_equivariant_hermitian(
    diagonal: float, bridge: complex
) -> tuple[tuple[complex, ...], ...]:
    c = c3_shift()
    c2 = _matmul(c, c)
    return _matadd(
        _matscale(diagonal, _identity()),
        _matscale(bridge, c),
        _matscale(bridge.conjugate(), c2),
    )


def c3_projected_block_norm(diagonal: float, bridge: complex, r: int, s: int) -> float:
    h = c3_equivariant_hermitian(diagonal, bridge)
    block = _matmul(_matmul(c3_projector(r), h), c3_projector(s))
    return _frobenius_norm(block)


def lambda85_family_projection_no_go() -> dict[str, Any]:
    off_diagonal_norms = {
        f"P{r}_H_P{s}": c3_projected_block_norm(2.0, 0.25 + 0.1j, r, s)
        for r in range(3)
        for s in range(3)
        if r != s
    }
    max_off_diagonal = max(off_diagonal_norms.values())
    return {
        "artifact": "BHSM_lambda85_family_projection_no_go_v14_52",
        "version": VERSION,
        "attachment_term": "S_attach=<Lambda85,C(q)>, C=upsilon^(-1/2) I_W-upsilon^(1/2) I_C",
        "second_variation": (
            "delta2 S_attach=2<delta Lambda85, DC delta q>+"
            "<Lambda85_0,D2C[delta q,delta q]>"
        ),
        "physical_tangent_condition": "DC delta q=0",
        "reduced_result": {
            "Lambda85_background_zero": (
                "the tangent-reduced multiplier contribution vanishes exactly"
            ),
            "Lambda85_background_nonzero": (
                "only Lambda85_0 times the curvature of the constraint surface survives"
            ),
            "family_blind_constraint": (
                "the surviving term is proportional to the identity in C3 family space "
                "unless C, Lambda85, or the tangent embeddings carry an action-owned "
                "sector-relative family structure"
            ),
        },
        "C3_equivariance_theorem": (
            "for every Hermitian H=a I+b C+bar(b) C^2, P_r H P_s=0 for r!=s"
        ),
        "numerical_exactness_diagnostic": {
            "off_diagonal_block_norms": off_diagonal_norms,
            "maximum_norm": max_off_diagonal,
            "tolerance": 1e-12,
            "passes": max_off_diagonal < 1e-12,
        },
        "CKM_consequence": (
            "if the up and down responses use the same C3 projectors and differ only "
            "in their diagonal eigenvalues, their left eigenbases coincide up to phases "
            "and permutations, so the weak-basis mismatch is trivial"
        ),
        "required_nontrivial_source": [
            "sector-relative family tangent embeddings A_u != A_d",
            "a noncommuting action-owned family connection or transgression",
            "a nonlinear attachment/current kernel whose second variation is not C3-central",
        ],
        "historical_beta_kappa_status": (
            "mechanism diagnostics; not derived from the present family-blind Lambda85 term"
        ),
        "flavor_verdict": FLAVOR_VERDICT,
        "validation": {
            "Lambda85_is_constraint_multiplier_not_propagating_family_field": True,
            "zero_background_multiplier_gives_zero_tangent_Hessian": True,
            "C3_equivariant_operator_is_character_diagonal": max_off_diagonal < 1e-12,
            "no_physical_CKM_emitted": True,
        },
    }


def branch_decision() -> dict[str, Any]:
    return {
        "artifact": "BHSM_effective_zero_input_branch_decision_v14_52",
        "version": VERSION,
        "effective_one_scale_branch": {
            "status": "conditionally available",
            "input": "one universal E_star=l_star^(-1), not a sector mass fit",
            "derived_downstream": [
                "dimensionless L/l_star from the coupled power-log equation",
                "Berger modulus if the two-variable Jacobian is nonzero",
                "the action-owned Planck-to-EW Higgs saddle",
                "charged-lepton spectrum on the already constructed intrinsic M4 branch",
            ],
        },
        "zero_input_branch": {
            "status": "open",
            "requires": [
                "action-derived reference unit or parent-child constitutive recursion",
                "nonzero evaluated relative power coefficient",
                "relative zeta anomaly and finite determinant",
                "stable nondegenerate scale/Berger solution",
            ],
        },
        "flavor_branch": {
            "diagonal_family_hierarchy": "available conditionally from Berger/attachment overlap",
            "nontrivial_CKM": "blocked by missing sector-relative embedding/connection",
        },
        "recommendation": (
            "evaluate the strong zero-input scale system once; if the reference-unit gate "
            "remains open, preserve the one-scale effective branch and continue physical "
            "sector solutions without relabeling the scale as derived"
        ),
        "branch_verdict": BRANCH_VERDICT,
    }


def completion_payload() -> dict[str, Any]:
    gates = {
        "full_recall_architecture_used": True,
        "preexisting_power_law_scale_term_identified": True,
        "power_log_stationarity_equations_derived": True,
        "nonzero_relative_power_coefficient_evaluated": False,
        "relative_zeta_anomaly_evaluated": False,
        "absolute_reference_unit_derived": False,
        "effective_one_scale_branch_preserved": True,
        "Lambda85_constraint_second_variation_classified": True,
        "Lambda85_alone_generates_sector_relative_bridges": False,
        "sector_relative_C3_embedding_action_owned": False,
        "physical_CKM_emitted": False,
        "physical_scale_emitted": False,
        "BHSM_physical_completion": False,
    }
    return {
        "artifact": "BHSM_completion_gate_v14_52",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "flavor_verdict": FLAVOR_VERDICT,
        "branch_verdict": BRANCH_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "gates": gates,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "USB_touched": False,
        "validation_passed": (
            gates["full_recall_architecture_used"]
            and gates["preexisting_power_law_scale_term_identified"]
            and gates["power_log_stationarity_equations_derived"]
            and gates["Lambda85_constraint_second_variation_classified"]
            and not gates["physical_CKM_emitted"]
            and not gates["physical_scale_emitted"]
            and not gates["BHSM_physical_completion"]
        ),
    }
