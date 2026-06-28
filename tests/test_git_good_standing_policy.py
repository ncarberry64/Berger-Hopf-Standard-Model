from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_final_completion_sprint_does_not_encode_destructive_git_operations() -> None:
    paths = (
        ROOT / "docs/common_16_closure_report.md",
        ROOT / "artifacts/BHSM_final_completion_claim_policy_v1_8.json",
    )
    text = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    for forbidden in ("git push --force", "git branch -D", "git push origin --delete"):
        assert forbidden not in text


def test_frozen_files_keep_release_hashes() -> None:
    import hashlib

    expected = {
        "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
        "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    }
    for relative, digest in expected.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest


def test_official_prediction_logic_and_ckm_artifact_are_unchanged() -> None:
    import hashlib

    expected = {
        "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
        "src/bhsm/interface/predictions.py": "ea0539bef06184c619dd028eafafb76ea15e92a444483ff93637593f0eaa1fed",
        "artifacts/CKM_no_fit_operator_output_v1.json": "9c354e8812682c75187c00becb90ff44b5dcc74aef10992103df28b34321d757",
    }
    for relative, digest in expected.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
