"""BHSM v14.42 completion-status facade."""

from __future__ import annotations

from .collective_dirac_vacuum_polarization_v14_42 import (
    PRIMARY_VERDICT,
    SECONDARY_VERDICT,
    VERSION,
    completion_payload,
    deterministic_json,
)


def status_text() -> str:
    payload = completion_payload()
    return "\n".join(
        [
            f"# BHSM {VERSION} collective Dirac vacuum-polarization gate",
            "",
            f"- Primary verdict: `{PRIMARY_VERDICT}`",
            f"- Secondary verdict: `{SECONDARY_VERDICT}`",
            f"- Dirac action gate: `{payload['Dirac_action_gate']}`",
            f"- Compact domain gate: `{payload['compact_self_adjoint_domain_gate']}`",
            f"- L2 crossing: `{payload['renormalized_L2_crossing_gate']}`",
            f"- L3 crossing: `{payload['renormalized_L3_crossing_gate']}`",
            f"- BHSM complete: `{payload['BHSM_complete']}`",
            f"- Exact next object: `{payload['exact_next_object']}`",
        ]
    ) + "\n"


__all__ = ["completion_payload", "deterministic_json", "status_text"]
