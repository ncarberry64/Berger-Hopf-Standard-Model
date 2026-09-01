"""Materialize the AE3.1 current-C2 fermion Hadamard-state theorem."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_fermion_hadamard_state_class import (
    ACTION_VERSION,
    CLASSIFICATION,
    cauchy_covariance_selection_contract,
    claim_boundary,
    hadamard_class_existence_theorem,
    retained_state_selector_audit,
)


A = ROOT / "artifacts"
GREEN = A / "action_extension/BHSM_AE31_C2_CHIRAL_GREEN_DOMAIN.json"
RESET = A / "action_extension/BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json"
TIME = A / (
    "intrinsic_state_selection/BHSM_N12_FORWARD_TIME_DOMAIN_ORIENTATION_AUDIT.json"
)
TARGET = A / "action_extension/BHSM_AE31_C2_FERMION_HADAMARD_STATE_CLASS.json"
INPUTS = (
    GREEN,
    RESET,
    TIME,
    ROOT / "src/bhsm/interface/ae31_c2_fermion_hadamard_state_class.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    normalized = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(normalized).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    green, reset, time = map(_load, INPUTS[:3])
    existence = hadamard_class_existence_theorem()
    covariance = cauchy_covariance_selection_contract()
    audit = retained_state_selector_audit()
    boundary = claim_boundary()
    validation = {
        "same_AE31_chiral_operator": (
            green["action_version"] == existence["action_version"] == ACTION_VERSION
            and green["chiral_operator_assembly"][
                "same_current_C2_first_order_LR_block_assembled"
            ]
        ),
        "global_hyperbolicity_and_causal_Green_theorem_inherited": (
            green["green_operator_feasibility"][
                "finite_core_global_hyperbolicity_derived_familywise"
            ]
            and green["green_operator_feasibility"][
                "advanced_retarded_Green_operator_existence_derived"
            ]
            and existence["globally_hyperbolic_member_by_member"]
        ),
        "AE2_reset_is_domain_not_state_selector": (
            reset["finite_certificate"]["transmission_graph"]["maximal_isotropic"]
            and audit["rows"][0]["candidate"] == "AE2_RESET_LIFT"
            and not audit["rows"][0]["selects_state"]
        ),
        "time_orientation_is_causal_not_positive_frequency_selection": (
            time["admissible_clock_domain"]["number_of_physical_time_orientations"]
            == 1
            and audit["rows"][1]["candidate"]
            == "CURRENT_C2_TIME_ORIENTATION"
            and not audit["rows"][1]["selects_state"]
        ),
        "Hadamard_class_exists_without_unique_state_promotion": (
            existence["quasifree_Hadamard_state_class_nonempty_member_by_member"]
            and existence["state_dependent_Feynman_two_point_distribution_exists"]
            and not existence["one_Hadamard_state_selected"]
        ),
        "smooth_state_dependence_not_hidden": (
            existence["any_two_Hadamard_two_point_functions_differ_by"]
            == "A_SMOOTH_BISOLUTION_OF_THE_DIRAC_EQUATION"
            and not existence["smooth_state_dependent_part_is_fixed_by_action"]
        ),
        "no_retained_shortcut_selects_covariance": (
            audit["candidate_count"] == 9
            and audit["selected_candidate_count"] == 0
            and not audit["retained_action_selects_unique_Feynman_state"]
        ),
        "no_dressed_pole_or_muon_g_minus_2_overclaim": (
            not boundary["CURRENT_C2_DRESSED_CHARGED_LEPTON_POLES_DERIVED"]
            and not boundary["CURRENT_C2_PHYSICAL_MUON_POLE_DERIVED"]
            and not boundary["MUON_MAGNETIC_MOMENT_DERIVED"]
        ),
        "no_new_state_parameter_or_spectrum_rebuild": (
            not boundary["new_state_parameter_inserted"]
            and not boundary["particle_spectrum_rebuilt"]
            and not covariance[
                "new_continuous_temperature_or_Bogoliubov_coefficient_inserted"
            ]
        ),
    }
    return {
        "artifact": "BHSM_AE31_C2_FERMION_HADAMARD_STATE_CLASS",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "hadamard_class_existence_theorem": existence,
        "cauchy_covariance_selection_contract": covariance,
        "retained_state_selector_audit": audit,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE3.1 fermion Hadamard-state theorem failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
