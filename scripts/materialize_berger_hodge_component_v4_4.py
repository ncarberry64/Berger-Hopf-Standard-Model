import json
from pathlib import Path

from bhsm.interface.berger_hodge_component_map import COMMAND_BUILDERS
from bhsm.interface.berger_hodge_component_map.common import REQUIRED_STATEMENTS

ROOT = Path(__file__).resolve().parents[1]
ITEMS = {
    "berger_hodge_component_map": "berger-hodge-component-map",
    "gauge_action_coframe_selection": "gauge-action-coframe-selection",
    "gauge_trace_hodge_component_expansion": "gauge-trace-hodge-component-expansion",
    "equal_coefficient_update": "equal-coefficient-update-v4-4",
    "frame_average_update": "frame-average-update-v4-4",
    "gauge_attachment_update": "gauge-attachment-update-v4-4",
    "denominator_update": "denominator-update-v4-4",
    "downstream_update": "downstream-update-v4-4",
    "full_completion_update": "full-completion-update-v4-4",
}
DOC_NAMES = {
    "berger_hodge_component_map": "berger_hodge_component_map.md",
    "gauge_action_coframe_selection": "gauge_action_coframe_selection.md",
    "gauge_trace_hodge_component_expansion": "gauge_trace_hodge_component_expansion.md",
    "equal_coefficient_update": "equal_coefficient_update_v4_4.md",
    "frame_average_update": "frame_average_update_v4_4.md",
    "gauge_attachment_update": "gauge_attachment_update_v4_4.md",
    "denominator_update": "denominator_update_v4_4.md",
    "downstream_update": "downstream_update_v4_4.md",
    "full_completion_update": "full_completion_update_v4_4.md",
}
MARKER = "<!-- BHSM_BERGER_HODGE_COMPONENT_V4_4 -->"


def render_doc(command, payload):
    statements = "\n".join(f"- {item}" for item in REQUIRED_STATEMENTS)
    return f"# {command.replace('-', ' ').title()} v4.4\n\nStatus: `{payload['status']}`\n\nCandidate: `{payload['candidate_formula']}`\n\nOrthonormal map: `{payload['orthonormal_formula']}`\n\nRaw Berger map: `{payload['raw_berger_formula']}`\n\n## Claim boundary\n\n{payload['claim_boundary']}\n\n{statements}\n\nRun `python -m bhsm.interface {command} --format json`.\n"


def append_once(path, body):
    text = path.read_text(encoding="utf-8")
    if MARKER not in text:
        path.write_text(text.rstrip() + "\n\n" + body + "\n", encoding="utf-8")


def main():
    for stem, command in ITEMS.items():
        payload = COMMAND_BUILDERS[command]()
        (ROOT / "artifacts" / f"BHSM_{stem}_v4_4.json").write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
        (ROOT / "docs" / DOC_NAMES[stem]).write_text(render_doc(command, payload), encoding="utf-8")
    block = MARKER + "\n## Berger Hodge component map v4.4\n\nThe explicit component map is conditionally derived from the Berger metric and chosen orientation. Gauge-action coframe selection, equal action coefficients, frame averaging, attachment, denominator, and downstream couplings remain open.\n\n" + "\n".join(f"- {item}" for item in REQUIRED_STATEMENTS)
    for name in ("STATUS.md", "CLAIMS.md", "ROADMAP.md", "ARTIFACT_INDEX.md", "CLI_REFERENCE.md"):
        append_once(ROOT / name, block)
    support = MARKER + "\n## v4.4 Berger Hodge update\n\nRaw Berger and orthonormal Hodge components are now explicit conditionally. This does not select the gauge-action basis or promote any normalization or coupling status."
    for name in ("docs/gauge_coframe_basis.md", "docs/hodge_star_metric_factors.md", "docs/anisotropy_compatibility_update_v4_3.md", "docs/equal_orthonormal_gauge_frame_coefficients.md", "docs/frame_average_update_v4_3.md", "docs/gauge_trace_attachment_update_v4_3.md", "docs/denominator_update_v4_3.md", "docs/full_bhsm_completion_gate.md"):
        append_once(ROOT / name, support)
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    text = text.replace("v4.3 finds the gauge coframe basis open and Hodge metric dependence conditional; averaging, attachment, couplings, CKM, scale, and transport remain open.", "v4.4 conditionally derives the Berger Hodge component map while gauge-action coframe selection, averaging, attachment, couplings, CKM, scale, and transport remain open.")
    readme.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
