"""Materialize deterministic v4.1 boundary/collar measure artifacts and docs."""

from __future__ import annotations

import json
from pathlib import Path

from bhsm.interface.boundary_collar_measure import COMMAND_BUILDERS
from bhsm.interface.boundary_collar_measure.common import REQUIRED_STATEMENTS


ROOT = Path(__file__).resolve().parents[1]

ARTIFACTS = {
    "BHSM_boundary_collar_measure_source_v4_1.json": "boundary-collar-measure-source",
    "BHSM_unit_s3_volume_normalization_v4_1.json": "unit-s3-volume-normalization",
    "BHSM_three_boundary_frame_directions_v4_1.json": "three-boundary-frame-directions",
    "BHSM_boundary_frame_averaging_v4_1.json": "boundary-frame-averaging-v4-1",
    "BHSM_gauge_trace_frame_average_attachment_v4_1.json": "gauge-trace-frame-average-attachment",
    "BHSM_gauge_denominator_source_v4_1.json": "gauge-denominator-source-v4-1",
    "BHSM_universal_gauge_quantum_update_v4_1.json": "universal-gauge-quantum-update",
    "BHSM_gauge_action_attachment_update_v4_1.json": "gauge-action-attachment-update",
    "BHSM_alpha_i_update_v4_1.json": "alpha-i-update-v4-1",
    "BHSM_g2_update_v4_1.json": "g2-update-v4-1",
    "BHSM_ckm_value_update_v4_1.json": "ckm-value-update-v4-1",
    "BHSM_full_completion_update_v4_1.json": "full-completion-update-v4-1",
}

DOCS = {
    "boundary_collar_measure_source.md": "boundary-collar-measure-source",
    "unit_s3_volume_normalization.md": "unit-s3-volume-normalization",
    "three_boundary_frame_directions.md": "three-boundary-frame-directions",
    "boundary_frame_averaging.md": "boundary-frame-averaging-v4-1",
    "gauge_trace_frame_average_attachment.md": "gauge-trace-frame-average-attachment",
    "gauge_denominator_source_v4_1.md": "gauge-denominator-source-v4-1",
    "universal_gauge_quantum_update.md": "universal-gauge-quantum-update",
    "gauge_action_attachment_update.md": "gauge-action-attachment-update",
    "alpha_i_update_v4_1.md": "alpha-i-update-v4-1",
    "g2_update_v4_1.md": "g2-update-v4-1",
    "ckm_value_update_v4_1.md": "ckm-value-update-v4-1",
    "full_completion_update_v4_1.md": "full-completion-update-v4-1",
}

ROOT_DOCS = ("STATUS.md", "CLAIMS.md", "ROADMAP.md", "ARTIFACT_INDEX.md", "CLI_REFERENCE.md")
SUPPORTING_DOCS = (
    "docs/full_action_status_snapshot.md", "docs/full_theorem_blocker_dag.md",
    "docs/gauge_denominator_source.md", "docs/gauge_coupling_volume_denominator.md",
    "docs/universal_gauge_coupling_quantum.md", "docs/gauge_coupling_action_attachment.md",
    "docs/alpha_i_action_gate.md", "docs/g2_action_gate.md", "docs/ckm_completion_gate.md",
    "docs/full_bhsm_completion_gate.md",
)
MARKER = "<!-- BHSM_BOUNDARY_COLLAR_MEASURE_V4_1 -->"


def _doc(command: str, payload: dict[str, object]) -> str:
    statements = "\n".join(f"- {line}" for line in REQUIRED_STATEMENTS)
    return (
        f"# {command.replace('-', ' ').title()} v4.1\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"## Candidate\n\n`{payload['candidate_formula']}`\n\n"
        f"## Claim boundary\n\n{payload['claim_boundary']}\n\n"
        f"## Required boundaries\n\n{statements}\n\n"
        f"Run `python -m bhsm.interface {command} --format json`.\n"
    )


def _append_once(path: Path, body: str) -> None:
    text = path.read_text(encoding="utf-8")
    if MARKER not in text:
        path.write_text(text.rstrip() + "\n\n" + body.rstrip() + "\n", encoding="utf-8")


def _root_block() -> str:
    statements = "\n".join(f"- {line}" for line in REQUIRED_STATEMENTS)
    return f"""{MARKER}
## Boundary/collar measure v4.1

Measure status: `CONDITIONAL_BOUNDARY_COLLAR_MEASURE_SOURCE`. Three coframe directions:
`ARTIFACT_BACKED_THREE_BOUNDARY_FRAME_DIRECTIONS`. Unit-S3 normalization, frame averaging,
gauge trace attachment, and the gauge denominator remain open.

{statements}
"""


def _supporting_block() -> str:
    return f"""{MARKER}
## v4.1 measure/frame update

The collar measure formula is conditional and three Berger coframe directions are artifact-backed.
Unit-S3 normalization, action-selected averaging, and gauge trace-density attachment remain open;
this result does not promote the gauge denominator, couplings, CKM value, or completion status.
See [boundary/collar measure source](boundary_collar_measure_source.md).
"""


def main() -> int:
    for filename, command in ARTIFACTS.items():
        payload = COMMAND_BUILDERS[command]()
        (ROOT / "artifacts" / filename).write_text(
            json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    for filename, command in DOCS.items():
        (ROOT / "docs" / filename).write_text(_doc(command, COMMAND_BUILDERS[command]()), encoding="utf-8")
    for path in ROOT_DOCS:
        _append_once(ROOT / path, _root_block())
    for path in SUPPORTING_DOCS:
        _append_once(ROOT / path, _supporting_block())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
