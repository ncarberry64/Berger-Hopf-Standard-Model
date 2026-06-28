"""Locate repository sources relevant to a possible common-16 generator."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from .common import Common16SourceSearch, repository_root


SOURCE_PATHS = (
    "data/charged_suppression_operator_kernel_v1.json",
    "data/incidence_normalized_overlap_bridge_source.json",
    "data/charged_stiffness_action_selector_v1.json",
    "data/bhsm_charged_hessian_source_audit.json",
    "audits/ckm_mixing_exponent_derivation_audit.json",
    "artifacts/common_scale_boundary_transport_v1.json",
    "artifacts/charged_boundary_bridge_values_v1.json",
)


def search_common_16_sources(repository: str | Path | None = None) -> Common16SourceSearch:
    root = repository_root(repository)
    found = tuple(path for path in SOURCE_PATHS if (root / path).is_file())
    missing = tuple(path for path in SOURCE_PATHS if not (root / path).is_file())
    kernel = json.loads((root / SOURCE_PATHS[0]).read_text(encoding="utf-8"))
    bridge = json.loads((root / SOURCE_PATHS[1]).read_text(encoding="utf-8"))
    selector = json.loads((root / SOURCE_PATHS[2]).read_text(encoding="utf-8"))
    ckm = json.loads((root / SOURCE_PATHS[4]).read_text(encoding="utf-8"))
    rho_three = next(
        row for row in selector["selector_candidates"] if row["rho_ch"] == "3"
    )
    return Common16SourceSearch(
        status="COMMON_16_SOURCE_SET_LOCATED" if not missing else "COMMON_16_SOURCE_SET_INCOMPLETE",
        source_paths=SOURCE_PATHS,
        source_paths_found=found,
        source_paths_missing=missing,
        omega_values=kernel["incidence_ranks"],
        rho_ch_candidate=int(rho_three["rho_ch"]),
        bridge_value=bridge["g_ch_factorization_value"],
        ckm_candidate_exponent=str(Fraction(str(ckm["exponent"]))),
        historical_candidate_selected_by_residual=bool(ckm["selected_by_residual"]),
        empirical_residual_used_as_theorem_input=False,
        frozen_predictions_changed=False,
        official_prediction_logic_changed=False,
    )
