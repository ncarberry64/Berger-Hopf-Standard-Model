"""Materialize the AE3.1 intrinsic M4 charged-lepton action transport."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_intrinsic_m4_lepton_action import (
    ACTION_VERSION,
    CLASSIFICATION,
    action_composition_contract,
    charged_lepton_yukawa_operator,
    claim_boundary,
    conditional_higgs_saddle,
    conditional_tree_mass_operator,
    first_variation_and_pole_gate,
    local_tangent_frame_poles,
)


A = ROOT / "artifacts"
TRANSPORT = A / "action_extension/BHSM_AE3_C2_HOPF_SEMIGROUP_TRANSPORT.json"
HS = A / "action_extension/BHSM_AE3_C2_HS_FERMION_MIXED_VARIATION.json"
PUZZLE = A / "action_extension/BHSM_AE3_C2_FULL_FIELD_PUZZLE_ASSEMBLY.json"
HISTORICAL = A / "BHSM_completion_gate_v11_4.json"
PACKET = ROOT / (
    "docs/research_packets/2026-08-03/"
    "BHSM_FINAL_PARENT_ACTION_LEPTON_MASS_COMPLETION_2026-08-03.md"
)
TARGET = A / "action_extension/BHSM_AE31_C2_INTRINSIC_M4_LEPTON_ACTION.json"
INPUTS = (
    TRANSPORT,
    HS,
    PUZZLE,
    HISTORICAL,
    PACKET,
    ROOT / "src/bhsm/interface/ae31_c2_intrinsic_m4_lepton_action.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    transport, hs, puzzle, historical = map(_load, INPUTS[:4])
    packet_text = PACKET.read_text(encoding="utf-8")
    composition = action_composition_contract()
    yukawa = charged_lepton_yukawa_operator()
    saddle = conditional_higgs_saddle()
    mass = conditional_tree_mass_operator()
    pole_gate = first_variation_and_pole_gate()
    local_poles = local_tangent_frame_poles()
    boundary = claim_boundary()
    expected = historical["charged_lepton_action"][
        "candidate_mass_eigenvalues_GeV"
    ]
    values = mass["eigenvalues_GeV_heavy_middle_light"]
    validation = {
        "predecessor_internal_operator_attached": transport["claim_boundary"][
            "frozen_internal_Hopf_response_operator_attached_to_current_C2"
        ],
        "historical_action_formula_source_present": (
            "S_{4,\\ell H}^{\\rm BH}" in packet_text
            and "\\mathbb Y_\\ell^{\\rm BH}" in packet_text
        ),
        "composition_adds_no_independent_Ye_or_mass_term": (
            not composition["independent_Y_e_retained"]
            and not composition["separate_post_EWSB_mass_term_added"]
        ),
        "yukawa_is_positive_noncentral_and_no_fit": (
            yukawa["positive_definite"]
            and yukawa["family_noncentral"]
            and not yukawa["measured_lepton_mass_used"]
        ),
        "conditional_saddle_reproduces_historical_vBH": math.isclose(
            saddle["v_BH_GeV"], 246.16986520825228, rel_tol=0.0, abs_tol=3.0e-13
        ),
        "tree_mass_triplet_reproduces_historical_action_result": all(
            math.isclose(value, expected[key], rel_tol=0.0, abs_tol=3.0e-15)
            for value, key in zip(values, ("tau_slot", "mu_slot", "e_slot"))
        ),
        "historical_triplet_not_used_as_input_to_operator": (
            not mass["measured_lepton_mass_used"]
        ),
        "predecessor_HS_and_current_full_field_gates_were_open": (
            not hs["claim_boundary"]["current_C2_dynamical_HS_kernel_derived"]
            and not puzzle["CURRENT_FULL_FIELD_ACTION_COMPLETE"]
        ),
        "same_C2_first_order_pole_join_remains_explicit": (
            not pole_gate["same_current_C2_first_order_LR_block_assembled"]
            and not pole_gate["simple_pole_residues_evaluated"]
        ),
        "local_enclosure_tree_poles_are_distinct_simple_and_unfitted": (
            local_poles["three_distinct_positive_local_mass_shells"]
            and local_poles["all_energy_poles_simple"]
            and not local_poles["independent_wavefunction_residue_fitted"]
        ),
        "local_poles_do_not_overclaim_global_propagator": (
            not local_poles["global_time_translation_invariance_claimed"]
            and not local_poles["global_current_C2_Green_function_derived"]
        ),
        "no_up_down_or_muon_overclaim": (
            not boundary["up_down_action_prefactors_derived"]
            and not boundary["muon_magnetic_moment_derived"]
        ),
    }
    return {
        "artifact": "BHSM_AE31_C2_INTRINSIC_M4_LEPTON_ACTION",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "action_composition_contract": composition,
        "charged_lepton_yukawa_operator": yukawa,
        "conditional_higgs_saddle": saddle,
        "conditional_tree_mass_operator": mass,
        "first_variation_and_pole_gate": pole_gate,
        "local_tangent_frame_poles": local_poles,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE3.1 intrinsic M4 lepton action transport failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
