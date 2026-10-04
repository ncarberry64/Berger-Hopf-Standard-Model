"""Actual source/metric checks; no synthetic W or claim that B54 was evaluated."""
from fractions import Fraction
from pathlib import Path
import json
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'artifacts/muon_wall_source_pairing_20261003/replay_reference'
GEO=ROOT/'artifacts/muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz'


def test_actual_full_source_pairing_against_independent_geometric_quadrature():
    with np.load(ART/'source_reached_pairings.npz') as p,np.load(GEO) as g:
        cells=p['gauss_cells'];widths=np.diff(g['rho'])[cells]
        weights=np.tile(np.polynomial.legendre.leggauss(4)[1],len(cells)//4)*widths/2
        gram=np.zeros((32,32),complex)
        for n in (1,3):
            source=p[f'actual_source_trial_n{n}']
            assert source.shape[:4]==(64,8,64,4)
            assert source.shape[-2:]==(n+1,n+1)
            columns=source.transpose(0,2,4,5,1,3).reshape(64,-1,32)
            gram+=np.einsum('goi,goj,g->ij',columns.conj(),columns,
                weights*p['mu5_volume_density_per_tau_normalized_Haar'])
            np.testing.assert_allclose(p[f'known_T_integrand_factor_mu5_p_n{n}'],
                source*p['mu5_volume_density_per_tau_normalized_Haar'][:,None,None,None,None,None],atol=0,rtol=0)
        np.testing.assert_allclose(gram,p['source_geometric_Gram'],atol=3e-15,rtol=3e-15)
        assert np.linalg.norm(p['actual_source_trial_n3'])>0


def test_radial_slice_signature_from_actual_metric_inverse_and_polynomial_certificate():
    cert=json.loads((ART/'radial_slice_causal_certificate.json').read_text())
    assert cert['all_source_support_cells_strictly_negative']
    assert cert['global_upper_outward']<0
    for row in cert['records']:
        assert max(map(Fraction,row['bernstein']))==Fraction(row['upper_exact'])<0
    with np.load(ART/'source_reached_pairings.npz') as p,np.load(GEO) as g:
        c=p['gauss_cells'];x=(p['gauss_rho']-g['rho'][c])/np.diff(g['rho'])[c]
        val=lambda k:g[k][0,c]*(1-x)+g[k][0,c+1]*x
        nu,C,z=(val(k) for k in ('proper_lapse','C_rho','proper_shift_rho'))
        metric=np.zeros((64,2,2));metric[:,0,0]=nu**2-(C*z)**2
        metric[:,0,1]=metric[:,1,0]=-C*C*z;metric[:,1,1]=-C*C
        inverse=np.linalg.inv(metric)
        expected=-p['constant_rho_induced_h_tau_tau']/(nu*C)**2
        # A floating inverse comparison is conditioned by the actual 2x2
        # metric, unlike the exact polynomial sign certificate above.
        roundoff=16*np.finfo(float).eps*np.linalg.cond(metric)*(1+abs(expected))
        assert np.all(abs(inverse[:,1,1]-expected)<=roundoff)
        assert np.all(inverse[:,1,1]>0)  # rho covector is timelike here.
        assert np.all(p['constant_rho_induced_h_tau_tau']<0)


def test_wall_pairing_has_both_chiral_sectors_without_duplicate_density():
    with np.load(ART/'source_reached_pairings.npz') as p,np.load(GEO) as g:
        nu,C,r,z=(g[k][0,-1] for k in ('proper_lapse','C_rho','base_radius','proper_shift_rho'))
        induced=np.diag([nu**2-(C*z)**2,-r*r,-r*r,-r*r])
        density=2*np.pi**2*np.sqrt(abs(np.linalg.det(induced)))
        np.testing.assert_allclose(p['M4_wall_geometric_density'],density*np.eye(64),rtol=2e-15,atol=0)
        L=np.kron(p['wall_chiral_left'],np.eye(16));R=np.kron(p['wall_chiral_right'],np.eye(16))
        np.testing.assert_allclose(L+R,np.eye(64),atol=4e-15,rtol=0)
        np.testing.assert_allclose(L.conj().T@p['M4_wall_geometric_density']@R,np.zeros((64,64)),atol=5e-14,rtol=0)
        rate=json.loads((ROOT/'artifacts/muon_parent_source_rate_20261003/replay_reference/cut_rate_record.json').read_text())
        np.testing.assert_allclose(p['M4_wall_geometric_density_tau'],3*rate['value']*p['M4_wall_geometric_density'],atol=0,rtol=0)


def test_initial_normal_chart_jet_retains_time_and_shift_terms():
    result=json.loads((ART/'result.json').read_text())['result']['wall_chart_initial_jet']
    with np.load(GEO) as g:
        nu,C,z=(float(g[k][0,-1]) for k in ('proper_lapse','C_rho','proper_shift_rho'))
        width=float(g['rho'][-1]-g['rho'][-2]);dt=float(g['proper_times'][1]-g['proper_times'][0])
        dr=lambda k:float((g[k][0,-1]-g[k][0,-2])/width)
        dtime=lambda k:float((g[k][1,-1]-g[k][0,-1])/dt)
        # Independent metric Christoffels at the seam, using the exact
        # inherited zero of shift there rather than roundoff sin(pi).
        z=0.0
        metric=np.array([[nu*nu-C*C*z*z,-C*C*z],[-C*C*z,-C*C]])
        derivatives=np.array([
            [[2*nu*dtime('proper_lapse'),-C*C*dtime('proper_shift_rho')],[-C*C*dtime('proper_shift_rho'),-2*C*dtime('C_rho')]],
            [[2*nu*dr('proper_lapse'),-C*C*dr('proper_shift_rho')],[-C*C*dr('proper_shift_rho'),-2*C*dr('C_rho')]],
        ])
        inv=np.linalg.inv(metric)
        gamma_rr=np.array([sum(inv[a,d]*(2*derivatives[1,d,1]-derivatives[d,1,1])/2 for d in range(2)) for a in range(2)])
        np.testing.assert_allclose([result['outgoing']['tau_ss_right_time_model'],result['outgoing']['rho_ss']],-gamma_rr/C**2,rtol=2e-15,atol=2e-15)
        assert result['outgoing']['tau_ss_right_time_model']!=0
        assert result['outgoing']['rho_s']==-result['incoming']['rho_s']
        assert result['outgoing']['tau_ss_right_time_model']==result['incoming']['tau_ss_right_time_model']
