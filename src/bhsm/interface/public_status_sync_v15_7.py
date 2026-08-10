"""Machine checks for the v15.9 public current-status contract.

The historical filename remains a compatibility surface for existing tooling.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

from .aether_cycle_spread_concentration_v15_9 import EXACT_NEXT_OBJECT, PRIMARY_VERDICT
from .current_program_status import CURRENT_VERSION, status_payload
from .science_hardening import payload_for_command


ROOT = Path(__file__).resolve().parents[3]
CURRENT_SECTIONS = {
    "README.md": ("## Current Public Status", "This independent mathematical-physics project"),
    "STATUS.md": ("## Current public summary", "## Historical v11.6"),
    "CLAIMS.md": ("## Current public claim boundary", "## Historical claim boundaries"),
    "ARTIFACT_INDEX.md": ("## Current BHSM v15.9", "## BHSM v11.5"),
    "docs/README.md": ("## Current v15.9", "## Historical v11.5"),
    "docs/current_bhsm_status.md": ("## v15.9", "## v14.2"),
    "docs/BHSM_1_0_DEFINITION_OF_DONE.md": ("## Current v15.9", "## Historical v11.1"),
    "theory/gate_ledger.md": ("## v15.9", "## v14.1"),
    "CLI_REFERENCE.md": ("## Current v15.9", "## BHSM v11.2"),
    "ROADMAP.md": ("## Current v15.9", "## Historical v11.6"),
    "FALSIFICATION.md": ("## Current v15.9", "## Historical v11.6"),
}


def _section(path: Path, start: str, end: str) -> str:
    text = path.read_text(encoding="utf-8")
    if start not in text or end not in text:
        raise ValueError(f"missing current-section marker in {path}")
    return start + text.split(start, 1)[1].split(end, 1)[0]


def current_surface_sections(root: Path = ROOT) -> dict[str, str]:
    return {
        name: _section(root / name, start, end)
        for name, (start, end) in CURRENT_SECTIONS.items()
    }


def stale_current_status_hits(root: Path = ROOT) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    for name, text in current_surface_sections(root).items():
        for match in re.finditer(r"(?i)current[^\n]{0,80}\bv(?!15\.9\b)\d+(?:\.\d+)+", text):
            hits.append({"file": name, "text": match.group(0)})
    return hits


def semantic_status_audit(root: Path = ROOT) -> dict[str, Any]:
    sections = current_surface_sections(root)
    status_json = json.loads((root / "docs/current_bhsm_status.json").read_text(encoding="utf-8"))
    cli = payload_for_command("physics-status")
    cli_current = cli["physics_current_status"]
    surfaces = {
        name: EXACT_NEXT_OBJECT in text
        and (CURRENT_VERSION in text or CURRENT_VERSION in CURRENT_SECTIONS[name][0])
        for name, text in sections.items()
    }
    surfaces["docs/current_bhsm_status.json"] = (
        status_json["current_version"] == CURRENT_VERSION
        and status_json["primary_verdict"] == PRIMARY_VERDICT
        and status_json["exact_next_object"] == EXACT_NEXT_OBJECT
        and status_json["FULL_BHSM_COMPLETE"] is False
    )
    surfaces["physics-status CLI"] = (
        cli_current["current_version"] == CURRENT_VERSION
        and cli_current["primary_verdict"] == PRIMARY_VERDICT
        and cli_current["exact_next_object"] == EXACT_NEXT_OBJECT
        and cli_current["FULL_BHSM_COMPLETE"] is False
    )
    python_status = status_payload()
    surfaces["Python status"] = python_status["current_version"] == CURRENT_VERSION
    return {
        "version": CURRENT_VERSION,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "surface_results": surfaces,
        "all_current": all(surfaces.values()),
        "stale_current_status_hits": stale_current_status_hits(root),
    }


def broken_current_links(root: Path = ROOT) -> list[dict[str, str]]:
    broken: list[dict[str, str]] = []
    link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for name, text in current_surface_sections(root).items():
        source = root / name
        for target in link_pattern.findall(text):
            if re.match(r"(?:https?://|mailto:|#)", target):
                continue
            clean = target.split("#", 1)[0]
            if not clean:
                continue
            resolved = (source.parent / clean).resolve()
            if not resolved.exists():
                broken.append({"file": name, "target": target})
    return broken


def audit_payload(root: Path = ROOT) -> dict[str, Any]:
    semantic = semantic_status_audit(root)
    links = broken_current_links(root)
    return {
        **semantic,
        "broken_current_links": links,
        "broken_current_link_count": len(links),
        "pass": semantic["all_current"]
        and not semantic["stale_current_status_hits"]
        and not links,
        "USB_TOUCHED": False,
    }
