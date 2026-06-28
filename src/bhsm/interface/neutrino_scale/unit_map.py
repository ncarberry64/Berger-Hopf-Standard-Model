"""Claim-safe neutral scale law and dimensionful unit mapping."""

from __future__ import annotations

import json
from pathlib import Path

from .artifact_search import ARTIFACT_SOURCES_CHECKED, search_neutral_scale_sources
from .common import (
    NeutralDimensionfulScaleResult,
    NeutralUnitMap,
    provenance_rows,
    repository_path,
)
from .neutral_scale_candidates import BOUNDARY_PACKAGE, build_neutral_scale_candidates
from .threshold_energy_map import build_threshold_energy_map


def derive_neutral_scale_law(
    repository: str | Path | None = None,
) -> NeutralDimensionfulScaleResult:
    root = repository_path(repository)
    profile = json.loads((root / BOUNDARY_PACKAGE).read_text(encoding="utf-8"))["profile_scale"]
    candidates = build_neutral_scale_candidates(root)
    sources = search_neutral_scale_sources(root)
    threshold_map = build_threshold_energy_map(root)
    valid = [row for row in candidates if row.can_map_to_eV and row.status == "DIMENSIONFUL_ARTIFACT"]
    if valid:
        chosen = valid[0]
        scale_ev = float(chosen.value)
        scale_gev = scale_ev * 1.0e-9
        status = "ARTIFACT_BACKED_DIMENSIONFUL_SCALE"
        missing = "none"
        unit_source = chosen.source
    else:
        chosen = next(row for row in candidates if row.candidate_key == "tau")
        scale_ev = None
        scale_gev = None
        status = "OPEN_MISSING_NEUTRAL_SCALE"
        missing = (
            "artifact-backed dimensionful neutral unit anchor and threshold-to-energy map; "
            "the symbolic boundary measure also lacks physical normalization"
        )
        unit_source = None
    used = tuple(
        row.source_path
        for row in sources
        if row.discovered and row.source_category != "EMPIRICAL_FORBIDDEN"
    )
    return NeutralDimensionfulScaleResult(
        theorem_key="neutral_dimensionful_scale",
        status_before="DIMENSIONLESS_ONLY_CLOSURE",
        status_after=status,
        scale_candidate_key=chosen.candidate_key,
        scale_value_dimensionless=float(profile["tau"]),
        scale_value_eV=scale_ev,
        scale_value_GeV=scale_gev,
        unit_available=scale_ev is not None,
        unit_source=unit_source,
        candidate_source=chosen.source,
        artifact_sources_checked=ARTIFACT_SOURCES_CHECKED,
        artifact_sources_used=used,
        provenance=provenance_rows(root, ARTIFACT_SOURCES_CHECKED),
        empirical_derivation_inputs_used=False,
        reference_values_used_as_theorem_inputs=False,
        electron_neutrino_limit_used_as_derivation_input=False,
        w_mass_used_as_theorem_input=False,
        claim_boundary=(
            "A dimensionless BHSM response is not, by itself, a physical eV/GeV mass. "
            f"Threshold-map status: {threshold_map.status}."
        ),
        remaining_missing_object=missing,
    )


def map_dimensionless_response(
    response: float,
    scale_result: NeutralDimensionfulScaleResult,
) -> NeutralUnitMap:
    mass_ev = response * scale_result.scale_value_eV if scale_result.unit_available else None
    mass_gev = response * scale_result.scale_value_GeV if scale_result.unit_available else None
    return NeutralUnitMap(
        dimensionless_response=float(response),
        neutral_scale_eV=scale_result.scale_value_eV,
        neutral_scale_GeV=scale_result.scale_value_GeV,
        effective_mass_eV=mass_ev,
        effective_mass_GeV=mass_gev,
        status=scale_result.status_after,
        unit_source=scale_result.unit_source,
        claim_boundary="Physical units are emitted only when the neutral scale result contains a valid unit source.",
    )

