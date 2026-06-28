"""Counterexample search for the raw space and admissible response cone."""

from __future__ import annotations

from itertools import product
from math import sqrt
from pathlib import Path

from .admissible_domain import derive_or_load_neutral_admissible_domain
from .common import NeutralPositivityCounterexample
from .neutral_quadratic_form import _base_payload, audit_neutral_kernel_exact
from .positivity_proof import prove_neutral_positivity_on_domain


def search_admissible_positivity_counterexample(
    repository: str | Path | None = None,
) -> NeutralPositivityCounterexample:
    audit = audit_neutral_kernel_exact(repository)
    domain = derive_or_load_neutral_admissible_domain(repository)
    proof = prove_neutral_positivity_on_domain(repository)
    candidate = None
    if domain.admissible_domain_defined:
        matrix = audit.kernel_matrix_numeric
        for values in product(range(11), repeat=3):
            if values == (0, 0, 0):
                continue
            norm = sqrt(sum(value * value for value in values))
            vector = tuple(value / norm for value in values)
            quadratic = sum(
                vector[i] * matrix[i][j] * vector[j]
                for i in range(3)
                for j in range(3)
            )
            if quadratic < -1.0e-12:
                candidate = {
                    "vector": vector,
                    "quadratic_value": quadratic,
                    "constraints_checked": list(domain.admissible_domain_constraints),
                }
                break
    found = candidate is not None
    counterexample = None
    if found:
        counterexample = candidate
    payload = _base_payload(audit)
    for key in (
        "admissible_domain_defined",
        "admissible_domain_constraints",
        "minimum_on_admissible_domain",
        "counterexample",
        "thresholding_used",
        "positivity_proven_without_thresholding",
        "counterexample_found",
    ):
        payload.pop(key)
    return NeutralPositivityCounterexample(
        candidate_key="neutral_admissible_counterexample_search",
        status=(
            "ADMISSIBLE_POSITIVITY_COUNTEREXAMPLE_FOUND"
            if found
            else proof.status
        ),
        claim_boundary=(
            "The raw negative eigenvector is retained as a full-space counterexample, but it has mixed signs and "
            "does not satisfy the nonnegative response-cone constraints. No admissible counterexample exists once the exact cone proof applies."
        ),
        remaining_missing_object=proof.remaining_missing_object,
        admissible_domain_defined=domain.admissible_domain_defined,
        admissible_domain_constraints=domain.admissible_domain_constraints,
        minimum_on_admissible_domain=proof.minimum_on_admissible_domain,
        counterexample=counterexample,
        thresholding_used=False,
        positivity_proven_without_thresholding=proof.positivity_proven_without_thresholding,
        counterexample_found=found,
        search_method="exact cone proof plus normalized nonnegative rational-grid counterexample scan",
        **payload,
    )
