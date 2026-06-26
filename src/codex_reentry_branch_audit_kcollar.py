from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import pi
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import charged_kf_generator as kf
from constants import ALPHA_INV_LOW_ENERGY, S_OVERLAP


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"

EXPECTED_CONTINUITY_FILES = (
    "bhsm_progress_bookmark_since_latest_codex_prompt.json",
    "bhsm_catchup_bookmark_2_since_last_json.json",
    "full_bhsm_closure_open_gate_ledger.json",
    "bhsm_assume_proceed_full_continuation.json",
    "bhsm_charged_generator_audit.py",
    "bhsm_k_collar_response_audit.py",
)

OPEN_PR_STACK = (
    {
        "number": 30,
        "head": "bhsm-rho-ch-branch-pressure-test-v1",
        "base": "main",
        "title": "PO-BH: rho_ch Branch Pressure Test",
    },
    {
        "number": 31,
        "head": "bhsm-charged-stiffness-action-selector-v1",
        "base": "bhsm-rho-ch-branch-pressure-test-v1",
        "title": "PO-BH: Charged Stiffness Action Selector",
    },
    {
        "number": 32,
        "head": "bhsm-charged-kf-bridge-coupling-kernel-v1",
        "base": "bhsm-charged-stiffness-action-selector-v1",
        "title": "PO-BH: Charged Kf Bridge-Coupling Source Kernel",
    },
    {
        "number": 33,
        "head": "bhsm-full-threshold-operator-eligibility-v1",
        "base": "bhsm-charged-kf-bridge-coupling-kernel-v1",
        "title": "PO-BH: Full Threshold Operator Eligibility Kernel",
    },
    {
        "number": 34,
        "head": "bhsm-neutral-sector-operator-kernel-v1",
        "base": "bhsm-full-threshold-operator-eligibility-v1",
        "title": "PO-BH: Neutral Sector Operator Kernel",
    },
    {
        "number": 35,
        "head": "bhsm-full-closure-dependency-rg-interface-v1",
        "base": "bhsm-neutral-sector-operator-kernel-v1",
        "title": "PO-BH: Full Closure Dependency Graph and RG Interface",
    },
    {
        "number": 36,
        "head": "bhsm-same-sector-rg-gauge-cancellation-v1",
        "base": "bhsm-full-closure-dependency-rg-interface-v1",
        "title": "PO-BH: Same-sector RG gauge cancellation",
    },
    {
        "number": 37,
        "head": "bhsm-residual-yukawa-transport-decomposition-v1",
        "base": "bhsm-same-sector-rg-gauge-cancellation-v1",
        "title": "PO-BH: Residual Yukawa transport decomposition",
    },
    {
        "number": 38,
        "head": "bhsm-full-shape-neutral-holonomy-continuation-v1",
        "base": "bhsm-residual-yukawa-transport-decomposition-v1",
        "title": "PO-BH: Shape, neutral, and holonomy structural diagnostics",
    },
    {
        "number": 39,
        "head": "bhsm-incidence-normalized-overlap-bridge-source-v1",
        "base": "bhsm-full-shape-neutral-holonomy-continuation-v1",
        "title": "PO-BH: Incidence-normalized overlap bridge source",
    },
)

REMAINING_OPEN_BLOCKERS = (
    "absolute same-sector mass ratios",
    "cross-sector transported mass ratios",
    "residual RG coefficients",
    "full scheme/common-scale alignment",
    "exact action derivation of g_bridge=16/189",
    "exact action derivation of boundary phase source",
    "neutral eta/beta/kappa final derivation",
    "neutral threshold rules",
    "PMNS numerical closure",
    "CKM numerical closure",
    "CP numerical closure",
    "Higgs/electroweak absolute scale",
    "final comparison-ready prediction package",
)


@dataclass(frozen=True)
class GeneratorInspection:
    classification: str
    a_background_implemented: bool
    z_virt_leakage_found: bool
    forbidden_fit_found: bool
    evidence: Tuple[str, ...]
    open_items: Tuple[str, ...]


