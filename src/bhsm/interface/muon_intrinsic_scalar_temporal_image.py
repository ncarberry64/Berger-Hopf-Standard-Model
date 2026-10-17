"""Exact temporal Yukawa source image in the reached finite scalar graph.

The scalar starting trial remains the retained tent b.  Multiplying it
by the external tent produces b^2, so only the internal fermion trial is
enlarged to span{b,b^2}.  The complete positive quadratic form retains
the derivative images b' and (b^2)' through their exact Gram.  Their
orthogonality to this reflection-even trial is not full Dirac-domain
closure.  No elliptic square root of a super-Hessian is selected here.
"""
from __future__ import annotations

from fractions import Fraction
import math
import numpy as np
from scipy.linalg import eigh
from flint import arb,ctx

from .muon_magnetic_mixed_green import _finite,_positive
from .muon_common_cutoff_green_kernel import (
    common_total_cutoff_green_kernel,contraction_series_tail_upper,
    outward_positive_product_sum,
)
from .muon_intrinsic_scalar_regulator_correction import (
    scalar_reduced_kernel,two_green_regulator_correction,
)


def temporal_yukawa_source_image():
    """Exact dimensionless moments on one existing Dirichlet tent cell."""
    M=np.array([[1/3,1/4],[1/4,1/5]],float)
    D=np.array([[4,4],[4,16/3]],float)
    T=np.array([1/4,1/5],float)
    eigenvalues,U=eigh(D,M)
    vertices=math.sqrt(3)*U.T@T
    return dict(Gram=M,derivative_Gram=D,external_source_pairing=T,
        temporal_eigenvalues=eigenvalues,temporal_eigenvectors=U,
        normalized_vertex_coefficients=vertices,
        original_vertex_moment=3/4,
        exact_moments=dict(Gram=[['1/3','1/4'],['1/4','1/5']],
            derivative_Gram=[['4','4'],['4','16/3']],source_pairing=['1/4','1/5'],
            kinetic_eigenvalues=['(208-32*sqrt(31))/3','(208+32*sqrt(31))/3'],
            full_source_normalized_norm_squared='3/5',
            original_projection_normalized_norm_squared='9/16',
            omitted_source_norm_squared_fraction='1/16'),
        source_image_identity='b_external*b_scalar=b^2 in the enlarged internal fermion trial',
        derivative_images=['bprime','2*b*bprime'],
        mixed_derivative_moments=np.zeros((2,2)),
        mixed_derivative_zero_reason='every trial is reflection-even and every derivative is reflection-odd on this constant-coefficient cell',
        derivative_source_norm_squared='integral |(b^2)prime|^2=16/(3*L)',
        differential_image_orthogonality_is_full_domain_closure=False,
        source_norm_fraction_is_Pauli_error=False)


def _pair_midpoint_error(arrays,pair):
    """Outward kernel midpoint error for the exact stored positive spectra.

    Symmetry cancels the linear term of the repeated pair.  The positive
    Laplace representation and cosh bound give
    |L3(a+d,a-d,z)-L3(a,a,z)| <= d^2/(min(a+d,a-d)^4*z).
    Dropping the total-time cutoff only increases this bound.
    """
    x,y=(arrays[i] for i in pair);z=arrays[3-sum(pair)]
    low=min(float(np.min(x)),float(np.min(y)))
    high=max(float(np.max(x)),float(np.max(y)))
    with ctx.workprec(192):
        bound=((arb(high)-arb(low))/2)**2/(arb(low)**4*arb(float(np.min(z))))
        return 0. if bound.is_zero() else float(np.nextafter(float(bound.upper()),np.inf))


