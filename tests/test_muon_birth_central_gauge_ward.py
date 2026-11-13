import numpy as np
import pytest
from bhsm.interface.muon_parent_gauge_geometry_correction import correction_representation
from bhsm.interface.muon_birth_central_gauge_ward import represented_central_gauge_germ
from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from bhsm.interface.muon_parent_maxwell_full_weak import FIELD_ORDER


@pytest.mark.parametrize('power',[1,2])
def test_radial_gauge_parameter_and_its_derivative_are_in_the_same_trial_space(power):
    rep=correction_representation(radial_points=48,radial_order=2,cap_points=48,include_wall_lift=True)
    raw=np.zeros(228);raw[220:224]=[.2,.7,-.1,.3]
    g=represented_central_gauge_germ(raw,rep,power)
    for key in ('parameter_value_reconstruction_defect','parameter_derivative_reconstruction_defect','derivative_in_field_space_defect'):
        np.testing.assert_allclose(g[key],0,atol=2e-14,rtol=0)
    # Independent complex connection/source convention, not a gauge-Hessian assertion.
    Y=higgs_u2_real_representation()['complex_generators'][3];H=raw[220:222]+1j*raw[222:224]
    actual=g['direction'][224:226]+1j*g['direction'][226:228]
    np.testing.assert_allclose(actual,Y@H,atol=1e-16,rtol=0)
    assert np.count_nonzero(g['direction'][100:160])==3
    assert np.count_nonzero(g['direction'][160:220])==3
    # The owned field labels must be used: cancellation is literal F_tr,
    # not just a Higgs phase shift in an unchanged temporal connection.
    fields=np.einsum('rj...,j->r...',rep['gauge_basis'],g['direction'][100:160])
    rates=np.einsum('rj...,j->r...',rep['gauge_basis'],g['direction'][160:220])
    radial=np.einsum('rj...,j->r...',rep['gauge_radial_basis'],g['direction'][100:160])
    np.testing.assert_allclose(rates[:,:,1]-radial[:,:,0],0,atol=2e-14,rtol=0)
    np.testing.assert_allclose(fields[:,:,:,0:3],0,atol=0,rtol=0)
    assert not g['physical_midpoint_null_quotient_claimed']


def test_gauge_vector_field_derivative_keeps_the_off_shell_contact():
    rep=correction_representation(radial_points=24,radial_order=2,cap_points=48,include_wall_lift=True)
    raw=np.zeros(228);raw[220:224]=[.2,.7,-.1,.3];d=np.zeros(228);d[220:224]=[.4,-.3,.5,.8]
    a=represented_central_gauge_germ(raw,rep,1);eps=1e-4
    p=represented_central_gauge_germ(raw+eps*d,rep,1);m=represented_central_gauge_germ(raw-eps*d,rep,1)
    np.testing.assert_allclose(a['direction_derivative']@d,(p['direction']-m['direction'])/(2*eps),atol=3e-13,rtol=1e-12)
