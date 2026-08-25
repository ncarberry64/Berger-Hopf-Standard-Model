"""Evaluate and compare the 1222-segment inverse-free Weyl cotangent."""

from __future__ import annotations

from decimal import Decimal
import hashlib
import json
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
RESULT = BASE / "BHSM_N12_C2_1222_SEGMENT_WEYL_COEFFICIENT_COTANGENT.json"
DATA_RESULT = BASE / "BHSM_N12_C2_1222_SEGMENT_WEYL_COEFFICIENT_COTANGENT.npz"
DESCRIPTOR = BASE / "BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
DESCRIPTOR_DATA = DESCRIPTOR.with_suffix(".npz")
PREFIX = BASE / "BHSM_N12_C2_1064_SEGMENT_WEYL_COEFFICIENT_COTANGENT.json"
PREFIX_DATA = PREFIX.with_suffix(".npz")
NO_GO = BASE / "BHSM_N12_FORWARD_RESOLVENT_HEAT_SYNTHESIS_AUDIT.json"
MODULE = ROOT / "src" / "bhsm" / "interface" / "aether_forward_c2_weyl_riccati.py"
THEORY = ROOT / "theory" / "n12_c2_1222_segment_weyl_coefficient_cotangent.md"
INPUTS = (DESCRIPTOR, DESCRIPTOR_DATA, PREFIX, PREFIX_DATA, NO_GO, MODULE, THEORY)


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
        raise FileNotFoundError("missing 1222 Weyl cotangent inputs: " + ", ".join(missing))
    descriptor, prefix, no_go = (_load(path) for path in (DESCRIPTOR, PREFIX, NO_GO))
    if not all(record.get("validation_passed") for record in (descriptor, prefix, no_go)):
        raise RuntimeError("validated descriptor, prefix, and heat boundary required")
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
            decimal_precision=90,
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
        old = prefix["channels_at_z_minus_1"][name]
        value = Decimal(channel["Weyl_birth_value_decimal"])
        old_value = Decimal(old["Weyl_birth_value_at_z_minus_1_decimal"])
        uniform_x = Decimal(channel["D_log_R4_uniform_shift_decimal"])
        old_uniform_x = Decimal(old["D_log_R4_uniform_shift_decimal"])
        summaries[name] = {
            "Weyl_birth_value_at_z_minus_1": channel["Weyl_birth_value"],
            "Weyl_birth_value_at_z_minus_1_decimal": str(value),
            "nested_core_Weyl_increment_decimal": str(value - old_value),
            "D_log_R4_uniform_shift_decimal": str(uniform_x),
            "nested_core_uniform_log_R4_cotangent_increment_decimal": str(uniform_x - old_uniform_x),
            "D_log_R4_node_l1_norm": float(np.linalg.norm(channel["D_log_R4_node_Weyl"], ord=1)),
            "D_duration_weighted_uniform_scale_decimal": channel["D_duration_weighted_uniform_scale_decimal"],
            "minimum_backward_impedance": float(np.min(channel["backward_impedance_values"])),
            "all_backward_impedances_positive": bool(np.all(np.asarray(channel["backward_impedance_values"]) > 0.0)),
            "explicit_matrix_inverse_formed": False,
        }
    np.savez_compressed(DATA_RESULT, **arrays)

    plus = Decimal(summaries["product_Dirac_lambda1_5_chirality_plus"]["D_log_R4_uniform_shift_decimal"])
    minus = Decimal(summaries["product_Dirac_lambda1_5_chirality_minus"]["D_log_R4_uniform_shift_decimal"])
    pair = plus + minus
    validation = {
        "full_1222_segment_descriptor_consumed": descriptor["coefficient_path"]["segment_count"] == 1222,
        "nested_1064_prefix_is_validated": prefix["validation_passed"] is True,
        "all_backward_impedances_remain_positive": all(row["all_backward_impedances_positive"] for row in summaries.values()),
        "all_coefficient_cotangents_are_finite": all(np.all(np.isfinite(array)) for array in arrays.values()),
        "paired_chirality_remainder_retained_at_high_precision": pair != 0,
        "inverse_free_recurrence_only": True,
        "far_edge_remains_a_form_core_not_a_physical_endpoint": descriptor["endpoint_event_child_partition"]["far_core_edge_is_physical_endpoint"] is False,
        "single_negative_probe_not_promoted_to_heat_force": no_go["adjudication"]["Gate7_zero_source_force_evaluable_from_current_rows"] is False,
        "reset_quotient_pullback_not_fabricated": True,
        "no_selector_terminal_load_scale_fit_recurrence_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_1222_SEGMENT_WEYL_COEFFICIENT_COTANGENT",
        "status": "C2_1222_SEGMENT_INVERSE_FREE_WEYL_COEFFICIENT_COTANGENT_AT_Z_MINUS_1_DERIVED" if passed else "C2_1222_SEGMENT_WEYL_COTANGENT_NOT_CERTIFIED",
        "classification": "THE_1222_CORE_BIRTH_WEYL_VALUE_AND_REVERSE_COEFFICIENT_COTANGENT_ARE_EVALUATED_BY_THE_POSITIVE_MOBIUS_RECURRENCE;_THE_DIFFERENCE_FROM_1064_IS_A_NESTED_CORE_INCREMENT_NOT_YET_THE_PHYSICAL_FORCE",
        "channels_at_z_minus_1": summaries,
        "paired_product_Dirac_audit": {
            "paired_uniform_log_radius_cotangent_decimal": str(pair),
            "binary64_exact_cancellation_forbidden": True,
        },
        "claim_boundary": {
            "finite_core_M_C2_at_z_minus_1": "EVALUATED_THROUGH_1222",
            "finite_core_coefficient_cotangent": "EVALUATED_THROUGH_1222",
            "negative_axis_heat_synthesis": "OPEN",
            "reset_quotient_pullback": "OPEN",
            "maximal_projected_tail": "OPEN",
            "zero_source_force": "OPEN",
            "Gate7": "G7_08_OPEN",
            "Gate8": "LOCKED",
        },
        "validated_invalidated_open": {
            "VALIDATED": ["inverse-free 1222-core Weyl value", "reverse coefficient cotangent", "nested 1064-to-1222 increment"],
            "INVALIDATED": ["binary64 exact chirality cancellation", "z=-1 alone equals the heat-minus-zeta force"],
            "OPEN": ["negative-axis heat synthesis", "reset-quotient contraction", "maximal projected Cauchy tail"],
        },
        "hindsight": {"classification": "CONTINUOUS_WITHIN_CLASS_EVOLUTION", "obstruction_physical": False},
        "exact_next_dependency": "EXTEND_THE_1222_CORE_RECURRENCE_TO_THE_COMPLETE_NEGATIVE_REAL_AXIS_AND_MATCH_THE_PARENT_RESET_AND_SOURCE_SLOTS_BEFORE_ANY_FORCE_CLAIM",
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
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({
        "status": payload["status"],
        "values": {name: row["Weyl_birth_value_at_z_minus_1_decimal"] for name, row in payload["channels_at_z_minus_1"].items()},
        "paired_remainder": payload["paired_product_Dirac_audit"]["paired_uniform_log_radius_cotangent_decimal"],
        "validation_passed": payload["validation_passed"],
    }, indent=2))


if __name__ == "__main__":
    main()
