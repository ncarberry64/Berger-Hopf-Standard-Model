"""Physical-unit audit for the neutral response-to-curvature map."""

from __future__ import annotations

from pathlib import Path

from ..neutrino_scale.boundary_measure import analyze_neutral_boundary_measure
from ..neutrino_scale.common import repository_path
from ..neutrino_scale.neutral_physical_curvature import search_neutral_physical_curvature_map
from ..neutrino_scale.transport_normalization import search_transport_normalization
from .common import PhysicalNeutralCurvatureMapResult, guard_fields, provenance


def derive_or_locate_physical_neutral_curvature_map(
    repository: str | Path | None = None,
) -> PhysicalNeutralCurvatureMapResult:
    root = repository_path(repository)
    existing = search_neutral_physical_curvature_map(root)
    measure = analyze_neutral_boundary_measure(root)
    transport = search_transport_normalization(root)
    sources = tuple(
        dict.fromkeys(
            (
                *existing.source_artifacts,
                measure.source,
                *transport.source_artifacts,
                "theory/theorem_discharge_collar_measure_extrinsic_geometry.md",
            )
        )
    )
    sources = tuple(path for path in sources if (root / path).is_file())
    return PhysicalNeutralCurvatureMapResult(
        candidate_key="physical_neutral_curvature_map",
        status="CONDITIONAL_PHYSICAL_NEUTRAL_CURVATURE_MAP_CANDIDATE",
        value="K_neutral,eff=kappa_curv R_nu_dimless",
        unit="m^-2 required; symbolic only",
        dimension="inverse_length_squared",
        numeric_value=None,
        symbolic_value="K_neutral,eff=kappa_curv R_nu_dimless",
        source_type="dimensionless neutral response plus conditional collar/curvature geometry",
        source_artifacts=sources,
        source_equations=(
            "R_nu=max(0,p*g_nu*||K_nu psi||/||psi||-kappa_nu)",
            "K_neutral,eff=kappa_curv R_nu_dimless",
            "J(Y,rho)=det(I+rho S(Y))",
        ),
        provenance=provenance(sources),
        author_ontology_dependency="interaction-supported propagation response",
        claim_boundary=(
            "The response and symbolic map exist, but kappa_curv is not supplied in m^-2. The dimensionless "
            "response is never treated as physical curvature."
        ),
        remaining_missing_object=(
            "physical curvature unit map kappa_curv in m^-2; normalized dmu_boundary dt; "
            "transport/support length; BHSM profile/embedding and shape-operator values"
        ),
        dimensionless_response_available=True,
        symbolic_physical_map_available=True,
        numeric_per_m2_available=False,
        curvature_per_m2=None,
        boundary_measure_normalized=measure.physical_normalization_available,
        transport_length_available=transport.physical_transport_normalization_available,
        **guard_fields(),
    )
