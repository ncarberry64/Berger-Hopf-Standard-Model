"""Direct source checked against independently executed original D5."""
import numpy as np
from bhsm.interface.muon_d5_shape_coefficient_source import d5_coefficient_source
from bhsm.interface.muon_holomorphic_d5_trace_action import d5_unsquared_weak_trace
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace


def test_complete_direct_source_matches_original_unsquared_action_difference():
    full=full_d5_localized_lepton_trace();g=full['gamma5D_particle'];T=full['unitTr16_gauge_particle'];rng=np.random.default_rng(512)
    c={};values=dict(lapse=1.2+.03j,radial_coframe=.8-.02j,radius=.9+.1j,coordinate_shift=.17-.04j,
        geometric_time_contact=.05+.02j,geometric_radial_contact=.03-.02j,surface_proper_clock_rate=.7+.03j,volume_density=1+.01j,eta_radial_contact=0j)
    for key,val in values.items():c[key]=np.array([val]);c[key+'_first']=np.array([[.02+.01j]])
    c['gauge_connection_material']=rng.normal(size=(1,5,4))*.1+.03j
    c['gauge_connection_material_first']=rng.normal(size=(1,1,5,4))*.03+.01j
    eta=rng.normal(size=(1,64,64))*.002+.001j;deta=rng.normal(size=(1,64,64))*.001+.002j
    for eps in(1,-1):
        a=d5_coefficient_source(c,gamma=g,generators=T,eta=eta,eta_first=deta,energy=.12+.03j,sheet_orientation=eps)
        def original(h):
            cc={k:(v+h*c[k+'_first'][0]if k+'_first'in c else v)for k,v in c.items()if not k.endswith('_first')}
            return d5_unsquared_weak_trace(cc,np.ones(1),gamma=g,carrier_generators=T,angular_derivatives=np.zeros((3,1,1)),
                right_values=np.eye(64)[None],right_radial=np.zeros((1,64,64)),right_coordinate_time=np.zeros((1,64,64)),
                literal_left_values=np.eye(64)[None],energy=.12+.03j,sheet_orientation=eps,eta_clifford_contact=eta+h*deta)['original_D5_on_trial']
        h=2e-6;fd=(original(h)-original(-h))/(2*h)
        assert np.max(abs(fd-a['direct_source_D5_zero_order']))<4e-10
        assert np.max(abs(original(0)-a['original_D5_zero_order']))<5e-15
