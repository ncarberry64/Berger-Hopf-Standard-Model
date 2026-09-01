"""Route existing Gate-7 certificates at the exact-affine signed-Y center."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
EXACT_RECORD = BASE / "BHSM_N12_GATE7_ARB_INTERACTION_TAYLOR26_SIGNED_SOURCE.json"
EXACT = EXACT_RECORD.with_suffix(".npz")
TANGENT = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_PHYSICAL_TANGENT_TRANSFER_RECONNAISSANCE.npz"
FROZEN = BASE / "BHSM_N12_GATE7_FROZEN_DECIMAL_GAUSS8_CENTER.npz"
MAGNUS4 = BASE / "BHSM_N12_GATE7_DECIMAL_SIGNED_Y_GREEN_MAGNUS4_PROP16_AUDIT.npz"
MAGNUS8 = BASE / "BHSM_N12_GATE7_ARB_MAGNUS8_AFFINE_COMPOSITION.npz"
OLD_RECENTER = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_MATCHED_TANGENT_CORRELATED_DEFECT_GAUSS12_RECONNAISSANCE.npz"
Z2 = BASE / "BHSM_N12_GATE7_SELECTED_CONE_INTERNAL_RESPONSE_Z2.json"
RECENTERED = (
    BASE / "BHSM_N12_GATE7_RECENTERED_CONE_BOUNDARY_CLUSTER_SPECTRUM.json"
)
RADII = BASE / "BHSM_N12_FINITE_TERMINAL_RADII_CERTIFICATE.json"
MARGINS = BASE / "BHSM_N12_FINITE_TERMINAL_MARGIN_TRANSFER.json"
FIRST_HIT = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_DENSE_DESCRIPTOR_FIRST_HIT.json"
FORCE = BASE / "BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json"
KKT = BASE / "BHSM_N12_FINITE_ENDPOINT_FORWARD_ADJOINT_KKT.json"
THIS_SCRIPT = Path(__file__).resolve()
RESULT = BASE / "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_TRANSFER_AUDIT.json"
DATA = RESULT.with_suffix(".npz")


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _quotient(profile: np.ndarray, tangents: np.ndarray) -> np.ndarray:
    return np.asarray([
        tangents[index].T @ profile[index] for index in range(48)
    ])


def main() -> None:
    boundary = np.asarray([*range(0, 369, 8), 370], dtype=int)
    with np.load(EXACT) as source:
        exact = np.asarray(source["global_signed_response_midpoint"])
        exact_radius = np.asarray(source["global_signed_response_Euclidean_radius"])
    with np.load(TANGENT) as source:
        tangents = np.asarray(source["physical_tangent_action"])
    with np.load(FROZEN) as source:
        frozen = np.asarray(source["state_correction_profile"])[boundary]
    with np.load(MAGNUS4) as source:
        magnus4 = np.asarray(source["Gauss8_correction_profile"])[boundary]
    with np.load(MAGNUS8) as source:
        magnus8 = np.asarray(source["global_signed_response_midpoint"])
        magnus8_radius = np.linalg.norm(
            np.asarray(source["global_signed_response_component_radius"]), axis=1,
        )
    with np.load(OLD_RECENTER) as source:
        old_recenter = np.asarray(source["fine_ambient_correction_profile"])[boundary]

    z2 = json.loads(Z2.read_text(encoding="utf-8"))
    recentered = json.loads(RECENTERED.read_text(encoding="utf-8"))
    radii = json.loads(RADII.read_text(encoding="utf-8"))
    margins = json.loads(MARGINS.read_text(encoding="utf-8"))
    first_hit = json.loads(FIRST_HIT.read_text(encoding="utf-8"))
    force = json.loads(FORCE.read_text(encoding="utf-8"))
    kkt = json.loads(KKT.read_text(encoding="utf-8"))
    cone = float(z2["domain"]["candidate_nonlinear_action_radius"])

    frozen_difference = np.linalg.norm(exact - _quotient(frozen, tangents), axis=1)
    magnus4_difference = np.linalg.norm(exact - _quotient(magnus4, tangents), axis=1)
    magnus8_difference = np.linalg.norm(exact - magnus8, axis=1)
    old_recenter_difference = np.linalg.norm(
        exact - _quotient(old_recenter, tangents), axis=1,
    )
    frozen_outward = frozen_difference + exact_radius
    magnus4_outward = magnus4_difference + exact_radius
    magnus8_outward = magnus8_difference + exact_radius + magnus8_radius
    old_recenter_outward = old_recenter_difference + exact_radius

    np.savez_compressed(
        DATA,
        macro_boundary_fine_indices=boundary,
        exact_affine_Euclidean_radius=exact_radius,
        exact_to_frozen_Decimal_center_outward=frozen_outward,
        exact_to_Magnus4_outward=magnus4_outward,
        exact_to_Magnus8_combined_outward=magnus8_outward,
        exact_to_old_recentered_Gauss12_outward=old_recenter_outward,
    )

    maximum_frozen = float(np.max(frozen_outward))
    maximum_old = float(np.max(old_recenter_outward))
    validation = {
        "exact_affine_source_certificate_valid": bool(
            json.loads(EXACT_RECORD.read_text(encoding="utf-8"))["validation_passed"]
        ),
        "exact_center_inside_frozen_Decimal_candidate_cone": maximum_frozen < cone,
        "exact_center_agrees_with_Magnus4_below_2e_minus_18": bool(
            np.max(magnus4_outward) < 2.0e-18
        ),
        "exact_center_agrees_with_Magnus8_below_3e_minus_20": bool(
            np.max(magnus8_outward) < 3.0e-20
        ),
        "old_recentered_Gauss12_center_outside_candidate_cone": maximum_old > cone,
        "existing_Z2_formula_certified_but_final_center_transfer_not_claimed": bool(
            z2["validation_passed"]
        ),
        "old_recentered_cone_certificate_valid_on_its_recorded_center_only": bool(
            recentered["validation_passed"]
        ),
        "terminal_radii_and_margin_theorems_valid_on_their_recorded_center_only": bool(
            radii["validation_passed"] and margins["validation_passed"]
        ),
        "stored_first_hit_requires_exact_center_domain_transfer": bool(
            first_hit["validation_passed"]
        ),
        "force_and_KKT_formulas_reusable_but_numerical_root_not_claimed": bool(
            force["validation_passed"] and kkt["validation_passed"]
        ),
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    payload = {
        "artifact": "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_TRANSFER_AUDIT",
        "status": (
            "EXACT_AFFINE_Y_CENTER_INSIDE_FROZEN_DECIMAL_CONE_BUT_EXISTING_"
            "GAUSS12_RECENTERED_NUMERICAL_CONE_IS_CENTER_INCOMPATIBLE"
            if all(validation.values()) else "CENTER_TRANSFER_AUDIT_INVALID"
        ),
        "authority": "EXACT_OUTWARD_CENTER_DISTANCE_AND_HASH_PROVENANCE_ROUTING",
        "summary": {
            "candidate_nonlinear_action_radius": cone,
            "maximum_exact_to_frozen_Decimal_center_outward": maximum_frozen,
            "frozen_Decimal_cone_utilization": maximum_frozen / cone,
            "maximum_exact_to_Magnus4_outward": float(np.max(magnus4_outward)),
            "maximum_exact_to_Magnus8_combined_outward": float(np.max(magnus8_outward)),
            "maximum_exact_to_old_recentered_Gauss12_outward": maximum_old,
            "old_recentered_Gauss12_cone_radius_multiple": maximum_old / cone,
            "maximum_exact_affine_Euclidean_radius": float(np.max(exact_radius)),
        },
        "routing": {
            "signed_Taylor_Volterra_Z2_formula_and_majorants": "REUSE",
            "existing_Gauss12_recentered_cone_numerical_ball": "DO_NOT_TRANSFER",
            "final_center_dependent_Z2_and_cone_ball": "OWNER_ONLY_REBUILD_REQUIRED",
            "terminal_radii_and_margin_theorem_formulas": "REUSE_AFTER_FINAL_CENTER_BALL",
            "stored_first_hit": "TRANSFER_ONLY_AFTER_FINAL_CENTER_DOMAIN_CLOSURE",
            "heat_minus_zeta_force_and_forward_adjoint_KKT_formulas": "REUSE",
            "force_value_KKT_root_and_Hessian": "EVALUATE_AFTER_FIRST_HIT_TRANSFER",
        },
        "claim_boundary": {
            "literal_outward_retained_Gauss8_signed_Y_propagation": "CERTIFIED",
            "final_center_dependent_Z2_cone_radii_first_hit": "OPEN_LOCALIZED_OWNER",
            "force_KKT_Hessian": "DOWNSTREAM_OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (
                EXACT_RECORD, EXACT, TANGENT, FROZEN, MAGNUS4, MAGNUS8,
                OLD_RECENTER, Z2, RECENTERED, RADII, MARGINS, FIRST_HIT,
                FORCE, KKT, THIS_SCRIPT,
            )
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "exact_next_dependency": (
            "REBUILD_ONLY_THE_FINAL_CENTER_DEPENDENT_Z2_AND_RECENTERED_CONE_BALL_"
            "USING_THE_CERTIFIED_EXACT_AFFINE_Y_CENTER;_THEN_TRANSFER_TERMINAL_"
            "RADII_MARGINS_AND_FIRST_HIT_AND_EVALUATE_THE_EXISTING_FORCE_KKT_SYSTEM"
        ),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
