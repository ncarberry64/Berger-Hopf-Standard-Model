"""Raw and admissible-response positivity audit for the neutral kernel."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from ..neutrino_propagation.neutral_kernel import load_neutral_kernel
from ..neutrino_scale.common import repository_path
from .common import NeutralKernelPositivityAudit, clean_provenance, guard_fields


def audit_neutral_kernel_positivity(
    repository: str | Path | None = None,
    *,
    tolerance: float = 1.0e-12,
) -> NeutralKernelPositivityAudit:
    root = repository_path(repository)
    kernel = load_neutral_kernel(root)
    eigenvalues = tuple(float(value) for value in np.linalg.eigvalsh(np.asarray(kernel.matrix, dtype=float)))
    raw_psd = min(eigenvalues) >= -tolerance
    return NeutralKernelPositivityAudit(
        candidate_key="neutral_kernel_positivity_audit",
        status="RAW_KERNEL_POSITIVE_SEMIDEFINITE" if raw_psd else "RAW_KERNEL_NOT_POSITIVE_SEMIDEFINITE",
        value="eigenvalues(K_nu)",
        unit=None,
        dimension="dimensionless boundary response",
        source_type="artifact-backed neutral kernel eigenspectrum",
        source_artifacts=(kernel.source_artifact,),
        source_equations=("K_nu", "R_excess = max(0, coupled_response-kappa_nu)"),
        provenance=clean_provenance((kernel.source_artifact,)),
        author_ontology_dependency="physical neutral boundary field with propagation-conditioned response",
        claim_boundary=(
            "The raw kernel has a negative eigenvalue. This raw audit does not infer admissible-domain positivity "
            "from threshold clipping; the separate v1.4 cone proof records that conditional result."
        ) if not raw_psd else "The raw finite kernel is positive semidefinite within the stated tolerance.",
        remaining_missing_object="separate admissible-domain proof report" if not raw_psd else "none for raw finite-kernel PSD",
        raw_eigenvalues=eigenvalues,
        raw_positive_semidefinite=raw_psd,
        projected_response_nonnegative_by_definition=True,
        admissible_positive_response_proven=False,
        **guard_fields(),
    )
