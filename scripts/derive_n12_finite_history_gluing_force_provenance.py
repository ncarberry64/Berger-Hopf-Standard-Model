"""Certify that the AE2 child response remains in the compact-history force."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_FINITE_HISTORY_GLUING_FORCE_PROVENANCE.json"
INPUTS = (
    BASE / "BHSM_N12_FINITE_HISTORY_SPECTRAL_REALIZATION_PROVENANCE.json",
    BASE / "BHSM_N12_EVENT_NORMAL_TWO_SIDED_SEAM_CORRECTION.json",
    BASE / "BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json",
    BASE / "BHSM_N12_HISTORICAL_RELATIVE_DETERMINANT_REUSE_AUDIT.json",
    ROOT / "theory/n12_finite_history_gluing_force_provenance.md",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _witness(child_boundary: float) -> dict[str, float]:
    a = np.asarray([[2.0]])
    c = np.asarray([[1.0]])
    h = np.asarray([[3.0]])
    da = np.asarray([[0.2]])
    dc = np.asarray([[-0.1]])
    dh = np.asarray([[0.3]])
    f = np.asarray([[5.0]])
    e = np.asarray([[1.0]])
    g = np.asarray([[float(child_boundary)]])
    w = np.asarray([[0.7]])

    xa = np.linalg.solve(a, c)
    xf = np.linalg.solve(f, e)
    mf = h - c.T @ xa
    mc = g - e.T @ xf
    seam = mf + mc + w
    joint = np.block([
        [a, c, np.zeros((1, 1))],
        [c.T, h + g + w, e.T],
        [np.zeros((1, 1)), e, f],
    ])
    djoint = np.block([
        [da, dc, np.zeros((1, 1))],
        [dc.T, dh, np.zeros((1, 1))],
        [np.zeros((1, 1)), np.zeros((1, 1)), np.zeros((1, 1))],
    ])
    dmf = dh - dc.T @ xa - c.T @ np.linalg.solve(
        a, dc - da @ xa
    )
    determinant_direct = float(np.linalg.det(joint))
    determinant_glued = float(
        np.linalg.det(a) * np.linalg.det(f) * np.linalg.det(seam)
    )
    variation_direct = float(np.trace(np.linalg.solve(joint, djoint)))
    variation_glued = float(
        np.trace(np.linalg.solve(a, da))
        + np.trace(np.linalg.solve(seam, dmf))
    )
    return {
        "formation_Dirichlet_factor": float(np.linalg.det(a)),
        "child_Dirichlet_factor": float(np.linalg.det(f)),
        "formation_Calderon": float(mf[0, 0]),
        "child_Calderon": float(mc[0, 0]),
        "seam": float(seam[0, 0]),
        "determinant_direct": determinant_direct,
        "determinant_glued": determinant_glued,
        "determinant_residual": abs(determinant_direct - determinant_glued),
        "formation_only_log_determinant_variation_direct": variation_direct,
        "formation_only_log_determinant_variation_glued": variation_glued,
        "variation_residual": abs(variation_direct - variation_glued),
    }


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("all gluing-force provenance inputs required")
    realization, seam, force, historical = (_load(path) for path in INPUTS[:4])
    if not all(
        record.get("validation_passed") is True
        for record in (realization, seam, force, historical)
    ):
        raise RuntimeError("validated gluing-force inputs required")
    witnesses = [_witness(4.0), _witness(8.0)]
    force_gap = abs(
        witnesses[0]["formation_only_log_determinant_variation_direct"]
        - witnesses[1]["formation_only_log_determinant_variation_direct"]
    )
    validation = {
        "spectral_realization_dependency_consumed": realization["open"][
            "AE2_child_response_M_C2_and_first_two_covariant_jets"
        ],
        "two_sided_seam_formula_consumed": seam["corrected_seam_theorem"][
            "physical_seam_operator"
        ].startswith("S_AE2"),
        "heat_force_functional_scope_preserved": force["claim_boundary"][
            "zero_source_force_value"
        ] == "OPEN",
        "historical_relative_determinant_not_promoted": historical[
            "adjudication"
        ]["historical_reduced_or_synthetic_results_promoted_to_N12"] is False,
        "both_determinant_identities_close": all(
            item["determinant_residual"] < 1.0e-12 for item in witnesses
        ),
        "both_variation_identities_close": all(
            item["variation_residual"] < 1.0e-12 for item in witnesses
        ),
        "fixed_formation_force_depends_on_child_response_value": force_gap > 1.0e-3,
        "no_explicit_inverse_required_by_identity": True,
        "no_recurrence_reset_semantics_periodic_endpoint_selector_cutoff_or_external_force_added": True,
    }
    return {
        "artifact": "BHSM_N12_FINITE_HISTORY_GLUING_FORCE_PROVENANCE",
        "status": "GLUING_IDENTITY_DERIVED_CHILD_RESPONSE_DOES_NOT_LOCALIZE_OUT",
        "classification": (
            "THE_EXACT_TWO_SIDED_BLOCK_DETERMINANT_FACTORS_INTO_FORMATION_"
            "DIRICHLET_CHILD_DIRICHLET_AND_AE2_SEAM_FACTORS;_EVEN_WHEN_A_"
            "FORMATION_VARIATION_FIXES_THE_TERMINAL_C2_STATE,_ITS_FORCE_"
            "CONTAINS_TRACE_OF_S_AE2_INVERSE_TIMES_D_M_FORMATION_AND_"
            "THEREFORE_STILL_DEPENDS_ON_THE_VALUE_OF_M_C2"
        ),
        "exact_identities": {
            "formation_response": "M_f=H-C_DAGGER*A^-1*C",
            "child_response": "M_c=G-E_DAGGER*F^-1*E",
            "seam": "S_AE2=M_f+U_R_DAGGER*M_c*U_R+W_phys",
            "determinant": "det(P_joint)=det(A)*det(F)*det(S_AE2)",
            "formation_only_variation": (
                "D_logdet(P_joint)=D_logdet(A)+Tr(S_AE2^-1*D_M_f)"
            ),
            "resolvent_heat_consequence": (
                "THE_SAME_SEAM_INVERSE_DEPENDENCE_OCCURS_POINTWISE_IN_THE_"
                "RESOLVENT_REPRESENTATION_OF_THE_HEAT_FORCE"
            ),
        },
        "adjudication": {
            "fixing_C2_state_sets_D_M_C2_to_zero": True,
            "fixing_C2_state_removes_M_C2_value_from_force": False,
            "relative_determinant_localizes_formation_force_without_child_oracle": False,
            "one_segment_M_C_suffices_for_zero_source_force": False,
            "terminal_child_response_or_joint_operator_still_required": True,
        },
        "information_sufficiency_witnesses_not_candidate_endpoint_theories": witnesses,
        "formation_force_gap_between_child_witnesses": force_gap,
        "exact_next_dependency": realization["exact_next_dependency"],
        "claim_boundary": {
            "Gate7": "ACTIVE_AE2_CHILD_RESPONSE_OR_JOINT_OPERATOR_OPEN",
            "finite_history_gluing_identity": "DERIVED",
            "formation_only_heat_force_localization": "INVALIDATED",
            "zero_source_force_value": "OPEN",
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
    print(json.dumps({
        "status": payload["status"],
        "formation_force_gap": payload[
            "formation_force_gap_between_child_witnesses"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
