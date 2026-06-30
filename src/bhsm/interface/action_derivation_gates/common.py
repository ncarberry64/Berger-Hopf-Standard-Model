"""Shared repository-source helpers for action provenance gates."""

from __future__ import annotations

from pathlib import Path


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def source_evidence(paths: tuple[str, ...], tokens: tuple[str, ...]) -> dict[str, object]:
    root = repository_root()
    present = []
    token_hits = {token: [] for token in tokens}
    for relative in paths:
        path = root / relative
        if not path.is_file():
            continue
        present.append(relative)
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in tokens:
            if token in text:
                token_hits[token].append(relative)
    return {
        "source_paths": list(paths),
        "present_paths": present,
        "token_hits": token_hits,
        "all_paths_present": len(present) == len(paths),
        "all_tokens_present": all(token_hits.values()),
    }


FORBIDDEN_INPUTS = [
    "PDG/reference values",
    "W-mass calibration",
    "charged-mass fitting",
    "CKM reference fitting",
    "neutrino limits",
    "legacy threshold tables",
]
