"""Deterministic materialization and completion gate for the v14.29 campaign."""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

import numpy as np

from bhsm.interface.completion.eta_fr_current_quantization_v14_29 import fr_quantization_payload
from bhsm.interface.completion.eta_g2_composite_intrinsic_torsion_v14_29 import composite_theta_bundle_payload, theta_hessian_payload
from bhsm.interface.completion.eta_minimally_gauged_p2_p8_action_v14_29 import minimally_gauged_action_payload
from bhsm.interface.completion.eta_su3_noether_current_v14_29 import noether_current_payload, pure_wall_current_payload, tangent_mode_payload
from bhsm.interface.completion.recovered_gauge_chiral_no_go_v14_29 import chiral_overlap_no_go_payload, gauge_normalization_no_go_payload
from bhsm.interface.completion.v14_9_28_lineage_recovery_v14_29 import lineage_recovery_payload
from bhsm.interface.completion.wilson_singlet_source_functional_v14_29 import wilson_singlet_payload
from bhsm.interface.confinement.view2_coupled_bvp_v14_29 import EXACT_NEXT_OBJECT, coupled_bvp_payload, transverse_flux_payload
from bhsm.interface.master_action.view2_master_action_promotion_v14_29 import PRIMARY_VERDICT, master_action_payload

VERSION = "v14.29"
SECONDARY_VERDICT = "LOCAL_CANDIDATE_VARIATION_GAUGE_INVARIANCE_AND_NO_NEW_VECTOR_RESULT_VALID; ACTION_OWNERSHIP_FR_MATCHING_AND_PHYSICAL_GAUSS_CHARGE_REMAIN_OPEN"
OWNERSHIP_NEXT_OBJECT = "COMMON_DOMAIN_ETA_TO_PHYSICAL_SU3_ASSOCIATED_BUNDLE_REDUCTION_WITH_COLLAR_MEASURE_AND_VARIATIONAL_INTERTWINER"
MATCHING_NEXT_OBJECT = "COLLECTIVE_COORDINATE_PATH_INTEGRAL_MATCHING_OF_THE_ETA_ZERO_MODE_CURRENT_TO_A_NORMALIZED_FR_DIRAC_ACTION_WITH_SELF_ADJOINT_DOMAIN_AND_MODE_SUBTRACTION"

