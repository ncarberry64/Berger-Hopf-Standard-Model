import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = (
    "BHSM_theorem_closure_sprint_a_manifest_v0_4.json",
    "BHSM_theorem_closure_report_v0_4.json",
    "BHSM_x_ch_theorem_closure_attempt_v0_4.json",
    "BHSM_neutrino_basis_scale_theorem_closure_attempt_v0_4.json",
    "BHSM_cp_o_int_theorem_closure_attempt_v0_4.json",
    "BHSM_theorem_proof_gate_summary_v0_4.json",
    "BHSM_theorem_registry_update_proposal_v0_4.json",
    "BHSM_theorem_closure_claim_policy_v0_4.json",
)


def test_closure_artifacts_exist_parse_and_do_not_promote():
    payloads = [json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8")) for name in ARTIFACTS]
    report = payloads[1]
    assert report["promotions_allowed"] == []
    assert report["empirical_derivation_inputs_used"] is False
    assert report["reference_values_used_as_derivation_inputs"] is False


def test_docs_contain_warnings_and_readme_section():
    docs = "\n".join((ROOT / "docs" / name).read_text(encoding="utf-8") for name in (
        "theorem_closure_sprint_a.md", "x_ch_theorem_closure_attempt.md",
        "neutrino_basis_scale_theorem_closure_attempt.md", "cp_o_int_theorem_closure_attempt.md",
        "theorem_proof_gates.md", "theorem_closure_claim_policy.md",
    ))
    for warning in (
        "Theorem closure requires executable artifact-backed support; narrative plausibility is not enough.",
        "Reference values, including PDG values, are comparison inputs only and are never theorem inputs.",
        "A partial localization is not a production prediction.",
        "Runtime-disabled software gates remain disabled until live external validation passes.",
        "The neutral operator kernel is not promoted to a physical neutrino mass matrix without a physical basis, dimensional scale, and Dirac/Majorana convention.",
    ):
        assert warning in docs
    assert "## Candidate And Open Theorem Areas" in (ROOT / "README.md").read_text(encoding="utf-8")


def test_frozen_predictions_unchanged():
    expected = {
        "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
        "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    }
    for path, digest in expected.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
