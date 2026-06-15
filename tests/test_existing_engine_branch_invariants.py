from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_existing_engine_branch_threshold import branch_assignments, build_payload  # noqa: E402


def test_expected_branch_roles_are_identified() -> None:
    rows = {(row.sector, row.generation_label): row for row in branch_assignments()}
    assert rows[("charged_lepton", "mu/tau")].branch_role == "lower_nonzero_action, mixed"
    assert rows[("charged_lepton", "e/tau")].branch_role == "higher_nonzero_action, mixed"
    assert rows[("up", "c/t")].branch_role == "lower_nonzero_action, pure_fiber"
    assert rows[("up", "u/t")].branch_role == "higher_nonzero_action, mixed"
    assert rows[("down", "s/b")].branch_role == "lower_nonzero_action, pure_base"
    assert rows[("down", "d/b")].branch_role == "higher_nonzero_action, mixed"


def test_pure_fiber_and_pure_base_specialness_are_reported() -> None:
    rows = {(row.sector, row.generation_label): row for row in branch_assignments()}
    assert rows[("up", "c/t")].pure_fiber_flag is True
    assert rows[("down", "s/b")].pure_base_flag is True
    assert rows[("up", "u/t")].mixed_flag is True
    assert rows[("down", "d/b")].mixed_flag is True

    labels = set(build_payload(ROOT)["verdict_labels"])
    assert "PURE_FIBER_BRANCH_SPECIALNESS_INDICATED" in labels
    assert "PURE_BASE_BRANCH_SPECIALNESS_INDICATED" in labels


def test_rank_order_checks_separate_middle_and_light_modes() -> None:
    checks = build_payload(ROOT)["invariant_diagnostics"]["rank_order_checks"]
    branch_rank_checks = [row for row in checks if row["variable"] == "branch_rank_by_N"]
    assert len(branch_rank_checks) == 3
    assert all(row["separates_middle_light"] is True for row in branch_rank_checks)
    assert all(row["diagnostic_only_small_sample"] is True for row in branch_rank_checks)
