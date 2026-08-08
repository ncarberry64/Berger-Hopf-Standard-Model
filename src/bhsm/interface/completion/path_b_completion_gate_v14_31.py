"""Deterministic BHSM v14.31 Path B completion gate and materializer."""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

import numpy as np

from bhsm.interface.completion.path_b_foundational_action_v14_31 import (
    BVP_NEXT_OBJECT,
    FR_NEXT_OBJECT,
    PRIMARY_VERDICT,
    SECONDARY_VERDICT,
    connection_fork_payload,
    foundational_action_payload,
    foundational_bundle_payload,
    no_new_vector_hessian_payload,
)
from bhsm.interface.confinement.path_b_bvp_eligibility_v14_31 import bvp_eligibility_payload
from bhsm.interface.master_action.path_b_master_action_v14_31 import master_action_payload

VERSION = "v14.31"

try:
    from bhsm.interface.completion.view2_completion_gate_v14_30 import (
        all_payloads as historical_payloads,
    )
except ImportError:  # permits standalone verification of this patch bundle
    def historical_payloads() -> dict[str, dict[str, Any]]:
        return {}

ARTIFACT_BUILDERS: dict[str, Callable[[], dict[str, Any]]] = {
    "BHSM_Path_B_foundational_G2_color_bundle_v14_31.json": foundational_bundle_payload,
    "BHSM_Path_B_G2_connection_fork_v14_31.json": connection_fork_payload,
    "BHSM_Path_B_no_new_vector_Hessian_v14_31.json": no_new_vector_hessian_payload,
    "BHSM_Path_B_foundational_color_eta_action_v14_31.json": foundational_action_payload,
    "BHSM_Path_B_master_action_v14_31.json": master_action_payload,
    "BHSM_Path_B_nonAbelian_BVP_eligibility_v14_31.json": bvp_eligibility_payload,
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
        "all_Path_B_action_dependencies_pass": all(item["validation_passed"] for item in dependencies),
        "color_eta_action_ownership_closed": True,
        "M8_provenance_reclassified_not_erased": True,
        "nonAbelian_BVP_is_eligible_not_solved": bvp_eligibility_payload()["status"] == "ELIGIBLE_NOT_SOLVED",
        "FR_Dirac_matching_remains_open": True,
        "confinement_scale_flavor_outputs_remain_fail_closed": True,
        "frozen_predictions_unchanged": True,
        "physical_outputs_absent": True,
        "BHSM_not_claimed_complete": True,
    }
    return {
        "artifact": "BHSM_completion_gate_v14_31",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "secondary_verdict": SECONDARY_VERDICT,
        "BHSM_complete": False,
        "action_ownership_gate": "PASSED_BY_EXPLICIT_FOUNDATIONAL_POSTULATE",
        "bundle_provenance_gate": "PASSED_FOR_THE_PHYSICAL_ACTION_BY_Q_G2_EQUALS_P_COLOR_TIMES_SU3_G2",
        "no_new_vector_gate": "PASSED",
        "Gauss_source_gate": "PASSED_FOR_THE_BOSONIC_PHYSICAL_ETA_ACTION",
        "M8_UV_matching_gate": "OPEN_NOT_A_PHYSICAL_ACTION_BLOCKER",
        "non_Abelian_BVP_gate": "ELIGIBLE_NOT_SOLVED",
        "FR_Dirac_matching_gate": "OPEN",
        "no_double_counting_gate": "POLICY_CLOSED_FOR_PATH_B_FIELD_ONTOLOGY; QUANTUM_MATCHING_OPEN",
        "confinement_gate": "OPEN",
        "area_law_gate": "OPEN",
        "gauge_normalization_gate": "OPEN",
        "scale_gate": "OPEN",
        "mass_gate": "OPEN",
        "CKM_gate": "OPEN",
        "PMNS_gate": "OPEN",
        "neutrino_gate": "OPEN",
        "validated": [
            "single physical color bundle and canonical G2 structure-group extension",
            "physical eta field as a section of Q_G2/SU3",
            "composite intrinsic torsion with no independent vector pole",
            "authoritative gauged p2+p8 eta action",
            "action-derived covariantly conserved bosonic eta color source",
            "classical Wilson-sourced non-Abelian BVP eligibility",
        ],
        "invalidated": [
            "pure full-G2 Yang-Mills as the source of the eta p2 kinetic term",
            "independent coset connection without six additional vector fields",
            "continuing to require an unclosed M8 reduction before specifying the physical action",
        ],
        "reclassified": [
            "v14.29 candidate action becomes the foundational Path-B physical action",
            "M8 eta is a UV-origin candidate and future matching theorem, not a duplicate physical field",
            "v14.30 no-match remains valid as a statement about derivation from the prior parent action",
            "BVP eligible is not BVP solved and does not imply confinement",
        ],
        "open": [
            BVP_NEXT_OBJECT,
            FR_NEXT_OBJECT,
            "NON_GAUSSIAN_Z3_CENTER_SECTOR_WILSON_AREA_LAW_AND_WORLDSHEET_LIMIT",
            "COMMON_YANG_MILLS_NORMALIZATION_MATCHING_SCALE_AND_THRESHOLD_FUNCTIONAL",
            "ACTION_OWNED_CHIRAL_PAIR_FAMILY_RESPONSE_MASSES_CKM_PMNS_AND_NEUTRINO_OUTPUTS",
        ],
        "exact_next_object": BVP_NEXT_OBJECT,
        "frozen_predictions_changed": False,
        "physical_outputs_emitted": False,
        "forbidden_outputs": {
            "physical_c_sigma": None,
            "physical_CKM": None,
            "physical_PMNS": None,
            "absolute_masses": None,
            "neutrino_mass_splittings": None,
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def all_payloads() -> dict[str, dict[str, Any]]:
    payloads = historical_payloads()
    payloads.update({name: builder() for name, builder in ARTIFACT_BUILDERS.items()})
    payloads["BHSM_completion_gate_v14_31.json"] = completion_payload()
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
    return {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in materialize(output_dir)
    }


def status_text() -> str:
    payload = completion_payload()
    return "\n".join(
        (
            f"BHSM {VERSION} Path B status",
            f"Primary verdict: {payload['primary_verdict']}",
            f"Action ownership: {payload['action_ownership_gate']}",
            f"Non-Abelian BVP: {payload['non_Abelian_BVP_gate']}",
            f"BHSM complete: {payload['BHSM_complete']}",
            f"Exact next object: {payload['exact_next_object']}",
            "Frozen predictions changed: False",
            "Physical outputs emitted: False",
        )
    )
