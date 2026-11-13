import numpy as np
from bhsm.interface.muon_moving_reference_trace_source import moving_reference_profile_source,fixed_radial_coefficient_test_restriction
from bhsm.interface.muon_holomorphic_normal_geometry import holomorphic_geometry_rows


def test_literal_reference_only_profile_clock_sign_and_all_three_slots():
    ref=np.zeros((2,268),complex);ref[:,0]=[.03+.01j,.05-.02j]
    ref[:,37]=[.02+.01j,-.01+.003j];ref[:,98]=[.001,.002];ref[:,99]=[.003+.001j,-.002+.001j]
    rho=np.array([.1,.3,.6]);a=moving_reference_profile_source(ref,rho);h=2e-5
    def value(r):
        parts=[holomorphic_geometry_rows(x[:100],rho,connection_only=True)['rows']for x in r]
        keys=('connection_lambda','lambda_tau','lambda_rho')
        p=[np.array([[row[k].value for k in keys]for row in branch])for branch in parts]
        return -p[0]+p[1]
    rate=a['reference_affine_raw_rate'];fd=(value(ref+h*rate)-value(ref-h*rate))/(2*h)
    np.testing.assert_allclose(a['child_source_first'],fd,atol=2e-10,rtol=2e-6)
    assert a['actual_parent_source_motion_count']==0
    assert np.max(abs(a['full_material_field_source'][:,:,:2]))==0


def test_fixed_test_restriction_preserves_complex_source_and_complement():
    rng=np.random.default_rng(362);B=rng.normal(size=(100,64));w=np.linspace(.2,1,5)
    source=rng.normal(size=(3,5,5,4))+.4j*rng.normal(size=(3,5,5,4))
    a=fixed_radial_coefficient_test_restriction(B,w,source)
    np.testing.assert_allclose(a['test_map_identity_defect'],0,atol=3e-15)
    np.testing.assert_allclose(a['represented_source_image']+a['full_source_image_complement'],a['full_source_image'],atol=2e-15)
    np.testing.assert_allclose(a['weighted_test_complement'],0,atol=5e-14)
    b=fixed_radial_coefficient_test_restriction(B,w,(1+2j)*source)
    np.testing.assert_allclose(b['represented_source_test_coefficients'],(1+2j)*a['represented_source_test_coefficients'],atol=3e-14)
    assert np.linalg.norm(a['full_source_image_complement'])>1
