"""Focused new range/branch checks; none replays the prior four checks."""
from pathlib import Path
import json
import numpy as np

from bhsm.interface.muon_collar_source_coverage import SavedNodalMetric,phase_rhs
from bhsm.interface.muon_cut_inverse_coverage import retained_radial_density_conversion

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'artifacts/muon_cut_inverse_coverage_20261003/replay_reference'


def read(p):
    with np.load(p,allow_pickle=False) as z:return {k:np.array(z[k]) for k in z.files}


def test_rapidity_first_exit_identity_on_actual_tail_arrays():
    geometry=read(ROOT/'artifacts/muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz')
    metric=SavedNodalMetric(geometry)
    for cell in (0,23,46):
        tau=float(np.mean(metric.times[cell:cell+2]));rho=float(metric.rho[-1]-.01)
        jet=metric.jet([tau,rho],(cell,63));nu,C,z=jet['values'][:3];dnu,dC,dz=jet['grad'][:3]
        theta=.03
        n=np.array([-np.sinh(theta)/nu,-np.cosh(theta)/C+z*np.sinh(theta)/nu])
        phase=np.r_[tau,rho,n];rhs=phase_rhs(phase,jet)
        # Independently differentiate theta=-asinh(nu*n_tau) using the
        # coordinate Christoffel geodesic action already implemented.
        theta_prime=-(nu*rhs[2]+(dnu@n)*n[0])/np.cosh(theta)
        a=dnu[1]/(nu*C);b=(dC[0]-z*dC[1]-C*dz[1])/(nu*C)
        assert abs(theta_prime-(a*np.sinh(theta)+b*np.cosh(theta)))<1e-11
        bounds=json.loads((REF/'connection_boxes.json').read_text())['tail_cells'][cell]
        assert bounds['a']['interval'][0]<=a<=bounds['a']['interval'][1]
        assert bounds['b']['interval'][0]<=b<=bounds['b']['interval'][1]


def test_whole_family_range_rejects_each_saved_source_point():
    c=json.loads((REF/'family_range.json').read_text());r=json.loads((REF/'source_range_rejection.json').read_text())
    assert c['radial_drop_upper']['interval'][1]<c['radial_strip']
    assert c['rapidity_upper']['interval'][1]<c['rapidity_bootstrap']
    assert c['prefix_rapidity_rate_lower']['interval'][0]>0
    # Independent inherited-array check of the chi->rho factor; a doubled
    # prefix C would still give positive rates, but would fail this check.
    prefix=json.loads((REF/'connection_boxes.json').read_text())['prefix']['C']['interval']
    geometry=read(ROOT/'artifacts/muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz')
    assert prefix[0]<=geometry['C_rho'][0,-1]<=prefix[1]
    assert .9<prefix[0]<prefix[1]<1.0
    assert c['prefix_family_bound_is_old_single_curve_bound'] is False
    assert c['ODE_replay_used_for_proof'] is False
    assert r['count']==64
    assert len(r['classifications'])==64
    assert np.all(np.array(r['points'])<r['hit_enclosure'][0])
    assert r['minimum_certified_gap']>.58
    assert r['root_solve_count']==0


def test_endpoint_branch_saltation_and_implicit_derivative():
    z=read(REF/'endpoint_branch_actions.npz');r=json.loads((REF/'endpoint_branch.json').read_text())
    c=json.loads((REF/'family_range.json').read_text());ph=z['phase']
    assert ph[-1,0]==0
    assert np.all(np.diff(ph[:,0])<0)
    assert len(r['interfaces'])==46
    assert all(i['new_cell'][0]==i['old_cell'][0]-1 for i in r['interfaces'])
    assert c['rho_hit_enclosure']['interval'][0]<=r['R_hit']<=c['rho_hit_enclosure']['interval'][1]
    assert r['tau_s']<-.03
    assert abs(r['dR_hit_dy']-r['determinant_slope'])<1e-11
    assert r['absolute_ODE_error_bound'] is None
    assert r['normalization_full'] is None


def test_actual_source_radial_density_conversion_is_not_native_overlap():
    geo=read(ROOT/'artifacts/muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz')
    pair=read(ROOT/'artifacts/muon_wall_source_pairing_20261003/replay_reference/source_reached_pairings.npz')
    arrays,receipt=retained_radial_density_conversion(geo,pair)
    assert max(abs(arrays['radial_candidate_normal_cancellation']))<1e-14
    assert max(abs(arrays['normalization_density_conversion_residual']))<1e-15
    assert np.any(abs(arrays['temporal_principal_ratio']-1)>.01)
    assert receipt['Gaussian_m_eta_replaced'] is False
    assert receipt['same_owner_inclusion_intertwining_proved'] is False
    result=json.loads((REF/'result.json').read_text())
    assert result['B54_required'] is None
    assert result['physical_a_mu'] is None and result['physical_g_mu'] is None
