"""Deterministic materialization and CLI report."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from . import coefficients, fields, hessians, measures, reduction, reductions, symmetries, terms, validation, variations
from .common import FROZEN_HASHES, deterministic_json


ARTIFACT_FILES = {
    "master_action": "BHSM_unified_master_action_v7_0.json",
    "master_latex": "BHSM_unified_master_action_latex_v7_0.tex",
    "configuration": "BHSM_master_configuration_space_v7_0.json",
    "bundles": "BHSM_master_field_bundle_ledger_v7_0.json",
    "symmetries": "BHSM_master_symmetry_ledger_v7_0.json",
    "measures": "BHSM_master_measure_orientation_ledger_v7_0.json",
    "coefficients": "BHSM_master_coefficient_input_ledger_v7_0.json",
    "historical": "BHSM_historical_action_reconciliation_v7_0.json",
    "variations": "BHSM_master_variational_equations_v7_0.json",
    "boundary": "BHSM_master_boundary_conditions_v7_0.json",
    "Hessians": "BHSM_master_hessian_operator_map_v7_0.json",
    "sector_reduction": "BHSM_master_sector_reduction_map_v7_0.json",
    "SM_reduction": "BHSM_SM_low_energy_reduction_v7_0.json",
    "recovery": "BHSM_existing_result_recovery_matrix_v7_0.json",
    "double_counting": "BHSM_master_no_double_counting_audit_v7_0.json",
    "code_map": "BHSM_master_action_to_code_map_v7_0.json",
    "obstruction": "BHSM_master_action_obstruction_ledger_v7_0.json",
    "verdict": "BHSM_RB01_closure_verdict_v7_0.json",
    "completion": "BHSM_1_0_completion_gate_update_v7_0.json",
}


def payloads() -> dict[str, dict[str, Any] | str]:
    return {
        "master_action": terms.payload(),
        "master_latex": terms.latex(),
        "configuration": fields.configuration_space_payload(),
        "bundles": fields.bundle_ledger_payload(),
        "symmetries": symmetries.payload(),
        "measures": measures.payload(),
        "coefficients": coefficients.payload(),
        "historical": reductions.historical_payload(),
        "variations": variations.equations_payload(),
        "boundary": variations.boundary_payload(),
        "Hessians": hessians.payload(),
        "sector_reduction": reductions.sector_payload(),
        "SM_reduction": reductions.sm_payload(),
        "recovery": reductions.recovery_payload(),
        "double_counting": validation.no_double_counting_payload(),
        "code_map": validation.code_map_payload(),
        "obstruction": validation.obstruction_payload(),
        "verdict": validation.verdict_payload(),
        "completion": validation.completion_update_payload(),
    }


def artifact_bytes() -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    for key, payload in payloads().items():
        text = payload if isinstance(payload, str) else deterministic_json(payload)
        if not text.endswith("\n"):
            text += "\n"
        result[ARTIFACT_FILES[key]] = text.encode("utf-8")
    return result


def materialize(root: Path) -> list[Path]:
    target = root / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    paths = []
    for filename, content in artifact_bytes().items():
        path = target / filename
        path.write_bytes(content)
        paths.append(path)
    canonical = target / "BHSM_1_0_completion_gate.json"
    from bhsm.interface.claim_input_completion_consistency import (
        canonical_completion_gate_payload,
    )

    canonical.write_bytes(
        deterministic_json(canonical_completion_gate_payload()).encode("utf-8")
    )
    paths.append(canonical)
    return paths


def frozen_file_sha256(path: Path) -> str:
    """Hash legacy frozen text in its declared canonical CRLF form."""

    canonical_lf = path.read_bytes().replace(b"\r\n", b"\n")
    canonical_crlf = canonical_lf.replace(b"\n", b"\r\n")
    return hashlib.sha256(canonical_crlf).hexdigest().upper()


def frozen_hashes_match(root: Path) -> bool:
    return all(
        frozen_file_sha256(root / path) == digest
        for path, digest in FROZEN_HASHES.items()
    )


def status_payload() -> dict[str, Any]:
    return reduction.status_report()


def status_to_markdown(payload: dict[str, Any] | None = None) -> str:
    data = payload or status_payload()
    lines = [
        "# BHSM v7.1 covariant master-action status",
        "",
        f"Architecture: `{data['authoritative_architecture']}`",
        "",
        "## Reduction maps",
        "",
        *[f"- `{name}`: `{formula}`" for name, formula in data["maps"].items()],
        "",
        f"RB-01: `{data['RB01_result']}`.",
        "",
        f"Core: `{data['core_result']}`.",
        "",
        "The physical fiber pushforward is used only on the invariant or "
        "equivariant retained subcategory. The M5 cap action and intrinsic "
        "M4 Standard Model action retain independent stratum ownership and "
        "are linked by covariant compatibility constraints.",
        "",
        "## Completion",
        "",
        f"- Current tier: `{data['current_tier']}`",
        f"- Scale bridge: `{data['scale_bridge']}`",
        f"- Remaining exact object: `{data['remaining_exact_object']}`",
        "",
        f"Verdict: `{data['final_verdict']}`",
        "",
    ]
    return "\n".join(lines)
