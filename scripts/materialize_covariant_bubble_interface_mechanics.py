"""Materialize the covariant BHSM bubble/interface mechanics authority."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.covariant_bubble_interface_mechanics import build_payload  # noqa: E402


A = ROOT / "artifacts/action_extension"
OWNER = A / "BHSM_OWNER_AUTHORIZED_ENCAPSULATION_INTERFACE_ACTION_CLASSIFICATION.json"
FSC = A / "BHSM_FSC_ENCAPSULATION_CONSTITUTIVE_ADJUDICATION.json"
ENVIRONMENT = A / "BHSM_ENVIRONMENTAL_RESET_COMPATIBILITY_CLASSIFICATION.json"
MOVING_RESET = A / "BHSM_FULL_FIELD_MOVING_RESET_GRAPH_DECISION.json"
RESULT = A / "BHSM_COVARIANT_BUBBLE_INTERFACE_MECHANICS.json"
THEORY = ROOT / "theory/bhsm_covariant_bubble_interface_mechanics.md"
MODULE = ROOT / "src/bhsm/interface/covariant_bubble_interface_mechanics.py"
THIS_SCRIPT = Path(__file__).resolve()


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def materialize() -> dict[str, object]:
    payload = build_payload(
        _load(OWNER), _load(FSC), _load(ENVIRONMENT), _load(MOVING_RESET)
    )
    inputs = (OWNER, FSC, ENVIRONMENT, MOVING_RESET, THEORY, MODULE, THIS_SCRIPT)
    payload["inputs"] = {_relative(path): _sha(path) for path in inputs}
    validation = {
        "prior_IF5_and_R4_boundaries_retained_as_inputs": (
            payload["recovered_authorities"]["prior_interface_class"] == "ORD1/IF5"
            and payload["recovered_authorities"]["prior_reset_class"] == "R4"
        ),
        "minimal_area_member_selected_without_fitted_parameter": (
            payload["interface_action"]["constitutive_class_after_owner_mechanics"]
            == "FSC-IF1_MINIMAL_AREA_MEMBER"
            and payload["interface_stiffness"]["fitted_coefficient"] is None
        ),
        "ordinary_mechanics_excluded_from_C_A": "no pressure" in payload["domain"]["pregeometry"],
        "FSC_is_symbolic_not_observed_alpha": (
            payload["FSC"]["authority"] == "FSC-P1"
            and payload["FSC"]["observed_alpha_EM_used"] is False
        ),
        "stress_and_motion_follow_from_one_action": (
            payload["variation"]["surface_stress"] == "S_Sigma^(ab)=-gamma_s h^(ab)"
            and payload["moving_interface"]["newtonian_fluid_equation_imported"] is False
        ),
        "carrier_and_reset_not_overpromoted": (
            payload["carrier_reset"]["F_B_selected_now"] is False
            and payload["claim_boundary"]["FULL_FIELD_RESET_DOMAIN_INSTANTIATED"] is False
        ),
        "Track1_not_read_or_promoted": payload["N12"]["Gate7_result_imported"] is False,
        "no_new_N12_rank": payload["N12"]["new_independent_rank"] == 0,
        "frozen_predictions_changed": False,
        "FULL_BHSM_COMPLETE": False,
    }
    payload["validation"] = validation
    payload["validation_passed"] = all(
        value for key, value in validation.items()
        if key not in {"frozen_predictions_changed", "FULL_BHSM_COMPLETE"}
    ) and not validation["frozen_predictions_changed"] and not validation[
        "FULL_BHSM_COMPLETE"
    ]
    return payload


def main() -> None:
    payload = materialize()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "gamma_class": payload["interface_stiffness"]["classification"],
        "rho_class": payload["formation_number"]["classification"],
        "carrier_class": payload["carrier_reset"]["carrier_class"],
        "validation_passed": payload["validation_passed"],
        "FULL_BHSM_COMPLETE": payload["FULL_BHSM_COMPLETE"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
