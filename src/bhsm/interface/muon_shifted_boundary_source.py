"""External trace charts and source-corrected finite form-core returns.

The independent analytic left envelope is not a Hilbert adjoint.  Neither
an external energy shift nor a finite Friedrichs restriction is identified
with the spectral substitution z=E**2 or with a physical exterior stop.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import expm
from .muon_chronological_clifford_graph import _angular_operators, _rows
from .muon_chronological_spectral_blocks import (
    chronological_spectral_factor, chronological_source_solve)
from .muon_native_reset_friedrichs_return import (
    chain_apply, terminal_friedrichs_source_return)


def canonical_reset_chart(parent_density, child_density, raw_reset):
    """Transform value and covector traces through the actual density chart.

    chi=C psi gives T=C_child U_raw C_parent^-1.  The analytic flux obeys
    pi_parent+T.T pi_child=0; the Hilbert flux uses T.dagger instead.
    A common canonical reset is a separate owner choice, not inferred by
    suppressing unequal density factors in a raw-Psi reset.
    """
    Cp,Cc,U=map(lambda a:np.asarray(a,complex),
        (parent_density,child_density,raw_reset))
    if Cp.ndim!=2 or Cp.shape[0]!=Cp.shape[1] or any(a.shape!=Cp.shape for a in(Cc,U)):
        raise ValueError('same complete raw and canonical trace coordinates required')
    T=np.linalg.solve(Cp.T,(Cc@U).T).T
    inverse=np.linalg.solve(T,np.eye(len(T)))
    return dict(canonical_value_reset=T,analytic_covector_reset=inverse.T,
        Hilbert_covector_reset=inverse.conj().T,
        canonical_Hilbert_unitarity_defect=T.conj().T@T-np.eye(len(T)),
        raw_reset_and_canonical_reset_identified_without_chart=False)


def shifted_boundary_forms(quadrature,*,temporal_nodes,angular_derivatives,alpha,
                           source_sampler=None):
    """Integrate distinct E-polynomials BEFORE choosing their boundary rows.

    A right forward-clock envelope has A_R-E.  Its independent analytic
    left exp(+E*tau) placement is A_sharp+E*w/ws, using the SAME forward
    clock tau'=w.  The genuine real-E Hilbert square has -E on both sides.
    No sampled external FE source clock is silently differentiated here.
    Optional sources are FUNCTIONS; original left target is independent.
    """
    d=6*np.asarray(angular_derivatives).shape[-1];n=temporal_nodes-1;I=np.eye(d)
    def blocks():
        return dict(diagonal=np.zeros((n,d,d),complex),
            upper=np.zeros((n-1,d,d),complex),lower=np.zeros((n-1,d,d),complex))
    forms={name:[blocks()for _ in range(3)]for name in(
        'analytic_envelope','native_reflected_envelope','Hilbert_shift')}
    B=R=LT=None;reflection=0.
    for q in quadrature:
        A,As=_angular_operators(q,angular_derivatives,alpha)
        w,ws=complex(q['right_clock']),complex(q['reflected_clock'])
        mu=complex(q['measure']);m=complex(q['original_holomorphic_measure'])
        if mu.imag or mu.real<=0 or not w or not ws:
            raise ValueError('positive native measure and both nonzero clock germs required')
        reflection=max(reflection,float(np.max(abs(As-A.conj().T))))
        rows=_rows(q,temporal_nodes)
        if source_sampler is not None:
            JR,left=map(lambda x:np.asarray(x,complex),source_sampler(q))
            if JR.ndim!=2 or JR.shape[0]!=d or left.shape!=JR.T.shape:
                raise ValueError('same literal source function and independent left required')
            if B is None:
                B=np.zeros((n,d,JR.shape[1]),complex);R=np.zeros_like(B)
                LT=np.zeros((n,JR.shape[1],d),complex)
        for j,pj,dj in rows:
            left0=dj*I/ws+pj*As
            Hilbert0=np.conj(dj)*I/np.conj(w)+np.conj(pj)*A.conj().T
            if source_sampler is not None:
                B[j]+=mu*left0@JR;R[j]+=mu*pj*JR;LT[j]+=m*pj*left
            for k,pk,dk in rows:
                right0=dk*I/w+pk*A
                name,index=('diagonal',j)if j==k else('upper',j)if k==j+1 else('lower',k)
                analytic=(left0@right0,
                    (w/ws)*pj*right0-left0*pk,-(w/ws)*pj*pk*I)
                hilbert=(Hilbert0@right0,
                    -np.conj(pj)*right0-Hilbert0*pk,np.conj(pj)*pk*I)
                for family,weight,values in(
                    ('analytic_envelope',m,analytic),
                    ('native_reflected_envelope',mu,analytic),
                    ('Hilbert_shift',mu,hilbert)):
                    for a,v in zip(forms[family],values):a[name][index]+=weight*v
    out=dict(forms=forms,independent_reflected_body_defect=reflection,
        external_energy_identified_with_spectral_square=False,
        analytic_left_envelope_is_Hilbert_adjoint=False)
    if B is not None:out.update(acted_source_numerator=B,
        geometric_source_moments=R,analytic_literal_left_moments=LT)
    return out


def source_corrected_form_core_return(blocks,numerator,literal_left,*,
                                      weak_factor=None,source_moments=None):
    """Actual K^T adjoints, forced source and original terminal conormal.

    xD=xN-G_:F G_FF^-1 xN(F).  The square's terminal reaction is the
    source-corrected conormal, including the acted-source subtraction.
    The unsquared acted return Aw*(xN-xD) is retained separately from
    that reaction and is not replaced by a fitted first-order Bout.
    """
    r=terminal_friedrichs_source_return(blocks,numerator,spectral_parameter=0.)
    K=tuple(np.asarray(blocks['K_'+k],complex)for k in('diagonal','upper','lower'))
    left=np.asarray(literal_left,complex)
    if left.ndim!=3 or left.shape[0]!=len(K[0])or left.shape[2]!=len(K[0][0]):
        raise ValueError('all original literal left target rows required')
    KT=(K[0].transpose(0,2,1),K[2].transpose(0,2,1),K[1].transpose(0,2,1))
    pN=np.asarray(chronological_source_solve(chronological_spectral_factor(*KT),left.transpose(0,2,1)))
    pD=np.zeros_like(pN)
    pD[:-1]=np.asarray(chronological_source_solve(
        chronological_spectral_factor(KT[0][:-1],KT[1][:-1],KT[2][:-1]),left[:-1].transpose(0,2,1)))
    xN=r['natural_solution'];xD=r['form_core_solution'];B=np.asarray(numerator,complex)
    current=lambda x:np.einsum('nci,nij->cj',left,x)
    dual=lambda p:np.einsum('nic,nij->cj',p,B)
    r.update(natural_literal_current=current(xN),form_core_literal_current=current(xD),
        forced_return_literal_current=current(r['forced_final_face_return']),
        independent_natural_transpose_current=dual(pN),
        independent_form_core_transpose_current=dual(pD),
        natural_square_transpose_adjoint=pN,form_core_square_transpose_adjoint=pD,
        natural_transpose_original_rows=chain_apply(*KT,pN)-left.transpose(0,2,1),
        form_core_transpose_original_rows=chain_apply(*KT,pD)-left.transpose(0,2,1),
        source_corrected_final_conormal=r['final_reaction'],
        source_corrected_final_conormal_omitting_source=r['final_reaction']+B[-1],
        square_adjoint_replaced_by_unsquared_adjoint=False)
    if weak_factor is not None:
        if source_moments is None:raise ValueError('actual unsquared source moments required')
        r.update(unsquared_forced_source_return=chain_apply(*weak_factor,r['forced_final_face_return']),
            natural_unsquared_source_rows=chain_apply(*weak_factor,xN)-source_moments,
            form_core_unsquared_source_rows=chain_apply(*weak_factor,xD)-source_moments)
    return r


def cauchy_external_trace_maps(proper_steps,body,*,energy=0.,reset_node=None,reset=None):
    """Complete operator Cauchy maps, not selected exterior states or poles.

    The envelope phi solves (d_tau+H-E)phi=0.  Its analytic dual is the
    inverse TRANSPOSE transport, not its Hilbert adjoint.  Physical chi
    is exp(-E*tau)phi, so the corresponding E contact cancels at every
    point.  Both initial and finite final Dirichlet values give a 2d-by-d
    homogeneous boundary residual; a d-by-d pole determinant is not made.
    """
    h,H=np.asarray(proper_steps,complex),np.asarray(body,complex);E=complex(energy)
    if h.ndim!=1 or H.ndim!=3 or len(h)!=len(H)or H.shape[1]!=H.shape[2]or not len(h):
        raise ValueError('complete directed action edges and full trace body required')
    d=H.shape[1];I=np.eye(d,dtype=complex);T=I if reset is None else np.asarray(reset,complex)
    if T.shape!=(d,d)or(reset_node is not None and not 0<reset_node<=len(h)):
        raise ValueError('same complete reset trace and actual interior node required')
    right=[I];left=[I];tau=[0j]
    for j,(step,A)in enumerate(zip(h,H)):
        V=expm(step*(E*I-A));R=V@right[-1]
        if reset_node==j+1:R=T@R
        right.append(R);left.append(np.linalg.solve(R.T,I));tau.append(tau[-1]+step)
    R=np.array(right);L=np.array(left);t=np.array(tau)
    RE=t[:,None,None]*R;LE=-t[:,None,None]*L
    physicalR=np.exp(-E*t)[:,None,None]*R
    physicalL=np.exp(+E*t)[:,None,None]*L
    rectangle=np.concatenate((I,R[-1]),axis=0)
    return dict(envelope_right_trace_map=R,envelope_analytic_left_trace_map=L,
        envelope_right_trace_map_energy_first=RE,envelope_analytic_left_trace_map_energy_first=LE,
        physical_right_trace_map=physicalR,physical_analytic_left_trace_map=physicalL,
        physical_right_trace_map_energy_first=np.exp(-E*t)[:,None,None]*(RE-t[:,None,None]*R),
        physical_analytic_left_trace_map_energy_first=np.exp(E*t)[:,None,None]*(LE+t[:,None,None]*L),
        proper_clock_at_trace=t,analytic_dual_pairing_residual=np.einsum('nji,njk->nik',L,R)-I,
        initial_and_terminal_Dirichlet_boundary_residual=rectangle,
        rectangular_boundary_rows=2*d,first_order_trace_dimension=d,
        physical_exterior_boundary_or_mass_selected=False)
