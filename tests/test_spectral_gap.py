from math import exp, isclose, pi

import pytest

from spectral_gap import (
    MU_H,
    UNIVERSAL_WIDTH,
    alpha_scaled_a,
    candidate_mode_grid,
    curvature_profile_term,
    default_protected_modes,
    dimensionless_gap_target,
    dimensionless_hopf_gap,
    gap_margin,
    heat_lift,
    hopf_gap_mass,
    net_v_min_over_modes,
    natural_lambda2,
    passes_heat_lift_bound,
    positive_barrier,
    profile_well,
    proxy_ht_eigenvalues,
    required_lambda2,
    scan_gap_robustness,
    scan_proxy_spectrum,
    scan_with_profile_terms,
    spectral_gap_screen,
)


def test_mu_h_is_supplied_dimensionless_hopf_gap():
    assert isclose(MU_H, 64 * pi**5)
    assert isclose(dimensionless_hopf_gap(), 64 * pi**5)
    assert isclose(dimensionless_gap_target(), 64 * pi**5)


def test_natural_lambda2_is_universal_overlap_width():
    assert isclose(UNIVERSAL_WIDTH, 1 / (4 * pi))
    assert isclose(natural_lambda2(), 1 / (4 * pi))


def test_hopf_gap_mass_formula():
    assert isclose(hopf_gap_mass(246.0), 4 * pi**2 * 246.0)


def test_heat_lift_is_zero_at_zero_mode():
    assert heat_lift(0.0, lambda2=1.0) == 0.0


def test_heat_lift_approaches_d_plus_mu_h_for_large_d_over_lambda2():
    d = 10.0
    lambda2 = 1.0e-6

    assert isclose(heat_lift(d, lambda2), d + MU_H, rel_tol=1e-12)
    assert isclose(heat_lift(d, lambda2), d + MU_H * (1 - exp(-d / lambda2)))


def test_lifted_proxy_spectrum_is_sorted_by_unlifted_eigenvalue():
    scan = scan_proxy_spectrum(a=1.0, n_max=6, lambda2=0.1)
    unlifted = [row["d"] for row in scan]

    assert unlifted == sorted(unlifted)
    assert scan[0]["d"] == 3.0
    assert scan[0]["k"] == 1


def test_first_nonzero_proxy_mode_passes_or_fails_for_explicit_lambda2():
    first_d = scan_proxy_spectrum(a=1.0, n_max=2, lambda2=0.1)[0]["d"]
    threshold = required_lambda2(first_d)

    assert first_d == 3.0
    assert passes_heat_lift_bound(first_d, lambda2=threshold / 10)
    assert not passes_heat_lift_bound(first_d, lambda2=threshold * 10)


def test_first_nonzero_mode_passes_with_natural_lambda2():
    first = scan_proxy_spectrum(a=1.0, n_max=20)[0]

    assert first["d"] == 3.0
    assert first["lambda2"] == natural_lambda2()
    assert passes_heat_lift_bound(first["d"])


def test_no_silent_tuning_of_lambda2():
    requested_lambda2 = 10.0
    scan = scan_proxy_spectrum(a=1.0, n_max=4, lambda2=requested_lambda2)

    assert {row["lambda2"] for row in scan} == {requested_lambda2}
    assert not scan[0]["passes"]
    with pytest.raises(ValueError):
        scan_proxy_spectrum(a=1.0, n_max=4, lambda2=0.0)
    with pytest.raises(ValueError):
        heat_lift(1.0, lambda2=0.0)


def test_negative_v_min_weakens_gap_condition():
    first = scan_proxy_spectrum(a=1.0, n_max=20)[0]
    baseline = gap_margin(first["d"])
    weakened = gap_margin(first["d"], v_min=-0.01 * MU_H)

    assert weakened < baseline
    assert isclose(baseline - weakened, 0.01 * MU_H)


def test_robustness_scan_reports_explicit_pass_fail_and_fixed_lambda2():
    requested_lambda2 = natural_lambda2()
    rows = scan_gap_robustness(
        a_values=[0.573, 1.0, alpha_scaled_a()],
        n_max_values=[10, 20, 40],
        lambda2=requested_lambda2,
        v_min_values=[0.0, -0.01 * MU_H],
    )

    assert len(rows) == 18
    assert {row["lambda2"] for row in rows} == {requested_lambda2}
    assert {type(row["passes"]) for row in rows} == {bool}
    assert any(row["passes"] for row in rows)
    assert any(not row["passes"] for row in rows)