def temporal_image_green_kernel(*eigenvalues,cutoff,terms=6):
    """Common-total kernels for the two reached temporal kinetic branches.

    Near spectra reuse the retained outward series.  Wide two-point
    kernels use their stable exact algebraic identity.  Wide triples
    repeat the close pair at its midpoint, with a separately outward
    Laplace error bound; their binary evaluation error is not enclosed.
    """
    if len(eigenvalues) not in (2,3):raise ValueError('two or three Green factors required')
    arrays=np.broadcast_arrays(*[_finite(x,'actual positive spectrum',real=True) for x in eigenvalues])
    c=_positive(cutoff,'explicit common cutoff',zero=True)
    if any(np.any(a<=0) for a in arrays):raise ValueError('positive actual spectra required')
    if type(terms) is not int or not 2<=terms<=12:raise ValueError('resolved series order required')
    if c==0:return dict(value=1/np.prod(np.stack(arrays),axis=0),kernel_approximation_upper=0.,method='exact zero-cutoff product')
    high=np.maximum.reduce(arrays)
    if max(float(np.max((high-a)/high)) for a in arrays)<=.125:
        r=common_total_cutoff_green_kernel(*arrays,cutoff=c,terms=terms)
        return dict(value=r['value'],kernel_approximation_upper=r['positive_series_truncation_upper'],method='retained near-spectrum positive series')
    if len(arrays)==2:
        p,q=arrays
        value=scalar_reduced_kernel(p,q,c)+two_green_regulator_correction(p,q,c)
        return dict(value=value,kernel_approximation_upper=0.,method='stable exact wide two-point identity')
    pairs=((0,1),(0,2),(1,2))
    pair=min(pairs,key=lambda ij:float(np.max(abs(arrays[ij[0]]-arrays[ij[1]])/np.minimum(arrays[ij[0]],arrays[ij[1]]))))
    x,y=(arrays[i] for i in pair);z=arrays[3-sum(pair)];a=(x+y)/2
    if np.max(abs(x-y)/np.minimum(x,y))>.125:
        raise ValueError('reached triple needs a close pair; use full simplex integration otherwise')
    difference=z-a
    if np.any(abs(difference)<=.05*np.minimum(a,z)):
        raise ArithmeticError('wide repeated divided difference is not resolved')
    ga=np.exp(-c*a)/a;gz=np.exp(-c*z)/z
    gap=-np.exp(-c*a)*(c/a+1/a**2)
    value=(gz-ga-gap*difference)/difference**2
    if not np.isfinite(value).all() or np.any(value<=0):raise ArithmeticError('positive wide kernel not resolved')
    return dict(value=value,kernel_approximation_upper=_pair_midpoint_error(arrays,pair),
        method='wide repeated-pair Hermite kernel with outward close-pair Laplace remainder')


def _source_derivative(data,scalar,cutoff,*,terms):
    """Both original PF squares, left numerator and PH insertion placements."""
    Ao,Ae,po,pe,Vo,Ve=(data[k] for k in ('A_odd','A_even','eigenvalues_odd','eigenvalues_even','eigenvectors_odd','eigenvectors_even'))
    ho,Uo=eigh(scalar['positive_H_odd']);he,Ue=eigh(scalar['positive_H_even'])
    if min(np.min(po),np.min(pe),ho[0],he[0])<=0:raise ValueError('positive same-action forms required')
    gram=_positive(scalar['action_Gram_scalar'],'scalar action Gram')
    B0,B1,B1H=(data[k] for k in ('mixed_vertex_n0_odd','mixed_vertex_n1_Hodd','mixed_vertex_n1_Heven'))
    transform=lambda U,B:np.einsum('ab,bij->aij',U.T,B)
    B0h,B1h,B1eh=transform(Uo,B0),transform(Uo,B1),transform(Ue,B1H)
    left1=B1h.conj().transpose(0,2,1)@Ve;right0=(Vo.conj().T@Ao.conj().T)@B0h
    left0=B0h.conj().transpose(0,2,1)@Vo;right1=(Ve.conj().T@Ae.conj().T)@B1h
    plain0,plain1=Vo.conj().T@B0h,Ve.conj().T@B1h
    squares=[np.einsum('ij,Ajk,kl->Ail',Ve.conj().T,data[k],Vo) for k in ('delta_P_square_left','delta_P_square_right')]
    numerator=np.einsum('ij,Ajk,kl->Ail',Ve.conj().T,data['Xi_reverse_dagger_even_odd'],Vo)
    reverse_numerator=np.einsum('ij,Ajk,kl->Ail',Vo.conj().T,data['Xi_even_odd'].conj().transpose(0,2,1),Ve)
    names=('fermion_square_left','fermion_square_right','fermion_numerator_contact','scalar_propagator_insertion')
    shape=(3,B1.shape[-1],B0.shape[-1])
    forward={k:np.zeros(shape,complex) for k in names};reverse={k:np.zeros((3,shape[2],shape[1]),complex) for k in names}
    tails={k:[] for k in names};methods=set()
    def kernel(*p):
        r=temporal_image_green_kernel(*p,cutoff=cutoff,terms=terms);methods.add(r['method']);return r
    def add_tail(name,r,L,M,R):
        tails[name].append((contraction_series_tail_upper(r['kernel_approximation_upper'],L,M,R,gram),))
    for a,h in enumerate(ho):
        k3=kernel(pe[:,None],po[None,:],h);ke=kernel(pe,h);ko=kernel(po,h)
        for source in range(3):
            for name,square in zip(names[:2],squares):
                forward[name][source]-=left1[a]@(k3['value']*square[source])@right0[a]/gram
                reverse[name][source]-=left0[a]@(k3['value'].T*square[source].conj().T)@right1[a]/gram
                add_tail(name,k3,left1[a],square[source],right0[a]);add_tail(name,k3,left0[a],square[source].conj().T,right1[a])
            forward[names[2]][source]+=left1[a]@(ke['value'][:,None]*numerator[source])@plain0[a]/gram
            reverse[names[2]][source]+=left0[a]@(ko['value'][:,None]*reverse_numerator[source])@plain1[a]/gram
            add_tail(names[2],ke,left1[a],numerator[source],plain0[a]);add_tail(names[2],ko,left0[a],reverse_numerator[source],plain1[a])
    dH=np.einsum('ij,Ajk,kl->Ail',Ue.T,scalar['delta_positive_H_even_odd'][:3],Uo)
    leftH=B1eh.conj().transpose(0,2,1)@Vo;rightH=(Vo.conj().T@Ao.conj().T)@B1eh
    for j,f in enumerate(po):
        k3=kernel(he[:,None],ho[None,:],f)
        L,R=leftH[:,:,j].T,right0[:,j,:];Lr,Rr=left0[:,:,j].T,rightH[:,j,:]
        for source in range(3):
            forward[names[3]][source]-=L@(k3['value']*dH[source])@R/gram
            reverse[names[3]][source]-=Lr@(k3['value'].T*dH[source].T)@Rr/gram
            add_tail(names[3],k3,L,dH[source],R);add_tail(names[3],k3,Lr,dH[source].T,Rr)
    for out in (forward,reverse):out['total']=sum(out.values())
    return dict(forward=forward,reverse=reverse,kernel_methods=sorted(methods),
        exact_stored_kernel_approximation_contracted_upper={k:outward_positive_product_sum(v) for k,v in tails.items()},
        error_scope='outward exact-stored kernel series/midpoint remainder and norm products only; binary evaluation/contractions, assembly/eigensystem and physical domain excluded')


