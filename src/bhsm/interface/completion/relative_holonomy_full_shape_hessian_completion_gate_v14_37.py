"""Deterministic v14.37 relative-holonomy/full-shape completion gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

from .relative_holonomy_full_shape_hessian_v14_37 import (
    VERSION,
    completion_payload,
    full_shape_spectrum_payload,
    holonomy_hessian_audit_payload,
    mixed_bifurcation_threshold_payload,
)

ARTIFACT_BUILDERS: dict[str, Callable[[], dict[str, Any]]] = {
    "BHSM_v12_relative_holonomy_Hessian_attachment_audit_v14_37.json": holonomy_hessian_audit_payload,
    "BHSM_degree_one_full_shape_Hessian_spectrum_v14_37.json": full_shape_spectrum_payload,
    "BHSM_joint_eta_attachment_bifurcation_threshold_v14_37.json": mixed_bifurcation_threshold_payload,
    "BHSM_completion_gate_v14_37.json": completion_payload,
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
    paths = []
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
            f"BHSM {VERSION} relative-holonomy/full-shape Hessian status",
            f"Primary verdict: {payload['primary_verdict']}",
            f"Secondary verdict: {payload['secondary_verdict']}",
            f"Holonomy Hessian gate: {payload['v12_holonomy_direct_Hessian_gate']}",
            f"Full-shape surrogate gate: {payload['v13_1_full_shape_surrogate_gate']}",
            f"Mixed Hessian gate: {payload['joint_mixed_Hessian_gate']}",
            f"BHSM complete: {payload['BHSM_complete']}",
            f"Exact next object: {payload['exact_next_object']}",
        )
    )
