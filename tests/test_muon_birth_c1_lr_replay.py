"""Read-only imported-evidence and physical-guard checks, no physical solve."""
import importlib.util
from pathlib import Path
import shutil

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "c1_lr_replay", ROOT / "scripts/replay_muon_birth_c1_lr_response.py")
REPLAY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPLAY)


def test_import_preserves_exact_fraction_bounds_and_pinned_sources():
    packet = REPLAY.validated_companion_result(ROOT)
    assert packet["exact_control_groups_passed"] == 43
    assert packet["source_verification"]["pinned_source_files_verified"] == 43
    assert packet["source_verification"]["coefficient_inputs_match_exactly"] is True
    assert packet["physical_status"]["actual_LR_perturbation_norm_and_variation"] is None


def test_changed_import_is_rejected_before_its_controls_can_be_reused(tmp_path):
    original = ROOT / REPLAY.ARTIFACT / "companion"
    target = tmp_path / "companion"
    shutil.copytree(original, target)
    path = target / "response_carrier_bounds.py"
    path.write_bytes(path.read_bytes() + b"\n# changed exact coefficient source\n")
    with pytest.raises(ValueError, match="Imported companion changed"):
        REPLAY.verify_package_bytes(target)


def test_all_38_published_milestone_files_remain_unchanged():
    assert len(REPLAY.preserved_milestones(ROOT)) == 38


def test_complete_physical_packet_preserves_first_operand_and_nulls(tmp_path):
    import json
    result = REPLAY.materialize(tmp_path)
    packet = json.loads((tmp_path / "c1_lr_response.json").read_text())
    assert result["first_unavailable"] == dict(
        argument="parent_jet", operand="P_F", derivative_order=0, tuple_index=0)
    assert all(value is None for jet in packet["solver_inputs"].values() for value in jet)
    assert packet["consumed_parent_LR_response"]["value"] is None
    assert packet["consumed_parent_LR_response"]["exact_zero_proved"] is False
    assert packet["physical_status"]["physical_C1_underdetermination_proved"] is False
    assert packet["physical_status"]["point_KKT_callback_called"] is False
    assert packet["physical_status"]["complete_CAR_verdict"] is None
    assert packet["claims"]["OWNER_DEFINITION_GAP"] == []
