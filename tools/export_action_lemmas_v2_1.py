"""Export v2.1 action-lemma reports and conservative documentation."""

from __future__ import annotations

import json
from pathlib import Path

from bhsm.interface.action_lemmas import (
    audit_ckm_log_transport_application,
    audit_maximal_overlap_bridge_rule,
    audit_primitive_lattice_rule,
    build_action_lemma_closure_report,
    prove_log_transport_averaging,
    search_action_lemma_sources,
)


ROOT = Path(__file__).resolve().parents[1]


def write_json(name: str, payload: dict[str, object]) -> None:
    (ROOT / "artifacts" / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_doc(name: str, title: str, body: str) -> None:
    (ROOT / "docs" / name).write_text(f"# {title}\n\n{body.strip()}\n", encoding="utf-8")


def main() -> int:
    source = search_action_lemma_sources()
    primitive = audit_primitive_lattice_rule()
    overlap = audit_maximal_overlap_bridge_rule()
    abstract = prove_log_transport_averaging(16)
    ckm = audit_ckm_log_transport_application()
    closure = build_action_lemma_closure_report()
    claim_policy = {
        "version": "2.1",
        "allowed": [
            "exact gcd and bridge arithmetic conditional on Omega_ch",
            "artifact-backed abstract quadratic log-averaging lemma",
            "conditional BHSM action candidates with named blockers",
        ],
        "forbidden": [
            "primitive lattice normalization is action-derived",
            "maximal overlap is action-selected",
            "abstract averaging alone derives the CKM exponent",
            "BHSM Physics is empirically validated",
        ],
        "full_completion_claimed": False,
        "frozen_predictions_modified": False,
    }
    outputs = {
        "BHSM_action_lemma_manifest_v2_1.json": {
            "version": "2.1",
            "status": closure["status"],
            "artifact_count": 8,
            "frozen_predictions_modified": False,
            "official_predictions_modified": False,
        },
        "BHSM_action_lemma_source_search_v2_1.json": source,
        "BHSM_primitive_lattice_normalization_rule_v2_1.json": primitive,
        "BHSM_maximal_overlap_bridge_rule_v2_1.json": overlap,
        "BHSM_log_transport_averaging_lemma_v2_1.json": abstract,
        "BHSM_ckm_log_transport_application_gate_v2_1.json": ckm,
        "BHSM_action_lemma_closure_report_v2_1.json": closure,
        "BHSM_action_lemma_claim_policy_v2_1.json": claim_policy,
    }
    for name, payload in outputs.items():
        write_json(name, payload)

    shared = """The primitive lattice normalization rule is not action-derived unless the BHSM action is shown to quotient common incidence rescalings.

The maximal-overlap bridge rule is not action-derived unless the BHSM charged bridge/Hessian action selects the maximal primitive overlap channel.

The abstract log-transport averaging lemma does not by itself derive the CKM exponent.

The CKM exponent remains open unless BHSM proves CKM transport acts over N_16 equivalent bilinear charged-incidence channels.

No empirical CKM fitting, charged-mass fitting, PDG values, W calibration, neutrino limits, or legacy threshold tables are used as theorem inputs."""
    write_doc("action_lemma_closure_report.md", "Action Lemma Closure Report", f"Status: `{closure['status']}`.\n\n{shared}")
    write_doc("primitive_lattice_normalization_rule.md", "Primitive Lattice Normalization Rule", f"Status: `{primitive['status']}`. Candidate status: `{primitive['candidate_status']}`.\n\n{primitive['claim_boundary']}")
    write_doc("maximal_overlap_bridge_rule.md", "Maximal-Overlap Bridge Rule", f"Status: `{overlap['status']}`. Candidate status: `{overlap['candidate_status']}`.\n\n`O_ch=4/3` and `g_bridge=16/189` remain exact conditional identities.\n\n{overlap['claim_boundary']}")
    write_doc("log_transport_averaging_lemma.md", "Log-Transport Averaging Lemma", f"Status: `{abstract['status']}`.\n\nFor fixed `sum x_i=L`,\n\n`sum x_i^2 - L^2/N = sum (x_i-L/N)^2 >= 0`.\n\nThe unique minimizer is `x_i=L/N`, so multiplicative transport contributes `Z^(1/N)` per abstract equivalent channel.\n\n{abstract['claim_boundary']}")
    write_doc("ckm_log_transport_application_gate.md", "CKM Log-Transport Application Gate", f"Status: `{ckm['status']}`. Candidate status: `{ckm['candidate_status']}`.\n\n{ckm['claim_boundary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
