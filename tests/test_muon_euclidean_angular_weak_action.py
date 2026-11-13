"""Independent whole-image/dual/current tests; controls are not primal data."""
import numpy as np
from bhsm.interface.muon_piecewise_euclidean_action import FAMILY_INDICES,family_piecewise_weak_forms,_basis
from bhsm.interface.muon_euclidean_angular_weak_action import (
    angular_action_coefficients,angular_magnetic_coefficients,angular_weak_square,
    angular_weak_square_contact,angular_current_moments,angular_current_contact_moments)


def test_holomorphic_vertices_are_literal_action_derivatives_with_reflected_reality():
    from bhsm.interface.muon_euclidean_angular_weak_action import euclidean_open_action_vertices
    from bhsm.interface.muon_magnetic_open_lepton_vertex import canonical_open_field_vertices
    from bhsm.interface.muon_continued_action_reality import _higgs_mass_realified
    fi=FAMILY_INDICES[1];R,N=.97+.01j,.73-.02j
    a=euclidean_open_action_vertices(R,N);sharp=euclidean_open_action_vertices(R.conjugate(),N.conjugate())
    np.testing.assert_allclose(sharp['vertices'],a['vertices'].conj().swapaxes(-1,-2),atol=1e-16)
    real=canonical_open_field_vertices(.97,.73)
    expected=np.concatenate((real['gauge'].reshape(20,18,18),real['scalar']))[:,fi][:,:,fi]
    np.testing.assert_array_equal(euclidean_open_action_vertices(.97,.73)['vertices'],expected)
    direction=np.array([.2+.1j,-.3+.4j,.11-.2j,.5+.07j])
    result=np.einsum('a,aij->ij',direction,a['scalar'])
    np.testing.assert_allclose(result,_higgs_mass_realified(direction)[np.ix_(fi,fi)],atol=1e-18)
    assert not a['electric_charge_inserted_again']


def test_executed_field_branches_reproduce_actual_Xi_without_extra_temporal_rotation():
    from pathlib import Path
    from scripts.evaluate_muon_continued_current_factor import retained_input
    from bhsm.interface.muon_continued_action_reality import actual_source_curve_coefficients
    from bhsm.interface.muon_piecewise_euclidean_action import proper_euclidean_source_nodes
    from bhsm.interface.muon_euclidean_angular_weak_action import euclidean_node_field_images,euclidean_open_action_vertices
    root=Path(__file__).resolve().parents[1];phase,_=retained_input('outgoing',{});data=[]
    for name in('phase','velocity','contacts'):
        with np.load(root/f'artifacts/muon_corrected_profile_magnetic_response_20261011/run_1/outgoing_{name}.npz',allow_pickle=False)as a:
            data.append({k:a[k].copy()for k in a.files})
    curves=actual_source_curve_coefficients(*data);curves={**curves,'times':curves['times'][48:50]}
    nodes=proper_euclidean_source_nodes(phase,curves,family_indices=FAMILY_INDICES[1])
    fields=euclidean_node_field_images(phase,curves,nodes)
    assert fields['reflected_wall_identity_max']==0
    assert fields['reflected_H_identity_max']==0
    for q in range(len(nodes['weight'])):
        vertices=euclidean_open_action_vertices(fields['R'][q],fields['N'][q])['vertices']
        coeff=np.concatenate((fields['source_wall'][q].reshape(3,20,20),fields['source_H_realified'][q]),axis=1)
        Xi=np.einsum('ach,cij->ahij',coeff,vertices)
        np.testing.assert_allclose(Xi,nodes['Xi'][q],rtol=2e-14,atol=2e-18)
        np.testing.assert_allclose(fields['source_H_Euclidean_proper_rate'][q],
            -1j*fields['source_H_coordinate_rate'][q]/fields['N'][q],atol=1e-18)


def _nodes():
    t,w=np.polynomial.legendre.leggauss(6);t=(t+1)/2;w=w/2
    H=np.diag(np.linspace(-1.3,1.1,6)).astype(complex)
    body=np.array([H+1j*x*.04*np.eye(6)for x in t])
    rng=np.random.default_rng(38);X=rng.normal(size=(6,3,20,6,6))*.015
    X=X+1j*rng.normal(size=X.shape)*.012
    return dict(proper_time=t,weight=w,H=body,Hsharp=body.conj().swapaxes(-1,-2),
        R=np.ones(6)*(1+.02j),Rsharp=np.ones(6)*(1-.02j),Xi=X,Xisharp=X.conj().swapaxes(-1,-2),
        source_axes=np.arange(3),lepton_indices=FAMILY_INDICES[1],total_proper_clock=1.)


