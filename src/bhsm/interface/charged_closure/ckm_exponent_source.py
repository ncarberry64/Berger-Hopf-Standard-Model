"""Audit the CKM 1/16 mixing-dressing exponent source."""

from __future__ import annotations

import json
from pathlib import Path

from .common import CKMExponentSourceResult, repository_root


SOURCES = (
    "audits/ckm_mixing_exponent_derivation_audit.json",
    "theory/ckm_1_16_channel_dilution.md",
    "artifacts/common_scale_boundary_transport_v1.json",
    "data/bhsm_weak_double_projection_zvirt_bridge.json",
)


def derive_or_locate_ckm_exponent_source(
    repository: str | Path | None = None,
) -> CKMExponentSourceResult:
    root = repository_root(repository)
    audit = json.loads((root / SOURCES[0]).read_text(encoding="utf-8"))
    transport = json.loads((root / SOURCES[2]).read_text(encoding="utf-8"))
    weak = json.loads((root / SOURCES[3]).read_text(encoding="utf-8"))
    selected_by_residual = bool(audit["selected_by_residual"])
    action_source_found = audit["classification"] != "OPEN_DERIVATION_REQUIRED"
    projector_source_found = weak["WEAK_DOUBLE_PROJECTION"] == "1/2"
    return CKMExponentSourceResult(
        status="ARTIFACT_BACKED_CKM_EXPONENT_SOURCE" if action_source_found and not selected_by_residual else "OPEN_MISSING_CKM_EXPONENT_DERIVATION",
        exponent="1/16" if float(audit["exponent"]) == 1.0 / 16.0 else str(audit["exponent"]),
        candidate_label=audit["candidate_label"],
        historical_candidate_selected_by_residual=selected_by_residual,
        residual_used_as_theorem_input=False,
        action_source_found=action_source_found,
        projector_source_found=projector_source_found,
        cross_scale_transport_status=(
            "OPEN_MISSING_CROSS_SCALE_TRANSPORT"
            if transport["external_empirical_RG_transport"] == "OPEN_SEPARATE_LAYER"
            else "CONDITIONAL_CKM_EXPONENT_SOURCE_CANDIDATE"
        ),
        source_artifacts=SOURCES,
        empirical_inputs_used=False,
        frozen_ckm_changed=False,
        official_prediction_logic_changed=False,
        remaining_missing_object="pre-comparison action/projector/transport theorem forcing the 1/16 exponent",
        claim_boundary=(
            "The 1/16 exponent remains a historical exploratory candidate selected after residual comparison. "
            "The weak-double projector does not by itself derive that exponent."
        ),
    )
