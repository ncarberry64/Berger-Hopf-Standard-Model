"""Same-action weak graph, proper-clock and all-source-image checks."""
import numpy as np
from bhsm.interface.muon_piecewise_euclidean_action import (
    proper_euclidean_source_nodes,family_piecewise_weak_forms,positive_weak_form_factor,weak_form_heat_action)


def test_actual_source_cell_proper_clock_and_independent_reflection():
    from scripts.evaluate_muon_continued_current_factor import retained_input
    from bhsm.interface.muon_continued_action_reality import actual_source_curve_coefficients
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]
    p,_=retained_input('outgoing',{})
    data=[]
    for name in('phase','velocity','contacts'):
        with np.load(root/f'artifacts/muon_corrected_profile_magnetic_response_20261011/run_1/outgoing_{name}.npz',allow_pickle=False)as a:
            data.append({k:a[k].copy()for k in a.files})
    curves=actual_source_curve_coefficients(*data);curves={**curves,'times':curves['times'][48:50]}
    a=proper_euclidean_source_nodes(p,curves)
    assert a['source_cells']==1
    assert a['total_proper_clock']>0
    assert a['proper_clock_reflected_ODE_max']<1e-22
    assert a['reflected_body_identity_max']<2e-15
    assert a['reflected_source_identity_max']<2e-15
    assert np.max(abs(a['coordinate_offset'].imag))>1e-9


def _coefficient_nodes():
    # A declared finite algebraic control checks the action, not a primal state.
    t,w=np.polynomial.legendre.leggauss(4);t=(t+1)/2;w=w/2
    H=np.diag(np.linspace(-1.5,1.2,18)).astype(complex)
    body=np.array([H+1j*x*np.eye(18)*.03 for x in t])
    Xi=np.zeros((4,8,20,18,18),complex)
    for q in range(4):
        Xi[q,0,0]=np.eye(18)*(.1+.02j*t[q])
        Xi[q,0,7]=np.eye(18)*(.03-.01j*t[q])
    return dict(proper_time=t,weight=w,H=body,Hsharp=body.conj().swapaxes(-1,-2),
        R=np.ones(4)*(1+.02j),Rsharp=np.ones(4)*(1-.02j),Xi=Xi,Xisharp=Xi.conj().swapaxes(-1,-2),
        total_proper_clock=1.)


def test_literal_weak_action_preserves_final_natural_row_and_full_n3_image():
    from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
    data=_coefficient_nodes();a=family_piecewise_weak_forms(data,temporal_cells=2)
    assert a['source_K'].shape==(12,12)
    assert a['target_K'].shape==(240,240)
    assert a['full20angular_source_image_retained']
    assert a['reflected_full_body_identity_max']<2e-15
    assert np.linalg.norm(a['target_K'][-120:])>1
    # A literal independent kinetic norm reproduces the source action.
    rng=np.random.default_rng(71);u=rng.normal(size=(2,6))+1j*rng.normal(size=(2,6))
    total=0.
    fi=a['family_indices']
    for q,t in enumerate(data['proper_time']):
        if t<.5:
            value=2*t*u[0];derivative=2*u[0]
        else:
            s=2*t-1;value=(1-s)*u[0]+s*u[1];derivative=2*(u[1]-u[0])
        application=derivative+data['H'][q][np.ix_(fi,fi)]@value
        total+=data['weight'][q]*np.vdot(application,application).real
    np.testing.assert_allclose(np.vdot(u.ravel(),a['source_K']@u.ravel()).real,total,atol=4e-14)
    assert np.linalg.norm(a['magnetic_delta_K'][0])>.1
    # The n3 source is retained rather than folded into the n1 image.
    assert np.linalg.norm(a['magnetic_delta_numerator'][0].reshape(2,6,20,6)[:,:,7])>.001
    s=positive_weak_form_factor(a['source_K'],a['source_M'])
    response=weak_form_heat_action(s,a['source_numerator'],0.)
    np.testing.assert_allclose(a['source_K']@response,a['source_numerator'],atol=4e-15)


def test_piecewise_weak_frame_corner_traces_are_single_shared_unknowns():
    from bhsm.interface.muon_piecewise_euclidean_action import _basis
    total=1.;cells=4
    left=_basis(.5-1e-12,total,cells);right=_basis(.5+1e-12,total,cells)
    l={i:v for i,v,d in left};r={i:v for i,v,d in right}
    assert l[1]>.99999999 and r[1]>.99999999
    # The final value is free, so its last weak row carries the conormal.
    assert _basis(1.,total,cells)[-1][:2]==(3,1.)
