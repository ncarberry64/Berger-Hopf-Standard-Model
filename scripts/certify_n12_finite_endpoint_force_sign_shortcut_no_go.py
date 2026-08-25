"""Certify that finite-endpoint positivity alone does not fix the Gate-7 force sign.

The witness uses the exact retained round spatial spectra, supertrace signs,
and the retained Dirichlet/Friedrichs reference class on a finite interval.
It is deliberately not promoted to an N12 Euler--Dirac history.  Its purpose
is to test, and refute, the proposed history-independent sign shortcut.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import mpmath as mp


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FINITE_ENDPOINT_FORCE_SIGN_SHORTCUT_NO_GO.json"
)
INPUTS = (
    ROOT / "artifacts/BHSM_aether_common_quantum_superdeterminant_v15_96.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_PROPER_TIME_FORM_OWNERSHIP.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_FINITE_ENCAPSULATION_PHYSICAL_DOMAIN_AUDIT.json",
)


mp.mp.dps = 100
ANGULAR_CUTOFF = 40
TEMPORAL_CUTOFF = 16
ZETA_COEFFICIENT = mp.mpf(59) / 30


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _tail_from_decreasing_ratio(first: mp.mpf, ratio: mp.mpf) -> mp.mpf:
    if not (0 <= ratio < 1):
        raise RuntimeError("tail ratio is not contractive")
    return first / (1 - ratio)


def _temporal_tail(duration: mp.mpf) -> mp.mpf:
    c = (mp.pi / duration) ** 2
    first = mp.exp(-c * TEMPORAL_CUTOFF**2)
    ratio = mp.exp(-c * (2 * TEMPORAL_CUTOFF + 1))
    return _tail_from_decreasing_ratio(first, ratio)


def _sector_rows(radius: mp.mpf) -> tuple[list[tuple[str, int, mp.mpf, mp.mpf]], mp.mpf]:
    """Return (name, sign, degeneracy, spatial eigenvalue) rows and angular tail."""

    rows: list[tuple[str, int, mp.mpf, mp.mpf]] = []
    angular_tail = mp.mpf("0")
    sectors = (
        ("gauge_transverse", -1, 2, lambda m: 24 * (m * m - 1), lambda m: mp.mpf(m)),
        ("rank16_three_family_Weyl", 1, 0, lambda n: 48 * (n + 1) * (n + 2), lambda n: mp.mpf(n) + mp.mpf("1.5")),
        ("complex_HS_doublet", -1, 1, lambda m: 4 * m * m, lambda m: mp.mpf(m)),
    )
    for name, force_sign, start, degeneracy, energy in sectors:
        for level in range(start, ANGULAR_CUTOFF):
            rows.append(
                (name, force_sign, mp.mpf(degeneracy(level)), (energy(level) / radius) ** 2)
            )
        level = ANGULAR_CUTOFF
        first = mp.mpf(degeneracy(level)) * mp.exp(-(energy(level) / radius) ** 2)
        next_term = mp.mpf(degeneracy(level + 1)) * mp.exp(
            -(energy(level + 1) / radius) ** 2
        )
        ratio = next_term / first
        angular_tail += _tail_from_decreasing_ratio(first, ratio)
    return rows, angular_tail


def force_interval(radius_text: str, duration_text: str = "3") -> dict[str, str]:
    radius = mp.mpf(radius_text)
    duration = mp.mpf(duration_text)
    rows, angular_tail = _sector_rows(radius)
    temporal_tail = _temporal_tail(duration)
    value = mp.mpf("0")
    retained_abs_angular_sum = mp.mpf("0")
    for _name, force_sign, degeneracy, spatial in rows:
        retained_abs_angular_sum += degeneracy * mp.exp(-spatial)
        for k in range(1, TEMPORAL_CUTOFF):
            temporal = (mp.pi * k / duration) ** 2
            eigenvalue = temporal + spatial
            value += (
                force_sign
                * degeneracy
                * spatial
                * mp.exp(-eigenvalue)
                / eigenvalue
            )
    value -= ZETA_COEFFICIENT * duration / radius

    # Since spatial/(temporal+spatial)<=1, exp(-temporal-spatial)
    # factorizes.  The two omitted rectangles are bounded without relying on
    # cancellation.  sum_(k>=1) exp(-(pi*k/T)^2) <= T/(2*sqrt(pi)).
    all_temporal_bound = duration / (2 * mp.sqrt(mp.pi))
    error = angular_tail * all_temporal_bound + retained_abs_angular_sum * temporal_tail
    return {
        "radius": mp.nstr(radius, 30),
        "duration": mp.nstr(duration, 30),
        "force_midpoint": mp.nstr(value, 80),
        "absolute_error_upper": mp.nstr(error, 20),
        "force_lower": mp.nstr(value - error, 80),
        "force_upper": mp.nstr(value + error, 80),
        "strict_sign": "NEGATIVE" if value + error < 0 else "POSITIVE" if value - error > 0 else "UNDECIDED",
    }


def build_payload() -> dict[str, object]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("force-sign shortcut inputs required")
    negative = force_interval("0.5")
    positive = force_interval("2.0")
    validation = {
        "all_inputs_present": True,
        "negative_witness_strict": negative["strict_sign"] == "NEGATIVE",
        "positive_witness_strict": positive["strict_sign"] == "POSITIVE",
        "same_proper_duration": negative["duration"] == positive["duration"],
        "same_Dirichlet_Friedrichs_reference_graph": True,
        "same_retained_round_sector_spectra_multiplicities_and_supertrace_signs": True,
        "angular_and_temporal_tails_bounded_without_cancellation": True,
        "actual_N12_history_sign_not_claimed": True,
        "no_reset_selector_endpoint_parameter_scale_fit_or_new_physics_added": True,
    }
    return {
        "artifact": "BHSM_N12_FINITE_ENDPOINT_FORCE_SIGN_SHORTCUT_NO_GO",
        "status": "FINITE_ENDPOINT_OPERATOR_STRUCTURE_ALONE_DOES_NOT_FIX_REPLACEMENT_FORCE_SIGN",
        "classification": (
            "THE_RETAINED_FIXED_CHANNEL_SPECTRA,_GRADED_MULTIPLICITIES,_POSITIVE_"
            "FINITE_ENDPOINT_OPERATOR,_AND_RETAINED_DIRICHLET_FRIEDRICHS_"
            "REFERENCE_CLASS_ADMIT_BOTH_"
            "SIGNS_OF_THE_COMMON_LOG_RADIUS_HEAT_MINUS_ZETA_FORCE;_THEREFORE_"
            "COMPACT_RESOLVENT,_POSITIVITY,_AND_BRST_SUPERTRACE_BOOKKEEPING_ALONE_"
            "CANNOT_REPLACE_THE_ACTUAL_ACTION_OWNED_N12_FINITE_HISTORY_ORACLE"
        ),
        "theorem_scope": {
            "proved": "NO_HISTORY_INDEPENDENT_SIGN_THEOREM_FOLLOWS_FROM_THE_LISTED_OPERATOR_STRUCTURE_ALONE",
            "not_proved": "THE_TWO_CONSTANT_ROUND_WITNESSES_ARE_NOT_ASSERTED_TO_BE_RETAINED_N12_EULER_DIRAC_HISTORIES",
            "physical_N12_force_sign": "OPEN",
            "reason_for_scope": "THE_COUNTERPAIR_TESTS_THE_PROPOSED_ALGEBRAIC_SHORTCUT,_NOT_THE_DYNAMICAL_COEFFICIENT_PATH",
        },
        "exact_formula": {
            "temporal_spectrum": "nu_k^2=(pi*k/T)^2,_k>=1_FOR_THE_DIRICHLET_FRIEDRICHS_REFERENCE_INTERVAL",
            "sector_force": "F_heat=sum_(C,l,k)[-s_C*d_C(l)*a_C(l,R)*exp(-(nu_k^2+a_C))/(nu_k^2+a_C)]",
            "force_sign_convention": "GAUGE_AND_HS_MINUS,_RANK16_THREE_FAMILY_WEYL_PLUS_AFTER_THE_COMMON_LOG_RADIUS_JET",
            "replacement_force": "F_rep=F_heat-(59/30)*T/R",
            "tail_method": "a/(nu^2+a)<=1,_SEPARABLE_GAUSSIAN_SUMS,_DECREASING_RATIO_GEOMETRIC_TAIL",
            "angular_cutoff": ANGULAR_CUTOFF,
            "temporal_cutoff": TEMPORAL_CUTOFF,
        },
        "certified_counterpair": [negative, positive],
        "hindsight": {
            "validated": "FINITE_ENDPOINT_TRACE_CONTROL_MAKES_THE_FORCE_FINITE_ON_EACH_REALIZATION",
            "invalidated": "FINITE_ENDPOINT_POSITIVITY_OR_GRADED_MULTIPLICITIES_DETERMINE_A_UNIVERSAL_COMMON_SCALE_FORCE_SIGN",
            "open": "ACTUAL_PARAMETRIC_N12_FORCE_ON_THE_PHYSICAL_RESET_QUOTIENT",
        },
        "exact_next_dependency": (
            "CONSTRUCT_THE_ACTUAL_ACTION_OWNED_FINITE_EVENT_OR_CANONICAL_STOP_"
            "COEFFICIENT_PATH_AND_ENDPOINT_GRAPH,_OR_THE_EQUIVALENT_PARAMETRIC_"
            "WEYL_CALDERON_ORACLE_WITH_ITS_PHYSICAL_FIRST_JET;_THEN_EVALUATE_"
            "THE_PROJECTED_FORCE_AND_SOLVE_THE_COUPLED_SAME_ACTION_SADDLE"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_ACTUAL_FINITE_HISTORY_FORCE_ORACLE_OPEN",
            "Gate8": "LOCKED",
            "universal_force_sign_shortcut": "CLOSED_INVALID",
            "actual_projected_force": "OPEN",
            "same_action_saddle": "OPEN_COUPLED_TO_FORCE",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(RESULT)


if __name__ == "__main__":
    main()
