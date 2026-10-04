"""New actual collar/prefix controls; no former production is invoked."""
import json
from pathlib import Path
import numpy as np
import sympy as sp

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'artifacts/muon_collar_source_coverage_20261003/replay_reference'


def test_actual_volume_pullback_and_transverse_geometric_identities():
    with np.load(DATA/'collar_coverage_actions.npz') as z:
        a={k:np.array(z[k]) for k in z.files}
    # This tests integrated transverse data, not the norm alone. No curve is rerun.
    assert np.max(abs(a['normal_transverse_pairing'])) < 1e-9
    assert np.max(abs(a['transverse_determinant_identity_residual'])) < 1e-9
    assert np.min(abs(a['Delta_X'])) > 1
    assert np.min(a['J_c']) > 0
    assert a['tau'][-1] == 0
    assert len(np.unique(a['metric_cells'][:,0])) >= 20
    assert abs(a['J_c'][0]-1) < 1e-12


def test_actual_spin_transport_uses_dirac_pairing_and_transported_chirality():
    with np.load(DATA/'collar_coverage_actions.npz') as a:
        U=a['spin_transport'];L=a['transported_chiral_left'];R=a['transported_chiral_right']
    r=json.loads((DATA/'result.json').read_text())['spin_transport']
    assert r['Dirac_pairing_residual'] < 1e-12
    assert r['transported_chiral_projector_residual'] < 1e-12
    assert np.max(abs(L@L-L)) < 1e-12
    assert np.max(abs(R@R-R)) < 1e-12
    assert np.max(abs(L+R-np.eye(4))) < 1e-12
    assert np.linalg.norm(U[-1].conj().T@U[-1]-np.eye(4)) > 1e-3
    assert r['both_chiral_sectors_retained']


def test_consumed_prefix_enclosure_excludes_saved_support_without_normalizing():
    p=json.loads((DATA/'prefix_collar_enclosure.json').read_text())
    r=json.loads((DATA/'result.json').read_text())
    assert p['bootstrap_closed'] and p['normal_turning_excluded_in_nodal_strip']
    assert p['radial_displacement_upper']['interval'][1] < 5.28e-26
    assert p['radial_momentum_change_upper']['interval'][1] < 4.30e-27
    assert r['prefix_chronology']['total_segments'] == 1222
    assert r['prefix_chronology']['proper_duration_interval'][1] < 1.495e-27
    assert p['rho_at_cut']-p['radial_displacement_upper']['interval'][1] > r['saved_source_support'][1]+0.58
    assert r['I_full'] is None and r['I_remainder'] is None
    assert r['T_required'] is None and r['B54_required'] is None
    assert r['physical_a_mu'] is None and r['physical_g_mu'] is None


def test_hamiltonian_covector_equation_and_branch_keep_full_shift():
    # Independent defining-equation control: the bounded equation omits no
    # time derivative by assumption; it is the canonical geodesic equation.
    t,r=sp.symbols('t r',real=True);nt,nr=sp.symbols('nt nr',real=True)
    nu,C,z=(sp.Function(k)(t,r) for k in ('nu','C','z'))
    g=sp.Matrix([[nu**2-C**2*z**2,-C**2*z],[-C**2*z,-C**2]])
    n=sp.Matrix([nt,nr]);inv=g.inv();variables=(t,r)
    Gamma=[sp.Matrix(2,2,lambda j,k:sum(inv[i,l]*(sp.diff(g[l,k],variables[j])+sp.diff(g[l,j],variables[k])-sp.diff(g[j,k],variables[l]))/2 for l in range(2))) for i in range(2)]
    acc=sp.Matrix([-(n.T@G@n)[0] for G in Gamma])
    covector=g*n
    derivative=sp.Matrix([sum(sp.diff(covector[i],variables[k])*n[k] for k in range(2)) for i in range(2)])+g*acc
    target=(n.T*g.diff(r)*n)[0]/2
    assert sp.simplify(derivative[1]-target) == 0
    assert sp.simplify(covector[1]+C**2*(nr+z*nt)) == 0
