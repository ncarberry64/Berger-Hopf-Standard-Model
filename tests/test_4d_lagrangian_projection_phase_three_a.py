import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PHASE_TWO_A_STATUS = (
    "BHSM v1.0.1 status-reconciled release: internal boundary no-fit package "
    "complete/exported; external empirical comparison layer separate/open"
)
FROZEN_HASHES = {
    ROOT / "docs" / "frozen_predictions.md": (
        "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4"
    ),
    ROOT / "docs" / "frozen_predictions.json": (
        "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7"
    ),
}
ALLOWED_TERM_STATUSES = {
    "DERIVED_FROM_REPO_ARTIFACT",
    "DERIVED_CONDITIONAL_FROM_AUTHOR_AXIOM",
    "STRUCTURAL_CANDIDATE",
    "SYMBOLIC_PLACEHOLDER",
    "BLOCKED_BY_MISSING_4D_PROJECTION_THEOREM",
    "BLOCKED_BY_MISSING_FIELD_NORMALIZATION",
    "BLOCKED_BY_MISSING_VERTEX_NORMALIZATION",
    "BLOCKED_BY_MISSING_GAUGE_FIXING",
    "BLOCKED_BY_MISSING_RENORMALIZATION_SCHEME",
    "NOT_FOR_UFO_EXPORT",
}


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def load(relative: str) -> dict:
    return json.loads(read(relative))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def run_tool(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_readme_preserves_status_and_phase_three_boundaries() -> None:
    text = " ".join(read("docs/archive/README_status_history_pre_v0_7.md").split())
    assert PHASE_TWO_A_STATUS in text
    assert "Phase Three-A attempts an analytical projection" in text
    assert "This is not production UFO readiness" in text
    assert "No MadGraph, LHE, HepMC, Athena, or CMSSW readiness is claimed." in text


def test_required_phase_three_docs_exist_and_state_blockers() -> None:
    required = [
        "docs/4d_lagrangian_projection.md",
        "docs/effective_lagrangian_candidate.md",
        "docs/field_normalization_ledger.md",
        "docs/vertex_normalization_ledger.md",
        "docs/mass_width_scheme_status.md",
        "docs/renormalization_scheme_status.md",
        "docs/feynrules_translation_gate.md",
        "docs/ufo_phase_three_blocker_resolution.md",
    ]
    for relative in required:
        assert (ROOT / relative).exists(), relative

    projection = read("docs/4d_lagrangian_projection.md")
    assert "A candidate ledger is not the same thing as a production collider Lagrangian." in projection
    assert "feynrules_ready = false" in read("docs/feynrules_translation_gate.md")
    assert "No fake vertices or Feynman rules are created." in read("docs/vertex_normalization_ledger.md")


def test_phase_three_artifacts_exist_and_parse() -> None:
    artifacts = [
        "artifacts/BHSM_4d_lagrangian_projection_audit_v0_3.json",
        "artifacts/BHSM_effective_lagrangian_candidate_v0_3.json",
        "artifacts/BHSM_field_normalization_ledger_v0_3.json",
        "artifacts/BHSM_vertex_normalization_ledger_v0_3.json",
        "artifacts/BHSM_mass_width_scheme_status_v0_3.json",
        "artifacts/BHSM_renormalization_scheme_status_v0_3.json",
        "artifacts/BHSM_feynrules_translation_gate_v0_3.json",
        "artifacts/BHSM_ufo_phase_three_readiness_v0_3.json",
    ]
    for relative in artifacts:
        payload = load(relative)
        assert isinstance(payload, dict), relative
        assert payload["empirical_derivation_inputs_used"] is False
        assert payload["boundary_predictions_modified_by_comparison"] is False
        assert payload["official_predictions_changed"] is False
        assert payload["source_model_files_changed"] is False


def test_effective_lagrangian_candidate_terms_are_blocked_ledgers() -> None:
    payload = load("artifacts/BHSM_effective_lagrangian_candidate_v0_3.json")
    assert payload["complete_4d_collider_ready_lagrangian_exported"] is False
    assert payload["production_feynrules_ready"] is False
    assert payload["production_ufo_ready"] is False

    expected_terms = {
        "profile_scale_term",
        "charged_boundary_response_term",
        "neutral_operator_term",
        "ckm_mixing_term",
        "pmns_mixing_term",
        "cp_holonomy_term",
        "boundary_transport_term",
    }
    term_ids = {entry["term_id"] for entry in payload["terms"]}
    assert expected_terms.issubset(term_ids)
    for entry in payload["terms"]:
        assert entry["derivation_status"] in ALLOWED_TERM_STATUSES
        assert entry["ufo_export_status"] == "BLOCKED"
        assert entry["source_artifacts"]
        assert entry["candidate_density_expression"]
        assert entry["missing_for_production_lagrangian"]
        assert entry["missing_for_feynrules"]
        assert entry["missing_for_ufo"]
        assert "production FeynRules model" in entry["missing_for_ufo"]


def test_field_and_vertex_normalization_ledgers_are_not_complete() -> None:
    fields = load("artifacts/BHSM_field_normalization_ledger_v0_3.json")
    vertices = load("artifacts/BHSM_vertex_normalization_ledger_v0_3.json")

    assert fields["field_normalization_complete"] is False
    assert fields["canonical_kinetic_terms_complete"] is False
    assert vertices["vertex_normalization_complete"] is False
    assert vertices["complete_vertex_table_present"] is False

    for entry in fields["entries"]:
        assert entry["normalization_status"] == "BLOCKED_BY_MISSING_FIELD_NORMALIZATION"
        assert entry["normalization_value"] is None
        assert entry["canonical_kinetic_term_ready"] is False
        assert entry["mass_term_ready"] is False
        assert entry["width_term_ready"] is False
        assert entry["gauge_representation_ready"] is False

    for entry in vertices["entries"]:
        assert entry["feynrules_ready"] is False
        assert entry["ufo_ready"] is False
        assert entry["normalization_status"] == "BLOCKED_BY_MISSING_VERTEX_NORMALIZATION"
        assert entry["lorentz_structure_status"] == "BLOCKED_BY_MISSING_4D_PROJECTION_THEOREM"
        assert entry["gauge_structure_status"] == "BLOCKED_BY_MISSING_GAUGE_FIXING"


def test_mass_width_and_renormalization_schemes_are_absent_not_fabricated() -> None:
    mass_width = load("artifacts/BHSM_mass_width_scheme_status_v0_3.json")
    renorm = load("artifacts/BHSM_renormalization_scheme_status_v0_3.json")

    assert mass_width["mass_width_scheme_complete"] is False
    assert renorm["renormalization_scheme_complete"] is False
    assert renorm["feynrules_ready"] is False
    assert renorm["ufo_ready"] is False
    assert renorm["renormalization_scheme_name"] is None

    for key in [
        "pole_mass_scheme",
        "running_mass_scheme",
        "decay_width_scheme",
        "gauge_boson_width_scheme",
        "fermion_width_scheme",
        "higgs_width_scheme",
        "neutrino_mass_scheme",
    ]:
        assert mass_width[key]["provided"] is False

    for key in [
        "gauge_coupling_scheme",
        "yukawa_scheme",
        "threshold_scheme",
        "counterterm_scheme",
        "running_scheme",
    ]:
        assert renorm[key]["provided"] is False


def test_feynrules_and_phase_three_ufo_readiness_gates_stay_closed() -> None:
    projection = load("artifacts/BHSM_4d_lagrangian_projection_audit_v0_3.json")
    gate = load("artifacts/BHSM_feynrules_translation_gate_v0_3.json")
    readiness = load("artifacts/BHSM_ufo_phase_three_readiness_v0_3.json")

    for key in [
        "complete_4d_lagrangian_exported",
        "feynrules_ready",
        "ufo_ready",
        "madgraph_ready",
        "lhe_generation_ready",
        "hepmc_generation_ready",
        "athena_ready",
        "cmssw_ready",
    ]:
        assert projection[key] is False

    for key in [
        "complete_4d_lagrangian_exported",
        "field_normalization_complete",
        "vertex_normalization_complete",
        "mass_width_scheme_complete",
        "renormalization_scheme_complete",
        "gauge_fixing_complete",
        "complete_vertex_table_present",
        "production_parameter_card_present",
    ]:
        assert gate[key] is False
        assert key in gate["blockers"]

    assert gate["feynrules_ready"] is False
    assert gate["ufo_ready"] is False
    assert readiness["effective_lagrangian_candidate_exported"] is True
    assert readiness["field_normalization_ledger_exported"] is True
    assert readiness["vertex_normalization_ledger_exported"] is True
    assert readiness["production_ufo_model_exported"] is False
    assert readiness["loadable_ufo_model"] is False
    assert readiness["remaining_blockers"]


def test_phase_three_tools_export_consistent_temporary_artifacts(tmp_path: Path) -> None:
    outputs = {
        "lagrangian": tmp_path / "candidate.json",
        "fields": tmp_path / "fields.json",
        "vertices": tmp_path / "vertices.json",
        "gate": tmp_path / "gate.json",
        "readiness": tmp_path / "readiness.json",
    }
    commands = [
        ("tools/export_bhsm_effective_lagrangian_candidate.py", "--output", str(outputs["lagrangian"])),
        ("tools/export_bhsm_field_normalization_ledger.py", "--output", str(outputs["fields"])),
        ("tools/export_bhsm_vertex_normalization_ledger.py", "--output", str(outputs["vertices"])),
        ("tools/check_bhsm_feynrules_translation_gate.py", "--output", str(outputs["gate"])),
        ("tools/check_bhsm_phase_three_ufo_readiness.py", "--output", str(outputs["readiness"])),
    ]
    for command in commands:
        result = run_tool(*command)
        assert result.returncode == 0, result.stderr

    assert json.loads(outputs["lagrangian"].read_text(encoding="utf-8"))["production_ufo_ready"] is False
    assert json.loads(outputs["fields"].read_text(encoding="utf-8"))["field_normalization_complete"] is False
    assert json.loads(outputs["vertices"].read_text(encoding="utf-8"))["vertex_normalization_complete"] is False
    assert json.loads(outputs["gate"].read_text(encoding="utf-8"))["feynrules_ready"] is False
    assert json.loads(outputs["readiness"].read_text(encoding="utf-8"))["production_ufo_model_exported"] is False


def test_no_fake_event_files_or_readiness_claims_exist() -> None:
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
            "docs/archive/README_status_history_pre_v0_7.md",
            "docs/4d_lagrangian_projection.md",
            "docs/effective_lagrangian_candidate.md",
            "docs/field_normalization_ledger.md",
            "docs/vertex_normalization_ledger.md",
            "docs/mass_width_scheme_status.md",
            "docs/renormalization_scheme_status.md",
            "docs/feynrules_translation_gate.md",
            "docs/ufo_phase_three_blocker_resolution.md",
            "docs/ufo_pipeline.md",
            "docs/feynman_rules_status.md",
        ]
    ).lower()
    forbidden_positive_claims = [
        "feynrules_ready = true",
        "ufo_ready = true",
        "madgraph_ready = true",
        "lhe_generation_ready = true",
        "hepmc_generation_ready = true",
        "athena_ready = true",
        "cmssw_ready = true",
        "official cern integration",
        "bhsm is empirically validated",
        "bhsm is empirically proven",
        "production ufo model exported",
        "complete 4d collider-ready lagrangian exported",
    ]
    for phrase in forbidden_positive_claims:
        assert phrase not in combined


def test_frozen_predictions_and_physics_source_remain_unchanged() -> None:
    for path, expected in FROZEN_HASHES.items():
        assert sha256(path) == expected

    tracked_src = subprocess.run(
        ["git", "diff", "--name-only", "HEAD", "--", "src"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert tracked_src.returncode == 0
    assert tracked_src.stdout.strip() == ""

    untracked_src = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "src"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert untracked_src.returncode == 0
    assert untracked_src.stdout.strip() == ""
