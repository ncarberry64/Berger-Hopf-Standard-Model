"""Compatibility entry point for the canonical BHSM public-status audit.

The historical module name remains import-stable. Current public authority is
the schema-v2 status pair under ``docs/``; legacy campaign ledgers are archives.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CURRENT_SECTIONS = {
    "README.md": ("## Current research status", "## How to read claims"),
    "STATUS.md": ("# BHSM Status Ledger", "## Authoritative current checkpoint"),
    "CLAIMS.md": ("# BHSM Claim Boundaries Ledger", "## Authoritative Gate-7 claim boundary"),
    "docs/README.md": ("## Canonical current authority", "## Historical v15.10 campaign"),
    "docs/current_bhsm_status.md": ("## Verdict", "## What is established at the retained scope"),
}
FLAGS = (
    "UNCHANGED_AE2_LOCALIZATION_CARRIER_FOUND",
    "PHYSICAL_ENCAPSULATION_IDENTIFIED",
    "FULL_BHSM_COMPLETE",
)


def _section(path: Path, start: str, end: str) -> str:
    text = path.read_text(encoding="utf-8")
    if start not in text or end not in text:
        raise ValueError(f"missing canonical-section marker in {path}")
    return start + text.split(start, 1)[1].split(end, 1)[0]


def current_surface_sections(root: Path = ROOT) -> dict[str, str]:
    return {
        name: _section(root / name, start, end)
        for name, (start, end) in CURRENT_SECTIONS.items()
    }


def stale_current_status_hits(root: Path = ROOT) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    patterns = (
        re.compile(r"ACTIVE_NOT_CLOSED"),
        re.compile(r"FULL_BHSM_COMPLETE\s*[=:]\s*TRUE", re.IGNORECASE),
        re.compile(r"PHYSICAL_ENCAPSULATION_IDENTIFIED\s*[=:]\s*TRUE", re.IGNORECASE),
    )
    for name, text in current_surface_sections(root).items():
        for pattern in patterns:
            for match in pattern.finditer(text):
                hits.append({"file": name, "text": match.group(0)})
    return hits


def semantic_status_audit(root: Path = ROOT) -> dict[str, Any]:
    sections = current_surface_sections(root)
    status = json.loads(
        (root / "docs/current_bhsm_status.json").read_text(encoding="utf-8")
    )
    surfaces = {
        name: all(f"{flag} = FALSE" in text for flag in FLAGS)
        for name, text in sections.items()
    }
    surfaces["docs/current_bhsm_status.json"] = (
        status.get("schema_version") == "2.0"
        and status.get("canonical_public_status") is True
        and status.get("gate_7", {}).get("status") == "OPEN"
        and all(status.get(flag) is False for flag in FLAGS)
    )
    return {
        "version": status.get("schema_version"),
        "exact_next_object": status.get("exact_promotion_dependency"),
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
            if clean and not (source.parent / clean).resolve().exists():
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
