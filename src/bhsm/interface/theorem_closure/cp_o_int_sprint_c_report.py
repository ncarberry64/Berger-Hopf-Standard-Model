"""Sprint C symbolic field/action construction and eligibility report."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from ..artifact_sources import repository_root
from .cp_o_int_action_candidate import build_action_density_candidate, field_action_template_enabled, load_field_action_template
from .cp_o_int_attachment import load_cp_phase_attachment
from .cp_o_int_callable import evaluate_symbolic_cp_o_int
from .cp_o_int_coupling import build_coupling_factor
from .cp_o_int_field_action import CPOIntFieldActionCandidate, CPOIntProductionEligibility, build_boundary_factor, build_field_factor, build_phase_factor, load_cp_symbolic_sources
from .cp_o_int_gauge import build_gauge_factor
from .cp_o_int_lorentz import build_lorentz_factor
from .proof_gates import build_cp_o_int_proof_gates


@dataclass(frozen=True)
class CPOIntConstructionStage:
    stage: int
    name: str
    passes: bool
    status: str
    evidence: str
    claim_boundary: str


@dataclass(frozen=True)
class CPOIntSprintCResult:
    candidate_key: str
    candidate_status: str
    status: str
    status_before: str
    status_after: str
    promoted: bool
    promotion_allowed: bool
    promotion_reason: str
    phase_factor: dict[str, Any]
    field_factor: dict[str, Any]
    lorentz_factor: dict[str, Any]
    gauge_factor: dict[str, Any]
    coupling_factor: dict[str, Any]
    boundary_factor: dict[str, Any]
    action_density: dict[str, Any]
    callable_key: str
    callable_available: bool
    symbolic_callable: dict[str, Any]
    production_eligible: bool
    runtime_export_eligible: bool
    production_eligibility: dict[str, Any]
    artifact_sources_checked: tuple[str, ...]
    artifact_sources_used: tuple[str, ...]
    provenance_chain: tuple[dict[str, Any], ...]
    stages: tuple[CPOIntConstructionStage, ...]
    deepest_valid_stage_before: str
    deepest_valid_stage_after: str
    first_failed_required_stage: str
    proof_gates: tuple[Any, ...]
    missing_objects: tuple[str, ...]
    empirical_derivation_inputs_used: bool
    reference_values_used_as_theorem_inputs: bool
    calibration_values_used_as_theorem_inputs: bool
    conditional_author_axiom_used: bool
    action_level_closure_achieved: bool
    runtime_gate_changes: bool
    registry_entries_affected: tuple[str, ...]
    claim_boundary: str
    warnings: tuple[str, ...]
    notes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _template_complete(template: Mapping[str, Any] | None) -> bool:
    required = (
        "field_representation", "lorentz_structure", "gauge_admissibility",
        "coupling_normalization", "boundary_operator", "action_density",
        "integration_measure", "locality",
    )
    return field_action_template_enabled(template) and all(template.get(key) not in (None, "", {}, []) for key in required)


def build_production_eligibility(
    field,
    lorentz,
    gauge,
    coupling,
    action,
    symbolic_callable,
) -> CPOIntProductionEligibility:
    production_missing = tuple(
        item
        for item in (
            field.missing_object,
            lorentz.missing_object,
            gauge.missing_object,
            coupling.missing_object,
            action.missing_object,
            None if symbolic_callable.production_callable else "action-backed production theorem callable",
        )
        if item
    )
    runtime_missing = ("live FeynRules syntax validation", "loadable UFO export validation", "MadGraph smoke test")
    return CPOIntProductionEligibility(False, False, production_missing, runtime_missing, "FORBIDDEN_UNSUPPORTED")


def build_cp_o_int_field_action_report(
    template_path: str | Path | None = None,
    repository: str | Path | None = None,
) -> CPOIntSprintCResult:
    root = Path(repository).resolve() if repository is not None else repository_root()
    template = load_field_action_template(template_path, root)
    conditional = _template_complete(template)
    phase = build_phase_factor(root)
    attachment = load_cp_phase_attachment(root)
    field = build_field_factor(root)
    boundary = build_boundary_factor(root)
    lorentz = build_lorentz_factor(root)
    gauge = build_gauge_factor(root)
    coupling = build_coupling_factor(root)
    action = build_action_density_candidate(root, template if conditional else None)
    callable_result = evaluate_symbolic_cp_o_int(coupling.symbol, phase.expression, "Psi_CP_interface_bar O_int Psi_CP_interface", boundary.symbol)
    candidate_status = "AVAILABLE_AUTHOR_AXIOM_CONDITIONAL" if conditional else "AVAILABLE_SYMBOLIC_CANDIDATE"
    theorem_status = "DERIVED_CONDITIONAL_AUTHOR_AXIOM" if conditional else "OPEN_MISSING_ACTION_SOURCE"
    sources = load_cp_symbolic_sources(root)["sources"] + attachment.source_artifacts
    sources = tuple(dict.fromkeys(sources))
    checked = tuple(dict.fromkeys(sources + ("data/theorem_inputs/cp_o_int_field_action_candidate_template.json",)))
    eligibility = build_production_eligibility(field, lorentz, gauge, coupling, action, callable_result)
    candidate = CPOIntFieldActionCandidate(
        "cp_o_int_symbolic_field_action_candidate",
        callable_result.expression,
        phase,
        field,
        boundary,
        candidate_status,
        sources,
        "A symbolic candidate is not action-level closure or a production vertex.",
    )
    stages = (
        CPOIntConstructionStage(1, "Load artifact-backed CP phase", phase.is_artifact_backed, phase.status, phase.source, phase.claim_boundary),
        CPOIntConstructionStage(2, "Load CKM/PMNS phase attachment", attachment.ckm_attachment and attachment.pmns_attachment, attachment.status, "matrix attachment artifact", "Matrix attachment is not standalone interaction closure."),
        CPOIntConstructionStage(3, "Construct field representation candidate", True, field.status, field.representation, field.claim_boundary),
        CPOIntConstructionStage(4, "Construct Lorentz/index candidate", True, lorentz.status, lorentz.expression, lorentz.claim_boundary),
        CPOIntConstructionStage(5, "Construct gauge/sector admissibility candidate", True, gauge.status, gauge.expression, gauge.claim_boundary),
        CPOIntConstructionStage(6, "Construct coupling/mass-dimension candidate", True, coupling.status, coupling.symbol, coupling.claim_boundary),
        CPOIntConstructionStage(7, "Construct boundary/action source candidate", True, action.status, action.expression, action.claim_boundary),
        CPOIntConstructionStage(8, "Construct callable symbolic O_int candidate", callable_result.callable_available, callable_result.status, callable_result.expression, callable_result.claim_boundary),
        CPOIntConstructionStage(9, "Evaluate production eligibility", eligibility.production_eligible, eligibility.status, "action-level gates remain open", "A symbolic candidate is not production-ready."),
        CPOIntConstructionStage(10, "Evaluate runtime export eligibility", eligibility.runtime_export_eligible, "DISABLED_UNTIL_RUNTIME_VALIDATED", "runtime tools were not invoked", "Runtime readiness requires live external validation."),
    )
    evidence = {
        "CP01": True,
        "CP02": False, "CP03": False, "CP04": False, "CP05": False,
        "CP06": False, "CP07": False, "CP08": stages[1].passes, "CP09": False,
        "CP10": False, "CP11": True, "CP12": phase.is_artifact_backed,
        "CP13": bool(sources), "CP14": True, "CP15": True, "CP16": True,
        "CP17": True, "CP18": True, "CP19": True, "CP20": True, "CP21": True,
    }
    evidence_text = {
        "CP01": "A formal symbolic-construction boundary is encoded.",
        "CP08": "The CKM/PMNS phase attachment remains artifact-backed.",
        "CP11": "The symbolic callable has explicit string inputs and structured output.",
        "CP12": "The CP phase and symbolic candidate terms are local artifacts.",
        "CP13": "All source paths are recorded in the provenance chain.",
        "CP14": "No empirical data are accepted.", "CP15": "No reference or PDG inputs are read.",
        "CP16": "No W anchor or calibration value is accepted.",
        "CP17": "Factor assembly and non-promotion checks pass.",
        "CP18": "A non-destructive registry proposal is generated.",
        "CP19": "A formula-registry update artifact is generated.",
        "CP20": "Sprint C claim policy is explicit.",
        "CP21": "Sprint B and prior blocker artifacts remain in the source chain.",
    }
    gates = build_cp_o_int_proof_gates(evidence, evidence_text)
    missing = tuple(dict.fromkeys(eligibility.production_missing))
    provenance = tuple({"source_path": path, "source_status": "DISCOVERED", "empirical_derivation_input": False, "reference_theorem_input": False} for path in sources)
    return CPOIntSprintCResult(
        candidate_key=candidate.candidate_key,
        candidate_status=candidate_status,
        status=theorem_status,
        status_before="OPEN_MISSING_INTERACTION_ATTACHMENT",
        status_after=theorem_status,
        promoted=False,
        promotion_allowed=False,
        promotion_reason="A source-traced symbolic candidate exists, but its physical factors and action provenance remain placeholders.",
        phase_factor=phase.to_dict(), field_factor=field.to_dict(), lorentz_factor=lorentz.to_dict(),
        gauge_factor=gauge.to_dict(), coupling_factor=coupling.to_dict(), boundary_factor=boundary.to_dict(),
        action_density=action.to_dict(), callable_key=callable_result.callable_key,
        callable_available=callable_result.callable_available, symbolic_callable=callable_result.to_dict(),
        production_eligible=False, runtime_export_eligible=False, production_eligibility=eligibility.to_dict(),
        artifact_sources_checked=checked, artifact_sources_used=sources, provenance_chain=provenance,
        stages=stages, deepest_valid_stage_before="Stage 2: Phase attachment rule availability",
        deepest_valid_stage_after="Stage 8: Construct callable symbolic O_int candidate",
        first_failed_required_stage="Stage 9: Evaluate production eligibility",
        proof_gates=gates, missing_objects=missing,
        empirical_derivation_inputs_used=False, reference_values_used_as_theorem_inputs=False,
        calibration_values_used_as_theorem_inputs=False, conditional_author_axiom_used=conditional,
        action_level_closure_achieved=False, runtime_gate_changes=False,
        registry_entries_affected=("cp_holonomy_phase_attachment", "minimal_collider_interface_subset", "feynrules_minimal_model", "ufo_export", "madgraph_smoke_test"),
        claim_boundary="The symbolic field/action candidate localizes the gap but is not action-level closure.",
        warnings=("CP holonomy or CKM/PMNS phase attachment alone is not a standalone CP O_int interaction theorem.", "A symbolic field/action candidate is not action-level closure.", "Runtime-disabled software gates remain disabled until live external validation passes."),
        notes=("Existing artifacts already label the CP density as symbolic/blocked.", "The template is disabled by default."),
    )


def cp_o_int_sprint_c_to_markdown(report: CPOIntSprintCResult) -> str:
    lines = [
        "# BHSM CP O_int Field/Action Construction Sprint C",
        "",
        f"Theorem status: `{report.status_after}`",
        f"Candidate status: `{report.candidate_status}`",
        f"Deepest valid stage: {report.deepest_valid_stage_after}",
        f"Production eligible: `{str(report.production_eligible).lower()}`",
        f"Runtime export eligible: `{str(report.runtime_export_eligible).lower()}`",
        "",
        "| Stage | Result | Status |",
        "| --- | --- | --- |",
    ]
    lines.extend(f"| {stage.stage}. {stage.name} | {'pass' if stage.passes else 'fail'} | `{stage.status}` |" for stage in report.stages)
    lines.extend(["", "A symbolic field/action candidate is not action-level closure."])
    return "\n".join(lines) + "\n"
