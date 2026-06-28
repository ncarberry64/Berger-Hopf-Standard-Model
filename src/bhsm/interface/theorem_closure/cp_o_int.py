"""Executable audit of standalone CP O_int attachment."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from ..artifact_sources import load_artifact_json, repository_root
from ..matrix_adapters import load_cp_phase_artifact
from .common import ActionTermCandidate, OperatorDefinition, TheoremClosureResult, TheoremStatement
from .proof_gates import build_proof_gates, promotion_allowed

THEOREM_PATH = "artifacts/BHSM_cp_holonomy_o_int_attachment_theorem_v1_1.json"


def evaluate_cp_o_int_candidate(
    inputs: Mapping[str, Any] | None = None,
    repository: str | Path | None = None,
) -> TheoremClosureResult:
    """Verify the phase seed and localize the absent standalone interaction."""

    del inputs
    root = Path(repository).resolve() if repository is not None else repository_root()
    path = root / THEOREM_PATH
    artifact = load_artifact_json(path) if path.is_file() else {}
    phase = load_cp_phase_artifact(root)
    missing = str(artifact.get("missing_if_open", "standalone CP O_int interaction attachment"))
    sources = tuple(path for path in (THEOREM_PATH, phase.provenance.source_path) if (root / path).is_file())
    statement = TheoremStatement(
        "cp_o_int",
        "The BHSM holonomy phase defines a standalone interaction only if an action-derived O_int fixes field content, Lorentz and gauge structure, coupling placement, and admissible sectors.",
        ("delta_BH=pi/3 is a phase seed", "matrix-phase attachment is not a standalone interaction"),
        "FORMAL_CONDITIONAL_STATEMENT",
    )
    operator = OperatorDefinition(
        "standalone O_int candidate",
        "unspecified production fields",
        "unspecified CP-sensitive production amplitudes",
        "exp(i*delta_BH) O_int + h.c.",
        "PHASE_DEFINED_INTERACTION_OPERATOR_MISSING",
    )
    action = ActionTermCandidate(
        "L_CP_O_int",
        "exp(i*pi/3) O_int + h.c.; O_int undefined",
        "OPEN_MISSING_INTERACTION_ATTACHMENT",
        sources,
        (missing,),
    )
    evidence = {
        "G01": True, "G02": False, "G03": False, "G04": False, "G05": True,
        "G06": bool(artifact and phase.source_status == "DISCOVERED"), "G07": bool(sources),
        "G08": not bool(artifact.get("empirical_derivation_inputs_used", False)), "G09": True,
        "G10": True, "G11": True, "G12": True, "G13": bool(artifact),
        "G14": False, "G15": False, "G16": True, "G17": True,
    }
    texts = {
        "G01": "A formal standalone-interaction eligibility statement is encoded.",
        "G05": "The closure-attempt callable has explicit schemas.",
        "G06": "The holonomy phase and v1.1 blocker are local machine-readable artifacts.",
        "G07": "The phase and blocker sources are recorded.",
        "G08": "The artifacts record no empirical derivation inputs.",
        "G09": "No observed CP or PDG value is read.",
        "G10": "delta_BH and Z6 phase consistency checks pass; standalone promotion remains false.",
        "G11": "The sprint generates a separate registry update proposal.",
        "G12": "The claim policy separates phase attachment from standalone interaction closure.",
        "G13": "The existing blocker artifact records the missing O_int theorem.",
        "G16": "No calibration input is accepted or used.",
        "G17": missing,
    }
    limits = {
        "G02": "Standalone field domain and production-amplitude codomain are absent.",
        "G03": "O_int has no field, Lorentz, gauge, or coupling definition.",
        "G04": "No standalone CP interaction callable exists.",
        "G14": "Gauge and sector admissibility cannot be tested without O_int.",
        "G15": "Coupling dimension and normalization are absent.",
    }
    gates = build_proof_gates(evidence, texts, limits)
    promoted = promotion_allowed(gates)
    return TheoremClosureResult(
        theorem_key="cp_o_int",
        display_name="Standalone CP O_int attachment theorem",
        closure_status="CLOSED_DERIVED_ACTION_LEVEL" if promoted else "OPEN_MISSING_INTERACTION_ATTACHMENT",
        proof_gates=gates,
        formal_statement=statement,
        domain=operator.domain,
        codomain=operator.codomain,
        operator_definition=operator,
        action_term=action,
        callable_key="cp_o_int_standalone_attachment",
        callable_available=promoted,
        artifact_sources=sources,
        provenance=({"source_path": THEOREM_PATH, "source_status": "DISCOVERED" if artifact else "ARTIFACT_NOT_FOUND", "empirical_derivation_input": False, "reference_comparison_input": False}, phase.to_dict()),
        empirical_derivation_inputs_used=False,
        reference_values_used_as_derivation_inputs=False,
        calibration_inputs_used=False,
        registry_entries_affected=("cp_holonomy_phase_attachment", "minimal_collider_interface_subset", "feynrules_minimal_model", "ufo_export", "madgraph_smoke_test"),
        status_before=str(artifact.get("theorem_status", "OPEN_EXACT_MISSING_THEOREM")),
        status_after="CLOSED_DERIVED_ACTION_LEVEL" if promoted else "OPEN_MISSING_INTERACTION_ATTACHMENT",
        promotion_allowed=promoted,
        promotion_reason="All standalone-interaction proof gates pass." if promoted else "O_int definition, action, callable, admissibility, and dimensional gates fail.",
        missing_objects=() if promoted else (missing,),
        claim_boundary="The CP phase seed is not a standalone production interaction without an explicit O_int attachment theorem.",
        warnings=("CKM/PMNS phase attachment does not define a standalone CP vertex.", "Runtime software gates remain disabled."),
        notes=("delta_BH and Z6 phase are artifact-backed internal values.",),
    )


def evaluate_cp_o_int_sprint_b(
    candidate_path: str | Path | None = None,
    repository: str | Path | None = None,
):
    """Run the focused staged Sprint B evaluator without changing Sprint A."""

    from .cp_o_int_report import build_cp_o_int_report

    return build_cp_o_int_report(candidate_path, repository)


def evaluate_cp_o_int_sprint_c(
    template_path: str | Path | None = None,
    repository: str | Path | None = None,
):
    """Build the source-traced symbolic field/action candidate for Sprint C."""

    from .cp_o_int_sprint_c_report import build_cp_o_int_field_action_report

    return build_cp_o_int_field_action_report(template_path, repository)
