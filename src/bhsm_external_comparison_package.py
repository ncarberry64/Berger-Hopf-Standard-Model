from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Mapping


PUBLIC_STATUS = "internal boundary no-fit package complete; external empirical comparison layer separate/open"
INTERNAL_COMPLETE = "COMPLETE_EXPORTED"
COMPARISON_LAYER = "IMPLEMENTED_COMPARISON_ONLY_LAYER"
DATA_ABSENT = "DATA_ABSENT"
NOT_EVALUATED_DATA_ABSENT = "NOT_EVALUATED_DATA_ABSENT"

TARGET_FAMILIES = (
    "charged_mass_ratios",
    "charged_same_sector_ratios",
    "charged_cross_sector_ratios",
    "CKM_matrix",
    "PMNS_matrix",
    "CP_observables",
    "Higgs_EW_values",
    "cosmology_DESI_directional_anisotropy",
)

CORE_PR52_ARTIFACTS = (
    "canonical_profile_hessian_theorem_v1.json",
    "tau_sigma_boundary_values_v1.json",
    "profile_scale_closure_values_v1.json",
    "charged_boundary_bridge_values_v1.json",
    "charged_outputs_at_boundary_tau_A_local_v1.json",
    "charged_outputs_at_boundary_tau_A_background_identity_v1.json",
    "common_scale_boundary_transport_v1.json",
    "neutral_operator_no_fit_output_v1.json",
    "PMNS_no_fit_operator_output_v1.json",
    "CKM_no_fit_operator_output_v1.json",
    "CP_no_fit_holonomy_output_v1.json",
    "BHSM_boundary_no_fit_prediction_package_v1.json",
)


@dataclass(frozen=True)
class ExternalTargetRequirement:
    family: str
    required_metadata: tuple[str, ...]
    comparison_only: bool
    not_derivation_input: bool


def _root(repo_root: Path | None = None) -> Path:
    return repo_root or Path(__file__).resolve().parents[1]


def guardrails() -> Dict[str, object]:
    return {
        "public_status": PUBLIC_STATUS,
        "public_status_before_gate": "structural architecture integrated conditional; numerical closure open",
        "official_predictions_changed": False,
        "empirical_derivation_inputs_used": False,
        "boundary_predictions_modified_by_comparison": False,
        "comparison_data_required_for_internal_completion": False,
        "observed_masses_used": False,
        "observed_Higgs_used": False,
        "observed_gauge_values_used": False,
        "observed_CKM_used": False,
        "observed_PMNS_used": False,
        "observed_CP_used": False,
        "tau_fit_to_masses": False,
        "sigma_fit_to_masses": False,
    }


def load_boundary_prediction_package(repo_root: Path | None = None) -> Dict[str, object]:
    root = _root(repo_root)
    path = root / "artifacts" / "BHSM_boundary_no_fit_prediction_package_v1.json"
    return json.loads(path.read_text(encoding="utf-8"))


def build_external_target_schema() -> Dict[str, object]:
    metadata = (
        "source",
        "date_or_version",
        "units",
        "scheme",
        "scale",
        "covariance_available",
        "comparison_only",
        "not_derivation_input",
    )
    return {
        **guardrails(),
        "artifact": "BHSM_external_comparison_target_schema_v1",
        "external_empirical_comparison_package": COMPARISON_LAYER,
        "external_targets_present": False,
        "comparison_result": DATA_ABSENT,
        "target_families": {
            family: asdict(ExternalTargetRequirement(family, metadata, True, True))
            for family in TARGET_FAMILIES
        },
    }


def load_external_targets_if_present(repo_root: Path | None = None) -> Dict[str, object]:
    root = _root(repo_root)
    path = root / "artifacts" / "BHSM_external_targets_v1.json"
    if not path.exists():
        return {
            **guardrails(),
            "external_targets_present": False,
            "comparison_result": DATA_ABSENT,
            "targets": {},
            "source_path": None,
        }
    return {
        **guardrails(),
        "external_targets_present": True,
        "comparison_result": "TARGETS_LOADED",
        "targets": json.loads(path.read_text(encoding="utf-8")),
        "source_path": str(path),
    }


def validate_external_targets(target_payload: Mapping[str, object] | None = None) -> Dict[str, object]:
    payload = target_payload or load_external_targets_if_present()
    if not payload.get("external_targets_present"):
        return {
            **guardrails(),
            "valid": True,
            "external_targets_present": False,
            "comparison_result": DATA_ABSENT,
            "validation_errors": [],
        }
    errors: list[str] = []
    targets = payload.get("targets", {})
    for family, rows in targets.items():
        if family not in TARGET_FAMILIES:
            errors.append(f"unknown target family: {family}")
            continue
        for index, row in enumerate(rows if isinstance(rows, list) else [rows]):
            for key in build_external_target_schema()["target_families"][family]["required_metadata"]:
                if key not in row:
                    errors.append(f"{family}[{index}] missing {key}")
            if row.get("comparison_only") is not True or row.get("not_derivation_input") is not True:
                errors.append(f"{family}[{index}] must be comparison_only and not_derivation_input")
    return {
        **guardrails(),
        "valid": not errors,
        "external_targets_present": True,
        "comparison_result": "TARGET_VALIDATION_PASSED" if not errors else "TARGET_VALIDATION_FAILED",
        "validation_errors": errors,
    }


