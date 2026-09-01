"""Materialize the full current-C2 scalar derivative pole matrix."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_full_scalar_derivative_pole import (
    ACTION_VERSION,
    CLASSIFICATION,
    claim_boundary,
    derivative_eigenmode_boundary,
    exact_remaining_owner,
    family_noncentral_rank_theorem,
    full_lorentzian_derivative_symbol,
    scalar_vertex_gram_matrix,
)


A = ROOT / "artifacts/action_extension"
TARGET = A / "BHSM_AE31_C2_FULL_SCALAR_DERIVATIVE_POLE.json"
INPUTS = (
    A / "BHSM_AE31_C2_INTRINSIC_M4_LEPTON_ACTION.json",
    A / "BHSM_AE31_C2_LEPTON_COMPOSITE_MIXING_STRUCTURE.json",
    A / "BHSM_AE31_C2_COMPOSITE_LORENTZIAN_KINETIC_POLE.json",
    ROOT / "src/bhsm/interface/ae31_c2_full_scalar_derivative_pole.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    intrinsic, mixing, composite = map(_load, INPUTS[:3])
    gram = scalar_vertex_gram_matrix()
    symbol = full_lorentzian_derivative_symbol(
        omega=0.25, spatial_eigenvalue=0.75, epsilon_uv=1.0
    )
    rank = family_noncentral_rank_theorem()
    modes = derivative_eigenmode_boundary()
    owner = exact_remaining_owner()
    boundary = claim_boundary()
    validation = {
        "intrinsic_and_auxiliary_vertices_reused": (
            intrinsic["claim_boundary"]["charged_lepton_M4_semigroup_coupling_action_owned_in_successor"]
            and mixing["claim_boundary"]["CURRENT_C2_INTRINSIC_LEPTON_COMPOSITE_VERTEX_JET_DERIVED"]
        ),
        "one_pair_Lorentzian_pole_reused": (
            composite["claim_boundary"]["CURRENT_C2_COMPOSITE_LORENTZIAN_PRINCIPAL_POLE_DERIVED"]
            and symbol["same_temporal_spatial_matrix"]
        ),
        "family_noncentrality_makes_lepton_block_rank_two": (
            gram["Y_l_family_noncentral"]
            and rank["strictly_positive"]
            and rank["current_family_noncentral_block_rank"] == 2
            and gram["variance_identity_residual"] < 1.0e-18
        ),
        "full_UV_kinetic_Gram_form_positive": (
            gram["positive_definite"]
            and gram["Gram_rank"] == 4
            and boundary["CURRENT_C2_FULL_SCALAR_UV_KINETIC_FORM_POSITIVE_DEFINITE"]
        ),
        "UV_modes_not_promoted_to_physical_Higgs": (
            modes["UV_derivative_eigendirections_action_derived"]
            and not modes["finite_canonical_fields_derived"]
            and not modes["physical_lightest_or_broken_scalar_selected"]
        ),
        "no_finite_Higgs_Yukawa_or_mass_overclaim": (
            not boundary["CURRENT_C2_FINITE_FULL_SCALAR_KINETIC_MATRIX_DERIVED"]
            and not boundary["CURRENT_C2_RENORMALIZED_ZERO_MOMENTUM_SCALAR_HESSIAN_DERIVED"]
            and not boundary["CURRENT_C2_PHYSICAL_SINGLE_HIGGS_DIRECTION_SELECTED"]
            and not boundary["CURRENT_C2_CANONICAL_YUKAWA_RESIDUES_DERIVED"]
            and not boundary["MEASURED_MASS_USED"]
            and not owner["old_EC_residue_or_fitted_scalar_normalization_allowed"]
        ),
    }
    return {
        "artifact": "BHSM_AE31_C2_FULL_SCALAR_DERIVATIVE_POLE",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "scalar_vertex_Gram_matrix": gram,
        "full_Lorentzian_derivative_symbol_example": symbol,
        "family_noncentral_rank_theorem": rank,
        "derivative_eigenmode_boundary": modes,
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
        raise SystemExit("AE3.1 current-C2 full scalar derivative pole failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
