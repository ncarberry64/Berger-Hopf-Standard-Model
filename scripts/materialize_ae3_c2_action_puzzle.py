"""Materialize the first current-C2 full-field puzzle attachment."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae3_c2_action_puzzle import (
    ACTION_VERSION,
    CLASSIFICATION,
    reduced_product_dirac_hs_source_jet,
    section_fit_ledger,
)
from bhsm.interface.aether_forward_c2_finite_core_descriptor import (
    assemble_finite_core_descriptor,
)


ARTIFACTS = ROOT / "artifacts"
DESCRIPTOR_JSON = ARTIFACTS / (
    "flagship_integration/BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
)
DESCRIPTOR_NPZ = ARTIFACTS / (
    "flagship_integration/BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.npz"
)
HISTORICAL_SOURCE = ARTIFACTS / "BHSM_aether_rank16_u1_hs_vertex_matrices_v16_01.json"
AE3_LOCALIZATION = ARTIFACTS / (
    "action_extension/BHSM_ACTION_AE3_RECIPROCAL_JOIN_LOCALIZATION.json"
)
TARGET = ARTIFACTS / (
    "action_extension/BHSM_AE3_C2_FULL_FIELD_PUZZLE_ASSEMBLY.json"
)
INPUTS = (
    DESCRIPTOR_JSON,
    DESCRIPTOR_NPZ,
    HISTORICAL_SOURCE,
    AE3_LOCALIZATION,
    ROOT / "src/bhsm/interface/aether_forward_c2_finite_core_descriptor.py",
    ROOT / "src/bhsm/interface/aether_rank16_u1_hs_vertex_matrices_v16_01.py",
    ROOT / "src/bhsm/interface/ae3_c2_action_puzzle.py",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def _summary(values: np.ndarray) -> dict[str, float]:
    array = np.asarray(values, dtype=float)
    return {
        "minimum": float(np.min(array)),
        "maximum": float(np.max(array)),
        "maximum_absolute": float(np.max(np.abs(array))),
    }


def build_payload() -> dict[str, Any]:
    missing = [path.as_posix() for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("C2 puzzle inputs required: " + ", ".join(missing))

    descriptor = json.loads(DESCRIPTOR_JSON.read_text(encoding="utf-8"))
    historical = json.loads(HISTORICAL_SOURCE.read_text(encoding="utf-8"))
    localization = json.loads(AE3_LOCALIZATION.read_text(encoding="utf-8"))
    with np.load(DESCRIPTOR_NPZ) as data:
        x = np.asarray(data["node_log_R4_center"], dtype=float)
        h = np.asarray(data["segment_proper_duration_proof_center"], dtype=float)
        channels: dict[str, Any] = {}
        exact_reassembly = True
        for chirality, suffix in (
            (1, "product_Dirac_lambda1_5_chirality_plus"),
            (-1, "product_Dirac_lambda1_5_chirality_minus"),
        ):
            rebuilt = assemble_finite_core_descriptor(
                log_radii=x,
                proper_durations=h,
                channel="product_Dirac",
                unit_channel_value=1.5,
                chirality=chirality,
            )
            comparisons = {
                name: bool(np.array_equal(rebuilt[name], data[f"{suffix}__{name}"]))
                for name in (
                    "K_diagonal",
                    "K_off_diagonal",
                    "M_diagonal",
                    "M_off_diagonal",
                    "element_coefficient",
                )
            }
            exact_reassembly = exact_reassembly and all(comparisons.values())
            W = np.asarray(data[f"{suffix}__element_coefficient"], dtype=float)
            jet = reduced_product_dirac_hs_source_jet(
                proper_durations=h,
                base_W=W,
                source_profile=np.ones_like(W),
            )
            channels[suffix] = {
                "chirality": chirality,
                "angular_value": 1.5,
                "dimension": int(W.size),
                "segment_count": int(W.size),
                "descriptor_exactly_reassembled": all(comparisons.values()),
                "descriptor_array_comparisons": comparisons,
                "generalized_gap_lower": descriptor["descriptor_pencils"][suffix][
                    "generalized_gap_lower"
                ],
                "base_W_summary": _summary(W),
                "unit_source_vertex_diagonal_summary": _summary(jet["vertex_diagonal"]),
                "unit_source_vertex_off_diagonal_summary": _summary(
                    jet["vertex_off_diagonal"]
                ),
                "unit_source_contact_diagonal_summary": _summary(
                    jet["contact_diagonal"]
                ),
                "unit_source_contact_off_diagonal_summary": _summary(
                    jet["contact_off_diagonal"]
                ),
                "source_jet_real_symmetric": bool(
                    np.allclose(
                        jet["vertex_elements"],
                        np.swapaxes(jet["vertex_elements"], 1, 2),
                        atol=0.0,
                        rtol=0.0,
                    )
                    and np.allclose(
                        jet["contact_elements"],
                        np.swapaxes(jet["contact_elements"], 1, 2),
                        atol=0.0,
                        rtol=0.0,
                    )
                ),
                "contact_form_positive_semidefinite_by_element_factorization": True,
                "explicit_inverse_formed": False,
            }

    fit = section_fit_ledger()
    validation = {
        "current_AE3_localization_input_valid": localization["validation_passed"] is True,
        "current_C2_descriptor_input_valid": descriptor["validation_passed"] is True,
        "historical_source_algebra_input_valid": historical["validation_passed"] is True,
        "both_chiral_descriptors_exactly_reassembled": exact_reassembly,
        "both_chiral_source_jets_real_symmetric": all(
            row["source_jet_real_symmetric"] for row in channels.values()
        ),
        "both_chiral_descriptor_gap_bounds_positive": all(
            row["generalized_gap_lower"] > 0.0 for row in channels.values()
        ),
        "far_core_edge_not_promoted_to_physical_endpoint": descriptor[
            "endpoint_event_child_partition"
        ]["far_core_edge_is_physical_endpoint"]
        is False,
        "proof_center_not_promoted_to_selected_physical_history": descriptor[
            "coefficient_path"
        ]["proof_centers_are_exact_physical_states"]
        is False,
        "family_factor_is_existing_I3": historical["rank16_trace_ledger"][
            "family_matrix"
        ]
        == "I3",
        "no_new_continuous_coefficient": historical["rank16_trace_ledger"][
            "new_continuous_coefficient"
        ]
        is False,
        "electromagnetic_vertex_not_claimed": True,
        "particle_spectrum_not_rebuilt": True,
        "prediction_not_emitted": fit["prediction_emitted"] is False,
    }
    return {
        "artifact": "BHSM_AE3_C2_FULL_FIELD_PUZZLE_ASSEMBLY",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "method": fit["method"],
        "domain": {
            "background": "ACTUAL_RESET_GENERATED_C2_FINITE_CORE_FAMILY",
            "retained_boundary": "C2_BIRTH_TRACE_NODE_0",
            "far_boundary": "FRIEDRICHS_FORM_CORE_TRUNCATION_ONLY",
            "proof_centers_are_selected_physical_histories": False,
            "maximal_exterior_attached": False,
        },
        "operator_piece": {
            "field_sector": "LOWEST_PRODUCT_DIRAC_WEYL_CHANNEL",
            "angular_value": 1.5,
            "chiralities": [-1, 1],
            "family_factor": "I3",
            "family_noncentral_mass_operator_derived": False,
            "source_probe": "UNIT_COMMUTING_REDUCED_LR_HS_PROBE",
            "source_shift": "W_e(epsilon)=W_e+epsilon*p_e_for_p_e=1",
            "first_derivative": "V_e=2*W_e*p_e*M_e+p_e*C",
            "second_contact_derivative": "Q_e=2*p_e^2*M_e",
            "transverse_electromagnetic_vertex": "NOT_DERIVED_BY_THIS_PIECE",
            "dynamical_HS_coordinate": "NOT_ATTACHED_BY_THIS_PIECE",
            "channels": channels,
        },
        "puzzle_section_fit": fit,
        "claim_boundary": {
            "derived": [
                "current_C2_lowest_Weyl_quadratic_operator_pencils_for_both_chiralities",
                "exact_current_domain_unit_reduced_LR_HS_source_and_contact_jets",
                "compatible_family_central_I3_tensor_attachment",
            ],
            "not_derived": [
                "physical_HS_saddle_or_fermion_mass",
                "family_mass_splitting",
                "transverse_photon_vertex_or_muon_F2_zero",
                "physical_particle_pole",
                "full_current_C2_field_action",
                "maximal_history_operator",
            ],
        },
        "inputs": {str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "CURRENT_C2_PRODUCT_DIRAC_QUADRATIC_PIECE_ATTACHED": True,
        "CURRENT_C2_REDUCED_HS_SOURCE_JET_DERIVED": True,
        "CURRENT_C2_TRANSVERSE_ELECTROMAGNETIC_VERTEX_DERIVED": False,
        "CURRENT_FULL_FIELD_ACTION_COMPLETE": False,
        "MUON_MAGNETIC_MOMENT_DERIVED": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE3 C2 puzzle validation failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT))


if __name__ == "__main__":
    main()