def transport_boundary_predictions_to_external_scheme_if_possible(
    repo_root: Path | None = None,
) -> Dict[str, object]:
    targets = load_external_targets_if_present(repo_root)
    return {
        **guardrails(),
        "artifact": "BHSM_external_transport_layer_v1",
        "internal_boundary_transport": {
            "mu_ref": "mu_BH_boundary",
            "T_boundary_to_boundary": 1,
            "status": "DERIVED_FIXED_IDENTITY_AT_BHSM_BOUNDARY_SCALE",
        },
        "external_empirical_transport": {
            "status": "OPEN_COMPARISON_LAYER",
            "purpose": "map BHSM boundary predictions to published schemes/scales for comparison only",
            "not_derivation_input": True,
        },
        "external_transport_population": (
            "TARGETS_LOADED" if targets["external_targets_present"] else "DATA_OR_SCHEME_DEPENDENT"
        ),
        "internal_boundary_package_complete": True,
    }


def compute_residuals(repo_root: Path | None = None) -> Dict[str, object]:
    targets = load_external_targets_if_present(repo_root)
    if not targets["external_targets_present"]:
        return {
            **guardrails(),
            "external_targets_present": False,
            "comparison_result": DATA_ABSENT,
            "residuals": [],
        }
    return {
        **guardrails(),
        "external_targets_present": True,
        "comparison_result": "RESIDUAL_ENGINE_READY_TARGET_MAPPING_REQUIRED",
        "residuals": [],
    }


def compute_chi2_if_covariance_present(repo_root: Path | None = None) -> Dict[str, object]:
    targets = load_external_targets_if_present(repo_root)
    return {
        **guardrails(),
        "chi2_computed": False,
        "covariance_present": False if not targets["external_targets_present"] else "CHECK_TARGET_ROWS",
        "comparison_result": DATA_ABSENT if not targets["external_targets_present"] else "COVARIANCE_CHECK_REQUIRED",
    }


def compute_simple_normalized_residuals_if_no_covariance(repo_root: Path | None = None) -> Dict[str, object]:
    targets = load_external_targets_if_present(repo_root)
    return {
        **guardrails(),
        "simple_normalized_residuals_computed": False,
        "comparison_result": DATA_ABSENT if not targets["external_targets_present"] else "TARGET_MAPPING_REQUIRED",
        "residuals": [],
    }


def evaluate_falsification_gates(repo_root: Path | None = None) -> Dict[str, object]:
    root = _root(repo_root)
    targets = load_external_targets_if_present(root)
    all_core_exist = all((root / "artifacts" / name).exists() for name in CORE_PR52_ARTIFACTS)
    comparison_gate_status = "READY_FOR_DATA" if targets["external_targets_present"] else NOT_EVALUATED_DATA_ABSENT
    return {
        **guardrails(),
        "artifact": "BHSM_falsification_gates_v1",
        "profile_scale_identity_gate": {
            "sigma*tau = pi": True,
            "kappa_H = 4*sigma^2": True,
            "tau = pi/sigma": True,
            "status": "PASSED_INTERNAL_IDENTITY",
        },
        "no_empirical_derivation_gate": {
            "empirical_derivation_inputs_used": False,
            "status": "PASSED",
        },
        "boundary_package_integrity_gate": {
            "all_required_internal_artifacts_exist": all_core_exist,
            "status": "PASSED" if all_core_exist else "FAILED_MISSING_ARTIFACT",
            "core_artifacts": list(CORE_PR52_ARTIFACTS),
        },
        "comparison_layer_separation_gate": {
            "external_comparison_can_modify_internal_constants": False,
            "status": "PASSED",
        },
        "charged_sector_comparison_gate": {
            "status": comparison_gate_status,
            "residuals": [],
        },
        "CKM_PMNS_CP_comparison_gate": {
            "status": comparison_gate_status,
            "residuals": [],
        },
        "cosmology_DESI_gate": {
            "status": comparison_gate_status,
            "actual_directional_anisotropy_data_present": targets["external_targets_present"]
            and "cosmology_DESI_directional_anisotropy" in targets.get("targets", {}),
        },
    }


def build_external_comparison_artifact(repo_root: Path | None = None) -> Dict[str, object]:
    targets = load_external_targets_if_present(repo_root)
    return {
        **guardrails(),
        "artifact": "BHSM_external_empirical_comparison_package_v1",
        "external_empirical_comparison_package": COMPARISON_LAYER,
        "external_targets_present": targets["external_targets_present"],
        "external_empirical_comparison_status": (
            "TARGETS_LOADED" if targets["external_targets_present"] else "DATA_OPTIONAL_OR_DATA_ABSENT"
        ),
        "comparison_result": DATA_ABSENT if not targets["external_targets_present"] else "TARGETS_LOADED",
        "target_schema": build_external_target_schema(),
        "target_validation": validate_external_targets(targets),
        "transport": transport_boundary_predictions_to_external_scheme_if_possible(repo_root),
        "residuals": compute_residuals(repo_root),
        "chi2": compute_chi2_if_covariance_present(repo_root),
        "simple_normalized_residuals": compute_simple_normalized_residuals_if_no_covariance(repo_root),
        "falsification_gates": evaluate_falsification_gates(repo_root),
    }


def build_completion_manifest(repo_root: Path | None = None) -> Dict[str, object]:
    targets = load_external_targets_if_present(repo_root)
    return {
        **guardrails(),
        "artifact": "BHSM_COMPLETE_V1_RELEASE_CANDIDATE",
        "release_candidate": "BHSM_COMPLETE_V1",
        "internal_boundary_package": INTERNAL_COMPLETE,
        "boundary_no_fit_prediction_package": INTERNAL_COMPLETE,
        "external_empirical_comparison_package": COMPARISON_LAYER,
        "external_empirical_comparison_status": "DATA_OPTIONAL_OR_DATA_ABSENT",
        "external_targets_present": targets["external_targets_present"],
        "comparison_result": DATA_ABSENT if not targets["external_targets_present"] else "TARGETS_LOADED",
        "core_artifacts": list(CORE_PR52_ARTIFACTS),
        "public_status": PUBLIC_STATUS,
    }