def test_general_angular_producer_reproduces_full20_owned_source_image_and_numerator():
    from bhsm.interface.muon_changing_magnetic_current_jets import magnetic_current_angular_images
    from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
    nodes=_nodes();old=family_piecewise_weak_forms(nodes,temporal_cells=2)
    source=angular_action_coefficients(nodes,np.zeros((3,1,1)))
    target=angular_action_coefficients(nodes,magnetic_current_angular_images()['derivatives']['field_odd'])
    G=np.eye(20)[:,None,:];mag=angular_magnetic_coefficients(nodes,G)
    S=angular_weak_square(nodes,source,temporal_cells=2)
    T=angular_weak_square(nodes,target,temporal_cells=2)
    D=angular_weak_square_contact(nodes,source,target,mag,temporal_cells=2)
    for a,b in((S['K'],old['source_K']),(T['K'],old['target_K']),
               (S['M'],old['source_M']),(T['M'],old['target_M']),(D,old['magnetic_delta_K'])):
        np.testing.assert_allclose(a,b,rtol=2e-14,atol=2e-14)
    fi=FAMILY_INDICES[1];Q=-lepton_current_hilbert_representation()['EM_charge'][np.ix_(fi,fi)]
    R=np.broadcast_to(Q,(6,6,6));L=R.copy()
    moments=angular_current_moments(nodes,source,R,L,temporal_cells=2)
    contact=angular_current_contact_moments(nodes,source,target,mag,R,np.zeros((6,3,120,6)),temporal_cells=2)
    np.testing.assert_allclose(moments['numerator'],old['source_numerator'],atol=1e-14)
    np.testing.assert_allclose(moments['left_current'],old['current_target'],atol=1e-14)
    np.testing.assert_allclose(contact,old['magnetic_delta_numerator'],atol=1e-14)
    assert mag['reverse_dual_identity_max']<1e-16


def test_both_square_contacts_equal_independent_literal_full_action_differentiation():
    nodes=_nodes();source=angular_action_coefficients(nodes,np.zeros((3,1,1)))
    target=angular_action_coefficients(nodes,np.zeros((3,2,2)))
    G=np.zeros((2,1,20));G[0,0,0]=1;G[1,0,7]=.7
    mag=angular_magnetic_coefficients(nodes,G)
    delta=angular_weak_square_contact(nodes,source,target,mag,temporal_cells=2)[0]
    rng=np.random.default_rng(13);us=rng.normal(size=(2,6))+1j*rng.normal(size=(2,6))
    ut=rng.normal(size=(2,12))+1j*rng.normal(size=(2,12));literal=0j
    for q,t in enumerate(nodes['proper_time']):
        vs=np.zeros(6,complex);ds=vs.copy();vt=np.zeros(12,complex);dt=vt.copy()
        for j,p,d in _basis(t,1.,2):vs+=p*us[j];ds+=d*us[j];vt+=p*ut[j];dt+=d*ut[j]
        As=ds+source['forward'][q]@vs;At=dt+target['forward'][q]@vt
        literal+=nodes['weight'][q]*(np.vdot(At,mag['forward'][q,0]@vs)
                                   +np.vdot(mag['reverse'][q,0]@vt,As))
    np.testing.assert_allclose(np.vdot(ut.ravel(),delta@us.ravel()),literal,atol=2e-14)


def test_independent_left_current_is_not_conjugated_and_rectangular_right_motion_is_kept():
    nodes=_nodes();source=angular_action_coefficients(nodes,np.zeros((3,1,1)))
    target=angular_action_coefficients(nodes,np.zeros((3,2,2)))
    G=np.zeros((2,1,20));G[:,0,0]=[1,.5];mag=angular_magnetic_coefficients(nodes,G)
    R=np.ones((6,6,1),complex)*(1+.3j);L=np.ones((6,1,6),complex)*(2-.7j)
    dR=np.ones((6,3,12,1),complex)*(.2+.4j)
    result=angular_current_moments(nodes,source,R,L,temporal_cells=2)
    contact=angular_current_contact_moments(nodes,source,target,mag,R,dR,temporal_cells=2)
    assert np.max(abs(result['left_current'].imag))>.1
    assert np.linalg.norm(contact)>1
    direct=np.zeros((3,24,1),complex)
    for q,t in enumerate(nodes['proper_time']):
        for j,p,d in _basis(t,1.,2):
            dual=d*np.eye(12)+p*target['reflected'][q]
            for a in range(3):direct[a,j*12:(j+1)*12]+=nodes['weight'][q]*(dual@dR[q,a]+p*mag['reflected_reverse_dual'][q,a]@R[q])
    np.testing.assert_allclose(contact,direct,atol=1e-14)
