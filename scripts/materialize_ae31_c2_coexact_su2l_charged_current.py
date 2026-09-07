"""Materialize the current-C2 SU(2)L charged-current family theorem."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_coexact_su2l_charged_current import (
    ACTION_VERSION,
    CLASSIFICATION,
    canonical_quark_family_kernel,
    claim_boundary,
    lowest_weyl_coexact_su2l_charged_source_jets,
    weak_charged_representation_ledger,
)


A = ROOT / "artifacts"
DESC_JSON = A / "flagship_integration/BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
DESC_NPZ = A / "flagship_integration/BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.npz"
J3 = A / "action_extension/BHSM_AE3_C2_COEXACT_SU2L_NEUTRAL_SOURCE_JET.json"
TRANSPORT = A / "action_extension/BHSM_AE3_C2_HOPF_SEMIGROUP_TRANSPORT.json"
GENERATION = A / "BHSM_generation_projector_action_attachment_v8_2.json"
PACKET = ROOT / "docs/research_packets/2026-08-03/BHSM_QUARK_YUKAWA_PAIR_AND_CKM_INTERTWINER_2026-08-03.md"
TARGET = A / "action_extension/BHSM_AE31_C2_COEXACT_SU2L_CHARGED_CURRENT.json"
INPUTS = (
    DESC_JSON,
    DESC_NPZ,
    J3,
    TRANSPORT,
    GENERATION,
    PACKET,
    ROOT / "src/bhsm/interface/ae31_c2_coexact_su2l_charged_current.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def _summary(values: np.ndarray) -> dict[str, float]:
    array = np.asarray(values)
    return {
        "minimum_real": float(array.real.min()),
        "maximum_real": float(array.real.max()),
        "maximum_absolute": float(np.abs(array).max()),
    }


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    descriptor, j3, transport, generation = map(_load, (DESC_JSON, J3, TRANSPORT, GENERATION))
    packet = PACKET.read_text(encoding="utf-8")
    representation = weak_charged_representation_ledger()
    family = canonical_quark_family_kernel()
    rows = {}
    with np.load(DESC_NPZ) as data:
        x = np.asarray(data["node_log_R4_center"])
        duration = np.asarray(data["segment_proper_duration_proof_center"])
        inverse = np.exp(-0.5 * (x[:-1] + x[1:]))
        for chirality, name in ((1, "plus"), (-1, "minus")):
            jet = lowest_weyl_coexact_su2l_charged_source_jets(
                proper_durations=duration,
                inverse_radii=inverse,
                source_profile=np.ones_like(duration),
                chirality=chirality,
            )
            rows[name] = {
                "chirality": chirality,
                "segments": jet["segments"],
                "W1_vertex_summary": _summary(jet["W1_vertex_elements"]),
                "W2_vertex_summary": _summary(jet["W2_vertex_elements"]),
                "W1_contact_summary": _summary(jet["W1_contact_elements"]),
                "W2_contact_summary": _summary(jet["W2_contact_elements"]),
                "coordinate_vertices_Hermitian": bool(
                    np.allclose(
                        jet["W1_vertex_elements"],
                        jet["W1_vertex_elements"].conjugate().transpose(0, 2, 1),
                    )
                    and np.allclose(
                        jet["W2_vertex_elements"],
                        jet["W2_vertex_elements"].conjugate().transpose(0, 2, 1),
                    )
                ),
            }
    boundary = claim_boundary()
    validation = {
        "current_C2_descriptor_valid": descriptor["validation_passed"],
        "neutral_SU2_predecessor_valid": j3["validation_passed"],
        "family_transport_predecessor_valid": transport["validation_passed"],
        "generation_projector_attachment_valid": generation["validation_passed"],
        "historical_packet_kept_prefactors_and_cross_kernel_open": (
            "sector-wide absolute quark scales" in packet
            and "Action derivation of \\(K_{ud}\\)" in packet
        ),
        "raising_and_lowering_are_adjoint": representation["T_minus_is_T_plus_adjoint"],
        "three_family_charged_trace_is_12": representation[
            "three_family_trace_Tminus_Tplus"
        ] == 12.0,
        "both_C2_coordinate_jets_Hermitian": all(
            row["coordinate_vertices_Hermitian"] for row in rows.values()
        ),
        "family_kernel_is_full_rank_identity": (
            family["kernel_rank"] == 3 and family["kernel_unitary"]
        ),
        "canonical_response_commutator_zero": family[
            "response_commutator_norm"
        ] == 0.0,
        "conditional_half_factor_not_promoted": not family[
            "middle_up_half_dressing_inserted"
        ],
        "claim_boundary_fail_closed": (
            boundary["current_C2_coexact_SU2L_charged_source_pair_derived"]
            and not boundary["physical_CKM_matrix_derived"]
            and not boundary["physical_W_pole_derived"]
        ),
    }
    return {
        "artifact": "BHSM_AE31_C2_COEXACT_SU2L_CHARGED_CURRENT",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "domain": {
            "background": "ACTUAL_RESET_GENERATED_C2_FINITE_CORE_FAMILY",
            "coexact_level": 0,
            "family_factor": "C3_family",
        },
        "representation_attachment": representation,
        "chiral_coordinate_rows": rows,
        "canonical_quark_family_kernel": family,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE3.1 SU2L charged-current theorem failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
