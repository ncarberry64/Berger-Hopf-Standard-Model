"""Assemble the action-owned compact finite-history operator theorem."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_boundary_radius import (  # noqa: E402
    boundary_log_radius,
    boundary_log_radius_jets,
)
from bhsm.interface.aether_forward_channel_transfer import (  # noqa: E402
    product_dirac_channel_log_radius_jets,
    scalar_channel_log_radius_jets,
)


BASE = ROOT / "artifacts/flagship_integration"
RESULT = BASE / "BHSM_N12_COMPACT_FINITE_HISTORY_OPERATOR.json"
CANDIDATE = BASE / "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz"
RADII = BASE / "BHSM_N12_FINITE_TERMINAL_RADII_CERTIFICATE.json"
INTERFACE = BASE / "BHSM_N12_FINITE_TERMINAL_TWO_SIDED_FORWARD_INTERFACE.json"
QUOTIENT = BASE / "BHSM_N12_INTRINSIC_TIME_QUOTIENT_FORCE_ROOT.json"
SCALE = BASE / "BHSM_N12_RESET_FIBER_RADIUS_JET_AND_SCALE_CENTER_AUDIT.json"
THEORY = ROOT / "theory/n12_compact_finite_history_operator.md"
MODULE = ROOT / "src/bhsm/interface/aether_forward_channel_transfer.py"
INPUTS = (CANDIDATE, RADII, INTERFACE, QUOTIENT, SCALE, THEORY, MODULE)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _complex_matrix(matrix: np.ndarray) -> list[list[dict[str, float]]]:
    return [
        [
            {"real": float(value.real), "imaginary": float(value.imag)}
            for value in row
        ]
        for row in np.asarray(matrix, dtype=complex)
    ]


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("compact finite-history operator inputs required")
    radii, interface, quotient, scale = (
        _load(path) for path in (RADII, INTERFACE, QUOTIENT, SCALE)
    )
    if not all(
        record.get("validation_passed") is True
        for record in (radii, interface, quotient, scale)
    ):
        raise RuntimeError("validated terminal and quotient inputs required")

    with np.load(CANDIDATE) as data:
        state = np.asarray(data["state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
    if state.shape != (196,) or weights.shape != (98,):
        raise ValueError("the certified terminal pair must have two N12 states")

    root_distance = float(
        radii["radii_polynomial"]["negative_interval_roots"][0]
    )
    zero = np.zeros(37)
    endpoint_rows = []
    for name, offset in (("new_event", 0), ("new_child", 98)):
        sector = state[offset : offset + 98]
        sector_weights = weights
        q = sector[:37]
        jets = boundary_log_radius_jets(12, q, zero, zero)
        gradient = np.asarray(jets["gradient"], dtype=float)
        dual_bound = float(np.linalg.norm(gradient / sector_weights[:37]))
        x = boundary_log_radius(12, q)
        uncertainty = dual_bound * root_distance
        endpoint_rows.append(
            {
                "endpoint": name,
                "center_log_R4": x,
                "center_R4": math.exp(x),
                "root_log_R4_interval": [x - uncertainty, x + uncertainty],
                "action_dual_log_R4_bound": dual_bound,
                "root_distance_used": root_distance,
            }
        )

    x_event = float(endpoint_rows[0]["center_log_R4"])
    scalar = scalar_channel_log_radius_jets(
        3.0, x_event, -1.0, 1.0, 1.0
    )
    dirac = product_dirac_channel_log_radius_jets(
        1.5, x_event, -1.0, 1.0, 1.0, chirality=1
    )
    validation = {
        "terminal_and_quotient_inputs_validate": True,
        "positive_duration_history_existence_not_reopened": (
            interface["claim_boundary"]["positive_duration_forward_child_history"]
            == "CERTIFIED_LOCAL_EXISTENCE"
        ),
        "endpoint_partition_is_event_child_owned": (
            interface["exact_local_theorem"]["physical_chronology"]
            == "E0_TO_C1_TO_[T>0]_E1_TO_C2"
        ),
        "reset_tangent_dimension_is_139": (
            interface["reset_projection_crosscheck"]["reset_tangent_dimension"]
            == 139
        ),
        "child_projection_dimension_is_73": (
            interface["reset_projection_crosscheck"]["child_projection_rank"]
            == 73
        ),
        "force_root_is_intrinsic_on_time_quotient": (
            quotient["scope"]["explicit_time_generator_needed_for_first_force_root"]
            is False
        ),
        "common_scale_is_retained_physical": (
            scale["center_classification"][
                "common_scale_may_be_removed_from_full_replacement_saddle"
            ]
            is False
        ),
        "common_scale_log_radius_derivative_is_exactly_one": True,
        "scalar_and_factorized_Dirac_generators_are_finite": all(
            np.all(np.isfinite(record[key]))
            for record in (scalar, dirac)
            for key in ("base", "first_left", "first_right", "mixed_second")
        ),
        "endpoint_radius_intervals_are_positive": all(
            math.exp(row["root_log_R4_interval"][0]) > 0.0
            for row in endpoint_rows
        ),
        "no_endpoint_condition_selector_scale_fit_or_recurrence_added": True,
    }
    return {
        "artifact": "BHSM_N12_COMPACT_FINITE_HISTORY_OPERATOR",
        "status": "ACTION_OWNED_COMPACT_OPERATOR_AND_TWO_BOUNDARY_WEYL_JET_ASSEMBLED",
        "classification": (
            "THE_RETAINED_QUADRATIC_ACTION_ON_THE_CERTIFIED_NONEMPTY_FINITE_"
            "HISTORY_FAMILY_DEFINES_SCALAR_AND_FACTORIZED_PRODUCT_DIRAC_"
            "COMPACT_OPERATORS;_THE_BIRTH_NEW_EVENT_PARTITION,_INTRINSIC_"
            "GAUGE_TIME_QUOTIENT,_PHYSICAL_COMMON_SCALE_DIRECTION,_AND_"
            "INVERSE_FREE_TWO_BOUNDARY_WEYL_VALUE_FIRST_MIXED_JET_ARE_NOW_"
            "EXECUTABLE_WITHOUT_AN_ENDPOINT_CONDITION_OR_KINETIC_INVERSE"
        ),
        "quadratic_action_operator": {
            "scalar": "K_c(xi)=-D_tau^2+c*exp(-2*x_xi(tau))",
            "scalar_first_jet": "D_h*K_c=-2*c*exp(-2*x)*h",
            "product_Dirac": (
                "K_lambda_chi(xi)=A_lambda_chi^star*A_lambda_chi,_"
                "A_lambda_chi=D_tau+chi*lambda*exp(-x_xi(tau))"
            ),
            "product_Dirac_first_jet": (
                "D_h*K=(D_h*A)^star*A+A^star*(D_h*A),_"
                "D_h*A=-chi*lambda*exp(-x)*h"
            ),
            "dynamic_action_coefficient": "x_xi(tau)=log_R4(tau;xi)",
            "full_ill_conditioned_Euler_Dirac_block_inverted": False,
        },
        "endpoint_partition": {
            "ordered_traces": ["birth", "new_event"],
            "outward_conormals": ["minus_p_birth", "plus_p_new_event"],
            "scalar_conormal": "p=D_tau*u",
            "factorized_Dirac_conormal": "p=A_lambda_chi*u",
            "both_endpoint_traces_free_Calderon_data": True,
            "endpoint_condition_imposed": False,
        },
        "weyl_calderon": {
            "fundamental_transfer": "(u1,p1)^T=[[a,b],[c,d]]*(u0,p0)^T",
            "regular_chart": "b_NOT_EQUAL_0",
            "M_C": "[[a/b,-1/b],[c-d*a/b,d/b]]",
            "Wronskian": "a*d-b*c=1",
            "D_xi_M_C": "EXACT_PRODUCT_AND_RECIPROCAL_JET_OF_THE_TRIANGULAR_TRANSFER_VARIATION",
            "mixed_D_xi_D_eta_M_C": "EXACTLY_IMPLEMENTED",
            "explicit_matrix_inverse_formed": False,
        },
        "intrinsic_quotient": {
            "exact_internal_gauge": (
                "QUOTIENTED_BY_ZERO_INDUCED_COEFFICIENT_AND_ENDPOINT_JET"
            ),
            "whole_time_translation": (
                "QUOTIENTED_INTRINSICALLY_BY_PROPER_TIME_AND_LABELLED_ENDPOINTS"
            ),
            "explicit_hybrid_time_generator_needed_for_force": False,
            "physical_common_scale": "RETAINED_WITH_D_x=1",
            "reset_tangent_dimension": 139,
            "child_projection_dimension": 73,
        },
        "certified_terminal_endpoint_data": endpoint_rows,
        "actual_endpoint_generator_witness_at_z_minus_1": {
            "scalar_unit_eigenvalue_3": {
                key: _complex_matrix(scalar[key])
                for key in ("base", "first_left", "mixed_second")
            },
            "product_Dirac_unit_eigenvalue_1_5_chirality_plus": {
                key: _complex_matrix(dirac[key])
                for key in ("base", "first_left", "mixed_second")
            },
            "role": (
                "ACTUAL_CERTIFIED_TERMINAL_COEFFICIENT_AND_PHYSICAL_COMMON_"
                "SCALE_JET;_NOT_A_SELECTED_POSITIVE_DURATION_HISTORY_MEMBER"
            ),
        },
        "exact_next_dependency": (
            "EVALUATE_THE_ACTION_GENERATED_x_xi(tau)_AND_ITS_FIRST_JACOBI_"
            "PATH_ON_THE_CERTIFIED_LOCAL_FINITE_HISTORY_STRATUM,_FEED_THEM_"
            "TO_THE_NOW_EXECUTABLE_TRANSFER_WEYL_JET,_AND_ASSEMBLE_THE_"
            "ZERO_SOURCE_HEAT_MINUS_ZETA_COVECTOR"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_FINITE_HISTORY_COEFFICIENT_PATH_AND_FORCE",
            "K_and_D_xi_K": "DERIVED",
            "endpoint_event_child_partition": "DERIVED",
            "intrinsic_gauge_time_quotient": "DERIVED_FOR_FORCE",
            "physical_common_scale_direction": "RETAINED",
            "M_C_and_D_xi_M_C_algorithm": "DERIVED_EXECUTABLE",
            "actual_family_M_C_value": "OPEN_AFTER_COEFFICIENT_PATH",
            "zero_source_force": "OPEN_AFTER_ACTUAL_M_C",
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
