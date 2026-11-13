"""New first-variation checks only; no prior producer or seven-check replay."""
from pathlib import Path
import json
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'artifacts'
OUT=A/'muon_joint_variational_attachment_20261005/run_2'

def read(path):
    with np.load(path,allow_pickle=False) as z:return {k:np.array(z[k]) for k in z.files}

@pytest.fixture(scope='module')
def actual():return read(OUT/'node3_joint_known_variations.npz')

def test_actual_green_densities_distinguish_action_dual_and_L2(actual):
    a=actual;G=a['Gamma'];mu=2*np.pi**2*float(a['radius'])**3
    # The coframe symbol gamma^rho=Gamma4/C-zeta Gamma0/nu and
    # mu5=2pi² nu C r³ give these two densities at the actual proper wall.
    L2=mu*1j*G[4];Dirac=mu*1j*(G[0]@G[4])
    np.testing.assert_allclose(a['geometric_L2_Green_density'],L2,rtol=2e-15,atol=1e-14)
    np.testing.assert_allclose(a['Dirac_bar_Green_density'],Dirac,rtol=2e-15,atol=1e-14)
    assert np.linalg.norm(L2-Dirac)>1
    assert np.linalg.norm(Dirac+Dirac.conj().T)<1e-12
    old=read(A/'muon_wall_input_attachment_20261005/run_1/node3_projected_intrinsic_kinetic.npz')
    columns=[]
    for n in (1,3):
        xi=old[f'normalized_wall_W_input_n{n}'];col=np.zeros_like(xi)
        # An independent matrix action on every actual angular coefficient.
        for m in range(n+1):
            for k in range(n+1):col[:,m,k]=Dirac@xi[:,m,k]*float(a['kappa'])
        columns.append(col.reshape(-1,12))
    np.testing.assert_allclose(np.concatenate(columns),a['W_material_Green_Dirac'],rtol=3e-15,atol=2e-14)

def test_actual_green_time_jet_uses_action_rate_and_inherited_norm(actual):
    a=actual;R=float(a['radius']);I=float(a['I']);H=float(a['H']);It=float(a['I_tau'])
    # Differentiate only the declared scalar coefficient at this node,
    # independent of the saved matrix formula. This is no history solve.
    eps=1e-20
    coefficient=lambda t:2*np.pi**2*(R+t*H*R)**3/np.sqrt(2*(I+t*It))
    derivative=coefficient(1j*eps).imag/eps
    expected=derivative/coefficient(0)
    assert abs(expected-float(a['Green_coordinate_time_rate']))<2e-15
    np.testing.assert_allclose(a['W_material_Green_Dirac_tau'],expected*a['W_material_Green_Dirac'],rtol=3e-15,atol=3e-14)

def test_actual_bulk_euler_pairing_and_diagnostic_dual_load(actual):
    a=actual;p=read(A/'muon_retained_tail_core_20261005/run_1/points/node_03.npz')
    old=read(A/'muon_wall_input_attachment_20261005/run_1/node3_projected_intrinsic_kinetic.npz')
    cut=read(A/'muon_coupled_cut_forms_20261004/run_1/coupled_cut_source_actions.npz')
    weighted=cut['radial_weights']*p['volume'];G0=a['Gamma'][0];expected=np.zeros(24,complex)
    for n in (1,3):
        xi=old[f'normalized_wall_W_input_n{n}']
        D=p[f'Dp_n{n}'];barD=np.einsum('oi,gimk->gomk',G0,D).reshape(len(weighted),-1)
        for j in range(12):
            test=xi[...,j].ravel()
            contracted=barD@test.conj()
            expected[j]+=np.dot(weighted*p['u'],contracted)
            expected[12+j]+=np.dot(weighted*p['p'],contracted)
    assert np.linalg.norm(expected-a['known_bulk_Dirac_Euler_p_source'])<1e-14*np.linalg.norm(expected)
    # Its positive-L2 load is the cached mass dual, not the Dirac-bar row.
    np.testing.assert_allclose(a['diagnostic_bulk_Riesz_load_12'],p['M'][:,12:],rtol=3e-14,atol=2e-15)
    c=a['source_coordinates'];x=np.r_[c,-c]
    ell=np.vdot(x,a['diagnostic_bulk_Riesz_load_original'])
    pp=np.vdot(c,p['M'][12:,12:]@c).real
    vv=np.vdot(x,p['M']@x).real
    assert abs(ell)**2<=pp*vv*(1+2e-14)
    result=json.loads((OUT/'result.json').read_text())
    assert result['native_R4'] is None and result['new_stationary_solve'] is False
