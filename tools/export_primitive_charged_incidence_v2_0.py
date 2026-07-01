"""Export exact primitive-incidence audits and conservative v2.0 documentation."""

from __future__ import annotations

import json
from pathlib import Path

from bhsm.interface.primitive_charged_incidence import (
    audit_bridge_beta_identity,
    audit_ckm_log_transport,
    audit_external_reproduction_status,
    audit_omega_trace,
    audit_overlap_4_over_3,
    audit_physical_normalization,
    audit_projector_reduction,
    audit_rho_gcd_selection,
    build_primitive_charged_incidence_report,
)


ROOT = Path(__file__).resolve().parents[1]


def write_json(name: str, payload: dict[str, object]) -> None:
    path = ROOT / "artifacts" / name
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_doc(name: str, title: str, body: str) -> None:
    (ROOT / "docs" / name).write_text(f"# {title}\n\n{body.strip()}\n", encoding="utf-8")


def main() -> int:
    omega = audit_omega_trace()
    rho = audit_rho_gcd_selection()
    projector = audit_projector_reduction()
    overlap = audit_overlap_4_over_3()
    bridge = audit_bridge_beta_identity()
    ckm = audit_ckm_log_transport()
    normalization = audit_physical_normalization()
    external = audit_external_reproduction_status()
    report = build_primitive_charged_incidence_report()
    manifest = {
        "version": "2.0",
        "artifacts": [
            "BHSM_omega_trace_audit_v2_0.json",
            "BHSM_rho_ch_gcd_selection_audit_v2_0.json",
            "BHSM_projector_reduction_audit_v2_0.json",
            "BHSM_overlap_4_over_3_source_audit_v2_0.json",
            "BHSM_bridge_beta_identity_audit_v2_0.json",
            "BHSM_ckm_log_transport_gate_v2_0.json",
            "BHSM_physical_normalization_gate_v2_0.json",
            "BHSM_external_reproduction_status_v2_0.json",
            "BHSM_primitive_charged_incidence_closure_report_v2_0.json",
        ],
        "status": report["status"],
        "frozen_predictions_modified": False,
        "official_predictions_modified": False,
    }
    outputs = {
        "BHSM_primitive_charged_incidence_manifest_v2_0.json": manifest,
        "BHSM_omega_trace_audit_v2_0.json": omega,
        "BHSM_rho_ch_gcd_selection_audit_v2_0.json": rho,
        "BHSM_projector_reduction_audit_v2_0.json": projector,
        "BHSM_overlap_4_over_3_source_audit_v2_0.json": overlap,
        "BHSM_bridge_beta_identity_audit_v2_0.json": bridge,
        "BHSM_ckm_log_transport_gate_v2_0.json": ckm,
        "BHSM_physical_normalization_gate_v2_0.json": normalization,
        "BHSM_external_reproduction_status_v2_0.json": external,
        "BHSM_primitive_charged_incidence_closure_report_v2_0.json": report,
    }
    for name, payload in outputs.items():
        write_json(name, payload)

    exact = """The primitive charged incidence audit establishes exact conditional algebraic identities, not full action derivations.

`Omega_ch=(3,6,12)`, `T_ch=21`, `rho_ch=gcd(Omega_ch)=3`, `s_ch=(1,2,4)`, `S_ch=7`, and `Pi_ch=(1/7,2/7,4/7)`.

`O_ch=4/3`, `N_16=16`, `g_bridge=16/189`, and `beta_ch=(16,32,64)/1323` follow exactly under those declared premises.

No empirical input is used. Frozen and official predictions are unchanged."""
    write_doc("primitive_charged_incidence.md", "Primitive Charged Incidence", exact)
    write_doc("rho_ch_gcd_selection.md", "rho_ch GCD Selection", "rho_ch = 3 is conditionally identified as the primitive common divisor of Omega_ch = (3,6,12), but the action rule requiring primitive charged-lattice normalization remains open.\n\nStatus: `CONDITIONAL_RHO_CH_PRIMITIVE_LATTICE_CANDIDATE`; blocker: `OPEN_MISSING_ACTION_PRIMITIVE_LATTICE_NORMALIZATION_RULE`.")
    write_doc("charged_overlap_4_over_3_source.md", "Charged Overlap 4/3 Source", "The charged overlap 4/3 is conditionally identified as s_d/rho_ch, but the action rule requiring the bridge to use maximal primitive overlap remains open.\n\nStatus: `CONDITIONAL_CHARGED_OVERLAP_4_OVER_3_SOURCE_CANDIDATE`; blocker: `OPEN_MISSING_ACTION_RULE_THAT_BRIDGE_USES_MAX_PRIMITIVE_OVERLAP`.")
    write_doc("ckm_log_transport_gate.md", "CKM Log-Transport Gate", "The CKM 1/16 exponent remains open because the CKM logarithmic transport averaging theorem is not yet derived.\n\nThe reciprocal identity `1/N_16=1/16` is exact, but its use as a physical transport exponent is conditional.")
    write_doc("physical_normalization_gate.md", "Physical Normalization Gate", "Physical normalization and external reproduction remain open gates. Exact dimensionless incidence identities do not provide a normalized measure, stiffness unit map, or physical mass scale.")
    write_doc("external_reproduction_status.md", "External Reproduction Status", "Status: `PREPARED_NOT_YET_REPRODUCED_EXTERNALLY`. The v1.9 packet exists, but no contact or independent result is recorded. This is an engine reproduction gate, not BHSM Physics validation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
