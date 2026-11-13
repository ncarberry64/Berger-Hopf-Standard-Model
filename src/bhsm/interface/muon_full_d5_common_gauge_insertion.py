"""Compact common EW4 insertions in the owned full D5 differential form.

These are coefficient/action maps on an explicit same-epoch core. They do
not choose a spectrum, statistical multiplicity, seam/exterior domain or
physical native energy continuation. Independent Higgs columns have zero
BULK gauge insertion; their surface insertion is not supplied by this map.
"""
from __future__ import annotations
import numpy as np
from scipy.sparse import csr_matrix


def common_material_gauge_maps(A, At, Ar, angular_derivatives, radial, temporal):
    """All1200 common columns, using 14 profile x4 internal x20 harmonics.

    ``temporal`` is (b,bprime,g0,g0prime,g1,g1prime,g0second,g1second).
    First is the actual coordinate-time derivative on that fixed chart;
    the ordinary tent derivative must be explicitly one-sided at its corner.
    """
    from .muon_parent_maxwell_corrected_retarded import _ad
    raw=[np.asarray(x) for x in (A,At,Ar,angular_derivatives,radial,temporal)]
    if any(np.iscomplexobj(x) and np.any(x.imag!=0) for x in raw):
        raise ValueError('the actual real common gauge/profile chart is required')
    A,At,Ar,E,r,t=[np.asarray(x.real,float) for x in raw]
    if A.shape!=(5,4) or At.shape!=A.shape or Ar.shape!=A.shape or E.shape!=(3,20,20) or r.shape!=(2,3) or t.shape!=(8,):
        raise ValueError('complete original EW4/common1200 point maps required')
    if any(not np.isfinite(x).all() for x in (A,At,Ar,E,r,t)):
        raise ValueError('finite common coefficient maps required')
    # mu, profile, angular-operator, output-adjoint, input-adjoint.
    C=np.zeros((5,14,4,4,4));Cx=C.copy();Cr=C.copy();I=np.eye(4)
    for p in range(2):
        for mu in range(5):
            C[mu,5*p+mu,0]=t[0]*r[p,0]*I
            Cx[mu,5*p+mu,0]=t[1]*r[p,0]*I
            Cr[mu,5*p+mu,0]=t[0]*r[p,1]*I
    for i in range(2):
        g,gp,gpp=t[2+2*i],t[3+2*i],t[6+i]
        for j in range(2):
            p=10+2*i+j;v,vr,vrr=r[j]
            for mu in range(5):
                C[mu,p,0]=g*v*_ad(A[mu])
                Cx[mu,p,0]=g*v*_ad(At[mu])+gp*v*_ad(A[mu])
                Cr[mu,p,0]=g*v*_ad(Ar[mu])+g*vr*_ad(A[mu])
            C[0,p,0]+=gp*v*I;Cx[0,p,0]+=gpp*v*I
            C[1,p,0]+=g*vr*I;Cx[1,p,0]+=gp*vr*I
            Cr[0,p,0]+=gp*vr*I;Cr[1,p,0]+=g*vrr*I
            for a in range(3):
                C[2+a,p,1+a]=g*v*I;Cx[2+a,p,1+a]=gp*v*I
                Cr[2+a,p,1+a]=g*vr*I
    ops=np.concatenate((np.eye(20)[None],E))
    def expand(coeff):
        # Order matches ordinary(radial,component,internal,harmonic), then
        # ghost(temporal,radial,internal,harmonic), then independent H80.
        L=np.einsum('fpaij,ahk->fihpjk',coeff,ops).reshape(400,1120)
        return csr_matrix(np.pad(L,((0,0),(0,80))))
    return dict(coefficient=C,coefficient_time=Cx,coefficient_radial=Cr,angular_operators=ops,
        material_value_map=expand(C),material_value_map_time=expand(Cx),
        material_value_map_radial=expand(Cr),
        common_dimension=1200,material_dimension=400,
        independent_H_bulk_gauge_columns_zero=True,independent_H_seam_supplied=False)


def full_d5_gauge_spin_factors(c, full, *, sheet_orientation):
    """delta A5=sum_mu spin[mu] tensor delta A_mu, with full fixed carriers."""
    eps=int(sheet_orientation)
    if eps not in(-1,1) or eps!=sheet_orientation:raise ValueError('original eta orientation +/-1 required')
    names=('lapse','radial_coframe','radius','coordinate_shift')
    raw=[np.asarray(c[k]) for k in names]
    if raw[0].ndim!=1 or len(raw[0])<1:raise ValueError('nonempty same-real-point coefficient arrays required')
    q=len(raw[0]);first=[np.asarray(c[k+'_first']) for k in names]
    if any(a.shape!=(q,) for a in raw) or any(a.shape!=(1,q) for a in first):
        raise ValueError('same q points and one explicit owned time-first slot required')
    if any(not np.isfinite(a).all() or (np.iscomplexobj(a) and np.any(a.imag!=0)) for a in raw+first):
        raise ValueError('real finite base geometry and real owned time-first required for fixed adjoint jets')
    N,C,R,z=[np.asarray(a,complex) for a in raw]
    Nx,Cx,Rx,zx=[np.asarray(a[0],complex) for a in first]
    if any(np.any(a.real<=0) for a in (N,C,R)):raise ValueError('positive original real coframe required')
    S=np.zeros((q,2,5,4,4),complex);Sx=S.copy()
    beta=np.zeros((q,2,4,4),complex);betax=beta.copy()
    gens=[]
    for b,branch in enumerate(('particle','conjugate')):
        g=np.asarray(full['gamma5D_'+branch]);I=np.eye(4)
        G=np.asarray(full['unitTr16_gauge_particle'])
        gens.append(G if b==0 else G.conj())
        K=-1j*eps*g[0]@g[4]
        S[:,b,0]=I/N[:,None,None]
        Sx[:,b,0]=-I*Nx[:,None,None]/N[:,None,None]**2
        S[:,b,1]=-z[:,None,None]*I/N[:,None,None]+K/C[:,None,None]
        Sx[:,b,1]=-(zx/N-z*Nx/N**2)[:,None,None]*I-K*Cx[:,None,None]/C[:,None,None]**2
        for a in range(3):
            K_a=-1j*g[0]@g[a+1]
            S[:,b,a+2]=K_a/R[:,None,None]
            Sx[:,b,a+2]=-K_a*Rx[:,None,None]/R[:,None,None]**2
        beta[:,b]=S[:,b,1];betax[:,b]=Sx[:,b,1]
    gen=np.array(gens)
    return dict(spin=S,spin_time=Sx,carrier_generators=gen,
        spin_left=S.conj().transpose(0,1,2,4,3),spin_left_time=Sx.conj().transpose(0,1,2,4,3),
        carrier_generators_left=gen.conj().transpose(0,1,3,2),
        material_radial_principal=beta,material_radial_principal_time=betax,
        temporal_principal=1/N,temporal_principal_time=-Nx/N**2,
        independent_source_coefficients_conjugated=False)


