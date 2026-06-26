import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CURRENT_STATUS = (
    "BHSM v1.0.0 internal boundary no-fit package complete/exported; "
    "external empirical comparison layer separate/open"
)
FROZEN_HASHES = {
    ROOT / "docs" / "frozen_predictions.md": (
        "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4"
    ),
    ROOT / "docs" / "frozen_predictions.json": (
        "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7"
    ),
}


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def load(relative: str) -> dict:
    return json.loads(read(relative))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def squash(text: str) -> str:
    return " ".join(text.split())


def run_tool(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_readme_preserves_status_and_ufo_pipeline_boundaries() -> None:
    text = read("README.md")
    assert CURRENT_STATUS in text
    assert "UFO / event-generation pipeline status" in text
    assert "does not yet export a production UFO model" in text
    assert "No collider events are generated unless a real validated Lagrangian" in text


def test_required_ufo_pipeline_docs_exist() -> None:
    for relative in [
        "docs/ufo_pipeline.md",
        "docs/feynman_rules_status.md",
        "docs/bhsm_lagrangian_schema.md",
        "docs/madgraph_event_generation_path.md",
        "docs/lhe_hepmc_generation_status.md",
    ]:
        assert (ROOT / relative).exists(), relative

    assert "pipeline_stage = PHASE_ONE_SCAFFOLD" in read("docs/ufo_pipeline.md")
    assert "ufo_export_ready = false" in read("docs/ufo_pipeline.md")
    assert "event_generation_ready = false" in read("docs/ufo_pipeline.md")
    assert "does not currently export a full set of collider-ready Feynman rules" in squash(
        read("docs/feynman_rules_status.md")
    )


def test_schemas_and_templates_exist_and_parse() -> None:
    schemas = [
        "schemas/bhsm_lagrangian_schema_v0_1.json",
        "schemas/bhsm_field_content_schema_v0_1.json",
        "schemas/bhsm_parameter_card_schema_v0_1.json",
        "schemas/bhsm_vertex_schema_v0_1.json",
        "schemas/bhsm_ufo_export_manifest_schema_v0_1.json",
    ]
    templates = [
        "data/bhsm_lagrangian_template_v0_1.json",
        "data/bhsm_field_content_template_v0_1.json",
        "data/bhsm_parameter_card_template_v0_1.json",
        "data/bhsm_vertex_template_v0_1.json",
    ]
    for relative in [*schemas, *templates]:
        payload = load(relative)
        assert isinstance(payload, dict)

    lagrangian_template = load("data/bhsm_lagrangian_template_v0_1.json")
    assert "NOT_A_PHYSICAL_LAGRANGIAN" in lagrangian_template["template_status"]
    assert "STRUCTURAL_TEMPLATE_ONLY" in lagrangian_template["template_status"]
    assert "DO_NOT_USE_FOR_EVENT_GENERATION" in lagrangian_template["template_status"]
    assert lagrangian_template["complete_4d_lagrangian_exported"] is False
    assert lagrangian_template["event_generation_ready"] is False


def test_ufo_audit_and_status_artifacts_are_not_ready() -> None:
    audit = load("artifacts/BHSM_ufo_pipeline_phase_one_audit_v0_1.json")
    feynman = load("artifacts/BHSM_feynman_rule_export_status_v0_1.json")
    blockers = load("artifacts/BHSM_event_generation_blocker_ledger_v0_1.json")
    manifest = load("artifacts/BHSM_ufo_export_manifest_v0_1.json")

    for payload in [audit, feynman, blockers, manifest]:
        assert payload["empirical_derivation_inputs_used"] is False
        assert payload["boundary_predictions_modified_by_comparison"] is False
        assert payload["official_predictions_changed"] is False

    assert audit["pipeline_stage"] == "PHASE_ONE_SCAFFOLD"
    assert audit["ufo_export_ready"] is False
    assert audit["event_generation_ready"] is False
    assert audit["athena_ready"] is False
    assert audit["cmssw_ready"] is False
    assert audit["complete_4d_lagrangian_exported"] is False
    assert audit["feynman_rules_exported"] is False
    assert feynman["feynman_rules_exported"] is False
    assert blockers["event_generation_ready"] is False
    assert manifest["ufo_export_ready"] is False


def test_validators_exit_cleanly_on_templates() -> None:
    lagrangian = run_tool("tools/validate_bhsm_lagrangian_schema.py")
    assert lagrangian.returncode == 0
    lagrangian_payload = json.loads(lagrangian.stdout)
    assert lagrangian_payload["schema_fields_present"] is True
    assert lagrangian_payload["complete_4d_lagrangian_exported"] is False
    assert lagrangian_payload["event_generation_ready"] is False

    ufo_inputs = run_tool("tools/validate_bhsm_ufo_inputs.py")
    assert ufo_inputs.returncode == 0
    ufo_payload = json.loads(ufo_inputs.stdout)
    assert ufo_payload["structural_templates_valid"] is True
    assert ufo_payload["ufo_export_ready"] is False
    assert ufo_payload["event_generation_ready"] is False


def test_manifest_exporter_and_readiness_checker_report_blockers(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest = run_tool("tools/export_bhsm_ufo_manifest.py", "--output", str(manifest_path))
    assert manifest.returncode == 0
    manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest_payload["ufo_export_ready"] is False
    assert manifest_payload["complete_4d_lagrangian_exported"] is False
    assert manifest_payload["blockers"]

    readiness = run_tool("tools/check_lhe_hepmc_generation_readiness.py")
    assert readiness.returncode == 0
    readiness_payload = json.loads(readiness.stdout)
    assert readiness_payload["event_generation_ready"] is False
    assert readiness_payload["lhe_generation_ready"] is False
    assert readiness_payload["hepmc_generation_ready"] is False
    assert readiness_payload["blockers"]


def test_madgraph_run_card_generator_writes_placeholder_warning(tmp_path: Path) -> None:
    output = tmp_path / "run_card.txt"
    result = run_tool("tools/generate_madgraph_run_card_template.py", "--output", str(output))
    assert result.returncode == 0
    text = output.read_text(encoding="utf-8")
    assert "BHSM UFO model is not yet exported." in text
    assert "This run card is a structural placeholder." in text
    assert "Do not use for physics analysis." in text

    committed = read("artifacts/madgraph_run_card_template_v0_1.txt")
    assert "BHSM UFO model is not yet exported." in committed
    assert "Do not use for physics analysis." in committed


def test_no_fake_event_files_or_official_integration_claims() -> None:
    event_suffixes = {".lhe", ".hepmc", ".hepmc3"}
    event_files = [
        path
        for path in ROOT.rglob("*")
        if path.is_file() and path.suffix.lower() in event_suffixes
    ]
    assert event_files == []

    combined = "\n".join(
        read(relative)
        for relative in [
            "README.md",
            "docs/ufo_pipeline.md",
            "docs/feynman_rules_status.md",
            "docs/madgraph_event_generation_path.md",
            "docs/lhe_hepmc_generation_status.md",
            "docs/athena_cmssw_integration_boundary.md",
        ]
    )
    forbidden_positive_claims = [
        "BHSM is empirically proven",
        "BHSM has experimentally replaced the Standard Model",
        "BHSM is validated by DESI",
        "Observed masses were used to derive constants",
        "External empirical comparison is complete",
        "Zenodo DOI assigned",
        "BHSM v1.0.1 provides Athena integration",
        "BHSM v1.0.1 provides CMSSW integration",
        "BHSM v1.0.1 provides LHE/HepMC event samples",
        "BHSM UFO model is exported",
        "MadGraph ready: true",
    ]
    for phrase in forbidden_positive_claims:
        assert phrase not in combined


def test_frozen_predictions_and_physics_source_remain_unchanged() -> None:
    for path, expected in FROZEN_HASHES.items():
        assert sha256(path) == expected

    for forbidden_source in [
        ROOT / "src" / "ufo_pipeline.py",
        ROOT / "src" / "feynman_rules.py",
        ROOT / "src" / "event_generation.py",
    ]:
        assert not forbidden_source.exists()
