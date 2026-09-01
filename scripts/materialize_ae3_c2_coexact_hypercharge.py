"""Materialize the current-C2 lowest-Weyl coexact hypercharge source jet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae3_c2_coexact_hypercharge import (
    ACTION_VERSION,
    CLASSIFICATION,
    coexact_hypercharge_puzzle_ledger,
    lowest_weyl_coexact_hypercharge_source_jet,
)


ARTIFACTS = ROOT / "artifacts"
DESCRIPTOR_JSON = ARTIFACTS / (
    "flagship_integration/BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
)
DESCRIPTOR_NPZ = ARTIFACTS / (
    "flagship_integration/BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.npz"
)
RANK16_SOURCE = ARTIFACTS / "BHSM_aether_rank16_u1_hs_vertex_matrices_v16_01.json"
C2_PUZZLE = ARTIFACTS / (
    "action_extension/BHSM_AE3_C2_FULL_FIELD_PUZZLE_ASSEMBLY.json"
)
TARGET = ARTIFACTS / (
    "action_extension/BHSM_AE3_C2_COEXACT_HYPERCHARGE_SOURCE_JET.json"
)
INPUTS = (
    DESCRIPTOR_JSON,
    DESCRIPTOR_NPZ,
    RANK16_SOURCE,
    C2_PUZZLE,
    ROOT / "src/bhsm/interface/ae3_c2_coexact_hypercharge.py",
    ROOT / "src/bhsm/interface/aether_rank16_u1_hs_vertex_matrices_v16_01.py",
    ROOT / "src/bhsm/interface/completion/exact_berger_dirac_cap_obstruction_v14_59.py",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _real_summary(values: np.ndarray) -> dict[str, float]:
    array = np.asarray(values)
    return {
        "minimum_real": float(np.min(array.real)),
        "maximum_real": float(np.max(array.real)),
        "maximum_absolute": float(np.max(np.abs(array))),
        "maximum_imaginary_absolute": float(np.max(np.abs(array.imag))),
    }


def _block_lift_matches(
    blocks: np.ndarray, scalar: np.ndarray, *, tolerance: float = 2.0e-16
) -> tuple[bool, float]:
    expected = np.asarray(scalar)[:, None, None] * np.eye(2)[None, :, :]
    scale = np.maximum(1.0, np.abs(expected))
    residual = float(np.max(np.abs(blocks - expected) / scale))
    return residual <= tolerance, residual


def build_payload() -> dict[str, Any]:
    missing = [path.as_posix() for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("coexact hypercharge inputs required: " + ", ".join(missing))
    descriptor = _load(DESCRIPTOR_JSON)
    rank16 = _load(RANK16_SOURCE)
    c2_puzzle = _load(C2_PUZZLE)
    trace = rank16["rank16_trace_ledger"]
    rows: dict[str, Any] = {}
    with np.load(DESCRIPTOR_NPZ) as data:
        x = np.asarray(data["node_log_R4_center"], dtype=float)
        h = np.asarray(data["segment_proper_duration_proof_center"], dtype=float)
        inverse_midpoint_radii = np.exp(-0.5 * (x[:-1] + x[1:]))
        for chirality, suffix in (
            (1, "product_Dirac_lambda1_5_chirality_plus"),
            (-1, "product_Dirac_lambda1_5_chirality_minus"),
        ):
            jet = lowest_weyl_coexact_hypercharge_source_jet(
                proper_durations=h,
                inverse_radii=inverse_midpoint_radii,
                source_profile=np.ones_like(h),
                chirality=chirality,
            )
            diag_match, diag_residual = _block_lift_matches(
                jet["background_diagonal_blocks"], data[f"{suffix}__K_diagonal"]
            )
            off_match, off_residual = _block_lift_matches(
                jet["background_off_diagonal_blocks"],
                data[f"{suffix}__K_off_diagonal"],
            )
            stored_W = np.asarray(data[f"{suffix}__element_coefficient"])
            W_residual = float(
                np.max(
                    np.abs(stored_W - chirality * 1.5 * inverse_midpoint_radii)
                    / np.maximum(1.0, np.abs(stored_W))
                )
            )
            rows[suffix] = {
                "chirality": chirality,
                "segment_count": int(h.size),
                "angular_level": 0,
                "angular_dimension": 2,
                "background_diagonal_is_exact_I2_lift": diag_match,
                "background_off_diagonal_is_exact_I2_lift": off_match,
                "background_diagonal_relative_residual": diag_residual,
                "background_off_diagonal_relative_residual": off_residual,
                "stored_W_relative_residual": W_residual,
                "vertex_diagonal_summary": _real_summary(jet["vertex_diagonal_blocks"]),
                "vertex_off_diagonal_summary": _real_summary(
                    jet["vertex_off_diagonal_blocks"]
                ),
                "contact_diagonal_summary": _real_summary(
                    jet["contact_diagonal_blocks"]
                ),
                "contact_off_diagonal_summary": _real_summary(
                    jet["contact_off_diagonal_blocks"]
                ),
                "vertex_elements_Hermitian": bool(
                    np.allclose(
                        jet["vertex_elements"],
                        jet["vertex_elements"].conj().transpose(0, 2, 1),
                        atol=0.0,
                        rtol=0.0,
                    )
                ),
                "contact_elements_positive_semidefinite_by_factorization": True,
                "source_generator_traceless": jet["source_generator_traceless"],
                "source_generator_square_is_identity": jet[
                    "source_generator_square_is_identity"
                ],
                "explicit_inverse_formed": False,
            }

    puzzle = coexact_hypercharge_puzzle_ledger()
    validation = {
        "current_C2_descriptor_valid": descriptor["validation_passed"] is True,
        "current_C2_puzzle_attachment_valid": c2_puzzle["validation_passed"] is True,
        "historical_rank16_source_algebra_valid": rank16["validation_passed"] is True,
        "rank16_three_family_hypercharge_square_trace_is_10": trace[
            "three_family_hypercharge_square_trace"
        ]
        == 10.0,
        "rank16_family_factor_is_I3": trace["family_matrix"] == "I3",
        "both_background_chiral_block_lifts_match": all(
            row["background_diagonal_is_exact_I2_lift"]
            and row["background_off_diagonal_is_exact_I2_lift"]
            for row in rows.values()
        ),
        "both_stored_W_paths_match_lowest_Berger_block": all(
            row["stored_W_relative_residual"] <= 2.0e-16 for row in rows.values()
        ),
        "both_source_jets_Hermitian": all(
            row["vertex_elements_Hermitian"] for row in rows.values()
        ),
        "coexact_generator_contract_exact": all(
            row["source_generator_traceless"]
            and row["source_generator_square_is_identity"]
            for row in rows.values()
        ),
        "far_core_is_not_physical_endpoint": descriptor[
            "endpoint_event_child_partition"
        ]["far_core_edge_is_physical_endpoint"]
        is False,
        "proof_center_is_not_selected_history": descriptor["coefficient_path"][
            "proof_centers_are_exact_physical_states"
        ]
        is False,
        "physical_photon_not_identified": puzzle[
            "physical_electromagnetic_vertex_derived"
        ]
        is False,
        "no_prediction_emitted": puzzle["prediction_emitted"] is False,
    }
    return {
        "artifact": "BHSM_AE3_C2_COEXACT_HYPERCHARGE_SOURCE_JET",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "domain": {
            "background": "ACTUAL_RESET_GENERATED_C2_FINITE_CORE_FAMILY",
            "retained_boundary": "C2_BIRTH_TRACE_NODE_0",
            "far_boundary": "FRIEDRICHS_FORM_CORE_TRUNCATION_ONLY",
            "proof_center_selected_as_physical_history": False,
        },
        "derivation": {
            "lowest_Berger_block": "D_0=(3/2)*R4^-1*I2",
            "coexact_unit_generator": "G=sigma_z",
            "chiral_first_order_factor": "W_s(epsilon)=s*(D_0+epsilon*p*G)",
            "element_form": "K_e=S/h_tensor_I2+M_tensor_W_s^2+C_tensor_W_s",
            "first_source_derivative": (
                "V_e=M_tensor_(W_s*dW_s+dW_s*W_s)+C_tensor_dW_s"
            ),
            "second_contact_derivative": "Q_e=2*M_tensor_dW_s^2",
            "unit_profile_used_in_certificate": True,
            "new_gauge_coupling_or_scale": False,
        },
        "rank16_attachment": {
            "one_family_hypercharge_square_trace": trace[
                "one_family_hypercharge_square_trace"
            ],
            "three_family_hypercharge_square_trace": trace[
                "three_family_hypercharge_square_trace"
            ],
            "family_factor": trace["family_matrix"],
            "gauge_coupling_derived_here": False,
        },
        "chiral_rows": rows,
        "puzzle_section_fit": puzzle,
        "claim_boundary": {
            "derived": [
                "current_C2_lowest_Weyl_spatial_coexact_U1Y_source_jet",
                "current_C2_lowest_Weyl_spatial_coexact_U1Y_contact_jet",
                "rank16_charge_square_and_family_central_attachment",
            ],
            "not_derived": [
                "dynamical_current_C2_U1Y_gauge_and_ghost_action",
                "broken_electroweak_saddle",
                "physical_photon_or_Weinberg_mixing",
                "muon_simple_pole_or_F2_zero",
                "maximal_history_exterior_vertex",
            ],
        },
        "inputs": {str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "CURRENT_C2_COEXACT_U1Y_SOURCE_JET_DERIVED": True,
        "CURRENT_C2_PHYSICAL_PHOTON_VERTEX_DERIVED": False,
        "MUON_MAGNETIC_MOMENT_DERIVED": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        failed = [key for key, value in payload["validation"].items() if not value]
        raise SystemExit("C2 coexact hypercharge validation failed: " + ", ".join(failed))
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT))


if __name__ == "__main__":
    main()
