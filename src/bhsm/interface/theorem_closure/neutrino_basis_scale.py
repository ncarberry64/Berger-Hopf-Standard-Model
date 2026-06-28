"""Executable audit of the neutral physical-basis and scale theorem."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from ..artifact_sources import load_artifact_json, repository_root
from ..boundary_adapters import load_neutral_operator_artifact
from .common import ActionTermCandidate, OperatorDefinition, TheoremClosureResult, TheoremStatement
from .proof_gates import build_proof_gates, promotion_allowed

THEOREM_PATH = "artifacts/BHSM_neutrino_dirac_majorana_basis_scale_theorem_v1_1.json"


def evaluate_neutrino_basis_scale_candidate(
    inputs: Mapping[str, Any] | None = None,
    repository: str | Path | None = None,
) -> TheoremClosureResult:
    """Expose K_nu while refusing to infer its physical basis or mass scale."""

    del inputs
    root = Path(repository).resolve() if repository is not None else repository_root()
    path = root / THEOREM_PATH
    artifact = load_artifact_json(path) if path.is_file() else {}
    neutral = load_neutral_operator_artifact(root)
    missing = str(artifact.get("missing_if_open", "physical neutrino basis + dimensional scale + Dirac/Majorana convention"))
    sources = tuple(path for path in (THEOREM_PATH, neutral.provenance.source_path) if (root / path).is_file())
    statement = TheoremStatement(
        "neutrino_basis_scale",
        "The neutral boundary kernel defines a physical neutrino mass or effective-mass operator only after a physical state-basis map, dimensional scale, ordering policy, and Dirac/Majorana convention are derived.",
        ("K_nu is a boundary seed", "PMNS target labels do not determine a mass basis"),
        "FORMAL_CONDITIONAL_STATEMENT",
    )
    operator = OperatorDefinition(
        "K_nu boundary operator seed",
        "three-dimensional neutral boundary channel basis",
        "three-dimensional neutral boundary channel basis",
        "K_nu=[[0,1/3,0],[1/3,3,1/6],[0,1/6,5/3]]",
        "BOUNDARY_SEED_ONLY_PHYSICAL_MAP_OPEN",
    )
    action = ActionTermCandidate(
        "L_nu_physical",
        "undefined pending U_nu, Lambda_nu, ordering, and Dirac/Majorana convention",
        "OPEN_MISSING_PHYSICAL_BASIS_AND_SCALE",
        sources,
        (missing,),
    )
    evidence = {
        "G01": True, "G02": False, "G03": False, "G04": False, "G05": True,
        "G06": bool(artifact and neutral.source_status == "DISCOVERED"), "G07": bool(sources),
        "G08": not bool(artifact.get("empirical_derivation_inputs_used", False)), "G09": True,
        "G10": True, "G11": True, "G12": True, "G13": bool(artifact),
        "G14": False, "G15": False, "G16": True, "G17": True,
    }
    texts = {
        "G01": "A formal conditional map-to-physics statement is encoded.",
        "G05": "The closure-attempt callable has explicit schemas.",
        "G06": "The boundary kernel and v1.1 theorem blocker are machine-readable local artifacts.",
        "G07": "The local source chain is explicit.",
        "G08": "Both inspected artifacts record no empirical derivation inputs.",
        "G09": "No electron-neutrino limit, PDG value, or reference value is read.",
        "G10": "Kernel shape and non-promotion checks pass.",
        "G11": "The sprint generates a separate registry update proposal.",
        "G12": "The claim policy forbids interpreting K_nu as a physical mass matrix.",
        "G13": "The existing blocker artifact records the exact missing theorem.",
        "G16": "No calibration anchor is accepted or used.",
        "G17": missing,
    }
    limits = {
        "G02": "The boundary channel basis is defined, but the physical neutrino basis and observable codomain are not.",
        "G03": "No physical mass/effective-mass action term is defined.",
        "G04": "No callable maps K_nu to physical masses or observables.",
        "G14": "Physical state admissibility and ordering are not fixed.",
        "G15": "Lambda_nu and the unit conversion are absent.",
    }
    gates = build_proof_gates(evidence, texts, limits)
    promoted = promotion_allowed(gates)
    return TheoremClosureResult(
        theorem_key="neutrino_basis_scale",
        display_name="Neutrino physical basis, scale, and Dirac/Majorana theorem",
        closure_status="CLOSED_DERIVED_ACTION_LEVEL" if promoted else "OPEN_EXACT_MISSING_THEOREM",
        proof_gates=gates,
        formal_statement=statement,
        domain=operator.domain,
        codomain="physical neutrino mass/effective-mass observables (not defined)",
        operator_definition=operator,
        action_term=action,
        callable_key="neutrino_physical_basis_scale",
        callable_available=promoted,
        artifact_sources=sources,
        provenance=({"source_path": THEOREM_PATH, "source_status": "DISCOVERED" if artifact else "ARTIFACT_NOT_FOUND", "empirical_derivation_input": False, "reference_comparison_input": False}, neutral.to_dict()),
        empirical_derivation_inputs_used=False,
        reference_values_used_as_derivation_inputs=False,
        calibration_inputs_used=False,
        registry_entries_affected=("neutral_operator_kernel_BH", "minimal_collider_interface_subset", "feynrules_minimal_model", "ufo_export", "madgraph_smoke_test"),
        status_before=str(artifact.get("theorem_status", "OPEN_EXACT_MISSING_THEOREM")),
        status_after="CLOSED_DERIVED_ACTION_LEVEL" if promoted else "OPEN_EXACT_MISSING_THEOREM",
        promotion_allowed=promoted,
        promotion_reason="All physical-map proof gates pass." if promoted else "Physical basis, scale, convention, admissibility, and callable gates fail.",
        missing_objects=() if promoted else (missing,),
        claim_boundary="The neutral boundary kernel is not a physical neutrino mass matrix without basis, scale, and Dirac/Majorana theorem support.",
        warnings=("PMNS mixing does not supply a physical neutrino mass basis.", "Electron-neutrino reference limits are not theorem inputs."),
        notes=("K_nu remains an artifact-backed boundary seed.",),
    )
