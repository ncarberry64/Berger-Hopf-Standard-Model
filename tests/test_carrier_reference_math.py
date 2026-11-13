import numpy as np
import pytest
from scipy.linalg import sqrtm

from bhsm.interface.carrier_reference_math import (
    gram_sqrt_jet, positive_projector_jet, unrestricted_affine_car_range,
)


def test_projector_jet_handles_same_sign_degeneracy_and_noncommuting_motion():
    h=np.diag([-2,-2,3,3]).astype(complex)
    dh=np.array([[1,2j,0.3,0.4],[-2j,0,0.6j,0.2],[0.3,-0.6j,1,0.1],[0.4,0.2,0.1,-1]])
    p,dp,gap=positive_projector_jet(h,dh)
    assert gap==2
    np.testing.assert_allclose(p@dp+dp@p,dp,atol=0)
    np.testing.assert_allclose(h@dp-dp@h+dh@p-p@dh,0,atol=1e-16)
    step=1e-4
    pp=positive_projector_jet(h+step*dh,dh)[0]
    pm=positive_projector_jet(h-step*dh,dh)[0]
    np.testing.assert_allclose((pp-pm)/(2*step),dp,atol=5e-10,rtol=0)
    with pytest.raises(ValueError,match='gap'):
        positive_projector_jet(np.diag([0,1]),np.eye(2))


def test_positive_gram_root_sylvester_and_literal_derivative():
    g=np.array([[2,0.3j],[-0.3j,1]])
    dg=np.array([[0.1,0.4+0.2j],[0.4-0.2j,-0.2]])
    root,dr=gram_sqrt_jet(g,dg)
    np.testing.assert_allclose(root@root,g,atol=1e-15)
    np.testing.assert_allclose(root@dr+dr@root,dg,atol=4e-16)
    h=1e-4
    np.testing.assert_allclose((sqrtm(g+h*dg)-sqrtm(g-h*dg))/(2*h),dr,atol=8e-11,rtol=0)
    with pytest.raises(ValueError,match='Hermitian'):
        gram_sqrt_jet([[1,2],[0,3]],np.eye(2))
    with pytest.raises(ValueError,match='positive'):
        gram_sqrt_jet(np.diag([0,1]),np.eye(2))


@pytest.mark.parametrize('scale',[1.0,1e-13,1e-18])
def test_car_extrema_preserve_small_odd_spectrum(scale):
    m=np.diag([scale,-scale]); j=np.array([[0,1],[1,0]])
    result=unrestricted_affine_car_range(m,j)
    for key,endpoint in [('C_minus','lower'),('C_plus','upper')]:
        c=result[key]
        np.testing.assert_allclose(c+j@c.conj()@j.T,np.eye(2),atol=0)
        assert np.trace(m@c).real==pytest.approx(result[endpoint],rel=2e-15,abs=0)
    # The supplied thresholded witness I/2 fails this exact tiny-spectrum case.
    if scale==1e-13:
        assert np.trace(m@np.eye(2)/2)==0 and result['upper']==scale


def test_car_is_basis_covariant_for_antiunitary_involution():
    u=np.array([[1,1j],[1j,1]])/np.sqrt(2)
    m=np.diag([0.3,-0.3]); j=np.array([[0,1],[1,0]])
    first=unrestricted_affine_car_range(m,j)
    second=unrestricted_affine_car_range(u@m@u.conj().T,u@j@u.T)
    np.testing.assert_allclose(second['C_plus'],u@first['C_plus']@u.conj().T,atol=4e-16)
    assert second['upper']==pytest.approx(first['upper'])


def test_roundoff_even_nullspace_cannot_create_car_invalid_witness():
    with pytest.raises(ValueError,match='witnesses unresolved'):
        unrestricted_affine_car_range(np.eye(2),(1+1e-14)*np.array([[0,1],[1,0]]))
