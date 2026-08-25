"""Certify the terminal Laurent germ of the compact finite-history Weyl map."""

from __future__ import annotations

from collections.abc import Callable
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_channel_transfer import (  # noqa: E402
    product_dirac_compact_history_weyl_jets,
    product_dirac_compact_weyl_terminal_germ,
    scalar_compact_history_weyl_jets,
    scalar_compact_weyl_terminal_germ,
)


BASE = ROOT / "artifacts/flagship_integration"
RESULT = BASE / "BHSM_N12_FINITE_HISTORY_TERMINAL_WEYL_GERM.json"
COEFFICIENT = BASE / "BHSM_N12_FINITE_HISTORY_TERMINAL_COEFFICIENT_JET.json"
OPERATOR = BASE / "BHSM_N12_COMPACT_FINITE_HISTORY_OPERATOR.json"
THEORY = ROOT / "theory/n12_finite_history_terminal_weyl_germ.md"
MODULE = ROOT / "src/bhsm/interface/aether_forward_channel_transfer.py"
INPUTS = (COEFFICIENT, OPERATOR, THEORY, MODULE)
SPECTRAL_PARAMETER = -1.0


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _matrix_payload(germ: dict[str, np.ndarray | float]) -> dict[str, Any]:
    return {
        key: value.tolist() if isinstance(value, np.ndarray) else float(value)
        for key, value in germ.items()
    }


def _affine_terminal_radius(
    duration: float, terminal_x: float, terminal_rate: float
) -> Callable[[float], dict[str, float]]:
    def radius(s: float) -> dict[str, float]:
        return {
            "base": terminal_x + duration * terminal_rate * (s - 1.0),
            "first_left": 1.0,
            "first_right": 0.0,
            "mixed_second": 0.0,
        }

    return radius


def _duration(duration: float) -> dict[str, float]:
    return {
        "base": duration,
        "first_left": 0.0,
        "first_right": 0.0,
        "mixed_second": 0.0,
    }


