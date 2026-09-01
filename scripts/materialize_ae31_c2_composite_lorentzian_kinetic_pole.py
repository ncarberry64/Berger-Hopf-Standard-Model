"""Materialize the current-C2 composite Lorentzian kinetic pole."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_composite_lorentzian_kinetic_pole import (
    ACTION_VERSION,
    CLASSIFICATION,
    chiral_bubble_principal_part,
    clifford_trace_witness,
    claim_boundary,
    combined_composite_hessian_structure,
    current_c2_lorentzian_principal_symbol,
    exact_remaining_owner,
    historical_mass_derivative_adjudication,
)


A = ROOT / "artifacts/action_extension"
TARGET = A / "BHSM_AE31_C2_COMPOSITE_LORENTZIAN_KINETIC_POLE.json"
INPUTS = (
    A / "BHSM_AE31_C2_GAUGE_COMPOSITE_HS_ACTION.json",
    A / "BHSM_AE31_C2_LR_SUSCEPTIBILITY_FACTORIZATION.json",
    A / "BHSM_AE31_C2_LEPTON_COMPOSITE_MIXING_STRUCTURE.json",
    ROOT / "artifacts/BHSM_aether_hs_channel_normalization_v16_02.json",
    ROOT / "artifacts/BHSM_aether_nonlinear_cartan_gap_branch_v15_77.json",
    ROOT / "src/bhsm/interface/ae31_c2_composite_lorentzian_kinetic_pole.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    auxiliary, susceptibility, mixing, historical_trace, old_gap = map(
        _load, INPUTS[:5]
    )
    bubble = chiral_bubble_principal_part()
    clifford = clifford_trace_witness(
        q=[0.7, -1.1, 0.3, 0.9], p=[0.2, 0.4, -0.5, 1.3]
    )
    symbol = current_c2_lorentzian_principal_symbol(
        omega=0.25, spatial_eigenvalue=0.75, epsilon_uv=1.0
    )
    hessian = combined_composite_hessian_structure()
    adjudication = historical_mass_derivative_adjudication()
    owner = exact_remaining_owner()
    boundary = claim_boundary()
    validation = {
        "same_action_unit_vertices_reused": (
            auxiliary["claim_boundary"]["CURRENT_C2_GAUGE_COMPOSITE_UNIT_LR_VERTICES_DERIVED"]
            and mixing["claim_boundary"]["CURRENT_C2_CHARGED_LEPTON_GAUGE_HS_CHANNEL_DERIVED"]
        ),
        "continuous_frequency_Lorentzian_pole_derived": (
            symbol["frequency_domain"] == "CONTINUOUS_REAL_OMEGA__NOT_PERIODIC_CYCLE_MODE"
            and symbol["same_temporal_and_spatial_residue_per_channel"]
            and bubble["one_pair_pole_coefficient_without_epsilon"] > 0.0
            and clifford["residual"] < 1.0e-13
            and clifford["Euclidean_Clifford_residual"] < 1.0e-13
        ),
        "historical_pairing_trace_only_reused": (
            historical_trace["HS_channel_normalization"]["pairing_multiplicity_matrix"]
            == "D=diag(9,9,3,3)"
            and symbol["pairing_multiplicities"] == [9, 9, 3]
            and not adjudication["historical_numeric_Z_H_promoted_to_current_C2_kinetic_residue"]
        ),
        "mass_and_momentum_derivatives_separated": (
            old_gap["effective_potential"]["composite_residue"]
            == "Z_H=-partial_Chi_LR/partial_(m^2)>0"
            and not adjudication["same_functional_derivative"]
        ),
        "pole_does_not_select_broken_direction": (
            susceptibility["claim_boundary"]["CURRENT_C2_LR_HADAMARD_UV_POLE_FACTOR_DERIVED"]
            and hessian["up_down_derivative_pole_degenerate"]
            and not hessian["physical_broken_eigenvector_selected"]
        ),
        "no_finite_gap_Yukawa_or_mass_overclaim": (
            not boundary["CURRENT_C2_FINITE_COMPOSITE_KINETIC_RESIDUE_DERIVED"]
            and not boundary["CURRENT_C2_COMPOSITE_GAP_DERIVED"]
            and not boundary["CURRENT_C2_CANONICAL_YUKAWA_RESIDUES_DERIVED"]
            and not boundary["MEASURED_MASS_USED"]
            and not owner["cutoff_fitted_residue_or_old_EC_number_allowed"]
        ),
    }
    return {
        "artifact": "BHSM_AE31_C2_COMPOSITE_LORENTZIAN_KINETIC_POLE",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "chiral_bubble_principal_part": bubble,
        "Clifford_trace_witness": clifford,
        "current_C2_Lorentzian_principal_symbol_example": symbol,
        "combined_composite_Hessian_structure": hessian,
        "historical_mass_derivative_adjudication": adjudication,
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
        raise SystemExit("AE3.1 current-C2 composite Lorentzian kinetic pole failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
