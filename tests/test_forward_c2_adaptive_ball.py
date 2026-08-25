from __future__ import annotations

import numpy as np

from bhsm.interface.aether_forward_c2_adaptive_ball import (
    derived_adaptive_ball,
    translated_ball_bounds_with_share,
)


def _fixtures():
    pf = {
        "hard_D3_center": 0.1,
        "D4_full_hard_hard_upper": 0.1,
        "rhs_raw_derivative_center": 0.1,
        "rhs_raw_second_derivative_upper": 0.1,
        "structured_b_psi_Lipschitz_upper": 0.01,
        "center_hard_rate_raw_norm": 0.1,
    }
    launch = {
        "c_psi_interval": [2.0, 2.1],
        "c_psi_Lipschitz_upper": 0.01,
        "b_psi_interval": [3.0, 3.1],
    }
    line = {
        "eigenline_gap_lower": 2.0,
        "weighted_selected_to_complement_first_variation_on_ball": 0.01,
        "selected_eigenvalue_first_derivative_bound": 0.01,
    }
    weights = np.ones(98)
    coefficient = lambda state, weights, radius: {
        "root_log_R4_interval": [-radius, radius],
        "root_lapse_interval": [1.0 - radius, 1.0 + radius],
        "root_D_tau_log_R4_interval": [1.0 - radius, 1.0 + radius],
    }
    return pf, launch, line, weights, coefficient


def test_supplied_share_stays_inside_admissible_radius() -> None:
    pf, launch, line, weights, coefficient = _fixtures()
    ball = translated_ball_bounds_with_share(
        center_path=0.1,
        tube=0.1,
        local_radius_share=0.75,
        pf=pf,
        launch_ball=launch,
        line=line,
        parent_radius=1.0,
        root_state=np.zeros(98),
        weights=weights,
        coefficient_enclosure=coefficient,
    )
    assert ball["local_radius_share"] == 0.75
    assert ball["derived_local_radius"] > 0.1
    assert ball["total_root_relative_radius"] < ball["admissible_radius"]


def test_adaptive_share_is_strict_midpoint_of_derived_interval() -> None:
    pf, launch, line, weights, coefficient = _fixtures()
    ball = derived_adaptive_ball(
        center_path=0.1,
        tube=0.1,
        pf=pf,
        launch_ball=launch,
        line=line,
        parent_radius=1.0,
        root_state=np.zeros(98),
        weights=weights,
        coefficient_enclosure=coefficient,
    )
    lower = ball["allocation_lower_necessity"]
    selected = ball["allocation_selected_midpoint"]
    upper = ball["allocation_feasible_upper"]
    assert 0.0 < lower < selected < upper < 1.0
    assert np.isclose(selected - lower, upper - selected)
    assert ball["derived_local_radius"] > 0.1


def test_lower_probe_advances_past_multiplication_rounding_equality() -> None:
    pf, launch, line, weights, coefficient = _fixtures()
    # This geometry makes rho_min exactly close to one half; one nextafter
    # step may still round rho*m back to the incoming tube.
    ball = derived_adaptive_ball(
        center_path=0.1,
        tube=0.4,
        pf=pf,
        launch_ball=launch,
        line=line,
        parent_radius=1.3,
        root_state=np.zeros(98),
        weights=weights,
        coefficient_enclosure=coefficient,
    )
    assert ball["derived_local_radius"] > 0.4
    assert ball["allocation_selected_midpoint"] > ball["allocation_lower_necessity"]
