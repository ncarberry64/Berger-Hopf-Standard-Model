"""MP exponential/variation controls, without selecting a physical source."""
import numpy as np
import mpmath as mp
import pytest
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
from bhsm.interface.muon_spin_duhamel_insertion import (
    spin_duhamel_insertion_kernels,spin_endpoint_and_frame_kernels)

def gamma():return full_d5_localized_lepton_trace()['gamma5D_particle'][[0,4,1,2,3]]
def mm(a):return mp.matrix([[mp.mpc(float(z.real),float(z.imag))for z in row]for row in a])
def binary(a):return np.array([[complex(z)for z in row]for row in a.tolist()])

def test_all10_noncommuting_exponentials_mp64_and_tiny_corrections():
    G=gamma()
    with mp.workdps(64):
        for total,split in((.23,.07),(2.1e-6,-3.0e-11)):
            for eps in(-1,1):
                a=spin_duhamel_insertion_kernels(G,total_parameter=total,split_parameter=split,orientation=eps)
                K=mm(a['background_boost_generator'])
                L=mp.expm(-eps*mp.mpf((total+split)/2)*K)
                R=mp.expm(-eps*mp.mpf((total-split)/2)*K)
                for j,J in enumerate(a['generators']):
                    ref=-L*mm(J)*R
                    np.testing.assert_allclose(a['stable_kernel'][j],binary(ref),atol=2e-15,rtol=2e-15)
                    np.testing.assert_allclose(a['literal_finite_gamma_kernel_correction'][j],binary(ref+mm(J)),atol=2e-15,rtol=2e-13)
                if abs(split)<1e-9:
                    anti=a['generator_anticommutes_with_boost']
                    assert np.min(abs(a['correction_coefficient_J'][anti]))>0
                    assert np.max(abs(a['correction_coefficient_J'][anti]))<1e-20
                    assert max(a['literal_increment_remainder_bounds'])<1e-100

def test_all10_independent_endpoint_frame_variations_mp64():
    G=gamma();a=spin_duhamel_insertion_kernels(G,total_parameter=.17,split_parameter=.03,orientation=1)
    with mp.workdps(64):
        K=mm(a['background_boost_generator']);P=mp.expm(-mp.mpf('.17')*K)
        A0=mp.mpf('.23')*K;A1=mp.mpf('-.12')*K
        v=spin_endpoint_and_frame_kernels(G,parallel=binary(P),initial_connection=binary(A0),final_connection=binary(A1))
        for j,J in enumerate(a['generators']):
            Jm=mm(J)
            end=mp.diff(lambda e:mp.expm(-e*Jm)*P,0)
            start=mp.diff(lambda e:P*mp.expm(e*Jm),0)
            np.testing.assert_allclose(v['independent_final_frame'][j],binary(end),atol=2e-15)
            np.testing.assert_allclose(v['independent_initial_frame'][j],binary(start),atol=2e-15)
        np.testing.assert_allclose(v['moving_initial_time'],binary(P*A0),atol=2e-15)
        np.testing.assert_allclose(v['moving_final_time'],binary(-A1*P),atol=2e-15)

def test_source_carrier_and_parameter_guards():
    G=gamma()
    with pytest.raises(ValueError):spin_duhamel_insertion_kernels(G,total_parameter=.2j,split_parameter=0,orientation=1)
    with pytest.raises(ValueError):spin_duhamel_insertion_kernels(G,total_parameter=.2,split_parameter=0,orientation=0)
    with pytest.raises(ValueError):spin_duhamel_insertion_kernels(G[:4],total_parameter=.2,split_parameter=0,orientation=1)
