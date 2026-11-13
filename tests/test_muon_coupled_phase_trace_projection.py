import numpy as np
from bhsm.interface.muon_coupled_phase_trace_projection import (
    coupled_phase_trace_projection, coupled_phase_trace_parameter,
)


def _example(parameter=0.):
    # v3,y2 with the fifth, named gauge direction exact. The active y
    # self block changes both the implicit response and source derivative.
    D=np.zeros((5,5),complex)
    D[:4,:4]=np.array([[4,1,.3,.7],[1,3,.2,-.6],[.3,.2,2,.5],[.7,-.6,.5,-1.5]],complex)
    D[:4,:4]+=1j*np.array([[.1,.2,0,.03],[.2,-.1,.07,0],[0,.07,.2,.04],[.03,0,.04,.1]])
    dD=np.zeros_like(D);dD[3,3]=.9+.4j;dD[0,3]=dD[3,0]=.2-.1j
    E=np.array([[1,0,0,0,0],[0,1,0,0,0]],complex)
    dE=np.zeros_like(E);dE[0,2]=.13+.07j
    F=np.array([[0,0,0,0,1]],complex);dF=np.zeros_like(F);dF[0,2]=-.06+.02j
    theta=np.array([.5+.7j,-.2+.1j,.3-.4j,0,0]);dt=np.array([.1-.2j,0,.07j,0,0])
    common=np.array([[1],[1]],complex)
    return (D+parameter*dD,E+parameter*dE,F+parameter*dF,theta+parameter*dt,common),(dD,dE,dF,dt)


def test_full_algebraic_response_and_every_original_trace_frame_row():
    args,_=_example();a=coupled_phase_trace_projection(*args)
    np.testing.assert_allclose(a['saddle_rows'],0,atol=2e-15)
    np.testing.assert_allclose(a['analytic_adjoint_rows'],0,atol=2e-15)
    np.testing.assert_allclose(a['original_phase_rows'],0,atol=2e-15)
    np.testing.assert_allclose(a['reduced_action_border_identity'],0,atol=2e-15)
    assert np.linalg.norm(a['phase_lift'][3])>.1
    # Holding y fixed fails the actual algebraic variation of this action.
    D,E,F,theta,common=args;held=D.copy();held[3,:]=held[:,3]=0;held[3,3]=1
    wrong=coupled_phase_trace_projection(held,E,F,theta,common)
    assert np.linalg.norm(D[3]@wrong['phase_lift'])>.5
    assert a['raw_action_dual_conjugated'] is False


def test_full_Lyy_source_and_moving_trace_frame_contacts_match_complex_action():
    args,(dD,dE,dF,dt)=_example();a=coupled_phase_trace_projection(*args)
    d=coupled_phase_trace_parameter(a,dD,dt,dE,dF)
    h=2e-5
    p=coupled_phase_trace_projection(*_example(h)[0]);m=coupled_phase_trace_projection(*_example(-h)[0])
    np.testing.assert_allclose(d['common_trace_cotangent_parameter'],
        (p['common_trace_cotangent']-m['common_trace_cotangent'])/(2*h),rtol=3e-9,atol=2e-11)
    np.testing.assert_allclose(d['cotangent_dual_identity_rows'],0,atol=2e-16)
    np.testing.assert_allclose(d['parameter_saddle_rows'],0,atol=4e-16)
    omitted=dD.copy();omitted[3,3]=0
    wrong=coupled_phase_trace_parameter(a,omitted,dt,dE,dF)
    assert np.linalg.norm(wrong['common_trace_cotangent_parameter']-d['common_trace_cotangent_parameter'])>1e-3
    # A Hilbert-conjugated face is an explicitly different application.
    hilbert=a['common_trace_map'].conj().T@(a['phase_lift'].conj().T@args[3])
    assert np.linalg.norm(hilbert-a['common_trace_cotangent'])>1e-2