def test_robustness_scan_uses_natural_lambda2_by_default():
    rows = scan_gap_robustness(
        a_values=[1.0],
        n_max_values=[20],
        v_min_values=[0.0],
    )

    assert rows[0]["lambda2"] == natural_lambda2()
    assert rows[0]["passes"] is True


def test_zero_profile_reproduces_gate_28b_margin():
    profile_rows = scan_with_profile_terms(
        a_values=[1.0],
        n_max_values=[20],
        profile_models=["zero"],
    )
    robustness_rows = scan_gap_robustness(
        a_values=[1.0],
        n_max_values=[20],
        v_min_values=[0.0],
    )

    assert profile_rows[0]["passes"] == robustness_rows[0]["passes"]
    assert isclose(profile_rows[0]["margin"], robustness_rows[0]["margin"])
    assert curvature_profile_term(1, 0, model="zero") == 0.0


def test_positive_barrier_never_weakens_gap():
    rows = scan_with_profile_terms(
        a_values=[1.0],
        n_max_values=[20],
        profile_models=[
            "zero",
            {
                "name": "barrier",
                "model": "positive_barrier",
                "params": {"strength": 2.0, "power": 1.0},
            },
        ],
    )
    zero = next(row for row in rows if row["model"] == "zero")
    barrier = next(row for row in rows if row["model"] == "positive_barrier")

    assert positive_barrier(1, 0, strength=2.0) >= 0.0
    assert barrier["margin"] >= zero["margin"]
    assert barrier["passes"] is True


def test_bounded_negative_fails_when_depth_is_large_enough():
    rows = scan_with_profile_terms(
        a_values=[1.0],
        n_max_values=[20],
        profile_models=[
            {"name": "negative", "model": "bounded_negative", "params": {"depth": 0.01}},
        ],
    )

    assert curvature_profile_term(1, 0, model="bounded_negative", depth=0.01) == -0.01 * MU_H
    assert rows[0]["passes"] is False
    assert rows[0]["margin"] < 0.0


def test_compensated_profile_restores_gap_when_first_mode_net_is_nonnegative():
    first_mode = (1, 0)
    well = profile_well(*first_mode, depth=0.01, width=1.0)
    exact_strength = -well / positive_barrier(*first_mode, strength=1.0, power=1.0)
    rows = scan_with_profile_terms(
        a_values=[1.0],
        n_max_values=[20],
        profile_models=[
            {
                "name": "under_compensated",
                "model": "compensated",
                "params": {"depth": 0.01, "width": 1.0, "strength": 0.0, "power": 1.0},
            },
            {
                "name": "compensated",
                "model": "compensated",
                "params": {
                    "depth": 0.01,
                    "width": 1.0,
                    "strength": exact_strength,
                    "power": 1.0,
                },
            },
        ],
    )
    under = next(row for row in rows if row["model_name"] == "under_compensated")
    compensated = next(row for row in rows if row["model_name"] == "compensated")
    net_first = curvature_profile_term(
        *first_mode,
        model="compensated",
        depth=0.01,
        width=1.0,
        strength=exact_strength,
        power=1.0,
    )

    assert under["passes"] is False
    assert isclose(net_first, 0.0, abs_tol=1e-12)
    assert compensated["passes"] is True


def test_profile_scan_reports_explicit_pass_fail_and_net_v_min():
    rows = scan_with_profile_terms(
        a_values=[1.0],
        n_max_values=[10],
        profile_models=["zero", {"name": "negative", "model": "bounded_negative", "params": {"depth": 0.01}}],
    )

    assert {type(row["passes"]) for row in rows} == {bool}
    assert all(row["lambda2"] == natural_lambda2() for row in rows)
    assert any(row["passes"] for row in rows)
    assert any(not row["passes"] for row in rows)
    modes = candidate_mode_grid(4)
    assert net_v_min_over_modes(modes, "zero") == 0.0


def test_proxy_ht_restricted_modes_clear_dimensionless_floor_compatibility_helper():
    modes = candidate_mode_grid(8, protected=default_protected_modes())
    values = proxy_ht_eigenvalues(modes)

    assert len(modes) > 0
    assert values.min() >= dimensionless_hopf_gap()


def test_spectral_gap_screen_reports_open_status():
    screen = spectral_gap_screen(k_max=8, lambda2=0.1)

    assert screen.status == "open"
    assert screen.outputs["passes_proxy_bound"] is True
    assert screen.outputs["first_nonzero_proxy_eigenvalue"] == 3.0
    assert screen.outputs["mode_count"] > 0
