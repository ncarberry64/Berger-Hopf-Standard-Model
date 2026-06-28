"""Audit the missing reciprocal logarithmic transport theorem for CKM 1/16."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from .common import CKMTransportAudit, repository_root
from .incidence_audit import audit_common_16_incidence


def audit_common_16_ckm_transport(
    repository: str | Path | None = None,
) -> CKMTransportAudit:
    root = repository_root(repository)
    historical = json.loads(
        (root / "audits/ckm_mixing_exponent_derivation_audit.json").read_text(encoding="utf-8")
    )
    transport = json.loads(
        (root / "artifacts/common_scale_boundary_transport_v1.json").read_text(encoding="utf-8")
    )
    incidence = audit_common_16_incidence(root)
    same_scale = transport["T_total(mu_BH_boundary -> mu_BH_boundary)"] == 1.0
    return CKMTransportAudit(
        status="OPEN_MISSING_CKM_EXPONENT_DERIVATION",
        candidate_status="CONDITIONAL_CKM_LOG_TRANSPORT_CANDIDATE",
        n_16=incidence.n_16,
        reciprocal_weight=Fraction(1, incidence.n_16),
        historical_candidate_selected_by_residual=bool(historical["selected_by_residual"]),
        residual_used_as_theorem_input=False,
        same_scale_identity_transport_available=same_scale,
        reciprocal_log_transport_theorem_available=False,
        cross_scale_transport_available=False,
        remaining_missing_object="OPEN_MISSING_CKM_LOG_TRANSPORT_AVERAGING_THEOREM",
        claim_boundary=(
            "The identity 1/N_16=1/16 is exact, but no pre-comparison action or transport operator in "
            "the repository proves that CKM logarithmic mixing must average over N_16 channels."
        ),
    )
