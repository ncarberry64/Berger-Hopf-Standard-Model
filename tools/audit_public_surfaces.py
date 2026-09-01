"""Fail-closed audit for canonical BHSM public presentation surfaces."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
STATUS_JSON = ROOT / "docs/current_bhsm_status.json"
CANONICAL_MUSEUM = "https://ncarberry64.github.io/Berger-Hopf-Standard-Model/"
FLAGS = {
    "UNCHANGED_AE2_LOCALIZATION_CARRIER_FOUND": False,
    "PHYSICAL_ENCAPSULATION_IDENTIFIED": False,
    "FULL_BHSM_COMPLETE": False,
}
PUBLIC_TEXT = (
    "README.md",
    "docs/current_bhsm_status.md",
    "museum/app/page.tsx",
)
FLAG_SURFACES = (
    "README.md",
    "STATUS.md",
    "CLAIMS.md",
    "docs/README.md",
    "docs/current_bhsm_status.md",
    "museum/app/page.tsx",
)
CMS_REQUIRED = (
    "Coordinate-engine validation—not a BHSM physics test",
    "No detector reconstruction",
    "no BHSM empirical validation",
    "no CERN/CMS endorsement",
    "https://opendata.cern.ch/record/303",
    "pr98_cms_sample_manifest.json",
    "artifacts/cern_open_data_benchmark/results.json",
    "tests/test_cern_open_data_benchmark.py",
    "100,000 events",
    "200,000 unique muon",
)
GENERATED_PATH = re.compile(
    r"(^|/)(node_modules|dist|\.next|__pycache__|coverage|\.cache)(/|$)|\.pyc$"
)
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def _text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def audit() -> dict:
    status = json.loads(STATUS_JSON.read_text(encoding="utf-8"))
    surfaces = {relative: _text(relative) for relative in PUBLIC_TEXT}
    joined = "\n".join(surfaces.values())
    flag_surface_text = {relative: _text(relative) for relative in FLAG_SURFACES}
    flag_checks = {
        name: status.get(name) is expected
        and status.get("flags", {}).get(name) is expected
        and all(
            f"{name} = FALSE" in text
            for text in flag_surface_text.values()
        )
        for name, expected in FLAGS.items()
    }

    museum_source = _text("museum/app/exhibits.ts")
    page_source = surfaces["museum/app/page.tsx"]
    cms_blob = " ".join((museum_source + "\n" + page_source).split())
    cms_checks = {
        phrase: phrase.casefold() in cms_blob.casefold() for phrase in CMS_REQUIRED
    }

    tracked = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout.splitlines()
    generated_tracked = [path for path in tracked if GENERATED_PATH.search(path)]

    provenance_paths = (
        "docs/assets/pr98_cms_open_data_animation/pr98_cms_sample_manifest.json",
        "docs/assets/pr98_cms_open_data_animation/generate_pr98_cms_animation.py",
        "artifacts/cern_open_data_benchmark/results.json",
        "tests/test_cern_open_data_benchmark.py",
        "museum/ASSET_PROVENANCE.md",
    )
    provenance_checks = {
        path: (ROOT / path).is_file() for path in provenance_paths
    }

    broken_links: list[dict[str, str]] = []
    for relative in (
        "README.md",
        "docs/current_bhsm_status.md",
        "docs/public_terminology.md",
        "docs/reviewer_start_here.md",
        "docs/archive/status/README.md",
    ):
        source = ROOT / relative
        for target in MARKDOWN_LINK.findall(source.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            clean = unquote(target.split("#", 1)[0]).strip("<>")
            if clean and not (source.parent / clean).resolve().exists():
                broken_links.append({"source": relative, "target": target})

    checks = {
        "canonical_schema": status.get("schema_version") == "2.0"
        and status.get("canonical_public_status") is True,
        "gate_7_open": status.get("gate_7", {}).get("status") == "OPEN",
        "flags_fail_closed": all(flag_checks.values()),
        "observable_machinery_gated": status.get(
            "observable_machinery_classification"
        )
        == "IMPLEMENTED_BUT_PHYSICAL_PROMOTION_GATED",
        "cms_boundary_complete": all(cms_checks.values()),
        "cms_provenance_resolves": all(provenance_checks.values()),
        "canonical_markdown_links_resolve": not broken_links,
        "canonical_museum_url": status.get("canonical_museum_url")
        == CANONICAL_MUSEUM
        and CANONICAL_MUSEUM in surfaces["README.md"]
        and CANONICAL_MUSEUM in _text("museum/app/layout.tsx")
        and CANONICAL_MUSEUM in _text("museum/app/exhibits.ts"),
        "historical_surfaces_archived": all(
            (ROOT / path).is_file()
            for path in (
                "docs/archive/status/README_pre_canonical_front_door_2026_09_01.md",
                "docs/archive/status/current_bhsm_status_pre_2026_09_01.md",
                "docs/archive/status/current_bhsm_status_pre_2026_09_01.json",
            )
        ),
        "no_tracked_generated_output": not generated_tracked,
        "no_full_completion_promotion": not re.search(
            r"FULL_BHSM_COMPLETE\s*[=:]\s*TRUE", joined, re.IGNORECASE
        ),
        "no_cms_physics_promotion": "CMS Open Data validates BHSM physics"
        not in joined,
    }
    return {
        "audit": "bhsm_public_surfaces",
        "passed": all(checks.values()),
        "checks": checks,
        "flag_checks": flag_checks,
        "cms_checks": cms_checks,
        "provenance_checks": provenance_checks,
        "generated_tracked": generated_tracked,
        "broken_links": broken_links,
    }


if __name__ == "__main__":
    result = audit()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["passed"] else 1)
