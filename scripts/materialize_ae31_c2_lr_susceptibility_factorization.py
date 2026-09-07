"""Materialize the current-C2 LR susceptibility factorization."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_lr_susceptibility_factorization import (
    ACTION_VERSION,
    CLASSIFICATION,
    claim_boundary,
    composite_hessian_decomposition,
    current_c2_slice_susceptibility,
    exact_remaining_owner,
    finite_state_remainder_witness,
    hadamard_pole_factorization,
)


A = ROOT / "artifacts/action_extension"
TARGET = A / "BHSM_AE31_C2_LR_SUSCEPTIBILITY_FACTORIZATION.json"
INPUTS = (
    ROOT / "artifacts/BHSM_aether_lr_susceptibility_zeta_v15_67.json",
    A / "BHSM_AE31_C2_FERMION_HADAMARD_STATE_CLASS.json",
    A / "BHSM_AE31_C2_FIXED_HISTORY_STATE_NONUNIQUENESS.json",
    A / "BHSM_AE31_C2_QUARK_CHANNEL_SELECTOR_DOMAIN.json",
    A / "BHSM_AE31_C2_QUARK_HIGGS_INCIDENCE_TRANSPORT.json",
    A / "BHSM_AE31_C2_QUARK_GAUGE_LR_CHANNEL_RAY.json",
    ROOT / "src/bhsm/interface/ae31_c2_lr_susceptibility_factorization.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    historical, hadamard, state, selector, incidence, gauge = map(_load, INPUTS[:6])
    slice_sum = current_c2_slice_susceptibility(8, 1.0)
    pole = hadamard_pole_factorization()
    hessian = composite_hessian_decomposition()
    remainder = finite_state_remainder_witness()
    owner = exact_remaining_owner()
    boundary = claim_boundary()
    validation = {
        "historical_spectral_sum_reused": (
            historical["claim_boundary"]["free_Weyl_LR_spectral_sum_derived"]
            and slice_sum["positive"]
            and not slice_sum["global_frequency_diagonalization_used"]
        ),
        "Hadamard_pole_is_universal_not_finite_state": (
            hadamard["claim_boundary"]["LOCAL_HADAMARD_SINGULARITY_CLASS_DERIVED"]
            and not hadamard["claim_boundary"]["CURRENT_C2_ACTION_SELECTED_HADAMARD_STATE_DERIVED"]
            and pole["pole_is_state_independent_within_Hadamard_class"]
            and not pole["finite_local_HdaggerH_subtraction_selected"]
        ),
        "equal_incidence_trace_gives_identity_pole": (
            incidence["quark_higgs_support_pencil"]["support_inner_product"] == 0.0
            and pole["normalized_channel_pole_is_identity"]
        ),
        "common_pole_cancels_only_from_traceless_channel": (
            gauge["claim_boundary"]["CURRENT_C2_QUARK_GAUGE_LR_RELATIVE_CHANNEL_RAY_DERIVED"]
            and not hessian["universal_pole_changes_relative_channel_direction"]
            and hessian["gauge_inverse_curvature_orders_up_below_down_for_positive_G_C2"]
        ),
        "finite_state_remainder_not_discarded": (
            state["claim_boundary"]["CURRENT_C2_FIXED_HISTORY_PURE_HADAMARD_STATE_NONUNIQUENESS_DERIVED"]
            and selector["claim_boundary"]["CURRENT_C2_QUANTUM_SELECTOR_STATE_DEPENDENCE_COUNTEREXAMPLE_DERIVED"]
            and remainder["finite_remainder_can_change_channel_eigenvectors"]
            and not remainder["universal_pole_factorization_selects_physical_direction"]
        ),
        "no_gap_Yukawa_or_mass_overclaim": (
            not boundary["CURRENT_C2_FULL_RENORMALIZED_LR_HESSIAN_DERIVED"]
            and not boundary["CURRENT_C2_COMPOSITE_GAP_DERIVED"]
            and not boundary["CURRENT_C2_UP_DOWN_YUKAWA_RESIDUES_DERIVED"]
            and not boundary["MEASURED_QUARK_MASS_USED"]
            and not owner["cutoff_or_fitted_subtraction_allowed"]
        ),
    }
    return {
        "artifact": "BHSM_AE31_C2_LR_SUSCEPTIBILITY_FACTORIZATION",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "current_c2_slice_susceptibility_example_R4_1": slice_sum,
        "hadamard_pole_factorization": pole,
        "composite_hessian_decomposition": hessian,
        "finite_state_remainder_witness": remainder,
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
        raise SystemExit("AE3.1 current-C2 LR susceptibility factorization failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
