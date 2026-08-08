"""Deterministic v14.38 Lambda85/eta mixed-Hessian completion gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

from .lambda85_eta_mixed_hessian_v14_38 import (
    VERSION,
    c3_projection_payload,
    completion_payload,
    lambda85_selection_rule_payload,
    zero_crossing_payload,
)

ARTIFACT_BUILDERS: dict[str, Callable[[], dict[str, Any]]] = {
    "BHSM_Lambda85_eta_mixed_Hessian_selection_rule_v14_38.json": lambda85_selection_rule_payload,
    "BHSM_canonical_C3_attachment_family_chain_no_go_v14_38.json": c3_projection_payload,
    "BHSM_Lambda85_eta_zero_crossing_test_v14_38.json": zero_crossing_payload,
    "BHSM_completion_gate_v14_38.json": completion_payload,
}


def deterministic_json(value: Any) -> str:
    def default(item: Any) -> Any:
        if isinstance(item, np.ndarray):
            return item.tolist()
        if isinstance(item, np.generic):
            return item.item()
        if isinstance(item, complex):
            return {"real": float(item.real), "imag": float(item.imag)}
        raise TypeError(type(item).__name__)

    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, default=default) + "\n"


def all_payloads() -> dict[str, dict[str, Any]]:
    return {name: builder() for name, builder in ARTIFACT_BUILDERS.items()}


def materialize(output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for name, payload in all_payloads().items():
        path = output_dir / name
        path.write_text(deterministic_json(payload), encoding="utf-8", newline="\n")
        paths.append(path)
    return paths


def materialization_hashes(output_dir: Path) -> dict[str, str]:
    return {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in materialize(output_dir)}


def status_text() -> str:
    payload = completion_payload()
    return "\n".join(
        (
            f"BHSM {VERSION} Lambda85/eta mixed-Hessian status",
            f"Primary verdict: {payload['primary_verdict']}",
            f"Secondary verdict: {payload['secondary_verdict']}",
            f"Lambda85 mixed gate: {payload['Lambda85_reduced_mixed_Hessian_gate']}",
            f"C3 family-chain gate: {payload['canonical_C3_family_chain_gate']}",
            f"Spin4 gate: {payload['Spin4_mixed_Hessian_gate']}",
            f"Bifurcation: {payload['bifurcation_status']}",
            f"BHSM complete: {payload['BHSM_complete']}",
            f"Exact next object: {payload['exact_next_object']}",
        )
    )
