import json
import subprocess
from pathlib import Path

from bhsm.interface.normalized_action_adjoint_pair import build_normalized_action_adjoint_pair_report


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = (
    "artifacts/BHSM_normalized_action_source_search_v2_5.json",
    "artifacts/BHSM_normalized_action_adjoint_pair_selection_v2_5.json",
    "artifacts/BHSM_hermitian_charged_current_action_rule_v2_5.json",
    "artifacts/BHSM_ckm_transport_space_gate_v2_5.json",
    "artifacts/BHSM_ckm_alternative_channel_blockers_v2_5.json",
)
REQUIRED_STATEMENTS = (
    "The existence of a Hermitian-conjugate charged-current term does not by itself derive the CKM exponent.",
    "The CKM exponent remains open unless BHSM proves that CKM transport acts on the normalized Hermitian adjoint-pair charged-current space.",
    "The bidirectional adjoint-pair channel count is 16, but this is a conditional channel assignment until selected by the normalized action.",
    "The maximal self-response channel also has dimension 16, but it is retired as the primary CKM source unless action evidence revives it.",
    "No empirical CKM fitting, charged-mass fitting, PDG values, W calibration, neutrino limits, or legacy threshold tables are used as theorem inputs.",
)


def test_normalized_action_artifacts_parse_and_preserve_boundaries():
    for relative in ARTIFACTS:
        payload = json.loads((ROOT / relative).read_text(encoding="utf-8"))
        assert payload
        assert payload["empirical_inputs_used"] is False
        assert payload["frozen_predictions_modified"] is False
        assert payload["official_prediction_logic_modified"] is False


def test_report_records_required_boundary_statements():
    report = build_normalized_action_adjoint_pair_report()
    for statement in REQUIRED_STATEMENTS:
        assert statement in report["required_boundary_statements"]
    assert report["artifact_backed_closures"] == []
    assert "REJECTED_ACTION_SELECTION_OVERCLAIM" in report["retired_or_rejected_claims"]


def test_docs_include_required_claim_boundaries():
    paths = [
        ROOT / "README.md",
        ROOT / "STATUS.md",
        ROOT / "docs" / "ckm_bidirectional_channel.md",
        ROOT / "docs" / "ckm_channel_equivalence.md",
        ROOT / "docs" / "normalized_action_adjoint_pair_selection.md",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    for statement in REQUIRED_STATEMENTS:
        assert statement in combined


def test_frozen_predictions_and_official_prediction_logic_unchanged_in_diff():
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

