"""Deterministic materialization and CLI report."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from . import coefficients, fields, hessians, measures, reductions, symmetries, terms, validation, variations
from .common import FROZEN_HASHES, MISSING_OBJECT, VERDICT, VERSION, deterministic_json


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
    canonical.write_bytes(
        deterministic_json(validation.canonical_completion_gate_payload()).encode("utf-8")
    )
    paths.append(canonical)
    return paths


def frozen_hashes_match(root: Path) -> bool:
    return all(
        hashlib.sha256((root / path).read_bytes()).hexdigest().upper() == digest
        for path, digest in FROZEN_HASHES.items()
    )


def status_payload() -> dict[str, Any]:
    checks = validation.validate_model()
    return {
        "version": VERSION,
        "action_levels": ["S8_PROVISIONAL", "S5_TWO_CAP_RELATIVE", "S4_EFFECTIVE"],
        "action_terms": [r["term_id"] for r in terms.term_rows()],
        "coefficient_types": {
            r["coefficient_id"]: r["classification"] for r in coefficients.rows()
        },
        "attached_sectors": [r["sector"] for r in reductions.sector_rows()],
        "unresolved_sources": [MISSING_OBJECT, "ONE_UNIVERSAL_PHYSICAL_SCALE"],
        "low_energy_reduction": reductions.sm_payload()["relation_status"],
        "RB01_verdict": VERDICT,
        "completion_impact": "Tier A remains blocked; Tier B/C not eligible.",
        "validation": checks,
        "validation_passed": all(checks.values()),
    }


def status_to_markdown(payload: dict[str, Any] | None = None) -> str:
    data = payload or status_payload()
    lines = [
        "# BHSM v7.0 master-action status",
        "",
        f"Verdict: `{data['RB01_verdict']}`",
        "",
        "## Action architecture",
        "",
        "`S8 --R_8to5--> S5|4 --R_5to4--> S4eff`",
        "",
        "The three levelwise actions are explicit. The covariant reduction "
        "functor supplying both arrows is not sourced, so this is a maximal "
        "action complex rather than a closed unified parent action.",
        "",
        "## Attached sectors",
        "",
    ]
    lines.extend(f"- {sector}" for sector in data["attached_sectors"])
    lines.extend(
        [
            "",
            "## Unresolved sources",
            "",
            *[f"- `{item}`" for item in data["unresolved_sources"]],
            "",
            "## Completion impact",
            "",
            data["completion_impact"],
            "",
        ]
    )
    return "\n".join(lines)
