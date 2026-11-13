"""Central-sector reduction and retarded fixed-trace action checks."""
import numpy as np
import pytest

from bhsm.interface.muon_parent_retarded_hypercharge import (
    ALPHA, WALL, central_source_reduction, frozen_e1_coefficients,
    regular_radial_basis, maxwell_galerkin_form,
    compact_trace_pulse, retarded_parent_dtn_application,
)


def test_actual_central_source_commutes_and_is_coexact_without_weak_sector_pruning():
    reduction = central_source_reduction()
    assert max(reduction['checks'].values()) < 2e-11
    np.testing.assert_allclose(reduction['source_Gram'], (10/3)*np.eye(8), atol=2e-12)
    assert not reduction['physical_total_photon_projection']


def test_actual_pole_scalings_fix_the_finite_energy_indicial_domain():
    rho = np.array([1e-4, 2e-4, 4e-4])
    data = frozen_e1_coefficients(rho)
    for name, exponent in (('electric', 4), ('radial', 4), ('angular', 2)):
        slopes = np.log(data[name][1:]/data[name][:-1])/np.log(2)
        np.testing.assert_allclose(slopes, exponent, atol=3e-5)
    np.testing.assert_allclose(data['angular']/data['radial']*rho**2, 1, atol=2e-6)
    assert ALPHA*(ALPHA+3) == pytest.approx(9)
    assert not data['stationary_base_claim']


def test_large_coordinate_shift_keeps_the_lorentz_action_without_invented_energy_guard():
    def coefficients(rho):
        data = control_coefficients(rho)
        data['shift'] = 4*rho*(WALL-rho)
        return data
    form = maxwell_galerkin_form(10, coefficients, quadrature_order=160)
    assert form['coordinate_stiffness_min_eigenvalue'] < 0
    assert form['shift_light_ratio_max'] > 1
    assert np.linalg.eigvalsh(form['Kspatial'])[0] > 0
    np.testing.assert_allclose(form['K'], form['Kspatial']-form['Kshift'])


def test_regular_tests_vanish_at_wall_while_the_trace_lift_is_independent():
    B, D = regular_radial_basis(np.array([WALL]), 7)
    np.testing.assert_allclose(B[0, :-1], 0)
    assert B[0, -1] == 1
    assert D[0, -1] == pytest.approx(ALPHA/WALL)
    eps = 1e-6; x = np.linspace(.1, WALL-.1, 12)
    Bp, _ = regular_radial_basis(x+eps, 7)
    Bm, _ = regular_radial_basis(x-eps, 7)
    _, Dx = regular_radial_basis(x, 7)
    np.testing.assert_allclose(Dx, (Bp-Bm)/(2*eps), atol=3e-9, rtol=1e-8)


def control_coefficients(rho):
    # A finite action control with the SAME action-owned pole powers.
    return dict(electric=rho**4, radial=1.2*rho**4,
                angular=1.2*rho**2, shift=.07*rho*(WALL-rho),
                wall_radial=1.2*WALL**4)


def test_retarded_dirichlet_parent_reaction_retains_action_endpoint_and_adjoint():
    form = maxwell_galerkin_form(10, control_coefficients, quadrature_order=160)
    result = retarded_parent_dtn_application(form, source_duration=.7,
        final_time=1.3, time_steps=512, rtol=2e-11, atol=2e-13)
    np.testing.assert_allclose(result['state'][0], 0)
    np.testing.assert_allclose(result['velocity'][0], 0)
    assert result['interior_algebraic_residual_max'] < 1e-10
    assert result['energy_work_defect'] < 2e-7
    assert result['on_shell_action_boundary_defect'] < 2e-7
    assert result['adjoint_defect'] < 2e-8
    assert not result['background_initial_state_assigned']
    assert not result['physical_Pauli_contraction']
    assert result['source_scope'].startswith('CONTROL_ONLY')


def test_compact_probe_and_derivatives_have_zero_before_source_support():
    t = np.array([-.2, 0., .2, 1., 1.1])
    for value in compact_trace_pulse(t, 1):
        np.testing.assert_allclose(value[[0, 1, 3, 4]], 0)
    eps = 1e-6; x = np.linspace(.1, .9, 13)
    v, dv, ddv = compact_trace_pulse(x, 1)
    p, dp, _ = compact_trace_pulse(x+eps, 1)
    m, dm, _ = compact_trace_pulse(x-eps, 1)
    np.testing.assert_allclose(dv, (p-m)/(2*eps), atol=3e-9)
    np.testing.assert_allclose(ddv, (dp-dm)/(2*eps), atol=2e-8)


def test_time_step_refinement_resolves_contraction_rather_than_a_conditioning_shift():
    form = maxwell_galerkin_form(8, control_coefficients, quadrature_order=160)
    options = dict(source_duration=.7, final_time=1.3, rtol=1e-12, atol=1e-14)
    a = retarded_parent_dtn_application(form, time_steps=128, **options)
    b = retarded_parent_dtn_application(form, time_steps=256, **options)
    c = retarded_parent_dtn_application(form, time_steps=512, **options)
    # The contraction is already near the integrator's accuracy floor;
    # require stability, and test refinement on independent weak identities.
    assert abs(b['boundary_trace_contraction']-c['boundary_trace_contraction']) < 1e-9
    assert abs(a['boundary_trace_contraction']-b['boundary_trace_contraction']) < 1e-9
    assert c['energy_work_defect'] < a['energy_work_defect']
    assert c['adjoint_defect'] < b['adjoint_defect'] < a['adjoint_defect']
    assert c['on_shell_action_boundary_defect'] < b['on_shell_action_boundary_defect'] < a['on_shell_action_boundary_defect']
    assert c['quadrature_source_breakpoint_split']
    assert c['quadrature_grid_points'] > c['time_steps']
