"""Export v2.3 Hermitian bidirectional CKM channel audits."""

from __future__ import annotations

import json
from pathlib import Path

from bhsm.interface.ckm_bidirectional_channel import (
    audit_bidirectional_channel_count,
    audit_bidirectional_log_transport_application,
    audit_ckm_adjoint_pair_selection,
    audit_ckm_channel_alternative_resolution,
    build_ckm_bidirectional_channel_report,
    search_ckm_bidirectional_sources,
)


ROOT = Path(__file__).resolve().parents[1]


def write_json(name: str, payload: dict[str, object]) -> None:
    (ROOT / "artifacts" / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_doc(name: str, title: str, body: str) -> None:
    (ROOT / "docs" / name).write_text(f"# {title}\n\n{body.strip()}\n", encoding="utf-8")


def main() -> int:
    source = search_ckm_bidirectional_sources()
    count = audit_bidirectional_channel_count()
    selection = audit_ckm_adjoint_pair_selection()
    alternatives = audit_ckm_channel_alternative_resolution()
    application = audit_bidirectional_log_transport_application()
    report = build_ckm_bidirectional_channel_report()
    outputs = {
        "BHSM_ckm_bidirectional_channel_count_v2_3.json": count,
        "BHSM_ckm_adjoint_pair_selection_v2_3.json": selection,
        "BHSM_ckm_channel_alternative_resolution_v2_3.json": alternatives,
        "BHSM_ckm_bidirectional_log_transport_application_v2_3.json": application,
        "BHSM_ckm_bidirectional_channel_report_v2_3.json": report,
        "BHSM_ckm_bidirectional_source_search_v2_3.json": source,
    }
    for name, payload in outputs.items():
        write_json(name, payload)

    shared = """The one-way up/down channel count is 8.

The Hermitian bidirectional up/down adjoint-pair channel count is 16.

The bidirectional channel count does not derive the CKM exponent unless BHSM proves that CKM transport is governed by the Hermitian charged-current adjoint pair.

The maximal self-response channel also has dimension 16, so the repo must distinguish same-number coincidence from physical source selection.

No empirical CKM fitting, charged-mass fitting, PDG values, W calibration, neutrino limits, or legacy threshold tables are used as theorem inputs."""
    write_doc("ckm_bidirectional_channel.md", "CKM Hermitian Bidirectional Channel", f"Status: `{report['status']}`.\n\n{shared}")
    write_doc("ckm_adjoint_pair_selection.md", "CKM Adjoint-Pair Selection", f"Status: `{selection['status']}`. Candidate: `{selection['candidate_status']}`.\n\nThe target expression contains `+ h.c.`, but the complete BHSM action selection rule remains open.")
    write_doc("ckm_channel_alternative_resolution.md", "CKM Channel Alternative Resolution", "| Candidate | Dimension | Status |\n| --- | ---: | --- |\n" + "\n".join(f"| `{row['id']}` | {row['dimension']} | `{row['status']}` |" for row in alternatives["rows"]))
    write_doc("ckm_bidirectional_log_transport_application.md", "CKM Bidirectional Log-Transport Application", f"Status: `{application['status']}`. Candidate: `{application['candidate_status']}`.\n\nThe abstract lemma is proved, while `selected_N_CKM` remains null and `1/16` remains underived.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
