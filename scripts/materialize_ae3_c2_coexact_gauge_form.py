"""Materialize the current-C2 coexact gauge form and normalization boundary."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae3_c2_coexact_gauge_form import (
    ACTION_VERSION,
    CLASSIFICATION,
    coexact_gauge_puzzle_ledger,
    gauge_normalization_interface,
    lowest_coexact_gauge_form_shape,
)


ARTIFACTS = ROOT / "artifacts"
DESCRIPTOR_JSON = ARTIFACTS / (
    "flagship_integration/BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
)
DESCRIPTOR_NPZ = ARTIFACTS / (
    "flagship_integration/BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.npz"
)
TARGET = ARTIFACTS / (
    "action_extension/BHSM_AE3_C2_COEXACT_GAUGE_FORM_SHAPE.json"
)
INPUTS = (
    DESCRIPTOR_JSON,
    DESCRIPTOR_NPZ,
    ARTIFACTS / "action_extension/BHSM_AE3_C2_COEXACT_HYPERCHARGE_SOURCE_JET.json",
    ARTIFACTS / "BHSM_aether_nonabelian_coexact_vertex_v16_03.json",
    ARTIFACTS / "BHSM_aether_event_weighted_unified_pushforward_v15_71.json",
    ARTIFACTS / "BHSM_aether_einstein_cartan_joint_pushforward_v15_75.json",
    ARTIFACTS / "BHSM_aether_cycle_dtn_local_limit_v15_90.json",
    ARTIFACTS / "BHSM_aether_proper_time_joint_pushforward_v15_91.json",
    ROOT / "src/bhsm/interface/ae3_c2_coexact_gauge_form.py",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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
        raise FileNotFoundError("coexact gauge-form inputs required: " + ", ".join(missing))
    descriptor = _load(DESCRIPTOR_JSON)
    source = _load(INPUTS[2])
    coexact = _load(INPUTS[3])
    weighted = _load(INPUTS[4])
    ec = _load(INPUTS[5])
    local_limit = _load(INPUTS[6])
    proper_time = _load(INPUTS[7])
    with np.load(DESCRIPTOR_NPZ) as data:
        x = np.asarray(data["node_log_R4_center"], dtype=float)
        h = np.asarray(data["segment_proper_duration_proof_center"], dtype=float)
    shape = lowest_coexact_gauge_form_shape(log_radii=x, proper_durations=h)
    pencil = shape["component_pencil"]
    normalization = gauge_normalization_interface()
    puzzle = coexact_gauge_puzzle_ledger()
    claims90 = local_limit["claim_boundary"]
    claims91 = proper_time["claim_boundary"]
    validation = {
        "current_C2_descriptor_valid": descriptor["validation_passed"] is True,
        "current_C2_hypercharge_source_valid": source["validation_passed"] is True,
        "historical_coexact_curl_and_BRST_valid": coexact["validation_passed"] is True,
        "historical_parent_weighted_Maxwell_action_valid": weighted[
            "validation_passed"
        ]
        is True,
        "historical_Einstein_Cartan_coefficient_relation_valid": ec[
            "validation_passed"
        ]
        is True,
        "n0_curl_spectrum_is_three_copies_of_plus2": (
            shape["coexact_dimension"] == 3
            and shape["longitudinal_dimension"] == 0
            and np.array_equal(shape["curl_eigenvalues"], np.full(3, 2.0))
        ),
        "finite_core_gauge_shape_gap_positive": pencil["generalized_gap_lower"] > 0.0,
        "finite_core_birth_retained_and_far_node_eliminated": (
            pencil["birth_node_retained"] is True
            and pencil["far_core_Dirichlet_node_eliminated"] is True
        ),
        "no_explicit_inverse": pencil["explicit_matrix_inverse_formed"] is False,
        "BRST_longitudinal_quotient_explicit": shape[
            "BRST_longitudinal_sector_removed_by_coexact_projection"
        ]
        is True,
        "historical_local_limit_rejects_single_Lorentzian_coefficient": claims90[
            "Lorentz_invariant_FmunuFmunu_coefficient_derived"
        ]
        is False,
        "historical_proper_time_rejects_Lorentzian_Maxwell_matching": claims91[
            "Lorentz_invariant_Maxwell_matching_derived"
        ]
        is False,
        "independent_gauge_normalization_forbidden": normalization[
            "independent_gauge_normalization_allowed"
        ]
        is False,
        "normalized_photon_propagator_not_claimed": puzzle[
            "normalized_photon_propagator_derived"
        ]
        is False,
        "far_cutoff_not_promoted_to_endpoint": descriptor[
            "endpoint_event_child_partition"
        ]["far_core_edge_is_physical_endpoint"]
        is False,
        "prediction_not_emitted": puzzle["prediction_emitted"] is False,
    }
    return {
        "artifact": "BHSM_AE3_C2_COEXACT_GAUGE_FORM_SHAPE",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "domain": {
            "background": "ACTUAL_RESET_GENERATED_C2_FINITE_CORE_FAMILY",
            "retained_boundary": "C2_BIRTH_TRACE_NODE_0",
            "far_boundary": "FRIEDRICHS_FORM_CORE_TRUNCATION_ONLY",
            "proof_center_selected_as_physical_history": False,
        },
        "coexact_gauge_form": {
            "angular_level": shape["angular_level"],
            "coexact_dimension": shape["coexact_dimension"],
            "longitudinal_dimension": shape["longitudinal_dimension"],
            "curl_eigenvalues": shape["curl_eigenvalues"].tolist(),
            "local_form": shape["form"],
            "descriptor_dimension_per_component": pencil["dimension"],
            "segment_count": pencil["segment_count"],
            "generalized_gap_lower": pencil["generalized_gap_lower"],
            "K_diagonal_summary": _summary(pencil["K_diagonal"]),
            "K_off_diagonal_summary": _summary(pencil["K_off_diagonal"]),
            "M_diagonal_summary": _summary(pencil["M_diagonal"]),
            "M_off_diagonal_summary": _summary(pencil["M_off_diagonal"]),
            "three_identical_component_blocks": True,
            "BRST_longitudinal_sector_removed": True,
            "explicit_inverse_formed": False,
        },
        "normalization_interface": normalization,
        "puzzle_section_fit": puzzle,
        "claim_boundary": {
            "derived": [
                "current_C2_n0_coexact_gauge_form_shape",
                "exact_threefold_plus2_curl_multiplicity",
                "coexact_BRST_quotient",
                "positive_inverse_free_finite_core_pencil",
            ],
            "not_derived": [
                "one_current_C2_Lorentzian_Maxwell_residue",
                "normalized_hypercharge_or_photon_propagator",
                "broken_electroweak_neutral_mixing",
                "maximal_history_exterior_gauge_operator",
                "muon_F2_zero_or_collision_amplitude",
            ],
        },
        "inputs": {str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "CURRENT_C2_COEXACT_GAUGE_FORM_SHAPE_DERIVED": True,
        "CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED": False,
        "CURRENT_C2_NORMALIZED_PHOTON_PROPAGATOR_DERIVED": False,
        "MUON_MAGNETIC_MOMENT_DERIVED": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        failed = [key for key, value in payload["validation"].items() if not value]
        raise SystemExit("C2 coexact gauge-form validation failed: " + ", ".join(failed))
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT))


if __name__ == "__main__":
    main()
