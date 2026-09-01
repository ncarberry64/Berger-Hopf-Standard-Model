"""Materialize the capture-to-neutrino propagation gate."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_capture_neutrino_propagation_gate import (
    ACTION_VERSION,
    CLASSIFICATION,
    capture_boundary_to_propagation_contract,
    claim_boundary,
    common_shift_invariance,
    electron_capture_family_source,
    family_central_propagation,
    family_noncentrality_theorem,
    historical_neutrino_reconciliation,
    squared_neutral_operator_contract,
)


A = ROOT / "artifacts/action_extension"
TARGET = A / "BHSM_AE31_C2_CAPTURE_NEUTRINO_PROPAGATION_GATE.json"
INPUTS = (
    A / "BHSM_AE31_C2_R2_ELECTRON_CAPTURE_SELECTION_RULE.json",
    A / "BHSM_AE31_C2_COEXACT_SU2L_CHARGED_CURRENT.json",
    A / "BHSM_AE31_C2_OUTER_CALDERON_ACTION_NO_GO.json",
    ROOT / "artifacts/BHSM_pair_wake_neutrino_action_v14_55.json",
    ROOT / "artifacts/BHSM_aether_physical_inverse_closure_v16_36.json",
    ROOT / "src/bhsm/interface/ae31_c2_capture_neutrino_propagation_gate.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    capture, charged, outer, historical, inverse = map(_load, INPUTS[:5])
    source = electron_capture_family_source()
    central = family_central_propagation((1.0, 0.0, 0.0), 0.713)
    gaps = common_shift_invariance(np.diag((0.2, 0.7, 1.4)), 8.3)
    squared = squared_neutral_operator_contract()
    noncentral = family_noncentrality_theorem()
    chain = capture_boundary_to_propagation_contract()
    reconciliation = historical_neutrino_reconciliation()
    boundary = claim_boundary()
    neutral_row = next(
        row
        for row in inverse["inverse_observation_ledger"]
        if row["OBSERVED_FACT"] == "neutrino_oscillation_requires_nonzero_propagation_splittings"
    )
    validation = {
        "capture_gate_reused": capture["validation_passed"],
        "charged_current_reused": charged["validation_passed"],
        "outer_state_no_go_preserved": outer["claim_boundary"][
            "CURRENT_AE31_RETAINED_ACTION_OUTER_CALDERON_COMPLETION_NO_GO_DERIVED"
        ],
        "historical_hypothesis_reclassified": "NOT_DERIVED" in historical[
            "hypothesis_status"
        ],
        "current_neutral_owner_reused": "family-noncentral" in neutral_row[
            "MISSING_MATHEMATICAL_OBJECT"
        ],
        "nue_source_exact": source["source_vector"] == [1.0, 0.0, 0.0],
        "central_no_oscillation_exact": central["probability_change_norm"] < 1.0e-15,
        "common_shift_gap_invariant": gaps["gap_invariance_residual"] < 5.0e-15,
        "local_D2_not_relabelled_mass": not squared[
            "local_D_squared_eigenvalue_is_automatically_a_mass_squared"
        ],
        "family_noncentral_gate_open": not noncentral[
            "current_C2_family_noncentral_neutral_operator_derived"
        ],
        "outgoing_mode_not_overclaimed": (
            not chain["outgoing_nu_e_boundary_trace_derived"]
            and not boundary["CURRENT_C2_TWO_NEUTRINO_SPLITTINGS_DERIVED"]
        ),
        "historical_mass_semantics_preserved": "QUASI_ENERGY" in reconciliation[
            "v14_55_reusable_ontology"
        ][2],
    }
    return {
        "artifact": "BHSM_AE31_C2_CAPTURE_NEUTRINO_PROPAGATION_GATE",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "capture_family_source": source,
        "family_central_propagation_witness": {
            key: value for key, value in central.items() if key != "evolution"
        },
        "common_shift_gap_witness": gaps,
        "squared_neutral_operator_contract": squared,
        "family_noncentrality_theorem": noncentral,
        "capture_boundary_to_propagation": chain,
        "historical_neutrino_reconciliation": reconciliation,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("capture-to-neutrino propagation gate failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
