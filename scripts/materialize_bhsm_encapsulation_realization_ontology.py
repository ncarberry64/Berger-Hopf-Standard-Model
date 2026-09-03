"""Materialize the current BHSM encapsulation and realization scope.

This is an evidence composition.  It changes no action, trajectory, center,
coefficient, scale, mode assignment, or frozen prediction.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT
    / "artifacts/current_semantics/BHSM_ENCAPSULATION_REALIZATION_ONTOLOGY.json"
)

PATHS = {
    "ae2_action": "artifacts/action_extension/BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json",
    "family": "artifacts/action_extension/BHSM_AE3_FAMILY_HIERARCHY_INTERFACE.json",
    "mass_ontology": "artifacts/action_extension/BHSM_AE3_FAMILY_MASS_ONTOLOGY_RECOVERY_AUDIT.json",
    "color_bridge": "artifacts/action_extension/BHSM_AE31_C2_COLOR_SINGLET_RESIDUAL_RESPONSE_BRIDGE.json",
    "enclosure_integration": "artifacts/action_extension/BHSM_AE4_CURRENT_C2_PHYSICAL_ENCLOSURE_STATE_INTEGRATION.json",
    "nonlinear_gate7": "artifacts/action_extension/BHSM_AE4_CURRENT_C2_NONLINEAR_CARRIER_AUTHORITY_ADJUDICATION.json",
    "identification_bridge": "artifacts/flagship_integration/BHSM_N12_GATE7_PHYSICAL_ENCAPSULATION_IDENTIFICATION_BRIDGE.json",
    "corpus": "artifacts/flagship_integration/BHSM_NORMAN_SCHOOL_FULL_CORPUS_RECONSTRUCTION.json",
    "generation": "artifacts/BHSM_generation_projector_action_attachment_v8_2.json",
    "gauge_color": "artifacts/BHSM_aether_sm_gauge_color_completion_v15_58.json",
    "completion_dag": "artifacts/current_semantics/BHSM_CURRENT_COMPLETION_DAG.json",
    "gate_ledger": "artifacts/current_semantics/BHSM_CURRENT_GATE_LEDGER.json",
    "ontology_registry": "artifacts/current_semantics/BHSM_CURRENT_ONTOLOGY_REGISTRY.json",
    "quadratic": "src/bhsm/interface/universal_quadratic_spectrum.py",
    "dressed_pole": "src/bhsm/interface/universal_dressed_pole.py",
    "lsz": "src/bhsm/interface/universal_lsz.py",
    "vertices": "src/bhsm/interface/universal_vertex_amplitude.py",
    "decay": "src/bhsm/interface/universal_decay_collision.py",
    "channels": "src/bhsm/interface/universal_channel_ledger.py",
    "optical": "src/bhsm/interface/universal_optical_theorem.py",
}

CLASSIFICATIONS = ("VALIDATED", "INVALIDATED", "OPEN", "CONDITIONAL", "HYPOTHESIS")


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(key: str) -> dict[str, Any]:
    return json.loads((ROOT / PATHS[key]).read_text(encoding="utf-8"))


def _claim(identifier: str, classification: str, statement: str, evidence: list[str],
           missing: list[str] | None = None) -> dict[str, Any]:
    return {
        "id": identifier,
        "classification": classification,
        "statement": statement,
        "evidence": [PATHS[key] for key in evidence],
        "missing_proof": missing or [],
    }


def build_payload() -> dict[str, Any]:
    records = {key: _load(key) for key in (
        "ae2_action", "family", "mass_ontology", "color_bridge",
        "enclosure_integration", "nonlinear_gate7", "identification_bridge",
        "corpus", "generation", "gauge_color", "completion_dag",
        "gate_ledger", "ontology_registry",
    )}
    nonlinear = records["nonlinear_gate7"]
    enclosure = records["enclosure_integration"]
    bridge = records["identification_bridge"]

    claims = [
        _claim(
            "ONE_CURRENT_ACTION_OWNER",
            "VALIDATED",
            "BHSM-AE-2.0.0 is the current owner action/domain; this scope audit adds no action term or adjustable input.",
            ["ae2_action"],
        ),
        _claim(
            "UNIVERSAL_LAW_NONUNIVERSAL_REALIZATIONS",
            "CONDITIONAL",
            "The same action and admissibility mechanism may realize distinct states when mode, scale, environment, boundary data, or interaction history differ.",
            ["corpus", "family", "generation"],
            ["particle-specific action-owned realization theorems"],
        ),
        _claim(
            "ONE_NUMERICAL_TRAJECTORY_FOR_ALL_PARTICLES",
            "INVALIDATED",
            "Using one numerical trajectory as a required representation of every particle is not authorized by the action or current Gate-7 proof.",
            ["corpus", "nonlinear_gate7"],
        ),
        _claim(
            "CURRENT_GATE7_REALIZATION",
            "VALIDATED",
            "The retained 371-node center and its certified carrier are one action-selected background realization used to test reusable local existence and stability machinery.",
            ["nonlinear_gate7", "enclosure_integration"],
        ),
        _claim(
            "CURRENT_GATE7_PARTICLE_UNIVERSALITY",
            "OPEN",
            "Gate 7 does not identify its current trajectory with every electron, quark, neutrino, hadron, atom, or other physical realization.",
            ["identification_bridge", "corpus"],
            ["environment-conditioned particle-specific realization maps"],
        ),
        _claim(
            "TOPOLOGICAL_ZERO_INTERIOR_FERMION_CLASS",
            "HYPOTHESIS",
            "A fundamental fermion-like mode may close topologically without a nonzero enclosed spacetime volume.",
            ["corpus", "family"],
            ["same-action topological closure theorem", "zero-interior theorem", "physical mode attachment"],
        ),
        _claim(
            "LOCAL_CARRIER_STATE_ENCLOSURE_BRIDGE",
            "VALIDATED",
            "Existing particle/family fibers are transported to the action-owned local carrier and state-enclosure interface without rebuilding the particle spectrum.",
            ["enclosure_integration", "family", "generation"],
        ),
        _claim(
            "COMPLETE_INTERACTING_SPACETIME_VOLUME_ENCLOSURE",
            "OPEN",
            "A complete interacting AE4 child with nonzero sector blocks and an independently proved spacetime-volume enclosure is not yet derived.",
            ["enclosure_integration", "identification_bridge"],
            ["Green-image two-radius certificate", "full interacting field inheritance", "physical Noether-Hamiltonian closure"],
        ),
        _claim(
            "HADRON_FIRST_SPACETIME_VOLUME_ONSET",
            "HYPOTHESIS",
            "Composite hadronic organization may be the first regime admitting genuine spacetime-volume enclosure.",
            ["corpus", "color_bridge"],
            ["returned hadron resolvent", "confinement theorem", "nonzero-volume enclosure theorem"],
        ),
        _claim(
            "ATOMIC_OR_MACROSCOPIC_SPACETIME_VOLUME_ENCLOSURE",
            "HYPOTHESIS",
            "Atomic and larger bound structures are expected to lie in an enclosure regime, but no universal particle-to-volume theorem is current.",
            ["corpus"],
            ["composite bound-state enclosure theorem"],
        ),
        _claim(
            "TWO_ELECTRON_SUPERCONDUCTOR",
            "INVALIDATED",
            "An isolated pair of electrons is not by itself a superconducting state.",
            ["corpus"],
        ),
        _claim(
            "CORRELATED_PAIR_IN_COLLECTIVE_STATE",
            "OPEN",
            "A paired topological configuration may contribute to a coherent many-body superconducting phase only after a collective action and propagation theorem are supplied.",
            ["corpus"],
            ["many-body environment", "collective coherence", "transport response"],
        ),
        _claim(
            "ENCAPSULATION_STABILITY_TO_DECAY",
            "OPEN",
            "Local encapsulation stability is not yet a decay-width or lifetime prediction; the pole, residue, vertex, channel, and phase-space chain must be instantiated on one action-owned realization.",
            ["quadratic", "dressed_pole", "lsz", "vertices", "decay", "channels", "optical"],
            ["closed physical background", "renormalized amplitudes", "complete open-channel ledger", "physical scale"],
        ),
    ]

    realization_dag = [
        {"id": "R1", "object": "UNIVERSAL_ACTION", "status": "VALIDATED", "depends_on": []},
        {"id": "R2", "object": "ENCAPSULATION_ADMISSIBILITY_LAW", "status": "CONDITIONAL", "depends_on": ["R1"]},
        {"id": "R3", "object": "ENVIRONMENT_MODE_SCALE_BOUNDARY_HISTORY_DATA", "status": "OPEN", "depends_on": ["R2"]},
        {"id": "R4", "object": "REALIZED_TRAJECTORY_OR_STATE", "status": "OPEN", "depends_on": ["R3"]},
        {"id": "R5", "object": "CONSTRAINED_STABILITY_AND_TRANSITION_STRUCTURE", "status": "OPEN", "depends_on": ["R4"]},
        {"id": "R6", "object": "PARTICLE_MANIFESTATION_AND_OBSERVABLES", "status": "OPEN", "depends_on": ["R5"]},
    ]

    environment_assets = [
        {"input": "mode_and_family_data", "status": "VALIDATED_REUSABLE_UPSTREAM", "evidence": [PATHS["family"], PATHS["generation"]], "open": "action-selected physical response and scale"},
        {"input": "representation_and_projector_data", "status": "VALIDATED_REUSABLE_UPSTREAM", "evidence": [PATHS["generation"], PATHS["gauge_color"]], "open": "current full-field attachment"},
        {"input": "gauge_weak_electromagnetic_environment", "status": "CONDITIONAL_COMPONENTS_PRESENT", "evidence": [PATHS["gauge_color"], PATHS["enclosure_integration"]], "open": "same-background interacting physical sector blocks"},
        {"input": "color_environment", "status": "CONDITIONAL_SINGLET_RESPONSE_INTERFACE", "evidence": [PATHS["color_bridge"]], "open": "global confinement, returned hadron resolvent, physical residual nuclear response"},
        {"input": "scalar_HS_environment", "status": "OPEN_CURRENT_ATTACHMENT", "evidence": [PATHS["enclosure_integration"]], "open": "nonzero interacting HS/scalar block on the certified background"},
        {"input": "boundary_and_event_data", "status": "VALIDATED_FOR_CURRENT_REALIZATION", "evidence": [PATHS["identification_bridge"], PATHS["nonlinear_gate7"]], "open": "particle-specific environment-conditioned boundary data"},
        {"input": "physical_scale", "status": "OPEN", "evidence": [PATHS["mass_ontology"]], "open": "action-owned mode energy-to-physical-scale link"},
    ]

    decay_dag = [
        {"id": "D1", "object": "ACTION_OWNED_ENVIRONMENT_CONDITIONED_REALIZATION", "status": "OPEN", "depends_on": []},
        {"id": "D2", "object": "PHYSICAL_QUOTIENT_QUADRATIC_HESSIAN", "status": "OPEN", "depends_on": ["D1"]},
        {"id": "D3", "object": "DRESSED_SIMPLE_POLES_AND_RESIDUES", "status": "OPEN", "depends_on": ["D2"]},
        {"id": "D4", "object": "RENORMALIZED_S3_S4_VERTICES_AND_LSZ_STATES", "status": "OPEN", "depends_on": ["D3"]},
        {"id": "D5", "object": "COMPLETE_ALLOWED_DECAY_CHANNEL_LEDGER", "status": "OPEN", "depends_on": ["D4"]},
        {"id": "D6", "object": "OUTWARD_PHASE_SPACE_AND_PARTIAL_WIDTHS", "status": "OPEN", "depends_on": ["D5"]},
        {"id": "D7", "object": "TOTAL_WIDTH_OPTICAL_THEOREM_AND_LIFETIME", "status": "OPEN", "depends_on": ["D6"]},
    ]

    guardrails = {
        "ALL_PARTICLES_SHARE_ONE_TRAJECTORY": False,
        "EVERY_ELEMENTARY_PARTICLE_ENCLOSES_SPACETIME": False,
        "PROTON_NEUTRON_SPACETIME_ENCLOSURE_DERIVED": False,
        "TWO_ELECTRONS_ALONE_CONSTITUTE_SUPERCONDUCTIVITY": False,
        "GATE7_PROVES_ALL_PARTICLE_SPECIFIC_REALIZATIONS": False,
        "ENCAPSULATION_STABILITY_DERIVES_DECAY_RATES": False,
        "PARTICLE_SPECTRUM_REBUILT_HERE": False,
        "NEW_ACTION_OR_FIT_INTRODUCED": False,
    }

    current_registry_text = json.dumps(
        {
            key: records[key]
            for key in ("completion_dag", "gate_ledger", "ontology_registry")
        },
        sort_keys=True,
    ).lower()
    natural_language_overclaims = (
        "all particles share the current 371-node trajectory",
        "every elementary particle encloses spacetime",
        "two electrons alone constitute superconductivity",
        "gate 7 proves all particle-specific realizations",
    )

    validations = {
        "all_inputs_exist": all((ROOT / path).is_file() for path in PATHS.values()),
        "all_source_artifacts_validate": all(records[key]["validation_passed"] is True for key in records),
        "current_action_preserved": records["ae2_action"]["action_version"] == "BHSM-AE-2.0.0",
        "family_modes_preserved_without_spectrum_rebuild": records["family"]["family_modes_can_manifest_as_SM_particles"] is True and records["family"]["particle_spectrum_rebuilt"] is False,
        "local_bridge_and_complete_interacting_boundary_reconciled": enclosure["claim_boundary"]["BHSM_NATIVE_PARTICLE_STATE_TO_LOCAL_ENCLOSURE_BRIDGE_DERIVED"] is True and enclosure["claim_boundary"]["PHYSICAL_ENCAPSULATION_IDENTIFIED_AT_COMPLETE_AE4_INTERACTING_LEVEL"] is False,
        "generic_identification_remains_fail_closed": bridge["claim_boundary"]["physical_encapsulation_identified"] is False and bridge["claim_boundary"]["spacetime_pocket_identified"] is False,
        "Gate7_math_and_active_blocker_preserved": nonlinear["claim_boundary"]["G7_CURRENT_GREEN_CORRELATED_CENTRAL_SCALAR_CAUSAL_COMPOSITION_DERIVED"] is True and nonlinear["claim_boundary"]["G7_CURRENT_GREEN_MIXED_DIRECT_BILINEAR_ALL_ENDPOINT_CENTERS_MATERIALIZED"] is True and nonlinear["claim_boundary"]["G7_CURRENT_GREEN_MIXED_DIRECT_BILINEAR_OUTWARD_EQUIVALENCE_DERIVED"] is True and nonlinear["claim_boundary"]["G7_CURRENT_GREEN_MIXED_TRANSVERSE_ALL_NODES_DERIVED"] is True and nonlinear["claim_boundary"]["G7_CURRENT_GREEN_MIXED_TRANSVERSE_ALL_MIDPOINTS_DERIVED"] is False and nonlinear["claim_boundary"]["G7_CURRENT_GREEN_TRANSVERSE_TRANSVERSE_FULL_OPERATOR_BOUND_DERIVED"] is False,
        "all_claims_classified": all(claim["classification"] in CLASSIFICATIONS for claim in claims),
        "realization_dag_is_acyclic_in_declared_order": all(all(dep < row["id"] for dep in row["depends_on"]) for row in realization_dag),
        "decay_dag_is_acyclic_in_declared_order": all(all(dep < row["id"] for dep in row["depends_on"]) for row in decay_dag),
        "all_overclaim_guardrails_fail_closed": not any(guardrails.values()),
        "current_completion_and_ontology_registries_contain_no_particle_universality_overclaim": not any(
            phrase in current_registry_text for phrase in natural_language_overclaims
        ),
    }

    return {
        "artifact": "BHSM_ENCAPSULATION_REALIZATION_ONTOLOGY",
        "schema_version": 1,
        "action_version": "BHSM-AE-2.0.0",
        "status": "UNIVERSAL_ACTION_WITH_ENVIRONMENT_CONDITIONED_REALIZATIONS__GATE7_ONE_REALIZATION_ACTIVE_NOT_CLOSED",
        "FULL_BHSM_COMPLETE": False,
        "scope_adjudication": {
            "universal_object": "ACTION_AND_ADMISSIBILITY_MECHANISM",
            "nonuniversal_objects": ["mode", "scale", "environment", "boundary_conditions", "interaction_history", "admissible_surface_trajectory", "realized_state"],
            "current_371_node_object": "ONE_ACTION_SELECTED_BACKGROUND_REALIZATION_AND_REUSABLE_PROOF_CARRIER",
            "Gate7_status": "ACTIVE_NOT_CLOSED",
            "Gate7_particle_scope": "NO_PARTICLE_SPECIFIC_UNIVERSALITY_CLAIM",
            "exact_active_blocker": nonlinear["exact_next_calculation"],
        },
        "audit_findings": [
            {
                "classification": "VALIDATED",
                "finding": "No explicit current completion-DAG, gate-ledger, or ontology-registry claim says that all particles share the retained 371-node trajectory.",
            },
            {
                "classification": "CONDITIONAL",
                "finding": "Earlier universal carrier/background wording could be overread as particle universality; the current scope now restricts universality to the action and admissibility mechanism.",
            },
            {
                "classification": "VALIDATED",
                "finding": "The local carrier/state enclosure bridge and the still-open complete interacting spacetime-volume enclosure are compatible statements at different proof levels.",
            },
            {
                "classification": "VALIDATED",
                "finding": "The historical corpus had already separated propagating, topological candidate, event-child, confined, and composite classes; this artifact restores that separation to the active integration layer.",
            },
        ],
        "claim_ledger": claims,
        "environment_conditioned_realization_dag": realization_dag,
        "environment_asset_map": environment_assets,
        "stability_to_decay_dependency_dag": decay_dag,
        "prediction_firewall": {
            "order": ["DERIVE", "CERTIFY", "FREEZE_AND_HASH", "PREDICT", "COMPARE"],
            "measured_values_used_to_select_upstream_mathematics": False,
        },
        "guardrails": guardrails,
        "consequences": {
            "current_Gate7_calculation_changed": False,
            "physical_result_invalidated": False,
            "frozen_prediction_changed": False,
            "calibration_value_entered_derivation": False,
        },
        "inputs": {path: _sha256(ROOT / path) for path in PATHS.values()},
        "validation": validations,
        "validation_passed": all(validations.values()),
    }


def main() -> None:
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(RESULT)


if __name__ == "__main__":
    main()
