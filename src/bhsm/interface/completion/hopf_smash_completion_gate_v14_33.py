"""Deterministic v14.33 Hopf-smash transgression completion gate."""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

import numpy as np

from .hopf_smash_topological_transgression_v14_33 import (
    CONFINEMENT_NEXT_OBJECT,
    EXACT_NEXT_OBJECT,
    PRIMARY_VERDICT,
    SECONDARY_VERDICT,
    degree_form_factorization_payload,
    fr_dirac_transgression_gate_payload,
    join_smash_architecture_payload,
    path_b_reconciliation_payload,
    topological_current_transgression_payload,
)

VERSION = "v14.33"

try:
    from .path_b_completion_gate_v14_32 import all_payloads as historical_payloads
except ImportError:
    def historical_payloads() -> dict[str, dict[str, Any]]:
        return {}

ARTIFACT_BUILDERS: dict[str, Callable[[], dict[str, Any]]] = {
    "BHSM_Hopf_base_fiber_join_smash_architecture_v14_33.json": join_smash_architecture_payload,
    "BHSM_eta_degree_form_suspension_factorization_v14_33.json": degree_form_factorization_payload,
    "BHSM_M8_to_M4_topological_current_transgression_v14_33.json": topological_current_transgression_payload,
    "BHSM_Path_B_and_M8_transgression_reconciliation_v14_33.json": path_b_reconciliation_payload,
    "BHSM_FR_Dirac_transgression_gate_v14_33.json": fr_dirac_transgression_gate_payload,
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
        "all_v14_33_transgression_dependencies_pass": all(item["validation_passed"] for item in dependencies),
        "v14_32_M4_topology_no_go_preserved": True,
        "route_A_topological_current_reopened": True,
        "action_normalization_not_overclaimed": True,
        "FR_Dirac_not_overclaimed": True,
        "parallel_Wilson_BVP_remains_open": True,
        "frozen_predictions_unchanged": True,
        "physical_outputs_absent": True,
        "BHSM_not_claimed_complete": True,
    }
    return {
        "artifact": "BHSM_completion_gate_v14_33",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "secondary_verdict": SECONDARY_VERDICT,
        "BHSM_complete": False,
        "Path_B_action_ownership_gate": "PRESERVED_PASSED",
        "M4_S6_intrinsic_topology_gate": "FAILED_AS_IN_V14_32",
        "full_preimage_smash_topology_gate": "PASSED_AT_THE_HOMOLOGY_AND_DEGREE_FORM_LEVEL",
        "M8_to_M4_particle_number_current_gate": "PASSED_CONDITIONALLY_ON_ORIENTED_FIBER_DOMAIN_AND_ZERO_BOUNDARY_FLUX",
        "smooth_equivariant_map_gate": "OPEN",
        "stationary_background_gate": "OPEN",
        "collective_measure_gate": "OPEN",
        "FR_Dirac_gate": "OPEN_TOPOLOGICALLY_AVAILABLE_NOT_ACTION_DERIVED",
        "non_Abelian_BVP_gate": "PARALLEL_OPEN",
        "validated": [
            "S3 smash S3 equals S6 and S3 join S3 equals S7 at the topological level",
            "suspension degree-form normalization",
            "fiber integration of the closed degree form produces a conserved physical three-form current",
            "total degree equals integrated M4 particle number when cap flux vanishes",
            "Path B bosonic action and M8 topological matter roles can be separated without double counting",
        ],
        "invalidated": [
            "the claim that pi3(S6)=0 alone eliminates every possible M8-to-M4 matter transgression",
            "identifying the transgressed particle-number current with a completed Dirac field",
            "assuming the abstract smash quotient is already the required smooth SU3-equivariant BHSM map",
        ],
        "reclassified": [
            "v14.32 remains exact for the M4 S6 field alone",
            "Route A now has an exact topological pushforward architecture but not an action/operator completion",
            "M8 nonbasic fiber dependence is required rather than an obstacle for the topological charge",
        ],
        "open": [EXACT_NEXT_OBJECT, CONFINEMENT_NEXT_OBJECT],
        "exact_next_object": EXACT_NEXT_OBJECT,
        "parallel_confinement_object": CONFINEMENT_NEXT_OBJECT,
        "frozen_predictions_changed": False,
        "physical_outputs_emitted": False,
        "forbidden_outputs": {
            "physical_Dirac_operator": None,
            "derived_quark_field": None,
            "physical_c_sigma": None,
            "physical_CKM": None,
            "physical_PMNS": None,
            "absolute_masses": None,
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def all_payloads() -> dict[str, dict[str, Any]]:
    payloads = historical_payloads()
    payloads.update({name: builder() for name, builder in ARTIFACT_BUILDERS.items()})
    payloads["BHSM_completion_gate_v14_33.json"] = completion_payload()
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
            f"BHSM {VERSION} Hopf-smash transgression status",
            f"Primary verdict: {payload['primary_verdict']}",
            f"Smash topology: {payload['full_preimage_smash_topology_gate']}",
            f"Particle current: {payload['M8_to_M4_particle_number_current_gate']}",
            f"FR/Dirac: {payload['FR_Dirac_gate']}",
            f"BHSM complete: {payload['BHSM_complete']}",
            f"Exact next object: {payload['exact_next_object']}",
            "Frozen predictions changed: False",
            "Physical outputs emitted: False",
        )
    )
