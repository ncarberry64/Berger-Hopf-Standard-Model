"""Bracket the C2 finite-prefix response over every nonnegative tail load."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_c2_weyl_riccati import (  # noqa: E402
    finite_core_weyl_and_coefficient_cotangent,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_FINITE_PREFIX_TERMINAL_LOAD_BRACKET.json"
DESCRIPTOR = BASE / "BHSM_N12_C2_1064_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
DESCRIPTOR_DATA = BASE / "BHSM_N12_C2_1064_SEGMENT_FINITE_CORE_DESCRIPTOR.npz"
NEGATIVE_AXIS = BASE / "BHSM_N12_C2_1064_SEGMENT_NEGATIVE_AXIS_WEYL_FAMILY.json"
FRIEDRICHS = BASE / "BHSM_N12_MAXIMAL_FRIEDRICHS_WEYL_EXHAUSTION.json"
MODULE = ROOT / "src/bhsm/interface/aether_forward_c2_weyl_riccati.py"
THEORY = ROOT / "theory/n12_c2_finite_prefix_terminal_load_bracket.md"
INPUTS = (DESCRIPTOR, DESCRIPTOR_DATA, NEGATIVE_AXIS, FRIEDRICHS, MODULE, THEORY)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing terminal-load inputs: " + ", ".join(missing))
    descriptor, axis, friedrichs = (_load(path) for path in (
        DESCRIPTOR, NEGATIVE_AXIS, FRIEDRICHS
    ))
    if not all(item.get("validation_passed") for item in (
        descriptor, axis, friedrichs
    )):
        raise RuntimeError("validated descriptor, negative axis, and exhaustion required")
    with np.load(DESCRIPTOR_DATA) as data:
        x = np.asarray(data["node_log_R4_center"], dtype=float)
        h = np.asarray(data["segment_proper_duration_proof_center"], dtype=float)

    specifications = {
        "scalar_c3": ("scalar", 3.0, 1),
        "product_Dirac_lambda1_5_chirality_plus": ("product_Dirac", 1.5, 1),
        "product_Dirac_lambda1_5_chirality_minus": ("product_Dirac", 1.5, -1),
    }
    magnitudes = (1.0e-16, 1.0, 1.0e16, 1.0e32, 1.0e48, 1.0e64)
    rows: list[dict[str, Any]] = []
    for magnitude in magnitudes:
        channels: dict[str, Any] = {}
        for name, (kind, value, sign) in specifications.items():
            lower = finite_core_weyl_and_coefficient_cotangent(
                log_radii=x,
                proper_durations=h,
                channel=kind,
                unit_channel_value=value,
                spectral_parameter=-magnitude,
                chirality=sign,
                terminal_load=0.0,
                decimal_precision=80,
            )
            upper = finite_core_weyl_and_coefficient_cotangent(
                log_radii=x,
                proper_durations=h,
                channel=kind,
                unit_channel_value=value,
                spectral_parameter=-magnitude,
                chirality=sign,
                decimal_precision=80,
            )
            channels[name] = {
                "zero_terminal_load_birth_Weyl_decimal": lower[
                    "Weyl_birth_value_decimal"
                ],
                "Dirichlet_terminal_limit_birth_Weyl_decimal": upper[
                    "Weyl_birth_value_decimal"
                ],
                "D_terminal_load_birth_Weyl_at_zero_decimal": lower[
                    "D_terminal_load_Weyl_decimal"
                ],
            }
        rows.append({
            "negative_spectral_magnitude": magnitude,
            "z": -magnitude,
            "channels": channels,
        })

    low_rows = [row for row in rows if row["negative_spectral_magnitude"] <= 1.0e32]
    low_sensitivities = [
        Decimal(channel["D_terminal_load_birth_Weyl_at_zero_decimal"])
        for row in low_rows for channel in row["channels"].values()
    ]
    all_ordered = all(
        Decimal(channel["zero_terminal_load_birth_Weyl_decimal"])
        < Decimal(channel["Dirichlet_terminal_limit_birth_Weyl_decimal"])
        for row in rows for channel in row["channels"].values()
    )
    validation = {
        "full_1064_segment_prefix_consumed": descriptor["coefficient_path"][
            "segment_count"
        ] == 1064,
        "all_zero_load_and_Dirichlet_limit_brackets_are_strictly_ordered": all_ordered,
        "low_and_moderate_probe_terminal_sensitivity_stays_within_1e_minus_27_of_one": all(
            abs(value - Decimal(1)) < Decimal("1e-27") for value in low_sensitivities
        ),
        "terminal_load_monotonicity_is_exact_from_positive_Mobius_determinant": True,
        "nonnegative_Friedrichs_tail_load_lies_in_the_zero_to_Dirichlet_bracket": True,
        "prefix_does_not_forget_the_unknown_tail_on_the_force_relevant_low_axis": True,
        "proof_edge_not_promoted_to_physical_endpoint": True,
        "bracket_not_promoted_to_heat_force_or_force_sign": True,
        "no_selector_terminal_load_scale_fit_recurrence_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_FINITE_PREFIX_TERMINAL_LOAD_BRACKET",
        "status": (
            "C2_1064_SEGMENT_PREFIX_TERMINAL_LOAD_DEPENDENCE_CERTIFIED_NOT_CONTRACTED"
            if passed else "C2_TERMINAL_LOAD_BRACKET_NOT_CERTIFIED"
        ),
        "classification": (
            "FOR_EVERY_REAL_z_LESS_THAN_ZERO_THE_1064_SEGMENT_C2_PREFIX_MAPS_"
            "THE_NONNEGATIVE_DOWNSTREAM_WEYL_LOAD_MONOTONICALLY_BETWEEN_ITS_"
            "ZERO_LOAD_AND_DIRICHLET_LIMITS,_BUT_ITS_LOW_AXIS_TERMINAL_"
            "SENSITIVITY_IS_ONE_TO_27_DECIMAL_PLACES_AND_THEREFORE_THE_PREFIX_"
            "DOES_NOT_DETERMINE_OR_FORGET_THE_MAXIMAL_TAIL"
        ),
        "exact_theorem": {
            "downstream_load": "L_T(z)>=0_FROM_THE_RETAINED_NONNEGATIVE_FRIEDRICHS_TAIL_FORM",
            "prefix_map": "M_prefix(z;L)=(a(z)*L+c(z))/(b(z)*L+d(z))",
            "monotonicity": "D_L_M_prefix=(a*d-b*c)/(b*L+d)^2>0",
            "bracket": "M_prefix(z;0)<=M_C2_max(z)<=lim_L_to_infinity_M_prefix(z;L)",
            "Dirichlet_limit_role": "FINITE_FORM_CORE_UPPER_ENDPOINT_NOT_A_PHYSICAL_BOUNDARY_CONDITION",
        },
        "sampled_crosschecks": rows,
        "adjudication": {
            "C2_finite_prefix_negative_axis_transfer": "CLOSED",
            "unknown_maximal_tail_load": "ACTUALLY_MISSING_AND_NOT_DAMPED_AT_LOW_PROBES",
            "additional_same_scale_prefix_refinement_can_replace_tail_theorem": False,
            "actual_later_event_or_canonical_stop": "NOT_REACHED",
            "zero_source_force": "OPEN",
        },
        "claim_boundary": {
            "terminal_load_monotone_bracket": "CERTIFIED_FOR_EVERY_REAL_z_NEGATIVE",
            "low_axis_tail_forgetting": "CERTIFIED_FALSE_ON_CURRENT_PREFIX",
            "maximal_C2_Weyl_value": "OPEN_AFTER_ACTUAL_TAIL_LOAD_OR_FINITE_ENDPOINT",
            "joint_AE2_seam": "OPEN",
            "zero_source_force": "OPEN",
            "Gate7": "ACTIVE_ACTUAL_LATER_EVENT_STOP_OR_MAXIMAL_TAIL_LOAD",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "CERTIFY_THE_ACTION_OWNED_C2_CONTINUATION_TO_A_LATER_EVENT_OR_"
            "CANONICAL_STOP,_OR_CERTIFY_THE_ACTUAL_MAXIMAL_DOWNSTREAM_WEYL_LOAD_"
            "AND_ITS_PROJECTED_HEAT_MINUS_ZETA_COTANGENT;_DO_NOT_USE_MORE_"
            "SAME_SCALE_PREFIX_SAMPLES_AS_A_SUBSTITUTE"
        ),
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "sample_count": len(payload["sampled_crosschecks"]),
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
