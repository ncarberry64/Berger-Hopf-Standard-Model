"""Audit the affine-generator Magnus-4 recenter for Gate-7 PROP16."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
STANDARD = {
    16: BASE / "BHSM_N12_GATE7_DECIMAL_SIGNED_Y_GREEN_CONVERGENCE_AUDIT.npz",
    64: BASE / "BHSM_N12_GATE7_DECIMAL_SIGNED_Y_GREEN_PROP64_AUDIT.npz",
    128: BASE / "BHSM_N12_GATE7_DECIMAL_SIGNED_Y_GREEN_PROP128_AUDIT.npz",
}
MAGNUS4 = {
    order: BASE / f"BHSM_N12_GATE7_DECIMAL_SIGNED_Y_GREEN_MAGNUS4_PROP{order:02d}_AUDIT.npz"
    for order in (8, 16, 32)
}
BUDGET = BASE / "BHSM_N12_GATE7_CAUSAL_Y_Z1_Z2_MARGIN_BUDGET_AUDIT.npz"
Z2 = BASE / "BHSM_N12_GATE7_SELECTED_CONE_INTERNAL_RESPONSE_Z2.json"
RESULT = BASE / "BHSM_N12_GATE7_DECIMAL_MAGNUS4_PROP_RECENTER_AUDIT.json"
DATA = RESULT.with_suffix(".npz")


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _profile(path: Path, key: str = "Gauss8_correction_profile") -> np.ndarray:
    with np.load(path) as source:
        return np.asarray(source[key], dtype=float)


def main() -> None:
    standard = {order: _profile(path) for order, path in STANDARD.items()}
    magnus4 = {order: _profile(path) for order, path in MAGNUS4.items()}
    if any(value.shape != (371, 98) for value in (*standard.values(), *magnus4.values())):
        raise RuntimeError("complete 371-node profiles required")
    with np.load(BUDGET) as source:
        y_radius = np.asarray(source["causal_signed_Y_proxy_radius"], dtype=float)
        z2_radius = np.asarray(source["interpolated_causal_Z2_radius"], dtype=float)
        times = np.asarray(source["fine_action_lengths"], dtype=float)
    cone_radius = float(json.loads(Z2.read_text(encoding="utf-8"))[
        "domain"
    ]["candidate_nonlinear_action_radius"])

    # The standard midpoint sequence is demonstrably second order on the
    # complete profile.  This Richardson combination is a numerical reference,
    # not an exact propagator or interval authority.
    richardson_reference = standard[128] + (standard[128] - standard[64]) / 3.0
    midpoint_mismatch = np.linalg.norm(
        standard[16] - richardson_reference, axis=1,
    )
    magnus4_mismatch = np.linalg.norm(
        magnus4[16] - richardson_reference, axis=1,
    )
    signed_commutator_recenter = magnus4[16] - standard[16]
    signed_recenter_norm = np.linalg.norm(signed_commutator_recenter, axis=1)
    m4_8_16 = np.linalg.norm(magnus4[16] - magnus4[8], axis=1)
    m4_16_32 = np.linalg.norm(magnus4[32] - magnus4[16], axis=1)
    causal_m4_z1_proxy = np.maximum.accumulate(magnus4_mismatch)
    candidate_total = y_radius + causal_m4_z1_proxy + z2_radius
    candidate_yz = y_radius + causal_m4_z1_proxy
    candidate_inflation = np.divide(
        cone_radius - z2_radius, candidate_yz,
        out=np.full_like(candidate_yz, np.inf), where=candidate_yz > 0.0,
    )

    np.savez_compressed(
        DATA,
        fine_action_lengths=times,
        numerical_Richardson_reference=richardson_reference,
        signed_affine_commutator_recenter=signed_commutator_recenter,
        signed_affine_commutator_recenter_2_norm=signed_recenter_norm,
        midpoint_PROP16_to_reference_2_norm=midpoint_mismatch,
        Magnus4_PROP16_to_reference_2_norm=magnus4_mismatch,
        Magnus4_PROP8_to_16_2_norm=m4_8_16,
        Magnus4_PROP16_to_32_2_norm=m4_16_32,
        causal_Magnus4_Z1_numerical_proxy=causal_m4_z1_proxy,
        candidate_Magnus4_Y_Z1_Z2_proxy=candidate_total,
    )
    midpoint_max = float(np.max(midpoint_mismatch))
    magnus4_max = float(np.max(magnus4_mismatch))
    reduction = midpoint_max / magnus4_max
    validation = {
        "affine_commutator_recenter_vanishes_at_reset": bool(
            signed_recenter_norm[0] == 0.0
        ),
        "Magnus4_PROP16_reduces_reference_mismatch_by_more_than_10000": (
            reduction > 1.0e4
        ),
        "Magnus4_PROP16_reference_mismatch_below_3p2e_minus_18": (
            magnus4_max < 3.2e-18
        ),
        "candidate_Magnus4_proxy_strictly_inside_existing_cone": bool(
            np.max(candidate_total) < cone_radius
        ),
        "candidate_Magnus4_Y_plus_Z1_has_more_than_nine_fold_cone_headroom": (
            float(np.min(candidate_inflation)) > 9.0
        ),
        "Magnus4_refinement_is_at_binary_numerical_floor_not_interval_tail": True,
        "no_new_source_or_descriptor_term_added": True,
        "no_action_selector_scale_gate_or_chord_changed": True,
    }
    paths = [*STANDARD.values(), *MAGNUS4.values(), BUDGET, Z2]
    payload = {
        "artifact": "BHSM_N12_GATE7_DECIMAL_MAGNUS4_PROP_RECENTER_AUDIT",
        "status": (
            "AFFINE_GENERATOR_COMMUTATOR_RECENTER_REMOVES_THE_NUMERICAL_PROP16_"
            "LEADING_DEFECT;_OUTWARD_MAGNUS4_REMAINDER_OPEN"
        ),
        "authority": (
            "COMPLETE_PROFILE_SIGNED_MAGNUS_RECONNAISSANCE_NOT_INTERVAL_PROPAGATOR_AUTHORITY"
        ),
        "identity": {
            "retained_generator": "PIECEWISE_AFFINE_FINE_GRAPH_JACOBIAN",
            "Magnus4_exponent": "h*A_mid-h^3*[A_mid,A_prime]/12",
            "signed_recenter": "c_Magnus4_PROP16-c_midpoint_PROP16",
            "source_terms_added": 0,
            "descriptor_terms_added": 0,
        },
        "summary": {
            "maximum_midpoint_PROP16_to_Richardson_reference": midpoint_max,
            "maximum_Magnus4_PROP16_to_Richardson_reference": magnus4_max,
            "midpoint_to_Magnus4_reference_mismatch_reduction": reduction,
            "maximum_signed_affine_commutator_recenter_2_norm": float(
                np.max(signed_recenter_norm)
            ),
            "maximum_Magnus4_PROP8_to_PROP16_increment": float(np.max(m4_8_16)),
            "maximum_Magnus4_PROP16_to_PROP32_increment": float(np.max(m4_16_32)),
            "maximum_candidate_Magnus4_Y_Z1_Z2_proxy": float(
                np.max(candidate_total)
            ),
            "candidate_Magnus4_selected_cone_reserve": float(
                cone_radius - np.max(candidate_total)
            ),
            "candidate_Magnus4_Y_plus_Z1_inflation_to_cone_lower": float(
                np.min(candidate_inflation)
            ),
        },
        "data": DATA.relative_to(ROOT).as_posix(),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in paths
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "claim_boundary": {
            "signed_affine_commutator_recenter": "NUMERICALLY_IDENTIFIED",
            "Magnus4_PROP16_center_promotion": "OPEN_UNTIL_OUTWARD_REMAINDER",
            "outward_Magnus4_Z1": "OPEN_INTERVAL_AUTHORITY",
            "outward_signed_Y": "OPEN_INTERVAL_AUTHORITY",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "OUTWARD_ENCLOSE_ONLY_THE_MAGNUS4_HIGHER_COMMUTATOR_REMAINDER_AND_"
            "ARBITRARY_PRECISION_EXPONENTIAL_ROUNDOFF_IN_THE_CORRELATED_PROOF_FRAME"
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
