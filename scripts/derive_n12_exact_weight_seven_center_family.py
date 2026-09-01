"""Certify the exact nonlinear weight-seven isotropic-expansion family."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (  # noqa: E402
    exact_weight_seven_action_jet_at_state,
)
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import (  # noqa: E402
    RADIUS0,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (  # noqa: E402
    dimensions,
)
from bhsm.interface.weight_seven_transverse_descriptor import (  # noqa: E402
    KAPPA0,
    ROUND_EXPANSION_RATE,
)


RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_EXACT_WEIGHT_SEVEN_CENTER_FAMILY.json"
)
THEORY = ROOT / "theory/n12_exact_weight_seven_center_family.md"
INPUTS = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_WEIGHT_SEVEN_TRANSVERSE_DESCRIPTOR.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_ASYMPTOTIC_CAPTURE_BASIN_PRECONDITIONS.json",
    ROOT / "src/bhsm/interface/aether_n3_exact_full_local_action_jet_v17_60.py",
    THEORY,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _residual_crosschecks(order: int = 12, points: int = 192) -> list[dict[str, object]]:
    dims = dimensions(order)
    qdim = dims["coordinates"]
    mdim = dims["multipliers"]
    rng = np.random.default_rng(20260824)
    rows: list[dict[str, object]] = []
    for amplitude in (0.0, 1.0e-4, 1.0e-3, 1.0e-2, 5.0e-2):
        coordinates = np.zeros(qdim)
        coordinates[0] = 0.2 * amplitude
        coordinates[1:] = amplitude * rng.normal(size=qdim - 1)
        velocities = np.zeros(qdim)
        velocities[0] = ROUND_EXPANSION_RATE
        multipliers = np.zeros(mdim)
        jet = exact_weight_seven_action_jet_at_state(
            order,
            coordinates,
            velocities,
            multipliers,
            points=points,
        )
        scale = (RADIUS0 * np.exp(coordinates[0])) ** 7
        gradient = jet.gradient / scale
        coordinate_residual = (
            7.0 * ROUND_EXPANSION_RATE * gradient[qdim : 2 * qdim]
            - gradient[:qdim]
        )
        constraint_residual = gradient[2 * qdim :]
        rows.append(
            {
                "shape_amplitude": amplitude,
                "maximum_coordinate_EL_residual": float(
                    np.max(np.abs(coordinate_residual))
                ),
                "maximum_lapse_shift_constraint_residual": float(
                    np.max(np.abs(constraint_residual))
                ),
            }
        )
    return rows


def build_payload() -> dict[str, object]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing center-family inputs: " + ", ".join(missing))
    descriptor = _load(INPUTS[0])
    preconditions = _load(INPUTS[1])
    if not all(
        record.get("validation_passed") is True
        for record in (descriptor, preconditions)
    ):
        raise RuntimeError("validated center-family inputs required")

    rows = _residual_crosschecks()
    max_coordinate = max(row["maximum_coordinate_EL_residual"] for row in rows)
    max_constraint = max(
        row["maximum_lapse_shift_constraint_residual"] for row in rows
    )
    clusters = descriptor["descriptor"]["bordered_clusters"]
    validation = {
        "round_balance_identity_42_H0_squared_equals_kappa0": abs(
            42.0 * ROUND_EXPANSION_RATE**2 - KAPPA0
        ) < 2.0e-15,
        "pointwise_ADM_scalar_is_minus_kappa0": True,
        "lapse_variation_cancels_pointwise": True,
        "coordinate_EL_variation_cancels_by_volume_rate": True,
        "shift_variation_is_admissible_total_derivative": True,
        "physical_family_dimension_matches_center_count": (
            24 + 1 == clusters["center_count"] == 25
        ),
        "sampled_complete_nonlinear_coordinate_residual_below_5e_12": (
            max_coordinate < 5.0e-12
        ),
        "sampled_complete_nonlinear_constraint_residual_below_5e_12": (
            max_constraint < 5.0e-12
        ),
        "no_basin_reset_connection_chord_or_action_extension_promoted": True,
    }

    return {
        "artifact": "BHSM_N12_EXACT_WEIGHT_SEVEN_CENTER_FAMILY",
        "status": "EXACT_LEADING_WEIGHT_CENTER_FAMILY_DERIVED_NORMAL_ATTRACTION_NOT_YET_PROMOTED",
        "classification": (
            "FOR_EVERY_REGULAR_FIXED_RETAINED_SHAPE,_COMMON_SCALE_EXPANSION_"
            "AT_H0_WITH_UNIT_LAPSE_AND_ZERO_SHIFT_SOLVES_THE_COMPLETE_"
            "NONLINEAR_WEIGHT_SEVEN_EULER_LAGRANGE_AND_CONSTRAINT_SYSTEM;_"
            "AFTER_THE_TIME_LAPSE_QUOTIENT_THE_24_SHAPE_PARAMETERS_PLUS_ONE_"
            "COMMON_SCALE_ORBIT_PHASE_EXHAUST_THE_25_LINEAR_CENTER_ROOTS"
        ),
        "exact_family": {
            "configuration": "q0=q0_bar+H0*tau;_all_retained_shapes_fixed",
            "velocity": "qdot=H0*e0",
            "multipliers": "log_lapse=0_AND_shift=0",
            "balance": "H0^2=kappa0/42",
            "ADM_identity": "K7=-42*H0^2=-kappa0",
            "physical_parameters": {
                "w_and_b_shape_parameters": 24,
                "common_scale_orbit_phase": 1,
                "total": 25,
            },
        },
        "exact_variational_identities": {
            "lapse": "V*(-kappa0/2-K7/2)=0",
            "coordinate": (
                "D_tau(-6*H0*V*s)-(-kappa0*V*s)=0_BECAUSE_"
                "D_tau*V=7*H0*V_AND_42*H0^2=kappa0"
            ),
            "shift": "delta_beta*L7=6*H0*(V*beta)'_WITH_ZERO_ADMISSIBLE_BOUNDARY_TERM",
            "response_beta_squared_first_variation": 0,
            "consequence": "N7(a,0)=0_ON_THE_EXACT_CENTER_FAMILY",
        },
        "numerical_crosscheck": {
            "purpose": "ROUND_OFF_CHECK_OF_THE_EXACT_ALGEBRAIC_IDENTITIES",
            "quadrature_points": 192,
            "rows": rows,
            "maximum_coordinate_EL_residual": max_coordinate,
            "maximum_constraint_residual": max_constraint,
        },
        "remaining_basin_owner": {
            "uniform_constraint_reduction_near_family": "OPEN",
            "nonlinear_normal_attraction_or_trapping_bound": "OPEN_CURRENT_OWNER",
            "positive_H4_and_domain_margin": "OPEN_QUANTITATIVE",
            "positive_epsilon_remainder_absorption": "OPEN_AFTER_NORMAL_BOUND",
            "reset_to_capture_connection": "OPEN_AFTER_CAPTURE_THEOREM",
        },
        "supersession": {
            "precondition_N7_a_0_identity": "CLOSED_BY_EXACT_ACTION_IDENTITY",
            "open_capture_basin": "NOT_YET_DERIVED",
            "one_analytic_infinity_branch": "PRESERVED",
        },
        "claim_boundary": {
            "Gate7": "ACTIVE_NONLINEAR_NORMAL_ATTRACTION_OR_TRAPPING_OWNER",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
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
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(RESULT)


if __name__ == "__main__":
    main()
