"""New cutoff-form, conormal-domain and whole-replacement applications."""
from pathlib import Path
import numpy as np
from bhsm.interface.muon_cutoff_domain_binding import (
    surface_inertia_forms,cutoff_inertia_coefficient,
    past_future_weyl,consume_comparison_domain,remove_recorded_local,
)

ROOT=Path(__file__).resolve().parents[1]


def saved():
    with np.load(ROOT/'artifacts/muon_stationary_native_reference_load_20261019/run_4/native_reference_load.npz') as z:
        return {k:z[k].copy() for k in z.files}


def test_surface_inertia_clock_projection_and_nonzero_endpoint_contacts():
    with np.load(ROOT/'artifacts/muon_retained_response_20261018/inputs/outgoing_history.npz') as z:
        raw=z['lo_raw_fields'][:100].copy();rate=z['lo_raw_coordinate_time_derivative'][:100].copy()
    a=surface_inertia_forms(raw)
    assert abs(a['wall_velocity'].value)>.1
    density=1.5*np.dot(a['radius'].gradient,rate)/(a['radius'].value*a['induced_lapse'].value)
    assert abs(a['proper_density_connection'].value-density)<2e-12
    assert abs(density)>.1
    dl=np.r_[1.,(-1.)**np.arange(1,13),(-1.)**np.arange(12),np.zeros(12)]
    for data in a['forms'].values():
        assert data['identity_twojet_defect']<2e-10
        assert data['independent_area_kinetic_defect']<2e-11
        assert data['independent_momentum_kinetic_defect']<2e-11
        assert abs(data['coordinate_source_momentum_per_gamma'].value)>1e-4
        expected=data['qdot_momentum_factor_per_gamma'].value*dl
        assert np.max(abs(data['original_area_per_gamma'].gradient[37:74]-expected))<2e-11
        rho=data['proper_inertia_per_gamma']
        assert np.max(abs(rho.gradient[37:74]))==0.
        assert rho.gradient[99]==0.


def test_new_cutoff_row_piece_has_complete_c_and_geometry_chain():
    with np.load(ROOT/'artifacts/muon_coupled_reference_replacement_20261019/run_2/coupled_replacement.npz') as z:
        raw=z['after_raw_geometry100'].copy()
    rho=surface_inertia_forms(raw)['forms']['M8']['proper_inertia_per_gamma']
    a=cutoff_inertia_coefficient(rho,dimension=7,cutoff_anchor=1.,full_geometry=True)
    assert a.value==-rho.value
    assert abs(a.gradient[-1]-3.5*rho.value)<1e-12
    assert abs(a.hessian[-1,-1]+3.5*4.5*rho.value)<1e-11
    assert np.max(abs(a.hessian[:-1,-1]-3.5*rho.gradient))<1e-11


def test_weyl_twojet_on_original_fields_and_independent_resolvent_parameter():
    n=saved();t=n['actual_theta'];v=np.sin(np.arange(23))*.02;step=2e-5
    a=past_future_weyl(t,spectral_parameter=-1.)
    plus=past_future_weyl(t+step*v[:22],spectral_parameter=-1.+step*v[22])
    minus=past_future_weyl(t-step*v[:22],spectral_parameter=-1.-step*v[22])
    for key in a['maps']:
        m,p,q=a['maps'][key],plus['maps'][key],minus['maps'][key]
        assert m['Riccati_original_row_max']<2e-10
        assert m['second_original_row_max']<2e-10
        assert np.max(abs((p['value']-q['value'])/(2*step)-np.einsum('i,iab->ab',v,m['gradient23'])))<2e-8
        assert np.max(abs((p['gradient23']-q['gradient23'])/(2*step)-np.einsum('j,ijab->iab',v,m['hessian23'])))<3e-7
    r=consume_comparison_domain(a,n['actual_theta_gradient'],n['actual_theta_hessian'])
    assert r['original_first_order_rows_max']<2e-10
    assert np.max(abs(r['conormal_jump_rows']))<2e-10
    assert r['frequency_Green_identity_defect']<2e-10
    assert r['full_gluing_Hessian_symmetry_defect']<2e-10
    assert np.max(abs(r['original36_source_rows']))<2e-10
    assert r['differentiated_source_jump_first_max']<2e-10
    assert r['differentiated_source_jump_second_max']<2e-10
    assert r['independently_solved_left_reflection_kernel_defect']<2e-10
    assert np.max(abs(r['past_cut_covector152'][:151]))>1.


def test_full_recorded_local_subtraction_uses_moved_cached_twojet():
    with np.load(ROOT/'artifacts/muon_coupled_reference_replacement_20261019/run_2/coupled_replacement.npz') as z:
        c={k:z[k].copy() for k in z.files}
    a=remove_recorded_local(c);n=saved()
    assert np.max(abs(c['after_known_gradient']-a['local_gradient151']-a['bare_gradient151']))<2e-12
    assert np.max(abs(c['after_known_hessian']-a['local_Hessian151']-a['bare_Hessian151']))<2e-11
    assert np.max(abs(a['bare_gradient151']))>1.
    assert np.max(abs(a['bare_gradient151'][62:]))==0.
    # Structural cancellation is a partial accounting identity, not a new
    # physical52 pass or an interacting inverse.
    fresh=n['known_plus_native0_gradient151']-a['local_gradient151']
    assert np.max(abs(fresh[62:]-n['actual_gradient'][62:]))<2e-12
