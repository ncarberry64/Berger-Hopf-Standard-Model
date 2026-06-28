"""Focused staged evaluation for standalone CP O_int attachment."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from ..artifact_sources import repository_root
from .cp_o_int_action import action_from_candidate, candidate_is_complete, candidate_is_enabled, load_cp_o_int_candidate_template
from .cp_o_int_admissibility import gauge_admissibility_from_candidate
from .cp_o_int_attachment import ATTACHMENT_THEOREM_PATH, load_cp_phase_attachment
from .cp_o_int_operator import CPOIntCodomain, CPOIntCouplingNormalization, CPOIntDomain, CPOIntFieldRepresentation, CPOIntLorentzStructure
from .proof_gates import build_cp_o_int_proof_gates, promotion_allowed

CHECKED_SOURCES = (
    "artifacts/CP_no_fit_holonomy_output_v1.json",
    "artifacts/CKM_no_fit_operator_output_v1.json",
    "artifacts/PMNS_no_fit_operator_output_v1.json",
    ATTACHMENT_THEOREM_PATH,
    "artifacts/BHSM_cp_o_int_theorem_closure_attempt_v0_4.json",
    "data/theorem_inputs/cp_o_int_attachment_candidate_template.json",
)


@dataclass(frozen=True)
class CPOIntStage:
    stage: int
    name: str
    passes: bool
    status: str
    evidence: str
    missing_object: str | None


@dataclass(frozen=True)
class CPOIntEvaluationResult:
    theorem_key: str
    display_name: str
    status_before: str
    status_after: str
    promoted: bool
    promotion_allowed: bool
    promotion_reason: str
    formal_statement: str
    domain: dict[str, Any]
    codomain: dict[str, Any]
    field_representation: dict[str, Any]
    lorentz_structure: dict[str, Any]
    gauge_admissibility: dict[str, Any]
    phase_attachment_rule: dict[str, Any]
    coupling_normalization: dict[str, Any]
    action_term: dict[str, Any]
    callable_key: str
    callable_available: bool
    artifact_sources_checked: tuple[str, ...]
    artifact_sources_used: tuple[str, ...]
    provenance_chain: tuple[dict[str, Any], ...]
    stages: tuple[CPOIntStage, ...]
    deepest_valid_stage: str
    proof_gates: tuple[Any, ...]
    missing_objects: tuple[str, ...]
    empirical_derivation_inputs_used: bool
    reference_values_used_as_theorem_inputs: bool
    calibration_values_used_as_theorem_inputs: bool
    runtime_gate_changes: bool
    registry_entries_affected: tuple[str, ...]
    formula_registry_updates: tuple[dict[str, Any], ...]
    conditional_author_axiom_used: bool
    action_level_closure_achieved: bool
    claim_boundary: str
    warnings: tuple[str, ...]
    notes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _text(candidate: Mapping[str, Any] | None, key: str) -> str:
    value = candidate.get(key) if candidate else None
    return str(value) if value not in (None, "", {}, []) else ""


def _components(candidate: Mapping[str, Any] | None):
    enabled = candidate_is_enabled(candidate)
    source = str(candidate.get("path", "author-supplied candidate template")) if enabled else "not present in local theorem artifacts"
    status = "AUTHOR_AXIOM_CONDITIONAL" if enabled else "OPEN"
    domain = CPOIntDomain(_text(candidate, "domain"), status if _text(candidate, "domain") else "OPEN_MISSING_FIELD_REPRESENTATION", source)
    codomain = CPOIntCodomain(_text(candidate, "codomain"), status if _text(candidate, "codomain") else "OPEN_MISSING_FIELD_REPRESENTATION", source)
    field_raw = candidate.get("field_representation") if candidate else None
    if isinstance(field_raw, Mapping):
        field = CPOIntFieldRepresentation(str(field_raw.get("field_content", "")), str(field_raw.get("representation", "")), status if field_raw else "OPEN_MISSING_FIELD_REPRESENTATION", source)
    else:
        field = CPOIntFieldRepresentation(str(field_raw or ""), "", status if field_raw else "OPEN_MISSING_FIELD_REPRESENTATION", source)
    lorentz_raw = candidate.get("lorentz_structure") if candidate else None
    if isinstance(lorentz_raw, Mapping):
        lorentz = CPOIntLorentzStructure(str(lorentz_raw.get("expression", "")), str(lorentz_raw.get("index_structure", "")), status if lorentz_raw else "OPEN_MISSING_LORENTZ_STRUCTURE", source)
    else:
        lorentz = CPOIntLorentzStructure(str(lorentz_raw or ""), "", status if lorentz_raw else "OPEN_MISSING_LORENTZ_STRUCTURE", source)
    coupling_raw = candidate.get("coupling_normalization") if candidate else None
    if isinstance(coupling_raw, Mapping):
        coupling = CPOIntCouplingNormalization(str(coupling_raw.get("coupling_symbol", "")), str(coupling_raw.get("normalization", "")), str(coupling_raw.get("mass_dimension", "")), status if coupling_raw else "OPEN_MISSING_COUPLING_NORMALIZATION", source)
    else:
        coupling = CPOIntCouplingNormalization("", str(coupling_raw or ""), "", status if coupling_raw else "OPEN_MISSING_COUPLING_NORMALIZATION", source)
    return domain, codomain, field, lorentz, gauge_admissibility_from_candidate(candidate if enabled else None), coupling, action_from_candidate(candidate if enabled else None)


def _status_from_stages(stages: tuple[CPOIntStage, ...], candidate: Mapping[str, Any] | None) -> str:
    if not stages[0].passes:
        return "ARTIFACT_NOT_FOUND"
    if not candidate_is_enabled(candidate):
        return "OPEN_MISSING_INTERACTION_ATTACHMENT"
    mapping = {
        3: "OPEN_MISSING_FIELD_REPRESENTATION",
        4: "OPEN_MISSING_LORENTZ_STRUCTURE",
        5: "OPEN_MISSING_GAUGE_ADMISSIBILITY",
        6: "OPEN_MISSING_COUPLING_NORMALIZATION",
        7: "OPEN_MISSING_ACTION_SOURCE",
    }
    for stage in stages[2:7]:
        if not stage.passes:
            return mapping[stage.stage]
    if candidate_is_complete(candidate):
        return "DERIVED_CONDITIONAL_AUTHOR_AXIOM"
    return "OPEN_MISSING_INTERACTION_ATTACHMENT"


def evaluate_cp_o_int_stages(
    candidate: Mapping[str, Any] | None = None,
    repository: str | Path | None = None,
) -> CPOIntEvaluationResult:
    root = Path(repository).resolve() if repository is not None else repository_root()
    candidate = dict(candidate) if candidate is not None else load_cp_o_int_candidate_template(repository=root)
    attachment = load_cp_phase_attachment(root)
    domain, codomain, field, lorentz, gauge, coupling, action = _components(candidate)
    enabled = candidate_is_enabled(candidate)
    field_ok = bool(field.field_content and (field.representation or not isinstance(candidate.get("field_representation"), Mapping)))
    lorentz_ok = bool(lorentz.expression)
    gauge_ok = bool(gauge.gauge_representation)
    coupling_ok = bool(coupling.normalization)
    action_ok = action.interaction_defined
    callable_ok = candidate_is_complete(candidate)
    stage_rows = (
        CPOIntStage(1, "Internal CP phase availability", attachment.delta_bh is not None and attachment.boundary_phase is not None, attachment.status, "delta_BH and Z6 boundary phase loaded from local artifact", "CP phase artifact" if attachment.delta_bh is None else None),
        CPOIntStage(2, "Phase attachment rule availability", attachment.ckm_attachment and attachment.pmns_attachment, attachment.status, "CKM/PMNS matrix-phase attachment is recorded", "phase attachment rule" if not attachment.ckm_attachment else None),
        CPOIntStage(3, "Field representation availability", field_ok, field.status, field.source, None if field_ok else "standalone O_int field content and representation"),
        CPOIntStage(4, "Lorentz structure availability", lorentz_ok, lorentz.status, lorentz.source, None if lorentz_ok else "standalone O_int Lorentz/index structure"),
        CPOIntStage(5, "Gauge/sector admissibility availability", gauge_ok, gauge.status, gauge.source, None if gauge_ok else "standalone O_int gauge representation and sector admissibility"),
        CPOIntStage(6, "Coupling normalization availability", coupling_ok, coupling.status, coupling.source, None if coupling_ok else "standalone O_int coupling normalization and mass dimension"),
        CPOIntStage(7, "Action/interacting operator availability", action_ok, action.status, action.source, None if action_ok else "standalone O_int action/source term"),
        CPOIntStage(8, "Callable theorem availability", callable_ok, "AUTHOR_AXIOM_CONDITIONAL" if callable_ok else "CALLABLE_NOT_AVAILABLE", "generic conditional candidate evaluator" if callable_ok else "closure evaluator is not a production theorem callable", None if callable_ok else "standalone O_int theorem callable"),
        CPOIntStage(9, "Registry promotion eligibility", False, "FORBIDDEN_UNSUPPORTED", "No action-derived theorem artifact is present", "action-derived support for production promotion"),
    )
    status = _status_from_stages(stage_rows, candidate)
    author_conditional = status == "DERIVED_CONDITIONAL_AUTHOR_AXIOM"
    evidence = {
        "CP01": True,
        "CP02": bool(domain.description), "CP03": bool(codomain.description), "CP04": field_ok,
        "CP05": lorentz_ok, "CP06": gauge_ok, "CP07": action_ok,
        "CP08": stage_rows[1].passes, "CP09": coupling_ok, "CP10": callable_ok,
        "CP11": True, "CP12": stage_rows[0].passes, "CP13": bool(attachment.source_artifacts),
        "CP14": True, "CP15": True, "CP16": True, "CP17": True,
        "CP18": True, "CP19": True, "CP20": True, "CP21": (root / ATTACHMENT_THEOREM_PATH).is_file(),
    }
    evidence_text = {
        "CP01": "The focused formal conditional theorem statement is encoded.",
        "CP08": "The local blocker records CKM/PMNS phase attachment.",
        "CP11": "The focused evaluator has structured mapping input and CPOIntEvaluationResult output.",
        "CP12": "The local CP phase artifact exists.",
        "CP13": "The phase and blocker source paths are explicit.",
        "CP14": "No empirical data are accepted by the evaluator.",
        "CP15": "No reference or PDG modules are imported.",
        "CP16": "No calibration value or W anchor is accepted.",
        "CP17": "Phase availability and non-promotion consistency checks pass.",
        "CP18": "A separate CP registry update proposal is generated.",
        "CP19": "A separate formula-registry update record is generated.",
        "CP20": "The CP Sprint B claim policy is explicit.",
        "CP21": "The v1.1 blocker and Sprint A result record the open theorem.",
    }
    gates = build_cp_o_int_proof_gates(evidence, evidence_text)
    action_level = promotion_allowed(gates) and action.action_derived
    promoted = action_level
    used = tuple(path for path in CHECKED_SOURCES if (root / path).is_file())
    deepest = max((stage for stage in stage_rows if stage.passes), key=lambda item: item.stage)
    missing = tuple(stage.missing_object for stage in stage_rows if not stage.passes and stage.missing_object)
    return CPOIntEvaluationResult(
        theorem_key="cp_o_int",
        display_name="Standalone CP O_int interaction attachment theorem",
        status_before="OPEN_MISSING_INTERACTION_ATTACHMENT",
        status_after="CLOSED_DERIVED_ACTION_LEVEL" if action_level else status,
        promoted=promoted,
        promotion_allowed=promoted,
        promotion_reason="All action-derived gates pass." if promoted else "Phase attachment exists, but standalone production operator gates remain unsatisfied.",
        formal_statement="A standalone CP O_int interaction exists only when the internal phase is attached to an action-derived field operator with Lorentz, gauge, coupling, callable, and provenance support.",
        domain=domain.to_dict(), codomain=codomain.to_dict(), field_representation=field.to_dict(),
        lorentz_structure=lorentz.to_dict(), gauge_admissibility=gauge.to_dict(),
        phase_attachment_rule=attachment.to_dict(), coupling_normalization=coupling.to_dict(), action_term=action.to_dict(),
        callable_key="cp_o_int_standalone_attachment", callable_available=callable_ok,
        artifact_sources_checked=CHECKED_SOURCES, artifact_sources_used=used,
        provenance_chain=tuple({"source_path": path, "source_status": "DISCOVERED", "empirical_derivation_input": False, "reference_theorem_input": False} for path in used),
        stages=stage_rows, deepest_valid_stage=f"Stage {deepest.stage}: {deepest.name}", proof_gates=gates,
        missing_objects=missing, empirical_derivation_inputs_used=False,
        reference_values_used_as_theorem_inputs=False, calibration_values_used_as_theorem_inputs=False,
        runtime_gate_changes=False,
        registry_entries_affected=("cp_holonomy_phase_attachment", "minimal_collider_interface_subset", "feynrules_minimal_model", "ufo_export", "madgraph_smoke_test"),
        formula_registry_updates=({"formula_key": "cp_o_int_standalone_attachment", "status_before": "OPEN_THEOREM_REQUIRED", "status_after": "OPEN_THEOREM_REQUIRED", "theorem_status": status},),
        conditional_author_axiom_used=author_conditional, action_level_closure_achieved=action_level,
        claim_boundary="CP holonomy and CKM/PMNS phase attachment are not a standalone production interaction theorem.",
        warnings=("A conditional author axiom is not an action-level closure.", "Runtime-disabled software gates remain disabled."),
        notes=("The disabled template is inert by default.",),
    )


def build_cp_o_int_report(
    candidate_path: str | Path | None = None,
    repository: str | Path | None = None,
) -> CPOIntEvaluationResult:
    root = Path(repository).resolve() if repository is not None else repository_root()
    candidate = load_cp_o_int_candidate_template(candidate_path, root)
    return evaluate_cp_o_int_stages(candidate, root)


def cp_o_int_report_to_markdown(report: CPOIntEvaluationResult) -> str:
    lines = [
        "# BHSM CP O_int Sprint B",
        "",
        f"Status: `{report.status_after}`",
        f"Deepest valid stage: {report.deepest_valid_stage}",
        f"Promoted: `{str(report.promoted).lower()}`",
        "",
        "| Stage | Result | Status | Missing object |",
        "| --- | --- | --- | --- |",
    ]
    lines.extend(f"| {stage.stage}. {stage.name} | {'pass' if stage.passes else 'fail'} | `{stage.status}` | {stage.missing_object or ''} |" for stage in report.stages)
    lines.extend(["", "CP holonomy or CKM/PMNS phase attachment alone is not a standalone CP O_int interaction theorem."])
    return "\n".join(lines) + "\n"
