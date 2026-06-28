"""Apply strict provenance gates to the proposed common-16 construction."""

from __future__ import annotations

from pathlib import Path

from .common import Common16ProvenanceAudit
from .bridge_beta_audit import audit_common_16_bridge_beta
from .ckm_transport_audit import audit_common_16_ckm_transport
from .incidence_audit import audit_common_16_incidence


def audit_common_16_provenance(
    repository: str | Path | None = None,
) -> Common16ProvenanceAudit:
    incidence = audit_common_16_incidence(repository)
    bridge = audit_common_16_bridge_beta(repository)
    transport = audit_common_16_ckm_transport(repository)
    return Common16ProvenanceAudit(
        status="CONDITIONAL_COMMON_16_GENERATOR_CANDIDATE",
        omega_f_source_status=incidence.omega_source_status,
        rho_ch_source_status=incidence.rho_ch_source_status,
        n_16_source_status="CONDITIONAL_ON_OMEGA_F_AND_RHO_CH_3",
        bridge_beta_source_status=bridge.bridge_source_status,
        ckm_reciprocal_transport_status=transport.remaining_missing_object,
        ckm_exponent_final_status=transport.status,
        fallback_target="rho_ch=3 action provenance and Omega_f action provenance",
        fallback_result=(
            "OPEN_MISSING_RHO_CH_ACTION_DERIVATION; OPEN_MISSING_OMEGA_F_ACTION_DERIVATION"
        ),
        artifact_backed_closures=(
            "exact rational identity N_16/(S_ch*rho_ch^3)=16/189 under declared premises",
            "exact beta_f=(16/189)Pi_f table identity",
            "exact reciprocal identity 1/N_16=1/16",
        ),
        conditional_closures=(
            "CONDITIONAL_COMMON_16_GENERATOR_CANDIDATE",
            "CONDITIONAL_CKM_LOG_TRANSPORT_CANDIDATE",
        ),
        open_blockers=(
            "OPEN_MISSING_OMEGA_F_ACTION_DERIVATION",
            "OPEN_MISSING_RHO_CH_ACTION_DERIVATION",
            "OPEN_MISSING_CHARGED_OVERLAP_4_OVER_3_ACTION_SOURCE",
            "OPEN_MISSING_CKM_LOG_TRANSPORT_AVERAGING_THEOREM",
            "OPEN_MISSING_CROSS_SCALE_TRANSPORT_THEOREM",
        ),
        retired_or_rejected_hypotheses=(
            "CKM 1/16 is artifact-backed merely because the same integer appears in g_bridge",
            "same-scale identity transport proves nontrivial CKM cross-scale transport",
            "rho_ch=3 may be selected from residual quality or near-degeneracy",
        ),
    )
