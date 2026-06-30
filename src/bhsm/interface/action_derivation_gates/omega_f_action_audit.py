"""Audit whether charged Omega_f operators have complete action provenance."""

from __future__ import annotations

from .common import FORBIDDEN_INPUTS, source_evidence


def audit_omega_f_action() -> dict[str, object]:
    evidence = source_evidence(
        (
            "docs/bhsm_sector_projector_ledger_theorem.md",
            "docs/boundary_graded_defect_action_kernel_v1.md",
            "src/boundary_graded_defect_action_kernel.py",
        ),
        ("Omega_l", "Omega_u", "Omega_d", "OPEN"),
    )
    scaffold_linked = evidence["all_paths_present"] and evidence["all_tokens_present"]
    return {
        "audit": "omega_f_action_derivation",
        "status": (
            "STRUCTURALLY_INTEGRATED_NOT_ACTION_DERIVED"
            if scaffold_linked
            else "OPEN_MISSING_OMEGA_F_ACTION_DERIVATION"
        ),
        "operators": {
            "lepton": "Omega_l=-q+2j=3",
            "up": "Omega_u=q-2j=6",
            "down": "Omega_d=q+4j=12",
        },
        "evidence": evidence,
        "complete_action_derivation": False,
        "remaining_blockers": [
            "derive the symbolic parent scaffold uniquely from the complete Berger-Hopf twisted Dirac/bundle action",
            "prove the sector boundary functional without inserting sector coefficients as scaffold data",
        ],
        "forbidden_inputs_used": [],
        "forbidden_inputs": FORBIDDEN_INPUTS,
        "claim_boundary": "The repository integrates Omega_f with projector and boundary-kernel scaffolds; a complete action derivation is not present.",
    }
