import numpy as np
from bhsm.interface.muon_actual_normal_shape_source import mixed_normal_shape_weak_source,normal_shape_source_pairing


def test_full_mixed_shape_action_keeps_embedding_and_independent_rate():
    rng=np.random.default_rng(317);d=7
    H=rng.normal(size=(d,d))+1j*rng.normal(size=(d,d));H=(H+H.T)/2
    l=rng.normal(size=d)+1j*rng.normal(size=d);q=rng.normal(size=d)*.1+1j*rng.normal(size=d)*.1
    r=rng.normal(size=d)+1j*rng.normal(size=d)
    c=rng.normal(size=d)+1j*rng.normal(size=d);Q=rng.normal(size=(d,d))+1j*rng.normal(size=(d,d));Q=(Q+Q.T)/2
    coefficient=lambda z:(1+c@z+.5*z@Q@z,c+Q@z,Q)
    a,da,dda=coefficient(q);G=l+H@q
    psi=.7+.1j;pt=.2-.3j;s=2;v=5
    S=mixed_normal_shape_weak_source(G,H,r,a,da,dda,normal_position=s,normal_velocity=v,amplitude=psi,amplitude_coordinate_first=pt)
    def first(z,zt):
        aa,dd,_=coefficient(z);b=np.zeros(d,complex);b[s]=aa*psi;b[v]=(dd@zt)*psi+aa*pt
        return (l+H@z)@b
    dq=rng.normal(size=d)+1j*rng.normal(size=d);dr=rng.normal(size=d)+1j*rng.normal(size=d);h=1e-5
    actual=normal_shape_source_pairing(S,dq,dr)
    errors=[abs((first(q+hh*dq,r+hh*dr)-first(q-hh*dq,r-hh*dr))/(2*hh)-actual)for hh in (h,h/2)]
    assert errors[1]<1e-8
    assert errors[1]<.4*errors[0]
    assert np.linalg.norm(S['moving_embedding_action_source'])>1
    assert abs(actual-S['ordinary_action_shape_source']@dq)>1
    assert np.linalg.norm(S['full_weak_phase_rate_source'])>1


def test_literal_area_affinity_at_held_full_shape_chart():
    rng=np.random.default_rng(178);d=6
    g=rng.normal(size=d)+1j*rng.normal(size=d);ga=rng.normal(size=d)+1j*rng.normal(size=d)
    H=rng.normal(size=(d,d))+1j*rng.normal(size=(d,d));Ha=rng.normal(size=(d,d))+1j*rng.normal(size=(d,d))
    rate=rng.normal(size=d);da=rng.normal(size=d);dd=rng.normal(size=(d,d));args=dict(normal_position=1,normal_velocity=4,amplitude=1,amplitude_coordinate_first=.3)
    S=lambda g,H:mixed_normal_shape_weak_source(g,H,rate,.8+.1j,da,dd,**args)
    A,B,C=S(g,H),S(ga,Ha),S(g+.11*ga,H+.11*Ha)
    for k in ('full_weak_state_source','full_weak_phase_rate_source','shape_action_first'):
        assert np.max(abs(C[k]-A[k]-.11*B[k]))<4e-15
