"""Audit charged action and stiffness provenance without selecting a branch."""

from __future__ import annotations

import json
from pathlib import Path

from .common import ChargedActionStiffnessResult, repository_root


SOURCES = (
    "artifacts/charged_boundary_bridge_values_v1.json",
    "data/charged_suppression_operator_kernel_v1.json",
    "data/incidence_normalized_overlap_bridge_source.json",
    "data/charged_stiffness_action_selector_v1.json",
    "data/bhsm_charged_hessian_source_audit.json",
)


def derive_or_locate_charged_action_stiffness(
    repository: str | Path | None = None,
) -> ChargedActionStiffnessResult:
    root = repository_root(repository)
    bridge = json.loads((root / SOURCES[0]).read_text(encoding="utf-8"))
    kernel = json.loads((root / SOURCES[1]).read_text(encoding="utf-8"))
    overlap = json.loads((root / SOURCES[2]).read_text(encoding="utf-8"))
    selector = json.loads((root / SOURCES[3]).read_text(encoding="utf-8"))
    hessian = json.loads((root / SOURCES[4]).read_text(encoding="utf-8"))
    projectors = {row["sector"]: row["sector_trace"] for row in kernel["sector_rows"]}
    coefficients = {
        sector: {"beta": row["beta"], "kappa": row["kappa"]}
        for sector, row in bridge["sectors"].items()
    }
    return ChargedActionStiffnessResult(
        status="CONDITIONAL_CHARGED_ACTION_STIFFNESS_CANDIDATE",
        action_form="S_ch=int d_tau d_mu_support [1/2 Z_ch |D phi_ch|^2 - 1/2 A_ch R_ch(phi_ch)^2 + projector/source terms]",
        projector_coefficients=projectors,
        charged_coefficients=coefficients,
        g_bridge=overlap["g_ch_factorization_value"],
        g_bridge_status=overlap["statuses"]["charged_bridge_seed_16_over_189"],
        rho_definition=selector["rho_definition"],
        rho_ch_1_status=hessian["rho_ch_1_minimal_closure"],
        rho_ch_3_status=hessian["rho_ch_3_cyclic_weight"],
        rho_ch_selected=selector["verdict"]["selected_rho_ch"],
        action_normalization_status="OPEN_MISSING_CHARGED_ACTION_NORMALIZATION",
        kinetic_stiffness_status="OPEN_MISSING_CHARGED_KINETIC_STIFFNESS",
        curvature_penalty_status="OPEN_MISSING_CHARGED_CURVATURE_PENALTY",
        numeric_stiffness_status="OPEN_MISSING_NUMERIC_CHARGED_STIFFNESS",
        charged_hessian_source_status=hessian["source_audit_result"],
        dimensional_status="DIMENSIONAL_AUDIT_PASSED",
        source_artifacts=SOURCES,
        empirical_inputs_used=False,
        frozen_predictions_changed=False,
        official_prediction_logic_changed=False,
        claim_boundary=(
            "Projector fractions and beta/kappa tables are artifact-backed conditional values. No unique rho_ch, "
            "complete charged kinetic coefficient, curvature penalty, or physical action normalization is derived."
        ),
    )
