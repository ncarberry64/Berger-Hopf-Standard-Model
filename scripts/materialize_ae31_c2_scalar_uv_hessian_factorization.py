"""Materialize the current-C2 full scalar UV Hessian factorization."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_scalar_uv_hessian_factorization import (
    ACTION_VERSION,
    CLASSIFICATION,
    claim_boundary,
    exact_remaining_owner,
    full_zero_momentum_hadamard_pole,
    renormalized_generalized_eigenproblem,
    uv_shape_proportionality_theorem,
)


A = ROOT / "artifacts/action_extension"
TARGET = A / "BHSM_AE31_C2_SCALAR_UV_HESSIAN_FACTORIZATION.json"
INPUTS = (
    A / "BHSM_AE31_C2_LR_SUSCEPTIBILITY_FACTORIZATION.json",
    A / "BHSM_AE31_C2_LEPTON_COMPOSITE_MIXING_STRUCTURE.json",
    A / "BHSM_AE31_C2_FULL_SCALAR_DERIVATIVE_POLE.json",
    ROOT / "src/bhsm/interface/ae31_c2_scalar_uv_hessian_factorization.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    susceptibility, mixing, derivative = map(_load, INPUTS[:3])
    mass_pole = full_zero_momentum_hadamard_pole(radius=1.0)
    theorem = uv_shape_proportionality_theorem()
    finite = renormalized_generalized_eigenproblem()
    owner = exact_remaining_owner()
    boundary = claim_boundary()
    validation = {
        "existing_masslike_and_mixed_poles_reused": (
            susceptibility["claim_boundary"]["CURRENT_C2_LR_HADAMARD_UV_POLE_FACTOR_DERIVED"]
            and mixing["claim_boundary"]["CURRENT_C2_LEPTON_COMPOSITE_HADAMARD_POLE_DIRECTION_DERIVED"]
            and mass_pole["local_and_state_independent"]
        ),
        "complete_derivative_Gram_reused": (
            derivative["claim_boundary"]["CURRENT_C2_FULL_FOUR_FIELD_DERIVATIVE_PRINCIPAL_POLE_DERIVED"]
            and derivative["claim_boundary"]["CURRENT_C2_FULL_SCALAR_UV_KINETIC_FORM_POSITIVE_DEFINITE"]
        ),
        "UV_shapes_factor_exactly": (
            theorem["normalized_shape_residual"] < 1.0e-15
            and theorem["generalized_operator_identity_residual"] < 1.0e-12
            and theorem["UV_singular_generalized_eigenspace_dimension"] == 4
        ),
        "UV_poles_do_not_select_direction": (
            not theorem["UV_poles_select_scalar_channel_direction"]
            and theorem["family_noncentrality_gives_full_rank_but_not_direction_selection"]
        ),
        "finite_problem_not_fabricated": (
            not finite["physical_generalized_eigenproblem_evaluable"]
            and not finite["minimal_subtraction_or_cutoff_chosen_as_physics"]
            and not boundary["CURRENT_C2_PHYSICAL_SINGLE_HIGGS_DIRECTION_SELECTED"]
            and not boundary["MEASURED_MASS_USED"]
            and not owner["fitted_finite_matrix_allowed"]
        ),
    }
    return {
        "artifact": "BHSM_AE31_C2_SCALAR_UV_HESSIAN_FACTORIZATION",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "full_zero_momentum_Hadamard_pole_example_R4_1": mass_pole,
        "UV_shape_proportionality_theorem": theorem,
        "renormalized_generalized_eigenproblem": finite,
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
        raise SystemExit("AE3.1 current-C2 scalar UV Hessian factorization failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