def temporal_image_source_application(data,scalar,*,length,lapse,cutoff,terms=6):
    """Apply the literal b^2 source through both reached temporal branches.

    Frozen angular operators and all source/contact matrices are reused.
    The scalar trial remains b, so no unrepresented b^3 vertex is created.
    The new internal fermion kinetic Gram is diagonalized as a whole.
    """
    L=_positive(length,'existing cell length');N=_positive(lapse,'actual intrinsic lapse')
    c=_positive(cutoff,'explicit common cutoff',zero=True)
    for key in ('A_odd','A_even','eigenvalues_odd','eigenvalues_even','eigenvectors_odd','eigenvectors_even',
        'mixed_vertex_n0_odd','mixed_vertex_n1_Hodd','mixed_vertex_n1_Heven','delta_P_square_left',
        'delta_P_square_right','Xi_reverse_dagger_even_odd','Xi_even_odd'):_finite(data.get(key),'reached '+key)
    for key in ('positive_H_odd','positive_H_even','delta_positive_H_even_odd'):_finite(scalar.get(key),'reached '+key,real=True)
    t=temporal_yukawa_source_image();branches=[]
    for mode,(kinetic,vertex) in enumerate(zip(t['temporal_eigenvalues'],t['normalized_vertex_coefficients'])):
        d=dict(data);shift=(kinetic-12)/(N*N*L*L)
        for key in ('eigenvalues_odd','eigenvalues_even'):d[key]=data[key]+shift
        for key in ('mixed_vertex_n0_odd','mixed_vertex_n1_Hodd','mixed_vertex_n1_Heven'):d[key]=data[key]*(vertex/(3/4))
        r=_source_derivative(d,scalar,c,terms=terms)
        branches.append(dict(mode=mode,kinetic_coefficient=float(kinetic),vertex_coefficient=float(vertex),
            normalized_temporal_kinetic=float(kinetic/(N*N*L*L)),**r))
    output={place:{name:sum(r[place][name] for r in branches) for name in branches[0][place]} for place in ('forward','reverse')}
    tails={name:outward_positive_product_sum([(r['exact_stored_kernel_approximation_contracted_upper'][name],) for r in branches]) for name in branches[0]['exact_stored_kernel_approximation_contracted_upper']}
    return dict(**output,branches=branches,temporal_image=t,exact_stored_kernel_approximation_contracted_upper=tails,
        cutoff=c,length=L,lapse=N,both_open_placements_and_both_PF_squares_retained=True,
        original_scalar_trial_enlarged=False,internal_fermion_source_image_b_squared_exact=True,
        source_first_order_differential_complement_removed=False,
        unchanged_old_attached_background_scope=True,physical_cutoff_or_native_Pauli_selected=False,
        Gaussian_statistics_sign_applied=False,complete_adopted_P_strat_derived=False)
