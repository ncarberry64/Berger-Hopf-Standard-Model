import numpy as np
import pytest
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase,profile_preserving_raw_sample
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from bhsm.interface.muon_electromagnetic_soft_magnetic_source import uniform_magnetic_source_first_jets
from bhsm.interface.muon_corrected_profile_magnetic_response import corrected_profile_reached_sample
from bhsm.interface.muon_corrected_profile_mean_load import corrected_profile_mean_load
from bhsm.interface.muon_parent_retarded_hypercharge import regular_radial_basis
from bhsm.interface.muon_parent_mean_causal_action import MAXWELL_TO_CAP


@pytest.mark.parametrize('side',['incoming','outgoing'])
def test_corrected_cubic_and_two_source_contacts_against_original_full488_action(side):
    phase=load_profile_preserving_phase('artifacts/muon_finite_normal_phase_20261011/incoming_run_1'if side=='incoming'
        else'artifacts/muon_inherited_finite_normal_phase_20261011/run_1')
    rep=phase['representation'];angular=retained_full_q_angular_space();L=abs(phase['receipt']['span'])
    t=-L/2 if side=='incoming'else L/2;raw=profile_preserving_raw_sample(phase,t)['raw_fields']
    kw=dict(initial_pair=phase['arrays']['initial_pair'],reference_pair=phase['arrays']['reference_pair'])if side=='outgoing'else{}
    # A declared numerical action test direction; it is never used as a physical first response.
    rng=np.random.default_rng(237);z=rng.normal(size=(488,3))*.001;zd=rng.normal(size=(488,3))*.002
    z[480:]=0;z[480:483]=np.eye(3);zd[480:]=0
    p=.7;pt=.2;z[480:483]*=p;zd[480:483]=pt*np.eye(3)
    def point(x,fields=False):
        s=uniform_magnetic_source_first_jets(x,angular,electric_charge=.3)
        if not fields:
            f=corrected_profile_reached_sample(x,rep,angular,s['connection_source'],s['connection_source_rate'],
                coordinate_time=t,nu_squared_action=4.,**kw)['raw_forms']
            M,B,K=f
            return MAXWELL_TO_CAP*(z.T@K@z+z.T@B@zd+zd.T@B.T@z+zd.T@M@zd)
        b,br=regular_radial_basis(rep['rho'],1)
        interior=z[:400].T.reshape(3,5,4,20);rate=zd[:400].T.reshape(interior.shape)
        wall=(p*s['connection_source']).T[:3].reshape(interior.shape)
        wallrate=(pt*s['connection_source']+p*s['connection_source_rate']).T[:3].reshape(interior.shape)
        return s,dict(first_gauge=b[:,0,None,None,None,None]*interior+b[:,1,None,None,None,None]*wall,
            first_gauge_rate=b[:,0,None,None,None,None]*rate+b[:,1,None,None,None,None]*wallrate,
            first_gauge_radial=br[:,0,None,None,None,None]*interior+br[:,1,None,None,None,None]*wall,
            first_wall_gauge=wall,first_H=z[400:480].T.reshape(3,4,20),first_H_rate=zd[400:480].T.reshape(3,4,20))
    s,fields=point(raw,True)
    r=corrected_profile_mean_load(raw,rep,angular,s,p,pt,**fields,coordinate_time=t,nu_squared_action=4.,**kw)
    direction=np.zeros(268);direction[[0,37,74,98,99,111,188,260,264]]=[.1,.07,.02,.03,.02,.04,.03,.01,-.02]
    step=2e-5;fd=(point(raw+step*direction)-point(raw-step*direction))/(2*step)
    exact=np.einsum('i,iab->ab',direction,r['raw_mean_cotangent'])
    np.testing.assert_allclose(exact,fd,rtol=2e-5,atol=2e-10)
    np.testing.assert_allclose(r['raw_mean_cotangent'],r['raw_mean_cotangent'].swapaxes(-1,-2),rtol=1e-12,atol=2e-12)
    assert np.linalg.norm(r['source_motion_cotangent'])>0
    if side=='outgoing':
        # Existing parent-child profile differentiates to minus the child jet.
        assert np.max(abs(r['background_geometry_connection_first_jet']))==0
        assert np.linalg.norm(r['inherited_parent_geometry_first_jet'])>0
