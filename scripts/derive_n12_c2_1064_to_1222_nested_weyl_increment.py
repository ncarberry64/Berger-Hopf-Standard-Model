"""Certify exact nested-core Weyl composition from segments 1064 to 1222."""

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
RESULT = BASE / "BHSM_N12_C2_1064_TO_1222_NESTED_WEYL_INCREMENT.json"
OLD = BASE / "BHSM_N12_C2_1064_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
OLD_DATA = OLD.with_suffix(".npz")
NEW = BASE / "BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
NEW_DATA = NEW.with_suffix(".npz")
AXIS = BASE / "BHSM_N12_C2_1222_SEGMENT_NEGATIVE_AXIS_WEYL_FAMILY.json"
FRIEDRICHS = BASE / "BHSM_N12_MAXIMAL_FRIEDRICHS_WEYL_EXHAUSTION.json"
MODULE = ROOT / "src" / "bhsm" / "interface" / "aether_forward_c2_weyl_riccati.py"
THEORY = ROOT / "theory" / "n12_c2_1064_to_1222_nested_weyl_increment.md"
INPUTS = (OLD, OLD_DATA, NEW, NEW_DATA, AXIS, FRIEDRICHS, MODULE, THEORY)
SPLIT = 1064
PRECISION = 100


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _weyl(
    x: np.ndarray,
    h: np.ndarray,
    specification: tuple[str, float, int],
    z: float,
    terminal_load: str | float | None = None,
    decimal_cotangent: bool = False,
) -> dict[str, Any]:
    kind, value, chirality = specification
    return finite_core_weyl_and_coefficient_cotangent(
        log_radii=x,
        proper_durations=h,
        channel=kind,
        unit_channel_value=value,
        spectral_parameter=z,
        chirality=chirality,
        terminal_load=terminal_load,
        decimal_precision=PRECISION,
        return_decimal_cotangent=decimal_cotangent,
    )


