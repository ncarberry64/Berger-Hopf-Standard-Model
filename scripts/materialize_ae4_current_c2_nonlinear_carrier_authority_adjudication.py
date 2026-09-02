"""Materialize the current AE4 nonlinear carrier-authority adjudication."""

from __future__ import annotations

import hashlib
import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae4_current_c2_nonlinear_carrier_authority_adjudication import (
    ACTION_VERSION,
    CLASSIFICATION,
    claim_boundary,
    nonlinear_carrier_authority_contract,
)


A = ROOT / "artifacts/action_extension"
F = ROOT / "artifacts/flagship_integration"
TRANSFER = F / "BHSM_N12_GATE7_AFFINE_72D_NONLINEAR_TRANSFER_AUDIT.json"
OUTWARD = F / "BHSM_N12_GATE7_ACCEPTED_REPLAY_CENTER_OUTWARD_74D_CONTRACTION.json"
GAUGE = A / "BHSM_AE4_CURRENT_C2_AFFINE72_GAUGE_CALDERON_FIRST_JET.json"
PARTICLE = A / "BHSM_AE4_CURRENT_C2_AFFINE72_PARTICLE_FIBER_CALDERON.json"
TARGET = A / "BHSM_AE4_CURRENT_C2_NONLINEAR_CARRIER_AUTHORITY_ADJUDICATION.json"
INPUTS = (
    TRANSFER,
    OUTWARD,
    GAUGE,
    PARTICLE,
    ROOT / "src/bhsm/interface/ae4_current_c2_nonlinear_carrier_authority_adjudication.py",
    ROOT / "scripts/materialize_ae4_current_c2_nonlinear_carrier_authority_adjudication.py",
    ROOT / "theory/ae4_current_c2_nonlinear_carrier_authority_adjudication.md",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


@lru_cache(maxsize=1)
def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    transfer, outward, gauge, particle = (_load(path) for path in INPUTS[:4])
    if not all(
        row.get("validation_passed") is True
        for row in (transfer, outward, gauge, particle)
    ):
        raise RuntimeError("validated transfer, outward, and AE4 carrier inputs required")

    transfer_allowed = transfer["adjudication"][
        "affine_jet_may_be_used_as_complete_operator_authority"
    ]
    decision = outward["decision"]
    result = nonlinear_carrier_authority_contract(
        affine_transfer_allowed=transfer_allowed,
        same_center_contraction_obstructed=decision[
            "current_same_center_contraction_theorem_obstructed"
        ],
        root_nonexistence_claim=decision["root_nonexistence_claim"],
        physical_instability_claim=decision[
            "physical_spacetime_instability_claim"
        ],
        another_center_or_trajectory_authorized=decision[
            "another_center_or_trajectory_authorized"
        ],
    )
    operands = outward["outward_operands"]
    boundary = claim_boundary()
    validation = {
        "same_center_outward_calculation_already_complete": (
            outward["owner"]
            == "SAME_CENTER_GATE7_Z2_PHYSICAL_LOCALIZATION_AND_ADJUDICATION"
            and outward["validation_passed"]
        ),
        "necessary_scalar_discriminant_strictly_negative": (
            operands[
                "necessary_discriminant_upper_1_minus_4_Ylower_Z2lower"
            ]
            < 0.0
            and outward["validation"][
                "necessary_quadratic_discriminant_strictly_negative"
            ]
        ),
        "affine_transfer_independently_rejected": transfer_allowed is False,
        "gauge_candidate_remains_non_authoritative": (
            gauge["validation_passed"]
            and not gauge["carrier"]["nonlinear_exact_family_authority"]
        ),
        "particle_candidate_remains_non_authoritative": (
            particle["validation_passed"]
            and not particle["carrier"]["nonlinear_exact_family_authority"]
            and particle["scientific_result"]["attached_existing_fiber_count"]
            == 9
        ),
        "no_physical_instability_or_root_nonexistence_overclaim": (
            not result["physical_spacetime_instability_inferred"]
            and not result["root_nonexistence_inferred"]
            and not boundary["G7_ROOT_NONEXISTENCE_DERIVED"]
            and not boundary["G7_PHYSICAL_SPACETIME_INSTABILITY_DERIVED"]
        ),
        "no_new_numerical_campaign_authorized": (
            not result[
                "accepted_replay_center_or_trajectory_may_be_reselected"
            ]
            and not boundary["NEW_CENTER_OR_TRAJECTORY_AUTHORIZED"]
        ),
        "scalar_route_not_left_as_open_next_calculation": boundary[
            "G7_SINGLE_RADIUS_74D_CONTRACTION_ROUTE_OBSTRUCTED"
        ],
    }
    return {
        "artifact": "BHSM_AE4_CURRENT_C2_NONLINEAR_CARRIER_AUTHORITY_ADJUDICATION",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "recovered_same_center_operands": {
            "Y_lower": operands["Y_lower"],
            "Z1_upper": operands["Z1_upper"],
            "Z2_required_lower_from_center_direction": operands[
                "Z2_required_lower_from_center_direction"
            ],
            "necessary_discriminant_upper": operands[
                "necessary_discriminant_upper_1_minus_4_Ylower_Z2lower"
            ],
        },
        "authority_adjudication": result,
        "claim_boundary": boundary,
        "exact_next_calculation": result["next_proof_object"],
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("nonlinear carrier-authority adjudication failed")
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
