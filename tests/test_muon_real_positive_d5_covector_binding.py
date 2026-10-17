"""Independent literal controls of the real positive-coframe eta conversion."""
from pathlib import Path
import sys
import unittest
import mpmath as mp
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from bhsm.interface.muon_real_positive_d5_covector_binding import real_positive_d5_covector_binding
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace


def fixture():
    values=dict(lapse=[1.3,.9],radial_coframe=[.8,1.4],radius=[1.1,.7],coordinate_shift=[.13,-.07],eta_profile=[.61,.92],eta_profile_coordinate_time=[.12,-.19],eta_profile_radial=[.31,.48])
    slopes=dict(lapse=[.04,-.02],radial_coframe=[-.03,.05],radius=[.07,.01],coordinate_shift=[.02,.015],eta_profile=[-.04,.06],eta_profile_coordinate_time=[.011,.023],eta_profile_radial=[.032,-.017])
    c={k:np.array(v,dtype=complex)for k,v in values.items()};c.update({k+'_first':np.array([v],dtype=complex)for k,v in slopes.items()})
    c['volume_density']=c['lapse']*c['radial_coframe']*c['radius']**3
    c['volume_density_first']=c['volume_density']*(c['lapse_first']/c['lapse']+c['radial_coframe_first']/c['radial_coframe']+3*c['radius_first']/c['radius'])
    return c


class CovectorBindingTests(unittest.TestCase):
    def test_mp_literal_clifford_covector_and_source_first(self):
        f=full_d5_localized_lepton_trace();c=fixture()
        with mp.workdps(70):
            for branch in ('particle','conjugate'):
                for eps in (-1,1):
                    a=real_positive_d5_covector_binding(c,gamma=f['gamma5D_'+branch],sheet_orientation=eps)
                    for r in range(2):
                        def literal(x):
                            b={k:mp.mpf(float(c[k][r].real))+x*mp.mpf(float(c[k+'_first'][0,r].real))for k in ('lapse','coordinate_shift','eta_profile','eta_profile_coordinate_time','eta_profile_radial')}
                            f0=(b['eta_profile_coordinate_time']-b['coordinate_shift']*b['eta_profile_radial'])/b['lapse']
                            return-(1+1j)*f0/mp.tan(b['eta_profile'])
                        self.assertLess(abs(complex(literal(0))-a['delta_scalar_body'][r]),2e-15)
                        self.assertLess(abs(complex(mp.diff(literal,0))-a['delta_scalar_body_first'][0,r]),2e-15)
                    self.assertLess(a['Clifford_output_contact_identity_defect'],2e-15)
                    self.assertLess(a['formal_to_native_contact_identity_defect'],2e-15)

    def test_local_nonunitary_similarity_with_noncommuting_body(self):
        c=fixture();G=full_d5_localized_lepton_trace()['gamma5D_particle'];a=real_positive_d5_covector_binding(c,gamma=G,sheet_orientation=-1)
        rng=np.random.default_rng(219);body=rng.normal(size=(4,4))+1j*rng.normal(size=(4,4))
        psi=rng.normal(size=4)+1j*rng.normal(size=4);pt=rng.normal(size=4)+1j*rng.normal(size=4);pr=rng.normal(size=4)+1j*rng.normal(size=4)
        for r in range(2):
            N,C,z,f,ft,fr=(c[k][r]for k in ('lapse','radial_coframe','coordinate_shift','eta_profile','eta_profile_coordinate_time','eta_profile_radial'))
            Bt=np.eye(4)/N;Br=-z*np.eye(4)/N+1j*G[0]@G[4]/C
            direct=Bt@pt+Br@pr+body@psi-(Bt*ft+Br*fr)@psi/np.tan(f)
            via_binding=Bt@pt+Br@pr+(body+a['covector_native_eta_spin_body'][r])@psi
            self.assertLess(np.max(abs(direct-via_binding)),5e-15)
        self.assertFalse(a['local_sin_f_similarity_is_unitary'])

    def test_density_isometry_and_real_source_norm_derivative(self):
        c=fixture();a=real_positive_d5_covector_binding(c,gamma=full_d5_localized_lepton_trace()['gamma5D_particle'],sheet_orientation=1)
        rng=np.random.default_rng(102);v=rng.normal(size=(2,16))+1j*rng.normal(size=(2,16));dv=rng.normal(size=(2,16))+1j*rng.normal(size=(2,16))
        w,dw=a['input_output_density_isometry'],a['input_output_density_isometry_first'][0]
        mu,dmu=a['fermion_geometric_density'],a['fermion_geometric_density_first'][0]
        left=mu*np.sum(abs(v)**2,axis=1);right=c['lapse']*np.sum(abs(w[:,None]*v)**2,axis=1)
        leftd=dmu*np.sum(abs(v)**2,axis=1)+2*mu*np.real(np.sum(v.conj()*dv,axis=1))
        chi=w[:,None]*v;chid=dw[:,None]*v+w[:,None]*dv
        rightd=c['lapse_first'][0]*np.sum(abs(chi)**2,axis=1)+2*c['lapse']*np.real(np.sum(chi.conj()*chid,axis=1))
        self.assertLess(np.max(abs(left-right)),3e-14);self.assertLess(np.max(abs(leftd-rightd)),3e-14)

    def test_no_complex_projection_or_polar_domain_selected(self):
        G=full_d5_localized_lepton_trace()['gamma5D_particle'];c=fixture();c['lapse'][0]+=1e-9j
        with self.assertRaises(ValueError):real_positive_d5_covector_binding(c,gamma=G,sheet_orientation=1)
        c=fixture();c['eta_profile'][0]=0
        with self.assertRaises(ValueError):real_positive_d5_covector_binding(c,gamma=G,sheet_orientation=1)


if __name__=='__main__':unittest.main()