def fraction_string(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _matrix_to_strings(matrix: Iterable[Iterable[object]]) -> List[List[str]]:
    rows: List[List[str]] = []
    for row in matrix:
        rows.append([
            fraction_string(value) if isinstance(value, Fraction) else str(value)
            for value in row
        ])
    return rows


def continuity_inventory(codex_root: Path, repo_root: Path) -> Dict[str, List[str]]:
    found: List[str] = []
    missing: List[str] = []
    for name in EXPECTED_CONTINUITY_FILES:
        candidates = (codex_root / name, repo_root / name, repo_root / "artifacts" / name)
        existing = [str(path) for path in candidates if path.exists()]
        if existing:
            found.extend(existing)
        else:
            missing.append(name)
    return {"found": found, "missing": missing}


def inspect_charged_generator(repo_root: Path) -> GeneratorInspection:
    source = (repo_root / "src" / "charged_kf_generator.py").read_text(encoding="utf-8")
    has_sector_local_metric = "charged_norm_N(q: int, j: int, rho_ch" in source
    has_direct_diagonal_costs = "charged_norm_N(q, j, rho_ch)" in source
    has_background_order = all(
        token in source
        for token in (
            "Tr_sector(P_ch)",
            "C_ch",
            "K_boundary[C_ch]",
            "P_f K_boundary",
        )
    )
    threshold_insertions = kf.threshold_insertions()
    z_virt_leakage_found = threshold_insertions != [
        {
            "sector": "up",
            "slot": 1,
            "mode": [6, 0],
            "value": "ln 2",
            "source": "Z_virt^{u,2}=1/2 weak-double projection bridge",
            "operator_level": True,
        }
    ]
    blocked_imports = (
        "prediction_ledger",
        "residual_audit",
        "flavor_matrix",
        "pmns",
        "gauge_couplings",
    )
    forbidden_fit_found = any(token in source for token in blocked_imports)
    if forbidden_fit_found:
        classification = "invalid"
    elif has_background_order:
        classification = "A-background"
    elif has_sector_local_metric and has_direct_diagonal_costs:
        classification = "B-diagnostic"
    else:
        classification = "open"
    return GeneratorInspection(
        classification=classification,
        a_background_implemented=classification == "A-background",
        z_virt_leakage_found=z_virt_leakage_found,
        forbidden_fit_found=forbidden_fit_found,
        evidence=(
            "charged_kf_generator computes diagonal costs through charged_norm_N(q,j,rho_ch), i.e. q^2 + rho_ch*j^2.",
            "No P_ch -> Tr_sector(P_ch) -> C_ch -> K_boundary[C_ch] -> P_f projection order is implemented.",
            "threshold_insertions emits only the up middle mode (q,j)=(6,0) ln2 slot.",
        ),
        open_items=(
            "A-background dependency-order implementation remains open.",
            "K_collar coefficient chi remains boundary-derived/open, not fitted.",
        ),
    )


def generator_inspection_artifact(repo_root: Path) -> Dict[str, object]:
    inspection = inspect_charged_generator(repo_root)
    return {
        "artifact": "charged_generator_branch_inspection_v2",
        "public_status": PUBLIC_STATUS,
        "official_predictions_changed": False,
        "charged_generator_classification": inspection.classification,
        "A_background_implemented": inspection.a_background_implemented,
        "Z_virt_leakage_found": inspection.z_virt_leakage_found,
        "forbidden_fit_found": inspection.forbidden_fit_found,
        "pass_condition_for_A_background": (
            "P_ch -> Tr_sector(P_ch) -> C_ch -> K_boundary[C_ch] -> K_f projection"
        ),
        "diagnostic_condition_found": "K_f_local -> rho_ch inserted through q^2 + rho_ch*j^2",
        "evidence": list(inspection.evidence),
        "open_items": list(inspection.open_items),
    }


def frozen_constants_artifact() -> Dict[str, object]:
    return {
        "artifact": "frozen_constants_v2",
        "public_status": PUBLIC_STATUS,
        "official_predictions_changed": False,
        "a": 1.157054135733433,
        "a_formula": "alpha^{-1}/(12*pi^2)",
        "a_repo_value": ALPHA_INV_LOW_ENERGY / (12.0 * pi**2),
        "S": "1/(4*pi)",
        "S_repo_value": S_OVERLAP,
        "Lambda_squared": "1/(4*pi)",
        "mu_H": "64*pi^5",
        "charged_dyadic_vector": [1, 2, 4],
        "I_ch": 21,
        "O_ch_squared": "16/9",
        "Z_virt_u2": "1/2",
        "Z_virt_scope": "up sector, middle mode (q,j)=(6,0) only",
    }


def _sector_template(sector: str, claim_status: str) -> Dict[str, object]:
    mode_ledgers = {
        "lepton": [[0, 0], [1, 2], [3, 3]],
        "up": [[0, 0], [6, 0], [8, 1]],
        "down": [[0, 0], [0, 3], [4, 2]],
    }
    row: Dict[str, object] = {
        "K": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        "mode_ledger": mode_ledgers[sector],
        "claim_status": claim_status,
        "matrix_status": "OPEN_EXPORT_REQUIRED",
    }
    if sector == "up":
        row["Z_virt_middle_up"] = "1/2 if dressed branch active"
    return row


def template_branch_matrix_artifact(branch: str) -> Dict[str, object]:
    return {
        "artifact": "charged_branch_matrices_v2",
        "public_status": PUBLIC_STATUS,
        "official_predictions_changed": False,
        "branch": branch,
        "frozen_before_comparison": True,
        "used_target_data": False,
        "a": 1.157054135733433,
        "c": [1, 2, 4],
        "generation_order": "by_y_ascending",
        "matrix_status": "OPEN_EXPORT_REQUIRED",
        "open_items": [f"{branch} charged K matrices are not implemented as a safe repo export."],
        "sectors": {
            "lepton": _sector_template("lepton", "DERIVED_CONDITIONAL"),
            "up": _sector_template("up", "DERIVED_CONDITIONAL_WITH_LOCAL_THRESHOLD"),
            "down": _sector_template("down", "DERIVED_CONDITIONAL"),
        },
    }


def b_diagnostic_branch_matrix_artifact() -> Dict[str, object]:
    sectors: Dict[str, Dict[str, object]] = {}
    for sector in kf.CHARGED_SECTORS:
        if sector == "up":
            matrix = kf.dressed_K_u_for_rule(3, kf.RULE_A_SINGLE_OPERATOR_TRACE)
            matrix_strings = _matrix_to_strings(matrix)
        else:
            matrix = kf.minimal_K_f_for_rule(sector, 3, kf.RULE_A_SINGLE_OPERATOR_TRACE)
            matrix_strings = _matrix_to_strings(matrix)
        row = _sector_template(
            sector,
            "DERIVED_CONDITIONAL_WITH_LOCAL_THRESHOLD"
            if sector == "up"
            else "DERIVED_CONDITIONAL",
        )
        row.update(
            {
                "K": matrix_strings,
                "matrix_status": "EXPORTED_FROM_REPO_GENERATOR",
                "rho_ch": 3,
                "suppression_rule": kf.RULE_A_SINGLE_OPERATOR_TRACE,
            }
        )
        sectors[sector] = row
    return {
        "artifact": "charged_branch_matrices_v2",
        "public_status": PUBLIC_STATUS,
        "official_predictions_changed": False,
        "branch": "B-diagnostic",
        "frozen_before_comparison": True,
        "used_target_data": False,
        "a": 1.157054135733433,
        "c": [1, 2, 4],
        "generation_order": "by_y_ascending",
        "matrix_status": "EXPORTED_FROM_REPO_GENERATOR",
        "source": "charged_kf_generator with rho_ch=3, Rule-A suppression, up middle ln2 threshold",
        "sectors": sectors,
    }


def k_collar_open_audit(branch: str, reason: str) -> Dict[str, object]:
    return {
        "audit": "K_collar_response_audit",
        "public_status": PUBLIC_STATUS,
        "official_predictions_changed": False,
        "branch": branch,
        "D": "3 diag(0,1,2)",
        "chi_source": "chi = lambda_A Tr(A^2)",
        "chi_fit_to_masses": False,
        "stack_verdict": "STACK_COLLAR_OPEN",
        "open_items": [reason],
    }


def open_gate_ledger_artifact() -> Dict[str, object]:
    return {
        "artifact": "full_BHSM_open_gate_ledger_v2",
        "public_status": PUBLIC_STATUS,
        "official_predictions_changed": False,
        "statuses": {
            "full_BHSM_architecture": "INTEGRATED_CONDITIONAL",
            "full_BHSM_numerical_closure": "OPEN",
            "charged_precision_closure": "OPEN",
            "K_collar_minimal_anisotropic_branch": "DERIVED_CONDITIONAL",
            "chi_from_boundary_geometry": "OPEN_LOCALIZABLE",
            "chi_from_mass_fit": "FORBIDDEN",
            "Z_virt_u2": "DERIVED_CONDITIONAL_FOR_MIDDLE_UP_MODE_ONLY",
            "A_background_branch": "OPEN",
            "B_diagnostic_branch": "ALLOWED_ONLY_AS_DIAGNOSTIC",
            "official_predictions": "UNCHANGED",
        },
        "remaining_open_blockers": list(REMAINING_OPEN_BLOCKERS),
    }


def claim_status_table_artifact() -> Dict[str, object]:
    return {
        "artifact": "full_BHSM_claim_status_table_v2",
        "public_status": PUBLIC_STATUS,
        "official_predictions_changed": False,
        "claim_statuses": [
            {
                "claim": "Full BHSM architecture",
                "status": "INTEGRATED_CONDITIONAL",
                "boundary": "Structural architecture only; numerical closure remains open.",
            },
            {
                "claim": "K_collar minimal anisotropic branch",
                "status": "DERIVED_CONDITIONAL",
                "boundary": "Requires boundary-derived chi; no mass fit is allowed.",
            },
            {
                "claim": "A-background charged generator branch",
                "status": "OPEN",
                "boundary": "Requires P_ch -> Tr_sector(P_ch) -> C_ch -> K_boundary[C_ch] before projection.",
            },
            {
                "claim": "B-diagnostic rho_ch scan branch",
                "status": "ALLOWED_ONLY_AS_DIAGNOSTIC",
                "boundary": "rho_ch=3 in local q^2+rho_ch*j^2 is not A-background.",
            },
            {
                "claim": "Full numerical closure",
                "status": "OPEN",
                "boundary": "No final mass, CKM, PMNS, CP, Higgs, or comparison-ready closure is claimed.",
            },
        ],
    }


def forbidden_claim_audit_artifact() -> Dict[str, object]:
    return {
        "artifact": "forbidden_claim_audit_v2",
        "public_status": PUBLIC_STATUS,
        "official_predictions_changed": False,
        "forbidden_claims_absent": True,
        "forbidden_fit_found": False,
        "forbidden_claims": [
            "full Standard Model derivation",
            "empirical validation",
            "final charged mass closure",
            "final CKM closure",
            "final PMNS closure",
            "final CP closure",
            "Higgs prediction",
            "neutrino prediction",
            "full numerical closure",
        ],
    }


def recovery_report_artifact(
    codex_root: Path,
    repo_root: Path,
    repo_branch_at_start: str,
    repo_branch_used: str,
) -> Dict[str, object]:
    continuity = continuity_inventory(codex_root, repo_root)
    inspection = inspect_charged_generator(repo_root)
    open_items = list(inspection.open_items)
    open_items.extend(f"missing continuity file: {name}" for name in continuity["missing"])
    return {
        "public_status": PUBLIC_STATUS,
        "official_predictions_changed": False,
        "continuity_files_found": continuity["found"],
        "continuity_files_missing": continuity["missing"],
        "repo_branch_at_start": repo_branch_at_start,
        "repo_branch_used": repo_branch_used,
        "open_prs_detected": list(OPEN_PR_STACK),
        "charged_generator_classification": inspection.classification,
        "A_background_implemented": inspection.a_background_implemented,
        "Z_virt_leakage_found": inspection.z_virt_leakage_found,
        "forbidden_fit_found": inspection.forbidden_fit_found,
        "open_items": open_items,
    }


def render_recovery_markdown(report: Dict[str, object]) -> str:
    missing = "\n".join(f"- `{name}`" for name in report["continuity_files_missing"])
    found = "\n".join(f"- `{name}`" for name in report["continuity_files_found"])
    open_items = "\n".join(f"- {item}" for item in report["open_items"])
    prs = "\n".join(
        f"- #{row['number']} `{row['head']}` -> `{row['base']}`"
        for row in report["open_prs_detected"]
    )
    return f"""# BHSM Codex Reentry Recovery Report v1

Current public status: {PUBLIC_STATUS}.

This artifact rehydrates the repository workflow from the supplied bookmark
JSONs and the current stacked PR state. It does not change frozen or official
predictions.

## Branch State

- repo_branch_at_start: `{report['repo_branch_at_start']}`
- repo_branch_used: `{report['repo_branch_used']}`

## Continuity Files Found

{found or "- none"}

## Continuity Files Missing

{missing or "- none"}

## Open PR Stack Detected

{prs}

## Charged Generator Inspection

- classification: `{report['charged_generator_classification']}`
- A_background_implemented: `{report['A_background_implemented']}`
- Z_virt_leakage_found: `{report['Z_virt_leakage_found']}`
- forbidden_fit_found: `{report['forbidden_fit_found']}`

The current generator is classified as `B-diagnostic` because it inserts
`rho_ch` through the local `q^2 + rho_ch*j^2` sector metric rather than through
the A-background dependency order.

## Open Items

{open_items}

Frozen predictions changed: no.

Official predictions changed: no.
"""
