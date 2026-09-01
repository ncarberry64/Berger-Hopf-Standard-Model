"""Materialize the Git-lineage reduction for the integrated BHSM corpus."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "flagship_integration" / "BHSM_INTEGRATED_LINEAGE_REDUCTION.json"
BASE = "1e7e9e0e"


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, text=True, encoding="utf-8"
    ).strip()


def is_ancestor(commit: str, target: str) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit, target],
        cwd=ROOT,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def ref_inventory(main: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    output = git(
        "for-each-ref",
        "--format=%(refname)|%(objectname)|%(committerdate:iso-strict)|%(subject)",
        "refs/heads",
        "refs/remotes/origin",
    )
    for line in output.splitlines():
        ref, tip, date, subject = line.split("|", 3)
        if ref == "refs/remotes/origin/HEAD":
            continue
        rows.append(
            {
                "ref": ref,
                "tip": tip,
                "tip_date": date,
                "tip_subject": subject,
                "is_ancestor_of_main": is_ancestor(tip, main),
                "asset_policy": "BHSM_ASSET_RETAINED_AT_ORIGINAL_CLAIM_STRENGTH",
            }
        )
    return rows


def integration_merges() -> list[dict[str, object]]:
    output = git(
        "log",
        "--first-parent",
        "--merges",
        "--reverse",
        "--format=%H|%P|%s",
        f"{BASE}..main",
    )
    rows: list[dict[str, object]] = []
    for line in output.splitlines():
        commit, parents, subject = line.split("|", 2)
        rows.append(
            {
                "merge_commit": commit,
                "parents": parents.split(),
                "subject": subject,
            }
        )
    return rows


def main() -> int:
    main_tip = git("rev-parse", "main")
    refs = ref_inventory(main_tip)
    unmerged = [row["ref"] for row in refs if not row["is_ancestor_of_main"]]
    payload = {
        "schema_version": "1.0",
        "status": (
            "ALL_FETCHED_BHSM_LINEAGES_INTEGRATED__SEMANTIC_REDUCTION_ACTIVE"
            if not unmerged
            else "UNMERGED_BHSM_LINEAGES_REMAIN"
        ),
        "integration_tip": main_tip,
        "reconstruction_base": git("rev-parse", BASE),
        "integration_policy": {
            "all_lineages_are_bhsm_assets": True,
            "unique_files_are_imported": True,
            "same_path_conflicts_retain_current_adjudicated_semantics": True,
            "historical_claim_strength_is_preserved": True,
            "historical_or_candidate_results_are_not_silently_promoted": True,
            "particle_spectrum_is_not_rebuilt": True,
        },
        "canonical_reduction": {
            "upstream_registry": (
                "Existing particle/family/mode, representation, projector, current, "
                "and topological results are reusable upstream assets."
            ),
            "ae2_dynamics": (
                "The selected lambda24=0 reduced Euler-Dirac Hessian stop and its "
                "event child are derived dynamical objects."
            ),
            "missing_bridge": (
                "An action-owned local enclosure, matching/junction data, full-field "
                "attachment and balance, and structure-preserving transport into the "
                "existing SM manifestation class remain open."
            ),
            "manifestation_rule": (
                "A BHSM family or mode may manifest as an SM particle through the "
                "existing manifestation/readout architecture."
            ),
            "forbidden_equivalences": [
                "lambda24_zero_equals_two_pi",
                "selected_stop_equals_spacetime_edge",
                "positive_duration_equals_particle_stability",
            ],
        },
        "authoritative_records": [
            "docs/BHSM_NORMAN_SCHOOL_FULL_CORPUS_RECONSTRUCTION.md",
            "artifacts/flagship_integration/BHSM_NORMAN_SCHOOL_FULL_CORPUS_RECONSTRUCTION.json",
            "theory/n12_gate7_physical_encapsulation_identification_bridge.md",
            "artifacts/flagship_integration/BHSM_N12_GATE7_PHYSICAL_ENCAPSULATION_IDENTIFICATION_BRIDGE.json",
        ],
        "counts": {
            "refs_examined": len(refs),
            "refs_integrated": len(refs) - len(unmerged),
            "refs_unmerged": len(unmerged),
            "integration_merges_after_reconstruction": len(integration_merges()),
            "repository_files_after_reduction": int(
                git("ls-files", "--cached", "--others", "--exclude-standard").count("\n")
                + 1
            ),
        },
        "unmerged_refs": unmerged,
        "integration_merges": integration_merges(),
        "ref_inventory": refs,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(payload["status"])
    return 0 if not unmerged else 1


if __name__ == "__main__":
    raise SystemExit(main())
