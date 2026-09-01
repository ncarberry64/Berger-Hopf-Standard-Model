"""Materialize the current-C2 lepton/composite mixing structure."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_lepton_composite_mixing_structure import (
    ACTION_VERSION,
    CLASSIFICATION,
    claim_boundary,
    exact_remaining_owner,
    nonzero_gauge_hs_channel_extension,
    one_loop_mixing_factorization,
    shared_charged_lepton_vertex_jet,
    species_block_selection_theorem,
)


A = ROOT / "artifacts/action_extension"
TARGET = A / "BHSM_AE31_C2_LEPTON_COMPOSITE_MIXING_STRUCTURE.json"
INPUTS = (
    A / "BHSM_AE31_C2_INTRINSIC_M4_LEPTON_ACTION.json",
    A / "BHSM_AE31_C2_GAUGE_COMPOSITE_HS_ACTION.json",
    A / "BHSM_AE31_C2_LR_SUSCEPTIBILITY_FACTORIZATION.json",
    ROOT / "artifacts/BHSM_aether_full_gauge_dtn_lr_kernel_v15_66.json",
    ROOT / "src/bhsm/interface/ae31_c2_lepton_composite_mixing_structure.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    intrinsic, auxiliary, susceptibility, historical = map(_load, INPUTS[:4])
    channels = nonzero_gauge_hs_channel_extension()
    jet = shared_charged_lepton_vertex_jet()
    mixing = one_loop_mixing_factorization()
    species = species_block_selection_theorem()
    owner = exact_remaining_owner()
    boundary = claim_boundary()
    validation = {
        "intrinsic_lepton_action_reused": (
            intrinsic["claim_boundary"]["charged_lepton_M4_semigroup_coupling_action_owned_in_successor"]
            and mixing["Y_l_family_noncentral"]
        ),
        "charged_lepton_gauge_channel_is_nonzero": (
            historical["left_right_group_factors"]["pre_Fierz_attraction_weights"]["charged_lepton"] == "3/10"
            and channels["bare_inverse_coefficients_over_G_C2"]["charged_lepton"] == "5/3"
            and not channels["neutrino_zero_kernel_HS_inverse_defined"]
        ),
        "shared_vertex_and_contact_jet_close": (
            auxiliary["claim_boundary"]["CURRENT_C2_GAUGE_COMPOSITE_UNIT_LR_VERTICES_DERIVED"]
            and jet["intrinsic_grading_residual"] == 0.0
            and jet["auxiliary_grading_residual"] == 0.0
            and jet["squared_pencil_cross_contact_residual"] < 1.0e-14
        ),
        "universal_mixing_direction_not_finite_value": (
            susceptibility["claim_boundary"]["CURRENT_C2_LR_HADAMARD_UV_POLE_FACTOR_DERIVED"]
            and mixing["universal_pole_family_direction_action_derived"]
            and not mixing["full_numeric_mixing_matrix_derived"]
        ),
        "one_loop_species_boundary_preserved": (
            species["direct_one_fermion_loop_intrinsic_quark_mixing_zero"]
            and species["all_orders_vector_gauge_mixing_zero_at_chirally_symmetric_quark_background"]
            and not species["nonperturbative_chirality_violating_topological_vertex_excluded"]
            and not owner["one_loop_zero_replaced_by_fitted_mixing"]
        ),
        "no_Higgs_Yukawa_or_mass_overclaim": (
            not boundary["CURRENT_C2_PHYSICAL_SINGLE_HIGGS_DIRECTION_SELECTED"]
            and not boundary["CURRENT_C2_CANONICAL_QUARK_YUKAWA_RESIDUES_DERIVED"]
            and not boundary["MEASURED_MASS_USED"]
            and not boundary["FULL_BHSM_COMPLETE"]
        ),
    }
    return {
        "artifact": "BHSM_AE31_C2_LEPTON_COMPOSITE_MIXING_STRUCTURE",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "nonzero_gauge_hs_channel_extension": channels,
        "shared_charged_lepton_vertex_jet": jet,
        "one_loop_mixing_factorization": mixing,
        "species_block_selection_theorem": species,
        "exact_remaining_owner": owner,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE3.1 lepton/composite mixing structure failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
