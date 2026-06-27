"""Adapters for frozen BHSM mass-ratio artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .artifact_sources import load_artifact_json, repository_root
from .provenance import ProvenanceRecord, ValueWithProvenance, missing_artifact_value

MASS_RATIO_PATH = "theory/bhsm_v1_frozen_prediction_set.json"


def _prediction_sets(repository: str | Path | None = None) -> tuple[dict[str, Any] | None, str]:
    root = Path(repository).resolve() if repository is not None else repository_root()
    path = root / MASS_RATIO_PATH
    if not path.is_file():
        return None, MASS_RATIO_PATH
    payload = load_artifact_json(path)
    sets = payload.get("prediction_sets", []) if isinstance(payload, dict) else []
    if not isinstance(sets, list) or not sets:
        return None, MASS_RATIO_PATH
    by_branch = {str(item.get("branch")): item for item in sets if isinstance(item, dict)}
    selected = {
        "BHSM_BARE_V1": by_branch.get("BHSM_BARE_V1"),
        "BHSM_DRESSED_V1_CANDIDATE": by_branch.get("BHSM_DRESSED_V1_CANDIDATE"),
    }
    if not all(selected.values()):
        # The stable export may omit a branch field but preserves deterministic order.
        selected = {
            "BHSM_BARE_V1": sets[0],
            "BHSM_DRESSED_V1_CANDIDATE": sets[1] if len(sets) > 1 else sets[0],
        }
    return selected, MASS_RATIO_PATH


def _provenance(field: str) -> ProvenanceRecord:
    return ProvenanceRecord(
        source_path=MASS_RATIO_PATH,
        source_artifact_key="bhsm_v1_frozen_prediction_set",
        source_field=field,
        source_status="DISCOVERED",
        loaded_at_runtime=True,
        empirical_derivation_input=False,
        calibration_input=False,
        reference_comparison_input=False,
        frozen_prediction=True,
        claim_status="FROZEN_INTERNAL_PREDICTION",
        notes=("Read directly from the existing frozen prediction-set artifact.",),
    )


def load_mass_ratio_predictions_artifact(repository: str | Path | None = None) -> ValueWithProvenance:
    sets, path = _prediction_sets(repository)
    if sets is None:
        return missing_artifact_value("mass_ratios", path, value_kind="mass_ratio_bundle")
    value: dict[str, Any] = {}
    for branch, package in sets.items():
        outputs = package.get("outputs", {})
        value[branch] = {
            "charged_lepton_ratios": outputs.get("charged_lepton_ratios"),
            "up_quark_ratios": outputs.get("up_quark_ratios"),
            "down_quark_ratios": outputs.get("down_quark_ratios"),
        }
    return ValueWithProvenance("mass_ratios", value, "dimensionless", "mass_ratio_bundle", _provenance("prediction_sets[].outputs.*_ratios"))


def load_charged_lepton_ratio_artifact(repository: str | Path | None = None) -> ValueWithProvenance:
    sets, path = _prediction_sets(repository)
    if sets is None:
        return missing_artifact_value("charged_lepton_ratios", path, value_kind="mass_ratio_bundle")
    value = {branch: package.get("outputs", {}).get("charged_lepton_ratios") for branch, package in sets.items()}
    if any(item is None for item in value.values()):
        return missing_artifact_value("charged_lepton_ratios", path, value_kind="mass_ratio_bundle")
    return ValueWithProvenance("charged_lepton_ratios", value, "dimensionless", "mass_ratio_bundle", _provenance("prediction_sets[].outputs.charged_lepton_ratios"))


def load_quark_ratio_artifact(repository: str | Path | None = None) -> ValueWithProvenance:
    sets, path = _prediction_sets(repository)
    if sets is None:
        return missing_artifact_value("quark_mass_ratios", path, value_kind="mass_ratio_bundle")
    value = {
        branch: {
            "up_quark_ratios": package.get("outputs", {}).get("up_quark_ratios"),
            "down_quark_ratios": package.get("outputs", {}).get("down_quark_ratios"),
        }
        for branch, package in sets.items()
    }
    if any(row["up_quark_ratios"] is None or row["down_quark_ratios"] is None for row in value.values()):
        return missing_artifact_value("quark_mass_ratios", path, value_kind="mass_ratio_bundle")
    return ValueWithProvenance("quark_mass_ratios", value, "dimensionless", "mass_ratio_bundle", _provenance("prediction_sets[].outputs.{up,down}_quark_ratios"))
