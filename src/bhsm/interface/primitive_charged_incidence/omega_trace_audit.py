"""Trace the structural charged Omega tuple without promoting its action origin."""

from __future__ import annotations

from .common import OMEGA_CH, no_empirical_inputs, repository_root


def audit_omega_trace() -> dict[str, object]:
    root = repository_root()
    sources = (
        "docs/bhsm_sector_projector_ledger_theorem.md",
        "src/bhsm_boundary_connection_holonomy.py",
        "artifacts/BHSM_omega_f_action_audit_v1_9.json",
    )
    return {
        "audit": "omega_trace",
        "omega_ch": list(OMEGA_CH),
        "total_incidence_trace": sum(OMEGA_CH),
        "status": "STRUCTURALLY_INTEGRATED_NOT_ACTION_DERIVED",
        "open_status": "OPEN_MISSING_OMEGA_F_ACTION_COVECTOR_DERIVATION",
        "sources": list(sources),
        "all_sources_present": all((root / path).is_file() for path in sources),
        "action_covector_derived": False,
        "claim_boundary": "The charged Omega tuple is structurally integrated; its complete action covector origin remains open.",
        **no_empirical_inputs(),
    }
