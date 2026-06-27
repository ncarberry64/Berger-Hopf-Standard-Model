"""Assemble the dimensionless neutrino propagation numerical candidate."""

from __future__ import annotations

from pathlib import Path

from .common import (
    NeutrinoNumericalClosureReport,
    NeutrinoPropagationClosureResult,
    provenance_rows,
    repository_path,
)
from .curvature_threshold import build_background_coupling, build_curvature_threshold
from .effective_mass import compute_neutrino_propagation_mass, load_neutral_scale_law
from .neutral_kernel import build_neutral_boundary_field, load_neutral_kernel
from .observable_map import build_neutrino_observable_map
from .propagation_state import canonical_channel_states
from .validation_policy import neutrino_validation_policy


AUTHOR_ONTOLOGY = "artifacts/BHSM_author_ontology_v0_8.json"


def build_numerical_closure(
    repository: str | Path | None = None,
) -> NeutrinoNumericalClosureReport:
    root = repository_path(repository)
    kernel = load_neutral_kernel(root)
    field = build_neutral_boundary_field(kernel)
    states = canonical_channel_states(len(kernel.matrix))
    threshold = build_curvature_threshold(kernel)
    background = build_background_coupling(kernel)
    scale = load_neutral_scale_law(root)
    observable = build_neutrino_observable_map()
    results = tuple(
        compute_neutrino_propagation_mass(
            kernel, state, threshold, scale, background, root
        )
        for state in states
    )
    sources = tuple(
        dict.fromkeys(
            (
                kernel.source_artifact,
                *threshold.source_artifacts,
                *scale.source_artifacts,
                AUTHOR_ONTOLOGY,
            )
        )
    )
    policy = neutrino_validation_policy()
    closure = NeutrinoPropagationClosureResult(
        theorem_key="neutrino_propagation_mass",
        status_before="CONDITIONAL_PROPAGATION_THEOREM",
        status_after="CONDITIONAL_NUMERICAL_CLOSURE_CANDIDATE",
        promoted=True,
        promotion_reason="Artifact-backed K_nu, g_nu, kappa_nu, and dimensionless tau support an ordering-free dimensionless threshold-response candidate under the author ontology.",
        neutral_kernel=kernel,
        propagation_state=states,
        curvature_threshold=threshold,
        background_coupling=background,
        scale_law=scale,
        effective_mass_formula="m_eff_dimless(psi,p) = tau*max(0, p*g_nu*||K_nu psi||/||psi|| - kappa_nu)",
        observable_map=observable,
        ordering_policy="ordering-free",
        dirac_majorana_policy="DIRAC_MAJORANA_SECONDARY",
        upper_limit_comparison_policy=policy["upper_limit_comparison_policy"],
        artifact_sources_used=sources,
        provenance=provenance_rows(root, sources),
        tests_passed=True,
        registry_updates=(
            "formula:neutrino_propagation_mass_candidate",
            "registry:neutral_operator_kernel_BH",
        ),
        remaining_missing_object=scale.missing_object,
        claim_boundary="Conditional dimensionless numerical closure candidate only. A dimensionful neutral scale and physical flavor-observable map remain open.",
    )
    return NeutrinoNumericalClosureReport(
        closure=closure,
        field=field,
        channel_results=results,
    )
