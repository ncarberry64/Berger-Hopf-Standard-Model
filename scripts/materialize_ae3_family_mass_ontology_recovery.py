"""Materialize the AE3 family mass-ontology recovery audit."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae3_family_mass_ontology_recovery import (
    ACTION_VERSION,
    CLASSIFICATION,
    claim_boundary,
    lineage_ledger,
    missing_bridge_decomposition,
    recovered_hopf_semigroup_candidate,
)


A = ROOT / "artifacts"
CYCLE = A / "BHSM_cycle_invariant_mass_contract_v14_54.json"
ANCHOR = A / "BHSM_cosmological_parent_anchor_v14_54.json"
SPECTRUM = A / "BHSM_aether_hybrid_flavor_spectrum_v15_54.json"
SEMANTICS = A / "BHSM_aether_hybrid_yukawa_mass_semantics_v15_56.json"
FAMILY = A / "action_extension/BHSM_AE3_FAMILY_NONCENTRAL_RETURN_PROVENANCE_AUDIT.json"
HARMONIC = A / "action_extension/BHSM_AE3_FAMILY_HARMONIC_ENERGY_PULLBACK_AUDIT.json"
PARENT = A / "qxi_relative_energy_preparation/BHSM_N12_MATCHED_PARENT_STATIONARY_SECTION_GATE.json"
CHARGE = A / "intrinsic_state_selection/BHSM_N12_CHILD_BOUNDARY_HAMILTONIAN_OWNERSHIP_GATE.json"
PACKET = ROOT / "docs/research_packets/2026-08-03/BHSM_HOPF_BASE_OVERLAP_AND_DIMENSIONFUL_LEPTON_SCALE_2026-08-03.md"
MANUAL = ROOT / "docs/research_packets/2026-08-03/BHSM_FINAL_PARENT_ACTION_LEPTON_MASS_COMPLETION_2026-08-03.md"
TARGET = A / "action_extension/BHSM_AE3_FAMILY_MASS_ONTOLOGY_RECOVERY_AUDIT.json"
INPUTS = (CYCLE, ANCHOR, SPECTRUM, SEMANTICS, FAMILY, HARMONIC, PARENT, CHARGE, PACKET, MANUAL, ROOT / "src/bhsm/interface/ae3_family_mass_ontology_recovery.py")


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    cycle, anchor, spectrum, semantics, family, harmonic, parent, charge = map(_load, INPUTS[:8])
    packet_text = PACKET.read_text(encoding="utf-8")
    manual_text = MANUAL.read_text(encoding="utf-8")
    lineage = lineage_ledger()
    candidate = recovered_hopf_semigroup_candidate()
    bridge = missing_bridge_decomposition()
    boundary = claim_boundary()
    validation = {
        "v14_54_mass_contract_is_parent_relative": "composite-minus-parent" in cycle["relative_charge"],
        "v14_54_scale_anchor_explicitly_conditional": anchor["effective_branch"]["absolute_unit_closed_conditionally"] is True and anchor["effective_branch"]["zero_input_scale_derived"] is False,
        "v15_54_scalar_seed_not_mass": spectrum["claim_boundary"]["physical_fermion_masses_derived"] is False,
        "v15_56_I3_scope_preserved": semantics["paired_mode_overlap"]["all_geometric_overlap_matrices"] == "I3" and semantics["Yukawa_operator_factorization"]["vertical_Dirac_levels_are_mass_matrix_entries"] is False,
        "current_family_audit_remains_open": family["claim_boundary"]["family_mass_hierarchy_derived"] is False,
        "positive_local_energy_no_go_scoped": harmonic["claim_boundary"]["v14_54_parent_relative_cycle_energy_tested_here"] is False,
        "matched_parent_still_absent": parent["Q_xi_evaluated"] is False and parent["Delta_H_evaluated"] is False,
        "complete_child_charge_still_absent": charge["no_go_scope"]["present_repository_can_evaluate_unique_differentiable_H_xi_child"] is False,
        "historical_semigroup_formula_recovered": "exp\\left(-\\frac{\\mathcal L_a}{4\\pi}\\right)" in packet_text,
        "historical_scale_inputs_were_conditional": "### CONDITIONAL INPUTS" in packet_text,
        "manual_action_packet_not_silently_current_AE3": "Repository baseline:** BHSM v11.3" in manual_text,
        "recovered_weights_are_distinct_and_decreasing": candidate["three_distinct_weights"] and candidate["weight_order"] == "heavy>middle>light",
        "no_single_radius_overclaim": bridge["single_missing_numeric_radius_only"] is False,
        "no_historical_number_promoted": boundary["historical_conditional_numbers_promoted"] is False,
        "no_measured_mass_or_spectrum_rebuild": boundary["measured_mass_used"] is False and boundary["particle_spectrum_rebuilt"] is False,
    }
    return {
        "artifact": "BHSM_AE3_FAMILY_MASS_ONTOLOGY_RECOVERY_AUDIT",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "lineage_ledger": lineage,
        "recovered_Hopf_semigroup_candidate": candidate,
        "missing_bridge_decomposition": bridge,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE3 family mass-ontology recovery audit failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
