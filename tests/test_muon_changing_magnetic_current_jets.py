"""CONTROL_ONLY exact mixed-image and current-chart variation checks."""
import numpy as np
from bhsm.interface.muon_changing_magnetic_current_jets import magnetic_current_angular_images,field_current_direction
from bhsm.interface.muon_coupled_higgs_magnetic_source import coupled_intrinsic_wall_images
from bhsm.interface.muon_parent_maxwell_corrected_retarded import _ad,higgs_u2_real_representation


def test_complete_even_field_times_n1_has_all_n5_current_returns():
    a=magnetic_current_angular_images();G=a['gaunt_even_odd_source']
    assert G.shape==(35,56,4)
    assert a['even_times_source_to_complete_odd_residual']<3e-14
    assert np.linalg.norm(G[:,20:])>1
    assert [l[0]for l in a['labels']['odd']].count(5)==36
    # Low even n0/n2 cannot reach n5; these are representation zeros.
    assert np.count_nonzero(G[:10,20:])==0


def test_current_dg_chart_direction_is_literal_bracket_and_higgs_variation():
    rng=np.random.default_rng(413);A=rng.normal(size=(5,4));H=rng.normal(size=4);Hd=rng.normal(size=4)
    E=np.zeros((3,1,1));tf=np.array([.6,.2,.3,.4,-.2,.7]);r=np.array([[.8,.1,.2],[.9,-.3,.4]])
    a=rng.normal(size=(5,4,1));h=rng.normal(size=(4,1));G=np.ones((1,1,1))
    base=coupled_intrinsic_wall_images(A,H,Hd,E,tf,r)
    d=field_current_direction(base,G,a,h);T=higgs_u2_real_representation()['real_generators']
    for p in range(2):
        for k in range(2):
            sl=slice(40+(2*p+k)*4,40+(2*p+k+1)*4);g=tf[2+2*p]*r[k,0]
            for f in range(5):np.testing.assert_allclose(d[4*f:4*(f+1),0,sl],g*_ad(a[f,:,0]),rtol=0,atol=1e-15)
            np.testing.assert_allclose(d[20:,0,sl],-g*np.einsum('cij,j->ic',T,h[:,0]),rtol=0,atol=1e-15)
    assert np.count_nonzero(d[:,:,:40])==0
    assert np.count_nonzero(d[:,:,56:])==0
    # Independent literal same-chart field map difference, not an inverse.
    eps=2e-5
    def values(A,H):
        b=coupled_intrinsic_wall_images(A,H,Hd,E,tf,r)
        return np.concatenate((b['gauge'].reshape(20,60),b['scalar'])).reshape(24,1,60)
    fd=(values(A+eps*a[:,:,0],H+eps*h[:,0])-values(A-eps*a[:,:,0],H-eps*h[:,0]))/(2*eps)
    np.testing.assert_allclose(d,fd,atol=1e-11,rtol=1e-10)
