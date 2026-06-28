"""Ontology-constrained measurement-supported neutral response domain."""

from __future__ import annotations

from pathlib import Path

from ..neutrino_scale.common import repository_path
from .common import NeutralAdmissibleDomain
from .neutral_quadratic_form import _base_payload, audit_neutral_kernel_exact


ONTOLOGY_SOURCES = (
    "artifacts/BHSM_author_ontology_v0_8.json",
    "artifacts/BHSM_neutral_measurement_support_ontology_v1_4.json",
    "src/bhsm/interface/neutrino_propagation/propagation_state.py",
    "src/bhsm/interface/neutrino_propagation/curvature_threshold.py",
)

DOMAIN_CONSTRAINTS = (
    "x is a real three-channel response-magnitude vector, not a raw signed or complex wave-amplitude vector",
    "x_i >= 0 for i=1,2,3",
    "sum_i x_i^2 = 1",
    "propagation_response > 0",
    "at least one physical interaction, detector-boundary, or measurement-support coupling is active",
    "zero support maps to the null BHSM mass contribution and is outside the normalized active cone",
)


def derive_or_load_neutral_admissible_domain(
    repository: str | Path | None = None,
) -> NeutralAdmissibleDomain:
    root = repository_path(repository)
    audit = audit_neutral_kernel_exact(root)
    found = tuple(path for path in ONTOLOGY_SOURCES if (root / path).is_file())
    defined = len(found) == len(ONTOLOGY_SOURCES)
    status = (
        "CONDITIONAL_MEASUREMENT_SUPPORTED_NEUTRAL_POSITIVITY_CANDIDATE"
        if defined
        else "OPEN_MISSING_ADMISSIBLE_NEUTRAL_DOMAIN"
    )
    return NeutralAdmissibleDomain(
        candidate_key="measurement_supported_neutral_response_cone",
        status=status,
        claim_boundary=(
            "The cone is justified by the controlling author ontology and existing propagation modules, "
            "but the magnitude-coordinate map and support rule are not yet uniquely derived from the complete neutral action."
        ),
        remaining_missing_object=(
            "complete-action derivation of the measurement-supported response-coordinate map"
            if defined else "machine-readable interaction-support ontology and response-coordinate map"
        ),
        admissible_domain_defined=defined,
        admissible_domain_constraints=DOMAIN_CONSTRAINTS if defined else (),
        coordinate_interpretation="response-magnitude coordinates x_i = nonnegative magnitude of the supported response in neutral channel i",
        ontology_sources=found,
        action_derived=False,
        **{
            key: value
            for key, value in _base_payload(audit).items()
            if key not in {"admissible_domain_defined", "admissible_domain_constraints"}
        },
    )
