"""Incidence calculus checks; these are not physical formation admission."""
import numpy as np

from bhsm.interface.muon_native_event_incidence_contacts import (
    endpoint_theta, native_density_clock_contact,
    evaluate_endpoint_incidence_contacts,
)


def _theta():
    return np.r_[1.2, .9, [.01, -.002, .003, .004],
                 np.linspace(-.08, .03, 12), [.1, 1.05, .02, -.01]]


def test_full_contact_twojet_has_both_clock_and_field_contacts():
    p = _theta(); c = p.copy(); c[:2] *= [1.01, .8]
    c[2:6] += .001
    a = native_density_clock_contact(p, c, .03, -.07)
    x = a['coordinate46']; direction = np.linspace(-.04, .03, 46)
    direction[[0, 1, 22, 23]] *= .1
    def value(t):
        z = x+t*direction
        return native_density_clock_contact(z[:22], z[22:44], z[44], z[45])['contact_value18']
    h = 2e-4
    vm, vp, v0 = value(-h), value(h), a['contact_value18']
    first = np.einsum('i,iab->ab', direction, a['contact_gradient46'])
    second = np.einsum('i,j,ijab->ab', direction, direction, a['contact_Hessian46'])
    assert np.max(abs((vp-vm)/(2*h)-first)) < 2e-10
    assert np.max(abs((vp-2*v0+vm)/h**2-second)) < 4e-8
    assert a['Hessian_symmetry_defect'] < 1e-13
    # A lapse change cannot be suppressed by treating proper clocks equally.
    assert abs(a['proper_clock_ratio']-1.25) < 1e-14
    assert np.linalg.norm(a['contact_value18']) > .1


def test_factor_incidence_is_independent_of_source_columns():
    p = _theta(); c = p.copy(); c[1] = .7
    a = native_density_clock_contact(p, c, .04, -.03)
    r, d = a['proper_clock_ratio'], a['density_ratio']
    qdot = np.arange(18*18).reshape(18, 18)*1e-4
    # q_parent=I enumerates the full operator kernel, not a physical mode.
    vp = qdot/p[1]+a['parent_C18']
    ddot = c[1]*d*(-.03-r*.04)
    vc = (ddot*np.eye(18)+d*qdot)/c[1]+a['child_C18']*d
    assert np.max(abs(vc-r*d*vp-a['contact_value18'])) < 1e-14


def test_identical_coefficients_without_equal_clock_rates_still_have_contact():
    p = _theta()
    a = native_density_clock_contact(p, p, .01, .04)
    assert np.max(abs(a['contact_value18']-.03*np.eye(18))) < 1e-14


def test_original_saved_endpoint_density_chain():
    from pathlib import Path
    folder = Path(__file__).resolve().parents[1]/'artifacts/muon_retained_response_20261018/inputs'
    args = []
    for side, label in [('incoming', 'hi'), ('outgoing', 'lo')]:
        with np.load(folder/(side+'_history.npz'), allow_pickle=False) as z:
            args.extend([z[label+'_raw_fields'], z[label+'_raw_coordinate_time_derivative']])
    with np.load(folder.parents[1]/'muon_cutoff_domain_binding_20261019/run_2/cutoff_domain_binding.npz') as z:
        saved=dict(raw268=z['retained_child_plus_raw268'],
                   rate268=z['retained_child_plus_coordinate_time_derivative268'])
        for target, source in [('density', 'canonical_Cauchy_density_factor'),
                               ('kappa', 'proper_density_connection')]:
            for suffix in ('value', 'gradient100', 'Hessian100'):
                saved[target+'_'+suffix] = z['retained_child_plus_'+source+'_'+suffix]
    arrays, r = evaluate_endpoint_incidence_contacts(*args, saved_child_density=saved)
    assert r['original_factor_chain_rule_max'] < 1e-13
    assert r['proper_clock_ratio'] > 1.5
    assert abs(r['density_ratio']-1) < 1e-12
    assert r['contact_Frobenius'] > 1
    assert not r['physical_transmission_or_common_time_flow_established']
    assert not r['added_as_action_or_force']
    assert r['saved_child_density_and_connection_reused']
    assert arrays['contact_Hessian46'].shape == (46, 46, 18, 18)
    assert endpoint_theta(args[0]).shape == (22,)
