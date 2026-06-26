from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List

import boundary_relative_holonomy_cp as cp
import ckm_structural_source as ckm
import common_scale_transport_closure_audit as transport_gate
import neutral_parameter_closure_audit as neutral_gate
import tau_sigma_numerical_gate_closure as tau_gate


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"

ALLOWED_GATE_STATUSES = {
    "OPEN_LOCALIZABLE",
    "BLOCKED_BY_TAU_SIGMA_BOUNDARY_DERIVATION",
    "BLOCKED_BY_MISSING_TRANSPORT_OBJECTS",
    "STRONGLY_SUPPORTED_CANDIDATE",
    "PMNS_BLOCKED_BY_NEUTRAL_OPERATOR_OPEN",
    "CKM_BLOCKED_BY_UP_OPERATOR_OPEN",
    "CP_NUMERICAL_CLOSURE_OPEN",
    "BLOCKED_BY_MISSING_OBJECTS",
    "MOCK_OR_SCAFFOLD_ONLY",
}


def _unique(items: Iterable[str]) -> List[str]:
    out: List[str] = []
    for item in items:
        if item not in out:
            out.append(item)
    return out


def charged_outputs_gate(tau_artifact: Dict[str, object]) -> Dict[str, object]:
    missing = list(tau_artifact.get("missing_objects", []))
    return {
        "attempted": True,
        "closed": False,
        "status": "BLOCKED_BY_TAU_SIGMA_BOUNDARY_DERIVATION",
        "missing_objects": missing,
        "public_status_before_gate": PUBLIC_STATUS,
        "official_predictions_changed": False,
        "tau_source": None,
        "tau_fit_to_masses": False,
        "sigma_fit_to_masses": False,
        "observed_masses_used": False,
        "target_ratios_used": False,
        "obstruction": "Boundary-derived tau is unavailable, so no charged output can be frozen at boundary tau.",
    }


def pmns_gate(neutral_artifact: Dict[str, object]) -> Dict[str, object]:
    return {
        "attempted": True,
        "closed": False,
        "status": "PMNS_BLOCKED_BY_NEUTRAL_OPERATOR_OPEN",
        "official_predictions_changed": False,
        "empirical_derivation_inputs_used": False,
        "missing_objects": [
            "neutral operator final derivation",
            "neutral threshold rules",
            "charged lepton operator at boundary-derived tau",
        ],
        "source_trace": neutral_artifact.get("source_trace", {}),
    }


def ckm_gate() -> Dict[str, object]:
    diag = ckm.diagnostic()
    return {
        "attempted": True,
        "closed": False,
        "status": "CKM_BLOCKED_BY_UP_OPERATOR_OPEN",
        "official_predictions_changed": False,
        "empirical_derivation_inputs_used": False,
        "structural_source_status": ckm.STATUS_TABLE["CKM_structural_source"],
        "diagnostic": {
            "down_cost_difference": diag.down_cost_difference,
            "up_threshold_gap_label": diag.up_threshold_gap_label,
            "theta_12_u_label": diag.theta_12_u_label,
        },
        "missing_objects": [
            "final up/down charged operators at boundary-derived tau",
            "CKM numerical lock",
            "common-scale transport population",
        ],
    }


def cp_gate() -> Dict[str, object]:
    diag = cp.diagnostic()
    return {
        "attempted": True,
        "closed": False,
        "status": "CP_NUMERICAL_CLOSURE_OPEN",
        "official_predictions_changed": False,
        "empirical_derivation_inputs_used": False,
        "CP_holonomy_source": cp.STATUS_TABLE["boundary_relative_holonomy_CP_source"],
        "diagnostic": {
            "relative_holonomy": diag.relative_holonomy,
            "primitive_phase": diag.primitive_phase,
            "nontrivial": diag.nontrivial,
        },
        "missing_objects": [
            "derived phase-to-CKM/PMNS operator map",
            "closed CKM operator",
            "closed PMNS operator",
        ],
    }


def higgs_ew_gate(tau_artifact: Dict[str, object]) -> Dict[str, object]:
    return {
        "attempted": True,
        "closed": False,
        "status": "BLOCKED_BY_MISSING_OBJECTS",
        "official_predictions_changed": False,
        "empirical_derivation_inputs_used": False,
        "missing_objects": _unique(
            [
                "Z_H",
                "v_BH",
                "V_eff''",
                "Lambda_BH",
                "Xi_i",
                "sin2_theta_W derivation",
                "v_EW derivation",
                "m_h derivation",
            ]
            + list(tau_artifact.get("missing_objects", []))
        ),
    }


def cosmology_desi_gate() -> Dict[str, object]:
    return {
        "attempted": True,
        "closed": False,
        "status": "MOCK_OR_SCAFFOLD_ONLY",
        "official_predictions_changed": False,
        "actual_DESI_data_used": False,
        "DESI_validation_claimed": False,
        "empirical_derivation_inputs_used": False,
        "constants": {
            "alpha_inverse": 137.035999,
            "a": "alpha_inverse/(12*pi^2)",
            "S": "1/(4*pi)",
            "R_H_Gpc": 24.0,
        },
        "missing_objects": ["actual DESI directional anisotropy data", "pre-registered comparison statistic"],
    }