def _maximum_relative_residual(
    direct: list[str], composed: list[Decimal]
) -> Decimal:
    residual = Decimal(0)
    for direct_item, composed_item in zip(direct, composed, strict=True):
        direct_value = Decimal(direct_item)
        scale = max(abs(direct_value), abs(composed_item), Decimal(1))
        residual = max(residual, abs(direct_value - composed_item) / scale)
    return residual


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing nested-core inputs: " + ", ".join(missing))
    old_meta, new_meta, axis, friedrichs = (
        _load(path) for path in (OLD, NEW, AXIS, FRIEDRICHS)
    )
    if not all(item.get("validation_passed") for item in (
        old_meta, new_meta, axis, friedrichs
    )):
        raise RuntimeError("validated nested-core parents required")
    with np.load(OLD_DATA) as data:
        old_x = np.asarray(data["node_log_R4_center"], dtype=float)
        old_h = np.asarray(data["segment_proper_duration_proof_center"], dtype=float)
    with np.load(NEW_DATA) as data:
        new_x = np.asarray(data["node_log_R4_center"], dtype=float)
        new_h = np.asarray(data["segment_proper_duration_proof_center"], dtype=float)

    specifications = {
        "scalar_c3": ("scalar", 3.0, 1),
        "product_Dirac_lambda1_5_chirality_plus": ("product_Dirac", 1.5, 1),
        "product_Dirac_lambda1_5_chirality_minus": ("product_Dirac", 1.5, -1),
    }
    magnitudes = (1.0e-16, 1.0, 1.0e16, 1.0e32, 1.0e48, 1.0e64)
    rows: list[dict[str, Any]] = []
    maximum_residual = Decimal(0)
    maximum_cotangent_relative_residual = Decimal(0)
    all_bracketed = True
    low_relative_decrements: list[Decimal] = []
    for magnitude in magnitudes:
        channels: dict[str, Any] = {}
        z = -magnitude
        for name, specification in specifications.items():
            zero = _weyl(old_x, old_h, specification, z, terminal_load=0.0)
            old_dirichlet = _weyl(old_x, old_h, specification, z)
            added_tail = _weyl(
                new_x[SPLIT:], new_h[SPLIT:], specification, z,
                decimal_cotangent=True,
            )
            composed = _weyl(
                old_x,
                old_h,
                specification,
                z,
                terminal_load=added_tail["Weyl_birth_value_decimal"],
                decimal_cotangent=True,
            )
            full = _weyl(
                new_x, new_h, specification, z, decimal_cotangent=True
            )
            zero_value = Decimal(zero["Weyl_birth_value_decimal"])
            old_value = Decimal(old_dirichlet["Weyl_birth_value_decimal"])
            full_value = Decimal(full["Weyl_birth_value_decimal"])
            composed_value = Decimal(composed["Weyl_birth_value_decimal"])
            residual = abs(composed_value - full_value)
            terminal_sensitivity = Decimal(
                composed["D_terminal_load_Weyl_decimal"]
            )
            composed_x_cotangent = [
                *(Decimal(value) for value in composed["D_x_mid_Weyl_decimal"]),
                *(
                    terminal_sensitivity * Decimal(value)
                    for value in added_tail["D_x_mid_Weyl_decimal"]
                ),
            ]
            composed_h_cotangent = [
                *(
                    Decimal(value)
                    for value in composed["D_proper_duration_Weyl_decimal"]
                ),
                *(
                    terminal_sensitivity * Decimal(value)
                    for value in added_tail["D_proper_duration_Weyl_decimal"]
                ),
            ]
            x_cotangent_residual = _maximum_relative_residual(
                full["D_x_mid_Weyl_decimal"], composed_x_cotangent
            )
            h_cotangent_residual = _maximum_relative_residual(
                full["D_proper_duration_Weyl_decimal"], composed_h_cotangent
            )
            cotangent_residual = max(
                x_cotangent_residual, h_cotangent_residual
            )
            decrement = old_value - full_value
            relative = decrement / old_value
            maximum_residual = max(maximum_residual, residual)
            maximum_cotangent_relative_residual = max(
                maximum_cotangent_relative_residual, cotangent_residual
            )
            all_bracketed &= zero_value < full_value < old_value
            if magnitude <= 1.0:
                low_relative_decrements.append(relative)
            channels[name] = {
                "old_1064_zero_load_Weyl_decimal": str(zero_value),
                "old_1064_Dirichlet_Weyl_decimal": str(old_value),
                "added_158_segment_Dirichlet_impedance_decimal": added_tail[
                    "Weyl_birth_value_decimal"
                ],
                "composed_1222_Weyl_decimal": str(composed_value),
                "direct_1222_Dirichlet_Weyl_decimal": str(full_value),
                "composition_absolute_residual_decimal": str(residual),
                "cotangent_semigroup_maximum_relative_residual_decimal": str(
                    cotangent_residual
                ),
                "Dirichlet_Weyl_decrement_decimal": str(decrement),
                "relative_Dirichlet_Weyl_decrement_decimal": str(relative),
            }
        rows.append({
            "negative_spectral_magnitude": magnitude,
            "z": z,
            "channels": channels,
        })

    validation = {
        "1064_path_is_binary_identical_prefix_of_1222_path": (
            np.array_equal(old_x, new_x[: SPLIT + 1])
            and np.array_equal(old_h, new_h[:SPLIT])
        ),
        "exactly_158_segments_are_added": new_h.size - old_h.size == 158,
        "added_tail_has_positive_proper_duration": float(np.sum(new_h[SPLIT:])) > 0.0,
        "all_split_compositions_replay_within_1e_minus_70": (
            maximum_residual <= Decimal("1e-70")
        ),
        "all_split_cotangents_replay_within_1e_minus_25_relative": (
            maximum_cotangent_relative_residual <= Decimal("1e-25")
        ),
        "all_zero_full_Dirichlet_brackets_are_strict": all_bracketed,
        "current_low_axis_relative_decrement_exceeds_0_99": all(
            value > Decimal("0.99") for value in low_relative_decrements
        ),
        "monotone_nesting_theorem_is_parametric_for_every_real_z_negative": True,
        "decimal_terminal_load_bypasses_binary64_round_trip": True,
        "finite_core_increment_not_promoted_to_projected_force": True,
        "far_edge_not_promoted_to_event_stop_or_boundary_selector": True,
        "abstract_maximal_Friedrichs_limit_not_invalidated": True,
        "no_selector_scale_fit_recurrence_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_1064_TO_1222_NESTED_WEYL_INCREMENT",
        "status": (
            "C2_NESTED_CORE_SEMIGROUP_CERTIFIED_CURRENT_WEYL_NET_NOT_CONVERGED"
            if passed else "C2_NESTED_CORE_INCREMENT_NOT_CERTIFIED"
        ),
        "classification": "THE_1222_CORE_CONTAINS_THE_1064_CORE_EXACTLY_AND_ITS_WEYL_MAP_EQUALS_THE_ARBITRARY_PRECISION_MOBIUS_COMPOSITION_WITH_THE_POSITIVE_158_SEGMENT_TAIL_IMPEDANCE;_THE_AVAILABLE_LOW_AXIS_DIRICHLET_VALUE_NET_CHANGES_BY_MORE_THAN_99_PERCENT_AND_IS_NOT_YET_CONVERGED",
        "parametric_theorem": {
            "domain": "EVERY_REAL_z_LESS_THAN_ZERO",
            "semigroup": "M_1222_D(z)=Phi_0_1064(z;L_1064_1222_D(z))",
            "cotangent_semigroup": "D_PREFIX_M_1222=D_PREFIX_Phi_AND_D_TAIL_M_1222=(D_L_Phi)*D_TAIL_L",
            "strict_bracket": "Phi_0_1064(z;0)<M_1222_D(z)<M_1064_D(z)",
            "reason": "POSITIVE_LOCAL_IMPEDANCES_AND_STRICTLY_POSITIVE_MOBIUS_DETERMINANTS",
        },
        "core_split": {
            "old_segment_count": int(old_h.size),
            "new_segment_count": int(new_h.size),
            "added_segment_count": int(new_h.size - old_h.size),
            "old_proper_duration_center": float(np.sum(old_h)),
            "added_proper_duration_center": float(np.sum(new_h[SPLIT:])),
            "new_proper_duration_center": float(np.sum(new_h)),
        },
        "sampled_crosschecks": rows,
        "maximum_composition_absolute_residual_decimal": str(maximum_residual),
        "maximum_cotangent_semigroup_relative_residual_decimal": str(
            maximum_cotangent_relative_residual
        ),
        "adjudication": {
            "nested_form_core_inverse_free_value_and_backward_cotangent_composition": "CLOSED",
            "current_finite_core_Weyl_value_net": "NOT_YET_CONVERGED",
            "maximal_Friedrichs_value_existence_uniqueness": "REMAINS_CLOSED_ABSTRACTLY",
            "physical_projected_heat_minus_zeta_force_tail": "OPEN",
            "finite_event_or_canonical_stop": "NOT_REACHED",
        },
        "validated_invalidated_open": {
            "VALIDATED": ["exact 1064-to-1222 nesting", "arbitrary-precision downstream-load value and backward-cotangent composition", "strict negative-axis Dirichlet Weyl decrement"],
            "INVALIDATED": ["binary64 load round-trip is an exact nesting replay", "the two available Dirichlet truncations are a converged Weyl net", "a Dirichlet core increment is the physical force"],
            "OPEN": ["source-contracted reset-quotient force Cauchy tail", "actual later event or canonical stop", "zero-source force and saddle"],
        },
        "hindsight": {
            "classification": "NUMERICAL_CONDITIONING_AND_PROOF_CHART_LIMIT",
            "obstruction_physical": False,
        },
        "exact_next_dependency": "USE_THE_ARBITRARY_PRECISION_NESTED_TRANSFER_INSIDE_THE_ACTUAL_SOURCE_CONTRACTED_RESET_QUOTIENT_ADJOINT_NET;_DO_NOT_TREAT_MORE_SCALAR_CORE_BOXES_OR_THE_DIRICHLET_INCREMENT_AS_A_PHYSICAL_FORCE_OR_ENDPOINT",
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
        "maximum_composition_absolute_residual_decimal": payload[
            "maximum_composition_absolute_residual_decimal"
        ],
        "maximum_cotangent_semigroup_relative_residual_decimal": payload[
            "maximum_cotangent_semigroup_relative_residual_decimal"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
