from bhsm.interface.aether_forward_product_dirac_weyl_enclosures import (
    product_dirac_compact_radius_weyl_variation_bounds,
    product_dirac_nonnegative_exterior_weyl_bounds,
)


def test_factorized_dirichlet_trial_decomposition() -> None:
    bounds = product_dirac_nonnegative_exterior_weyl_bounds(0.5, 2.0, 1.0)
    assert bounds["lower"] == 0.0
    assert bounds["trial_derivative_energy"] == 2.0
    assert bounds["trial_cross_bound"] == 2.0
    assert bounds["trial_potential_and_probe_bound"] == 5.0 / 6.0
    assert bounds["upper"] == 29.0 / 6.0


def test_factorized_variation_bounds_vanish_for_zero_superpotential() -> None:
    bounds = product_dirac_compact_radius_weyl_variation_bounds(10.0, 0.0, 1.0)
    assert bounds["first_Weyl_variation_bound"] == 0.0
    assert bounds["mixed_Weyl_variation_bound"] == 0.0


def test_factorized_variation_bounds_include_both_resolvent_pairs() -> None:
    bounds = product_dirac_compact_radius_weyl_variation_bounds(10.0, 2.0, 1.0)
    assert bounds["first_Weyl_variation_bound"] == 40.0
    assert bounds["direct_mixed_form_bound"] == 120.0
    assert bounds["two_resolvent_pair_bound"] == 320.0
    assert bounds["mixed_Weyl_variation_bound"] == 440.0
