import numpy as np
import pytest
from bhsm.interface.muon_finite_normal_worldvolume_jacobi import warped_worldtube_curvature,finite_normal_worldvolume_jacobi


def test_round_static_worldtube_has_owned_negative_curvature_term():
    R=2.3;a=warped_worldtube_curvature(np.diag([1.,-1.]),np.zeros((2,2,2)),np.zeros((2,2,2,2)),
        [(R,np.array([0.,1.]),np.zeros((2,2)),3)],wall_rate=0.,wall_acceleration=0.)
    np.testing.assert_allclose(a['constant_normal_curvature_coefficient'],-3/R**2,rtol=1e-15)
    np.testing.assert_allclose(a['ambient_Ric_normal_normal'],0.,atol=0.)
    np.testing.assert_allclose(a['outward_unit_normal'],[0.,1.],atol=0.)


def test_shift_coordinate_change_preserves_static_worldtube_curvature():
    R=1.8;beta=.31;g=np.array([[1-beta**2,-beta],[-beta,-1.]])
    a=warped_worldtube_curvature(g,np.zeros((2,2,2)),np.zeros((2,2,2,2)),
        [(R,np.array([beta,1.]),np.zeros((2,2)),3)],wall_rate=-beta,wall_acceleration=0.)
    np.testing.assert_allclose(a['constant_normal_curvature_coefficient'],-3/R**2,rtol=1e-15)
    np.testing.assert_allclose(a['induced_lapse'],1.,rtol=1e-15)


def test_rindler_acceleration_retained_separately_from_ambient_ricci():
    R=1.7;g=np.diag([R**2,-1.]);dg=np.zeros((2,2,2));ddg=np.zeros((2,2,2,2))
    dg[0,0,1]=2*R;ddg[0,0,1,1]=2.
    a=warped_worldtube_curvature(g,dg,ddg,[(1.,np.zeros(2),np.zeros((2,2)),3)],wall_rate=0.,wall_acceleration=0.)
    np.testing.assert_allclose(a['ambient_Ric_normal_normal'],0.,atol=2e-16)
    np.testing.assert_allclose(a['principal_curvatures'][0],1/R,rtol=1e-15)
    np.testing.assert_allclose(a['constant_normal_curvature_coefficient'],-1/R**2,rtol=1e-15)


@pytest.mark.parametrize('stratum',['M8','M5'])
def test_actual_nonzero_finite_normal_wall_is_timelike_and_oriented(stratum):
    with np.load('artifacts/muon_inherited_finite_normal_phase_20261011/run_1/application.npz',allow_pickle=False)as z:
        raw=z['stage_independent_raw'][0]
    a=finite_normal_worldvolume_jacobi(raw,stratum=stratum)
    assert a['wall_coordinate']!=np.pi/4
    np.testing.assert_allclose(a['normal_norm'],-1.,atol=3e-16)
    np.testing.assert_allclose(a['normal_tangent_pairing'],0.,atol=1e-16)
    assert len(a['principal_curvatures'])==(3 if stratum=='M8'else 2)
    assert not a['complete_J_principal_operator_or_bulk_impedance_or_formation_selected']
