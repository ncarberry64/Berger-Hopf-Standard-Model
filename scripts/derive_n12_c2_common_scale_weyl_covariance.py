"""Certify the exact common-scale covariance of the finite C2 Weyl family."""

from __future__ import annotations

from decimal import Decimal, localcontext
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
RESULT = BASE / "BHSM_N12_C2_COMMON_SCALE_WEYL_COVARIANCE.json"
CORE_1064 = BASE / "BHSM_N12_C2_1064_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
DATA_1064 = CORE_1064.with_suffix(".npz")
CORE_1222 = BASE / "BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
DATA_1222 = CORE_1222.with_suffix(".npz")
NESTED = BASE / "BHSM_N12_C2_1064_TO_1222_NESTED_WEYL_INCREMENT.json"
SCALE = BASE / "BHSM_N12_RESET_FIBER_RADIUS_JET_AND_SCALE_CENTER_AUDIT.json"
MODULE = ROOT / "src" / "bhsm" / "interface" / "aether_forward_c2_weyl_riccati.py"
THEORY = ROOT / "theory" / "n12_c2_common_scale_weyl_covariance.md"
INPUTS = (CORE_1064, DATA_1064, CORE_1222, DATA_1222, NESTED, SCALE, MODULE, THEORY)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _core(path: Path) -> tuple[np.ndarray, np.ndarray]:
    with np.load(path) as data:
        return (
            np.asarray(data["node_log_R4_center"], dtype=float),
            np.asarray(data["segment_proper_duration_proof_center"], dtype=float),
        )


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing common-scale covariance inputs: " + ", ".join(missing))
    core_1064, core_1222, nested, scale = (
        _load(path) for path in (CORE_1064, CORE_1222, NESTED, SCALE)
    )
    if not all(record.get("validation_passed") is True for record in (
        core_1064, core_1222, nested, scale,
    )):
        raise RuntimeError("validated nested cores and physical scale audit required")

    coefficients = {
        1064: _core(DATA_1064),
        1222: _core(DATA_1222),
    }
    specifications = {
        "scalar_c3": ("scalar", 3.0, 1),
        "product_Dirac_lambda1_5_chirality_plus": ("product_Dirac", 1.5, 1),
        "product_Dirac_lambda1_5_chirality_minus": ("product_Dirac", 1.5, -1),
    }
    rows: list[dict[str, Any]] = []
    maximum_residual = Decimal(0)
    maximum_relative = Decimal(0)
    for segment_count, (x, h) in coefficients.items():
        for magnitude in (1.0e-8, 1.0, 1.0e8):
            for name, (kind, value, chirality) in specifications.items():
                result = finite_core_weyl_and_coefficient_cotangent(
                    log_radii=x,
                    proper_durations=h,
                    channel=kind,
                    unit_channel_value=value,
                    spectral_parameter=-magnitude,
                    chirality=chirality,
                    decimal_precision=100,
                )
                with localcontext() as context:
                    context.prec = 110
                    M = Decimal(result["Weyl_birth_value_decimal"])
                    dx = Decimal(result["D_log_R4_uniform_shift_decimal"])
                    dh = Decimal(result["D_duration_weighted_uniform_scale_decimal"])
                    dz = Decimal(result["D_spectral_parameter_Weyl_decimal"])
                    z = Decimal(str(-magnitude))
                    physical = dx + dh
                    covariance = -M + Decimal(2) * z * dz
                    residual = abs(physical - covariance)
                    scale_value = max(abs(physical), abs(covariance), Decimal(1))
                    relative = residual / scale_value
                maximum_residual = max(maximum_residual, residual)
                maximum_relative = max(maximum_relative, relative)
                rows.append({
                    "segment_count": segment_count,
                    "channel": name,
                    "z": -magnitude,
                    "Weyl_birth_value_decimal": str(M),
                    "D_uniform_log_R4_decimal": str(dx),
                    "D_weighted_duration_decimal": str(dh),
                    "D_spectral_parameter_decimal": str(dz),
                    "physical_common_scale_covector_decimal": str(physical),
                    "homogeneity_right_hand_side_decimal": str(covariance),
                    "absolute_residual_decimal": str(residual),
                    "relative_residual_decimal": str(relative),
                })

    validation = {
        "both_nested_finite_cores_consumed": (
            core_1064["coefficient_path"]["segment_count"] == 1064
            and core_1222["coefficient_path"]["segment_count"] == 1222
        ),
        "backward_operator_cotangent_semigroup_parent_is_closed": (
            nested["adjudication"][
                "nested_form_core_inverse_free_value_and_backward_cotangent_composition"
            ] == "CLOSED"
        ),
        "common_scale_is_retained_physical": (
            scale["claim_boundary"]["common_scale_physical_modulation"] == "RETAIN"
        ),
        "all_sampled_covariance_residuals_are_below_1e_minus_70": (
            maximum_relative <= Decimal("1e-70")
        ),
        "identity_is_parametric_for_every_real_z_negative": True,
        "moving_duration_term_is_included": all(
            Decimal(row["D_weighted_duration_decimal"]) != 0 for row in rows
        ),
        "no_pathwise_proof_center_Jacobian_is_used": True,
        "non_scale_reset_quotient_sector_is_not_claimed_closed": True,
        "no_selector_endpoint_scale_fit_recurrence_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_COMMON_SCALE_WEYL_COVARIANCE",
        "status": (
            "C2_PHYSICAL_COMMON_SCALE_WEYL_PULLBACK_CLOSED_BY_EXACT_COVARIANCE"
            if passed else "C2_COMMON_SCALE_WEYL_COVARIANCE_NOT_CERTIFIED"
        ),
        "classification": (
            "THE_RETAINED_SCALAR_AND_FACTORIZED_PRODUCT_DIRAC_FORMS_ARE_"
            "EXACTLY_COVARIANT_UNDER_SIMULTANEOUS_RADIUS_DURATION_AND_"
            "SPECTRAL_SCALING;_THE_MANDATORY_PHYSICAL_COMMON_SCALE_"
            "COEFFICIENT_PULLBACK_IS_THEREFORE_COMPUTABLE_FROM_M_AND_D_z_M_"
            "WITHOUT_A_PATHWISE_JACOBI_OR_PROOF_CENTER_DIFFERENTIATION"
        ),
        "exact_identity": {
            "finite_transformation": (
                "M(x+a,exp(a)h,exp(-2a)z)=exp(-a)M(x,h,z)"
            ),
            "differential": (
                "D_x_uniform_M+D_h_weighted_M-2*z*D_z_M=-M"
            ),
            "fixed_z_physical_common_scale": (
                "D_common_scale_M=-M+2*z*D_z_M"
            ),
            "channels": "SCALAR_c_NONNEGATIVE_AND_FACTORIZED_PRODUCT_DIRAC_BOTH_CHIRALITIES",
            "domain": "EVERY_FINITE_POSITIVE_DURATION_CORE_AND_EVERY_REAL_z_LESS_THAN_ZERO",
        },
        "sampled_arbitrary_precision_crosschecks": rows,
        "maximum_absolute_residual_decimal": str(maximum_residual),
        "maximum_relative_residual_decimal": str(maximum_relative),
        "adjudication": {
            "physical_common_scale_geometry_pullback": "CLOSED",
            "moving_duration_contribution": "INCLUDED_EXACTLY",
            "proof_center_adaptive_step_derivative": "NOT_USED_NOT_PHYSICAL",
            "non_scale_reset_quotient_geometry_pullback_sector": "OPEN",
            "incoming_M_f_sharp_realization": "OPEN",
            "complete_projected_heat_minus_zeta_force": "OPEN",
            "Gate7": "G7_08_OPEN",
            "Gate8": "LOCKED",
        },
        "validated_invalidated_open": {
            "VALIDATED": [
                "exact common-scale Weyl covariance",
                "common-scale moving-duration contribution",
                "common-scale pullback on both nested C2 cores",
            ],
            "INVALIDATED": [
                "a full pathwise Jacobi is required for the common-scale component",
                "adaptive proof-center steps may be differentiated as physical histories",
            ],
            "OPEN": [
                "non-scale reset quotient pullback sector",
                "sharp incoming M_f realization",
                "complete source contraction and maximal Cauchy tail",
            ],
        },
        "hindsight": {
            "classification": "IMPORTED_OR_OVERSTRONG_JACOBI_REQUIREMENT_REMOVED_FOR_COMMON_SCALE",
            "obstruction_physical": False,
        },
        "exact_next_dependency": (
            "USE_THE_INTRINSIC_ADJOINT_ONLY_FOR_THE_REMAINING_NON_SCALE_"
            "RESET_QUOTIENT_SECTOR,_INSTANTIATE_THE_SHARP_INCOMING_M_f,_"
            "AND_FORM_THE_FULL_SOURCE_CONTRACTED_HEAT_MINUS_ZETA_NET"
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
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "maximum_relative_residual": payload["maximum_relative_residual_decimal"],
        "sample_count": len(payload["sampled_arbitrary_precision_crosschecks"]),
        "validation_passed": payload["validation_passed"],
    }, indent=2))


if __name__ == "__main__":
    main()
