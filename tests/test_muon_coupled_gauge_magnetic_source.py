import numpy as np
import pytest
from bhsm.interface.muon_coupled_gauge_magnetic_source import one_form_magnetic_source_point,integrated_lorenz_magnetic_source
from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_s3_discretization
from bhsm.interface.muon_parent_positive_brst_ghost import _linear_curvature
from bhsm.interface.muon_parent_positive_gauge_form import _weighted_curvature_maps,positive_curvature_contact_matrix
from bhsm.interface.muon_parent_maxwell_corrected_retarded import _ad,constant_angular_curvatures
from bhsm.interface.muon_matched_mechanical_source import epsilon


def setup():
    s=scalar_s3_discretization(2);labels=s['real_basis_labels'];rng=np.random.default_rng(516)
    ids={k:[i for i,x in enumerate(labels)if x[0]in ns]for k,ns in [('odd',(1,)),('even',(0,2))]}
    Y={k:s['real_basis_values'][:,v]for k,v in ids.items()};E={k:s['real_angular_derivative_matrices'][:,v][:,:,v]for k,v in ids.items()}
    G=np.einsum('pe,po,ps,p->eos',Y['even'],Y['odd'],Y['odd'],s['haar_weights'])
    kw=dict(connection=rng.normal(size=(5,4))*.1,connection_time=rng.normal(size=(5,4))*.05,
        connection_radial=rng.normal(size=(5,4))*.05,odd_derivatives=E['odd'],even_derivatives=E['even'],
        source_derivatives=E['odd'],gaunt=G,radial=np.array([[.4,.1,.02],[1.,.2,.03]]),
        metric=np.array([.9,1.2,.8,.7,.13,1.1]),densities=np.array([1.2,.8,.7,1.2*.8/.7,.13]),
        temporal=np.array([.8,-.3,.06,.2,-.01,.1]),source_gauge=rng.normal(size=(3,5,4,4))*.1,
        source_gauge_time=rng.normal(size=(3,5,4,4))*.1,source_gauge_radial=rng.normal(size=(3,5,4,4))*.1)
    return kw,Y,E,s['haar_weights'],rng


def literal_field(c,n,Y,dY,A,F,t,r):
    ind=c[:40*n].reshape(2,5,4,n);ghost=c[40*n:].reshape(2,2,4,n)
    v=t[0]*np.einsum('r,rfcn,pn->pfc',r[:,0],ind,Y)
    vt=t[1]*np.einsum('r,rfcn,pn->pfc',r[:,0],ind,Y)
    vr=t[0]*np.einsum('r,rfcn,pn->pfc',r[:,1],ind,Y)
    ev=t[0]*np.einsum('r,rfcn,pin->pifc',r[:,0],ind,dY)
    eta=np.einsum('t,r,trcn,pn->pc',t[[2,4]],r[:,0],ghost,Y)
    et=np.einsum('t,r,trcn,pn->pc',t[[3,5]],r[:,0],ghost,Y)
    er=np.einsum('t,r,trcn,pn->pc',t[[2,4]],r[:,1],ghost,Y)
    ei=np.einsum('t,r,trcn,pin->pic',t[[2,4]],r[:,0],ghost,dY)
    dg=np.array([[_ad(a)@ee for a in row]for row,ee in zip(A,eta)])
    dg[:,0]+=et;dg[:,1]+=er;dg[:,2:]+=ei
    curves=[]
    for p in range(len(Y)):
        fc=_linear_curvature(A[p],v[p,:,:,None],vt[p,:,:,None],vr[p,:,:,None],ev[p,:,:,:,None])
        gc=tuple(np.array([_ad(x)@eta[p]for x in np.atleast_2d(F[p][key])]).reshape(fc[j].shape)
            for j,key in enumerate(('Ftr','Ft','Fr','B')))
        curves.append(tuple(x+y for x,y in zip(fc,gc)))
    return v+dg,curves


