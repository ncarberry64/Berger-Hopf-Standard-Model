"""Proper-clock Clifford action on the retained piecewise source graph.

Every source cell has its own analytic coefficient chart.  The complex
physical-time germ solves dt/dtau_E=-i/N(t), and the independent reflected
germ solves the conjugate equation.  Real Euclidean proper-clock weights
then pair the actual continued first-order map with that reflected dual.
The temporal FE trace is shared at every corner and the final natural
cotangent is retained.  This finite graph is not a maximal exterior or a
complete stratified quantum loop.
"""
from __future__ import annotations
import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import eigh
from .muon_continued_action_reality import (
    _geometry,action_reality_coefficient,action_reality_source)
from .muon_profile_preserving_phase_sample import profile_preserving_raw_sample
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from .muon_changing_magnetic_current_jets import magnetic_current_angular_images


FAMILY_INDICES=np.array([[0,1,6,7,12,13],[2,3,8,9,14,15],[4,5,10,11,16,17]])


def proper_euclidean_source_nodes(phase,curves,*,quadrature_order=2,
                                  family_indices=None,source_axes=(0,1,2)):
    """Execute both source-cell proper-clock coefficient branches.

The positive cell lengths are the real-anchor physical proper-clock
integrals.  They define this numerical Euclidean representation, rather
than a physical cutoff.  No source spline is treated as globally analytic.
    """
    fi=np.arange(18)if family_indices is None else np.asarray(family_indices,int)
    axes=np.asarray(source_axes,int)
    if fi.ndim!=1 or len(set(fi.tolist()))!=len(fi) or np.any((fi<0)|(fi>=18)):
        raise ValueError('distinct retained lepton indices required')
    if axes.ndim!=1 or len(set(axes.tolist()))!=len(axes) or np.any((axes<0)|(axes>=8)):
        raise ValueError('distinct retained source axes required')
    gauss,gw=np.polynomial.legendre.leggauss(int(quadrature_order))
    metric_nodes,metric_w=np.polynomial.legendre.leggauss(4)
    grid=np.asarray(curves['times'],float);L=abs(float(phase['receipt']['span']))
    rows=[];clock=0.;errors=[]
    for j,(left,right)in enumerate(zip(grid[:-1],grid[1:])):
        future_center=(left+right)/2
        anchor=future_center-L if phase['receipt']['side']=='incoming'else future_center
        raw=profile_preserving_raw_sample(phase,anchor)
        x,rate=raw['raw_fields'],raw['raw_coordinate_time_derivative']
        half=(right-left)/2
        actual_times=anchor+half*metric_nodes
        Nreal=np.array([action_reality_coefficient(phase,t)['geometry']['N'].real for t in actual_times])
        length=float(half*(metric_w@Nreal)); offsets=gauss*length/2
        if length<=0:raise ValueError('proper clock changed orientation')
        def germ(sign):
            result=np.zeros(len(offsets),complex)
            for mask,end in((offsets<0,float(np.min(offsets))),(offsets>=0,float(np.max(offsets)))):
                if not np.any(mask):continue
                def rhs(t,z):return np.array([sign*1j/_geometry(x+z[0]*rate)['N']])
                solution=solve_ivp(rhs,(0,end),[0j],rtol=1e-11,atol=1e-17,dense_output=True,max_step=abs(end)/2)
                if not solution.success:raise ArithmeticError(solution.message)
                result[mask]=solution.sol(offsets[mask])[0]
            return result
        z,zs=germ(-1),germ(1)
        errors.append(float(np.max(abs(zs-z.conj()))))
        for k,(offset,weight)in enumerate(zip(offsets,gw*length/2)):
            forward=action_reality_coefficient(phase,anchor,z[k])
            reflected=action_reality_coefficient(phase,anchor,zs[k])
            source=action_reality_source(phase,anchor,curves,z[k])
            source_sharp=action_reality_source(phase,anchor,curves,zs[k])
            rows.append(dict(proper_time=clock+length/2+offset,weight=weight,
                source_cell=j,coordinate_anchor=anchor,coordinate_offset=z[k],reflected_coordinate_offset=zs[k],
                H=forward['Hcan'][np.ix_(fi,fi)],Hsharp=reflected['Hcan'][np.ix_(fi,fi)],
                R=forward['geometry']['R4'],Rsharp=reflected['geometry']['R4'],
                N=forward['geometry']['N'],
                Xi=source['Xi'][axes][:,:,fi][:,:,:,fi],
                Xisharp=source_sharp['Xi'][axes][:,:,fi][:,:,:,fi]))
        clock+=length
    result={key:np.array([r[key]for r in rows])for key in rows[0]}
    result.update(total_proper_clock=clock,source_cells=len(grid)-1,
        quadrature_order=int(quadrature_order),proper_clock_reflected_ODE_max=max(errors),
        reflected_body_identity_max=float(np.max(abs(result['Hsharp']-result['H'].conj().swapaxes(-1,-2)))),
        reflected_source_identity_max=float(np.max(abs(result['Xisharp']-result['Xi'].conj().swapaxes(-1,-2)))),
        source_cells_are_computational_chart_corners=True,
        lepton_indices=fi,source_axes=axes)
    return result


