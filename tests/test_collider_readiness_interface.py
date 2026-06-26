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


def test_readme_preserves_status_and_declares_not_collider_ready() -> None:
    text = read("README.md")
    assert CURRENT_STATUS in text
    assert "Collider / CERN Software Readiness" in text
    assert "BHSM v1.0.1 is not an Athena, CMSSW, or detector-simulation-ready" in text
    assert "See `docs/collider_readiness.md`" in text


def test_required_collider_docs_exist_and_state_boundaries() -> None:
    required = [
        "docs/collider_readiness.md",
        "docs/lagrangian_status.md",
        "docs/pdg_validation_plan.md",
        "docs/event_generation_interface.md",
        "docs/athena_cmssw_integration_boundary.md",
    ]
    for relative in required:
        assert (ROOT / relative).exists(), relative

    lagrangian = read("docs/lagrangian_status.md")
    assert "No complete collider-ready 4D physical Lagrangian is exported" in lagrangian
    assert "boundary/operator-level no-fit artifacts" in lagrangian

    event_interface = read("docs/event_generation_interface.md")
    assert "does not currently provide a validated event generator" in event_interface
    assert "does not currently provide LHE/HepMC event samples" in event_interface
    assert "does not currently provide Athena or CMSSW integration" in event_interface


def test_collider_readiness_artifact_is_honest_about_missing_hep_interface() -> None:
    payload = load("artifacts/BHSM_collider_readiness_audit_v0_1.json")
    assert payload["bhsm_release_basis"] == "v1.0.1"
    assert payload["internal_boundary_package_status"] == "COMPLETE_EXPORTED"
    assert payload["external_empirical_comparison_status"] == "OPEN_SEPARATE_LAYER"
    assert payload["collider_ready"] is False
    assert payload["athena_ready"] is False
    assert payload["cmssw_ready"] is False
    assert payload["complete_4d_lagrangian_exported"] is False
    assert payload["feynman_rules_exported"] is False
    assert payload["ufo_model_exported"] is False
    assert payload["event_generator_ready"] is False
    assert payload["lhe_hepmc_output_supported"] is False
    assert payload["pdg_validation_plots_present"] is False
    assert payload["pdg_validation_requires_pinned_targets"] is True
    assert payload["empirical_derivation_inputs_used"] is False
    assert payload["boundary_predictions_modified_by_comparison"] is False
    assert payload["official_predictions_changed"] is False


def test_interface_artifacts_parse_and_do_not_claim_ready_outputs() -> None:
    lagrangian = load("artifacts/BHSM_lagrangian_status_v0_1.json")
    pdg = load("artifacts/BHSM_pdg_validation_schema_v0_1.json")
    events = load("artifacts/BHSM_event_generation_interface_v0_1.json")

    assert lagrangian["complete_4d_lagrangian_exported"] is False
    assert lagrangian["production_event_generator_model_exported"] is False
    assert pdg["schema_only"] is True
    assert pdg["contains_pdg_numeric_targets"] is False
    assert pdg["pdg_validation_requires_pinned_targets"] is True
    assert events["validated_event_generator_provided"] is False
    assert events["lhe_output_supported"] is False
    assert events["hepmc_output_supported"] is False
    assert events["athena_integration_provided"] is False
    assert events["cmssw_integration_provided"] is False


def test_pdg_template_contains_no_fake_numeric_validation_values() -> None:
    template = load("data/pdg_targets_template_v0_1.json")
    assert template["schema_only"] is True
    assert template["contains_pdg_numeric_targets"] is False
    assert template["target_rows"]
    for row in template["target_rows"]:
        assert row["pdg_value"] is None
        assert row["pdg_uncertainty"] is None
        assert row["bhsm_value"] is None
        assert row["comparison_status"] == "TEMPLATE_ONLY_NO_TARGET_DATA"


def test_plot_generator_exits_cleanly_without_real_target_data(tmp_path: Path) -> None:
    target = ROOT / "data" / "pdg_targets_template_v0_1.json"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "generate_pdg_validation_plots.py"),
            "--targets",
            str(target),
            "--output-dir",
            str(tmp_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0
    combined = result.stdout + result.stderr
    assert "No real numeric PDG target rows found" in combined
    assert "No fake validation plots generated" in combined
    assert not any(tmp_path.iterdir())


def test_no_fake_event_files_or_official_cern_claims_are_created() -> None:
    suffixes = {".lhe", ".hepmc", ".hepmc3"}
    event_files = [
        path
        for path in ROOT.rglob("*")
        if path.is_file() and path.suffix.lower() in suffixes
    ]
    assert event_files == []

    combined = "\n".join(
        read(relative)
        for relative in [
            "README.md",
            "docs/collider_readiness.md",
            "docs/athena_cmssw_integration_boundary.md",
            "docs/event_generation_interface.md",
        ]
    )
    forbidden_positive_claims = [
        "BHSM is empirically proven",
        "BHSM has experimentally replaced the Standard Model",
        "BHSM is validated by DESI",
        "Observed masses were used to derive constants",
        "External empirical comparison is complete",
        "Zenodo DOI assigned",
        "The repository is an official ATLAS",
        "The repository is an official CMS",
        "BHSM v1.0.1 provides Athena integration",
        "BHSM v1.0.1 provides CMSSW integration",
        "BHSM v1.0.1 provides LHE/HepMC event samples",
    ]
    for phrase in forbidden_positive_claims:
        assert phrase not in combined


def test_frozen_predictions_and_physics_source_remain_unchanged() -> None:
    for path, expected in FROZEN_HASHES.items():
        assert sha256(path) == expected

    changed_source_markers = [
        ROOT / "src" / "collider_readiness.py",
        ROOT / "src" / "event_generation_interface.py",
        ROOT / "src" / "pdg_validation.py",
    ]
    for path in changed_source_markers:
        assert not path.exists()
