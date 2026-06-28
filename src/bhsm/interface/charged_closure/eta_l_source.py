"""Audit the charged-lepton eta_l source chain."""

from __future__ import annotations

import json
from pathlib import Path

from .common import EtaLSourceResult, repository_root


SOURCES = (
    "audits/charged_lepton_eta_derivation_audit.json",
    "audits/charged_lepton_partial_derivation_consolidation_audit.json",
    "data/charged_suppression_operator_kernel_v1.json",
    "theory/alpha_over_pi_stochastic_strength_derivation.md",
)


def derive_or_locate_eta_l_source(repository: str | Path | None = None) -> EtaLSourceResult:
    root = repository_root(repository)
    historical = json.loads((root / SOURCES[0]).read_text(encoding="utf-8"))
    consolidated = json.loads((root / SOURCES[1]).read_text(encoding="utf-8"))
    kernel = json.loads((root / SOURCES[2]).read_text(encoding="utf-8"))
    conditional = (
        consolidated["does_eta_l_8alpha_9pi_remain_supported"] is True
        and kernel["statuses"]["Pi_f_incidence_projection_fractions"]
        == "DERIVED_CONDITIONAL_FROM_B_SUPP_TRACE"
    )
    return EtaLSourceResult(
        status="CONDITIONAL_ETA_L_SOURCE_CANDIDATE" if conditional else "OPEN_MISSING_ETA_L_ACTION_SOURCE",
        preferred_conditional_formula="eta_l=8*alpha/(9*pi) under the repository Brownian exponent convention",
        fitted_eta_present_in_history=historical["fitted_eta_l"] is not None,
        fitted_eta_used_as_theorem_input=False,
        boundary_projection_status=kernel["statuses"]["Pi_f_incidence_projection_fractions"],
        stochastic_strength_status=consolidated["alpha_pi_status"],
        action_source_status="OPEN_MISSING_ETA_L_ACTION_SOURCE",
        transport_normalization_status="OPEN_MISSING_ETA_L_TRANSPORT_NORMALIZATION",
        exact_value_derived=False,
        source_artifacts=SOURCES,
        empirical_inputs_used=False,
        frozen_predictions_changed=False,
        official_prediction_logic_changed=False,
        remaining_missing_objects=(
            "complete charged stochastic/action generator",
            "independent boundary cycle/time normalization",
            "action-level lepton projection coupling",
            "charged transport normalization",
        ),
        claim_boundary=(
            "The eta_l chain is a conditional source candidate. The historical fitted eta is not used, and no "
            "exact official eta_l value is promoted by this audit."
        ),
    )