def _basis(t,total,cells):
    grid=np.linspace(0,total,cells+1);j=min(int(t/total*cells),cells-1)
    h=grid[j+1]-grid[j];s=(t-grid[j])/h
    # The initial right trace is removed; every later and final trace remains.
    return [(k-1,value,derivative)for k,value,derivative in((j,1-s,-1/h),(j+1,s,1/h))if k>0]


def family_piecewise_weak_forms(nodes,*,temporal_cells=4,family=1):
    """Assemble both positive action forms and all20source-image contacts.

Canonical coefficients use the actual ordered family block and unit Haar
Gram.  K=A_Edagger A_E is integrated BEFORE inversion; the complex-time
coefficient/dual maps were produced separately.  This is a conforming
finite graph approximation, not a source-compressed heat operator.
    """
    fi=FAMILY_INDICES[int(family)];n=int(temporal_cells);d0,d1=6,120
    selected=np.asarray(nodes.get('lepton_indices',np.arange(18)),int)
    positions=np.array([np.flatnonzero(selected==i)[0]for i in fi])
    axes=np.asarray(nodes.get('source_axes',np.arange(8)),int)
    axis_positions=np.array([np.flatnonzero(axes==i)[0]for i in range(3)])
    K0=np.zeros((n*d0,n*d0),complex);K1=np.zeros((n*d1,n*d1),complex)
    M0=np.zeros_like(K0);M1=np.zeros_like(K1);B=np.zeros((n*d0,d0),complex)
    L=np.zeros((d0,n*d0),complex);Lt=np.zeros((d1,n*d1),complex)
    dK=np.zeros((3,n*d1,n*d0),complex);dB=np.zeros((3,n*d1,d0),complex)
    rep=lepton_current_hilbert_representation();Q=-rep['EM_charge'][np.ix_(fi,fi)]
    alpha=rep['alpha'][:,fi][:,:,fi];E=magnetic_current_angular_images()['derivatives']['field_odd']
    angular=-1j*sum(np.kron(a,e)for a,e in zip(alpha,E));Q1=np.kron(Q,np.eye(20))
    reflection=0.
    for q,t in enumerate(nodes['proper_time']):
        weight=float(nodes['weight'][q]);basis=_basis(t,nodes['total_proper_clock'],n)
        H0=nodes['H'][q][np.ix_(positions,positions)];Hs0=nodes['Hsharp'][q][np.ix_(positions,positions)]
        H1=np.kron(H0,np.eye(20))+angular/nodes['R'][q]
        Hs1=np.kron(Hs0,np.eye(20))+angular/nodes['Rsharp'][q]
        reflection=max(reflection,float(np.max(abs(Hs1-H1.conj().T))))
        X=nodes['Xi'][q,axis_positions][:,:,positions][:,:,:,positions]
        Xs=nodes['Xisharp'][q,axis_positions][:,:,positions][:,:,:,positions]
        forward=X.transpose(0,2,1,3).reshape(3,d1,d0)
        # The [10] block of the independent reflected full operator is
        # the dagger of the FORWARD operator's [01], not of its [10].
        sharp=Xs.transpose(0,2,1,3).reshape(3,d1,d0)
        I0,I1=np.eye(d0),np.eye(d1)
        product0,product1=Hs0@H0,Hs1@H1
        for j,pj,dj in basis:
            sj, tj=slice(j*d0,(j+1)*d0),slice(j*d1,(j+1)*d1)
            dual0=dj*np.eye(d0)+pj*Hs0;dual1=dj*np.eye(d1)+pj*Hs1
            B[sj]+=weight*(dual0@Q);L[:,sj]+=weight*pj*Q;Lt[:,tj]+=weight*pj*Q1
            dB[:,tj]+=weight*pj*np.einsum('aij,jk->aik',sharp,Q)
            for k,pk,dk in basis:
                sk,tk=slice(k*d0,(k+1)*d0),slice(k*d1,(k+1)*d1)
                right0=dk*np.eye(d0)+pk*H0;right1=dk*np.eye(d1)+pk*H1
                K0[sj,sk]+=weight*(dj*dk*I0+dj*pk*H0+pj*dk*Hs0+pj*pk*product0)
                K1[tj,tk]+=weight*(dj*dk*I1+dj*pk*H1+pj*dk*Hs1+pj*pk*product1)
                M0[sj,sk]+=weight*pj*pk*np.eye(d0);M1[tj,tk]+=weight*pj*pk*np.eye(d1)
                dK[:,tj,sk]+=weight*(pj*np.einsum('aij,jk->aik',sharp,right0)
                                    +pk*np.einsum('ij,ajk->aik',dual1,forward))
    return dict(source_K=K0,target_K=K1,source_M=M0,target_M=M1,
        source_numerator=B,current_target=L,angular_current_target=Lt,
        magnetic_delta_K=dK,magnetic_delta_numerator=dB,
        family_indices=fi,temporal_cells=n,total_proper_clock=nodes['total_proper_clock'],
        full20angular_source_image_retained=True,source_image_compressed_before_square=False,
        reflected_full_body_identity_max=reflection,
        source_Hermiticity_rounding_max=float(np.max(abs(K0-K0.conj().T))),
        target_Hermiticity_rounding_max=float(np.max(abs(K1-K1.conj().T))),
        right_initial_trace_zero=True,final_natural_trace_kept=True,
        physical_outer_or_complete_stratified_domain=False)


