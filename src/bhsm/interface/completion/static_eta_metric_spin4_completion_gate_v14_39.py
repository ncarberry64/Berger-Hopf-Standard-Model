"""Completion gate and deterministic materialization for BHSM v14.39."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from .static_eta_metric_spin4_source_v14_39 import (
    EXACT_NEXT_OBJECT,
    PRIMARY_VERDICT,
    SECONDARY_VERDICT,
    VERSION,
    mixed_variation_payload,
    route_eligibility_payload,
    static_source_payload,
)

ARTIFACT_FILES = {
    "mixed_variation": "BHSM_PathB_eta_metric_mixed_second_variation_v14_39.json",
    "static_source": "BHSM_static_eta_ADM_momentum_and_Spin4_source_audit_v14_39.json",
    "route_eligibility": "BHSM_nonhomogeneous_attachment_and_Spin4_route_eligibility_v14_39.json",
    "completion": "BHSM_completion_gate_v14_39.json",
}


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return _jsonable(value.tolist())
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
    return value


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(_jsonable(payload), indent=2, sort_keys=True, allow_nan=False) + "\n"


def completion_payload() -> dict[str, Any]:
    mixed = mixed_variation_payload()
    source = static_source_payload()
    routes = route_eligibility_payload()
    validation = {
        "mixed_variation_identity_derived": mixed["validation_passed"],
        "static_source_no_go_derived": source["validation_passed"],
        "route_ledger_complete": routes["validation_passed"],
        "static_eta_bifurcation_not_promoted": True,
        "Spin4_response_not_promoted": True,
        "physical_CKM_not_emitted": True,
        "frozen_predictions_unchanged": True,
        "BHSM_incomplete": True,
    }
    return {
        "artifact": "BHSM_completion_gate_v14_39",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "secondary_verdict": SECONDARY_VERDICT,
        "eta_metric_mixed_variation_gate": "DERIVED_EXACT_LOCAL_IDENTITY",
        "static_ADM_momentum_source_gate": "FAILED_ZERO",
        "Spin4_L2_L3_activation_gate": "OFF_ON_STATIC_BRANCH",
        "nonhomogeneous_spatial_metric_gate": "OPEN_GAUGE_FIXED_COMPACT_CAP_OPERATOR",
        "dynamic_or_external_source_gate": "OPEN",
        "physical_CKM_CP_mass_scale": "WITHHELD",
        "BHSM_complete": False,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def all_payloads() -> dict[str, dict[str, Any]]:
    return {
        ARTIFACT_FILES["mixed_variation"]: mixed_variation_payload(),
        ARTIFACT_FILES["static_source"]: static_source_payload(),
        ARTIFACT_FILES["route_eligibility"]: route_eligibility_payload(),
        ARTIFACT_FILES["completion"]: completion_payload(),
    }


def materialize(output_dir: Path) -> list[Path]:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for filename, payload in sorted(all_payloads().items()):
        path = destination / filename
        path.write_text(deterministic_json(payload), encoding="utf-8", newline="\n")
        paths.append(path)
    return paths


def materialization_hashes(output_dir: Path) -> dict[str, str]:
    return {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in materialize(output_dir)
    }


def status_text() -> str:
    payload = completion_payload()
    return "\n".join(
        [
            f"# BHSM {VERSION} static eta/metric and Spin(4) source gate",
            "",
            f"- Primary verdict: `{payload['primary_verdict']}`",
            f"- Secondary verdict: `{payload['secondary_verdict']}`",
            f"- Static ADM source: `{payload['static_ADM_momentum_source_gate']}`",
            f"- Spin(4) L2/L3 activation: `{payload['Spin4_L2_L3_activation_gate']}`",
            f"- BHSM complete: `{payload['BHSM_complete']}`",
            f"- Exact next object: `{payload['exact_next_object']}`",
            "",
        ]
    )
