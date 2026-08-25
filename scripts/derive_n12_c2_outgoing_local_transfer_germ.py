"""Derive the actual outgoing C2 channel-transfer and quotient-jet germ."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Callable

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_c2_local_transfer_germ import (  # noqa: E402
    local_transfer_cauchy_germ,
    product_dirac_channel_cauchy_generator_jets,
    scalar_channel_cauchy_generator_jets,
)
from bhsm.interface.aether_forward_channel_transfer import (  # noqa: E402
    integrate_transfer_jets,
    product_dirac_channel_log_radius_jets,
    scalar_channel_log_radius_jets,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_OUTGOING_LOCAL_TRANSFER_GERM.json"
BIRTH = BASE / "BHSM_N12_C2_BIRTH_COEFFICIENT_QUOTIENT_JET.json"
MATCHING = BASE / "BHSM_N12_GATE7_C2_DIAGRAM_SLOT_MATCHING_AUDIT.json"
MODULE = ROOT / "src/bhsm/interface/aether_forward_c2_local_transfer_germ.py"
TRANSFER = ROOT / "src/bhsm/interface/aether_forward_channel_transfer.py"
THEORY = ROOT / "theory/n12_c2_outgoing_local_transfer_germ.md"
INPUTS = (BIRTH, MATCHING, MODULE, TRANSFER, THEORY)
SPECTRAL_PARAMETER = -1.0
DURATIONS = (1.0e-3, 5.0e-4)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _matrix(matrix: np.ndarray) -> list[list[float]]:
    value = np.asarray(matrix, dtype=complex)
    if np.linalg.norm(value.imag) > 1.0e-13:
        raise ValueError("real negative-axis crosscheck expected")
    return value.real.tolist()


def _crosscheck(
    generator_builder: Callable[[float], dict[str, np.ndarray]],
    germ: dict[str, np.ndarray | bool],
) -> dict[str, Any]:
    value_residuals: list[float] = []
    parameter_residuals: list[float] = []
    wronskian_residuals: list[float] = []
    for duration in DURATIONS:
        transfer = integrate_transfer_jets(
            generator_builder,
            (0.0, duration),
            relative_tolerance=1.0e-13,
            absolute_tolerance=1.0e-15,
        )
        value_approximation = (
            np.asarray(germ["transfer_constant"])
            + duration * np.asarray(germ["transfer_linear"])
            + duration**2 * np.asarray(germ["transfer_quadratic"])
        )
        parameter_approximation = (
            duration * np.asarray(germ["parameter_linear"])
            + duration**2 * np.asarray(germ["parameter_quadratic"])
        )
        value_residuals.append(
            float(np.linalg.norm(transfer["base"] - value_approximation))
        )
        parameter_residuals.append(
            float(
                np.linalg.norm(
                    transfer["first_left"] - parameter_approximation
                )
            )
        )
        wronskian_residuals.append(
            float(transfer["base_Wronskian_residual"])
        )
    return {
        "proper_durations": list(DURATIONS),
        "value_residuals": value_residuals,
        "parameter_jet_residuals": parameter_residuals,
        "value_halving_ratio": value_residuals[1] / value_residuals[0],
        "parameter_jet_halving_ratio": (
            parameter_residuals[1] / parameter_residuals[0]
        ),
        "Wronskian_residuals": wronskian_residuals,
        "affine_history_role": (
            "NUMERICAL_CAUCHY_GERM_CROSSCHECK_NOT_A_PROMOTED_PHYSICAL_"
            "ENDPOINT_OR_COMPLETE_C2_HISTORY"
        ),
    }


def _channel_payload(
    channel: str,
    x0: float,
    h0: float,
    rate0: float,
    rate_h0: float,
    *,
    chirality: int | None = None,
) -> dict[str, Any]:
    if channel == "scalar":
        generator = scalar_channel_cauchy_generator_jets(
            3.0,
            x0,
            rate0,
            SPECTRAL_PARAMETER,
            h0,
            rate_h0,
        )

        def builder(proper_time: float) -> dict[str, np.ndarray]:
            return scalar_channel_log_radius_jets(
                3.0,
                x0 + rate0 * proper_time,
                SPECTRAL_PARAMETER,
                h0 + rate_h0 * proper_time,
                0.0,
                0.0,
            )

        metadata = {
            "channel": "scalar",
            "unit_radius_spatial_eigenvalue": 3.0,
        }
    else:
        if chirality not in (-1, 1):
            raise ValueError("product Dirac chirality required")
        generator = product_dirac_channel_cauchy_generator_jets(
            1.5,
            x0,
            rate0,
            SPECTRAL_PARAMETER,
            h0,
            rate_h0,
            chirality=chirality,
        )

        def builder(proper_time: float) -> dict[str, np.ndarray]:
            return product_dirac_channel_log_radius_jets(
                1.5,
                x0 + rate0 * proper_time,
                SPECTRAL_PARAMETER,
                h0 + rate_h0 * proper_time,
                0.0,
                chirality=chirality,
                mixed_second_direction=0.0,
            )

        metadata = {
            "channel": "factorized_product_Dirac",
            "unit_radius_Dirac_eigenvalue": 1.5,
            "chirality": chirality,
        }
    germ = local_transfer_cauchy_germ(generator)
    return {
        **metadata,
        "generator_Cauchy_jet": {
            key: _matrix(value) for key, value in generator.items()
        },
        "transfer_germ": {
            key: _matrix(value)
            for key, value in germ.items()
            if isinstance(value, np.ndarray) and value.shape == (2, 2)
        },
        "crosscheck": _crosscheck(builder, germ),
        "endpoint_condition_imposed": False,
        "explicit_matrix_inverse_formed": False,
    }


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("all C2 local-transfer inputs required")
    birth, matching = (_load(path) for path in (BIRTH, MATCHING))
    if not (birth.get("validation_passed") and matching.get("validation_passed")):
        raise RuntimeError("validated C2 birth and diagram match required")
    x0 = float(birth["C2_birth_coefficient"]["center_log_R4"])
    rate0 = float(
        birth["C2_birth_coefficient"]["center_D_tau_log_R4"]
    )
    rows: list[dict[str, Any]] = []
    for direction in birth["C2_birth_quotient_jet"][
        "representative_directions"
    ]:
        h0, rate_h0 = (
            float(value) for value in direction["C2_birth_Cauchy_jet"]
        )
        rows.append(
            {
                "reset_quotient_direction": int(
                    direction["right_singular_direction"]
                ),
                "birth_parameter_log_radius": h0,
                "birth_parameter_proper_rate": rate_h0,
                "channels": {
                    "scalar_c_3": _channel_payload(
                        "scalar", x0, h0, rate0, rate_h0
                    ),
                    "product_Dirac_lambda_1_5_chirality_plus": (
                        _channel_payload(
                            "product_dirac",
                            x0,
                            h0,
                            rate0,
                            rate_h0,
                            chirality=1,
                        )
                    ),
                    "product_Dirac_lambda_1_5_chirality_minus": (
                        _channel_payload(
                            "product_dirac",
                            x0,
                            h0,
                            rate0,
                            rate_h0,
                            chirality=-1,
                        )
                    ),
                },
            }
        )
    witnesses = [
        channel
        for row in rows
        for channel in row["channels"].values()
    ]
    validation = {
        "validated_actual_C2_birth_jet_consumed": True,
        "existing_C2_operator_type_match_consumed": matching["adjudication"][
            "new_C2_physical_theory_required"
        ]
        is False,
        "both_independent_reset_quotient_directions_propagated": len(rows) == 2,
        "scalar_and_both_Dirac_chiralities_assembled": all(
            len(row["channels"]) == 3 for row in rows
        ),
        "all_value_germs_show_cubic_order_halving": all(
            0.11 < witness["crosscheck"]["value_halving_ratio"] < 0.14
            for witness in witnesses
        ),
        "all_first_jet_germs_show_cubic_order_halving": all(
            0.11
            < witness["crosscheck"]["parameter_jet_halving_ratio"]
            < 0.14
            for witness in witnesses
        ),
        "all_transfer_Wronskians_close": all(
            max(witness["crosscheck"]["Wronskian_residuals"]) < 1.0e-12
            for witness in witnesses
        ),
        "no_endpoint_condition_or_matrix_inverse_used": all(
            witness["endpoint_condition_imposed"] is False
            and witness["explicit_matrix_inverse_formed"] is False
            for witness in witnesses
        ),
        "no_affine_crosscheck_promoted_to_complete_physical_history": True,
        "no_selector_endpoint_scale_action_term_recurrence_gate_or_chord_added": True,
    }
    return {
        "artifact": "BHSM_N12_C2_OUTGOING_LOCAL_TRANSFER_GERM",
        "status": "ACTUAL_C2_CHANNEL_TRANSFER_AND_FIRST_QUOTIENT_JET_GERM_DERIVED",
        "classification": (
            "THE_CERTIFIED_ACTUAL_C2_BIRTH_CAUCHY_DATA_FIX_THE_EXACT_"
            "PROPER_TIME_GENERATOR_CAUCHY_JETS_AND_THE_INVERSE_FREE_"
            "SECOND_ORDER_OUTGOING_TRANSFER_GERM_FOR_SCALAR_AND_BOTH_"
            "FACTORIZED_PRODUCT_DIRAC_CHIRALITIES_IN_TWO_INDEPENDENT_"
            "RESET_QUOTIENT_DIRECTIONS;_NO_FUTURE_ENDPOINT_OR_COMPLETE_"
            "MAXIMAL_RESPONSE_IS_PROMOTED"
        ),
        "exact_identities": {
            "transfer": (
                "T(tau)=I+tau*G0+(tau^2/2)*(G0^2+D_tau_G0)+o(tau^2)"
            ),
            "first_quotient_jet": (
                "D_xi_T=tau*D_xi_G0+(tau^2/2)*(D_xi_G0*G0+G0*D_xi_G0+D_xi_D_tau_G0)+o(tau^2)"
            ),
            "scalar": {
                "V": "c*exp(-2*x)",
                "D_tau_V": "-2*H*V",
                "D_xi_V": "-2*h*V",
                "D_xi_D_tau_V": "(4*H*h-2*h_H)*V",
            },
            "product_Dirac": {
                "s": "chi*lambda*exp(-x)",
                "D_tau_G": "diag(H*s,-H*s)",
                "D_xi_G": "diag(h*s,-h*s)",
                "D_xi_D_tau_G": "diag((h_H-H*h)*s,-(h_H-H*h)*s)",
            },
        },
        "actual_C2_birth_data": {
            "log_R4": x0,
            "D_tau_log_R4": rate0,
            "source": BIRTH.relative_to(ROOT).as_posix(),
        },
        "spectral_probe": {
            "z": SPECTRAL_PARAMETER,
            "role": (
                "NUMERICAL_CROSSCHECK_ONLY;_THE_ALGEBRAIC_GERM_IDENTITIES_"
                "HOLD_FOR_ARBITRARY_NATIVE_z"
            ),
        },
        "reset_quotient_rows": rows,
        "diagram_feed": {
            "C2_local_leg_transfer": "DERIVED_THROUGH_SECOND_PROPER_TIME_ORDER",
            "C2_local_leg_first_quotient_jet": "DERIVED_THROUGH_SECOND_PROPER_TIME_ORDER",
            "downstream_C2_load": "NOT_SELECTED_AND_NOT_REQUIRED_FOR_THE_LOCAL_TWO_BOUNDARY_GERM",
            "composition_when_available": (
                "USE_EXISTING_TERMINAL_LOAD_SCHUR_REDUCTION_WITH_THE_LATER_"
                "AE2_OR_FRIEDRICHS_RESPONSE"
            ),
            "complete_M_C2": "OPEN_AFTER_VALIDATED_SEGMENT_AND_MAXIMAL_CONTINUATION",
        },
        "exact_next_dependency": (
            "CERTIFY_A_NONZERO_OUTGOING_C2_COEFFICIENT_SEGMENT_WITH_A_"
            "REMAINDER_BOUND_IN_THE_PHYSICAL_EVENT_DESINGULARIZED_CHART,_"
            "THEN_INTEGRATE_THE_EXISTING_TRIANGULAR_TRANSFER_JET_ON_THAT_"
            "ACTUAL_SEGMENT_WITHOUT_PROMOTING_ITS_VALIDATION_EDGE_TO_AN_ENDPOINT"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_FIRST_VALIDATED_C2_REGULAR_SEGMENT",
            "actual_C2_birth_and_transfer_germ": "DERIVED",
            "actual_nonzero_C2_segment": "OPEN",
            "complete_M_C2_and_second_jet": "OPEN",
            "zero_source_force": "OPEN_AFTER_COMPLETE_C2_REALIZATION",
            "same_action_saddle": "OPEN_AFTER_FORCE",
            "physical_Hessian": "OPEN_AFTER_SADDLE",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in INPUTS
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
    print(
        json.dumps(
            {
                "status": payload["status"],
                "quotient_directions": len(payload["reset_quotient_rows"]),
                "validation_passed": payload["validation_passed"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
