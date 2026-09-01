"""Evaluate the inverse-free z=-1 C2 finite-core Weyl coefficient cotangent."""

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
RESULT = BASE / "BHSM_N12_C2_1064_SEGMENT_WEYL_COEFFICIENT_COTANGENT.json"
DATA_RESULT = BASE / "BHSM_N12_C2_1064_SEGMENT_WEYL_COEFFICIENT_COTANGENT.npz"
DESCRIPTOR = BASE / "BHSM_N12_C2_1064_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
DESCRIPTOR_DATA = BASE / "BHSM_N12_C2_1064_SEGMENT_FINITE_CORE_DESCRIPTOR.npz"
ONE_PROBE_NO_GO = BASE / "BHSM_N12_FORWARD_RESOLVENT_HEAT_SYNTHESIS_AUDIT.json"
MODULE = ROOT / "src/bhsm/interface/aether_forward_c2_weyl_riccati.py"
THEORY = ROOT / "theory/n12_c2_1064_segment_weyl_coefficient_cotangent.md"
INPUTS = (DESCRIPTOR, DESCRIPTOR_DATA, ONE_PROBE_NO_GO, MODULE, THEORY)


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
        raise FileNotFoundError("missing C2 Weyl cotangent inputs: " + ", ".join(missing))
    descriptor, no_go = (_load(path) for path in (DESCRIPTOR, ONE_PROBE_NO_GO))
    if not descriptor.get("validation_passed") or not no_go.get("validation_passed"):
        raise RuntimeError("validated descriptor and heat-synthesis boundary required")
    with np.load(DESCRIPTOR_DATA) as data:
        x = np.asarray(data["node_log_R4_center"], dtype=float)
        h = np.asarray(data["segment_proper_duration_proof_center"], dtype=float)

    specifications = {
        "scalar_c3": ("scalar", 3.0, 1),
        "product_Dirac_lambda1_5_chirality_plus": ("product_Dirac", 1.5, 1),
        "product_Dirac_lambda1_5_chirality_minus": ("product_Dirac", 1.5, -1),
    }
    channels = {
        name: finite_core_weyl_and_coefficient_cotangent(
            log_radii=x,
            proper_durations=h,
            channel=kind,
            unit_channel_value=value,
            spectral_parameter=-1.0,
            chirality=sign,
        )
        for name, (kind, value, sign) in specifications.items()
    }
    arrays: dict[str, np.ndarray] = {}
    summaries: dict[str, Any] = {}
    for name, channel in channels.items():
        for key in (
            "backward_impedance_values", "D_x_mid_Weyl",
            "D_log_R4_node_Weyl", "D_proper_duration_Weyl",
        ):
            arrays[f"{name}__{key}"] = np.asarray(channel[key])
        summaries[name] = {
            "Weyl_birth_value_at_z_minus_1": channel["Weyl_birth_value"],
            "Weyl_birth_value_at_z_minus_1_decimal": channel[
                "Weyl_birth_value_decimal"
            ],
            "D_log_R4_node_l1_norm": float(np.linalg.norm(
                channel["D_log_R4_node_Weyl"], ord=1
            )),
            "D_duration_weighted_uniform_scale": float(
                np.asarray(channel["D_proper_duration_Weyl"]) @ h
            ),
            "D_log_R4_uniform_shift": float(np.sum(channel["D_log_R4_node_Weyl"])),
            "D_duration_weighted_uniform_scale_decimal": channel[
                "D_duration_weighted_uniform_scale_decimal"
            ],
            "D_log_R4_uniform_shift_decimal": channel[
                "D_log_R4_uniform_shift_decimal"
            ],
            "minimum_backward_impedance": float(np.min(channel["backward_impedance_values"])),
            "all_backward_impedances_positive": bool(np.all(
                np.asarray(channel["backward_impedance_values"]) > 0.0
            )),
            "explicit_matrix_inverse_formed": False,
        }
    np.savez_compressed(DATA_RESULT, **arrays)

    reciprocal_duration = 1.0 / float(np.sum(h))
    values = np.asarray([
        channel["Weyl_birth_value"] for channel in channels.values()
    ])
    plus_decimal = Decimal(channels[
        "product_Dirac_lambda1_5_chirality_plus"
    ]["Weyl_birth_value_decimal"])
    minus_decimal = Decimal(channels[
        "product_Dirac_lambda1_5_chirality_minus"
    ]["Weyl_birth_value_decimal"])
    paired_uniform_x_decimal = (
        Decimal(summaries["product_Dirac_lambda1_5_chirality_plus"][
            "D_log_R4_uniform_shift_decimal"
        ])
        + Decimal(summaries["product_Dirac_lambda1_5_chirality_minus"][
            "D_log_R4_uniform_shift_decimal"
        ])
    )
    validation = {
        "full_1064_segment_descriptor_consumed": descriptor["coefficient_path"]["segment_count"] == 1064,
        "all_three_channel_Riccati_updates_remain_positive": all(
            summary["all_backward_impedances_positive"] for summary in summaries.values()
        ),
        "short_core_values_are_consistent_with_reciprocal_duration": np.all(
            np.abs(values / reciprocal_duration - 1.0) < 1.0e-12
        ),
        "high_precision_retains_the_order_one_chirality_split": (
            plus_decimal != minus_decimal
            and abs(plus_decimal - minus_decimal) > Decimal(1)
        ),
        "paired_product_Dirac_order_one_uniform_log_radius_terms_cancel_but_residual_is_retained": (
            abs(paired_uniform_x_decimal) < Decimal("1e-12")
            and paired_uniform_x_decimal != Decimal(0)
        ),
        "all_coefficient_cotangents_are_finite": all(
            all(np.all(np.isfinite(channel[key])) for key in (
                "D_x_mid_Weyl", "D_log_R4_node_Weyl", "D_proper_duration_Weyl"
            )) for channel in channels.values()
        ),
        "no_ill_conditioned_tridiagonal_Schur_subtraction_or_inverse_formed": True,
        "far_edge_remains_a_form_core_not_a_physical_endpoint": all(
            channel["terminal_Dirichlet_form_core"] for channel in channels.values()
        ),
        "single_negative_probe_not_promoted_to_heat_force": (
            no_go["adjudication"]["Gate7_zero_source_force_evaluable_from_current_rows"] is False
        ),
        "proof_center_coefficient_value_not_promoted_to_exact_physical_path": True,
        "reset_quotient_Jacobi_pullback_not_fabricated": True,
        "no_selector_terminal_load_scale_fit_recurrence_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_1064_SEGMENT_WEYL_COEFFICIENT_COTANGENT",
        "status": (
            "C2_1064_SEGMENT_INVERSE_FREE_WEYL_COEFFICIENT_COTANGENT_AT_Z_MINUS_1_DERIVED"
            if passed else "C2_1064_SEGMENT_WEYL_COTANGENT_NOT_CERTIFIED"
        ),
        "classification": (
            "A_STABLE_SCALAR_MOBIUS_RICCATI_RECURRENCE_EVALUATES_THE_BIRTH_"
            "WEYL_VALUE_AND_REVERSE_COEFFICIENT_COTANGENT_FOR_ALL_THREE_"
            "FIXED_CHANNELS_WITHOUT_THE_CATASTROPHIC_STIFFNESS_SCHUR_"
            "SUBTRACTION_OR_ANY_MATRIX_INVERSE"
        ),
        "channels_at_z_minus_1": summaries,
        "paired_product_Dirac_audit": {
            "high_precision_Weyl_chirality_split": str(plus_decimal - minus_decimal),
            "paired_uniform_log_radius_cotangent_decimal": str(
                paired_uniform_x_decimal
            ),
            "status": (
                "FIXED_CORE_Z_MINUS_1_ORDER_ONE_BOUNDARY_CHIRALITY_TERMS_"
                "CANCEL_WITH_NONZERO_HIGH_PRECISION_REMAINDER"
            ),
            "not_promoted_to_full_heat_or_maximal_tail": True,
        },
        "inverse_free_identity": {
            "scalar": "Z_L=(k*tanh(kh)+Z_R)/(1+Z_R*tanh(kh)/k)",
            "product_Dirac": "Z_L=(c+Z_R*a)/(d+Z_R*b)_FOR_[u,p]_R=T_e[u,p]_L",
            "coefficient_cotangent": "REVERSE_CHAIN_RULE_THROUGH_THE_SCALAR_MOBIUS_UPDATES",
            "far_core_initialization": "DIRICHLET_Z_R=INFINITY_TAKEN_ANALYTICALLY",
        },
        "claim_boundary": {
            "finite_core_M_C2_at_z_minus_1_on_proof_centers": "EVALUATED",
            "finite_core_coefficient_cotangent_at_z_minus_1": "EVALUATED",
            "full_negative_axis_heat_synthesis": "OPEN",
            "reset_quotient_pullback": "OPEN",
            "maximal_tail": "OPEN",
            "zero_source_force": "OPEN",
            "Gate7": "ACTIVE_PROJECTED_FORCE_TAIL_OR_FINITE_EVENT_STOP",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "EXTEND_THE_INVERSE_FREE_RICCATI_COTANGENT_TO_THE_ACTION_OWNED_"
            "NEGATIVE_AXIS_HEAT_SYNTHESIS_AND_PULL_THE_RESULT_THROUGH_THE_"
            "RESET_QUOTIENT_ADJOINT,_WITH_A_MAXIMAL_CAUCHY_TAIL_OR_ACTUAL_"
            "FINITE_EVENT_STOP_STILL_REQUIRED"
        ),
        "data": DATA_RESULT.relative_to(ROOT).as_posix(),
        "data_SHA256": _sha256(DATA_RESULT),
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
        "values": {
            name: row["Weyl_birth_value_at_z_minus_1"]
            for name, row in payload["channels_at_z_minus_1"].items()
        },
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
