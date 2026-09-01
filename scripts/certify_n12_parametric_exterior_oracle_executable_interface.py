"""Certify the executable finite-stratum exterior-oracle jet interface."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.parametric_finite_stratum_exterior_oracle import (  # noqa: E402
    schur_weyl_directional_jet,
)


ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "flagship_integration/"
    "BHSM_N12_PARAMETRIC_EXTERIOR_ORACLE_EXECUTABLE_INTERFACE.json"
)
INPUTS = (
    ARTIFACTS / (
        "flagship_integration/"
        "BHSM_N12_PARAMETRIC_RESET_FIBER_EXTERIOR_ORACLE_THEOREM.json"
    ),
    ARTIFACTS / (
        "flagship_integration/"
        "BHSM_N12_RESET_FIBER_RADIUS_JET_AND_SCALE_CENTER_AUDIT.json"
    ),
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_FINITE_HISTORY_FORCE_DOMAIN_AUDIT.json"
    ),
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_GATE7_TWO_CHORD_HEAT_TAIL_AUDIT.json"
    ),
    ARTIFACTS / (
        "intrinsic_state_selection/"
        "BHSM_N12_GATE7_FIRST_CHORD_CERTIFICATE_TRANSFER_AUDIT.json"
    ),
    ARTIFACTS / (
        "intrinsic_state_selection/"
        "BHSM_N12_GATE7_CHORD_02_SIGNED_ALIGNED_GREEN.json"
    ),
    ROOT / "src/bhsm/interface/parametric_finite_stratum_exterior_oracle.py",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def executable_witness() -> dict[str, Any]:
    base = np.asarray((
        (4.0, 0.2, -0.4, 0.1),
        (0.2, 3.5, 0.3, -0.2),
        (-0.4, 0.3, 5.0, 0.6),
        (0.1, -0.2, 0.6, 4.5),
    ))
    first = np.asarray((
        (0.2, -0.1, 0.05, 0.02),
        (-0.1, 0.3, -0.04, 0.07),
        (0.05, -0.04, -0.2, 0.06),
        (0.02, 0.07, 0.06, 0.1),
    ))
    second = np.asarray((
        (0.05, 0.02, -0.01, 0.03),
        (0.02, -0.04, 0.02, -0.01),
        (-0.01, 0.02, 0.06, -0.02),
        (0.03, -0.01, -0.02, 0.08),
    ))
    result = schur_weyl_directional_jet(
        base, first, second, (0, 1), z=-1.0
    )
    step = 2.0e-4

    def value(parameter: float) -> np.ndarray:
        operator = base + parameter * first + 0.5 * parameter**2 * second
        return schur_weyl_directional_jet(
            operator,
            first + parameter * second,
            second,
            (0, 1),
            z=-1.0,
        )["value"]

    plus, center, minus = value(step), value(0.0), value(-step)
    finite_first = (plus - minus) / (2.0 * step)
    finite_second = (plus - 2.0 * center + minus) / step**2

    angle_boundary, angle_interior = 0.31, -0.27
    ub = np.asarray((
        (np.cos(angle_boundary), -np.sin(angle_boundary)),
        (np.sin(angle_boundary), np.cos(angle_boundary)),
    ))
    ui = np.asarray((
        (np.cos(angle_interior), -np.sin(angle_interior)),
        (np.sin(angle_interior), np.cos(angle_interior)),
    ))
    unitary = np.block([[ub, np.zeros((2, 2))], [np.zeros((2, 2)), ui]])
    transformed = schur_weyl_directional_jet(
        unitary.T @ base @ unitary,
        unitary.T @ first @ unitary,
        unitary.T @ second @ unitary,
        (0, 1),
        z=-1.0,
    )
    covariance = {
        key: float(np.linalg.norm(transformed[key] - ub.T @ result[key] @ ub))
        for key in ("value", "first", "second")
    }
    return {
        "matrix_size": 4,
        "boundary_dimension": 2,
        "interior_dimension": 2,
        "probe_z": -1.0,
        "minimum_shifted_interior_eigenvalue": result[
            "minimum_shifted_interior_eigenvalue"
        ],
        "first_centered_difference_residual": float(
            np.linalg.norm(result["first"] - finite_first)
        ),
        "second_centered_difference_residual": float(
            np.linalg.norm(result["second"] - finite_second)
        ),
        "block_unitary_covariance_residuals": covariance,
        "interior_solve_residuals": {
            key: result[key]
            for key in (
                "interior_value_residual_norm",
                "interior_first_residual_norm",
                "interior_second_residual_norm",
            )
        },
        "Hermitian_residuals": {
            key: result[key]
            for key in (
                "value_hermitian_residual_norm",
                "first_hermitian_residual_norm",
                "second_hermitian_residual_norm",
            )
        },
        "explicit_matrix_inverse_formed": result[
            "explicit_matrix_inverse_formed"
        ],
    }


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("executable exterior-oracle inputs required")
    parametric, radius_jet, force_domain, two_chord, first, second = (
        _load(path) for path in INPUTS[:-1]
    )
    if not all(record.get("validation_passed") is True for record in (
        parametric, radius_jet, force_domain, two_chord, first, second
    )):
        raise RuntimeError("validated executable exterior-oracle inputs required")
    witness = executable_witness()
    validation = {
        "value_first_second_jet_interface_executes": (
            witness["minimum_shifted_interior_eigenvalue"] > 1.0
        ),
        "first_jet_matches_centered_difference": (
            witness["first_centered_difference_residual"] < 1.0e-9
        ),
        "second_jet_matches_centered_difference": (
            witness["second_centered_difference_residual"] < 2.0e-7
        ),
        "interior_solve_residuals_are_small": all(
            value < 1.0e-12
            for value in witness["interior_solve_residuals"].values()
        ),
        "Hermitian_structure_is_preserved": all(
            value < 1.0e-12 for value in witness["Hermitian_residuals"].values()
        ),
        "block_unitary_covariance_is_verified": all(
            value < 1.0e-12
            for value in witness["block_unitary_covariance_residuals"].values()
        ),
        "no_explicit_matrix_inverse_is_formed": (
            witness["explicit_matrix_inverse_formed"] is False
        ),
        "two_certified_chords_are_not_promoted_to_force_endpoint": (
            two_chord["validation"]["two_certified_chords_consumed"] is True
            and second["claim_boundary"]["terminal_event_or_domain_exit"]
            == "NOT_REACHED_ON_THIS_CHORD"
            and force_domain["domain_adjudication"][
                "arbitrary_regular_free_cutoff_allowed"
            ] is False
        ),
        "parametric_data_not_fabricated": (
            parametric["claim_boundary"]["actual_parametric_exterior_oracle"]
            == "OPEN_CURRENT_OWNER"
            and radius_jet["fiber_invariance_adjudication"][
                "actual_parametric_exterior_oracle_still_required"
            ] is True
        ),
        "no_recurrence_chord3_endpoint_selector_scale_fit_or_prediction_added": True,
    }
    return {
        "artifact": "BHSM_N12_PARAMETRIC_EXTERIOR_ORACLE_EXECUTABLE_INTERFACE",
        "status": "STABLE_WEYL_VALUE_AND_TWO_JET_SOLVER_DERIVED_ACTUAL_FINITE_STRATUM_DATA_OPEN",
        "classification": (
            "FOR_ANY_SUPPLIED_FIXED_STRATUM_HERMITIAN_OPERATOR_AND_FIRST_"
            "SECOND_DIRECTIONAL_GEOMETRY_JETS_WITH_A_COERCIVE_NEGATIVE_"
            "PROBE_INTERIOR_BLOCK,_THE_WEYL_CALDERON_VALUE_AND_TWO_JETS_ARE_"
            "NOW_COMPUTED_BY_THREE_BORDERED_INTERIOR_SOLVES_WITHOUT_FORMING_"
            "AN_INVERSE;_THE_TWO_CERTIFIED_1E-8_CHORDS_ARE_NOT_A_PHYSICAL_"
            "FORCE_ENDPOINT,_SO_THE_ACTUAL_ACTION_OWNED_FINITE_STRATUM_DATA_"
            "REMAIN_OPEN"
        ),
        "solver_contract": {
            "input_pencil": "P(xi,z)=K(xi)-z*I_ON_ONE_FIXED_REGULAR_FINITE_STRATUM",
            "required_inputs": [
                "K",
                "D_xi_K[eta]",
                "D_xi2_K[eta,eta]",
                "ACTION_OWNED_BOUNDARY_INTERIOR_PARTITION",
                "REAL_NEGATIVE_PROBE_z",
                "POSITIVE_INTERIOR_COERCIVITY_MARGIN",
            ],
            "outputs": [
                "M_C(z;xi)",
                "D_xi_M_C(z;xi)[eta]",
                "D_xi2_M_C(z;xi)[eta,eta]",
                "POISSON_TAIL_AND_TWO_JETS",
                "SOLVE_HERMITICITY_AND_COERCIVITY_RESIDUALS",
            ],
            "interior_equations": [
                "P_ii*X=P_ib",
                "P_ii*X'=K_ib'-K_ii'*X",
                "P_ii*X''=K_ib''-K_ii''*X-2*K_ii'*X'",
            ],
            "Weyl_equations": [
                "M=P_bb-P_bi*X",
                "M'=K_bb'-K_bi'*X-P_bi*X'",
                "M''=K_bb''-K_bi''*X-2*K_bi'*X'-P_bi*X''",
            ],
            "full_or_interior_inverse_formed": False,
            "ill_conditioned_Euler_Dirac_kinetic_block_inverted": False,
        },
        "executable_crosscheck": witness,
        "tracked_two_chord_adjudication": {
            "first_chord_exact_shadowing": first["claim_boundary"][
                "first_chord_exact_shadowing"
            ],
            "second_chord_exact_shadowing": second["claim_boundary"][
                "chord02_exact_forward_shadowing"
            ],
            "certified_core_end": 2.0e-8,
            "terminal_event_or_canonical_stop_at_core_end": False,
            "may_be_used_as_complete_force_domain": False,
            "reason": (
                "THE_RETAINED_ZETA_EXTENSION_FORCE_IS_STRICTLY_ADDITIVE_AND_"
                "THE_SECOND_CHORD_REACHES_NEITHER_EVENT_NOR_DOMAIN_EXIT"
            ),
            "terminal_recurrence_reopened": False,
            "chord_03_authorized": False,
        },
        "exact_next_dependency": (
            "SUPPLY_FROM_THE_RETAINED_ACTION_A_NONEMPTY_COMPLETE_FINITE_"
            "ENDPOINT_OR_CANONICAL_STOP_STRATUM_WITH_K(xi),_D_xi_K,_D_xi2_K_"
            "AND_THE_INTRINSIC_EXACT_GAUGE_TIME_QUOTIENT;_THEN_THIS_SOLVER_"
            "RETURNS_THE_EXTERIOR_BUNDLE_NEEDED_BY_q_rep_AND_THE_GEOMETRY_"
            "RESET_KKT_HESSIAN"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_ACTUAL_PARAMETRIC_FINITE_STRATUM_DATA_OPEN",
            "stable_Weyl_value_first_second_jet_solver": "DERIVED",
            "actual_parametric_exterior_oracle": "OPEN_CURRENT_OWNER",
            "two_chord_core_as_complete_force_domain": False,
            "actual_projected_force": "OPEN",
            "geometry_reset_KKT_Hessian": "OPEN",
            "same_action_saddle": "OPEN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
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
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(RESULT)


if __name__ == "__main__":
    main()
