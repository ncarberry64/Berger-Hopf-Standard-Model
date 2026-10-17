"""Representation, frame scaling and partial-jet checks; no physical H seed."""
import numpy as np
import pytest
from pathlib import Path

from bhsm.interface.muon_intrinsic_higgs_connection import (
    CHILD_PATCH, CHILD_PATCH_OWNER, mechanical_higgs_connection_two_jet,
    mechanical_higgs_connection_from_weight_jet, apply_fixed_field_connection_two_jet,
)


def arguments():
    K=np.array([[0.,-1.,0.],[1.,0.,0.],[0.,0.,0.]])
    return dict(radius=2.,radius_first=.3,radius_second=-.2,
                lambda_geom=.4,lambda_first=.07,lambda_second=-.03,
                rotation=np.eye(3),rotation_first=K,rotation_second=K@K)


def rotation(s):
    return np.array([[np.cos(s),-np.sin(s),0.],
                     [np.sin(s),np.cos(s),0.],[0.,0.,1.]])


def test_parent_unit_coframe_cancels_radius_before_density_insertion():
    data=mechanical_higgs_connection_two_jet(**arguments())
    assert data['unit_s3_coefficient']==pytest.approx(-.6)
    assert data['orthonormal_coefficient']==pytest.approx(-.3)
    assert data['unit_s3_coefficient_first']==.07
    assert data['unit_s3_coefficient_second']==-.03
    r,r1,r2=(arguments()[k] for k in ('radius','radius_first','radius_second'))
    A,A1,A2=(data[k] for k in ('orthonormal_connection','orthonormal_connection_first',
                              'orthonormal_connection_second'))
    np.testing.assert_allclose(data['unit_s3_connection'],r*A,atol=1e-15)
    np.testing.assert_allclose(data['unit_s3_connection_first'],r1*A+r*A1,atol=1e-15)
    np.testing.assert_allclose(data['unit_s3_connection_second'],r2*A+2*r1*A1+r*A2,atol=1e-15)
    other=arguments();other.update(radius=7.,radius_first=-2.,radius_second=4.)
    changed=mechanical_higgs_connection_two_jet(**other)
    for key in ('unit_s3_connection','unit_s3_connection_first','unit_s3_connection_second'):
        np.testing.assert_array_equal(changed[key],data[key])


def test_owned_child_patch_requires_explicit_provenance():
    with pytest.raises(ValueError,match='owned child'):
        mechanical_higgs_connection_two_jet(**arguments(),patch=CHILD_PATCH)
    child=mechanical_higgs_connection_two_jet(**arguments(),patch=CHILD_PATCH,
                                              child_patch_owner=CHILD_PATCH_OWNER)
    assert child['unit_s3_coefficient']==.4
    assert child['orthonormal_coefficient']==.2
    assert child['temporal_connection'] is None
    assert child['independent_u1_connection'] is None
    assert not child['full_gauge_connection_claimed']


def test_so3_and_coefficient_product_second_jet_matches_direct_application():
    base=arguments();data=mechanical_higgs_connection_two_jet(**base)
    eps=2e-4
    values=[]
    for s in (-eps,eps):
        args=base.copy()
        args.update(radius=2+.3*s-.1*s*s,radius_first=.3-.2*s,
                    lambda_geom=.4+.07*s-.015*s*s,lambda_first=.07-.03*s,
                    rotation=rotation(s),rotation_first=base['rotation_first']@rotation(s),
                    rotation_second=base['rotation_second']@rotation(s))
        values.append(mechanical_higgs_connection_two_jet(**args))
    for prefix in ('unit_s3','orthonormal'):
        key=prefix+'_connection'
        np.testing.assert_allclose((values[1][key]-values[0][key])/(2*eps),
                                   data[key+'_first'],atol=1e-8)
        np.testing.assert_allclose((values[1][key]+values[0][key]-2*data[key])/eps**2,
                                   data[key+'_second'],atol=1e-8)
        for suffix in ('','_first','_second'):
            A=data[key+suffix]
            np.testing.assert_allclose(A+A.conj().swapaxes(-1,-2),0,atol=1e-15)


def test_unit_and_physical_spatial_kinetic_pairings_agree():
    data=mechanical_higgs_connection_two_jet(**arguments())
    H=np.array([.7+.2j,-.4+.1j]);phi=np.array([.2-.3j,.5+.4j])
    app=apply_fixed_field_connection_two_jet(data,H=H,phi=phi)
    unit=np.vdot(app['spatial_Dphi_background'],app['spatial_DH_background'])
    physicalH=np.einsum('aij,j->ai',data['orthonormal_connection'],H)
    physicalphi=np.einsum('aij,j->ai',data['orthonormal_connection'],phi)
    radius=arguments()['radius'];lapse=1.3
    assert lapse*radius*unit==pytest.approx(lapse*radius**3*np.vdot(physicalphi,physicalH))
    np.testing.assert_allclose(app['delta_spatial_DH'],
                               np.einsum('aij,j->ai',data['unit_s3_connection_first'],H))
    np.testing.assert_allclose(app['second_spatial_Dphi'],
                               np.einsum('aij,j->ai',data['unit_s3_connection_second'],phi))
    assert not app['full_DH_claimed']
    assert not app['induced_H_response_included']


def test_actual_retained_geometric_jet_handoff_uses_owned_normal_index():
    from bhsm.interface.muon_moving_geometric_action import retained_state
    from bhsm.interface.muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
    q,qdot,multipliers=retained_state(Path(__file__).resolve().parents[1],side='incoming_C1_E1')
    weights=intrinsic_m4_weight_jet((len(q)-1)//3,q,qdot,multipliers)
    data=mechanical_higgs_connection_from_weight_jet(
        weights,rotation=np.eye(3),rotation_first=np.zeros((3,3)),
        rotation_second=np.zeros((3,3)))
    parent=weights['section1_orthonormal_connection_coefficient'];i=weights['source_indices'][0]
    assert data['orthonormal_coefficient']==pytest.approx(parent.value)
    assert data['orthonormal_coefficient_first']==pytest.approx(parent.gradient[i])
    assert data['orthonormal_coefficient_second']==pytest.approx(parent.hessian[i,i])
    assert not data['physical_scalar_primal_selected']


@pytest.mark.parametrize('replacement',[
    dict(radius=0.),dict(lambda_geom=1.1),dict(radius_second=np.nan),
    dict(rotation=None),dict(rotation_first=np.eye(3)),dict(rotation_second=np.eye(3)),
    dict(rotation=np.diag([1.,1.,-1.])),
])
def test_geometry_and_coframe_guards(replacement):
    args=arguments();args.update(replacement)
    with pytest.raises(ValueError):
        mechanical_higgs_connection_two_jet(**args)


def test_fixed_field_guard_requires_actual_doublet_operand():
    data=mechanical_higgs_connection_two_jet(**arguments())
    with pytest.raises(ValueError,match='explicit fixed H'):
        apply_fixed_field_connection_two_jet(data,H=None,phi=np.ones(2))
