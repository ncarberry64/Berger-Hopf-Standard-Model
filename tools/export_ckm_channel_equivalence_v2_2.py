"""Export v2.2 CKM channel-equivalence audits and documentation."""

from __future__ import annotations

import json
from pathlib import Path

from bhsm.interface.ckm_channel_equivalence import (
    audit_ckm_channel_application,
    audit_ckm_channel_counts,
    audit_maximal_sector_selection,
    build_ckm_channel_equivalence_report,
    search_ckm_channel_sources,
)


ROOT = Path(__file__).resolve().parents[1]


def write_json(name: str, payload: dict[str, object]) -> None:
    (ROOT / "artifacts" / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_doc(name: str, title: str, body: str) -> None:
    (ROOT / "docs" / name).write_text(f"# {title}\n\n{body.strip()}\n", encoding="utf-8")


def main() -> int:
    source = search_ckm_channel_sources()
    counts = audit_ckm_channel_counts()
    selection = audit_maximal_sector_selection()
    application = audit_ckm_channel_application()
    report = build_ckm_channel_equivalence_report()
    manifest = {
        "version": "2.2",
        "status": report["status"],
        "artifact_count": 6,
        "frozen_predictions_modified": False,
        "official_predictions_modified": False,
    }
    outputs = {
        "BHSM_ckm_channel_equivalence_manifest_v2_2.json": manifest,
        "BHSM_ckm_channel_source_search_v2_2.json": source,
        "BHSM_ckm_channel_count_audit_v2_2.json": counts,
        "BHSM_ckm_maximal_sector_selection_v2_2.json": selection,
        "BHSM_ckm_log_transport_application_v2_2.json": application,
        "BHSM_ckm_channel_equivalence_report_v2_2.json": report,
    }
    for name, payload in outputs.items():
        write_json(name, payload)

    shared = """The abstract log-transport averaging lemma does not by itself derive the CKM exponent.

The CKM 1/16 exponent is not derived unless BHSM proves that CKM transport acts over the N_16 charged bilinear channel space.

The N_16 channel assignment remains conditional unless the action selects maximal primitive charged self-response over competing channel assignments.

No empirical CKM fitting, charged-mass fitting, PDG values, W calibration, neutrino limits, or legacy threshold tables are used as theorem inputs."""
    write_doc("ckm_channel_equivalence.md", "CKM Channel Equivalence", f"Status: `{report['status']}`.\n\n{shared}")
    write_doc("ckm_channel_count_audit.md", "CKM Channel Count Audit", "| Assignment | Dimension |\n| --- | ---: |\n| `Hom(V_u,V_d)` | 8 |\n| `End(V_ch)` | 49 |\n| direct sum of sector self responses | 21 |\n| `End(V_d)` | 16 |\n\nAll dimensions are exact. No assignment is selected by arithmetic.")
    write_doc("ckm_maximal_sector_selection.md", "CKM Maximal-Sector Selection", f"Status: `{selection['status']}`. Candidate status: `{selection['candidate_status']}`.\n\nEvidence against alternatives is absent. The missing action rule is: {selection['missing_action_rule']}.")
    write_doc("ckm_log_transport_application.md", "CKM Log-Transport Application", f"Status: `{application['status']}`.\n\nThe abstract averaging lemma is artifact-backed, but `selected_N_CKM` remains null. The candidate exponent `1/16` is not derived.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
