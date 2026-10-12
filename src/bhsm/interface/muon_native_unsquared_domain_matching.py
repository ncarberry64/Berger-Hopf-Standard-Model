"""Unsquared current/adjoint matching and the exact finite range complement.

The native factor acts into the quadrature derivative image, which can be
larger than the chosen FE value test space.  Its square/numerator is not
identified with a projected unsquared inverse without evaluating that
complement.  The holomorphic and geometric measures are both retained.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import solve_banded
from .muon_chronological_clifford_graph import (
    _angular_operators,_rows,chronological_clifford_blocks)
from .muon_chronological_spectral_blocks import (
    chronological_spectral_factor,chronological_source_solve,
    chronological_source_residual)
from .muon_native_reset_friedrichs_return import chain_apply


def _weak_source_solve(pencil,rhs):
    """Original-row band-pivoted solve; zero local derivative pivots are legal.

    An invertible first-order FE action can have zero diagonal cell Schurs.
    Pivoting the complete band avoids treating such a local pivot as a
    physical null direction, while retaining every trace/action row.
    """
    D,U,L=map(np.asarray,pencil);b=np.asarray(rhs,complex);n,d,_=D.shape
    bandwidth=2*d-1;band=np.zeros((2*bandwidth+1,n*d),complex)
    nodes=np.arange(n)*d;edges=np.arange(n-1)*d
    for i in range(d):
        for k in range(d):
            band[bandwidth+i-k,nodes+k]=D[:,i,k]
            band[bandwidth+i-k-d,edges+d+k]=U[:,i,k]
            band[bandwidth+i-k+d,edges+k]=L[:,i,k]
    solution=solve_banded((bandwidth,bandwidth),band,b.reshape(n*d,-1),
        overwrite_ab=True,check_finite=True)
    return solution.reshape(b.shape)


def _assemble_matching_forms(quadrature,*,temporal_nodes,angular_derivatives,alpha,source_sampler):
    h=np.asarray(angular_derivatives).shape[-1];d=6*h;n=temporal_nodes-1;I=np.eye(d)
    forms={}
    for measure in ('geometric','analytic'):
        forms[measure]=dict(diagonal=np.zeros((n,d,d),complex),upper=np.zeros((n-1,d,d),complex),lower=np.zeros((n-1,d,d),complex))
    source_columns=None;right={};left={};numerator=None;reflection=0.
    for q in quadrature:
        A,As=_angular_operators(q,angular_derivatives,alpha)
        reflection=max(reflection,float(np.max(abs(As-A.conj().T))))
        JR,LT=map(lambda x:np.asarray(x,complex),source_sampler(q))
        if JR.ndim!=2 or JR.shape[0]!=d or LT.shape!=JR.T.shape or not np.isfinite(JR).all()or not np.isfinite(LT).all():
            raise ValueError('literal right source FUNCTION and analytic left target required')
        if source_columns is None:
            source_columns=JR.shape[1]
            right={k:np.zeros((n,d,source_columns),complex)for k in forms}
            left={k:np.zeros((n,source_columns,d),complex)for k in forms}
            numerator=np.zeros_like(right['geometric'])
        if JR.shape[1]!=source_columns:raise ValueError('same complete source columns at every node required')
        mu=complex(q['measure']);m=complex(q['original_holomorphic_measure']);w=complex(q['right_clock']);ws=complex(q['reflected_clock'])
        if mu.imag or mu.real<=0:raise ValueError('native geometric Gram must be positive')
        rows=_rows(q,temporal_nodes)
        for j,pj,dj in rows:
            numerator[j]+=mu*(dj*I/ws+pj*As)@JR
            for key,weight in(('geometric',mu),('analytic',m)):
                right[key][j]+=weight*pj*JR;left[key][j]+=weight*pj*LT
                for k,pk,dk in rows:
                    value=weight*pj*(dk*I/w+pk*A)
                    name,index=('diagonal',j)if j==k else ('upper',j)if k==j+1 else ('lower',k)
                    forms[key][name][index]+=value
    return dict(weak_factors=forms,right_moments=right,left_moments=left,
        independently_acted_source_numerator=numerator,background_Hilbert_reflection_defect=reflection)


def native_unsquared_domain_matching(quadrature,*,temporal_nodes,angular_derivatives,alpha,source_sampler):
    """Evaluate one same-background current and both finite inverse realizations.

    A_w=int mu phi*A phi, M=int mu phi*phi,
    K=A_w^dagger M^-1 A_w+K_range and
    B=A_w^dagger M^-1 R+B_range. Both range contacts are applied to the
    ACTUAL source before inversion, not discarded or called a tail bound.
    The original analytic transpose adjoint/current is solved separately.
    """
    a=_assemble_matching_forms(quadrature,temporal_nodes=temporal_nodes,
        angular_derivatives=angular_derivatives,alpha=alpha,source_sampler=source_sampler)
    blocks=chronological_clifford_blocks(quadrature,temporal_nodes=temporal_nodes,
        angular_derivatives=angular_derivatives,alpha=alpha)
    K=tuple(blocks['K_'+k]for k in('diagonal','upper','lower'))
    M=tuple(blocks['M_'+k]for k in('diagonal','upper','lower'))
    fk=chronological_spectral_factor(*K);fm=chronological_spectral_factor(*M)
    uk=np.asarray(chronological_source_solve(fk,a['independently_acted_source_numerator']))
    out=dict(native_factor_response=uk,
        native_original_square_residual=np.asarray(chronological_source_residual(fk,uk,a['independently_acted_source_numerator'])),
        initial_right_trace_removed=True,free_final_and_all_corner_rows_retained=True,
        right_source_function_replaced_by_weak_moment=False,
        source_tangent_conjugated=False,physical_LSZ_or_external_domain_identified=False,
        background_Hilbert_reflection_defect=a['background_Hilbert_reflection_defect'])
    for key,form in a['weak_factors'].items():
        P=tuple(form[k]for k in('diagonal','upper','lower'))
        R=a['right_moments'][key];LT=a['left_moments'][key]
        u=_weak_source_solve(P,R)
        # This is the analytic transpose; it does not conjugate source or target.
        tP=(P[0].transpose(0,2,1),P[2].transpose(0,2,1),P[1].transpose(0,2,1))
        p=_weak_source_solve(tP,LT.transpose(0,2,1))
        current=np.einsum('nci,nij->cj',LT,u)
        dual=np.einsum('nic,nij->cj',p,R)
        out[key+'_weak_response']=u;out[key+'_transpose_adjoint']=p
        out[key+'_current']=current;out[key+'_independent_transpose_current']=dual
        out[key+'_original_weak_rows']=chain_apply(*P,u)-R
        out[key+'_original_transpose_rows']=chain_apply(*tP,p)-LT.transpose(0,2,1)
        out[key+'_factor_current']=np.einsum('nci,nij->cj',LT,uk)
        out[key+'_factor_weak_equation_defect']=chain_apply(*P,uk)-R
        if key=='geometric':
            AP=(P[0].conj().transpose(0,2,1),P[2].conj().transpose(0,2,1),P[1].conj().transpose(0,2,1))
            source_projection=np.asarray(chronological_source_solve(fm,R))
            factor_action=chain_apply(*P,uk)
            factor_projection=np.asarray(chronological_source_solve(fm,factor_action))
            out['acted_source_range_contact']=a['independently_acted_source_numerator']-chain_apply(*AP,source_projection)
            out['square_range_contact_on_actual_response']=chain_apply(*K,uk)-chain_apply(*AP,factor_projection)
            out['range_identity_original_row_residual']=out['square_range_contact_on_actual_response']-out['acted_source_range_contact']
            # K u=B implies rangeK*u-rangeB= -Aw†M^-1(Aw*u-R), not zero in general.
            out['range_identity_original_row_residual']+=chain_apply(*AP,np.asarray(chronological_source_solve(fm,
                out[key+'_factor_weak_equation_defect'])))
    out.update(independently_acted_source_numerator=a['independently_acted_source_numerator'],
        geometric_right_current_moments=a['right_moments']['geometric'],analytic_right_current_moments=a['right_moments']['analytic'],
        geometric_literal_left_moments=a['left_moments']['geometric'],analytic_literal_left_moments=a['left_moments']['analytic'])
    return out
