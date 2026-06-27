"""Claim-aware registry for artifact-backed and interface-default formulas."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

from .boundary_adapters import load_boundary_constants_artifact
from .mass_ratio_adapters import load_mass_ratio_predictions_artifact
from .matrix_adapters import load_ckm_matrix_artifact, load_cp_phase_artifact, load_pmns_matrix_artifact
from .minimal_action.neutrino_basis_closure import propagation_conditioned_neutrino_mass
from .minimal_action.x_ch_closure import apply_x_ch_boundary_response
from .neutrino_propagation.numerical_closure import build_numerical_closure
from .neutrino_scale.unit_map import derive_neutral_scale_law
from .neutrino_scale.curvature_mass_functional import load_curvature_mass_functional_from_legacy_artifacts
from .neutrino_scale.legacy_scale_report import build_legacy_neutral_scale_candidate

FORMULA_STATUSES = (
    "AVAILABLE_ARTIFACT_BACKED",
    "AVAILABLE_INTERFACE_DEFAULT",
    "AVAILABLE_AUTHOR_SUPPLIED_CONDITIONAL",
    "RETIRED_TARGET",
    "PLACEHOLDER_INTERFACE_ONLY",
    "CALLABLE_NOT_AVAILABLE",
    "OPEN_THEOREM_REQUIRED",
    "DISABLED_UNTIL_RUNTIME_VALIDATED",
)


@dataclass(frozen=True)
class FormulaCallableEntry:
    formula_key: str
    display_name: str
    description: str
    callable_path: str | None
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    status: str
    source_type: str
    source_artifacts: tuple[str, ...]
    theorem_status: str
    claim_boundary: str
    safe_for_default_report: bool
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["source_artifacts"] = list(self.source_artifacts)
        payload["notes"] = list(self.notes)
        return payload


@dataclass(frozen=True)
class FormulaEvaluationResult:
    formula_key: str
    registry_status: str
    evaluation_status: str
    value: Any
    callable_path: str | None
    claim_boundary: str
    empirical_derivation_inputs_used: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class FormulaRegistry:
    entries: dict[str, FormulaCallableEntry]
    registry_name: str = "BHSM Formula Registry"
    version: str = "0.3"

    def get(self, formula_key: str) -> FormulaCallableEntry | None:
        return self.entries.get(formula_key)

    def to_dict(self) -> dict[str, Any]:
        rows = [self.entries[key].to_dict() for key in sorted(self.entries)]
        return {
            "registry_name": self.registry_name,
            "version": self.version,
            "formula_entries": rows,
            "available_artifact_backed": [row["formula_key"] for row in rows if row["status"] == "AVAILABLE_ARTIFACT_BACKED"],
            "available_interface_default": [row["formula_key"] for row in rows if row["status"] == "AVAILABLE_INTERFACE_DEFAULT"],
            "available_author_supplied_conditional": [row["formula_key"] for row in rows if row["status"] == "AVAILABLE_AUTHOR_SUPPLIED_CONDITIONAL"],
            "retired_targets": [row["formula_key"] for row in rows if row["status"] == "RETIRED_TARGET"],
            "open_theorem_required": [row["formula_key"] for row in rows if row["status"] == "OPEN_THEOREM_REQUIRED"],
            "callable_not_available": [row["formula_key"] for row in rows if row["status"] == "CALLABLE_NOT_AVAILABLE"],
            "disabled_until_runtime_validated": [row["formula_key"] for row in rows if row["status"] == "DISABLED_UNTIL_RUNTIME_VALIDATED"],
            "claim_boundary": "Formula availability does not promote an open theorem or turn an interface default into a BHSM derivation.",
        }


def register_formula(registry: FormulaRegistry, entry: FormulaCallableEntry) -> None:
    if entry.status not in FORMULA_STATUSES:
        raise ValueError(f"unsupported formula status: {entry.status}")
    registry.entries[entry.formula_key] = entry


def _artifact_status(loader: Callable[..., Any], repository: str | Path | None) -> str:
    return "AVAILABLE_ARTIFACT_BACKED" if loader(repository).source_status == "DISCOVERED" else "CALLABLE_NOT_AVAILABLE"


def default_formula_registry(repository: str | Path | None = None) -> FormulaRegistry:
    """Build the registry from local artifact availability only."""

    registry = FormulaRegistry({})

    def artifact_entry(key: str, name: str, description: str, loader: Callable[..., Any], path: str) -> FormulaCallableEntry:
        status = _artifact_status(loader, repository)
        return FormulaCallableEntry(
            key, name, description,
            f"{loader.__module__}.{loader.__name__}" if status == "AVAILABLE_ARTIFACT_BACKED" else None,
            {}, {"type": "ValueWithProvenance"}, status, "local BHSM artifact", (path,),
            "ARTIFACT_AVAILABLE_NOT_THEOREM_PROMOTION" if status == "AVAILABLE_ARTIFACT_BACKED" else "MISSING",
            "Artifact-backed output with provenance; not an empirical validation claim.", True,
        )

    entries = (
        artifact_entry("ckm_matrix_from_artifact", "CKM matrix artifact", "Load BHSM CKM magnitudes.", load_ckm_matrix_artifact, "artifacts/CKM_no_fit_operator_output_v1.json"),
        artifact_entry("pmns_matrix_from_artifact", "PMNS matrix artifact", "Load BHSM PMNS magnitudes.", load_pmns_matrix_artifact, "artifacts/PMNS_no_fit_operator_output_v1.json"),
        artifact_entry("cp_phase_from_artifact", "CP phase artifact", "Load the BHSM holonomy phase seed.", load_cp_phase_artifact, "artifacts/CP_no_fit_holonomy_output_v1.json"),
        artifact_entry("boundary_constants_from_artifact", "Boundary constants artifact", "Load no-fit boundary profile constants.", load_boundary_constants_artifact, "artifacts/BHSM_boundary_no_fit_prediction_package_v1.json"),
        artifact_entry("mass_ratios_from_artifact", "Frozen mass ratios", "Load frozen BHSM charged-sector mass ratios.", load_mass_ratio_predictions_artifact, "theory/bhsm_v1_frozen_prediction_set.json"),
        FormulaCallableEntry("hyperspherical_default_metric", "Default interface metric", "Deterministic interface-default metric.", "bhsm.interface.geometry.HypersphericalGeometry.geometric_metric", {"geometry": "HypersphericalGeometry"}, {"type": "number"}, "AVAILABLE_INTERFACE_DEFAULT", "interface default", (), "PLACEHOLDER_UNTIL_BHSM_THEOREM_SUPPLIED", "Interface default formulas remain interface defaults unless a theorem-backed artifact or callable replaces them.", True),
        FormulaCallableEntry("hyperspherical_default_tension", "Default interface tension", "Deterministic interface-default tension.", "bhsm.interface.geometry.HypersphericalGeometry.geometric_tension", {"geometry": "HypersphericalGeometry"}, {"type": "number"}, "AVAILABLE_INTERFACE_DEFAULT", "interface default", (), "PLACEHOLDER_UNTIL_BHSM_THEOREM_SUPPLIED", "Interface default formulas remain interface defaults unless a theorem-backed artifact or callable replaces them.", True),
        FormulaCallableEntry("charged_response_from_artifact", "Charged boundary response", "Ontology-defined charged boundary-response callable.", "bhsm.interface.minimal_action.x_ch_closure.apply_x_ch_boundary_response", {"boundary_field": "string"}, {"type": "boundary_response_chain"}, "AVAILABLE_AUTHOR_SUPPLIED_CONDITIONAL", "author ontology plus local boundary source", ("artifacts/BHSM_x_ch_charged_boundary_response_theorem_v1_1.json", "artifacts/BHSM_x_ch_minimal_action_closure_v0_8.json", "artifacts/BHSM_author_ontology_v0_8.json"), "CONDITIONAL_ACTION_THEOREM", "Conditional boundary-response theorem only; no standalone production-field claim.", True),
        FormulaCallableEntry("neutral_kernel_from_artifact", "Neutral boundary kernel", "Loadable neutral boundary seed; physical observable is propagation conditioned.", None, {}, {}, "AVAILABLE_ARTIFACT_BACKED", "local BHSM artifact", ("artifacts/neutral_operator_no_fit_output_v1.json",), "ARTIFACT_BACKED_BOUNDARY_SEED", "K_nu is a boundary seed, not a static physical mass matrix.", True),
        FormulaCallableEntry("x_ch_production_vertex", "X_ch production vertex", "Retired standalone production-field target.", None, {}, {}, "RETIRED_TARGET", "author ontology", ("artifacts/BHSM_author_ontology_v0_8.json",), "RETIRED_TARGET", "X_ch is modeled as a charged boundary-response operator, not a standalone production field.", False),
        FormulaCallableEntry("neutrino_physical_basis_scale", "Neutrino propagation-mass response", "Propagation-conditioned curvature-response callable.", "bhsm.interface.minimal_action.neutrino_basis_closure.propagation_conditioned_neutrino_mass", {"curvature_response": "value", "propagating": "bool", "threshold_met": "bool"}, {"type": "effective_mass_response"}, "AVAILABLE_AUTHOR_SUPPLIED_CONDITIONAL", "author ontology plus neutral boundary seed", ("artifacts/BHSM_neutrino_basis_scale_minimal_action_closure_v0_8.json", "artifacts/BHSM_author_ontology_v0_8.json"), "CONDITIONAL_PROPAGATION_THEOREM", "Structural propagation theorem only; numerical curvature scale remains open.", True),
        FormulaCallableEntry("neutrino_propagation_mass_candidate", "Neutrino dimensionless propagation-mass candidate", "Build the ordering-free dimensionless threshold-response candidate.", "bhsm.interface.neutrino_propagation.numerical_closure.build_numerical_closure", {}, {"type": "NeutrinoNumericalClosureReport"}, "AVAILABLE_AUTHOR_SUPPLIED_CONDITIONAL", "author ontology plus local no-fit artifacts", ("artifacts/BHSM_neutrino_numerical_closure_report_v0_9.json", "artifacts/BHSM_author_ontology_v0_8.json"), "CONDITIONAL_NUMERICAL_CLOSURE_CANDIDATE", "Dimensionless-only conditional candidate; eV/GeV scale remains open.", True),
        FormulaCallableEntry("neutral_dimensionful_scale_search", "Neutral dimensionful scale search", "Classify local neutral scale candidates and fail closed when no physical unit anchor exists.", "bhsm.interface.neutrino_scale.unit_map.derive_neutral_scale_law", {}, {"type": "NeutralDimensionfulScaleResult"}, "AVAILABLE_AUTHOR_SUPPLIED_CONDITIONAL", "local artifact inventory and author ontology", ("artifacts/BHSM_neutral_scale_closure_report_v1_0.json", "artifacts/BHSM_author_ontology_v0_8.json"), "OPEN_MISSING_NEUTRAL_SCALE", "A dimensionless BHSM response is not, by itself, a physical eV/GeV mass.", True),
        FormulaCallableEntry("legacy_curvature_mass_functional", "Legacy curvature mass functional", "Load the author-supplied geometric matching functional with its explicit ansatz boundary.", "bhsm.interface.neutrino_scale.curvature_mass_functional.load_curvature_mass_functional_from_legacy_artifacts", {}, {"type": "CurvatureMassFunctional"}, "AVAILABLE_AUTHOR_SUPPLIED_CONDITIONAL", "bundled author-supplied legacy theory artifact", ("artifacts/BHSM_curvature_mass_functional_v1_1.json",), "ARTIFACT_BACKED_CURVATURE_MASS_FUNCTIONAL", "The functional is artifact-backed, but it is not an action-derived neutrino mass and supplies no r_prop or physical k_neutral,eff.", True),
        FormulaCallableEntry("legacy_neutral_scale_candidate", "Legacy neutral scale candidate", "Test the curvature functional against the independent neutral radius and curvature-unit gates.", "bhsm.interface.neutrino_scale.legacy_scale_report.build_legacy_neutral_scale_candidate", {}, {"type": "LegacyNeutralScaleCandidate"}, "AVAILABLE_AUTHOR_SUPPLIED_CONDITIONAL", "legacy theory artifacts plus current BHSM neutral audit", ("artifacts/BHSM_legacy_neutral_scale_report_v1_1.json",), "OPEN_MISSING_PROPAGATION_LOCALIZATION_RADIUS", "No eV/GeV output is produced without both a physical propagation radius and neutral curvature map.", True),
        FormulaCallableEntry("cp_o_int_standalone_attachment", "Standalone CP O_int attachment", "Retired standalone production target.", None, {}, {}, "RETIRED_TARGET", "author ontology", ("artifacts/CP_no_fit_holonomy_output_v1.json", "artifacts/BHSM_cp_o_int_minimal_action_closure_v0_8.json", "artifacts/BHSM_author_ontology_v0_8.json"), "RETIRED_TARGET", "CP is represented by the artifact-backed Z6 holonomy constraint; no standalone production vertex is required.", False),
    )
    for entry in entries:
        register_formula(registry, entry)
    return registry


_LOADERS: dict[str, Callable[..., Any]] = {
    "ckm_matrix_from_artifact": load_ckm_matrix_artifact,
    "pmns_matrix_from_artifact": load_pmns_matrix_artifact,
    "cp_phase_from_artifact": load_cp_phase_artifact,
    "boundary_constants_from_artifact": load_boundary_constants_artifact,
    "mass_ratios_from_artifact": load_mass_ratio_predictions_artifact,
}

_CONDITIONAL_CALLABLES: dict[str, Callable[..., Any]] = {
    "charged_response_from_artifact": apply_x_ch_boundary_response,
    "neutrino_physical_basis_scale": propagation_conditioned_neutrino_mass,
    "neutrino_propagation_mass_candidate": build_numerical_closure,
    "neutral_dimensionful_scale_search": derive_neutral_scale_law,
    "legacy_curvature_mass_functional": load_curvature_mass_functional_from_legacy_artifacts,
    "legacy_neutral_scale_candidate": build_legacy_neutral_scale_candidate,
}


def evaluate_formula(formula_key: str, repository: str | Path | None = None, **inputs: Any) -> FormulaEvaluationResult:
    """Evaluate available artifact callables; fail closed for missing callables."""

    registry = default_formula_registry(repository)
    entry = registry.get(formula_key)
    if entry is None:
        return FormulaEvaluationResult(formula_key, "CALLABLE_NOT_AVAILABLE", "CALLABLE_NOT_AVAILABLE", None, None, "Unknown formula key; no formula was guessed.")
    loader = _LOADERS.get(formula_key)
    if loader is not None and entry.status == "AVAILABLE_ARTIFACT_BACKED":
        value = loader(repository)
        return FormulaEvaluationResult(formula_key, entry.status, "EVALUATED", value.to_dict(), entry.callable_path, entry.claim_boundary, value.provenance.empirical_derivation_input)
    conditional = _CONDITIONAL_CALLABLES.get(formula_key)
    if conditional is not None and entry.status == "AVAILABLE_AUTHOR_SUPPLIED_CONDITIONAL":
        try:
            value = conditional(**inputs)
        except (TypeError, ValueError) as exc:
            return FormulaEvaluationResult(formula_key, entry.status, "INPUT_REQUIRED", None, entry.callable_path, f"{entry.claim_boundary} {exc}")
        serialized = value.to_dict() if hasattr(value, "to_dict") else value
        return FormulaEvaluationResult(formula_key, entry.status, "EVALUATED_CONDITIONAL", serialized, entry.callable_path, entry.claim_boundary)
    # Geometry defaults require a caller-supplied geometry and remain defaults.
    if formula_key in {"hyperspherical_default_metric", "hyperspherical_default_tension"} and "geometry" in inputs:
        geometry = inputs["geometry"]
        result = geometry.geometric_metric() if formula_key.endswith("metric") else geometry.geometric_tension()
        return FormulaEvaluationResult(formula_key, entry.status, "EVALUATED_INTERFACE_DEFAULT", result, entry.callable_path, entry.claim_boundary)
    return FormulaEvaluationResult(formula_key, entry.status, "CALLABLE_NOT_AVAILABLE", None, entry.callable_path, entry.claim_boundary)
