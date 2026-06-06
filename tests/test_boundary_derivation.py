from claims import build_claims_ledger
from boundary_derivation import (
    DerivationStatus,
    action_link_report,
    boundary_equation,
    compare_to_operational_omega,
    coefficients_from_phase_contributions,
    default_boundaries,
    derive_boundary_coefficients,
    derive_omega_from_phases,
    explain_boundary,
    omega_from_boundary,
    phase_contributions_for_sector,
    target_from_phase_contributions,
)
from mode_selection import omega_down, omega_lepton, omega_up


def test_symbolic_boundary_equations_match_mode_selection_functions():
    boundaries = default_boundaries()
    samples = {
        "lepton": [(5, 2), (9, 3)],
        "up": [(6, 0), (10, 1)],
        "down": [(6, 3), (8, 2)],
    }
    functions = {
        "lepton": omega_lepton,
        "up": omega_up,
        "down": omega_down,
    }

    for sector, modes in samples.items():
        boundary = boundaries[sector]
        for mode in modes:
            assert omega_from_boundary(*mode, boundary) == functions[sector](*mode)


def test_coefficients_reproduce_required_omega_forms():
    boundaries = default_boundaries()

    assert derive_boundary_coefficients(boundaries["lepton"]) == {
        "sector": "lepton",
        "fiber_coefficient_on_q": -1,
        "base_coefficient_on_j": 2,
        "target": 3,
        "derivation_status": "ACTION_LINKED",
    }
    assert derive_boundary_coefficients(boundaries["up"])["fiber_coefficient_on_q"] == 1
    assert derive_boundary_coefficients(boundaries["up"])["base_coefficient_on_j"] == -2
    assert derive_boundary_coefficients(boundaries["down"])["fiber_coefficient_on_q"] == 1
    assert derive_boundary_coefficients(boundaries["down"])["base_coefficient_on_j"] == 4


def test_targets_are_generation_multiples():
    boundaries = default_boundaries()
    n_gen = 3

    assert boundaries["lepton"].target == n_gen
    assert boundaries["up"].target == 2 * n_gen
    assert boundaries["down"].target == 4 * n_gen


def test_boundaries_are_action_linked_not_action_derived():
    boundaries = default_boundaries()

    assert all(boundary.derivation_status == DerivationStatus.ACTION_LINKED for boundary in boundaries.values())
    assert all(boundary.derivation_status != DerivationStatus.ACTION_DERIVED for boundary in boundaries.values())


def test_comparison_reports_match_and_equations():
    for sector in ["lepton", "up", "down"]:
        report = compare_to_operational_omega(sector)

        assert report["matches_operational"] is True
        assert all(row["matches"] for row in report["comparisons"])
        assert f"Omega_{sector}" in report["equation"]


def test_explanations_name_remaining_derivation_gap():
    for boundary in default_boundaries().values():
        explanation = explain_boundary(boundary)

        assert "remaining open task" in explanation
        assert "twisted Dirac/bundle action" in explanation
        assert boundary_equation(boundary) in explanation


def test_claim_status_not_upgraded_by_boundary_scaffold():
    claims = {claim.id: claim for claim in build_claims_ledger()}

    assert claims["charged_sector_mode_ledger"].status.value == "VERIFIED_TEST"
    limitation = " ".join(claims["charged_sector_mode_ledger"].limitations)
    assert "ACTION_LINKED" in limitation
    assert "not fully ACTION_DERIVED" in limitation
    assert claims["forbidden_numerical_predictions"].status.value == "FORBIDDEN"


def test_phase_contributions_reproduce_expected_coefficients():
    expected = {
        "lepton": (-1, 2),
        "up": (1, -2),
        "down": (1, 4),
    }

    for sector, coefficients in expected.items():
        contribs = phase_contributions_for_sector(sector)
        assert coefficients_from_phase_contributions(contribs) == coefficients


def test_phase_targets_recover_family_winding_targets():
    expected = {"lepton": 3, "up": 6, "down": 12}

    for sector, target in expected.items():
        contribs = phase_contributions_for_sector(sector)
        assert target_from_phase_contributions(contribs) == target
        assert derive_omega_from_phases(sector).target == target


def test_action_link_report_contains_all_source_factors():
    required = {
        "hopf_fiber_phase",
        "base_node_phase",
        "chirality_sign",
        "weak_component_sign",
        "coframe_factor",
        "family_index",
        "hypercharge_factor",
        "sector_winding_multiplier",
    }

    for sector in ["lepton", "up", "down"]:
        report = action_link_report(sector)
        assert set(report["phase_contributions"]) == required
        assert report["derivation_status"] == "ACTION_LINKED"
        assert report["action_derived"] is False


def test_phase_derived_boundaries_match_default_boundaries():
    defaults = default_boundaries()

    for sector in ["lepton", "up", "down"]:
        linked = derive_omega_from_phases(sector)
        assert linked.fiber_weight == defaults[sector].fiber_weight
        assert linked.base_weight == defaults[sector].base_weight
        assert linked.target == defaults[sector].target
        assert linked.derivation_status != DerivationStatus.ACTION_DERIVED
