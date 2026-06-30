"""Export BHSM v1.9 reviewer, theorem-gate, and falsification artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from bhsm.interface.action_derivation_gates import build_action_derivation_report
from bhsm.interface.engine_invariants import build_engine_invariant_report
from bhsm.interface.science_hardening import (
    engine_physics_status,
    external_reproduction_packet,
    falsification_table,
    minimal_theorem_core,
    reviewer_manifest,
)


ROOT = Path(__file__).resolve().parents[1]


def write_json(relative: str, payload: dict[str, object]) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_doc(relative: str, title: str, body: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {title}\n\n{body.strip()}\n", encoding="utf-8")


def table(rows: list[dict[str, object]], columns: tuple[str, ...]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(column, "")).replace("\n", " ") for column in columns) + " |")
    return "\n".join(lines)


def main() -> int:
    status = engine_physics_status()
    reviewer = reviewer_manifest()
    invariants = build_engine_invariant_report()
    core = minimal_theorem_core()
    action = build_action_derivation_report()
    falsification = falsification_table()
    external = external_reproduction_packet()

    write_json("artifacts/BHSM_engine_physics_status_separation_v1_9.json", status)
    write_json("artifacts/BHSM_reviewer_reproduction_manifest_v1_9.json", reviewer)
    write_json("artifacts/BHSM_engine_invariant_preservation_v1_9.json", invariants)
    write_json("artifacts/BHSM_minimal_theorem_core_v1_9.json", core)
    write_json("artifacts/BHSM_omega_f_action_audit_v1_9.json", action["omega_f"])
    write_json("artifacts/BHSM_rho_ch_action_audit_v1_9.json", action["rho_ch"])
    write_json("artifacts/BHSM_charged_overlap_source_audit_v1_9.json", action["charged_overlap"])
    write_json("artifacts/BHSM_action_derivation_gates_report_v1_9.json", action)
    write_json("artifacts/BHSM_brutal_falsification_table_v1_9.json", falsification)
    write_json("artifacts/BHSM_external_reproduction_packet_v1_9.json", external)

    exact = (
        "The BHSM Engine validates high-throughput, precision-gated geometric coordinate transformations on synthetic and real HEP kinematic data.\n\n"
        "BHSM Engine validation does not constitute empirical validation of BHSM as new particle physics.\n\n"
        "BHSM Physics remains an integrated conditional Berger-Hopf boundary-mode framework with open action, transport, normalization, unit-map, gauge/scalar, and runtime gates.\n\n"
        "BHSM does not claim full Standard Model derivation or physical eV/GeV neutrino mass closure."
    )
    write_doc("docs/engine_vs_physics_claim_boundary.md", "Engine vs Physics Claim Boundary", exact)
    write_doc(
        "docs/bhsm_engine_status.md",
        "BHSM Engine Status",
        exact + "\n\n## Validated capabilities\n\n" + "\n".join(f"- {x}" for x in status["engine_validated_capabilities"]) +
        "\n\n## Excluded capabilities\n\n" + "\n".join(f"- {x}" for x in status["engine_excluded_capabilities"]),
    )
    write_doc(
        "docs/bhsm_physics_status.md",
        "BHSM Physics Status",
        exact + "\n\n## Open blockers\n\n" + "\n".join(f"- {x}" for x in status["physics_open_blockers"]),
    )
    commands = "\n".join(f"- `{name}`: `{command}`" for name, command in reviewer["commands"].items())
    write_doc("docs/reviewer_reproduction_guide.md", "Reviewer Reproduction Guide", commands + "\n\nThe CERN command is `requires_network_or_cached_data`; all other listed status and invariant commands are offline.")
    write_doc("docs/reviewer_30min_quickstart.md", "Reviewer 30-Minute Quickstart", "Run `make reviewer-smoke`, `make reviewer-invariants`, and `make reviewer-claims-audit`. Review the engine/physics boundary before interpreting results.")
    write_doc("docs/reviewer_2hour_validation.md", "Reviewer Two-Hour Validation", "Run `make reviewer-full`, then the invariant and status targets. Record the exact test count and host metadata.")
    write_doc("docs/reviewer_1day_validation.md", "Reviewer One-Day Validation", "Run the full suite, fetch the pinned CERN sample, execute the open-data benchmark, and use a PMU-enabled host for native profiling. Treat unfavorable results as reportable results.")
    write_doc("docs/engine_invariant_tests.md", "Engine Invariant Tests", f"Status: `{invariants['status']}`.\n\n" + table([{"check": k, "passes": v} for k, v in invariants["checks"].items()], ("check", "passes")) + "\n\nThese tests cover four-vector transformations, not detector reconstruction.")
    core_table = table(core["core_items"], ("core_id", "name", "status", "remaining_blockers"))
    write_doc("docs/minimal_theorem_core.md", "Minimal Theorem Core", "This is an evidence-gated map, not a claim of full completion.\n\n" + core_table)
    write_doc("docs/minimal_theorem_core_status_table.md", "Minimal Theorem Core Status Table", core_table)
    write_doc("docs/omega_f_action_audit.md", "Omega_f Action Audit", f"Status: `{action['omega_f']['status']}`.\n\n{action['omega_f']['claim_boundary']}\n\n## Remaining blockers\n\n" + "\n".join(f"- {x}" for x in action["omega_f"]["remaining_blockers"]))
    write_doc("docs/rho_ch_action_audit.md", "rho_ch Action Audit", f"Status: `{action['rho_ch']['status']}`. No value is selected.\n\n{action['rho_ch']['claim_boundary']}\n\n" + "\n".join(f"- {x}" for x in action["rho_ch"]["remaining_blockers"]))
    write_doc("docs/charged_overlap_source_audit.md", "Charged Overlap Source Audit", f"Status: `{action['charged_overlap']['status']}`.\n\n{action['charged_overlap']['claim_boundary']}\n\n" + "\n".join(f"- {x}" for x in action["charged_overlap"]["remaining_blockers"]))
    write_doc("docs/action_derivation_gates_report.md", "Action Derivation Gates Report", f"Overall status: `{action['status']}`. No empirical theorem inputs were used. Frozen predictions are unchanged.")
    falsification_rows = table(falsification["rows"], ("claim_id", "track", "claim", "current_status", "what_would_falsify_it"))
    write_doc("docs/falsification_table.md", "Brutal Falsification Table", falsification_rows)
    write_doc("docs/falsification_criteria_engine.md", "Engine Falsification Criteria", table([x for x in falsification["rows"] if x["track"] == "ENGINE"], ("claim_id", "claim", "current_status", "what_would_falsify_it")))
    write_doc("docs/falsification_criteria_physics.md", "Physics Falsification Criteria", table([x for x in falsification["rows"] if x["track"] == "PHYSICS"], ("claim_id", "claim", "current_status", "what_would_falsify_it")))
    write_doc("docs/external_reproduction_scope.md", "External Reproduction Scope", f"In scope: {external['scope']}.\n\nNot in scope:\n" + "\n".join(f"- {x}" for x in external["not_in_scope"]))
    write_doc("docs/external_reproduction_checklist.md", "External Reproduction Checklist", "- Record commit and hardware.\n- Verify the pinned CERN data checksum.\n- Run invariant and open-data commands.\n- Attach generated JSON.\n- Report negative results.\n- Do not interpret engine results as BHSM Physics validation.")
    write_doc("docs/external_reproduction_request.md", "External Reproduction Request", f"Draft only; no contact has been performed.\n\n> {external['draft_message']}\n\nPlease report host, compiler, SIMD flags, command output, and generated artifacts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
