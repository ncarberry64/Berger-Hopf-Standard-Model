import numpy as np
from scipy.linalg import expm

from bhsm.interface.muon_parent_gauge_geometry_correction import (
    ROOT,retained_state,correction_representation,coupled_sector_application,
)
from bhsm.interface.muon_finite_orientation_ward import orientation_coefficient_generators,recorded_orientation_ward_application


def test_constant_orientation_symmetry_and_offshell_Ward_from_literal_action():
    rep=correction_representation(time_points=3,radial_points=12,radial_order=1,cap_points=12,
        include_wall_lift=True,include_scalar_mean=True)
    c=np.zeros(rep['count']);c[62:rep['scalar_start']]=.01*np.sin(np.arange(rep['gauge_count']))
    c[-8:]=[.003,-.002,.005,.001,.2,.8,.1,-.2]
    ref=retained_state(ROOT);parameters=dict(nu_squared_action=4.,surface_gamma=.002)
    center=coupled_sector_application(c,rep,ref,**parameters)
    result=recorded_orientation_ward_application(c,center['residual'],center['hessian'],rep['gauge_labels'],rep['scalar_count'])
    assert result['first_Ward_defect_max']<1e-13
    assert result['differentiated_Ward_defect_norm']<1e-9
    generators=orientation_coefficient_generators(rep['gauge_labels'],rep['scalar_count'])
    rotation=expm(.13*generators[0]-.09*generators[1]+.05*generators[2]+.07*generators[3])
    moved=coupled_sector_application(rotation@c,rep,ref,**parameters)
    np.testing.assert_allclose(moved['value'],center['value'],rtol=2e-13,atol=1e-15)
    np.testing.assert_allclose(moved['residual'],rotation@center['residual'],rtol=2e-10,atol=1e-11)


def test_orientation_generators_preserve_geometry_and_all_gauge_gauss_components():
    rep=correction_representation(radial_order=2,include_wall_lift=True,include_scalar_mean=True)
    g=orientation_coefficient_generators(rep['gauge_labels'],rep['scalar_count'])
    np.testing.assert_array_equal(g[:,:62],0.)
    np.testing.assert_array_equal(g[:,:,:62],0.)
    np.testing.assert_allclose(g+g.transpose(0,2,1),0.,atol=1e-15)
    # At and Ar transform nontrivially; no Gauss coordinate is silently removed.
    assert np.linalg.norm(g[:,62:70,62:70])>0
