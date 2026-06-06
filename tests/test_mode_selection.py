from math import isclose
from pathlib import Path

from berger_spectrum import berger_lambda, hopf_charge, ledger_modes
from mode_selection import (
    HEAVY_MODE,
    admissible_modes,
    boundary_penalty,
    is_admissible,
    mode_ledger,
    omega_down,
    omega_lepton,
    omega_up,
    selected_generation_modes,
    selection_report,
)
from yukawa_overlap import hierarchy_screen, mass_ratio


def test_berger_lambda_and_hopf_charge_for_supplied_modes():
    assert hopf_charge(5, 2) == 1
    assert berger_lambda(0, 0) == 0
    assert berger_lambda(5, 2) == 35
    assert berger_lambda(9, 3) == 99
    assert berger_lambda(6, 3) == 48


def test_boundary_operator_values_document_mode_separation():
    modes = ledger_modes()

    def omega_l(k, j):
        q = hopf_charge(k, j)
        return 2 * j - q

    def omega_u(k, j):
        q = hopf_charge(k, j)
        return q - 2 * j

    def omega_d(k, j):
        q = hopf_charge(k, j)
        return q + 4 * j

    assert omega_l(*modes["charged_leptons"]["middle"].__dict__.values()) == 3
    assert omega_u(*modes["up_quarks"]["middle"].__dict__.values()) == 6
    assert omega_d(*modes["down_quarks"]["middle"].__dict__.values()) == 12


def test_gate_25b_hopf_charges_for_expected_modes():
    assert hopf_charge(5, 2) == 1
    assert hopf_charge(9, 3) == 3
    assert hopf_charge(6, 0) == 6
    assert hopf_charge(10, 1) == 8
    assert hopf_charge(6, 3) == 0
    assert hopf_charge(8, 2) == 4


def test_gate_25b_boundary_operators_hit_targets():
    assert omega_lepton(5, 2) == 3
    assert omega_lepton(9, 3) == 3
    assert omega_up(6, 0) == 6
    assert omega_up(10, 1) == 6
    assert omega_down(6, 3) == 12
    assert omega_down(8, 2) == 12


def test_gate_25b_boundary_penalty_vanishes_on_expected_modes():
    assert boundary_penalty(5, 2, "lepton") == 0
    assert boundary_penalty(6, 0, "up") == 0
    assert boundary_penalty(6, 3, "down") == 0
    assert boundary_penalty(4, 1, "lepton") > 0


def test_gate_25b_sector_rules_and_selected_modes():
    assert is_admissible(5, 2, "lepton")
    assert is_admissible(10, 1, "up")
    assert is_admissible(8, 2, "down")
    assert not is_admissible(*HEAVY_MODE, "lepton")

    assert selected_generation_modes("lepton", k_max=12) == [(5, 2), (9, 3)]
    assert selected_generation_modes("up", k_max=12) == [(6, 0), (10, 1)]
    assert selected_generation_modes("down", k_max=12) == [(6, 3), (8, 2)]


def test_gate_25b_mode_ledger_includes_heavy_separately():
    ledger = mode_ledger(k_max=12)

    assert ledger["lepton"]["heavy"] == HEAVY_MODE
    assert ledger["lepton"]["selected"] == [(5, 2), (9, 3)]
    assert ledger["up"]["selected"] == [(6, 0), (10, 1)]
    assert ledger["down"]["selected"] == [(6, 3), (8, 2)]


def test_gate_25b_robustness_over_k_max_and_no_lower_action_competitors():
    for k_max in [10, 12, 20, 40]:
        report = selection_report(k_max)

        assert report["recovered_all"] is True
        for sector in ["lepton", "up", "down"]:
            sector_report = report["sectors"][sector]
            assert sector_report["recovered_expected"] is True
            assert sector_report["lower_action_competitors"] == []


def test_gate_25b_admissible_modes_are_action_sorted():
    modes = admissible_modes("down", k_max=20)
    actions = [berger_lambda(*mode) for mode in modes]

    assert actions == sorted(actions)
    assert modes[:2] == [(6, 3), (8, 2)]


def test_mode_selection_does_not_reference_empirical_data():
    source = Path(__file__).parents[1].joinpath("src", "mode_selection.py").read_text()
    forbidden_tokens = ["EMPIRICAL", "MASS", "mass", "hierarchy_screen", "EMPIRICAL_MASS_RATIOS"]

    assert all(token not in source for token in forbidden_tokens)


def test_yukawa_overlap_screen_outputs_hierarchy_ratios():
    assert isclose(mass_ratio(0, 0), 1.0)

    screen = hierarchy_screen()
    assert screen.status == "screened"
    assert screen.outputs["charged_leptons.heavy"] == 1.0
    assert screen.outputs["charged_leptons.middle"] > screen.outputs["charged_leptons.light"]
    assert screen.outputs["up_quarks.middle"] > screen.outputs["up_quarks.light"]
    assert screen.outputs["down_quarks.middle"] > screen.outputs["down_quarks.light"]
    assert screen.relative_error["charged_leptons.middle"] < 0.1
    assert screen.relative_error["down_quarks.middle"] < 0.1
