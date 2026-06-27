"""Dimensionless BHSM neutrino propagation-mass candidate."""

from __future__ import annotations

import json
from pathlib import Path

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
) -> EffectivePropagationMass:
    """Compute the conditional dimensionless response without external inputs."""

    response_norm, coupled, excess = threshold_response(kernel, state, threshold, background)
    dimensionless = scale_law.dimensionless_scale * excess
    if state.propagation_response == 0:
        dimensionless = 0.0
    mass_ev = (
        dimensionless * scale_law.effective_mass_eV_per_unit
        if scale_law.effective_mass_eV_per_unit is not None
        else None
    )
    mass_gev = (
        dimensionless * scale_law.effective_mass_GeV_per_unit
        if scale_law.effective_mass_GeV_per_unit is not None
        else None
    )
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
        status=scale_law.status,
        provenance=provenance_rows(repository_path(repository), tuple(dict.fromkeys(sources))),
        claim_boundary="Dimensionless conditional response only; it is not an ordinary static rest mass or a numerical eV/GeV prediction.",
    )
