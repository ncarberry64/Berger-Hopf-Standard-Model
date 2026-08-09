import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "tools" / "audit_public_readiness.py"
SPEC = importlib.util.spec_from_file_location("audit_public_readiness", AUDIT_PATH)
assert SPEC is not None and SPEC.loader is not None
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


def run_json(*command: str) -> dict:
    result = subprocess.run(
        list(command),
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return json.loads(result.stdout)


def test_public_readiness_audit_passes_with_single_ready_verdict():
    result = AUDIT.audit()
    assert result["passed"] is True
    assert result["verdict"] == "BHSM_REPOSITORY_PUBLIC_REVIEW_READY"
    assert all(check["passed"] for check in result["checks"].values())


def test_required_files_links_citation_license_and_hygiene_pass():
    result = AUDIT.audit()
    for name in (
        "required_files",
        "markdown_links",
        "citation",
        "license_visibility",
        "hygiene",
    ):
        assert result["checks"][name]["passed"] is True
    citation = result["checks"]["citation"]
    assert citation["doi"] == "10.5281/zenodo.20663419"
    assert citation["release_tag"] == "v1.1.0"
    assert citation["zenodo_archive_version"] == "v1.2.0"
    assert citation["license"] == "LicenseRef-AllRightsReserved"


def test_current_surfaces_share_the_frozen_scientific_boundary():
    assert AUDIT.check_science_alignment()["passed"] is True
    for relative in AUDIT.ALIGNMENT_FILES:
        text = " ".join(AUDIT.current_slice(relative).split()).casefold()
        for phrase in AUDIT.ALIGNMENT_PHRASES:
            assert phrase in text


def test_handoff_has_supported_and_not_supported_review_sections():
    text = (
        ROOT / "docs" / "bhsm_public_scientific_handoff_v6_21_0.md"
    ).read_text(encoding="utf-8")
    for heading in (
        "## 4. What is currently derived",
        "## 5. What is adopted",
        "## 6. What has been rejected by calculation",
        "## 8. Exact current frontier",
        "## 10. What BHSM does not claim",
        "## 12. How to submit critique",
    ):
        assert heading in text


def test_quickstart_commands_and_engine_physics_boundary_are_public():
    assert AUDIT.check_reproduction_commands()["passed"] is True
    readme = AUDIT.read_text("README.md")
    quickstart = AUDIT.read_text("QUICKSTART.md")
    assert "Engine Validation Versus Physics Validation" in readme
    assert "Engine tests do not validate BHSM as particle physics" in readme
    assert "engine/physics claim separation" in quickstart
    assert "it is not empirical validation of\nBHSM physics" in quickstart
    for command in AUDIT.QUICKSTART_COMMANDS:
        assert command in quickstart


def test_frozen_predictions_and_official_prediction_logic_are_unchanged():
    frozen = AUDIT.check_frozen_predictions()
    assert frozen["passed"] is True
    assert frozen["frozen_predictions_changed"] is False
    status = run_json(sys.executable, "tools/audit_bhsm_status.py")
    assert status["passed"] is True
    assert status["checks"]["official_predictions_unchanged"] is True


def test_no_scientific_source_module_changed_in_v621_maintenance_commit():
    result = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            AUDIT.SOURCE_MAIN_SHA,
            "45dcb92e99a3edd7a0cbfb9d582e7bc409a5d8c3",
            "--",
            "src",
            "bhsm",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert result.stdout.strip() == ""


def test_manifest_is_canonical_and_deterministic():
    result = AUDIT.audit()
    expected = AUDIT.deterministic_json(AUDIT.manifest_payload(result))
    actual = AUDIT.MANIFEST.read_text(encoding="utf-8")
    assert actual == expected
    manifest = json.loads(actual)
    assert manifest["public_readiness_verdict"] == (
        "BHSM_REPOSITORY_PUBLIC_REVIEW_READY"
    )
    assert manifest["scientific_formulas_changed"] is False
    assert manifest["scientific_source_modules_changed"] is False
    assert manifest["official_prediction_logic_changed"] is False


def test_public_audit_cli_supports_human_and_json_output():
    human = subprocess.run(
        [sys.executable, str(AUDIT_PATH), "--format", "human"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout
    machine = run_json(
        sys.executable, str(AUDIT_PATH), "--format", "json"
    )
    assert "BHSM_REPOSITORY_PUBLIC_REVIEW_READY" in human
    assert machine["verdict"] == "BHSM_REPOSITORY_PUBLIC_REVIEW_READY"
