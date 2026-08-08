"""Deterministic v14.34 Hopf-phase flavor materialization and status gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

from .hopf_phase_flavor_cross_gram_v14_34 import (
    completion_payload,
    feshbach_cross_gram_payload,
    frozen_harmonic_ledger_payload,
    multi_harmonic_bridge_payload,
    nonlinear_tower_payload,
    phase_shift_no_go_payload,
    proxy_kill_screen_payload,
)

VERSION = "v14.34"
ARTIFACT_BUILDERS: dict[str, Callable[[], dict[str, Any]]] = {
    "BHSM_frozen_quark_Hopf_imbalance_ledger_v14_34.json": frozen_harmonic_ledger_payload,
    "BHSM_constant_and_single_weight_phase_CKM_no_go_v14_34.json": phase_shift_no_go_payload,
    "BHSM_multi_harmonic_Hopf_bridge_selection_rules_v14_34.json": multi_harmonic_bridge_payload,
    "BHSM_minimal_harmonic_bridge_proxy_kill_screen_v14_34.json": proxy_kill_screen_payload,
    "BHSM_Feshbach_dressed_identity_current_cross_Gram_theorem_v14_34.json": feshbach_cross_gram_payload,
    "BHSM_Hopf_phase_nonlinear_mode_tower_and_stiffness_v14_34.json": nonlinear_tower_payload,
    "BHSM_completion_gate_v14_34.json": completion_payload,
}


def deterministic_json(value: Any) -> str:
    def default(item: Any) -> Any:
        if isinstance(item, np.ndarray):
            if np.iscomplexobj(item):
                return {
                    "real": item.real.tolist(),
                    "imag": item.imag.tolist(),
                }
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
            f"BHSM {VERSION} Hopf-phase flavor status",
            f"Primary verdict: {payload['primary_verdict']}",
            f"Mass hierarchy: {payload['mass_hierarchy_gate']}",
            f"Single phase: {payload['single_weight_bridge_gate']}",
            f"Cross-Gram: {payload['Feshbach_cross_Gram_gate']}",
            f"CKM: {payload['CKM_status']}",
            f"BHSM complete: {payload['BHSM_complete']}",
            f"Exact next object: {payload['exact_next_object']}",
            "Frozen predictions changed: False",
            "Physical outputs emitted: False",
        )
    )
