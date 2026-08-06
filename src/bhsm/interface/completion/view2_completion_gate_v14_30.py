"""Deterministic v14.30 gate after the common-domain eta/SU(3) proof audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

from .common_domain_eta_su3_reduction_v14_30 import (
    bundle_reduction_payload,
    completion_payload as common_domain_completion_payload,
    measure_action_variation_payload,
    uniqueness_payload,
)
from .full_hopf_preimage_effective_action_v14_30 import (
    completion_payload,
    dtn_schur_payload,
    fiber_spectrum_payload,
    low_energy_matching_payload,
    measure_hessian_payload,
    prior_work_recall_payload,
    representation_obstruction_payload,
)
from .view2_completion_gate_v14_29 import all_payloads as v14_29_payloads


VERSION = "v14.30"
ARTIFACT_BUILDERS: dict[str, Callable[[], dict[str, Any]]] = {
    "BHSM_common_domain_eta_SU3_bundle_reduction_audit_v14_30.json": bundle_reduction_payload,
    "BHSM_eta_collar_measure_action_variation_no_go_v14_30.json": measure_action_variation_payload,
    "BHSM_eta_SU3_common_domain_uniqueness_audit_v14_30.json": uniqueness_payload,
    "BHSM_common_domain_completion_gate_v14_30.json": common_domain_completion_payload,
    "BHSM_full_recall_path_composition_audit_v14_30.json": prior_work_recall_payload,
    "BHSM_full_preimage_eta_color_representation_gate_v14_30.json": representation_obstruction_payload,
    "BHSM_eta_full_preimage_fiber_mode_spectrum_v14_30.json": fiber_spectrum_payload,
    "BHSM_full_preimage_measure_parent_eta_hessian_v14_30.json": measure_hessian_payload,
    "BHSM_eta_gauge_covariant_DtN_and_Schur_audit_v14_30.json": dtn_schur_payload,
    "BHSM_v14_29_full_preimage_low_energy_matching_gate_v14_30.json": low_energy_matching_payload,
    "BHSM_completion_gate_v14_30.json": completion_payload,
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
    payloads = v14_29_payloads()
    payloads.update({name: builder() for name, builder in ARTIFACT_BUILDERS.items()})
    return payloads


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
            f"BHSM {VERSION} common-domain eta/SU3 status",
            f"Primary verdict: {payload['primary_verdict']}",
            f"Secondary verdict: {payload['secondary_verdict']}",
            f"BHSM complete: {payload['BHSM_complete']}",
            f"Exact next object: {payload['exact_next_object']}",
            "Frozen predictions changed: False",
            "Physical outputs emitted: False",
        )
    )
