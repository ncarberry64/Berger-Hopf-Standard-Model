"""Materialize the current-C2 r2/electron-capture selection rule."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_r2_electron_capture_selection_rule import (
    ACTION_VERSION,
    CLASSIFICATION,
    capture_vertex_and_hessian_gate,
    claim_boundary,
    electron_metric_incidence_contract,
    normalized_s3_rank2_witness,
    recovered_r2_provenance,
    scientific_decision,
)


A = ROOT / "artifacts/action_extension"
TARGET = A / "BHSM_AE31_C2_R2_ELECTRON_CAPTURE_SELECTION_RULE.json"
INPUTS = (
    ROOT / "artifacts/BHSM_differential_shear_softening_v14_83.json",
    ROOT / "artifacts/BHSM_stationary_full_preimage_transport_no_go_v14_85.json",
    A / "BHSM_AE31_C2_INTRINSIC_M4_LEPTON_ACTION.json",
    A / "BHSM_AE31_C2_COEXACT_SU2L_CHARGED_CURRENT.json",
    A / "BHSM_AE31_C2_OUTER_CALDERON_ACTION_NO_GO.json",
    ROOT / "artifacts/BHSM_aether_physical_inverse_closure_v16_36.json",
    ROOT / "src/bhsm/interface/ae31_c2_r2_electron_capture_selection_rule.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    old_shear, stationary, lepton, charged, outer, inverse = map(_load, INPUTS[:6])
    witness = normalized_s3_rank2_witness()
    provenance = recovered_r2_provenance()
    incidence = electron_metric_incidence_contract()
    capture = capture_vertex_and_hessian_gate()
    decision = scientific_decision()
    boundary = claim_boundary()
    validation = {
        "v14_83_sign_theorem_reused": old_shear["validation_passed"],
        "v14_85_stationary_zero_reused": stationary["validation_passed"],
        "current_lepton_action_reused": lepton["validation_passed"],
        "current_charged_current_reused": charged["validation_passed"],
        "outer_environment_no_go_preserved": outer["claim_boundary"][
            "CURRENT_AE31_RETAINED_ACTION_OUTER_CALDERON_COMPLETION_NO_GO_DERIVED"
        ],
        "proton_neutron_gate_reused": any(
            row["particle_or_sector"] == "proton_neutron_minimal_composite"
            for row in inverse["physical_requirement_matrix"]
        ),
        "rank2_diagonal_zero": witness["diagonal_Gaunt_000_to_2"] == 0.0,
        "rank2_mixing_nonzero": witness["rank0_to_rank2_mixing_allowed"],
        "stationary_transport_not_overridden": not provenance[
            "nonzero_physical_r2_transport_derived"
        ],
        "capture_not_overclaimed": (
            not capture["capture_Hessian_derived"]
            and not boundary["CURRENT_C2_PHYSICAL_ELECTRON_CAPTURE_AMPLITUDE_DERIVED"]
        ),
        "r2_not_relabelled_as_orbital": not decision[
            "r2_may_be_renamed_the_capture_orbital"
        ],
        "no_new_coefficient": not incidence["new_electron_shear_coefficient_required"],
    }
    return {
        "artifact": "BHSM_AE31_C2_R2_ELECTRON_CAPTURE_SELECTION_RULE",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "normalized_S3_rank2_witness": witness,
        "recovered_r2_provenance": provenance,
        "electron_metric_incidence": incidence,
        "capture_vertex_and_hessian_gate": capture,
        "scientific_decision": decision,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("r2/electron-capture selection rule failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