def _gate_row(status: str, missing_objects: Iterable[str] = ()) -> Dict[str, object]:
    return {
        "attempted": True,
        "closed": status in {"DERIVED_CONDITIONAL", "CLOSED_BY_REPO_DERIVATION"},
        "status": status,
        "missing_objects": list(missing_objects),
    }


def build_gate_artifacts(repo_root: Path | None = None) -> Dict[str, Dict[str, object]]:
    root = repo_root or Path(__file__).resolve().parents[1]
    tau = tau_gate.build_tau_sigma_closure_or_obstruction_artifact(root)
    charged = charged_outputs_gate(tau)
    transport = transport_gate.build_transport_closure_or_obstruction_artifact(root)
    neutral = neutral_gate.build_neutral_parameter_closure_or_obstruction_artifact()
    pmns = pmns_gate(neutral)
    ckm_row = ckm_gate()
    cp_row = cp_gate()
    higgs = higgs_ew_gate(tau)
    cosmology = cosmology_desi_gate()
    return {
        "tau_sigma": tau,
        "charged_outputs_at_tau": charged,
        "common_scale_transport": transport,
        "neutral_parameters": neutral,
        "PMNS": pmns,
        "CKM": ckm_row,
        "CP": cp_row,
        "Higgs_EW": higgs,
        "cosmology_DESI": cosmology,
    }


def central_report(repo_root: Path | None = None) -> Dict[str, object]:
    gates = build_gate_artifacts(repo_root)
    blocked = []
    missing: List[str] = []
    promoted: List[str] = []
    for gate_id, gate in gates.items():
        status = str(gate["status"])
        if status in {"DERIVED_CONDITIONAL", "CLOSED_BY_REPO_DERIVATION"}:
            promoted.append(f"{gate_id}:{status}")
        else:
            blocked.append({"gate": gate_id, "status": status})
        missing.extend(str(item) for item in gate.get("missing_objects", []))
    return {
        "public_status_before_sprint": PUBLIC_STATUS,
        "public_status_after_sprint": PUBLIC_STATUS,
        "official_predictions_changed": False,
        "gates": gates,
        "promoted_statuses": promoted,
        "blocked_gates": blocked,
        "missing_objects": _unique(missing),
        "empirical_derivation_inputs_used": False,
    }


def update_prediction_package(package: Dict[str, object], gates: Dict[str, Dict[str, object]]) -> Dict[str, object]:
    updated = json.loads(json.dumps(package))
    sections = updated["sections"]
    sections["charged_same_sector_ratios"]["status"] = gates["charged_outputs_at_tau"]["status"]
    sections["charged_same_sector_ratios"]["comparison_ready"] = False
    sections["charged_same_sector_ratios"]["open_blockers"] = gates["charged_outputs_at_tau"]["missing_objects"]
    sections["charged_cross_sector_ratios"]["status"] = gates["common_scale_transport"]["status"]
    sections["charged_cross_sector_ratios"]["comparison_ready"] = False
    sections["charged_cross_sector_ratios"]["open_blockers"] = gates["common_scale_transport"]["missing_objects"]
    sections["neutral_mass_splittings"]["status"] = gates["neutral_parameters"]["status"]
    sections["neutral_mass_splittings"]["source_artifact"] = "artifacts/neutral_parameter_closure_or_obstruction_v1.json"
    sections["neutral_mass_splittings"]["open_blockers"] = gates["neutral_parameters"]["missing_objects"]
    sections["PMNS_angles_and_phase"]["status"] = gates["PMNS"]["status"]
    sections["PMNS_angles_and_phase"]["open_blockers"] = gates["PMNS"]["missing_objects"]
    sections["CKM_angles_and_phase"]["status"] = gates["CKM"]["status"]
    sections["CKM_angles_and_phase"]["open_blockers"] = gates["CKM"]["missing_objects"]
    sections["CP_Jarlskog_invariants"]["status"] = gates["CP"]["status"]
    sections["CP_Jarlskog_invariants"]["open_blockers"] = gates["CP"]["missing_objects"]
    sections["gauge_couplings"]["status"] = gates["common_scale_transport"]["status"]
    sections["gauge_couplings"]["open_blockers"] = gates["common_scale_transport"]["missing_objects"]
    sections["sin2_theta_W"]["status"] = gates["Higgs_EW"]["status"]
    sections["sin2_theta_W"]["open_blockers"] = gates["Higgs_EW"]["missing_objects"]
    sections["W_Z_Higgs_scale"]["status"] = gates["Higgs_EW"]["status"]
    sections["W_Z_Higgs_scale"]["open_blockers"] = gates["Higgs_EW"]["missing_objects"]
    sections["open_boundary_parameters"]["status"] = gates["tau_sigma"]["status"]
    sections["open_boundary_parameters"]["open_blockers"] = gates["tau_sigma"]["missing_objects"]
    updated["package_status"] = "EXPORTED_NOT_COMPARISON_READY"
    updated["empirical_derivation_inputs_used"] = False
    updated["official_predictions_changed"] = False
    return updated
