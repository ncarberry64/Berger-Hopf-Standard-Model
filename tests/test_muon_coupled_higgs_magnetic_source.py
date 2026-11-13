import numpy as np
import pytest
from bhsm.interface.muon_coupled_higgs_magnetic_source import intrinsic_coupled_magnetic_source_point,VOLUME
from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_s3_discretization
from bhsm.interface.muon_parent_maxwell_corrected_retarded import _ad,higgs_u2_real_representation


def setup():
    s=scalar_s3_discretization(2);labels=s['real_basis_labels']
    ids={k:[i for i,x in enumerate(labels)if x[0]in ns]for k,ns in [('odd',(1,)),('even',(0,2))]}
    Y={k:s['real_basis_values'][:,v]for k,v in ids.items()};E={k:s['real_angular_derivative_matrices'][:,v][:,:,v]for k,v in ids.items()}
    G=np.einsum('pe,po,ps,p->eos',Y['even'],Y['odd'],Y['odd'],s['haar_weights'])
    rng=np.random.default_rng(421)
    kw=dict(weights=np.array([1.2,.8,.9]),H=np.array([.2,1.1,.1,-.3]),Hdot=np.array([.1,.2,-.1,.05]),connection=rng.normal(size=(5,4))*.1,
        odd_derivatives=E['odd'],even_derivatives=E['even'],source_derivatives=E['odd'],gaunt=G,temporal=np.array([.8,-.3,.06,.2,-.01,.1]),
        wall_radial=np.array([[.4,.1,0],[1.,.2,0]]),source_gauge=rng.normal(size=(3,5,4,4))*.1,
        source_H=rng.normal(size=(3,4,4))*.1,source_Hdot=rng.normal(size=(3,4,4))*.1,lambda_H=.7,nu_squared_action=4)
    return kw,Y,E,s['haar_weights'],rng


def literal_pair(c,n,Y,dY,H,Ht,Hi,A,t,r):
    T=higgs_u2_real_representation()['real_generators']
    ind=c[:40*n].reshape(2,5,4,n);ghost=c[40*n:56*n].reshape(2,2,4,n);scalar=c[56*n:].reshape(4,n)
    a=t[0]*np.einsum('r,rfcn,pn->pfc',r[:,0],ind,Y)
    eta=np.einsum('t,r,trcn,pn->pc',t[[2,4]],r[:,0],ghost,Y)
    etat=np.einsum('t,r,trcn,pn->pc',t[[3,5]],r[:,0],ghost,Y)
    etar=np.einsum('t,r,trcn,pn->pc',t[[2,4]],r[:,1],ghost,Y)
    etai=np.einsum('t,r,trcn,pin->pic',t[[2,4]],r[:,0],ghost,dY)
    a+=np.array([[_ad(aa)@ee for aa in row]for row,ee in zip(A,eta)])
    a[:,0]+=etat;a[:,1]+=etar;a[:,2:]+=etai
    h=t[0]*np.einsum('cn,pn->pc',scalar,Y)-np.einsum('pc,cij,pj->pi',eta,T,H)
    ht=t[1]*np.einsum('cn,pn->pc',scalar,Y)-np.einsum('pc,cij,pj->pi',etat,T,H)-np.einsum('pc,cij,pj->pi',eta,T,Ht)
    hi=t[0]*np.einsum('cn,pin->pic',scalar,dY)-np.einsum('pac,cij,pj->pai',etai,T,H)-np.einsum('pc,cij,paj->pai',eta,T,Hi)
    B=[];DH=[]
    for f in (0,2,3,4):
        B.append((ht if f==0 else hi[:,f-2])+np.einsum('pc,cij,pj->pi',A[:,f],T,h)+np.einsum('pc,cij,pj->pi',a[:,f],T,H))
        DH.append((Ht if f==0 else Hi[:,f-2])+np.einsum('pc,cij,pj->pi',A[:,f],T,H))
    return a,h,np.array(B),np.array(DH)


def test_source_derivative_matches_literal_variable_background_scalar_action():
    kw,Y,E,w,rng=setup();r=intrinsic_coupled_magnetic_source_point(**kw)
    left=rng.normal(size=600)*.03;right=rng.normal(size=240)*.03
    T=higgs_u2_real_representation()['real_generators'];Ys=Y['odd'];dYs=np.einsum('ph,ihk->pik',Ys,E['odd'])
    dy={k:np.einsum('ph,ihk->pik',Y[k],E[k])for k in Y}
    def original(axis,eps):
        H=kw['H'][None]+eps*np.einsum('pn,cn->pc',Ys,kw['source_H'][axis])
        Ht=kw['Hdot'][None]+eps*np.einsum('pn,cn->pc',Ys,kw['source_Hdot'][axis])
        Hi=eps*np.einsum('pin,cn->pic',dYs,kw['source_H'][axis])
        A=kw['connection'][None]+eps*np.einsum('pn,fcn->pfc',Ys,kw['source_gauge'][axis])
        al,hl,Bl,DH=literal_pair(left,10,Y['even'],dy['even'],H,Ht,Hi,A,kw['temporal'],kw['wall_radial'])
        ar,hr,Br,_=literal_pair(right,4,Y['odd'],dy['odd'],H,Ht,Hi,A,kw['temporal'],kw['wall_radial'])
        value=np.zeros(len(w))
        for i,mu in enumerate(kw['weights'][[0,1,1,1]]):
            f=(0,2,3,4)[i]
            contact=np.einsum('pc,cij,pj->pi',al[:,f],T,hr)+np.einsum('pc,cij,pj->pi',ar[:,f],T,hl)
            value+=(2*mu/VOLUME)*(np.sum(Bl[i]*Br[i],axis=1)+np.sum(DH[i]*contact,axis=1))
        potential=kw['lambda_H']*(4*H[:,:,None]*H[:,None,:]+2*(np.sum(H*H,axis=1)-kw['nu_squared_action'])[:,None,None]*np.eye(4))
        value+=(2*kw['weights'][2]/VOLUME)*np.einsum('pi,pij,pj->p',hl,potential,hr)
        return w@value
    for axis in range(3):
        h=1e-5;finite=(original(axis,h)-original(axis,-h))/(2*h)
        actual=left@r['intrinsic_coupled_delta_Hessian_even_odd'][axis]@right
        np.testing.assert_allclose(actual,finite,rtol=2e-8,atol=2e-12)
    assert np.min(r['dependent_gauge_scalar_rate_image_motion_norms'])>0


def test_angular_parity_magnetic_source_does_not_mean_the_green_derivative_is_zero():
    kw,_,_,_,_=setup();r=intrinsic_coupled_magnetic_source_point(**kw)
    assert r['intrinsic_coupled_delta_Hessian_even_odd'].shape==(3,600,240)
    assert np.linalg.norm(r['intrinsic_coupled_delta_Hessian_even_odd'])>.01
    assert np.linalg.norm(r['intrinsic_coupled_delta_Gram_even_odd'])>0
    assert r['bulk_YM_Lorenz_and_ghost_source_variations_not_filled_zero']


def test_point_operator_guard_keeps_actual_missing_and_complex_fields_explicit():
    kw,*_=setup();kw['source_H']=None
    with pytest.raises(ValueError,match='required'):intrinsic_coupled_magnetic_source_point(**kw)
    kw,*_=setup();kw['source_gauge']=kw['source_gauge'].astype(complex)+1j
    with pytest.raises(ValueError,match='real'):intrinsic_coupled_magnetic_source_point(**kw)
