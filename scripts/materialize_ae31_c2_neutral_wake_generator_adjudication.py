"""Materialize the neutral stiffness-versus-wake-generator adjudication."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_neutral_wake_generator_adjudication import (
    ACTION_VERSION,
    CLASSIFICATION,
    claim_boundary,
    historical_first_order_owner_alignment,
    positive_stiffness_zero_reference_theorem,
    traceless_wake_generator,
    unitary_wake_evolution,
)


A = ROOT / "artifacts/action_extension"
TARGET = A / "BHSM_AE31_C2_NEUTRAL_WAKE_GENERATOR_ADJUDICATION.json"
INPUTS = (
    A / "BHSM_AE31_C2_NEUTRAL_SEED_IDENTIFICATION_BRIDGE.json",
    ROOT / "artifacts/BHSM_pair_wake_hybrid_action_v14_56.json",
    ROOT / "artifacts/BHSM_three_response_two_gap_minimum_v14_56.json",
    ROOT / "artifacts/BHSM_dtn_heat_kernel_wake_insertion_contract_v14_57.json",
    ROOT / "src/bhsm/interface/ae31_c2_neutral_wake_generator_adjudication.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    bridge, action, two_gap, insertion = map(_load, INPUTS[:4])
    stiffness = positive_stiffness_zero_reference_theorem()
    generator = traceless_wake_generator()
    evolution = unitary_wake_evolution(0.713)
    owner = historical_first_order_owner_alignment()
    boundary = claim_boundary()
    validation = {
        "current_mode_bridge_reused": bridge["validation_passed"],
        "v14_56_first_order_action_reused": "i z^dagger D_tau z" in action[
            "closed_coherent_action"
        ],
        "v14_56_two_gap_state_reused": two_gap["minimum_wake_state"][
            "independent_relative_phase_dimension"
        ] == 2,
        "v14_57_owner_formula_reused": "traceless_hermitian_part" in insertion[
            "formulae"
        ]["wake_generator"],
        "positive_stiffness_no_go_exact": not stiffness[
            "historical_seed_is_positive_stiffness"
        ],
        "traceless_two_gap_generator": generator[
            "two_nonzero_eigenvalue_gaps"
        ],
        "unitary_evolution_witness": evolution["unitary"],
        "physical_owner_not_overclaimed": not owner[
            "K_nu_equals_action_evaluated_H_wake_on_current_C2"
        ],
        "diagnostic_fixture_not_substituted": not boundary[
            "historical_diagnostic_fixture_substituted"
        ],
    }
    return {
        "artifact": "BHSM_AE31_C2_NEUTRAL_WAKE_GENERATOR_ADJUDICATION",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "positive_stiffness_zero_reference_theorem": stiffness,
        "traceless_wake_generator": generator,
        "unitary_wake_evolution_witness": evolution,
        "historical_first_order_owner_alignment": owner,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("neutral wake-generator adjudication failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
