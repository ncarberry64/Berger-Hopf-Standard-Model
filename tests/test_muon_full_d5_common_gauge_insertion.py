import numpy as np
import pytest

from bhsm.interface.muon_full_d5_common_gauge_insertion import (
    common_material_gauge_maps,full_d5_gauge_spin_factors,
    apply_material_insertion,internal_material_actions,material_source_gram,
    common_source_square_action)
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_s3_discretization
from bhsm.interface.muon_parent_positive_brst_ghost import covariant_ghost_gradient_images


def fixture():
    a=scalar_s3_discretization(4)
    ids=[i for i,l in enumerate(a['real_basis_labels']) if l[0] in(1,3)]
    E=a['real_angular_derivative_matrices'][:,ids][:,:,ids]
    A=np.arange(20).reshape(5,4)/37-.2;At=np.roll(A,2,axis=0)/3;Ar=np.roll(A,1,axis=1)/5
    radial=np.array([[.7,-.31,.29],[.83,.21,-.17]])
    temporal=np.array([.69,.73,.11,-.17,.13,.19,-.23,.31])
    return a,ids,E,A,At,Ar,radial,temporal


def test_all1200_common_incidence_matches_independent_gradient_owner():
    _,_,E,A,At,Ar,r,t=fixture()
    m=common_material_gauge_maps(A,At,Ar,E,r,t)
    g=covariant_ghost_gradient_images(A,At,Ar,E,
        np.array([[t[2],t[3],t[6]],[t[4],t[5],t[7]]]),r)
    I=np.eye(400).reshape(5,80,400)
    for key,rate in(('material_value_map',0),('material_value_map_time',1),('material_value_map_radial',2)):
        literal=np.zeros((400,1200))
        ordinary=np.concatenate([rj[int(rate==2)]*I for rj in r],axis=2)
        literal[:,:800]=(t[int(rate==1)]*ordinary).reshape(400,800)
        literal[:,800:1120]=g[('value','time','radial')[rate]].reshape(400,320)
        np.testing.assert_allclose(m[key].toarray(),literal,rtol=2e-15,atol=2e-15)
        assert m[key][:,1120:].nnz==0


def test_full384_complex_source_is_independent_of_fixed_left_adjoint():
    full=full_d5_localized_lepton_trace();rng=np.random.default_rng(113)
    c={k:np.array([v],complex) for k,v in dict(lapse=1.2,radial_coframe=.9,radius=1.7,coordinate_shift=.23).items()}
    for k in tuple(c):c[k+'_first']=np.array([[.017]],complex)
    f=full_d5_gauge_spin_factors(c,full,sheet_orientation=-1)
    g=np.eye(2)[:,None,:];u=rng.normal(size=(1,3,2,4,16,2,2))+1j*rng.normal(size=(1,3,2,4,16,2,2))
    v=rng.normal(size=u.shape)+1j*rng.normal(size=u.shape)
    a=rng.normal(size=(1,5,4,1))+1j*rng.normal(size=(1,5,4,1))
    right=apply_material_insertion(a,f['spin'],f['carrier_generators'],g,u)
    left=apply_material_insertion(a,f['spin_left'],f['carrier_generators_left'],g.conj().transpose(2,1,0),v)
    # Independent dual: conjugate the fixed operator matrices, not a.
    direct=0j
    for b in range(2):
        for mu in range(5):
            for j in range(4):
                O=np.kron(f['spin'][0,b,mu],f['carrier_generators'][b,j])
                vv=v[0,:,b].reshape(3,64,2,2);uu=u[0,:,b].reshape(3,64,2,2)
                direct+=a[0,mu,j,0]*np.einsum('fiha,ij,fjha->',vv.conj(),O,uu)
    np.testing.assert_allclose(np.vdot(v,right),direct,rtol=3e-14,atol=3e-13)
    # Pairing u† A_left(a) v equals the SAME a coefficients, not their conjugates.
    expected=0j
    for b in range(2):
        for mu in range(5):
            for j in range(4):
                O=np.kron(f['spin'][0,b,mu],f['carrier_generators'][b,j]).conj().T
                expected+=a[0,mu,j,0]*np.einsum('fiha,ij,fjha->',u[0,:,b].reshape(3,64,2,2).conj(),O,v[0,:,b].reshape(3,64,2,2))
    np.testing.assert_allclose(np.vdot(u,left),expected,rtol=3e-14,atol=3e-13)
    assert abs(expected-np.conj(direct))>1e-3


def test_complete55_source_square_matches_literal_Haar_action():
    a,ids,E,A,At,Ar,radial,temporal=fixture();full=full_d5_localized_lepton_trace()
    c={k:np.array([v],complex) for k,v in dict(lapse=1.2,radial_coframe=.9,radius=1.7,coordinate_shift=.23).items()}
    for k in tuple(c):c[k+'_first']=np.array([[.017]],complex)
    f=full_d5_gauge_spin_factors(c,full,sheet_orientation=1)
    Yg=a['real_basis_values'][:,ids];Yi=a['basis_values'][:,:5];Yo=a['basis_values'];w=a['haar_weights']
    gaunt=np.einsum('p,po,ph,pk->ohk',w,Yo.conj(),Yg,Yi,optimize=True)
    rng=np.random.default_rng(531);u=rng.normal(size=(1,3,2,4,16,5,1))+1j*rng.normal(size=(1,3,2,4,16,5,1))
    maps=[common_material_gauge_maps(A,At,Ar,E,radial,temporal)]
    z=rng.normal(size=1200);material=(maps[0]['material_value_map']@z).reshape(1,5,4,20)
    T=internal_material_actions(f['spin'],f['carrier_generators'],u);G=material_source_gram(T,gaunt)
    h=common_source_square_action(z,maps,G,np.array([.83]))
    # Literal multiplication at Haar nodes, not a Gaunt/kernel contraction.
    vp=np.einsum('pk,qfbsikn->qfbspin',Yi,u);field=np.einsum('ph,qmch->qpmc',Yg,material)
    action=np.einsum('qpmc,qbmst,bcij,qfbtpjn->qfbspin',field,f['spin'],f['carrier_generators'],vp,optimize=True)
    literal=2*.83*np.einsum('p,qfbspin,qfbspin->',w,action.conj(),action).real
    np.testing.assert_allclose(z@h,literal,rtol=4e-13,atol=1e-9)
    product=apply_material_insertion(material,f['spin'],f['carrier_generators'],gaunt,u)
    assert np.linalg.norm(product[...,5:,:])>1


def test_real_base_and_owned_time_first_guards_do_not_conjugate_complex_geometry():
    full=full_d5_localized_lepton_trace()
    c={k:np.array([v],complex) for k,v in dict(lapse=1.2,radial_coframe=.9,radius=1.7,coordinate_shift=.23).items()}
    for k in tuple(c):c[k+'_first']=np.array([[.017]],complex)
    with pytest.raises(ValueError,match='orientation'):
        full_d5_gauge_spin_factors(c,full,sheet_orientation=1.7)
    c['lapse_first'][0,0]+=.001j
    with pytest.raises(ValueError,match='real finite'):
        full_d5_gauge_spin_factors(c,full,sheet_orientation=1)
    c['lapse_first']=np.array([.017])
    with pytest.raises(ValueError,match='owned time-first'):
        full_d5_gauge_spin_factors(c,full,sheet_orientation=1)
