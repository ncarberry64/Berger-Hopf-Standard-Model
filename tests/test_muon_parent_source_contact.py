"""New parent source/action checks; do not replay prior calculations."""
from pathlib import Path
import numpy as np
from bhsm.interface.muon_parent_source_contact import (
    parent_insertion, computational_profiles, exact_affine_integral,
    gauss_affine_integral,
)

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'artifacts/muon_matched_mechanical_source_20261002/replay_reference/matched_source_and_weak_actions.npz'
GEO=ROOT/'artifacts/muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz'
NEW=ROOT/'artifacts/muon_parent_source_contact_20261003/replay_reference/parent_source_contact.npz'


def test_new_parent_sign_matches_existing_charged_n0_insertion():
    """Independent charged restriction of the actual rank16 source."""
    with np.load(SRC) as s:
        H=s['unit_trace_carrier_basis']
        Q=1j*(np.sqrt(2)*H[2]+np.sqrt(10/3)*H[3])
        charged=np.flatnonzero(np.isclose(np.diag(Q),-1))[0]
        xi=parent_insertion(s['saved_gamma_LR'],s['original_n1'],H)
    with np.load(ROOT/'artifacts/muon_source_jet_20261002/replay_reference/local_source_actions.npz') as p:
        inp=p['input_labels'];out=p['output_labels'];old=p['Xi_complete']
        for lr in (0,1):
            for ci,(n,spin,m,k) in enumerate(inp):
                if n:continue
                for lrout in (0,1):
                    for ri,(nout,sout,mout,kout) in enumerate(out):
                        if nout!=1:continue
                        actual=xi[:,(2*lrout+sout)*16+charged,(2*lr+spin)*16+charged,
                                  (1-mout)//2,(1-kout)//2]
                        np.testing.assert_allclose(actual,old[:,lrout*len(out)+ri,lr*len(inp)+ci],atol=3e-15,rtol=3e-15)


def test_actual_parent_contact_and_connected_source_output():
    with np.load(NEW) as p:
        c=p['K_ZA_unit_contact']
        assert c.shape==(8,8,64,64)
        assert p['Xi_A_unit_n3'].shape==(8,64,64,4,4)
        assert np.linalg.norm(p['Xi_A_unit_n3'])>6.5
        np.testing.assert_allclose(c,c.conj().transpose(0,1,3,2),atol=2e-14)
        np.testing.assert_allclose(np.trace(c,axis1=2,axis2=3),(80/3)*np.eye(8),atol=4e-14)


def test_zero_trace_test_is_in_central_coexact_gauge_subset():
    with np.load(GEO) as g, np.load(SRC) as s:
        L,z=computational_profiles(g['rho'])
        assert np.all(z[:24]==0) and np.all(z[40:]==0)
        assert L[-1]==1 and z[-1]==0
        np.testing.assert_array_equal(L[z>0],1)
        H=s['unit_trace_carrier_basis']
        np.testing.assert_array_equal(H[:3]@H[3]-H[3]@H[:3],0)
        # The saved full constraint gradient, restricted only to central Y.
        assert np.linalg.norm(s['constraint_gradient_n1'][:,:,3])<6e-15


def test_new_nodal_integration_agrees_with_exact_polynomial_integral():
    with np.load(GEO) as g:
        rho=g['rho'];_,z=computational_profiles(rho)
        nu,C,r=(g[k][0] for k in ('proper_lapse','C_rho','base_radius'))
        for factors in ([nu,C,r,z,z,z],[nu,C,r,r,r,z,z]):
            exact=float(exact_affine_integral(rho,factors))
            np.testing.assert_allclose(gauss_affine_integral(rho,factors),exact,rtol=3e-15,atol=0)
