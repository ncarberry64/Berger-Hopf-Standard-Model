"""Deterministic v14.36 phase-Hessian completion gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

from .degree_one_phase_hessian_v14_36 import (
    VERSION,
    bifurcation_gate_payload,
    completion_payload,
    positivity_theorem_payload,
    round_smash_spectrum_payload,
)

ARTIFACT_BUILDERS: dict[str, Callable[[], dict[str, Any]]] = {
    "BHSM_Path_B_phase_Hessian_positivity_theorem_v14_36.json": positivity_theorem_payload,
    "BHSM_round_smash_degree_one_phase_spectrum_v14_36.json": round_smash_spectrum_payload,
    "BHSM_flavor_channel_bifurcation_gate_v14_36.json": bifurcation_gate_payload,
    "BHSM_completion_gate_v14_36.json": completion_payload,
}


def deterministic_json(value: Any) -> str:
    def default(item: Any) -> Any:
        if isinstance(item, np.ndarray):
            return item.tolist()
        if isinstance(item, np.generic):
            return item.item()
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
            f"BHSM {VERSION} degree-one phase-Hessian status",
            f"Primary verdict: {payload['primary_verdict']}",
            f"Secondary verdict: {payload['secondary_verdict']}",
            f"Phase Hessian gate: {payload['phase_Hessian_gate']}",
            f"Full Hessian gate: {payload['full_Hessian_gate']}",
            f"BHSM complete: {payload['BHSM_complete']}",
            f"Exact next object: {payload['exact_next_object']}",
        )
    )
