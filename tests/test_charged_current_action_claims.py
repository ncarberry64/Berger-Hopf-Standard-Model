import json
import subprocess
from pathlib import Path

from bhsm.interface.charged_current_action import build_charged_current_action_report


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = (
    "artifacts/BHSM_charged_current_action_source_search_v2_6.json",
    "artifacts/BHSM_normalized_charged_current_action_term_v2_6.json",
    "artifacts/BHSM_charged_current_transport_space_audit_v2_6.json",
    "artifacts/BHSM_hermitian_adjoint_pair_transport_gate_v2_6.json",
    "artifacts/BHSM_ckm_transport_space_application_gate_v2_6.json",
)
REQUIRED_STATEMENTS = (
    "The normalized charged-current action term, not arithmetic channel-count coincidence, must select the CKM transport space.",
    "The Hermitian adjoint-pair channel count is 16, but the CKM exponent remains not derived unless BHSM proves CKM acts on that selected transport space.",
    "The existence of a Hermitian-conjugate term supports action reality but does not by itself derive CKM transport-space selection.",
    "Same numerical dimension does not establish the physical source.",
    "No empirical CKM fitting, charged-mass fitting, PDG values, W calibration, neutrino limits, or legacy threshold tables are used as theorem inputs.",
)


def test_charged_current_action_artifacts_parse_and_preserve_boundaries():
    for relative in ARTIFACTS:
        payload = json.loads((ROOT / relative).read_text(encoding="utf-8"))
        assert payload
        assert payload["empirical_inputs_used"] is False
        assert payload["frozen_predictions_modified"] is False
        assert payload["official_prediction_logic_modified"] is False


def test_charged_current_action_report_records_required_boundaries():
    report = build_charged_current_action_report()
    for statement in REQUIRED_STATEMENTS:
        assert statement in report["required_boundary_statements"]
    assert report["artifact_backed_closures"] == []
    assert report["conditional_closures"] == []
    assert "RETIRED_MAXIMAL_SELF_RESPONSE_AS_PRIMARY_CKM_SOURCE" in report["retired_or_rejected_claims"]


def test_charged_current_action_docs_include_required_boundaries():
    paths = [
        ROOT / "README.md",
        ROOT / "STATUS.md",
        ROOT / "docs" / "normalized_charged_current_action_term.md",
        ROOT / "docs" / "charged_current_transport_space.md",
        ROOT / "docs" / "hermitian_adjoint_pair_transport_gate.md",
        ROOT / "docs" / "ckm_transport_space_application_gate.md",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    for statement in REQUIRED_STATEMENTS:
        assert statement in combined


def test_charged_current_action_does_not_touch_frozen_or_official_logic():
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
