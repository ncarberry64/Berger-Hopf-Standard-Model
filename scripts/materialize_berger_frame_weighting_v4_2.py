"""Materialize deterministic v4.2 Berger frame-weighting artifacts and docs."""

import json
from pathlib import Path

from bhsm.interface.berger_frame_weighting import COMMAND_BUILDERS
from bhsm.interface.berger_frame_weighting.common import REQUIRED_STATEMENTS


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = {
    "BHSM_equal_frame_weighting_v4_2.json": "equal-frame-weighting",
    "BHSM_frame_average_normalization_v4_2.json": "frame-average-normalization",
    "BHSM_berger_anisotropy_compatibility_v4_2.json": "berger-anisotropy-compatibility",
    "BHSM_gauge_trace_frame_average_attachment_v4_2.json": "gauge-trace-frame-average-attachment-v4-2",
    "BHSM_gauge_denominator_update_v4_2.json": "gauge-denominator-update-v4-2",
    "BHSM_universal_quantum_update_v4_2.json": "universal-quantum-update-v4-2",
    "BHSM_gauge_action_attachment_update_v4_2.json": "gauge-action-attachment-update-v4-2",
    "BHSM_alpha_i_update_v4_2.json": "alpha-i-update-v4-2",
    "BHSM_g2_update_v4_2.json": "g2-update-v4-2",
    "BHSM_ckm_value_update_v4_2.json": "ckm-value-update-v4-2",
    "BHSM_full_completion_update_v4_2.json": "full-completion-update-v4-2",
}
DOCS = {
    "equal_frame_weighting.md": "equal-frame-weighting",
    "frame_average_normalization.md": "frame-average-normalization",
    "berger_anisotropy_compatibility.md": "berger-anisotropy-compatibility",
    "gauge_trace_frame_average_attachment_v4_2.md": "gauge-trace-frame-average-attachment-v4-2",
    "gauge_denominator_update_v4_2.md": "gauge-denominator-update-v4-2",
    "universal_quantum_update_v4_2.md": "universal-quantum-update-v4-2",
    "gauge_action_attachment_update_v4_2.md": "gauge-action-attachment-update-v4-2",
    "alpha_i_update_v4_2.md": "alpha-i-update-v4-2",
    "g2_update_v4_2.md": "g2-update-v4-2",
    "ckm_value_update_v4_2.md": "ckm-value-update-v4-2",
    "full_completion_update_v4_2.md": "full-completion-update-v4-2",
}
ROOT_DOCS = ("STATUS.md", "CLAIMS.md", "ROADMAP.md", "ARTIFACT_INDEX.md", "CLI_REFERENCE.md")
SUPPORTING_DOCS = (
    "docs/boundary_collar_measure_source.md", "docs/unit_s3_volume_normalization.md",
    "docs/three_boundary_frame_directions.md", "docs/boundary_frame_averaging.md",
    "docs/gauge_trace_frame_average_attachment.md", "docs/gauge_denominator_source_v4_1.md",
    "docs/full_theorem_blocker_dag.md", "docs/full_bhsm_completion_gate.md",
)
MARKER = "<!-- BHSM_BERGER_FRAME_WEIGHTING_V4_2 -->"


def _doc(command, payload):
    statements = "\n".join(f"- {line}" for line in REQUIRED_STATEMENTS)
    return (
        f"# {command.replace('-', ' ').title()} v4.2\n\nStatus: `{payload['status']}`\n\n"
        f"## Candidate\n\n`{payload['candidate_formula']}`\n\n## Claim boundary\n\n{payload['claim_boundary']}\n\n"
        f"## Required boundaries\n\n{statements}\n\nRun `python -m bhsm.interface {command} --format json`.\n"
    )


def _append_once(path, body):
    text = path.read_text(encoding="utf-8")
    if MARKER not in text:
        path.write_text(text.rstrip() + "\n\n" + body.rstrip() + "\n", encoding="utf-8")


def _root_block():
    statements = "\n".join(f"- {line}" for line in REQUIRED_STATEMENTS)
    return f"""{MARKER}
## Berger frame weighting v4.2

Equal weighting and frame-average normalization remain open. Berger anisotropy compatibility is
conditional on an action-selected orthonormal gauge coframe. Gauge attachment and all downstream
coupling gates remain open.

{statements}
"""


def _supporting_block():
    return f"""{MARKER}
## v4.2 frame-weighting update

The orthonormal-coframe compatibility route is conditional. No action-selected equal weights,
factor `1/3`, or gauge trace-density attachment was located, so the denominator and couplings remain open.
See [Berger anisotropy compatibility](berger_anisotropy_compatibility.md).
"""


def main():
    for filename, command in ARTIFACTS.items():
        payload = COMMAND_BUILDERS[command]()
        (ROOT / "artifacts" / filename).write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    for filename, command in DOCS.items():
        (ROOT / "docs" / filename).write_text(_doc(command, COMMAND_BUILDERS[command]()), encoding="utf-8")
    for path in ROOT_DOCS:
        _append_once(ROOT / path, _root_block())
    for path in SUPPORTING_DOCS:
        _append_once(ROOT / path, _supporting_block())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
