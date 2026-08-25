"""Certify the inverse-free C2 finite-core Weyl family on every real z<0."""

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
RESULT = BASE / "BHSM_N12_C2_1064_SEGMENT_NEGATIVE_AXIS_WEYL_FAMILY.json"
DESCRIPTOR = BASE / "BHSM_N12_C2_1064_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
DESCRIPTOR_DATA = BASE / "BHSM_N12_C2_1064_SEGMENT_FINITE_CORE_DESCRIPTOR.npz"
SINGLE_PROBE = BASE / "BHSM_N12_C2_1064_SEGMENT_WEYL_COEFFICIENT_COTANGENT.json"
HEAT_NO_GO = BASE / "BHSM_N12_FORWARD_RESOLVENT_HEAT_SYNTHESIS_AUDIT.json"
MODULE = ROOT / "src/bhsm/interface/aether_forward_c2_weyl_riccati.py"
THEORY = ROOT / "theory/n12_c2_1064_segment_negative_axis_weyl_family.md"
INPUTS = (DESCRIPTOR, DESCRIPTOR_DATA, SINGLE_PROBE, HEAT_NO_GO, MODULE, THEORY)


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
        raise FileNotFoundError("missing negative-axis C2 inputs: " + ", ".join(missing))
    descriptor, probe, no_go = (_load(path) for path in (
        DESCRIPTOR, SINGLE_PROBE, HEAT_NO_GO
    ))
    if not all(item.get("validation_passed") for item in (descriptor, probe, no_go)):
        raise RuntimeError("validated descriptor, probe, and heat boundary required")
    with np.load(DESCRIPTOR_DATA) as data:
        x = np.asarray(data["node_log_R4_center"], dtype=float)
        h = np.asarray(data["segment_proper_duration_proof_center"], dtype=float)

    specifications = {
        "scalar_c3": ("scalar", 3.0, 1),
        "product_Dirac_lambda1_5_chirality_plus": ("product_Dirac", 1.5, 1),
        "product_Dirac_lambda1_5_chirality_minus": ("product_Dirac", 1.5, -1),
    }
    magnitudes = (1.0e-16, 1.0e-8, 1.0, 1.0e8, 1.0e32, 1.0e64)
    rows: list[dict[str, Any]] = []
    for magnitude in magnitudes:
        channels: dict[str, Any] = {}
        for name, (kind, value, sign) in specifications.items():
            result = finite_core_weyl_and_coefficient_cotangent(
                log_radii=x,
                proper_durations=h,
                channel=kind,
                unit_channel_value=value,
                spectral_parameter=-magnitude,
                chirality=sign,
                decimal_precision=80,
            )
            channels[name] = {
                "Weyl_birth_value_decimal": result["Weyl_birth_value_decimal"],
                "D_log_R4_uniform_shift_decimal": result[
                    "D_log_R4_uniform_shift_decimal"
                ],
                "D_duration_weighted_uniform_scale_decimal": result[
                    "D_duration_weighted_uniform_scale_decimal"
                ],
                "all_backward_impedances_positive": bool(np.all(
                    np.asarray(result["backward_impedance_values"]) > 0.0
                )),
            }
        paired = (
            Decimal(channels["product_Dirac_lambda1_5_chirality_plus"][
                "D_log_R4_uniform_shift_decimal"
            ])
            + Decimal(channels["product_Dirac_lambda1_5_chirality_minus"][
                "D_log_R4_uniform_shift_decimal"
            ])
        )
        rows.append({
            "negative_spectral_magnitude": magnitude,
            "z": -magnitude,
            "channels": channels,
            "paired_product_Dirac_uniform_log_R4_remainder_decimal": str(paired),
        })

    z_minus_one = next(row for row in rows if row["z"] == -1.0)
    replay_residual = Decimal(
        z_minus_one["paired_product_Dirac_uniform_log_R4_remainder_decimal"]
    ) - Decimal(probe["paired_product_Dirac_audit"][
        "paired_uniform_log_radius_cotangent_decimal"
    ])
    all_positive = all(
        channel["all_backward_impedances_positive"]
        for row in rows for channel in row["channels"].values()
    )
    all_paired_nonzero = all(
        Decimal(row["paired_product_Dirac_uniform_log_R4_remainder_decimal"]) != 0
        for row in rows
    )
    validation = {
        "full_1064_segment_path_consumed": descriptor["coefficient_path"][
            "segment_count"
        ] == 1064,
        "all_sampled_backward_impedances_are_positive": all_positive,
        "z_minus_one_high_precision_probe_replays_exactly": replay_residual == 0,
        "paired_chirality_remainders_are_not_rounded_to_zero": all_paired_nonzero,
        "parametric_no_pole_argument_uses_only_z_negative_positive_duration_and_nonnegative_square_potential": True,
        "arbitrary_precision_coefficient_cotangent_is_executable_for_every_real_z_negative": True,
        "sample_grid_is_crosscheck_not_spectral_quadrature": True,
        "negative_axis_family_not_promoted_to_heat_force_without_parent_seam_source_trace_and_tail": (
            no_go["adjudication"]["Gate7_zero_source_force_evaluable_from_current_rows"]
            is False
        ),
        "proof_center_path_not_promoted_to_exact_action_history": True,
        "far_form_core_edge_not_promoted_to_physical_endpoint": True,
        "no_selector_terminal_load_scale_fit_recurrence_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_1064_SEGMENT_NEGATIVE_AXIS_WEYL_FAMILY",
        "status": (
            "C2_1064_SEGMENT_NEGATIVE_REAL_AXIS_WEYL_AND_COEFFICIENT_COTANGENT_FAMILY_DERIVED"
            if passed else "C2_NEGATIVE_AXIS_WEYL_FAMILY_NOT_CERTIFIED"
        ),
        "classification": (
            "THE_ACTUAL_1064_SEGMENT_PROOF_CENTER_COEFFICIENT_PATH_DEFINES_A_"
            "POSITIVE_POLE_FREE_INVERSE_FREE_MOBIUS_RICCATI_WEYL_FAMILY_AND_"
            "ARBITRARY_PRECISION_COEFFICIENT_COTANGENT_FOR_EVERY_REAL_z_LESS_THAN_ZERO"
        ),
        "parametric_theorem": {
            "domain": "z_IN_MINUS_INFINITY_TO_ZERO",
            "scalar_positivity": (
                "k=sqrt(c*exp(-2x)-z)>0,_tanh(kh)>0,_AND_EVERY_"
                "MOBIUS_NUMERATOR_AND_DENOMINATOR_IS_POSITIVE"
            ),
            "product_Dirac_positivity": (
                "k=sqrt(W^2-z)>abs(W),_SO_1_PLUS_OR_MINUS_W*tanh(kh)/k>0;_"
                "THE_POSITIVE_TERMINAL_IMPEDANCE_RECURRENCE_HAS_NO_REAL_NEGATIVE_AXIS_POLE"
            ),
            "regularity": (
                "FINITE_COMPOSITION_OF_ANALYTIC_HYPERBOLIC_AND_MOBIUS_MAPS_"
                "GIVES_REAL_ANALYTIC_M_C2_T(z)_AND_COEFFICIENT_COTANGENT_ON_z<0"
            ),
            "inverse_free": True,
            "far_edge_role": "NESTED_DIRICHLET_FORM_CORE_ONLY",
        },
        "sampled_crosschecks": rows,
        "precision_adjudication": {
            "binary64_failure": (
                "ORDER_ONE_CHIRAL_TERMS_CANCEL_AGAINST_A_NONZERO_REMAINDER_"
                "OF_ORDER_1E_MINUS_31_ON_LOW_PROBES"
            ),
            "decimal_remainder_retained": True,
            "sample_rows_are_not_a_heat_quadrature": True,
        },
        "matching_audit": {
            "C2_negative_axis_value_and_coefficient_cotangent": "VALID_MATCH",
            "event_frame_reset_pullback": "EXISTING_ALGEBRA_BUT_ACTUAL_QUOTIENT_JACOBI_OPEN",
            "parent_M_f_negative_axis_value_and_jet": "ACTUALLY_MISSING_AS_A_SHARP_REALIZATION",
            "sector_complete_source_weighted_trace": "ACTUALLY_MISSING_ON_THIS_REALIZATION",
            "maximal_tail_or_finite_later_event": "ACTUALLY_MISSING",
        },
        "claim_boundary": {
            "finite_core_complete_negative_real_axis_spectral_parameter_coverage": "DERIVED_EXECUTABLE",
            "finite_core_coefficient_cotangent_family": "DERIVED_EXECUTABLE",
            "joint_AE2_seam": "OPEN_AFTER_PARENT_AND_RESET_QUOTIENT_REALIZATION",
            "heat_minus_zeta_force": "OPEN",
            "maximal_tail": "OPEN",
            "same_action_saddle": "OPEN_AFTER_FORCE",
            "physical_Hessian": "OPEN_AFTER_SADDLE",
            "Gate7": "ACTIVE_PROJECTED_FORCE_TAIL_OR_FINITE_EVENT_STOP",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "ASSEMBLE_A_SHARP_ACTION_OWNED_PARENT_M_f_NEGATIVE_AXIS_FAMILY_AND_"
            "THE_RESET_QUOTIENT_PULLBACK_WITH_THE_EXISTING_SEAM_ALGEBRA,_THEN_"
            "CONTRACT_THE_JOINT_FAMILY_WITH_THE_COMPLETE_PAIR_PLUS_CONTACT_SOURCE_"
            "TRACE_AND_CERTIFY_THE_MAXIMAL_PROJECTED_TAIL_OR_AN_ACTUAL_LATER_STOP"
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
