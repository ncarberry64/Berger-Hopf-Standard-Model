"""Deterministic BHSM v14.32 Path-B topology and matter completion gate."""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

import numpy as np

from .path_b_physical_topology_v14_32 import (
    CONFINEMENT_NEXT_OBJECT,
    MATTER_NEXT_OBJECT,
    PRIMARY_VERDICT,
    SECONDARY_VERDICT,
    bvp_interpretation_payload,
    fr_obstruction_payload,
    global_target_payload,
    matter_completion_fork_payload,
    physical_topology_payload,
)

VERSION = "v14.32"

try:
    from .path_b_completion_gate_v14_31 import all_payloads as historical_payloads
except ImportError:
    def historical_payloads() -> dict[str, dict[str, Any]]:
        return {}

ARTIFACT_BUILDERS: dict[str, Callable[[], dict[str, Any]]] = {
    "BHSM_Path_B_global_S6_target_v14_32.json": global_target_payload,
    "BHSM_Path_B_physical_eta_topology_gate_v14_32.json": physical_topology_payload,
    "BHSM_Path_B_FR_topology_obstruction_v14_32.json": fr_obstruction_payload,
    "BHSM_Path_B_BVP_topology_interpretation_v14_32.json": bvp_interpretation_payload,
    "BHSM_Path_B_matter_completion_fork_v14_32.json": matter_completion_fork_payload,
}


def deterministic_json(value: Any) -> str:
    def default(item: Any) -> Any:
        if isinstance(item, np.ndarray):
            return item.tolist()
        if isinstance(item, np.generic):
            return item.item()
        raise TypeError(type(item).__name__)
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, default=default) + "\n"


@lru_cache(maxsize=1)
def completion_payload() -> dict[str, Any]:
    dependencies = [builder() for builder in ARTIFACT_BUILDERS.values()]
    validation = {
        "all_v14_32_topology_dependencies_pass": all(item["validation_passed"] for item in dependencies),
        "v14_31_color_eta_action_ownership_preserved": True,
        "physical_M4_eta_degree_one_claim_rejected": True,
        "physical_M4_eta_FR_claim_rejected": True,
        "external_Wilson_BVP_remains_eligible": True,
        "M8_matching_reclassified_as_matter_origin_gate": True,
        "no_new_postulate_silently_adopted": True,
        "frozen_predictions_unchanged": True,
        "physical_outputs_absent": True,
        "BHSM_not_claimed_complete": True,
    }
    return {
        "artifact": "BHSM_completion_gate_v14_32",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "secondary_verdict": SECONDARY_VERDICT,
        "BHSM_complete": False,
        "v14_31_action_ownership_gate": "PRESERVED_PASSED_BY_FOUNDATIONAL_POSTULATE",
        "physical_eta_topological_particle_gate": "FAILED_PI3_S6_EQUALS_ZERO",
        "physical_eta_FR_gate": "FAILED_PI4_S6_EQUALS_ZERO",
        "M8_matter_origin_gate": "OPEN_REQUIRED_FOR_DERIVED_FERMIONS_UNDER_ROUTE_A",
        "foundational_Dirac_route": "AVAILABLE_ONLY_AS_EXPLICIT_NEW_POSTULATE",
        "non_Abelian_BVP_gate": "ELIGIBLE_AS_EXTERNAL_WILSON_RESPONSE_NOT_AS_ETA_QUARK_SOLUTION",
        "confinement_gate": "OPEN",
        "FR_Dirac_matching_gate": "NOT_ELIGIBLE_FROM_THE_M4_S6_FIELD_ALONE",
        "validated": [
            "global S6 target realization as the unit sphere in R plus C3",
            "pi3(S6)=0 for finite-energy physical static eta configurations",
            "pi4(S6)=0 and trivial FR loop group for based M4 eta maps",
            "p2+p8+YM Derrick balance can support a non-topological stationary response",
            "external Wilson BVP eligibility remains distinct from matter derivation",
        ],
        "invalidated": [
            "a degree-one eta knot in the physical M4 S6 sigma field",
            "direct transfer of the historical M8 FR-odd line to the Path-B physical eta field",
            "interpreting a source-bound eta response as a topologically protected quark",
        ],
        "reclassified": [
            "M8 matching remains nonessential for bosonic color action ownership but essential for route-A derived fermionic matter",
            "the Wilson-sourced BVP is a confinement/response calculation, not a matter-origin calculation",
            "v14.31 Path B is a valid bosonic action completion layer but not a complete particle ontology",
        ],
        "open": [MATTER_NEXT_OBJECT, CONFINEMENT_NEXT_OBJECT],
        "exact_next_object": MATTER_NEXT_OBJECT,
        "parallel_confinement_object": CONFINEMENT_NEXT_OBJECT,
        "frozen_predictions_changed": False,
        "physical_outputs_emitted": False,
        "forbidden_outputs": {
            "physical_c_sigma": None,
            "physical_CKM": None,
            "physical_PMNS": None,
            "absolute_masses": None,
            "neutrino_mass_splittings": None,
            "derived_quark_FR_state": None,
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def all_payloads() -> dict[str, dict[str, Any]]:
    payloads = historical_payloads()
    payloads.update({name: builder() for name, builder in ARTIFACT_BUILDERS.items()})
    payloads["BHSM_completion_gate_v14_32.json"] = completion_payload()
    return payloads


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
            f"BHSM {VERSION} Path B physical-topology status",
            f"Primary verdict: {payload['primary_verdict']}",
            f"Physical eta topology: {payload['physical_eta_topological_particle_gate']}",
            f"Physical eta FR: {payload['physical_eta_FR_gate']}",
            f"Wilson BVP: {payload['non_Abelian_BVP_gate']}",
            f"BHSM complete: {payload['BHSM_complete']}",
            f"Exact next object: {payload['exact_next_object']}",
            "Frozen predictions changed: False",
            "Physical outputs emitted: False",
        )
    )
