"""Ordered event reconstruction and complete coordinate contact checks."""
import numpy as np
import pytest
from scipy.linalg import expm, expm_frechet

from bhsm.interface.muon_d5_affine_event_trace_application import (
    parent_trace_coordinates, reconstruct_child_trace_jet,
    complete_parent_pullback_first,
)


def test_child_reconstruction_preserves_noncommutative_density_bundle_order():
    rng=np.random.default_rng(773)
    maps=[np.eye(4)+.12*rng.normal(size=(4,4)) for _ in range(4)]
    first=[.1*rng.normal(size=(4,4)) for _ in range(4)]
    q=rng.normal(size=(4,7));qx=rng.normal(size=q.shape)
    S,D,K,P=maps;Sx,Dx,Kx,Px=first
    value,derivative=reconstruct_child_trace_jet(q,qx,
        child_spin=S,child_spin_first=Sx,child_density=D,child_density_first=Dx,
        middle_lift=K,middle_lift_first=Kx,parent_density=P,parent_density_first=Px)
    # Original coordinate definition, with all noncommuting factors retained.
    recovered=np.linalg.solve(P,np.linalg.solve(K,D@np.linalg.solve(S,value)))
    np.testing.assert_allclose(recovered,q,atol=2e-15)
    h=2e-6
    def direct(e):
        return (S+e*Sx)@np.linalg.solve(D+e*Dx,(K+e*Kx)@(P+e*Px)@(q+e*qx))
    np.testing.assert_allclose(derivative,(direct(h)-direct(-h))/(2*h),atol=6e-10)
    assert np.linalg.norm(value-S@K@np.linalg.solve(D,P@q))>.01


def test_total_parent_pullback_includes_moving_point_and_frame_once():
    rng=np.random.default_rng(774)
    A,B,C=[.1*rng.normal(size=(4,4)) for _ in range(3)]
    P,T,R,X=[rng.normal(size=(4,5)) for _ in range(4)]
    t,r=.13,.27;dt,dr=.21,-.16
    V=P+t*T+r*R
    Z=t*A+r*B
    S=expm(Z);Sx=expm_frechet(Z,C,compute_expm=False)
    St=expm_frechet(Z,A,compute_expm=False)
    Sr=expm_frechet(Z,B,compute_expm=False)
    operand=dict(value=V,source=X,time=T,radial=R,
        time_source=np.zeros_like(V),radial_source=np.zeros_like(V))
    q=parent_trace_coordinates(operand,S,Sx,St)
    actual=complete_parent_pullback_first(q['value'],q['source'],q['time'],
        q['radial_fixed_frame'],event_time_first=dt,event_radius_first=dr,
        radial_frame_connection=np.linalg.solve(S,Sr))
    def direct(e):
        tp,rp=t+e*dt,r+e*dr
        return np.linalg.solve(expm(tp*A+rp*B+e*C),P+tp*T+rp*R+e*X)
    h=2e-6
    np.testing.assert_allclose(actual,(direct(h)-direct(-h))/(2*h),atol=3e-10)
    assert np.linalg.norm(actual-(q['source']+q['time']*dt+q['radial_fixed_frame']*dr))>1e-3


def test_full_ambient_homogeneous_basis_is_not_identified_with_material_frame():
    rng=np.random.default_rng(775)
    S=expm(.1*rng.normal(size=(6,6)))
    Eta=expm(.13*rng.normal(size=(6,6)))
    source=.07*rng.normal(size=(6,6));St=.05*rng.normal(size=(6,6))
    q=parent_trace_coordinates(dict(value=Eta,source=source,time=source,
        radial=source,time_source=source,radial_source=source),S,St,St)
    assert np.linalg.norm(q['value']-np.eye(6))>.1
    np.testing.assert_allclose(S@q['value'],Eta,atol=3e-16)
    np.testing.assert_allclose(S@q['source']+St@q['value'],source,atol=2e-16)


def test_physical_frame_contact_and_every_trace_source_slot_are_required():
    z=np.zeros((3,4));I=np.eye(3)
    with pytest.raises(ValueError,match='source gradients'):
        parent_trace_coordinates(dict(value=z,source=z,time=z,radial=z),I,I,I)
    with pytest.raises(ValueError,match='radial frame'):
        complete_parent_pullback_first(z,z,z,z,event_time_first=0.,event_radius_first=0.,
            radial_frame_connection=None)
