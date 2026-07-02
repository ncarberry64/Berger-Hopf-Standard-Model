"""Materialize deterministic v4.0 full-action closure artifacts and documents."""

from __future__ import annotations

import json
from pathlib import Path

from bhsm.interface.full_action_closure import COMMAND_BUILDERS
from bhsm.interface.full_action_closure.common import REQUIRED_STATEMENTS


ROOT = Path(__file__).resolve().parents[1]

ARTIFACTS = {
    "BHSM_full_action_status_snapshot_v4_0.json": "full-action-status-snapshot",
    "BHSM_full_theorem_blocker_dag_v4_0.json": "full-theorem-blocker-dag",
    "BHSM_unified_action_skeleton_v4_0.json": "unified-action-skeleton",
    "BHSM_boundary_frame_averaging_v4_0.json": "boundary-frame-averaging",
    "BHSM_gauge_denominator_source_v4_0.json": "gauge-denominator-source",
    "BHSM_sector_weight_action_attachment_v4_0.json": "sector-weight-action-attachment",
    "BHSM_gauge_action_coefficient_k_v4_0.json": "gauge-action-coefficient-k",
    "BHSM_alpha_i_action_gate_v4_0.json": "alpha-i-action-gate",
    "BHSM_g2_action_gate_v4_0.json": "g2-action-gate",
    "BHSM_ckm_completion_gate_v4_0.json": "ckm-completion-gate",
    "BHSM_neutral_scale_gate_v4_0.json": "neutral-scale-gate",
    "BHSM_scalar_topographic_gate_v4_0.json": "scalar-topographic-gate",
    "BHSM_dimensionful_scale_bridge_v4_0.json": "dimensionful-scale-bridge",
    "BHSM_full_completion_gate_v4_0.json": "full-bhsm-completion-gate",
}

DOCS = {
    "full_action_status_snapshot.md": "full-action-status-snapshot",
    "full_theorem_blocker_dag.md": "full-theorem-blocker-dag",
    "unified_action_skeleton.md": "unified-action-skeleton",
    "boundary_frame_averaging.md": "boundary-frame-averaging",
    "gauge_denominator_source.md": "gauge-denominator-source",
    "sector_weight_action_attachment.md": "sector-weight-action-attachment",
    "gauge_action_coefficient_k.md": "gauge-action-coefficient-k",
    "alpha_i_action_gate.md": "alpha-i-action-gate",
    "g2_action_gate.md": "g2-action-gate",
    "ckm_completion_gate.md": "ckm-completion-gate",
    "neutral_scale_gate.md": "neutral-scale-gate",
    "scalar_topographic_gate.md": "scalar-topographic-gate",
    "dimensionful_scale_bridge.md": "dimensionful-scale-bridge",
    "full_bhsm_completion_gate.md": "full-bhsm-completion-gate",
}

ROOT_DOCS = (
    "STATUS.md", "CLAIMS.md", "ROADMAP.md", "ARTIFACT_INDEX.md", "CLI_REFERENCE.md",
)

SUPPORTING_DOCS = (
    "docs/minimal_theorem_core.md", "docs/falsification_table.md", "docs/bhsm_physics_status.md",
    "docs/gauge_coupling_registry_pattern.md", "docs/gauge_coupling_volume_denominator.md",
    "docs/universal_gauge_coupling_quantum.md", "docs/gauge_coupling_action_attachment.md",
    "docs/alpha_i_action_derivation.md", "docs/g2_action_source_update.md", "docs/ckm_value_source_update.md",
    "docs/neutrino_bedrock_dynamic_layer.md",
)

V4_MARKER = "<!-- BHSM_FULL_ACTION_CLOSURE_V4_0 -->"


def _append_once(path: Path, block: str) -> None:
    text = path.read_text(encoding="utf-8")
    if V4_MARKER not in text:
        path.write_text(text.rstrip() + "\n\n" + block.rstrip() + "\n", encoding="utf-8")


def _root_update() -> str:
    statements = "\n".join(f"- {statement}" for statement in REQUIRED_STATEMENTS)
    return f"""{V4_MARKER}
## Full action closure v4.0

Status: `FULL_BHSM_NOT_COMPLETE`.

The deterministic blocker DAG is in [docs/full_theorem_blocker_dag.md](docs/full_theorem_blocker_dag.md) and
`artifacts/BHSM_full_theorem_blocker_dag_v4_0.json`.

{statements}
"""


def _supporting_update(path: str) -> str:
    prefix = "../" if path.startswith("docs/") else ""
    return f"""{V4_MARKER}
## v4.0 action-normalization status

This surface is incorporated into the [{prefix}full-action blocker DAG]({prefix}docs/full_theorem_blocker_dag.md).
Its existing artifact-backed or conditional result is preserved; it is not promoted across a missing action,
normalization, transport, or dimensionful-scale gate. Overall status: `FULL_BHSM_NOT_COMPLETE`.
"""


def _doc(command: str, payload: dict[str, object]) -> str:
    title = command.replace("-", " ").title()
    statements = "\n".join(f"- {statement}" for statement in REQUIRED_STATEMENTS)
    return (
        f"# {title} v4.0\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"## Claim boundary\n\n{payload['claim_boundary']}\n\n"
        f"## Required repository boundaries\n\n{statements}\n\n"
        f"## Machine-readable source\n\n"
        f"Run `python -m bhsm.interface {command} --format json`.\n"
    )


def main() -> int:
    for filename, command in ARTIFACTS.items():
        payload = COMMAND_BUILDERS[command]()
        (ROOT / "artifacts" / filename).write_text(
            json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    for filename, command in DOCS.items():
        payload = COMMAND_BUILDERS[command]()
        (ROOT / "docs" / filename).write_text(_doc(command, payload), encoding="utf-8")
    for path in ROOT_DOCS:
        _append_once(ROOT / path, _root_update())
    for path in SUPPORTING_DOCS:
        _append_once(ROOT / path, _supporting_update(path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
