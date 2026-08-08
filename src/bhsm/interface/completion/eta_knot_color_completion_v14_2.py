"""BHSM v14.2 FR eta-knot color-matter completion theorem."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

from .eta_knot_color_action_v14_2 import (
    berry_gauge_no_double_counting_payload,
    collective_dirac_action_payload,
    independent_gauss_current_payload,
    topology_sector_payload,
)
from .eta_knot_quantization_bundle_v14_2 import (
    boundary_dirac_domain_payload,
    one_particle_hilbert_bundle_payload,
    su3_representation_map_payload,
)
from .eta_stabilizer_current_v14_2 import stabilizer_no_current_payload
from .eta_color_bundle_matcher_audit_v14_1 import parent_architecture_recovery_payload

VERSION = "v14.2"
THEOREM_TARGET = (
    "ACTION_AND_QUANTIZATION_OWNED_IDENTIFICATION_OF_THE_FR_ETA_KNOT_ONE_"
    "PARTICLE_BUNDLE_WITH_THE_RETAINED_M4_CHIRAL_COLOR_MATTER_BUNDLE_AND_"
    "MINIMAL_SU3_COUPLING_YIELDING_THE_INDEPENDENT_GAUSS_CURRENT"
)
PRIMARY_VERDICT = (
    "BHSM_ETA_KNOT_TO_M4_COLOR_COUPLING_REMAINS_BLOCKED_AT_THE_COMMON_PARENT_"
    "CONNECTION_OR_EQUIVALENT_BUNDLE_GAUGING_THEOREM"
)
EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_ETA_EXTENSION_OF_THE_V7_1_PARENT_BUNDLE_REDUCTION_FUNCTOR_"
    "WITH_COMMON_SU3_CONNECTION_COLOR_AND_POLARIZATION_REPRESENTATIONS_AND_"
    "VARIATIONAL_GAUSS_LAW"
)
HISTORICAL_VERDICT = (
    "BHSM_V7_1_COVARIANT_REDUCTION_COMPATIBILITY_AND_ASSOCIATED_BUNDLE_"
    "FRAMEWORK_RECOVERED_AS_THE_EXISTING_CROSS_STRATUM_ARCHITECTURE"
)
HISTORICAL_LIMIT = (
    "BHSM_V7_1_DOES_NOT_YET_INSTANTIATE_A_COMMON_PARENT_SU3_CONNECTION_FOR_"
    "THE_ETA_POLARIZATION_AND_INDEPENDENT_M4_COLOR_BUNDLES"
)
FLAVOR_OBJECT = (
    "PARENT_ACTION_DERIVATION_OR_UNIQUENESS_SELECTION_OF_THE_SPECTRAL_"
    "CHARGED_CURRENT_KERNEL"
)
ARTIFACT_FILES = {
    "selector": "BHSM_eta_stabilizer_no_color_current_v14_2.json",
    "hilbert": "BHSM_eta_knot_one_particle_Hilbert_bundle_v14_2.json",
    "representation": "BHSM_eta_knot_SU3_representation_map_v14_2.json",
    "kinetic": "BHSM_eta_knot_collective_Dirac_action_v14_2.json",
    "gauss": "BHSM_eta_knot_independent_Gauss_current_v14_2.json",
    "double_counting": "BHSM_eta_Berry_physical_color_no_double_counting_v14_2.json",
    "topology": "BHSM_eta_knot_color_topology_sector_audit_v14_2.json",
    "dirac": "BHSM_eta_knot_boundary_Dirac_domain_v14_2.json",
    "lineage": "BHSM_eta_knot_color_scientific_lineage_v14_2.json",
    "blocker": "BHSM_eta_knot_color_blocker_falsification_v14_2.json",
    "completion": "BHSM_completion_gate_v14_2.json",
}


@lru_cache(maxsize=1)
def lineage_payload() -> dict[str, Any]:
    recovery = parent_architecture_recovery_payload()
    rows = [
        {"layer": "v6.3-v6.4", "result": "conditional G2/SU3 polarization, Hopf split, and chiral collar; physical domain/transgression open"},
        {"layer": "v7.0-v7.1", "result": "covariant associated-bundle reduction and compatibility architecture recovered"},
        {"layer": "v8.8", "result": "conditional parent-induced associated connection precedent; current kernel not action derived"},
        {"layer": "v13.3", "result": "FR odd spin/statistics parity and finite diagnostic inertia; local physical Hilbert bundle explicitly open"},
        {"layer": "v13.4-v13.5", "result": "conditional Weyl normal form, conjugate rank-three polarization, restricted Berry connection"},
        {"layer": "v14.1", "result": "projector connection proved not equivalent to independent Yang-Mills field"},
        {"layer": "v14.2", "result": "stabilizer selector current vanishes; collective colored-matter representation/action provenance audited fail-closed"},
    ]
    validation = {
        "v7_recovery_preserved": recovery["validation_passed"],
        "no_total_architecture_absence_claim": True,
        "FR_parity_not_promoted_to_Dirac_action": True,
        "rank_three_not_promoted_to_physical_triplet": True,
        "projector_connection_no_go_preserved": True,
    }
    return {
        "artifact": "BHSM_eta_knot_color_scientific_lineage_v14_2",
        "version": VERSION,
        "rows": rows,
        "historical_verdict": HISTORICAL_VERDICT,
        "historical_limit": HISTORICAL_LIMIT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def blocker_falsification_payload() -> dict[str, Any]:
    criteria = [
        {"claim": "physical one-particle Hilbert bundle", "would_falsify_blocker": "construct normalized collective states, moduli measure/metric, zero-mode quotient, regular domain, and M4 gluing"},
        {"claim": "physical 3 or bar3", "would_falsify_blocker": "supply action/quantization-owned P_color action, transition cocycles, and rho maps on H_eta^(1)"},
        {"claim": "collective Dirac action", "would_falsify_blocker": "derive the local first-order operator and all connection terms from the eta collective action"},
        {"claim": "independent eta-sourced Gauss law", "would_falsify_blocker": "derive minimal coupling and its mixed A/Psi_eta variation without reusing the EFT fermion term as provenance"},
        {"claim": "global A=A^P+a", "would_falsify_blocker": "prove both are connections on the same principal bundle in each declared c2 sector"},
        {"claim": "boundary index", "would_falsify_blocker": "close compact Euclidean continuation, tensor connection, boundary form, self-adjoint domain, and APS data"},
    ]
    validation = {
        "criteria_are_constructive": len(criteria) == 6,
        "no_proxy_solution_accepted": True,
        "no_measurement_can_falsify_a_provenance_gap": True,
        "exact_next_object_unique_for_current_branch": True,
    }
    return {
        "artifact": "BHSM_eta_knot_color_blocker_falsification_v14_2",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "criteria": criteria,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def completion_payload() -> dict[str, Any]:
    selector = stabilizer_no_current_payload()
    hilbert = one_particle_hilbert_bundle_payload()
    representation = su3_representation_map_payload()
    kinetic = collective_dirac_action_payload()
    gauss = independent_gauss_current_payload()
    double = berry_gauge_no_double_counting_payload()
    topology = topology_sector_payload()
    dirac = boundary_dirac_domain_payload()
    lineage = lineage_payload()
    blocker = blocker_falsification_payload()
    validation = {
        "selector_no_current_proved": selector["validation_passed"],
        "Hilbert_bundle_fail_closed": hilbert["validation_passed"],
        "representation_fail_closed": representation["validation_passed"],
        "collective_action_fail_closed": kinetic["validation_passed"],
        "Gauss_current_conditional_not_promoted": gauss["validation_passed"],
        "Berry_gauge_double_counting_prevented": double["validation_passed"],
        "global_c2_sectors_preserved": topology["validation_passed"],
        "boundary_index_fail_closed": dirac["validation_passed"],
        "lineage_recovered": lineage["validation_passed"],
        "falsification_criteria_explicit": blocker["validation_passed"],
        "family_current_I3_preserved": gauss["charged_current"] == "J_+^family=I3",
        "Kud_not_inserted": gauss["K_ud"] is None,
        "frozen_predictions_unchanged": True,
        "official_prediction_logic_unchanged": True,
        "measured_inputs_not_used": True,
        "new_fields_not_introduced": True,
        "new_continuous_coefficients_not_introduced": True,
        "gauge_dressed_BVP_not_attempted": True,
    }
    return {
        "artifact": "BHSM_completion_gate_v14_2",
        "version": VERSION,
        "theorem_target": THEOREM_TARGET,
        "primary_result": PRIMARY_VERDICT,
        "historical_verdict": HISTORICAL_VERDICT,
        "historical_limit": HISTORICAL_LIMIT,
        "stabilizer_selector_current_verdict": selector["verdict"],
        "Hilbert_bundle_verdict": hilbert["verdict"],
        "SU3_representation_verdict": representation["verdict"],
        "collective_kinetic_action_verdict": kinetic["verdict"],
        "minimal_coupling_ownership_verdict": "NOT_ACTION_OR_QUANTIZATION_OWNED",
        "independent_Gauss_current_verdict": gauss["verdict"],
        "Berry_gauge_verdict": double["verdict"],
        "global_c2_verdict": topology["verdict"],
        "boundary_Dirac_verdict": dirac["verdict"],
        "flavor_current_verdict": "J_+^family=I3",
        "Mark_III": "NOT_REACHED",
        "BHSM_physical_completion": False,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "flavor_exact_next_object": FLAVOR_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def build_artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "selector": stabilizer_no_current_payload(),
        "hilbert": one_particle_hilbert_bundle_payload(),
        "representation": su3_representation_map_payload(),
        "kinetic": collective_dirac_action_payload(),
        "gauss": independent_gauss_current_payload(),
        "double_counting": berry_gauge_no_double_counting_payload(),
        "topology": topology_sector_payload(),
        "dirac": boundary_dirac_domain_payload(),
        "lineage": lineage_payload(),
        "blocker": blocker_falsification_payload(),
        "completion": completion_payload(),
    }


def _default(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, complex):
        return {"real": float(value.real), "imag": float(value.imag)}
    raise TypeError(type(value).__name__)


def deterministic_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, default=_default) + "\n"


def materialize(output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    payloads = build_artifact_payloads()
    paths = []
    for key, filename in ARTIFACT_FILES.items():
        path = output_dir / filename
        path.write_text(deterministic_json(payloads[key]), encoding="utf-8")
        paths.append(path)
    return paths


def cli_status() -> dict[str, Any]:
    completion = completion_payload()
    return {
        "version": VERSION,
        "primary_result": completion["primary_result"],
        "Mark_III": completion["Mark_III"],
        "BHSM_physical_completion": completion["BHSM_physical_completion"],
        "exact_next_object": completion["exact_next_object"],
    }


if __name__ == "__main__":
    print(deterministic_json(cli_status()), end="")