def test_full_one_form_source_matches_literal_variable_angular_curvature_action():
    kw,Y,E,w,rng=setup();result=one_form_magnetic_source_point(**kw)
    left=rng.normal(size=560)*.03;right=rng.normal(size=224)*.03
    dy={k:np.einsum('ph,ihk->pik',Y[k],E[k])for k in Y}
    def action(axis,e):
        A=kw['connection'][None]+e*np.einsum('pn,fcn->pfc',Y['odd'],kw['source_gauge'][axis])
        At=kw['connection_time'][None]+e*np.einsum('pn,fcn->pfc',Y['odd'],kw['source_gauge_time'][axis])
        Ar=kw['connection_radial'][None]+e*np.einsum('pn,fcn->pfc',Y['odd'],kw['source_gauge_radial'][axis])
        da=e*np.einsum('pin,fcn->pifc',dy['odd'],kw['source_gauge'][axis]);F=[]
        for j in range(len(w)):
            f=constant_angular_curvatures(A[j],At[j],Ar[j]);f['Ft']-=da[j,:,0];f['Fr']-=da[j,:,1]
            for i,k,l in np.argwhere(epsilon()):f['B'][i]+=epsilon()[i,k,l]*da[j,k,2+l]
            F.append(f)
        vl,cl=literal_field(left,10,Y['even'],dy['even'],A,F,kw['temporal'],kw['radial'])
        vr,cr=literal_field(right,4,Y['odd'],dy['odd'],A,F,kw['temporal'],kw['radial'])
        out=[]
        for j in range(len(w)):
            l=_weighted_curvature_maps(cl[j],kw['densities']).ravel();r=_weighted_curvature_maps(cr[j],kw['densities']).ravel()
            C=positive_curvature_contact_matrix(F[j],kw['densities'],1)
            out.append(l@r+vl[j].ravel()@C@vr[j].ravel())
        return w@out
    for axis in range(3):
        h=1e-5;fd=(action(axis,h)-action(axis,-h))/(2*h)
        actual=left@result['one_form_delta_Hessian_even_odd'][axis]@right
        np.testing.assert_allclose(actual,fd,rtol=2e-8,atol=2e-12)
    assert np.linalg.norm(result['curvature_contact_delta_Hessian_even_odd'])>0
    assert np.min(result['dependent_DG_value_and_curvature_motion_norms'])>0


def test_integrated_lorenz_derivative_has_both_product_placements():
    rng=np.random.default_rng(127);n=56;ng=16
    ge=rng.normal(size=(n,n));ge=ge.T@ge+np.eye(n)
    go=rng.normal(size=(n,n));go=go.T@go+np.eye(n)
    he=np.eye(ng)*2;ho=np.eye(ng)*3;dg=rng.normal(size=(3,n,n))*.01
    r=integrated_lorenz_magnetic_source(even_one_form_Gram=ge,odd_one_form_Gram=go,
        even_ghost_Gram=he,odd_ghost_Gram=ho,delta_one_form_Gram_even_odd=dg)
    G=np.block([[ge,np.zeros_like(ge)],[np.zeros_like(go),go]])
    H=np.block([[he,np.zeros_like(he)],[np.zeros_like(ho),ho]])
    ids=np.r_[np.arange(40,56),np.arange(96,112)]
    for a in range(3):
        d=np.block([[np.zeros_like(ge),dg[a]],[dg[a].T,np.zeros_like(go)]])
        def form(e):B=(G+e*d)[ids];return B.T@np.linalg.solve(H,B)
        h=1e-4;fd=(form(h)-form(-h))/(2*h)
        np.testing.assert_allclose(r['Lorenz_delta_Hessian_even_odd'][a],fd[:56,56:],rtol=2e-10,atol=2e-11)


def test_unbound_or_complex_source_is_rejected_before_operator_application():
    kw,*_=setup();kw['source_gauge_radial']=None
    with pytest.raises(ValueError,match='required'):one_form_magnetic_source_point(**kw)
    kw,*_=setup();kw['source_gauge_time']=kw['source_gauge_time'].astype(complex)+1j
    with pytest.raises(ValueError,match='real'):one_form_magnetic_source_point(**kw)
