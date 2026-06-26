from __future__ import annotations

from typing import Dict, List


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"

ARCHITECTURE_SECTORS = (
    "finite algebra / gauge skeleton",
    "hypercharge and anomaly ledger",
    "charged sector",
    "A-local branch",
    "A-background identity branch",
    "minimal K_collar anisotropic scaffold",
    "K_collar audit result and downgrade",
    "B-diagnostic branch",
    "Z_virt up-sector threshold bridge",
    "neutral Hessian sector",
    "neutral bridge / PMNS structural source",
    "CKM structural source",
    "boundary relative-holonomy CP source",
    "gauge/electroweak/Higgs open gates",
    "common-scale/RG transport open gates",
    "comparison-ready prediction package open gate",
)

REMAINING_OPEN_BLOCKERS = (
    "boundary-derived chi",
    "non-diagonal value-curvature K_collar only if action-derived",
    "oriented finite-width / jet-heat response audit",
    "absolute same-sector mass ratios",
    "cross-sector transported mass ratios",
    "residual RG coefficients",
    "full scheme/common-scale alignment",
    "exact action derivation of g_bridge=16/189",
    "neutral eta/beta/kappa final derivation",
    "neutral threshold rules",
    "PMNS numerical closure",
    "CKM numerical closure",
    "CP numerical closure",
    "Higgs/electroweak absolute scale",
    "final comparison-ready prediction package",
)

FORBIDDEN_CLAIMS = (
    "BHSM is proven",
    "BHSM replaces the Standard Model",
    "BHSM predicts all particle masses",
    "BHSM has solved CKM/PMNS",
    "BHSM has predicted the Higgs mass",
    "BHSM is experimentally confirmed",
)

ALLOWED_STRONGEST_CLAIM = (
    "BHSM provides an integrated conditional action-level architecture that "
    "organizes the Standard Model gauge ledger, chiral matter content, charged "
    "hierarchy mechanism, neutral topographic suppression, mixing structure, "
    "CP source, and no-retuning prediction protocol within a Berger-Hopf / "
    "finite-boundary geometric framework."
)


def architecture_freeze_artifact() -> Dict[str, object]:
    return {
        "artifact": "full_BHSM_architecture_freeze_v1",
        "public_status": PUBLIC_STATUS,
        "official_predictions_changed": False,
        "core_rule": "derive -> freeze -> compare -> claim",
        "architecture_sectors": list(ARCHITECTURE_SECTORS),
        "branch_distinctions": {
            "A-local": "K_f = P_f[K_0 + K_incidence + K_bridge + K_threshold]P_f",
            "A-background identity": (
                "K_f = P_f[K_0 + C_ch K_collar,id + K_incidence + "
                "K_bridge + K_threshold]P_f"
            ),
            "A-background identity C_ch": "Tr_sector(P_ch)=3",
            "A-background identity K_collar": "I_J",
            "minimal anisotropic K_collar": "K_collar,min^J = diag(1, 1+chi, 1+2chi)",
            "minimal anisotropic chi": "chi = lambda_A Tr(A^2)",
            "B-diagnostic": "rho_ch scan / q^2 + rho_ch*j^2 candidate diagnostics only",
        },
        "charged_status": {
            "charged_generator_classification": "B-diagnostic",
            "A_background_implemented_in_PR40": False,
            "A_background_identity_branch": "IMPLEMENTED_CONDITIONAL",
            "A_background_dependency_order": "VERIFIED",
            "A_local_branch_matrix_export": "EXPORTED",
            "B_diagnostic_branch": "PRESERVED_DIAGNOSTIC",
            "Z_virt_leakage_found": False,
            "forbidden_fit_found": False,
            "K_collar_response_audit": "RAN",
            "K_collar_sector_verdicts": {
                "lepton": "COLLAR_COMPRESSES_HIERARCHY",
                "up": "COLLAR_COMPRESSES_HIERARCHY",
                "down": "COLLAR_COMPRESSES_HIERARCHY",
            },
            "K_collar_stack_verdict": "STACK_COLLAR_REJECTED_AS_PRIMARY",
            "minimal_positive_diagonal_K_collar_as_primary_charged_precision_route": (
                "REJECTED_AS_PRIMARY_BY_RESPONSE_AUDIT"
            ),
            "charged_precision_closure": "OPEN",
            "chi_from_boundary_geometry": "OPEN_LOCALIZABLE",
            "chi_from_mass_fit": "FORBIDDEN",
        },
        "charged_precision_redirect": [
            "oriented finite-width / jet-heat response",
            "localized thresholds",
            "common-scale RG/scheme transport",
            "possible non-diagonal value-curvature collar mixing only if action-derived",
            "B-diagnostic geometry discovery only",
        ],
        "latest_pr_checkpoints": [
            {
                "pr": 40,
                "title": "PO-BH: Codex reentry branch audit and K-collar scaffold",
                "branch": "bhsm-codex-reentry-branch-audit-kcollar-v1",
                "commit": "cee1fd0",
                "tests": "1647 passed",
            },
            {
                "pr": 41,
                "title": "PO-BH: A-background collar dependency-order scaffold",
                "branch": "bhsm-a-background-collar-dependency-order-v1",
                "commit": "84ec474",
                "tests": "1648 passed",
            },
        ],
        "forbidden_claims": list(FORBIDDEN_CLAIMS),
        "allowed_strongest_claim": ALLOWED_STRONGEST_CLAIM,
        "remaining_open_blockers": list(REMAINING_OPEN_BLOCKERS),
    }


def open_gate_ledger_updates() -> Dict[str, object]:
    return {
        "full_BHSM_architecture": "INTEGRATED_CONDITIONAL",
        "full_BHSM_numerical_closure": "OPEN",
        "minimal_positive_diagonal_K_collar_as_primary_charged_precision_route": (
            "REJECTED_AS_PRIMARY_BY_RESPONSE_AUDIT"
        ),
        "K_collar_response_audit": "RAN",
        "K_collar_stack_verdict": "STACK_COLLAR_REJECTED_AS_PRIMARY",
        "charged_precision_closure": "OPEN",
        "official_predictions": "UNCHANGED",
    }


def claim_status_rows() -> List[Dict[str, str]]:
    return [
        {
            "claim": "Full BHSM architecture",
            "status": "INTEGRATED_CONDITIONAL",
            "boundary": "Architecture is integrated conditionally; numerical closure remains open.",
        },
        {
            "claim": "Minimal positive diagonal K_collar as primary charged-precision route",
            "status": "REJECTED_AS_PRIMARY_BY_RESPONSE_AUDIT",
            "boundary": "This rejects the minimal diagonal collar route as primary, not BHSM.",
        },
        {
            "claim": "A-background identity branch",
            "status": "IMPLEMENTED_CONDITIONAL",
            "boundary": "Identity dependency-order scaffold only; chi remains open.",
        },
        {
            "claim": "Full numerical closure",
            "status": "OPEN",
            "boundary": "No final mass, CKM, PMNS, CP, Higgs, or comparison-ready closure is claimed.",
        },
    ]
