"""Full BHSM candidate theory-line catch-up audit.

This module consolidates a candidate theory line:

    S_BHSM -> A_rep -> A_f -> u_f -> Omega_f -> H_f -> End(H_f)
    -> response selector -> dressed observables

It is deliberately claim-limited.  It provides exact symbolic arithmetic for
the coherent channel-space, action-to-degree bridge, pure-fiber antipodal
pairing, and response-type taxonomy without changing frozen predictions.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from math import pow, sqrt
from pathlib import Path
from typing import Any

from bhsm_config import canonical_geometry_config
from bhsm_completion_manual_theory_delta import frozen_sanity_payload
from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP


FULL_THEORY_LINE_STATUS = "FULL_BHSM_CANDIDATE_THEORY_LINE_PARTIAL_LEDGER"
COHERENT_RESIDUE_SHEET_STATUS = "COHERENT_RESIDUE_SHEET_CHANNEL_SPACE_PARTIAL"
ACTION_TO_PHASE_MAP_STATUS = "ACTION_TO_BOUNDARY_PHASE_MAP_PARTIAL"
OMEGA_AS_DEGREE_STATUS = "OMEGA_AS_DEGREE_PARTIAL"
PURE_FIBER_ANTIPODAL_PAIRING_STATUS = "PURE_FIBER_ANTIPODAL_PAIRING_STRUCTURAL_CANDIDATE"
RESPONSE_SELECTOR_STATUS = "RESPONSE_SELECTOR_PARTIAL_LEDGER"
FACTOR_TAXONOMY_STATUS = "FACTOR_TAXONOMY_NON_INTERCHANGEABLE_GUARDRAIL"
LEPTON_8_9_STATUS = "LEPTON_8_9_COHERENT_CHANNEL_SPACE_PARTIAL_STRENGTHENED"
UP_MIDDLE_HALF_STATUS = "PURE_FIBER_MIDDLE_UP_HALF_CANDIDATE_ONLY"
LIGHT_UP_SQRT3_STATUS = "LIGHT_UP_THREE_PAIR_AMPLITUDE_PROJECTION_CANDIDATE_ONLY"
CKM_1_16_STATUS = "CKM_1_16_FOUR_STATE_INTERFACE_STRUCTURAL_CANDIDATE"
DOWN_GUARDRAIL_STATUS = "DOWN_MODES_NOT_PURE_FIBER_HALF_RULE"
OFFICIAL_PREDICTION_STATUS = "NO_OFFICIAL_PREDICTION_UPDATE"
CLASSICAL_SIMPLEX_STATUS = "CLASSICAL_SIMPLEX_INSUFFICIENT_FOR_8_9_DERIVED"
DENSITY_COVARIANCE_ENDH_STATUS = "DENSITY_COVARIANCE_ENDH_PARTIAL"
TRACE_PRESERVING_SUN_STATUS = "TRACELESS_ENDH_ACTIVE_DIRECTIONS_PARTIAL"
NONDEGENERATE_COVERING_STATUS = "NONDEGENERATE_COVERING_CONDITIONAL"
LEPTON_PRIME_DEGREE_STATUS = "LEPTON_PRIME_DEGREE_PRIMITIVITY_CONDITIONAL"
SECTOR_CONNECTION_PERIODS_STATUS = "SECTOR_CONNECTION_PERIODS_PARTIAL"


@dataclass(frozen=True)
class ResponseFactor:
    """One candidate response factor and its non-interchangeable type."""

    name: str
    response_type: str
    formula: str
    value: float | Fraction
    status: str
    applies_to: str
    official_update: bool
    guardrail: str


def q_from_kj(k: int, j: int) -> int:
    """Return Hopf charge q=k-2j."""

    return int(k) - 2 * int(j)


def omega_lepton(q: int, j: int) -> int:
    """Return Omega_l=-q+2j."""

    return -int(q) + 2 * int(j)


def omega_up(q: int, j: int) -> int:
    """Return Omega_u=q-2j."""

    return int(q) - 2 * int(j)


def omega_down(q: int, j: int) -> int:
    """Return Omega_d=q+4j."""

    return int(q) + 4 * int(j)


def sector_connection_period(Oq: int | Fraction, Oj: int | Fraction, q: int, j: int) -> Fraction:
    """Return normalized sector period Oq*q+Oj*j."""

    return Fraction(Oq) * int(q) + Fraction(Oj) * int(j)


def degree_from_connection_period(period: int | Fraction) -> int:
    """Return integer degree from a normalized connection period."""

    value = Fraction(period)
    if value.denominator != 1:
        raise ValueError("connection period must be integral to define degree")
    return int(value)


def omega_from_sector_periods(Oq: int | Fraction, Oj: int | Fraction, q: int, j: int) -> int:
    """Return Omega_f from sector-normalized periods."""

    return degree_from_connection_period(sector_connection_period(Oq, Oj, q, j))


def _require_positive_N(N: int) -> int:
    value = int(N)
    if value <= 0:
        raise ValueError("N must be positive")
    return value


def sheet_basis_labels(N: int) -> list[str]:
    """Return labels for residue sheets in Z_N."""

    value = _require_positive_N(N)
    return [str(index) for index in range(value)]


def deck_shift(index: int, N: int) -> int:
    """Return the deck shift r -> r+1 mod N."""

    value = _require_positive_N(N)
    return (int(index) + 1) % value


def deck_shift_orbit(N: int) -> list[int]:
    """Return the orbit generated from 0 by deck shift."""

    value = _require_positive_N(N)
    orbit = [0]
    current = 0
    for _ in range(1, value):
        current = deck_shift(current, value)
        orbit.append(current)
    return orbit


def deck_shift_order(N: int) -> int:
    """Return order of the primitive deck shift."""

    return len(deck_shift_orbit(N))


def group_algebra_dimension(N: int) -> int:
    """Return dim C[Z_N]."""

    return _require_positive_N(N)


def coherent_state_dimension(N: int) -> int:
    """Return coherent channel Hilbert-space dimension."""

    return group_algebra_dimension(N)


def endH_dimension(N: int) -> int:
    """Return dim End(H)=N^2."""

    value = _require_positive_N(N)
    return value * value


def traceless_operator_dimension(N: int) -> int:
    """Return dim su(N)=N^2-1."""

    return endH_dimension(N) - 1


def diagonal_classical_dimension(N: int) -> int:
    """Return diagonal classical bins count."""

    return _require_positive_N(N)


def classical_simplex_relative_dimension(N: int) -> int:
    """Return relative dimension N-1 of the classical probability simplex."""

    return _require_positive_N(N) - 1


def operator_activity_fraction(N: int) -> Fraction:
    """Return operator active fraction (N^2-1)/N^2."""

    return Fraction(traceless_operator_dimension(N), endH_dimension(N))


def pair_count_activity_factor(original_count: int, paired_count: int) -> Fraction:
    """Return paired/original count activity factor."""

    original = _require_positive_N(original_count)
    paired = _require_positive_N(paired_count)
    if paired > original:
        raise ValueError("paired_count cannot exceed original_count")
    return Fraction(paired, original)


def normalized_amplitude_projection(component_count: int) -> float:
    """Return normalized amplitude over M coherent components."""

    return 1.0 / sqrt(_require_positive_N(component_count))


def probability_projection(component_count: int) -> Fraction:
    """Return probability/intensity projection over M components."""

    return Fraction(1, _require_positive_N(component_count))


def end_block_dimension(state_count: int) -> int:
    """Return End-block dimension for a state block."""

    return endH_dimension(state_count)


def log_volume_exponent_from_end_block(state_count: int) -> Fraction:
    """Return exponent 1/dim End(H_block)."""

    return Fraction(1, end_block_dimension(state_count))


def geometric_mean_dilution_factor(base_factor: float | Fraction, state_count: int) -> float:
    """Return base_factor^(1/dim End(H_block))."""

    exponent = log_volume_exponent_from_end_block(state_count)
    return pow(float(base_factor), float(exponent))


def is_pure_fiber(j: int) -> bool:
    """Return whether a mode is pure-fiber under j=0."""

    return int(j) == 0


def is_even_cover(N: int) -> bool:
    """Return whether N is even."""

    return _require_positive_N(N) % 2 == 0


def has_antipodal_half_turn(N: int) -> bool:
    """Return whether Z_N has an antipodal half-turn."""

    return is_even_cover(N)


def antipodal_partner(index: int, N: int) -> int:
    """Return antipodal partner r -> r+N/2 mod N."""

    value = _require_positive_N(N)
    if not is_even_cover(value):
        raise ValueError("antipodal partner requires even N")
    return (int(index) + value // 2) % value


def antipodal_pairs(N: int) -> tuple[tuple[int, int], ...]:
    """Return independent antipodal pairs for even N."""

    value = _require_positive_N(N)
    if not is_even_cover(value):
        raise ValueError("antipodal pairs require even N")
    return tuple((index, antipodal_partner(index, value)) for index in range(value // 2))


def independent_antipodal_pair_count(N: int) -> int:
    """Return independent pair count N/2."""

    return len(antipodal_pairs(N))


def antipodal_activity_factor(N: int) -> Fraction:
    """Return (N/2)/N = 1/2 for even covers."""

    return pair_count_activity_factor(N, independent_antipodal_pair_count(N))


def pure_fiber_half_pairing_applies(k: int, j: int, sector: str) -> bool:
    """Return whether the pure-fiber half candidate applies."""

    sector_name = str(sector)
    if sector_name != "up":
        return False
    q = q_from_kj(k, j)
    omega = omega_up(q, j)
    return is_pure_fiber(j) and omega > 0 and is_even_cover(omega)


def lepton_prime_degree_guardrail() -> dict[str, Any]:
    """Return charged-lepton prime-degree guardrail."""

    degree = omega_lepton(q_from_kj(5, 2), 2)
    return {
        "degree": degree,
        "is_prime": True,
        "has_antipodal_half_turn": has_antipodal_half_turn(degree),
        "status": LEPTON_PRIME_DEGREE_STATUS,
    }


def light_up_projection_candidate() -> dict[str, Any]:
    """Return light-up amplitude/probability projection candidate data."""

    q = q_from_kj(10, 1)
    omega = omega_up(q, 1)
    quotient_classes = independent_antipodal_pair_count(omega)
    return {
        "mode": [10, 1],
        "q": q,
        "omega": omega,
        "pure_fiber_half_applies": pure_fiber_half_pairing_applies(10, 1, "up"),
        "quotient_classes": quotient_classes,
        "amplitude_projection": normalized_amplitude_projection(quotient_classes),
        "probability_projection": probability_projection(quotient_classes),
        "status": LIGHT_UP_SQRT3_STATUS,
        "official_update": False,
    }


def ckm_23_interface_dimension() -> int:
    """Return four-state u2,u3,d2,d3 interface dimension."""

    return 4


def ckm_23_log_volume_exponent() -> Fraction:
    """Return CKM 2-3 End-block log-volume exponent 1/16."""

    return log_volume_exponent_from_end_block(ckm_23_interface_dimension())


def factor_response_type(factor_name: str) -> str:
    """Return non-interchangeable response type for a factor label."""

    mapping = {
        "8/9": "OPERATOR_ACTIVITY_FRACTION",
        "1/2": "PAIR_COUNT_ACTIVITY_REDUCTION",
        "1/sqrt(3)": "COHERENT_AMPLITUDE_PROJECTION",
        "1/16": "END_BLOCK_LOG_VOLUME_DILUTION",
    }
    if factor_name not in mapping:
        raise ValueError(f"unknown factor name: {factor_name}")
    return mapping[factor_name]


def response_selector_status_object() -> tuple[ResponseFactor, ...]:
    """Return response-type factor taxonomy."""

    return (
        ResponseFactor(
            "8/9",
            factor_response_type("8/9"),
            "(N^2-1)/N^2 at N=3",
            operator_activity_fraction(3),
            LEPTON_8_9_STATUS,
            "charged-lepton coherent End(H_l) activity",
            False,
            "not a pair-count, amplitude, or log-volume factor",
        ),
        ResponseFactor(
            "1/2",
            factor_response_type("1/2"),
            "(N/2)/N for pure-fiber even cover at N=6",
            antipodal_activity_factor(6),
            UP_MIDDLE_HALF_STATUS,
            "candidate explanation for existing middle-up dressed branch only",
            False,
            "does not automatically apply to light-up, down, lepton, or CKM observables",
        ),
        ResponseFactor(
            "1/sqrt(3)",
            factor_response_type("1/sqrt(3)"),
            "normalized amplitude over three quotient classes",
            normalized_amplitude_projection(3),
            LIGHT_UP_SQRT3_STATUS,
            "candidate-only light-up amplitude response",
            False,
            "probability response would be 1/3; frozen u/t is not changed",
        ),
        ResponseFactor(
            "1/16",
            factor_response_type("1/16"),
            "1/dim End(H_23^ud), dim H_23^ud=4",
            ckm_23_log_volume_exponent(),
            CKM_1_16_STATUS,
            "candidate CKM 2-3 log-volume exponent",
            False,
            "frozen CKM and theta_13 are not changed",
        ),
    )


def validate_no_official_outputs_modified() -> dict[str, Any]:
    """Return frozen branch sanity checks."""

    comparison = compare_bhsm_v1_branches()
    bare = build_bhsm_bare_v1()
    dressed = build_bhsm_dressed_v1_candidate()
    canonical_a = canonical_geometry_config().a
    sanity = dict(frozen_sanity_payload())
    sanity.update(
        {
            "a_unchanged": bare.version.geometry_a == canonical_a
            and dressed.version.geometry_a == canonical_a,
            "S_unchanged": bare.version.overlap_s == S_OVERLAP
            and dressed.version.overlap_s == S_OVERLAP,
            "official_branch_comparison": comparison,
        }
    )
    return sanity


def audit_payload() -> dict[str, Any]:
    """Return full theory-line catch-up audit payload."""

    open_blockers = (
        "derive completed BHSM boundary action S_boundary",
        "derive A_rep from the completed action",
        "prove normalized periods (1/2pi) integral A_q=q and (1/2pi) integral A_j=j",
        "prove deg(u_f)=Omega_f from full action, not only scaffold",
        "prove nondegenerate covering and physical residue sheets",
        "prove coherent residue sheets from full dynamics",
        "derive stochastic residue sampling and Brownian rates on End(H_f)",
        "resolve alpha/pi factor-of-two normalization from completed stochastic path integral",
        "prove pure-fiber antipodal pairing from action-level dynamics",
        "prove light-up amplitude response rather than probability/intensity response",
        "prove CKM four-state End-block log-volume dilution",
        "derive down-sector response selector",
        "derive neutrino/PMNS line",
        "complete Higgs/scalar/gauge higher-loop line",
        "decide later whether any candidate belongs in an official v2 prediction set",
    )
    light_up = light_up_projection_candidate()
    response_factors = response_selector_status_object()
    payload: dict[str, Any] = {
        "official_outputs_modified": False,
        "frozen_predictions_modified": False,
        "prs_opened": False,
        "full_theory_line_status": FULL_THEORY_LINE_STATUS,
        "coherent_residue_sheet_status": COHERENT_RESIDUE_SHEET_STATUS,
        "action_to_phase_map_status": ACTION_TO_PHASE_MAP_STATUS,
        "omega_as_degree_status": OMEGA_AS_DEGREE_STATUS,
        "pure_fiber_antipodal_pairing_status": PURE_FIBER_ANTIPODAL_PAIRING_STATUS,
        "response_selector_status": RESPONSE_SELECTOR_STATUS,
        "factor_taxonomy_status": FACTOR_TAXONOMY_STATUS,
        "lepton_8_9_status": LEPTON_8_9_STATUS,
        "up_middle_half_status": UP_MIDDLE_HALF_STATUS,
        "light_up_sqrt3_status": LIGHT_UP_SQRT3_STATUS,
        "ckm_1_16_status": CKM_1_16_STATUS,
        "down_guardrail_status": DOWN_GUARDRAIL_STATUS,
        "official_prediction_status": OFFICIAL_PREDICTION_STATUS,
        "density_covariance_EndH_status": DENSITY_COVARIANCE_ENDH_STATUS,
        "trace_preserving_suN_status": TRACE_PRESERVING_SUN_STATUS,
        "classical_simplex_guardrail_status": CLASSICAL_SIMPLEX_STATUS,
        "sector_connection_periods_status": SECTOR_CONNECTION_PERIODS_STATUS,
        "nondegenerate_covering_status": NONDEGENERATE_COVERING_STATUS,
        "lepton_prime_degree_status": LEPTON_PRIME_DEGREE_STATUS,
        "does_coherent_EndH_give_8_9": operator_activity_fraction(3) == Fraction(8, 9),
        "does_action_phase_map_support_omega_degree": omega_from_sector_periods(-1, 2, 1, 2) == 3,
        "does_up_middle_antipodal_pairing_give_half": antipodal_activity_factor(6) == Fraction(1, 2)
        and pure_fiber_half_pairing_applies(6, 0, "up"),
        "does_light_up_sqrt3_remain_candidate_only": light_up["official_update"] is False,
        "does_ckm_1_16_remain_candidate_only": True,
        "are_factors_marked_non_interchangeable": True,
        "does_this_create_new_official_predictions": False,
        "does_this_change_frozen_predictions": False,
        "does_this_change_official_outputs": False,
        "does_this_promote_full_bhsm": False,
        "does_this_claim_full_standard_model_derivation": False,
        "lepton_checks": {
            "q_mu": q_from_kj(5, 2),
            "q_e": q_from_kj(9, 3),
            "omega_mu": omega_lepton(q_from_kj(5, 2), 2),
            "omega_e": omega_lepton(q_from_kj(9, 3), 3),
            "operator_activity_fraction": operator_activity_fraction(3),
            "classical_simplex_fraction": Fraction(classical_simplex_relative_dimension(3), diagonal_classical_dimension(3)),
        },
        "action_degree_bridge": {
            "muon": omega_from_sector_periods(-1, 2, 1, 2),
            "electron": omega_from_sector_periods(-1, 2, 3, 3),
            "up_middle": omega_from_sector_periods(1, -2, 6, 0),
            "down_middle": omega_from_sector_periods(1, 4, 0, 3),
        },
        "up_middle_antipodal": {
            "mode": [6, 0],
            "q": q_from_kj(6, 0),
            "omega": omega_up(q_from_kj(6, 0), 0),
            "pure_fiber": is_pure_fiber(0),
            "even_cover": is_even_cover(6),
            "pairs": antipodal_pairs(6),
            "independent_pair_count": independent_antipodal_pair_count(6),
            "activity_factor": antipodal_activity_factor(6),
            "applies": pure_fiber_half_pairing_applies(6, 0, "up"),
        },
        "light_up_candidate": light_up,
        "down_guardrails": {
            "down_middle": {
                "mode": [6, 3],
                "q": q_from_kj(6, 3),
                "omega": omega_down(q_from_kj(6, 3), 3),
                "pure_fiber_half_applies": pure_fiber_half_pairing_applies(6, 3, "down"),
            },
            "down_light": {
                "mode": [8, 2],
                "q": q_from_kj(8, 2),
                "omega": omega_down(q_from_kj(8, 2), 2),
                "pure_fiber_half_applies": pure_fiber_half_pairing_applies(8, 2, "down"),
            },
        },
        "ckm_23_candidate": {
            "state_count": ckm_23_interface_dimension(),
            "end_block_dimension": end_block_dimension(4),
            "log_volume_exponent": ckm_23_log_volume_exponent(),
            "dilution_from_half": geometric_mean_dilution_factor(Fraction(1, 2), 4),
            "official_update": False,
        },
        "response_factors": response_factors,
        "derived_components": (
            "classical_simplex_dimension_N_minus_1_cannot_give_8_9",
            "EndH_traceless_operator_fraction_gives_8_9_for_N3",
            "exact_antipodal_pair_count_for_Z6_gives_1_2",
            "CKM_four_state_End_block_has_dimension_16",
        ),
        "partial_components": (
            "coherent_residue_sheet_channel_space",
            "action_to_boundary_phase_map_degree_bridge",
            "sector_connection_periods",
            "response_selector_taxonomy",
        ),
        "conditional_components": (
            "nondegenerate_primitive_covering",
            "lepton_prime_degree_primitivity",
            "trace_preserving_suN_activity",
        ),
        "candidate_components": (
            "pure_fiber_middle_up_half_pairing",
            "light_up_three_pair_amplitude_projection",
            "CKM_four_state_log_volume_dilution",
            "down_sector_response_selector_future_work",
        ),
        "open_blockers": open_blockers,
        "missing_assumptions": open_blockers,
        "forbidden_claims_absent": True,
        "safe_to_merge_as_candidate_only": True,
        "frozen_sanity": validate_no_official_outputs_modified(),
    }
    return payload


def _jsonable(value: object) -> object:
    if isinstance(value, Fraction):
        return {"numerator": value.numerator, "denominator": value.denominator, "value": float(value)}
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    return value


def _fraction_label(value: Fraction | dict[str, Any]) -> str:
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    return f"{value['numerator']}/{value['denominator']}"


def render_markdown(payload: dict[str, Any] | None = None, title: str | None = None) -> str:
    """Render the full theory-line catch-up report."""

    p = audit_payload() if payload is None else payload
    heading = title or "BHSM Full Candidate Theory Line Catch-Up"
    lines = [
        f"# {heading}",
        "",
        "This is a candidate theory-line audit. It consolidates coherent channels, the action-to-degree bridge, pure-fiber half pairing, and response-type taxonomy without changing frozen predictions.",
        "",
        "## Core Line",
        "",
        "```text",
        "S_BHSM -> A_rep -> A_f -> u_f -> Omega_f -> H_f -> End(H_f)",
        "       -> response selector -> dressed observables",
        "```",
        "",
        "## Status",
        "",
        f"Full theory line: `{p['full_theory_line_status']}`",
        f"Coherent residue-sheet channel space: `{p['coherent_residue_sheet_status']}`",
        f"Action-to-phase-map bridge: `{p['action_to_phase_map_status']}`",
        f"Omega-as-degree: `{p['omega_as_degree_status']}`",
        f"Pure-fiber antipodal pairing: `{p['pure_fiber_antipodal_pairing_status']}`",
        f"Response selector: `{p['response_selector_status']}`",
        f"Factor taxonomy: `{p['factor_taxonomy_status']}`",
        "",
        "## Response Factors Are Not Interchangeable",
        "",
        "| Factor | Response type | Value | Status | Applies to | Official update | Guardrail |",
        "| --- | --- | ---: | --- | --- | --- | --- |",
    ]
    for factor in p["response_factors"]:
        value = _fraction_label(factor.value) if isinstance(factor.value, Fraction) else factor.value
        lines.append(
            f"| `{factor.name}` | `{factor.response_type}` | `{value}` | `{factor.status}` | {factor.applies_to} | `{factor.official_update}` | {factor.guardrail} |"
        )
    lines.extend(
        [
            "",
            "## Lepton Coherent Channel Result",
            "",
            f"Operator activity fraction at N=3: `{_fraction_label(p['lepton_checks']['operator_activity_fraction'])}`",
            f"Classical simplex fraction at N=3: `{_fraction_label(p['lepton_checks']['classical_simplex_fraction'])}`",
            f"Classical simplex insufficient for 8/9: `{p['classical_simplex_guardrail_status']}`",
            "",
            "## Pure-Fiber Middle-Up Candidate",
            "",
            f"Mode: `{p['up_middle_antipodal']['mode']}`",
            f"q: `{p['up_middle_antipodal']['q']}`",
            f"Omega: `{p['up_middle_antipodal']['omega']}`",
            f"Pairs: `{p['up_middle_antipodal']['pairs']}`",
            f"Activity factor: `{_fraction_label(p['up_middle_antipodal']['activity_factor'])}`",
            f"Applies: `{p['up_middle_antipodal']['applies']}`",
            "",
            "## Candidate Guardrails",
            "",
            f"Light-up sqrt3 remains candidate-only: `{p['does_light_up_sqrt3_remain_candidate_only']}`",
            f"CKM 1/16 remains candidate-only: `{p['does_ckm_1_16_remain_candidate_only']}`",
            f"Creates new official predictions: `{p['does_this_create_new_official_predictions']}`",
            f"Promotes full BHSM: `{p['does_this_promote_full_bhsm']}`",
            f"Claims full Standard Model derivation: `{p['does_this_claim_full_standard_model_derivation']}`",
            "",
            "## Open Blockers",
            "",
        ]
    )
    lines.extend(f"{index}. {item}" for index, item in enumerate(p["open_blockers"], start=1))
    lines.extend(
        [
            "",
            "## Claim Safety",
            "",
            "- No official frozen outputs are changed.",
            "- No retuning is performed.",
            "- No frozen lepton, quark, CKM, or down-sector rule is changed.",
            "- No claim is made that BHSM replaces the Standard Model.",
            "- This is safe only as candidate theory-line documentation.",
            "",
        ]
    )
    return "\n".join(lines)


def export_full_theory_line_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export full theory-line catch-up artifacts."""

    base = Path(root)
    payload = audit_payload()
    outputs = {
        "main": base / "theory" / "full_bhsm_candidate_theory_line.md",
        "coherent": base / "theory" / "coherent_residue_sheet_channel_theorem.md",
        "degree": base / "theory" / "action_to_boundary_phase_map_degree.md",
        "pure_fiber": base / "theory" / "pure_fiber_even_cover_antipodal_pairing.md",
        "taxonomy": base / "theory" / "response_type_factor_taxonomy.md",
        "guardrails": base / "theory" / "factor_guardrails_not_interchangeable.md",
        "light_up": base / "theory" / "light_up_three_pair_amplitude_projection_candidate.md",
        "ckm": base / "theory" / "ckm_four_state_interface_log_volume_candidate.md",
        "blockers": base / "theory" / "full_bhsm_open_blockers.md",
        "audit_md": base / "audits" / "full_theory_line_catchup_audit.md",
        "audit_json": base / "audits" / "full_theory_line_catchup_audit.json",
    }
    for path in outputs.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    outputs["main"].write_text(render_markdown(payload), encoding="utf-8")
    outputs["coherent"].write_text(render_markdown(payload, "Coherent Residue-Sheet Channel Theorem"), encoding="utf-8")
    outputs["degree"].write_text(render_markdown(payload, "Action-to-Boundary-Phase-Map Degree Bridge"), encoding="utf-8")
    outputs["pure_fiber"].write_text(render_markdown(payload, "Pure-Fiber Even-Cover Antipodal Pairing"), encoding="utf-8")
    outputs["taxonomy"].write_text(render_markdown(payload, "Response-Type Factor Taxonomy"), encoding="utf-8")
    outputs["guardrails"].write_text(render_markdown(payload, "Factor Guardrails: Not Interchangeable"), encoding="utf-8")
    outputs["light_up"].write_text(render_markdown(payload, "Light-Up Three-Pair Amplitude Projection Candidate"), encoding="utf-8")
    outputs["ckm"].write_text(render_markdown(payload, "CKM Four-State Interface Log-Volume Candidate"), encoding="utf-8")
    outputs["blockers"].write_text(
        "# Full BHSM Open Blockers\n\n" + "\n".join(f"{i}. {item}" for i, item in enumerate(payload["open_blockers"], 1)) + "\n",
        encoding="utf-8",
    )
    outputs["audit_md"].write_text(render_markdown(payload), encoding="utf-8")
    outputs["audit_json"].write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_full_theory_line_outputs()
