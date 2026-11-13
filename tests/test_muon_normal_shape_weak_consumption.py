import numpy as np
from bhsm.interface.muon_actual_normal_shape_source import mixed_normal_shape_weak_source
from bhsm.interface.muon_normal_shape_weak_consumption import integrate_shape_rate_contact,weak_shape_action_pairing


def test_actual_rate_derivative_identity_does_not_presume_equation_or_drop_faces():
    rng=np.random.default_rng(610);d=6;s=1;v=4
    G=rng.normal(size=d)+1j*rng.normal(size=d);H=rng.normal(size=(d,d))+1j*rng.normal(size=(d,d))
    Gt=rng.normal(size=d)+1j*rng.normal(size=d);rate=rng.normal(size=d);da=rng.normal(size=d)+1j*rng.normal(size=d)
    dd=rng.normal(size=(d,d))+1j*rng.normal(size=(d,d));dd=(dd+dd.T)/2
    S=mixed_normal_shape_weak_source(G,H,rate,.8+.1j,da,dd,normal_position=s,normal_velocity=v,amplitude=.9,amplitude_coordinate_first=.2)
    A=integrate_shape_rate_contact(S,G,Gt,da,dd,rate,normal_position=s,normal_velocity=v)
    assert np.max(abs(A['integrated_minus_ordinary_and_equation']))<2e-15
    assert np.linalg.norm(A['canonical_equation_shape_contact'])>.1
    # Independent time-first differentiation of g_rate=Pi_s psi Da.
    h=1e-6
    first=lambda t:(G[v]+t*Gt[v])*(.9+t*.2)*(da+t*(dd@rate))
    fd=(first(h)-first(-h))/(2*h)
    assert np.max(abs(fd-A['weak_phase_rate_source_time_first']))<2e-9
    u=rng.normal(size=(d,3));ut=rng.normal(size=(d,3))
    original=S['full_weak_state_source']@u+S['full_weak_phase_rate_source']@ut
    reduced=A['integrated_weak_bulk_source']@u+A['weak_phase_rate_source_time_first']@u+A['temporal_boundary_source_covector']@ut
    assert np.max(abs(original-reduced))<4e-15
    w=weak_shape_action_pairing([A['integrated_weak_bulk_source']],[u],[.1],
        da,u,2*da,2*u,[da],[u],[3*da],[u])
    assert np.linalg.norm(w['coefficient_corner_rate_contact'])>.1
    assert np.max(abs(w['complete_shape_action_pairing']-(.1*A['integrated_weak_bulk_source']@u+4*da@u-da@u-2*da@u)))<4e-15
