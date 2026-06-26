import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PHASE_THREE_C_STATUS = (
    "BHSM v1.0.1 status-reconciled release: internal boundary no-fit package "
    "complete/exported; external empirical comparison layer separate/open"
)
PACKET_SHA = "8384772C492162326C215449201175792E663DFC7807A41CDDBC7E322126F4ED"
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


def sha256_lf_normalized(path: Path) -> str:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest().upper()


def run_tool(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_uploaded_working_packet_is_preserved_and_summarized() -> None:
    packet_path = ROOT / "artifacts" / "BHSM_phase_three_c_analytical_working_packet_v0_5.json"
    assert packet_path.exists()
    assert sha256_lf_normalized(packet_path) == PACKET_SHA

    packet = load("artifacts/BHSM_phase_three_c_analytical_working_packet_v0_5.json")
    summary = load("artifacts/BHSM_phase_three_c_source_summary_v0_5.json")
    assert packet["artifact_name"] == "BHSM Phase Three-C Analytical Working Packet"
    assert summary["source_packet_present"] is True
    assert summary["source_sha256"] == PACKET_SHA
    assert summary["field_dictionary_entries"] == 6
    assert summary["gauge_dictionary_entries"] == 3
    assert summary["vertex_source_targets"] == 5


def test_required_phase_three_c_docs_exist_and_preserve_status() -> None:
    for relative in [
        "docs/phase_three_c_field_dictionary.md",
        "docs/explicit_4d_field_dictionary.md",
        "docs/gauge_field_target_dictionary.md",
        "docs/bhsm_candidate_parameter_card.md",
        "docs/boundary_source_matrices.md",
        "docs/vertex_source_target_map.md",
        "docs/phase_three_c_gate_status.md",
    ]:
        assert (ROOT / relative).exists(), relative

    readme = " ".join(read("README.md").split())
    assert PHASE_THREE_C_STATUS in readme
    assert "Phase Three-C field dictionary status" in read("README.md")
    assert "This does not constitute production FeynRules/UFO readiness." in read("README.md")
    assert "8384772C492162326C215449201175792E663DFC7807A41CDDBC7E322126F4ED" in read(
        "docs/phase_three_c_field_dictionary.md"
    )


def test_required_phase_three_c_artifacts_exist_and_parse() -> None:
    artifacts = [
        "artifacts/BHSM_explicit_4d_field_dictionary_v0_5.json",
        "artifacts/BHSM_gauge_field_target_dictionary_v0_5.json",
        "artifacts/BHSM_candidate_parameter_card_v0_5.json",
        "artifacts/BHSM_boundary_source_matrices_v0_5.json",
        "artifacts/BHSM_vertex_source_target_map_v0_5.json",
        "artifacts/BHSM_phase_three_c_gate_status_v0_5.json",
        "artifacts/BHSM_phase_three_c_source_summary_v0_5.json",
    ]
    for relative in artifacts:
        payload = load(relative)
        assert isinstance(payload, dict), relative
        assert payload["empirical_derivation_inputs_used"] is False
        assert payload["boundary_predictions_modified_by_comparison"] is False
        assert payload["official_predictions_changed"] is False
        assert payload["source_model_files_changed"] is False


def test_explicit_field_dictionary_is_candidate_and_not_ufo_ready() -> None:
    payload = load("artifacts/BHSM_explicit_4d_field_dictionary_v0_5.json")
    assert payload["field_dictionary_target_exported"] is True
    assert payload["production_ufo_ready"] is False
    ids = {entry["field_entry_id"] for entry in payload["entries"]}
    assert {
        "bhsm_profile_scalar_H",
        "bhsm_lepton_left_doublet",
        "bhsm_charged_lepton_right",
        "bhsm_quark_left_doublet",
        "bhsm_up_quark_right",
        "bhsm_down_quark_right",
    }.issubset(ids)
    for entry in payload["entries"]:
        assert entry["production_status"] == "NOT_UFO_READY"
        assert entry["ufo_ready"] is False
        assert entry["source_artifacts"]
        assert entry["missing"]

    scalar = next(entry for entry in payload["entries"] if entry["field_entry_id"] == "bhsm_profile_scalar_H")
    assert (
        scalar["warning"]
        == "kappa_H is a BHSM profile Hessian curvature, not automatically the observed Higgs mass."
    )


def test_gauge_dictionary_uses_target_conventions_not_completed_theorem() -> None:
    payload = load("artifacts/BHSM_gauge_field_target_dictionary_v0_5.json")
    assert payload["gauge_field_target_dictionary_exported"] is True
    assert payload["completed_bhsm_gauge_theorem"] is False
    ids = {entry["field_entry_id"] for entry in payload["entries"]}
    assert {"gauge_gluon_target", "gauge_weak_target", "gauge_hypercharge_target"}.issubset(ids)
    for entry in payload["entries"]:
        assert entry["status"] == "STANDARD_HEP_TARGET_WITH_BHSM_COUPLING_CANDIDATE"
        assert entry["production_status"] == "BLOCKED"
        assert entry["ufo_ready"] is False
        assert entry["missing"]


def test_candidate_parameter_card_has_no_pdg_validation_or_ufo_ready_entries() -> None:
    payload = load("artifacts/BHSM_candidate_parameter_card_v0_5.json")
    assert payload["BHSM_internal_parameter_card_candidate_exported"] is True
    assert payload["production_parameter_card_ready"] is False
    assert payload["pdg_validation_claimed"] is False
    parameters = {entry["parameter"]: entry for entry in payload["entries"]}
    for expected in [
        "tau_BH",
        "sigma_BH",
        "kappa_H_BH",
        "rho_ch_BH",
        "g_bridge_BH",
        "delta_BH",
        "g1_BH_candidate",
        "g2_BH_candidate",
        "g3_BH_candidate",
    ]:
        assert expected in parameters
        assert parameters[expected]["ufo_ready"] is False

    for expected in ["g1_BH_candidate", "g2_BH_candidate", "g3_BH_candidate"]:
        assert parameters[expected]["status"] == "SCHEME_CONDITIONAL"


def test_boundary_source_matrices_are_not_collider_vertices() -> None:
    payload = load("artifacts/BHSM_boundary_source_matrices_v0_5.json")
    assert payload["boundary_source_vertex_matrices_exported"] is True
    assert payload["not_collider_vertices"] is True
    assert payload["ufo_ready"] is False
    matrices = {entry["matrix_id"]: entry for entry in payload["matrices"]}
    assert matrices["C_ch_boundary"]["exact"] == [
        "4/(1323*pi^(3/2))",
        "8/(1323*pi^(3/2))",
        "16/(1323*pi^(3/2))",
    ]
    assert matrices["C_ch_boundary"]["approx_diagonal"] == [
        0.00054296937906324,
        0.00108593875812648,
        0.00217187751625296,
    ]
    assert matrices["K_ch_boundary"]["exact"] == [
        "4/(1323*pi^(3/2))",
        "4/(1323*pi^(3/2))",
        "4/(3591*pi^(3/2))",
    ]
    assert matrices["K_ch_boundary"]["approx_diagonal"] == [
        0.00054296937906324,
        0.00054296937906324,
        0.000200041350181194,
    ]
    assert matrices["K_nu_boundary"]["matrix"] == [
        [0, "1/3", 0],
        ["1/3", 3, "1/6"],
        [0, "1/6", "5/3"],
    ]
    assert all(entry["ufo_ready"] is False for entry in matrices.values())


def test_vertex_source_targets_are_not_feynrules_ready() -> None:
    payload = load("artifacts/BHSM_vertex_source_target_map_v0_5.json")
    assert payload["standard_collider_vertex_targets_identified"] is True
    assert payload["feynrules_ready"] is False
    assert payload["ufo_ready"] is False
    ids = {entry["vertex_family_id"] for entry in payload["targets"]}
    assert {
        "q_charged_current_CKM_BH",
        "lepton_charged_current_PMNS_BH",
        "charged_boundary_response_matrix",
        "neutral_operator_kernel_BH",
        "cp_holonomy_phase_attachment",
    }.issubset(ids)
    for entry in payload["targets"]:
        assert entry["feynrules_ready"] is False
        assert entry["ufo_ready"] is False
        assert entry["missing"]


def test_phase_three_c_gate_status_keeps_readiness_false() -> None:
    payload = load("artifacts/BHSM_phase_three_c_gate_status_v0_5.json")
    assert payload["field_dictionary_target_exported"] is True
    assert payload["BHSM_internal_parameter_card_candidate_exported"] is True
    assert payload["boundary_source_vertex_matrices_exported"] is True
    assert payload["standard_collider_vertex_targets_identified"] is True
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
        assert payload[key] is False
    assert "vector and fermion normalizations" in payload["remaining_blockers"]
    assert "mass-width scheme" in payload["remaining_blockers"]
    assert "renormalization scheme" in payload["remaining_blockers"]


def test_phase_three_c_tools_export_to_temporary_outputs(tmp_path: Path) -> None:
    commands = [
        ("tools/import_phase_three_c_working_packet.py", "--output", str(tmp_path / "summary.json")),
        ("tools/export_explicit_4d_field_dictionary.py", "--output", str(tmp_path / "fields.json")),
        ("tools/export_gauge_field_target_dictionary.py", "--output", str(tmp_path / "gauge.json")),
        ("tools/export_candidate_parameter_card_v0_5.py", "--output", str(tmp_path / "params.json")),
        ("tools/export_boundary_source_matrices_v0_5.py", "--output", str(tmp_path / "matrices.json")),
        ("tools/export_vertex_source_target_map_v0_5.py", "--output", str(tmp_path / "vertices.json")),
        ("tools/check_phase_three_c_gate_status.py", "--output", str(tmp_path / "gate.json")),
    ]
    for command in commands:
        result = run_tool(*command)
        assert result.returncode == 0, result.stderr

    assert json.loads((tmp_path / "fields.json").read_text(encoding="utf-8"))["production_ufo_ready"] is False
    assert json.loads((tmp_path / "gauge.json").read_text(encoding="utf-8"))["completed_bhsm_gauge_theorem"] is False
    assert json.loads((tmp_path / "params.json").read_text(encoding="utf-8"))["pdg_validation_claimed"] is False
    assert json.loads((tmp_path / "matrices.json").read_text(encoding="utf-8"))["not_collider_vertices"] is True
    assert json.loads((tmp_path / "vertices.json").read_text(encoding="utf-8"))["feynrules_ready"] is False
    assert json.loads((tmp_path / "gate.json").read_text(encoding="utf-8"))["ufo_ready"] is False


def test_no_fake_event_files_or_forbidden_claims() -> None:
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
            "docs/phase_three_c_field_dictionary.md",
            "docs/explicit_4d_field_dictionary.md",
            "docs/gauge_field_target_dictionary.md",
            "docs/bhsm_candidate_parameter_card.md",
            "docs/boundary_source_matrices.md",
            "docs/vertex_source_target_map.md",
            "docs/phase_three_c_gate_status.md",
        ]
    ).lower()
    for phrase in [
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
        "zenodo doi assigned",
        "is production feynrules/ufo ready",
        "production feynrules/ufo ready = true",
    ]:
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