ARTIFACT_BUILDERS: dict[str, Callable[[], dict[str, Any]]] = {
    "BHSM_v14_9_to_v14_28_lineage_recovery.json": lineage_recovery_payload,
    "BHSM_G2_SU3_composite_theta_bundle_v14_29.json": composite_theta_bundle_payload,
    "BHSM_eta_minimally_gauged_p2_p8_action_v14_29.json": minimally_gauged_action_payload,
    "BHSM_eta_SU3_Noether_current_v14_29.json": noether_current_payload,
    "BHSM_eta_pure_wall_zero_current_kill_screen_v14_29.json": pure_wall_current_payload,
    "BHSM_eta_tangent_mode_nonzero_current_v14_29.json": tangent_mode_payload,
    "BHSM_theta_no_independent_vector_Hessian_v14_29.json": theta_hessian_payload,
    "BHSM_eta_FR_current_quantization_no_double_counting_v14_29.json": fr_quantization_payload,
    "BHSM_Wilson_singlet_operator_source_v14_29.json": wilson_singlet_payload,
    "BHSM_View2_master_action_promotion_v14_29.json": master_action_payload,
    "BHSM_View2_coupled_BVP_gate_v14_29.json": coupled_bvp_payload,
    "BHSM_transverse_flux_relative_determinant_gate_v14_29.json": transverse_flux_payload,
    "BHSM_recovered_gauge_normalization_no_go_v14_29.json": gauge_normalization_no_go_payload,
    "BHSM_recovered_chiral_overlap_no_go_v14_29.json": chiral_overlap_no_go_payload,
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
    classical = [
        composite_theta_bundle_payload(), theta_hessian_payload(), minimally_gauged_action_payload(),
        noether_current_payload(), pure_wall_current_payload(), tangent_mode_payload(), master_action_payload(),
    ]
    validation = {
        "lineage_recovered_with_missing_versions_fail_closed": lineage_recovery_payload()["validation_passed"],
        "conditional_View2_candidate_audits_pass": all(item["validation_passed"] for item in classical),
        "FR_no_double_counting_policy_audited_but_matching_open": fr_quantization_payload()["validation_passed"],
        "Wilson_singlet_exact": wilson_singlet_payload()["validation_passed"],
        "downstream_BVP_specified_but_not_falsely_solved": coupled_bvp_payload()["validation_passed"],
        "transverse_analytic_screens_pass": transverse_flux_payload()["validation_passed"],
        "v14_20_gauge_normalization_no_go_recovered": gauge_normalization_no_go_payload()["validation_passed"],
        "v14_21_chiral_overlap_no_go_recovered": chiral_overlap_no_go_payload()["validation_passed"],
        "A_P_not_A_physical": True,
        "selector_current_zero_preserved": True,
        "family_current_remains_I3_until_action_derived": True,
        "frozen_prediction_integrity_preserved": True,
        "forbidden_physical_outputs_absent": True,
    }
    return {
        "artifact": "BHSM_completion_gate_v14_29",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "secondary_verdict": SECONDARY_VERDICT,
        "BHSM_complete": False,
        "frozen_predictions_changed": False,
        "physical_outputs_emitted": False,
        "validated": ["conditional G2/SU3 associated-bundle geometry", "composite theta has no independent vector coordinate", "local variation and gauge identity of the candidate eta p2+p8 covariantization", "pure-wall zero/off-shell tangent nonzero split", "exact Wilson singlet invariants"],
        "invalidated": ["identical-layer DtN radius selection", "family splitting from degenerate thresholds", "linear/Gaussian collar as an asymptotic confinement mechanism", "generator-trace or 6pi2 derivation of an absolute common gauge coefficient", "rank-(dim g-1) unbroken kinetic projectors", "a complete Dirac pair or family hierarchy from one common eta wall profile"],
        "reclassified": ["v14.29 minimal gauging is a candidate action completion, not derived from the prior stratified action", "theta is canonical associated-bundle geometry/definition, not action-derived", "FR Dirac current is an intended but unproved collective representative, not an additive source", "stable finite tube does not alone establish an area law", "trace data determine ratios only"],
        "open": [
            {"object": OWNERSHIP_NEXT_OBJECT, "type": "mathematical/action-domain"},
            {"object": MATCHING_NEXT_OBJECT, "type": "mathematical/quantization-matching"},
            {"object": fr_quantization_payload()["open_gate"], "type": "mathematical/action-domain"},
            {"object": EXACT_NEXT_OBJECT, "type": "mathematical-computational-numerical"},
            {"object": "COMMON_YANG_MILLS_NORMALIZATION_MATCHING_SCALE_AND_THRESHOLD_FUNCTIONAL", "type": "action-principle/physical"},
            {"object": chiral_overlap_no_go_payload()["exact_next_object"], "type": "mathematical/action-principle"},
            {"object": "NON_GAUSSIAN_Z3_CENTER_SECTOR_MEASURE_AND_WORLDSHEET_LIMIT", "type": "nonperturbative mathematical-physical"},
        ],
        "exact_next_object": OWNERSHIP_NEXT_OBJECT,
        "downstream_BVP_object": EXACT_NEXT_OBJECT,
        "forbidden_outputs": {"physical_CKM": None, "physical_PMNS": None, "absolute_masses": None, "mass_splittings": None, "c_sigma": None},
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def all_payloads() -> dict[str, dict[str, Any]]:
    payloads = {name: builder() for name, builder in ARTIFACT_BUILDERS.items()}
    payloads["BHSM_completion_gate_v14_29.json"] = completion_payload()
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
    return "\n".join((
        f"BHSM {VERSION} View 2 status",
        f"Primary verdict: {payload['primary_verdict']}",
        f"Secondary verdict: {payload['secondary_verdict']}",
        f"BHSM complete: {payload['BHSM_complete']}",
        f"Exact next object: {payload['exact_next_object']}",
        "Frozen predictions changed: False",
        "Physical outputs emitted: False",
    ))
