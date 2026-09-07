"""Materialize the current-C2 quark projector-overlap bridge."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_quark_projector_overlap_bridge import (
    ACTION_VERSION,
    CLASSIFICATION,
    action_trace_bifurcation,
    basis_invariance_witness,
    claim_boundary,
    current_family_projector_contract,
    exact_remaining_owner,
    projector_overlap_response,
)


A = ROOT / "artifacts/action_extension"
TARGET = A / "BHSM_AE31_C2_QUARK_PROJECTOR_OVERLAP_BRIDGE.json"
INPUTS = (
    A / "BHSM_AE31_C2_QUARK_HIGGS_CONTACT_CLOSURE.json",
    A / "BHSM_AE31_C2_QUARK_HIGGS_INCIDENCE_TRANSPORT.json",
    A / "BHSM_AE3_C2_QUARK_RESPONSE_SUM_RULES.json",
    ROOT / "theory/theorem_discharge_raw_mode_berger_harmonic_map.md",
    ROOT / "theory/theorem_discharge_m_weight_assignment.md",
    ROOT / "src/bhsm/interface/ae31_c2_quark_projector_overlap_bridge.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    contact, incidence, response = map(_load, INPUTS[:3])
    sample_response = projector_overlap_response(
        active_projector=((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)),
        scalar_map=((0, 0, 1, 0), (0, 0, 0, 2), (0, 0, 0, 0), (0, 0, 0, 0)),
        singlet_projector=((0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)),
    )
    witness = basis_invariance_witness()
    family = current_family_projector_contract()
    bifurcation = action_trace_bifurcation()
    remaining = exact_remaining_owner()
    boundary = claim_boundary()
    modes = response["quark_response_sum_rule_theorem"]
    validation = {
        "projector_response_is_positive_hilbert_schmidt_norm": (
            sample_response["response"] == 5.0
            and sample_response["hilbert_schmidt_residual"] < 1e-12
            and sample_response["nonnegative"]
        ),
        "individual_amplitude_changes_but_projector_sum_is_invariant": (
            witness["single_vector_amplitude_basis_dependent"]
            and witness["projector_sum_invariance_residual"] < 1e-12
            and witness["projectors_unchanged_residual"] < 1e-12
        ),
        "preserved_current_quark_modes_reused_exactly": (
            family["up_modes_k_j"] == modes["up"]["modes"]
            and family["down_modes_k_j"] == modes["down"]["modes"]
            and not family["particle_spectrum_rebuilt"]
        ),
        "incidence_and_contact_closure_reused": (
            incidence["claim_boundary"]["CURRENT_C2_QUARK_HIGGS_INCIDENCE_SUPPORT_TRANSPORTED_CONDITIONAL"]
            and contact["claim_boundary"]["CURRENT_C2_QUARK_SQUARED_PENCIL_CONTACT_CLOSED_BY_FIRST_VERTICES"]
        ),
        "action_trace_bifurcation_keeps_state_selection_honest": (
            bifurcation["full_multiplet_trace"]["basis_invariant"]
            and not bifurcation["full_multiplet_trace"]["m_selection_required"]
            and bifurcation["selected_vector_or_density"]["m_or_density_selection_required"]
        ),
        "normalization_and_residues_not_overclaimed": (
            not boundary["CURRENT_C2_QUARK_ACTION_TRACE_DOMAIN_DERIVED"]
            and not boundary["CURRENT_C2_NORMALIZED_INTERNAL_SCALAR_MAP_DERIVED"]
            and not boundary["CURRENT_C2_UP_DOWN_YUKAWA_VERTEX_RESIDUES_ACTION_DERIVED"]
            and not remaining["historical_boundary_targets_relabelled_as_residues"]
            and not boundary["FULL_BHSM_COMPLETE"]
        ),
    }
    return {
        "artifact": "BHSM_AE31_C2_QUARK_PROJECTOR_OVERLAP_BRIDGE",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "projector_overlap_response": sample_response,
        "basis_invariance_witness": witness,
        "current_family_projector_contract": family,
        "action_trace_bifurcation": bifurcation,
        "exact_remaining_owner": remaining,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE3.1 quark projector-overlap bridge failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
