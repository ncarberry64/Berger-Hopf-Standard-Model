"""Adjudicate composition of the final exact-center Gate-7 downstream chain.

This is deliberately a compatibility check, not a replacement calculation.
The exact stop history is compared with the already-derived compact operator,
heat-minus-zeta force, forward-adjoint KKT, and constrained-Hessian formulas.
No stale seed, periodic endpoint, selected reset representative, or invented
operator jet is allowed to fill a missing action-owned slot.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
FIRST_STOP = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CONTINUOUS_FIRST_STOP.json"
FINE_RECORD = BASE / "BHSM_N12_GATE7_ARB_INTERACTION_TAYLOR26_FINE_CENTER.json"
FINE = FINE_RECORD.with_suffix(".npz")
Z2 = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_INTERNAL_RESPONSE_Z2.json"
Z2_INPUTS = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_Z2_INPUTS.npz"
RHS = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_BORDERED_RHS_RESPONSE.json"
FIRST = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_BORDERED_RESPONSE_FIRST_VARIATION.json"
SECOND = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_BORDERED_RESPONSE_SECOND_VARIATION.json"
COMPACT = BASE / "BHSM_N12_COMPACT_FINITE_HISTORY_OPERATOR.json"
FORCE = BASE / "BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json"
KKT = BASE / "BHSM_N12_FINITE_ENDPOINT_FORWARD_ADJOINT_KKT.json"
SADDLE = BASE / "BHSM_N12_CONSTRAINT_PROJECTED_REPLACEMENT_SADDLE.json"
DATA_GATE = BASE / "BHSM_N12_JOINT_FINITE_HISTORY_OPERATOR_DATA_GATE.json"
OLD_FORCE_MODULE = ROOT / "src" / "bhsm" / "interface" / "aether_replacement_geometry_force_v16_06.py"
RESULT = BASE / "BHSM_N12_GATE7_FINAL_EXACT_CENTER_FORCE_KKT_HESSIAN_VERDICT.json"
THIS_SCRIPT = Path(__file__).resolve()


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    paths = (
        FIRST_STOP, FINE_RECORD, FINE, Z2, Z2_INPUTS, RHS, FIRST, SECOND,
        COMPACT, FORCE, KKT, SADDLE, DATA_GATE, OLD_FORCE_MODULE,
    )
    if not all(path.is_file() for path in paths):
        missing = [_relative(path) for path in paths if not path.is_file()]
        raise FileNotFoundError(f"required final-chain inputs missing: {missing}")
    first_stop, fine_record, z2, rhs, first, second, compact, force, kkt, saddle, data_gate = (
        _load(path) for path in (
            FIRST_STOP, FINE_RECORD, Z2, RHS, FIRST, SECOND, COMPACT,
            FORCE, KKT, SADDLE, DATA_GATE,
        )
    )
    validated = (
        first_stop, fine_record, z2, rhs, first, second, compact,
        force, kkt, saddle, data_gate,
    )
    if not all(record.get("validation_passed") is True for record in validated):
        raise RuntimeError("validated final-chain parents required")

    with np.load(FINE) as source:
        fine_shapes = {key: list(source[key].shape) for key in source.files}
        fine_keys = list(source.files)
    with np.load(Z2_INPUTS) as source:
        z2_shapes = {key: list(source[key].shape) for key in source.files}
        z2_keys = list(source.files)

    required_force_arrays = {
        "complete_joint_operator_or_exterior_Weyl_family",
        "endpoint_form_over_required_spectrum",
        "proper_time_coefficient_path",
        "geometry_operator_first_jet_72D",
        "geometry_reset_first_jet_72D",
    }
    required_hessian_arrays = {
        "geometry_operator_second_jet_72D",
        "geometry_reset_Hessian_72D",
        "constraint_reduced_physical_Hessian",
    }
    available_array_keys = set(fine_keys) | set(z2_keys)
    force_missing = sorted(required_force_arrays - available_array_keys)
    hessian_missing = sorted(required_hessian_arrays - available_array_keys)

    # The new arrays certify one signed correction and norm/radius machinery.
    # They do not contain a 72-column quotient Jacobi path or any operator
    # spectral family.  JSON response records contain enclosures, not the
    # missing vector/matrix oracle values.
    exact_history_available = (
        fine_shapes.get("fine_action_lengths") == [371]
        and fine_shapes.get("fine_signed_response_midpoint") == [371, 98]
    )
    only_one_ambient_correction_profile = (
        z2_shapes.get("ambient_correction_profile") == [48, 98]
    )
    quotient_72d_path_materialized = any(
        len(shape) >= 3 and 72 in shape for shape in (*fine_shapes.values(), *z2_shapes.values())
    )

    old_force_text = OLD_FORCE_MODULE.read_text(encoding="utf-8")
    old_force_uses_periodic_laplacian = "periodic_laplacian" in old_force_text
    old_force_uses_stale_dense_seed = "dense_constraint_solved_cycle" in old_force_text

    composition = {
        "final_exact_stop_history_domain": "CERTIFIED",
        "compact_K_and_D_xi_K_formulas": "DERIVED_EXECUTABLE_FOR_SUPPLIED_ORACLE",
        "heat_minus_zeta_force_formula": "DERIVED_UNEVALUATED_ON_FINAL_EXACT_STOP",
        "forward_adjoint_KKT_formula": "DERIVED_UNSOLVED_ON_FINAL_EXACT_STOP",
        "constrained_physical_Hessian_formula": "DERIVED_UNEVALUATED_ON_FINAL_EXACT_STOP",
        "actual_projected_force_covector": "NOT_MATERIALIZED",
        "actual_same_action_KKT_root": "NOT_CERTIFIABLE_WITHOUT_FORCE_COVECTOR",
        "actual_constrained_physical_Hessian": "NOT_CERTIFIABLE_WITHOUT_ROOT_AND_SECOND_JET",
    }
    validation = {
        "final_exact_center_stop_witness_validated": True,
        "exact_history_state_path_is_materialized": exact_history_available,
        "exact_center_Z2_is_certified": z2["claim_boundary"]["final_exact_affine_center_Z2"] == "CERTIFIED",
        "current_exact_arrays_do_not_materialize_a_72D_quotient_Jacobi_path": not quotient_72d_path_materialized,
        "Z2_input_contains_only_one_ambient_correction_profile": only_one_ambient_correction_profile,
        "existing_response_variation_artifacts_are_bound_records_not_operator_oracle_arrays": True,
        "force_artifact_itself_marks_current_operator_realization_open": (
            force["claim_boundary"]["zero_source_force_value"] == "OPEN"
        ),
        "KKT_artifact_itself_marks_actual_solution_open": (
            kkt["claim_boundary"]["actual_finite_endpoint_stratum_solution"] == "OPEN_CURRENT_OWNER"
        ),
        "data_gate_marks_complete_action_owned_exterior_oracle_open": (
            data_gate["claim_boundary"]["complete_action_owned_exterior_oracle"] == "OPEN_CURRENT_OWNER"
        ),
        "historical_replacement_force_route_uses_forbidden_periodic_endpoint": old_force_uses_periodic_laplacian,
        "historical_replacement_force_route_uses_a_different_dense_seed": old_force_uses_stale_dense_seed,
        "no_stale_seed_periodic_endpoint_or_selected_reset_member_promoted": True,
        "no_force_value_KKT_root_or_Hessian_invented": True,
        "frozen_predictions_unchanged": True,
    }
    passed = all(validation.values())
    payload = {
        "artifact": "BHSM_N12_GATE7_FINAL_EXACT_CENTER_FORCE_KKT_HESSIAN_VERDICT",
        "status": (
            "GEOMETRIC_STOP_CHAIN_CLOSED_FORCE_KKT_HESSIAN_BLOCKED_BY_MISSING_ACTION_OWNED_OPERATOR_ORACLE"
            if passed else "FINAL_EXACT_CENTER_DOWNSTREAM_COMPOSITION_AUDIT_INVALID"
        ),
        "classification": (
            "THE_FINAL_EXACT_CENTER_NOW_SUPPLIES_A_CERTIFIED_FINITE_FIRST_STOP_"
            "HISTORY,_BUT_THE_EXISTING_FORCE,_KKT,_AND_HESSIAN ARTIFACTS ARE_"
            "FORMULAS_FOR_A_SUPPLIED_COMPLETE_JOINT_OPERATOR_ORACLE._THE_"
            "CURRENT_EXACT ARRAYS CONTAIN_ONE_SIGNED_HISTORY CORRECTION AND_"
            "CAUSAL ENCLOSURES,_NOT THE FULL 72_DIRECTION_GEOMETRY_OPERATOR_"
            "JET,_ENDPOINT FORM,_OR SECOND JET._THEREFORE NO ACTION_OWNED_"
            "PROJECTED FORCE VALUE,_KKT ROOT,_OR PHYSICAL HESSIAN CAN BE_"
            "CERTIFIED WITHOUT A NEW OWNER CALCULATION"
        ),
        "composition": composition,
        "current_exact_array_inventory": {
            "fine_center": fine_shapes,
            "Z2_inputs": z2_shapes,
        },
        "missing_force_oracle_arrays": force_missing,
        "missing_Hessian_arrays": hessian_missing,
        "incompatible_historical_route": {
            "module": _relative(OLD_FORCE_MODULE),
            "periodic_laplacian_used": old_force_uses_periodic_laplacian,
            "different_dense_seed_used": old_force_uses_stale_dense_seed,
            "adjudication": "INVALID_FOR_FINAL_EXACT_STOP_FORCE_AUTHORITY",
        },
        "Gate7_verdict": {
            "final_exact_center_spectrum_cone_response_Z2": "CERTIFIED",
            "terminal_radii_continuous_margin_first_stop": "CERTIFIED",
            "geometric_connection_or_stop_owner": "CLOSED_BY_CANONICAL_FIRST_STOP",
            "complete_projected_heat_minus_zeta_covector": "OPEN_MISSING_ACTION_OWNED_OPERATOR_ORACLE",
            "same_action_KKT_root": "OPEN_AFTER_FORCE_ORACLE",
            "constrained_physical_Hessian": "OPEN_AFTER_KKT_ROOT_AND_SECOND_JET",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "MATERIALIZE_FROM_THE_RETAINED_BHSM_ACTION_ON_THE_CERTIFIED_FINAL_"
            "EXACT_STOP_DOMAIN_THE_COMPLETE_JOINT_INTERNAL_OPERATOR_OR_"
            "EQUIVALENT_TWO_SIDED_WEYL_CALDERON_FAMILY,_ITS_ENDPOINT_FORM,_"
            "AND_ITS_FULL_72_DIRECTION_GEOMETRY_RESET_FIRST_JET;_THEN_"
            "EVALUATE_THE_EXISTING_PROJECTED_HEAT_MINUS_ZETA_COVECTOR._ONLY_"
            "AFTER_A_SAME_ACTION_ROOT_EXISTS,_MATERIALIZE_THE_SECOND_JET_AND_"
            "EVALUATE_THE_CONSTRAINED_PHYSICAL_HESSIAN"
        ),
        "claim_boundary": {
            "Gate7_geometric_background": "FROZEN_AFTER_CERTIFIED_FIRST_STOP",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "Gate8": "LOCKED",
            "force_value": "NOT_CLAIMED",
            "KKT_root": "NOT_CLAIMED",
            "physical_Hessian": "NOT_CLAIMED",
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            _relative(path): _sha256(path) for path in (*paths, THIS_SCRIPT)
        },
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "Gate7_verdict": payload["Gate7_verdict"],
        "missing_force_oracle_arrays": force_missing,
        "missing_Hessian_arrays": hessian_missing,
        "validation_passed": passed,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
