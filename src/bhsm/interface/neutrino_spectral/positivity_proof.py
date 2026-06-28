"""Exact copositivity proof on the measurement-supported response cone."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path

from .admissible_domain import derive_or_load_neutral_admissible_domain
from .common import AdmissiblePositivityProof
from .neutral_quadratic_form import _base_payload, audit_neutral_kernel_exact


PROOF_STEPS = (
    "On the admissible domain, each response coordinate x_i is nonnegative.",
    "The exact kernel has no negative entry.",
    "q(x)=3*x2^2+(5/3)*x3^2+(2/3)*x1*x2+(1/3)*x2*x3.",
    "Every displayed monomial is nonnegative for x_i>=0.",
    "Therefore q(x)>=0 on the full response cone by exact termwise sign analysis.",
    "The normalized-cone minimum is 0, attained at x=(1,0,0).",
)


def _all_exact_entries_nonnegative(matrix: tuple[tuple[str, ...], ...]) -> bool:
    return all(Fraction(value) >= 0 for row in matrix for value in row)


def prove_neutral_positivity_on_domain(
    repository: str | Path | None = None,
) -> AdmissiblePositivityProof:
    audit = audit_neutral_kernel_exact(repository)
    domain = derive_or_load_neutral_admissible_domain(repository)
    proven = domain.admissible_domain_defined and _all_exact_entries_nonnegative(audit.kernel_matrix_exact)
    status = (
        "CONDITIONAL_MEASUREMENT_SUPPORTED_NEUTRAL_POSITIVITY_CANDIDATE"
        if proven
        else "OPEN_MISSING_ADMISSIBLE_NEUTRAL_DOMAIN"
    )
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
    return AdmissiblePositivityProof(
        candidate_key="measurement_supported_neutral_copositivity_proof",
        status=status,
        claim_boundary=(
            "The quadratic-form proof is exact on the stated response cone. Its physical applicability is conditional "
            "on the author-ontology response-magnitude domain and does not establish raw-kernel PSD."
        ),
        remaining_missing_object="complete-action derivation of the measurement-supported response cone",
        admissible_domain_defined=domain.admissible_domain_defined,
        admissible_domain_constraints=domain.admissible_domain_constraints,
        minimum_on_admissible_domain=0.0 if proven else None,
        counterexample=None,
        thresholding_used=False,
        positivity_proven_without_thresholding=proven,
        counterexample_found=False,
        proof_method="exact entrywise copositivity on the nonnegative response cone",
        proof_steps=PROOF_STEPS if proven else (),
        **payload,
    )
