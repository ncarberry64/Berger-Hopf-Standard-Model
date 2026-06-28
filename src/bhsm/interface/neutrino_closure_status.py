"""Canonical public status for BHSM neutral-sector closure."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


DIMENSIONLESS_PROPAGATION_CLOSURE_STATUS = "CONDITIONAL_DIMENSIONLESS_PROPAGATION_CLOSURE"
NEUTRAL_SPECTRAL_MASS_THEOREM_STATUS = "CONDITIONAL_NEUTRAL_SPECTRAL_MASS_CANDIDATE"
MEASUREMENT_SUPPORTED_ADMISSIBLE_POSITIVITY_STATUS = (
    "CONDITIONAL_MEASUREMENT_SUPPORTED_NEUTRAL_POSITIVITY_CANDIDATE"
)
ACTION_DERIVED_RESPONSE_CONE_STATUS = "CONDITIONAL_ACTION_DERIVED_RESPONSE_CONE_CANDIDATE"
DIMENSIONFUL_EV_GEV_MASS_CLOSURE_STATUS = "DIMENSIONFUL_MASS_NOT_AVAILABLE"

NEUTRINO_PUBLIC_STATUS = (
    "BHSM has conditional dimensionless neutrino propagation closure, a conditional neutral "
    "spectral-mass theorem, and conditional measurement-supported admissible neutral positivity. "
    "Physical eV/GeV neutrino mass closure remains open pending a numeric neutral stiffness length "
    "sqrt(A_nu/Z_nu), a physical K_neutral,eff map in m^-2, and complete-action derivation of the "
    "admissible response cone."
)

PUBLIC_REPO_STATUS = (
    "BHSM is an artifact-backed computational framework for Berger-Hopf boundary-mode physics. "
    "Current public status: structural architecture integrated conditional; frozen predictions "
    "unchanged; physical eV/GeV neutrino mass closure remains open; external HEP runtime integration "
    "remains gated."
)

REMAINING_MISSING_OBJECTS = (
    "numeric sqrt(A_nu/Z_nu) in metres",
    "physical K_neutral,eff in m^-2",
    "complete-action derivation of the admissible response cone",
)


@dataclass(frozen=True)
class V15StatusStabilizationReport:
    stack_merged: bool
    merge_path: str
    public_base_branch: str
    dimensionless_propagation_closure_status: str
    neutral_spectral_mass_theorem_status: str
    measurement_supported_admissible_positivity_status: str
    action_derived_response_cone_status: str
    dimensionful_ev_gev_mass_closure_status: str
    remaining_missing_objects: tuple[str, ...]
    frozen_predictions_changed: bool
    official_prediction_logic_changed: bool
    empirical_inputs_used: bool
    claim_boundary: str
    public_repo_status: str
    external_review_ready: bool
    physical_mass_emitted: bool = False
    raw_neutral_kernel_psd_claimed: bool = False
    complete_neutral_action_claimed: bool = False
    internet_required: bool = False
    external_hep_tools_required: bool = False

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["remaining_missing_objects"] = list(self.remaining_missing_objects)
        return payload


def build_v1_5_status_stabilization_report() -> V15StatusStabilizationReport:
    """Build the fail-closed public status record for the integrated v1.5 stack."""

    return V15StatusStabilizationReport(
        stack_merged=True,
        merge_path="aggregate_integration_branch_from_main",
        public_base_branch="main",
        dimensionless_propagation_closure_status=DIMENSIONLESS_PROPAGATION_CLOSURE_STATUS,
        neutral_spectral_mass_theorem_status=NEUTRAL_SPECTRAL_MASS_THEOREM_STATUS,
        measurement_supported_admissible_positivity_status=(
            MEASUREMENT_SUPPORTED_ADMISSIBLE_POSITIVITY_STATUS
        ),
        action_derived_response_cone_status=ACTION_DERIVED_RESPONSE_CONE_STATUS,
        dimensionful_ev_gev_mass_closure_status=DIMENSIONFUL_EV_GEV_MASS_CLOSURE_STATUS,
        remaining_missing_objects=REMAINING_MISSING_OBJECTS,
        frozen_predictions_changed=False,
        official_prediction_logic_changed=False,
        empirical_inputs_used=False,
        claim_boundary=NEUTRINO_PUBLIC_STATUS,
        public_repo_status=PUBLIC_REPO_STATUS,
        external_review_ready=True,
    )


def neutrino_closure_status_to_markdown(report: V15StatusStabilizationReport) -> str:
    """Render the canonical split without introducing a physical mass value."""

    lines = [
        "# BHSM Neutrino Closure Status",
        "",
        report.public_repo_status,
        "",
        report.claim_boundary,
        "",
        "| Closure component | Status |",
        "| --- | --- |",
        f"| Dimensionless propagation closure | `{report.dimensionless_propagation_closure_status}` |",
        f"| Neutral spectral-mass theorem | `{report.neutral_spectral_mass_theorem_status}` |",
        f"| Measurement-supported admissible positivity | `{report.measurement_supported_admissible_positivity_status}` |",
        f"| Action-derived response cone | `{report.action_derived_response_cone_status}` |",
        f"| Physical eV/GeV mass closure | `{report.dimensionful_ev_gev_mass_closure_status}` |",
        "",
        "## Remaining Missing Objects",
        "",
        *(f"- {item}" for item in report.remaining_missing_objects),
        "",
        "No physical eV/GeV neutrino mass is emitted.",
    ]
    return "\n".join(lines) + "\n"


def write_v1_5_status_stabilization_artifact(path: str | Path) -> Path:
    """Write the deterministic machine-readable review artifact."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(build_v1_5_status_stabilization_report().to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return destination
