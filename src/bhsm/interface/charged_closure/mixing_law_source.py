"""Audit provenance of the frozen charged-sector CKM mixing law."""

from __future__ import annotations

import json
from pathlib import Path

from .common import ChargedMixingLawResult, repository_root


SOURCES = (
    "artifacts/CKM_no_fit_operator_output_v1.json",
    "artifacts/CP_no_fit_holonomy_output_v1.json",
    "src/ckm_structural_source.py",
    "artifacts/common_scale_boundary_transport_v1.json",
)


def derive_or_locate_charged_mixing_law_source(
    repository: str | Path | None = None,
) -> ChargedMixingLawResult:
    root = repository_root(repository)
    ckm = json.loads((root / SOURCES[0]).read_text(encoding="utf-8"))
    transport = json.loads((root / SOURCES[3]).read_text(encoding="utf-8"))
    formulas = ckm["canonical_CKM_higher_channel_source_theorem"]
    conditional = ckm["CKM_higher_channels"] == "DERIVED_CONDITIONAL_FROM_AUTHOR_AXIOM"
    return ChargedMixingLawResult(
        status="CONDITIONAL_CHARGED_MIXING_LAW_CANDIDATE" if conditional else "OPEN_MISSING_CHARGED_MIXING_LAW_SOURCE",
        theta12_formula=formulas["theta12_CKM"],
        theta23_formula=formulas["theta23_CKM"],
        theta13_formula=formulas["theta13_CKM"],
        delta_formula=formulas["delta_BH"],
        theta12_source_status="ARTIFACT_BACKED",
        theta23_source_status="CONDITIONAL_CHARGED_MIXING_LAW_CANDIDATE",
        theta13_source_status="CONDITIONAL_CHARGED_MIXING_LAW_CANDIDATE",
        delta_source_status="ARTIFACT_BACKED",
        mixing_law_source_status="CONDITIONAL_CHARGED_MIXING_LAW_CANDIDATE",
        source_artifacts=SOURCES,
        empirical_inputs_used=False,
        frozen_ckm_changed=False,
        official_prediction_logic_changed=False,
        remaining_missing_object=(
            "action/projection theorem for tau-suppressed higher channels and nontrivial charged transport"
            if transport["external_empirical_RG_transport"] == "OPEN_SEPARATE_LAYER"
            else "complete charged mixing action theorem"
        ),
        claim_boundary=(
            "The frozen CKM formulas are artifact-backed outputs. Higher-channel tau scaling is conditional on "
            "an author axiom, not a complete charged action derivation."
        ),
    )
