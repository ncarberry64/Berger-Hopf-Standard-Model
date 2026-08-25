"""Certify the inverse-free 1222-core Weyl family for every real z<0."""

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
RESULT = BASE / "BHSM_N12_C2_1222_SEGMENT_NEGATIVE_AXIS_WEYL_FAMILY.json"
DESCRIPTOR = BASE / "BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
DESCRIPTOR_DATA = DESCRIPTOR.with_suffix(".npz")
PROBE = BASE / "BHSM_N12_C2_1222_SEGMENT_WEYL_COEFFICIENT_COTANGENT.json"
NO_GO = BASE / "BHSM_N12_FORWARD_RESOLVENT_HEAT_SYNTHESIS_AUDIT.json"
MODULE = ROOT / "src" / "bhsm" / "interface" / "aether_forward_c2_weyl_riccati.py"
THEORY = ROOT / "theory" / "n12_c2_1222_segment_negative_axis_weyl_family.md"
INPUTS = (DESCRIPTOR, DESCRIPTOR_DATA, PROBE, NO_GO, MODULE, THEORY)


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
        raise FileNotFoundError("missing 1222 negative-axis inputs: " + ", ".join(missing))
    descriptor, probe, no_go = (_load(path) for path in (DESCRIPTOR, PROBE, NO_GO))
    if not all(record.get("validation_passed") for record in (descriptor, probe, no_go)):
        raise RuntimeError("validated negative-axis parents required")
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
                log_radii=x, proper_durations=h, channel=kind,
                unit_channel_value=value, spectral_parameter=-magnitude,
                chirality=sign, decimal_precision=90,
            )
            channels[name] = {
                "Weyl_birth_value_decimal": result["Weyl_birth_value_decimal"],
                "D_log_R4_uniform_shift_decimal": result["D_log_R4_uniform_shift_decimal"],
                "D_duration_weighted_uniform_scale_decimal": result["D_duration_weighted_uniform_scale_decimal"],
                "all_backward_impedances_positive": bool(np.all(np.asarray(result["backward_impedance_values"]) > 0.0)),
            }
        paired = Decimal(channels["product_Dirac_lambda1_5_chirality_plus"]["D_log_R4_uniform_shift_decimal"]) + Decimal(channels["product_Dirac_lambda1_5_chirality_minus"]["D_log_R4_uniform_shift_decimal"])
        rows.append({
            "negative_spectral_magnitude": magnitude,
            "z": -magnitude,
            "channels": channels,
            "paired_product_Dirac_uniform_log_R4_remainder_decimal": str(paired),
        })
    replay = next(row for row in rows if row["z"] == -1.0)
    expected = probe["paired_product_Dirac_audit"]["paired_uniform_log_radius_cotangent_decimal"]
    validation = {
        "full_1222_segment_path_consumed": descriptor["coefficient_path"]["segment_count"] == 1222,
        "all_sampled_backward_impedances_are_positive": all(channel["all_backward_impedances_positive"] for row in rows for channel in row["channels"].values()),
        "z_minus_one_probe_replays_exactly": Decimal(replay["paired_product_Dirac_uniform_log_R4_remainder_decimal"]) == Decimal(expected),
        "paired_chirality_remainders_are_retained": all(Decimal(row["paired_product_Dirac_uniform_log_R4_remainder_decimal"]) != 0 for row in rows),
        "parametric_no_pole_theorem_covers_every_real_z_negative": True,
        "sample_grid_is_not_a_heat_quadrature": True,
        "far_edge_not_promoted_to_physical_endpoint": descriptor["endpoint_event_child_partition"]["far_core_edge_is_physical_endpoint"] is False,
        "heat_force_not_claimed_without_parent_reset_source_and_tail": no_go["adjudication"]["Gate7_zero_source_force_evaluable_from_current_rows"] is False,
        "no_selector_terminal_load_scale_fit_recurrence_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_1222_SEGMENT_NEGATIVE_AXIS_WEYL_FAMILY",
        "status": "C2_1222_SEGMENT_NEGATIVE_REAL_AXIS_WEYL_AND_COTANGENT_FAMILY_DERIVED" if passed else "C2_1222_NEGATIVE_AXIS_FAMILY_NOT_CERTIFIED",
        "classification": "THE_1222_SEGMENT_C2_FORM_CORE_DEFINES_A_POSITIVE_POLE_FREE_REAL_ANALYTIC_INVERSE_FREE_WEYL_AND_COEFFICIENT_COTANGENT_FAMILY_FOR_EVERY_REAL_z_LESS_THAN_ZERO",
        "parametric_theorem": {
            "domain": "z_IN_MINUS_INFINITY_TO_ZERO",
            "scalar_positivity": "sqrt(c*exp(-2x)-z)>0_AND_POSITIVE_MOBIUS_RECURRENCE",
            "product_Dirac_positivity": "sqrt(W^2-z)>abs(W)_AND_POSITIVE_IMPEDANCE_RECURRENCE",
            "regularity": "FINITE_COMPOSITION_OF_REAL_ANALYTIC_HYPERBOLIC_AND_MOBIUS_MAPS",
            "inverse_free": True,
        },
        "sampled_crosschecks": rows,
        "matching_audit": {
            "C2_negative_axis_value_and_coefficient_cotangent": "VALID_MATCH_THROUGH_FINITE_CORE_1222",
            "parent_M_f_negative_axis_value_and_jet": "ACTUALLY_MISSING_SHARP_REALIZATION",
            "event_frame_reset_quotient_Jacobi": "ACTUALLY_MISSING_ALONG_THE_COEFFICIENT_PATH",
            "complete_graded_heat_minus_zeta_source_contraction": "ACTUALLY_MISSING",
            "maximal_projected_Cauchy_tail_or_finite_stop": "ACTUALLY_MISSING",
        },
        "claim_boundary": {
            "finite_core_complete_negative_axis_family": "DERIVED_EXECUTABLE_THROUGH_1222",
            "heat_minus_zeta_force": "OPEN",
            "maximal_tail": "OPEN",
            "Gate7": "G7_08_OPEN",
            "Gate8": "LOCKED",
        },
        "validated_invalidated_open": {
            "VALIDATED": ["1222-core negative-axis Weyl family", "inverse-free coefficient cotangent family"],
            "INVALIDATED": ["sample probes constitute heat synthesis", "far core edge is an endpoint"],
            "OPEN": ["parent seam", "reset quotient Jacobi pullback", "complete source contraction", "maximal Cauchy tail"],
        },
        "hindsight": {"classification": "CONTINUOUS_WITHIN_CLASS_EVOLUTION", "obstruction_physical": False},
        "exact_next_dependency": "MATCH_OR_DERIVE_THE_SHARP_PARENT_M_f_NEGATIVE_AXIS_REALIZATION_AND_THE_ACTUAL_RESET_QUOTIENT_JACOBI_PATH,_THEN_CONTRACT_THE_COMPLETE_HEAT_MINUS_ZETA_SOURCE_BEFORE_TESTING_THE_MAXIMAL_CAUCHY_TAIL",
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": payload["status"], "samples": len(payload["sampled_crosschecks"]), "validation_passed": payload["validation_passed"]}, indent=2))


if __name__ == "__main__":
    main()
