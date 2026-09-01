"""Materialize the current-C2 color-singlet residual-response bridge."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_color_singlet_residual_response_bridge import (
    ACTION_VERSION,
    CLASSIFICATION,
    baryon_response,
    claim_boundary,
    enclosure_response_contract,
    meson_response,
)


A = ROOT / "artifacts/action_extension"
TARGET = A / "BHSM_AE31_C2_COLOR_SINGLET_RESIDUAL_RESPONSE_BRIDGE.json"
INPUTS = (
    ROOT / "artifacts/BHSM_Wilson_singlet_operator_source_v14_29.json",
    ROOT / "artifacts/BHSM_aether_sm_gauge_color_completion_v15_58.json",
    ROOT / "artifacts/BHSM_aether_physical_inverse_closure_v16_36.json",
    ROOT / "src/bhsm/interface/ae31_c2_color_singlet_residual_response_bridge.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    wilson, closed_color, inverse = map(_load, INPUTS[:3])
    meson = meson_response((1.0, 0.0))
    baryon = baryon_response((1.0, 0.0, 0.0))
    contract = enclosure_response_contract()
    boundary = claim_boundary()
    color_row = next(
        row
        for row in inverse["inverse_observation_ledger"]
        if row["OBSERVED_FACT"] == "isolated_colored_asymptotic_matter_is_absent"
    )
    validation = {
        "historical_Wilson_singlet_reused": wilson["validation_passed"],
        "closed_child_Gauss_singlet_reused": closed_color["validation"][
            "color_singlet_constraint_derived"
        ],
        "later_global_confinement_boundary_preserved": "OPEN" in color_row["CURRENT_STATUS"],
        "meson_numerator_exact": bool(meson["formula_residual"] < 1.0e-12),
        "baryon_numerator_exact": bool(baryon["formula_residual"] < 1.0e-12),
        "linear_color_charge_zero": meson["linear_color_charge_zero"] and baryon[
            "linear_color_charge_zero"
        ],
        "finite_size_transition_nonzero": meson["transition_channel_nonzero"] and baryon[
            "transition_channel_nonzero"
        ],
        "wilson_not_relabelled_as_action": not contract["wilson_source_is_action_term"],
        "resolvent_and_force_not_overclaimed": (
            not boundary["CURRENT_C2_RETURNED_HADRON_COLORED_RESOLVENT_DERIVED"]
            and not boundary["CURRENT_C2_NONZERO_PHYSICAL_RESIDUAL_NUCLEAR_FORCE_DERIVED"]
        ),
    }
    return {
        "artifact": "BHSM_AE31_C2_COLOR_SINGLET_RESIDUAL_RESPONSE_BRIDGE",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "meson_reference_probe": meson,
        "baryon_reference_probe": baryon,
        "enclosure_response_contract": contract,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("color-singlet residual-response bridge failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