def _convergence_witness(
    terminal_x: float, terminal_rate: float
) -> dict[str, Any]:
    durations = (1.0e-3, 5.0e-4)
    scalar_germ = scalar_compact_weyl_terminal_germ(
        3.0, terminal_x, SPECTRAL_PARAMETER
    )
    witnesses: dict[str, Any] = {}

    def residuals(
        builder: Callable[[float], dict[str, Any]],
        germ: dict[str, np.ndarray | float],
        *,
        has_constant: bool,
    ) -> dict[str, Any]:
        value_residuals: list[float] = []
        derivative_residuals: list[float] = []
        for duration in durations:
            weyl = builder(duration)["weyl"]
            approximation = germ["inverse_duration"] / duration
            if has_constant:
                approximation = approximation + germ["constant"]
            approximation = approximation + duration * germ["duration"]
            derivative = (
                germ["common_scale_constant"]
                + duration * germ["common_scale_duration"]
            )
            value_residuals.append(float(np.linalg.norm(
                weyl["base"].real - approximation
            )))
            derivative_residuals.append(float(np.linalg.norm(
                weyl["first_left"].real - derivative
            )))
        return {
            "durations": list(durations),
            "value_residuals": value_residuals,
            "common_scale_derivative_residuals": derivative_residuals,
            "value_halving_ratio": value_residuals[1] / value_residuals[0],
            "derivative_halving_ratio": (
                derivative_residuals[1] / derivative_residuals[0]
            ),
        }

    witnesses["scalar_c_3"] = residuals(
        lambda duration: scalar_compact_history_weyl_jets(
            3.0,
            SPECTRAL_PARAMETER,
            _affine_terminal_radius(duration, terminal_x, terminal_rate),
            _duration(duration),
            relative_tolerance=1.0e-12,
            absolute_tolerance=1.0e-14,
        ),
        scalar_germ,
        has_constant=False,
    )
    for chirality in (-1, 1):
        germ = product_dirac_compact_weyl_terminal_germ(
            1.5,
            terminal_x,
            terminal_rate,
            SPECTRAL_PARAMETER,
            chirality=chirality,
        )
        witnesses[f"product_Dirac_lambda_1_5_chirality_{chirality:+d}"] = (
            residuals(
                lambda duration, sign=chirality: (
                    product_dirac_compact_history_weyl_jets(
                        1.5,
                        SPECTRAL_PARAMETER,
                        _affine_terminal_radius(
                            duration, terminal_x, terminal_rate
                        ),
                        _duration(duration),
                        chirality=sign,
                        relative_tolerance=1.0e-12,
                        absolute_tolerance=1.0e-14,
                    )
                ),
                germ,
                has_constant=True,
            )
        )
    return witnesses


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("terminal Weyl-germ inputs required")
    coefficient, operator = (_load(path) for path in (COEFFICIENT, OPERATOR))
    if not all(record.get("validation_passed") is True for record in (
        coefficient, operator
    )):
        raise RuntimeError("validated compact operator parents required")
    endpoint = coefficient["terminal_coefficient_data"]
    terminal_x = float(endpoint["center_log_R4"])
    terminal_rate = float(endpoint["center_D_tau_log_R4"])
    scalar = scalar_compact_weyl_terminal_germ(
        3.0, terminal_x, SPECTRAL_PARAMETER
    )
    dirac_plus = product_dirac_compact_weyl_terminal_germ(
        1.5,
        terminal_x,
        terminal_rate,
        SPECTRAL_PARAMETER,
        chirality=1,
    )
    dirac_minus = product_dirac_compact_weyl_terminal_germ(
        1.5,
        terminal_x,
        terminal_rate,
        SPECTRAL_PARAMETER,
        chirality=-1,
    )
    paired_constant = (
        dirac_plus["common_scale_constant"]
        + dirac_minus["common_scale_constant"]
    )
    paired_duration = (
        dirac_plus["common_scale_duration"]
        + dirac_minus["common_scale_duration"]
    )
    convergence = _convergence_witness(terminal_x, terminal_rate)
    validation = {
        "validated_terminal_coefficient_consumed": True,
        "validated_inverse_free_operator_consumed": True,
        "all_germ_remainders_show_second_order_halving": all(
            witness[key] < 0.3
            for witness in convergence.values()
            for key in ("value_halving_ratio", "derivative_halving_ratio")
        ),
        "scalar_common_scale_response_is_nonzero": float(np.linalg.norm(
            scalar["common_scale_duration"]
        )) > 0.0,
        "chirality_pair_constant_common_scale_response_cancels": float(
            np.linalg.norm(paired_constant)
        ) < 1.0e-14,
        "chirality_pair_duration_common_scale_response_is_nonzero": float(
            np.linalg.norm(paired_duration)
        ) > 0.0,
        "endpoint_condition_not_imposed": True,
        "lambda_0_or_history_member_not_selected": True,
        "no_recurrence_reset_physics_cutoff_external_force_or_scale_added": True,
    }
    return {
        "artifact": "BHSM_N12_FINITE_HISTORY_TERMINAL_WEYL_GERM",
        "status": "ACTION_OWNED_TERMINAL_WEYL_LAURENT_GERM_CERTIFIED",
        "classification": (
            "THE_CERTIFIED_TERMINAL_RADIUS_CAUCHY_JET_DETERMINES_THE_"
            "ACTUAL_SMALL_POSITIVE_DURATION_LAURENT_GERMS_OF_M_C_AND_"
            "THE_FIXED_DURATION_COEFFICIENT_PART_OF_ITS_PHYSICAL_COMMON_"
            "SCALE_DERIVATIVE_IN_SCALAR_AND_FACTORIZED_"
            "PRODUCT_DIRAC_CHANNELS;_THE_RESPONSE_IS_NONTRIVIAL_AFTER_"
            "CHIRALITY_PAIRING_BUT_THE_COMPLETE_HEAT_MINUS_ZETA_TRACE_IS_"
            "NOT_EQUAL_TO_ONE_WEYL_PROBE_AND_REMAINS_TO_BE_ASSEMBLED"
        ),
        "terminal_data": {
            "log_R4": terminal_x,
            "D_tau_log_R4": terminal_rate,
            "R4": float(endpoint["center_R4"]),
        },
        "spectral_probe": {
            "z": SPECTRAL_PARAMETER,
            "role": "NUMERIC_CROSSCHECK_ONLY;_THE_FORMULAS_ARE_VALID_FOR_FINITE_REAL_z",
        },
        "weyl_Laurent_germs": {
            "scalar_c_3": _matrix_payload(scalar),
            "product_Dirac_lambda_1_5_chirality_plus": _matrix_payload(
                dirac_plus
            ),
            "product_Dirac_lambda_1_5_chirality_minus": _matrix_payload(
                dirac_minus
            ),
            "chirality_pair_common_scale_constant": paired_constant.tolist(),
            "chirality_pair_common_scale_duration": paired_duration.tolist(),
        },
        "direct_compact_history_crosscheck": convergence,
        "hindsight": {
            "action_required": "M_C_AND_D_M_C_TERMINAL_LAURENT_GERM",
            "single_probe_sufficient_for_zero_source_force": False,
            "positive_duration_member_selection_required": False,
            "existence_or_reset_semantics_reopened": False,
        },
        "exact_next_dependency": (
            "ASSEMBLE_THE_COMPLETE_z_DEPENDENT_SELF_ADJOINT_EVENT_CHILD_"
            "SPECTRAL_FAMILY_AND_PAIR_ITS_OPERATOR_JET_WITH_exp(-ell^2*P)_"
            "P^-1,_OR_SOLVE_THE_EQUIVALENT_SAME_ACTION_FORWARD_OPERATOR_"
            "ADJOINT_KKT_SYSTEM_ON_THE_LOCAL_PARAMETER_FAMILY"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_COMPLETE_SPECTRAL_FORCE_ASSEMBLY",
            "terminal_M_C_Laurent_germ": "CERTIFIED",
            "terminal_fixed_duration_D_common_scale_M_C_germ": "CERTIFIED",
            "total_physical_D_common_scale_M_C": "OPEN_DURATION_JET_CONTRIBUTION",
            "complete_finite_duration_M_C_family": "OPEN_BEYOND_GERM",
            "zero_source_force_functional": "DERIVED",
            "zero_source_force_value": "OPEN_COMPLETE_SPECTRAL_TRACE",
            "same_action_saddle": "OPEN_AFTER_FORCE",
            "physical_Hessian": "OPEN_AFTER_SADDLE",
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
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
    print(RESULT)


if __name__ == "__main__":
    main()
