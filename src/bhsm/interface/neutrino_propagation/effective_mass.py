"""Dimensionless BHSM neutrino propagation-mass candidate."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from .common import (
    BackgroundCoupling,
    CurvatureThreshold,
    EffectivePropagationMass,
    NeutralKernelArtifact,
    NeutralScaleLaw,
    PropagationState,
    provenance_rows,
    repository_path,
)
from .curvature_threshold import threshold_response

if TYPE_CHECKING:
    from ..neutrino_scale.common import NeutralScaleClosureResult


BOUNDARY_PACKAGE = "artifacts/BHSM_boundary_no_fit_prediction_package_v1.json"


def load_neutral_scale_law(repository: str | Path | None = None) -> NeutralScaleLaw:
    root = repository_path(repository)
    path = root / BOUNDARY_PACKAGE
    if not path.is_file():
        raise FileNotFoundError(f"boundary package is missing: {BOUNDARY_PACKAGE}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    profile = payload.get("profile_scale", {})
    if "tau" not in profile:
        raise ValueError("boundary package does not contain dimensionless tau")
    return NeutralScaleLaw(
        dimensionless_scale=float(profile["tau"]),
        scale_symbol="tau",
        effective_mass_eV_per_unit=None,
        effective_mass_GeV_per_unit=None,
        status="OPEN_MISSING_NEUTRAL_SCALE",
        source_artifacts=(BOUNDARY_PACKAGE,),
        missing_object="artifact-backed dimensionful neutral scale mapping BHSM boundary response to eV/GeV",
        claim_boundary="Tau supplies an artifact-backed dimensionless response scale, not an eV/GeV conversion.",
    )


def compute_neutrino_propagation_mass(
    kernel: NeutralKernelArtifact,
    state: PropagationState,
    threshold: CurvatureThreshold,
    scale_law: NeutralScaleLaw,
    background: BackgroundCoupling,
    repository: str | Path | None = None,
    neutral_scale_result: NeutralScaleClosureResult | None = None,
) -> EffectivePropagationMass:
    """Compute the conditional dimensionless response without external inputs."""

    response_norm, coupled, excess = threshold_response(kernel, state, threshold, background)
    dimensionless = scale_law.dimensionless_scale * excess
    if state.propagation_response == 0:
        dimensionless = 0.0
    scale_ev = scale_law.effective_mass_eV_per_unit
    scale_gev = scale_law.effective_mass_GeV_per_unit
    status = scale_law.status
    if neutral_scale_result is not None:
        scale_ev = neutral_scale_result.scale_value_eV
        scale_gev = neutral_scale_result.scale_value_GeV
        status = neutral_scale_result.status_after
    mass_ev = dimensionless * scale_ev if scale_ev is not None else None
    mass_gev = dimensionless * scale_gev if scale_gev is not None else None
    sources = (kernel.source_artifact, *threshold.source_artifacts, *scale_law.source_artifacts)
    return EffectivePropagationMass(
        state_label=state.label,
        propagation_response=state.propagation_response,
        kernel_response_norm=response_norm,
        coupled_response=coupled,
        threshold_excess=excess,
        effective_mass_dimensionless=dimensionless,
        effective_mass_eV=mass_ev,
        effective_mass_GeV=mass_gev,
        status=status,
        provenance=provenance_rows(repository_path(repository), tuple(dict.fromkeys(sources))),
        claim_boundary=(
            "A dimensionless BHSM response is not, by itself, a physical eV/GeV mass. "
            "Physical units are emitted only when an accepted neutral scale result supplies a valid unit source; "
            "a legacy curvature functional without numeric r_prop, physical k_neutral,eff, and a passing mass-dimension audit is insufficient."
        ),
    )
