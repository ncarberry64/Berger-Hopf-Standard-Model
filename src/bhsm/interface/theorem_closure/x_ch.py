"""Executable, fail-closed attempt at the X_ch production theorem."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from ..artifact_sources import load_artifact_json, repository_root
from ..boundary_adapters import load_charged_bridge_constants_artifact
from .common import ActionTermCandidate, OperatorDefinition, TheoremClosureResult, TheoremStatement
from .proof_gates import build_proof_gates, promotion_allowed

THEOREM_PATH = "artifacts/BHSM_x_ch_charged_boundary_response_theorem_v1_1.json"


def evaluate_x_ch_candidate(
    inputs: Mapping[str, Any] | None = None,
    repository: str | Path | None = None,
) -> TheoremClosureResult:
    """Localize the X_ch gap without supplying the missing interaction theorem."""

    del inputs  # The closure audit deliberately takes no empirical or calibration input.
    root = Path(repository).resolve() if repository is not None else repository_root()
    path = root / THEOREM_PATH
    artifact = load_artifact_json(path) if path.is_file() else {}
    charged = load_charged_bridge_constants_artifact(root)
    missing = str(artifact.get("missing_if_open", "explicit X_ch production interaction theorem"))
    sources = tuple(path for path in (THEOREM_PATH, charged.provenance.source_path) if (root / path).is_file())
    statement = TheoremStatement(
        "X_ch",
        "A charged boundary-response source defines a production interaction only if X_ch has an action-derived field representation, Lorentz structure, admissible current attachment, and normalized coupling.",
        ("charged boundary values are source data only", "X_ch is not identified with W_mu without a theorem"),
        "FORMAL_CONDITIONAL_STATEMENT",
    )
    operator = OperatorDefinition(
        "X_ch charged boundary-response candidate",
        "charged boundary source channels (candidate; physical field domain not derived)",
        "production interaction amplitudes (candidate; codomain not established)",
        "X_ch^mu J_mu^boundary",
        "INCOMPLETE_MISSING_FIELD_AND_CURRENT_THEOREM",
    )
    action = ActionTermCandidate(
        "L_X_ch",
        "undefined pending action-derived X_ch field content, current attachment, and coupling normalization",
        "OPEN_MISSING_ACTION_SOURCE",
        sources,
        (missing,),
    )
    evidence = {
        "G01": True, "G02": False, "G03": False, "G04": False, "G05": True,
        "G06": bool(artifact and charged.source_status == "DISCOVERED"), "G07": bool(sources),
        "G08": not bool(artifact.get("empirical_derivation_inputs_used", False)), "G09": True,
        "G10": True, "G11": True, "G12": True, "G13": bool(artifact),
        "G14": False, "G15": False, "G16": True, "G17": True,
    }
    texts = {
        "G01": "A formal conditional production-eligibility statement is encoded.",
        "G05": "The closure-attempt callable has mapping input and TheoremClosureResult output schemas.",
        "G06": "The v1.1 theorem blocker and charged boundary package are local machine-readable artifacts.",
        "G07": "Every inspected local source is recorded in the result.",
        "G08": "The source artifact records empirical_derivation_inputs_used=false.",
        "G09": "The attempt reads no reference or PDG values.",
        "G10": "Local source presence and non-promotion consistency checks pass.",
        "G11": "The sprint generates a separate registry update proposal.",
        "G12": "The closure claim policy forbids production promotion.",
        "G13": "The existing blocker artifact records OPEN_EXACT_MISSING_THEOREM.",
        "G16": "No calibration input is accepted or used.",
        "G17": missing,
    }
    limits = {
        "G02": "Physical field domain and production-amplitude codomain are not derived.",
        "G03": "No action-derived X_ch interaction term exists.",
        "G04": "Only the closure-attempt callable exists; no production X_ch callable exists.",
        "G14": "Spin, gauge representation, and allowed/forbidden production channels are not fixed by theorem.",
        "G15": "Coupling normalization and dimensional policy are missing.",
    }
    gates = build_proof_gates(evidence, texts, limits)
    promoted = promotion_allowed(gates)
    return TheoremClosureResult(
        theorem_key="X_ch",
        display_name="X_ch charged boundary-response production theorem",
        closure_status="CLOSED_DERIVED_ACTION_LEVEL" if promoted else "OPEN_EXACT_MISSING_THEOREM",
        proof_gates=gates,
        formal_statement=statement,
        domain=operator.domain,
        codomain=operator.codomain,
        operator_definition=operator,
        action_term=action,
        callable_key="x_ch_production_vertex",
        callable_available=promoted,
        artifact_sources=sources,
        provenance=({"source_path": THEOREM_PATH, "source_status": "DISCOVERED" if artifact else "ARTIFACT_NOT_FOUND", "empirical_derivation_input": False, "reference_comparison_input": False}, charged.to_dict()),
        empirical_derivation_inputs_used=False,
        reference_values_used_as_derivation_inputs=False,
        calibration_inputs_used=False,
        registry_entries_affected=("charged_boundary_response_matrix", "minimal_collider_interface_subset", "feynrules_minimal_model", "ufo_export", "madgraph_smoke_test"),
        status_before=str(artifact.get("theorem_status", "OPEN_EXACT_MISSING_THEOREM")),
        status_after="CLOSED_DERIVED_ACTION_LEVEL" if promoted else "OPEN_EXACT_MISSING_THEOREM",
        promotion_allowed=promoted,
        promotion_reason="All production proof gates pass." if promoted else "Action, field representation, current attachment, admissibility, and coupling gates fail.",
        missing_objects=() if promoted else (missing,),
        claim_boundary="X_ch is not a production-ready interaction without an explicit action-backed theorem.",
        warnings=("A closure-attempt callable is not the missing production interaction callable.", "Runtime software gates remain disabled."),
        notes=("The charged boundary constants are artifact-backed source data.",),
    )
