"""Dimensionally complete neutral spectral-gap candidate builder."""

from __future__ import annotations

from pathlib import Path

from ..neutrino_scale.common import repository_path
from ..neutrino_scale.neutral_physical_curvature import search_neutral_physical_curvature_map
from .common import NeutralSpectralGapCandidate, NeutralStiffnessRatio, clean_provenance, guard_fields
from .stiffness_ratio import search_neutral_stiffness_ratio


HBAR_SI = 1.054_571_817e-34
LIGHT_SPEED_SI = 299_792_458.0
EV_PER_JOULE = 1.0 / 1.602_176_634e-19


def build_neutral_spectral_gap_candidate(
    repository: str | Path | None = None,
    *,
    stiffness_length_m: float | None = None,
    curvature_per_m2: float | None = None,
    propagating: bool = True,
) -> NeutralSpectralGapCandidate:
    """Build a symbolic candidate, producing units only from explicit physical inputs."""

    root = repository_path(repository)
    ratio = search_neutral_stiffness_ratio(root)
    curvature_map = search_neutral_physical_curvature_map(root)
    if stiffness_length_m is not None and stiffness_length_m < 0:
        raise ValueError("stiffness_length_m must be nonnegative")
    if curvature_per_m2 is not None and curvature_per_m2 < 0:
        raise ValueError("curvature_per_m2 must be nonnegative")
    numeric = stiffness_length_m is not None and curvature_per_m2 is not None
    inverse_gap = stiffness_length_m * curvature_per_m2 if numeric and propagating else (0.0 if numeric else None)
    mass_kg = HBAR_SI * inverse_gap / LIGHT_SPEED_SI if inverse_gap is not None else None
    energy_ev = HBAR_SI * LIGHT_SPEED_SI * inverse_gap * EV_PER_JOULE if inverse_gap is not None else None
    sources = tuple(dict.fromkeys((*ratio.source_artifacts, *curvature_map.source_artifacts)))
    if numeric:
        missing = "none for the explicitly supplied dimensional demonstration inputs"
    else:
        missing = "numeric action-derived sqrt(A_nu/Z_nu) in metres and physical K_neutral,eff in m^-2"
    return NeutralSpectralGapCandidate(
        candidate_key="neutral_spectral_gap_candidate",
        status="CONDITIONAL_NEUTRAL_SPECTRAL_MASS_CANDIDATE",
        value="m_nu c^2 = hbar c sqrt(A_nu/Z_nu) K_neutral,eff",
        unit="symbolic" if not numeric else "kg and eV/c^2",
        dimension="mass via inverse_length_gap",
        source_type="conditional neutral action normalization and physical curvature gate",
        source_artifacts=sources,
        source_equations=(
            "mu_nu = sqrt(A_nu/Z_nu) K_neutral,eff",
            "E_nu = hbar c mu_nu",
            "m_nu = (hbar/c) mu_nu",
        ),
        provenance=clean_provenance(sources),
        author_ontology_dependency="neutral mass contribution exists only through propagation-conditioned curvature response",
        claim_boundary=(
            "The theorem shape is conditional. Repository defaults remain symbolic and produce no kg/eV/GeV value; "
            "the optional dimensional arguments are an explicit unit-path test, not fitted BHSM inputs."
        ),
        remaining_missing_object=missing,
        stiffness_ratio=ratio,
        curvature_numeric_per_m2=curvature_per_m2 is not None,
        inverse_length_gap_available=numeric,
        inverse_length_gap_per_m=inverse_gap,
        dimensionful_mass_available=numeric,
        dimensionful_mass_kg=mass_kg,
        dimensionful_mass_eV=energy_ev,
        dimensionful_mass_GeV=energy_ev / 1.0e9 if energy_ev is not None else None,
        zero_propagation_mass_vanishes=(not propagating and inverse_gap == 0.0) or propagating,
        **guard_fields(),
    )
