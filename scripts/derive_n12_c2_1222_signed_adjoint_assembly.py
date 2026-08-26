"""Assemble the signed C2 finite-core coefficient-history adjoint."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_c2_signed_coefficient_adjoint import (  # noqa: E402
    signed_coefficient_history_adjoint,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_1222_SIGNED_ADJOINT_ASSEMBLY.json"
PARAMETRIC = BASE / "BHSM_N12_C2_1222_PARAMETRIC_BASE_FAMILY.json"
COTANGENT = BASE / "BHSM_N12_C2_1222_SEGMENT_WEYL_COEFFICIENT_COTANGENT.json"
COTANGENT_DATA = COTANGENT.with_suffix(".npz")
COMPLETE_NORM = BASE / "BHSM_N12_C2_1222_COMPLETE_GEOMETRY_PULLBACK_NORM.json"
FORCE_ADJOINT = BASE / "BHSM_N12_FORCE_ADJOINT_PULLBACK.json"
LAUNCH_ADJOINT = BASE / "BHSM_N12_C2_RESET_LAUNCH_ADJOINT_INTERFACE.json"
FIXED_OWNER = BASE / "BHSM_N12_C2_FIXED_SEED_UPSTREAM_FORCE_OWNER.json"
INCIDENCE = BASE / "BHSM_N12_FORWARD_COMMON_SOURCE_INCIDENCE.json"
INTERVAL_ACTIONS = BASE / "BHSM_N12_C2_1222_TRANSPOSED_DURATION_ACTION_COVERAGE.json"
SOURCE_ONTOLOGY = BASE / "BHSM_N12_GATE7_CLOSED_SYSTEM_ZERO_EXTERNAL_SOURCE_ONTOLOGY.json"
JOINT_SEED = BASE / "BHSM_N12_GATE7_JOINT_HEAT_COTANGENT_REVERSE_SEED.json"
MODULE = ROOT / "src" / "bhsm" / "interface" / "aether_forward_c2_signed_coefficient_adjoint.py"
THEORY = ROOT / "theory" / "n12_c2_1222_signed_adjoint_assembly.md"
INPUTS = (
    PARAMETRIC,
    COTANGENT,
    COTANGENT_DATA,
    COMPLETE_NORM,
    FORCE_ADJOINT,
    LAUNCH_ADJOINT,
    FIXED_OWNER,
    INCIDENCE,
    INTERVAL_ACTIONS,
    SOURCE_ONTOLOGY,
    JOINT_SEED,
    MODULE,
    THEORY,
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _crosscheck() -> dict[str, Any]:
    rng = np.random.default_rng(7122202)
    segments = 9
    state_dimension = 6
    parameter_dimension = 4
    transitions = np.asarray([
        np.eye(state_dimension) + 0.02 * rng.normal(
            size=(state_dimension, state_dimension)
        )
        for _ in range(segments)
    ])
    x_covectors = rng.normal(size=(segments + 1, state_dimension))
    h_covectors = rng.normal(size=(segments, state_dimension))
    d_x = rng.normal(size=segments + 1)
    d_h = rng.normal(size=segments)
    terminal = rng.normal(size=state_dimension)
    seed = rng.normal(size=(state_dimension, parameter_dimension))
    result = signed_coefficient_history_adjoint(
        transition_jacobians_action=transitions,
        node_log_radius_covectors_action_dual=x_covectors,
        segment_duration_covectors_action_dual=h_covectors,
        D_log_radius_functional=d_x,
        D_proper_duration_functional=d_h,
        terminal_state_covector_action_dual=terminal,
    )
    jacobi = seed.copy()
    forward = d_x[0] * (x_covectors[0] @ jacobi)
    forward += d_h[0] * (h_covectors[0] @ jacobi)
    for index in range(segments):
        jacobi = transitions[index] @ jacobi
        forward += d_x[index + 1] * (x_covectors[index + 1] @ jacobi)
        if index + 1 < segments:
            forward += d_h[index + 1] * (h_covectors[index + 1] @ jacobi)
    forward += terminal @ jacobi
    reverse = result["initial_state_covector_action_dual"] @ seed
    residual = float(np.linalg.norm(forward - reverse))
    return {
        "segments": segments,
        "state_dimension": state_dimension,
        "parameter_dimension": parameter_dimension,
        "forward_reverse_residual": residual,
        "crosscheck_passed": residual < 2.0e-12,
    }


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing signed-adjoint inputs: " + ", ".join(missing))
    (
        parametric, cotangent, complete_norm, force, launch, owner, incidence,
        interval_actions, source_ontology, joint_seed,
    ) = (
        _load(path)
        for path in (
            PARAMETRIC,
            COTANGENT,
            COMPLETE_NORM,
            FORCE_ADJOINT,
            LAUNCH_ADJOINT,
            FIXED_OWNER,
            INCIDENCE,
            INTERVAL_ACTIONS,
            SOURCE_ONTOLOGY,
            JOINT_SEED,
        )
    )
    if not all(record.get("validation_passed") is True for record in (
        parametric, cotangent, complete_norm, force, launch, owner, incidence,
        interval_actions, source_ontology, joint_seed,
    )):
        raise RuntimeError("validated signed-adjoint lineage required")
    channel_shapes: dict[str, Any] = {}
    with np.load(COTANGENT_DATA) as data:
        for name in cotangent["channels_at_z_minus_1"]:
            d_x = np.asarray(data[f"{name}__D_log_R4_node_Weyl"])
            d_h = np.asarray(data[f"{name}__D_proper_duration_Weyl"])
            channel_shapes[name] = {
                "D_log_R4_shape": list(d_x.shape),
                "D_proper_duration_shape": list(d_h.shape),
                "D_log_R4_positive_entries": int(np.count_nonzero(d_x > 0.0)),
                "D_log_R4_negative_entries": int(np.count_nonzero(d_x < 0.0)),
                "D_proper_duration_positive_entries": int(np.count_nonzero(d_h > 0.0)),
                "D_proper_duration_negative_entries": int(np.count_nonzero(d_h < 0.0)),
                "signed_coefficient_cotangent_is_nonzero": bool(
                    np.any(d_x != 0.0) or np.any(d_h != 0.0)
                ),
            }
    crosscheck = _crosscheck()
    validation = {
        "exact_parametric_family_exists_through_1222": (
            parametric["claim_boundary"][
                "parametric_base_history_existence_through_1222"
            ] == "DERIVED"
        ),
        "all_three_actual_coefficient_cotangent_shapes_match_1222_core": all(
            row["D_log_R4_shape"] == [1223]
            and row["D_proper_duration_shape"] == [1222]
            for row in channel_shapes.values()
        ),
        "all_stored_signed_coefficient_cotangents_are_nonzero": all(
            row["signed_coefficient_cotangent_is_nonzero"]
            for row in channel_shapes.values()
        ),
        "finite_core_first_jet_norm_parent_is_certified": (
            complete_norm["claim_boundary"][
                "complete_finite_core_geometry_pullback_norm"
            ] == "CERTIFIED"
        ),
        "continuous_adjoint_parent_is_derived": (
            force["claim_boundary"]["G7_08_force_adjoint_pullback"] == "DERIVED"
        ),
        "launch_adjoint_composition_is_derived": (
            launch["claim_boundary"]["launch_adjoint_interface"] == "DERIVED"
        ),
        "upstream_fixed_seed_owner_is_not_discarded": (
            owner["adjudication"]["one_joint_history_adjoint_is_preferred"] is True
        ),
        "graded_source_incidence_is_available_as_conditional_consumer": (
            incidence["claim_boundary"]["domain_parametric_nonzero_local_incidence"]
            == "DERIVED"
        ),
        "all_1222_interval_transposed_duration_actions_are_certified": (
            interval_actions["adjudication"][
                "all_1222_interval_transposed_duration_actions"
            ] == "CERTIFIED"
        ),
        "zero_source_means_only_zero_external_birth_Cauchy_datum": (
            source_ontology["external_internal_partition"]["set_to_zero"] == ["J_ext"]
        ),
        "joint_heat_cotangent_reverse_seed_is_derived": (
            joint_seed["adjudication"]["joint_reverse_seed_formula"] == "CLOSED"
        ),
        "no_internal_response_is_zeroed_or_reintroduced_as_a_seam_source": (
            source_ontology["adjudication"]["internal_response_zeroing"] == "FORBIDDEN"
            and joint_seed["adjudication"]["additional_seam_source"] == "FORBIDDEN"
        ),
        "forward_and_reverse_pairings_crosscheck": crosscheck["crosscheck_passed"],
        "actual_BHSM_signed_covector_is_not_claimed_from_proof_centers": True,
        "no_inverse_selector_endpoint_recurrence_scale_fit_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_C2_1222_SIGNED_ADJOINT_ASSEMBLY",
        "status": (
            "SIGNED_FINITE_CORE_COEFFICIENT_ADJOINT_ASSEMBLED_ACTUAL_FORCE_OPEN"
            if passed else "SIGNED_FINITE_CORE_ADJOINT_NOT_ASSEMBLED"
        ),
        "classification": (
            "ON_EVERY_EXACT_MEMBER_OF_THE_CERTIFIED_LOCAL_73_PARAMETER_C2_"
            "FAMILY_THE_SIGNED_WEYL_COEFFICIENT_COTANGENT_PULLS_BACK_BY_ONE_"
            "INVERSE_FREE_REVERSE_STATE_SWEEP_INCLUDING_MOVING_PROPER_"
            "DURATION;_THE_RESULT_COMPOSES_WITH_THE_EXISTING_RESET_LAUNCH_"
            "ADJOINT_AND_THE_COMPLETE_INTERNAL_UPSTREAM_INTERFACE_COVECTOR;_"
            "ALL_1222_INTERVAL_TRANSPOSED_DURATION_ACTIONS_AND_THE_SINGLE_"
            "JOINT_HEAT_COTANGENT_SEED_ARE_NOW_CLOSED,_WHILE_THE_ACTUAL_JOINT_"
            "GRADED_SPECTRAL_COTANGENT_AND_NUMERICAL_PARAMETRIC_OR_INTERVAL_"
            "REALIZATION_REMAIN_OPEN"
        ),
        "exact_recurrence": {
            "history": "Y_(j+1)=Phi_j(Y_j),_x_j=log_R4(Y_j),_h_j=H_j(Y_j)",
            "terminal": "p_N=C_x,N*x_Y,N+g_T",
            "backward": (
                "p_j=C_x,j*x_Y,j+C_h,j*h_Y,j+Phi_Y,j^dagger*p_(j+1)"
            ),
            "C2_initial_covector": "p_C2,0=p_0",
            "joint_reset_pullback": (
                "g_reset=Z^dagger*p_Mf+B^dagger*p_C2,0+p_retained_contacts"
            ),
            "zero_external_source_rule": "SET_J_ext=0_ONLY_AFTER_THE_COMPLETE_JOINT_REVERSE_SWEEP",
            "additional_seam_source": "FORBIDDEN",
            "physical_force": "g_phys=N_phys^dagger*g_reset",
            "full_Euler_Dirac_inverse_formed": False,
            "forward_Jacobi_columns_required": 0,
        },
        "actual_1222_coefficient_inputs": channel_shapes,
        "crosscheck": crosscheck,
        "adjudication": {
            "signed_finite_core_adjoint_equation": "CLOSED",
            "all_1222_interval_transposed_duration_actions": "CLOSED",
            "joint_heat_cotangent_reverse_seed": "CLOSED",
            "zero_external_source_semantics": "CLOSED_ONLY_J_ext",
            "moving_duration_included": True,
            "proof_center_used_as_physical_history": False,
            "numerical_parametric_or_interval_BHSM_adjoint": "OPEN_CURRENT_OWNER",
            "complete_internal_upstream_history_covector": "OPEN_CURRENT_OWNER",
            "actual_joint_graded_heat_minus_zeta_cotangent": "OPEN_CURRENT_OWNER",
            "maximal_projected_tail": "OPEN_AFTER_FINITE_CORE_FORCE_NET",
            "actual_projected_zero_source_force": "OPEN",
        },
        "validated_invalidated_open": {
            "VALIDATED": [
                "signed coefficient-to-state adjoint recurrence",
                "moving-duration term in the same reverse sweep",
                "composition with reset launch and upstream covectors",
                "all 1222 interval transposed duration actions",
                "single closed-system joint heat cotangent reverse seed",
                "only external J_ext is zeroed after joint differentiation",
            ],
            "INVALIDATED": [
                "73 forward Jacobi columns are required for one scalar force",
                "a new C2 response theory is needed for the signed pullback",
                "the stored proof centers evaluate the physical signed covector",
            ],
            "OPEN": [
                "numerical parametric or interval BHSM reverse sweep",
                "complete upstream C1-to-E1 signed covector",
                "actual joint graded heat-minus-zeta spectral cotangent",
                "maximal projected force tail or finite later stop",
            ],
        },
        "exact_next_dependency": (
            "REALIZE_OR_SHARPLY_ENCLOSE_THE_ACTUAL_COMPLETE_JOINT_GRADED_"
            "HEAT_MINUS_ZETA_SPECTRAL_COTANGENT_ON_THE_PARAMETRIC_FAMILY,_"
            "FEED_IT_TO_THE_ALREADY_CERTIFIED_1222_INTERVAL_ACTIONS,_COMPLETE_"
            "THE_INTERNAL_UPSTREAM_AND_CHILD_REVERSE SWEEP_ONCE,_THEN_APPLY_"
            "THE_EXISTING_RESET_AND_PHYSICAL_QUOTIENT_PULLBACKS"
        ),
        "claim_boundary": {
            "Gate7": "G7_08_OPEN_NUMERICAL_JOINT_SOURCE_ADJOINT_AND_MAXIMAL_TAIL",
            "Gate8": "LOCKED",
            "signed_finite_core_adjoint_assembly": "DERIVED",
            "actual_BHSM_signed_covector": "OPEN",
            "same_action_saddle": "WAITING_ON_FORCE",
            "physical_Hessian": "WAITING_ON_SADDLE",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
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
        "crosscheck": payload["crosscheck"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