def positive_weak_form_factor(K,M):
    """Finite generalized action square, keeping its rounding defect visible."""
    K,M=np.asarray(K,complex),np.asarray(M,complex)
    rounded=(K+K.conj().T)/2
    lam,C=eigh(rounded,M)
    if lam[0]<=0:raise ArithmeticError('nonpositive finite form; no shift or eigenvector deletion allowed')
    return dict(K=K,M=M,eigenvalues=lam,eigenvectors=C,
        Hermitian_quadratic_action=rounded,
        rounding_only_Hermitian_difference_max=float(np.max(abs(rounded-K))),
        exact_stored_unsymmetric_original_rows_retained=True)


def weak_form_heat_action(factor,B,c):
    C,lam=factor['eigenvectors'],factor['eigenvalues'];c=float(c)
    if c<0 or not np.isfinite(c):raise ValueError('unchanged positive cutoff required')
    return C@((np.exp(-c*lam)/lam)[:,None]*(C.conj().T@B))


def weak_form_heat_source_contact(source,target,B,dK,dB,c):
    from .muon_continued_current_boundary_heat import spectral_divided_g
    C0,C1=source['eigenvectors'],target['eigenvectors']
    numerator=weak_form_heat_action(target,dB,c)
    square=C1@((spectral_divided_g(target['eigenvalues'],source['eigenvalues'],float(c))
                *(C1.conj().T@dK@C0))@(C0.conj().T@B))
    return dict(response=square+numerator,square_contact=square,numerator_contact=numerator)
