"""Offline report surface for the neutrino bedrock/dynamic-layer doctrine."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ARTIFACT_PATH = "artifacts/neutrino_bedrock_dynamic_layer_v1.json"


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_neutrino_bedrock_status() -> dict[str, Any]:
    path = _repository_root() / ARTIFACT_PATH
    return json.loads(path.read_text(encoding="utf-8"))


def neutrino_bedrock_status_to_markdown(payload: dict[str, Any] | None = None) -> str:
    report = payload or load_neutrino_bedrock_status()
    lines = [
        "# Neutrino Bedrock and Dynamic-Layer Status",
        "",
        f"Status: `{report['status']}`",
        "",
        "## Bedrock Layer Allows",
        "",
        *(f"- {item}" for item in report["bedrock_layer_allows"]),
        "",
        "## Dynamic Layer Deferred",
        "",
        *(f"- {item}" for item in report["dynamic_layer_deferred"]),
        "",
        "## Forbidden Claims",
        "",
        *(f"- {item}" for item in report["forbidden_claims"]),
        "",
        "## Remaining Theorem Blockers",
        "",
        *(f"- {item}" for item in report["bedrock_blockers"]),
        *(f"- {item}" for item in report["dynamic_layer_open_blockers"]),
    ]
    return "\n".join(lines) + "\n"