def apply_material_insertion(material, spin, generators, gaunt, value):
    """Full family3 x branches2 x Spin4 x SM16 action, no output projection.

    material[q,mu,c,h_source]; value[q,f,b,s,i,h_input,column].
    gaunt[h_output,h_source,h_input] covers the complete product range.
    """
    return np.einsum('qmch,qbmst,bcij,ohk,qfbtjkn->qfbsion',
        material,spin,generators,gaunt,value,optimize=True)


def internal_material_actions(spin,generators,value):
    """Twenty material gauge directions before angular multiplication."""
    a=np.einsum('qbmst,bcij,qfbtjkn->qfbmcsikn',spin,generators,value,optimize=True)
    return a.reshape(a.shape[:3]+(20,)+a.shape[5:])


def material_pairing(left, actions, gaunt):
    """Independent analytic row pairing; caller supplies dagger when intended.

    Returns q x400 x left-column x right-column. No source coefficient is
    conjugated. Both angular branches and all family contractions remain.
    """
    a=np.einsum('qfbsioa,qfbmsikn,ohk->qmh an',left,actions,gaunt,optimize=True)
    return a.reshape(a.shape[0],400,a.shape[-2],a.shape[-1])


def material_source_gram(actions,gaunt,actions_time=None,*,return_factors=False):
    """Exact compact400 square-contact matrix on all original common maps.

    It traces only the explicitly supplied trial-column Gram, with no
    heat/statistical weights. The complete product output is contracted.
    """
    angular=np.einsum('ohl,okj->hklj',gaunt.conj(),gaunt,optimize=True)
    inner=np.einsum('qfbmsila,qfbnsija->qmnl j',actions.conj(),actions,optimize=True)
    G=np.einsum('qmnl j,hklj->qmhnk',inner,angular,optimize=True).reshape(len(actions),400,400)
    if actions_time is None:return (G,dict(angular_product_Gram=angular,internal_Gram=inner)) if return_factors else G
    ix=np.einsum('qfbmsila,qfbnsija->qmnl j',actions_time.conj(),actions,optimize=True)
    ix+=np.einsum('qfbmsila,qfbnsija->qmnl j',actions.conj(),actions_time,optimize=True)
    Gx=np.einsum('qmnl j,hklj->qmhnk',ix,angular,optimize=True).reshape(len(actions),400,400)
    return (G,Gx,dict(angular_product_Gram=angular,internal_Gram=inner,internal_Gram_time=ix)) if return_factors else (G,Gx)


def common_form_pullback(material_pair, maps, weights, *, material_pair_time=None,
        weights_time=None):
    """All1200 ordered form coefficients, retaining incidence/measure jets."""
    w=np.asarray(weights);r=np.zeros((1200,)+material_pair.shape[2:],complex)
    rx=None if material_pair_time is None else np.zeros_like(r)
    for j,m in enumerate(maps):
        L=m['material_value_map'];r+=w[j]*(L.T@material_pair[j].reshape(400,-1)).reshape(r.shape)
        if rx is not None:
            Lx=m['material_value_map_time']
            rx+=(w[j]*(L.T@material_pair_time[j].reshape(400,-1))
                +w[j]*(Lx.T@material_pair[j].reshape(400,-1))
                +weights_time[j]*(L.T@material_pair[j].reshape(400,-1))).reshape(r.shape)
    return (r,rx) if rx is not None else r


def common_source_square_action(direction,maps,material_gram,weights,*,
        material_gram_time=None,weights_time=None):
    """Full1200 source-square Hessian matvec without a dense1200 tensor.

    Real common coordinates; complex analytic continuation uses the fixed
    real coefficient matrices. No symmetrization or threshold is applied.
    """
    z=np.asarray(direction)
    if z.shape!=(1200,):raise ValueError('all1200 common coefficients required')
    result=np.zeros(1200,dtype=np.result_type(z,float))
    first=None if material_gram_time is None else np.zeros_like(result)
    for j,m in enumerate(maps):
        L=m['material_value_map'];a=L@z;G=material_gram[j].real
        result+=2*weights[j]*(L.T@(G@a))
        if first is not None:
            Lx=m['material_value_map_time'];ax=Lx@z
            first+=2*(weights_time[j]*(L.T@(G@a))
                +weights[j]*(Lx.T@(G@a)+L.T@(material_gram_time[j].real@a+G@ax)))
    return (result,first) if first is not None else result
