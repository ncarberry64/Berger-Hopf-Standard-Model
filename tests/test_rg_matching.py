from math import isclose, pi

from claims import build_claims_ledger
from rg_matching import (
    ELECTROWEAK_WINDOW_GEV,
    MZ,
    default_reference_values,
    geometric_matching_values,
    matching_report,
    run_alpha_inverse_one_loop,
    run_couplings_one_loop,
    solve_matching_scale_one_loop,
    threshold_placeholder,
    two_loop_placeholder,
)


def test_one_loop_running_preserves_input_at_reference_scale():
    refs = default_reference_values()
    assert run_alpha_inverse_one_loop(1.0 / refs["alpha1"], 41 / 10, MZ, MZ) == 1.0 / refs["alpha1"]
    run = run_couplings_one_loop(refs, MZ, MZ)
    assert all(isclose(run[name], refs[name]) for name in refs)


def test_geometric_matching_values_are_supplied_values():
    values = geometric_matching_values()

    assert isclose(values["alpha1"], 1 / (6 * pi**2))
    assert isclose(values["alpha2"], 1 / (3 * pi**2))
    assert isclose(values["alpha3"], 7 / (6 * pi**2))


def test_solved_matching_scales_are_finite_positive():
    refs = default_reference_values()
    geom = geometric_matching_values()

    for name, b in {"alpha1": 41 / 10, "alpha2": -19 / 6, "alpha3": -7}.items():
        scale = solve_matching_scale_one_loop(refs[name], geom[name], b, MZ)
        assert scale > 0
        assert scale < 1.0e6


def test_default_matching_scales_are_in_electroweak_window():
    report = matching_report()
    low, high = ELECTROWEAK_WINDOW_GEV

    for row in report["rows"].values():
        assert low <= row["matching_scale_gev"] <= high
        assert row["in_electroweak_window"] is True


def test_placeholders_are_explicitly_incomplete():
    threshold = threshold_placeholder("heavy", scale=100.0)
    two_loop = two_loop_placeholder("sm")

    assert threshold["status"] == "PLACEHOLDER_OPEN"
    assert threshold["complete"] is False
    assert "not implemented" in threshold["limitation"]
    assert two_loop["status"] == "PLACEHOLDER_OPEN"
    assert two_loop["complete"] is False
    assert "not implemented" in two_loop["limitation"]


def test_claims_ledger_does_not_upgrade_rg_matching_to_completed_theorem():
    claims = {claim.id: claim for claim in build_claims_ledger()}
    claim = claims["gauge_coupling_screen"]

    assert claim.status.value == "STRONG_SCREEN"
    assert "not a completed" in " ".join(claim.limitations)
