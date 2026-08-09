"""Deterministic v14.35 Hopf-phase bifurcation materialization gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

from .hopf_phase_bifurcation_cp_v14_35 import (
    action_selection_payload,
    completion_payload,
    minimal_texture_payload,
    nonlinear_tower_payload,
    phase_locking_payload,
    relative_holonomy_payload,
)

VERSION = "v14.35"
ARTIFACT_BUILDERS: dict[str, Callable[[], dict[str, Any]]] = {
    "BHSM_minimal_Hopf_phase_mixing_and_CP_textures_v14_35.json": minimal_texture_payload,
    "BHSM_Hopf_phase_CP_resonance_and_locking_v14_35.json": phase_locking_payload,
    "BHSM_Path_B_nonaxisymmetric_bifurcation_gate_v14_35.json": action_selection_payload,
    "BHSM_Hopf_phase_texture_nonlinear_tower_gate_v14_35.json": nonlinear_tower_payload,
    "BHSM_v12_relative_holonomy_to_v14_35_phase_texture_ledger.json": relative_holonomy_payload,
    "BHSM_completion_gate_v14_35.json": completion_payload,
}


def deterministic_json(value: Any) -> str:
    def default(item: Any) -> Any:
        if isinstance(item, np.ndarray):
            if np.iscomplexobj(item):
                return {"real": item.real.tolist(), "imag": item.imag.tolist()}
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
            f"BHSM {VERSION} Hopf-phase bifurcation status",
            f"Primary verdict: {payload['primary_verdict']}",
            f"Minimal texture: {payload['minimal_texture_gate']}",
            f"CP phase: {payload['CP_phase_gate']}",
            f"Branch: {payload['nonaxisymmetric_branch_gate']}",
            f"Tower: {payload['tower_gate']}",
            f"CKM: {payload['CKM_status']}",
            f"BHSM complete: {payload['BHSM_complete']}",
            f"Exact next object: {payload['exact_next_object']}",
            "Frozen predictions changed: False",
            "Physical outputs emitted: False",
        )
    )
