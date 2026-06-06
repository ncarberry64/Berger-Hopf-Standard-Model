from claims import build_claims_ledger
from constants import V_HIGGS_EMPIRICAL_GEV
from scalar_decoupling import (
    ScalarMode,
    build_scalar_proxy_spectrum,
    check_scalar_gap,
    classify_scalar_mode,
    coupling_suppression_factor,
    fifth_force_range,
    hopf_gap_mass,
    orthogonal_scalar_modes,
    scalar_decoupling_report,
)


def test_exactly_one_higgs_projection_passes():
    gap = hopf_gap_mass(V_HIGGS_EMPIRICAL_GEV)
    modes = build_scalar_proxy_spectrum(6, gap_scale=gap)
    report = scalar_decoupling_report(modes, gap)

    assert report["light_higgs_projection_count"] == 1
    assert report["exactly_one_light_higgs_projection"] is True
    assert report["passes"] is True


def test_heavy_orthogonal_modes_pass():
    gap = 100.0
    mode = ScalarMode("heavy", "orthogonal", 120.0, "heavy_orthogonal", 1.0, False)

    classification = classify_scalar_mode(mode, gap)
    assert classification["passes"] is True
    assert classification["status"] == "heavy_orthogonal"
    assert classification["conditional"] is False


def test_derivative_filtered_light_modes_are_conditional():
    mode = ScalarMode("d", "orthogonal", 1.0, "derivative_filtered", 0.2, False)
    classification = classify_scalar_mode(mode, gap=10.0)

    assert classification["passes"] is True
    assert classification["conditional"] is True
    assert classification["status"] == "conditional_derivative_filtered"


def test_curvature_filtered_light_modes_are_conditional():
    mode = ScalarMode("c", "orthogonal", 1.0, "curvature_filtered", 0.2, False)
    classification = classify_scalar_mode(mode, gap=10.0)

    assert classification["passes"] is True
    assert classification["conditional"] is True
    assert classification["status"] == "conditional_curvature_filtered"


def test_screened_light_modes_are_conditional():
    mode = ScalarMode("s", "orthogonal", 1.0, "screened", 0.2, False)
    classification = classify_scalar_mode(mode, gap=10.0)

    assert classification["passes"] is True
    assert classification["conditional"] is True
    assert classification["status"] == "conditional_screened"


def test_dangerous_light_direct_coupled_scalars_fail():
    gap = 100.0
    modes = [
        ScalarMode("h", "higgs", 10.0, "higgs_projection", 1.0, True),
        ScalarMode("bad", "orthogonal", 10.0, "dangerous_light", 1.0, False),
    ]
    report = check_scalar_gap(modes, gap)

    assert report["passes"] is False
    assert report["dangerous_light_modes"][0]["mode_id"] == "bad"


def test_fifth_force_range_decreases_as_mass_increases():
    assert fifth_force_range(1.0) > fifth_force_range(10.0) > fifth_force_range(100.0)


def test_orthogonal_modes_and_suppression_factor():
    modes = build_scalar_proxy_spectrum(4)
    orthogonal = orthogonal_scalar_modes(modes)
    factor = coupling_suppression_factor(orthogonal[0], suppression_scale=1000.0)

    assert len(orthogonal) == 3
    assert factor < orthogonal[0].coupling_strength


def test_claims_ledger_does_not_upgrade_scalar_decoupling_to_proven():
    claims = {claim.id: claim for claim in build_claims_ledger()}
    claim = claims["scalar_decoupling"]

    assert claim.status.value == "OPEN"
    assert "OPEN" in " ".join(claim.limitations) or "not proven" in " ".join(claim.limitations)
