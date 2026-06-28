"""Local-only provenance search for charged closure inputs."""

from __future__ import annotations

from pathlib import Path

from .common import ChargedSourceSearchResult, repository_root


SOURCE_PATHS = (
    "artifacts/charged_boundary_bridge_values_v1.json",
    "artifacts/CKM_no_fit_operator_output_v1.json",
    "artifacts/CP_no_fit_holonomy_output_v1.json",
    "artifacts/common_scale_boundary_transport_v1.json",
    "data/charged_stiffness_action_selector_v1.json",
    "data/bhsm_charged_hessian_source_audit.json",
    "data/charged_suppression_operator_kernel_v1.json",
    "data/incidence_normalized_overlap_bridge_source.json",
    "audits/charged_lepton_eta_derivation_audit.json",
    "audits/charged_lepton_partial_derivation_consolidation_audit.json",
    "audits/ckm_mixing_exponent_derivation_audit.json",
)


def search_charged_closure_sources(repository: str | Path | None = None) -> ChargedSourceSearchResult:
    root = repository_root(repository)
    found = tuple(path for path in SOURCE_PATHS if (root / path).is_file())
    missing = tuple(path for path in SOURCE_PATHS if not (root / path).is_file())
    return ChargedSourceSearchResult(
        status="CHARGED_SOURCE_INVENTORY_COMPLETE" if not missing else "CHARGED_SOURCE_INVENTORY_INCOMPLETE",
        source_paths=SOURCE_PATHS,
        sources_found=found,
        sources_missing=missing,
        artifact_backed_values_found=(
            "Pi_l=1/7, Pi_u=2/7, Pi_d=4/7",
            "g_bridge=16/189 conditional factorization",
            "charged beta/kappa coefficient table",
            "frozen CKM angle and phase formulas",
        ),
        conditional_sources_found=(
            "trace-normalized charged suppression kernel",
            "alpha/pi stochastic-strength chain",
            "tau-suppressed higher CKM channels from author axiom",
            "weak-double projection bridge",
        ),
        open_sources=(
            "complete charged action normalization",
            "unique rho_ch selector",
            "eta_l complete action source and transport normalization",
            "CKM 1/16 action/projector/transport derivation",
            "nontrivial cross-scale charged transport",
        ),
        empirical_inputs_used=False,
        frozen_predictions_changed=False,
        official_prediction_logic_changed=False,
        claim_boundary="Local artifacts expose charged values and conditional source chains, not a complete charged action theorem.",
    )
