"""Record whether the admissible neutral restriction is a linear projection."""

from __future__ import annotations

from pathlib import Path

from .admissible_domain import derive_or_load_neutral_admissible_domain
from .common import ProjectedNeutralKernel
from .neutral_quadratic_form import _base_payload, audit_neutral_kernel_exact


def build_projected_neutral_kernel(
    repository: str | Path | None = None,
) -> ProjectedNeutralKernel:
    audit = audit_neutral_kernel_exact(repository)
    domain = derive_or_load_neutral_admissible_domain(repository)
    payload = _base_payload(audit)
    for key in (
        "admissible_domain_defined",
        "admissible_domain_constraints",
        "projection_matrix",
        "projected_kernel",
        "projected_eigenvalues",
        "projected_psd",
    ):
        payload.pop(key)
    return ProjectedNeutralKernel(
        candidate_key="neutral_cone_restriction_audit",
        status=domain.status,
        claim_boundary=(
            "The admissible set is a convex cone of response magnitudes, not a linear subspace. "
            "No projector PSD claim is made and the raw kernel remains indefinite."
        ),
        remaining_missing_object="complete-action derivation of the response cone; no linear projector is applicable",
        admissible_domain_defined=domain.admissible_domain_defined,
        admissible_domain_constraints=domain.admissible_domain_constraints,
        projection_matrix=None,
        projected_kernel=None,
        projected_eigenvalues=(),
        projected_psd=None,
        restriction_kind="nonnegative_response_cone_not_linear_projection",
        **payload,
    )
