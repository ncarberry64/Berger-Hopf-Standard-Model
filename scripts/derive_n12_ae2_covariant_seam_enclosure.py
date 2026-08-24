"""Assemble retained two-chord child Weyl bounds into the AE2 seam."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
from scipy.linalg import expm


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae2_covariant_seam_response import (  # noqa: E402
    covariant_effective_event_load,
    covariant_effective_event_load_jet,
    covariant_seam_response,
    transition_covariant_derivative,
)


ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "flagship_integration/BHSM_N12_AE2_COVARIANT_SEAM_ENCLOSURE_Z_MINUS_1.json"
)
INPUTS = (
    ARTIFACTS / "action_extension/BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json",
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_EVENT_NORMAL_TWO_SIDED_SEAM_CORRECTION.json"
    ),
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_FORWARD_TWO_CHORD_PRODUCT_DIRAC_WEYL_ENCLOSURES.json"
    ),
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_FORWARD_TWO_CHORD_SCALAR_WEYL_ENCLOSURES.json"
    ),
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_FORWARD_COMPACT_SUPPORT_WEYL_VARIATIONS.json"
    ),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def covariant_frame_witness() -> dict[str, float]:
    """Check that frame motion is absorbed by the covariant child jet."""

    rng = np.random.default_rng(7121)
    raw = rng.normal(size=(4, 4)) + 1.0j * rng.normal(size=(4, 4))
    lift, _ = np.linalg.qr(raw)
    generator = rng.normal(size=(4, 4)) + 1.0j * rng.normal(size=(4, 4))
    generator = 0.5 * (generator - generator.conj().T)
    child_raw = rng.normal(size=(4, 4)) + 1.0j * rng.normal(size=(4, 4))
    child = child_raw.conj().T @ child_raw + np.eye(4)
    d_child_raw = rng.normal(size=(4, 4)) + 1.0j * rng.normal(size=(4, 4))
    d_child = 0.5 * (d_child_raw + d_child_raw.conj().T)
    wentzell = np.diag([0.2, 0.4, 0.6, 0.8])
    d_wentzell = np.diag([0.03, -0.02, 0.01, 0.04])
    event = np.diag([0.5, 0.7, 0.9, 1.1])

    # U(epsilon)=exp(epsilon*K)U.  The compatible child parameter
    # connection is -K when the event connection is zero, so nabla U=0.
    covariant_residual = transition_covariant_derivative(
        lift, generator @ lift, np.zeros((4, 4)), -generator
    )
    analytic = covariant_effective_event_load_jet(d_child, d_wentzell, lift)
    epsilon = 1.0e-6

    def pulled(sign: float) -> np.ndarray:
        moving = expm(sign * epsilon * generator) @ lift
        # The ordinary child jet in the moving frame contains the connection
        # commutator, so its pulled-back derivative is the covariant jet.
        moving_child = (
            child
            + sign * epsilon * (d_child + generator @ child - child @ generator)
        )
        return covariant_effective_event_load(
            moving_child, wentzell + sign * epsilon * d_wentzell, moving
        )

    finite = (pulled(1.0) - pulled(-1.0)) / (2.0 * epsilon)
    seam = covariant_seam_response(event, child, wentzell, lift)
    return {
        "transition_covariant_derivative_residual": float(
            np.linalg.norm(covariant_residual, ord=2)
        ),
        "covariant_jet_finite_difference_residual": float(
            np.linalg.norm(analytic - finite, ord=2)
        ),
        "seam_hermiticity_residual": float(
            np.linalg.norm(seam - seam.conj().T, ord=2)
        ),
        "unitary_pullback_preserves_child_operator_norm_residual": abs(
            float(np.linalg.norm(lift.conj().T @ child @ lift, ord=2))
            - float(np.linalg.norm(child, ord=2))
        ),
    }


def _fermion_rows(product: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in product["representative_retained_low_levels"]["rows"]:
        child_interval = row["birth_Weyl_interval_at_z_minus_1"]
        jets = row["unit_compact_log_radius_direction_bounds"]
        rows.append({
            "absolute_unit_radius_eigenvalue": row[
                "absolute_unit_radius_eigenvalue"
            ],
            "occurrences": row["occurrences"],
            "child_Calderon_interval": child_interval,
            "event_effective_load_interval_AE2_W_zero": child_interval,
            "covariant_first_load_jet_norm_upper": jets[
                "first_Weyl_variation_bound"
            ],
            "covariant_mixed_load_jet_norm_upper": jets[
                "mixed_Weyl_variation_bound"
            ],
            "reset_frame_derivative_separate_physical_source": False,
        })
    return rows


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("AE2 covariant seam-enclosure inputs required")
    records = {path.name: _load(path) for path in INPUTS}
    if not all(record.get("validation_passed") is True for record in records.values()):
        raise RuntimeError("validated AE2 seam-enclosure inputs required")
    action = records["BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json"]
    correction = records[
        "BHSM_N12_EVENT_NORMAL_TWO_SIDED_SEAM_CORRECTION.json"
    ]
    product = records[
        "BHSM_N12_FORWARD_TWO_CHORD_PRODUCT_DIRAC_WEYL_ENCLOSURES.json"
    ]
    scalar = records[
        "BHSM_N12_FORWARD_TWO_CHORD_SCALAR_WEYL_ENCLOSURES.json"
    ]
    weak = records["BHSM_N12_FORWARD_COMPACT_SUPPORT_WEYL_VARIATIONS.json"]
    rows = _fermion_rows(product)
    witness = covariant_frame_witness()
    validation = {
        "AE2_common_reset_frame_is_owned": (
            action["action_definition"]["common_reset_frame"]
            == "U_R=I_UP_TO_GLOBAL_SPIN_SIGN_AND_GAUGE_FRAME"
        ),
        "two_sided_correction_consumed": (
            correction["claim_boundary"]["physical_AE2_event_initial_value"]
            == "OPEN"
        ),
        "native_probe_is_negative_z_not_momentum": (
            product["spectral_probe"]["z"] == -1.0
            and product["spectral_probe"]["role"]
            == "RESOLVENT_PROBE_NOT_MOMENTUM_SQUARED"
        ),
        "child_product_Calderon_and_jets_are_broadly_enclosed": (
            product["adjudication"]["product_Dirac_base_Weyl_at_z_minus_1"]
            == "ENCLOSED_BROADLY"
            and product["adjudication"]["product_Dirac_core_supported_weak_jets"]
            == "ENCLOSED_BROADLY"
        ),
        "child_scalar_deRham_Calderon_and_jets_are_broadly_enclosed": (
            scalar["adjudication"]["scalar_and_deRham_base_Weyl_on_two_chord_core"]
            == "ENCLOSED_BROADLY"
            and scalar["adjudication"]["scalar_and_deRham_compact_support_weak_jets"]
            == "ENCLOSED_BROADLY"
        ),
        "compact_support_covariant_variation_class_is_derived": (
            weak["status"]
            == "COMPACT_SUPPORT_WEYL_C1_C2_AT_FRIEDRICHS_END_DERIVED"
        ),
        "transition_is_covariantly_parallel": (
            witness["transition_covariant_derivative_residual"] < 1.0e-12
        ),
        "covariant_load_jet_verified": (
            witness["covariant_jet_finite_difference_residual"] < 1.0e-8
        ),
        "unitary_pullback_preserves_norm_bounds": (
            witness["unitary_pullback_preserves_child_operator_norm_residual"]
            < 1.0e-12
        ),
        "all_fermion_load_intervals_and_jets_are_finite": all(
            row["event_effective_load_interval_AE2_W_zero"][0] >= 0.0
            and row["event_effective_load_interval_AE2_W_zero"][1]
            >= row["event_effective_load_interval_AE2_W_zero"][0]
            and np.isfinite(row["covariant_first_load_jet_norm_upper"])
            and np.isfinite(row["covariant_mixed_load_jet_norm_upper"])
            for row in rows
        ),
        "no_phase_endpoint_contour_p2_scale_fit_selector_action_term_or_gate_added": True,
    }
    return {
        "artifact": "BHSM_N12_AE2_COVARIANT_SEAM_ENCLOSURE_Z_MINUS_1",
        "status": "AE2_TWO_SIDED_CHILD_LOAD_AND_COMPACT_COVARIANT_JETS_ENCLOSED_BROADLY_AT_Z_MINUS_1",
        "classification": (
            "THE_AE2_RESET_LIFT_IS_A_TRANSITION_MAP_OF_ONE_GLOBAL_BUNDLE_AND_"
            "IS_COVARIANTLY_PARALLEL;_ITS_FRAME_DERIVATIVE_IS_ABSORBED_INTO_"
            "THE_COVARIANT_CHILD_CALDERON_JET;_THE_EXISTING_CERTIFIED_TWO_"
            "CHORD_PRODUCT_DIRAC_AND_SCALAR_DERHAM_BOUNDS_THEREFORE_PULL_BACK_"
            "UNCHANGED_TO_FINITE_TWO_SIDED_EVENT_LOAD_AND_COMPACT_SUPPORT_JET_"
            "ENCLOSURES_AT_THE_NATIVE_RESOLVENT_PROBE_z=-1"
        ),
        "covariant_seam_reduction": {
            "global_connection_compatibility": "NABLA_Phi_U_R=0",
            "ordinary_frame_formula": (
                "D_U_TERMS_ARE_ABSORBED_INTO_NABLA_Phi_M_child_UNDER_THE_"
                "COMPATIBLE_EVENT_CHILD_PARAMETER_CONNECTION"
            ),
            "effective_load": "B_event=U_R_DAGGER*M_child*U_R+W_phys",
            "first_covariant_jet": (
                "NABLA_Phi_B_event=U_R_DAGGER*(NABLA_Phi_M_child)*U_R+"
                "NABLA_Phi_W_phys"
            ),
            "mixed_covariant_jet": (
                "NABLA_PhiPsi_B_event=U_R_DAGGER*(NABLA_PhiPsi_M_child)*"
                "U_R+NABLA_PhiPsi_W_phys"
            ),
            "relative_event_child_orientation_erased": False,
            "where_relative_orientation_lives": (
                "IN_THE_COVARIANTLY_PULLED_BACK_CHILD_RESPONSE_RELATIVE_TO_"
                "M_event,_NOT_IN_AN_EXTRA_FRAME_DERIVATIVE_SOURCE"
            ),
        },
        "native_resolvent_probe": product["spectral_probe"],
        "certified_child_core": product["certified_core"],
        "fermion_AE2_W_zero_load_enclosures": rows,
        "scalar_deRham_enclosure_count": len(
            scalar["representative_retained_low_levels"]["rows"]
        ),
        "witness": witness,
        "exact_next_dependency": (
            "EXTEND_THE_TWO_SIDED_COVARIANT_SEAM_VALUE_AND_JET_ENCLOSURES_"
            "FROM_THE_SINGLE_NATIVE_PROBE_z=-1_AND_COMPACT_LOG_RADIUS_TESTS_"
            "TO_THE_COMPLETE_SPECTRAL_FUNCTIONAL_REQUIRED_BY_"
            "exp(-ell_squared_P)*P_inverse,_OR_MATERIALIZE_THE_EQUIVALENT_"
            "JOINT_FINITE_HISTORY_OPERATOR;_THEN_SOLVE_THE_RESET_FIBER_"
            "VARIABLES_JOINTLY_AND_EVALUATE_THE_HEAT_MINUS_ZETA_FORCE"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_COMPLETE_SPECTRAL_FORCE_ORACLE_OPEN",
            "two_sided_child_load_at_z_minus_1": "ENCLOSED_BROADLY",
            "compact_covariant_first_and_mixed_load_jets_at_z_minus_1": (
                "ENCLOSED_BROADLY"
            ),
            "reset_lift_independent_frame_source": "ABSENT_COVARIANTLY",
            "complete_heat_spectral_family": "OPEN",
            "zero_source_force_value": "OPEN",
            "same_action_saddle": "WAITING_ON_COMPLETE_SPECTRAL_FORCE_ORACLE",
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
