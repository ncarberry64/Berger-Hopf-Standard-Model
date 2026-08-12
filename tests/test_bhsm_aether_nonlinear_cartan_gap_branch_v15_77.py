from bhsm.interface.aether_nonlinear_cartan_gap_branch_v15_77 import (
    completion_payload,
    gap_branch_rows,
)


def test_gap_branch_turns_on_below_crossing() -> None:
    rows = gap_branch_rows()
    assert not rows[0]["broken"]
    assert not rows[1]["broken"]
    assert rows[2]["broken"]
    assert rows[2]["mass_times_R4"] > 0.0


def test_mass_and_yukawa_grow_on_broken_samples() -> None:
    broken = [row for row in gap_branch_rows() if row["broken"]]
    assert all(row["Yukawa_residue"] > 0.0 for row in broken)
    assert broken[-1]["mass_times_R4"] > broken[0]["mass_times_R4"]


def test_payload_validates() -> None:
    assert completion_payload()["validation_passed"]
