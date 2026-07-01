import json
import subprocess
from pathlib import Path

from bhsm.interface.ckm_bounded_interface_normalization import build_ckm_bounded_interface_report


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = (
    "BHSM_ckm_bounded_interface_source_search_v2_7.json",
    "BHSM_ckm_bounded_interface_term_v2_7.json",
    "BHSM_normalized_projector_sandwich_action_term_v2_7.json",
    "BHSM_projector_domain_codomain_selection_v2_7.json",
    "BHSM_paired_term_normalization_v2_7.json",
    "BHSM_ckm_identification_gate_v2_7.json",
    "BHSM_ckm_transport_space_selection_v2_7.json",
)
REQUIRED_STATEMENTS = (
    "L_CKM_charged_current_bounded is a bounded interface term, not automatically a normalized action-selected transport operator.",
    "A normalized projector-sandwiched action term requires boundary/action measure, coefficient normalization, sector projectors, and action provenance.",
    "Projector arithmetic alone does not derive the CKM exponent.",
    "The CKM exponent remains not derived unless the normalized action selects a CKM transport space and the CKM identification theorem closes.",
    "No empirical CKM fitting, charged-mass fitting, PDG values, W calibration, neutrino limits, or legacy threshold tables are used as theorem inputs.",
)


def test_v27_artifacts_parse_and_use_no_empirical_inputs():
    for name in ARTIFACTS:
        payload = json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))
        assert payload["empirical_inputs_used"] is False
        assert payload["frozen_predictions_modified"] is False
        assert payload["official_prediction_logic_modified"] is False


def test_v27_report_preserves_boundaries_and_rejections():
    report = build_ckm_bounded_interface_report()
    assert len(report["required_boundary_statements"]) == 5
    assert report["artifact_backed_closures"] == ["ARTIFACT_BACKED_BOUNDED_CKM_INTERFACE_TERM"]
    assert "REJECTED_BOUNDED_TERM_IMPLIES_ACTION_SELECTION" in report["retired_or_rejected_claims"]
    assert report["channel_dimensions"]["one_way_up_down"] == 8
    assert report["channel_dimensions"]["bidirectional_adjoint_pair"] == 16


def test_v27_docs_include_required_claim_boundaries():
    paths = (
        ROOT / "README.md",
        ROOT / "STATUS.md",
        ROOT / "CLAIMS.md",
        ROOT / "docs/ckm_bounded_interface_term.md",
        ROOT / "docs/normalized_projector_sandwich_action_term.md",
        ROOT / "docs/projector_domain_codomain_selection.md",
        ROOT / "docs/ckm_identification_gate.md",
        ROOT / "docs/ckm_transport_space_selection.md",
    )
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    for statement in REQUIRED_STATEMENTS:
        assert statement in combined


def test_v27_does_not_touch_protected_prediction_logic():
    protected = (
        "docs/frozen_predictions.md",
        "docs/frozen_predictions.json",
        "src/bhsm_model.py",
        "src/bhsm/interface/predictions.py",
        "artifacts/CKM_no_fit_operator_output_v1.json",
    )
    result = subprocess.run(
        ["git", "diff", "--name-only", "--", *protected],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == ""
