"""Changing-coefficient paired heat cotangent on an explicit temporal form.

This differentiates the same first-order factor and its generalized Gram.
It keeps the coefficient Y² by functional calculus, rather than subtracting
two nearly identical family heat traces. The domain is recorded explicitly;
the calculation does not supply its unrepresented starting-loop complement.
"""
from __future__ import annotations
import math
import numpy as np
from scipy.linalg import cholesky,eigh,solve_triangular
from scipy.special import exprel
from .muon_source_directed_temporal_green import source_product_temporal_values
from .muon_profile_preserving_phase_sample import profile_preserving_lepton_sample
from .muon_native_mean_core_heat_target import _unit_lepton_mass6
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_primal_native_phase_adjoint import native_phase_midpoint_map,native_phase_named_border,native_phase_load_rows


def heat_gradient_divided_differences(values,cutoff):
    """Stable g[1],g[2] for g(x)=-exp(-cx)/x and positive real poles.

    Leibniz divided differences split exponential and reciprocal factors.
    Every term of g[2] has the same sign. Close exponential poles use the
    actual simplex Taylor integral; no spectral rank or pole deletion.
    """
    a=np.asarray(values,float);c=float(cutoff)
    if a.ndim!=1 or np.any(a<=0)or not np.isfinite(a).all()or not np.isfinite(c)or c<0:
        raise ValueError('positive complete poles and nonnegative same cutoff required')
    lo=np.minimum(a[:,None],a[None,:]);hi=np.maximum(a[:,None],a[None,:])
    first=np.exp(-c*lo)*(1/(lo*hi)+c*exprel(-c*(hi-lo))/hi)
    def second(rows):
        poles=np.broadcast_arrays(a[rows,None,None],a[None,:,None],a[None,None,:])
        low=np.minimum(np.minimum(poles[0],poles[1]),poles[2])
        high=np.maximum(np.maximum(poles[0],poles[1]),poles[2])
        middle=np.maximum(np.minimum(poles[0],poles[1]),np.minimum(np.maximum(poles[0],poles[1]),poles[2]))
        y=c*(middle-low);z=c*(high-low);F=np.empty_like(z)
        small=z<.1
        # int_triangle exp[-y*s-z*t]=sum (-1)^n h_n(y,z)/(n+2)!
        ys,zs=y[small],z[small];total=np.zeros_like(ys)
        for n in range(12):
            hn=sum(ys**k*zs**(n-k)for k in range(n+1))
            total+=(-1)**n*hn/math.factorial(n+2)
        F[small]=total
        large=~small
        F[large]=(exprel(-y[large])-np.exp(-y[large])*exprel(-(z[large]-y[large])))/z[large]
        exponential=np.exp(-c*low)
        return -exponential*(1/(low*middle*high)+c*exprel(-y)/(middle*high)+c*c*F/high)
    return first,second


def even_y_trace_duals(P0,P1,P2,Gram,cutoff,*,row_chunk=8):
    """Actual coefficient and all three action/Gram cotangents of Tr E1.

    The supplied matrices are unnormalized weak-action coefficients. The
    returned duals differentiate their one common generalized Gram. No
    complex-fermion statistics factor is inserted here.
    """
    K,C,B,G=(np.asarray(x,complex)for x in(P0,P1,P2,Gram));n=len(K)
    if any(x.shape!=(n,n)or not np.isfinite(x).all()for x in(K,C,B,G)):
        raise ValueError('same complete finite action and Gram required')
    cg=cholesky(G,lower=True);X=solve_triangular(cg.conj().T,np.eye(n),lower=False)
    p=X.conj().T@K@X;c1=X.conj().T@C@X;b2=X.conj().T@B@X
    lam,V=eigh(p);U=X@V;cc=V.conj().T@c1@V;bb=V.conj().T@b2@V
    if lam[0]<=0:raise ArithmeticError('unshifted positive temporal form required')
    first,second=heat_gradient_divided_differences(lam,cutoff)
    g=-np.exp(-float(cutoff)*lam)/lam;D=first*cc;Z=first*bb
    for start in range(0,n,row_chunk):
        end=min(start+row_chunk,n);s=second(slice(start,end))
        Z[start:end]+=np.einsum('ikj,ik,kj->ij',s,cc[start:end],cc)
    Z=(Z+Z.conj().T)/2;D=(D+D.conj().T)/2;Q=np.diag(g)
    coefficient=float((g@np.diag(bb).real+.5*np.sum(first*abs(cc)**2)).real)
    dualG=.5*(lam[:,None]*Z+Z*lam[None,:]+cc@D+D@cc+bb@Q+Q@bb)
    duals=[U@a@U.conj().T for a in(Z,D,Q,dualG)]
    return dict(even_Y2_coefficient=coefficient,action_duals=duals[:3],Gram_dual=duals[3],
        generalized_eigenvalues=lam,Gram_orthonormal_eigenvectors=U,
        generalized_eigen_residual=float(np.linalg.norm(K@U-(G@U)*lam)/np.linalg.norm(K@U)),
        Gram_orthonormality_defect=float(np.linalg.norm(U.conj().T@G@U-np.eye(n))),
        coefficient_gradient_includes_Gram=True,statistics_factor_applied=False)


def changing_n0_heat_mean_target(phase,*,cutoff,quadrature_order=12):
    """Evaluate the n0/C6 temporal8 heat target and its actual phase pullback."""
    if phase['receipt']['steps']!=1:raise ValueError('same one-cell phase required')
    L=abs(phase['receipt']['span']);z,w=np.polynomial.legendre.leggauss(quadrature_order)
    times=np.concatenate(((z+1)*L/4,(z+3)*L/4));weights=np.tile(w*L/4,2)
    tf=source_product_temporal_values(times,L);v,vd=tf['value'],tf['coordinate_rate'];points=[]
    fi=np.array([2,3,8,9,14,15]);fj=np.array([4,5,10,11,16,17]);sign=np.diag([1]*4+[-1]*2)
    for u in times:
        t=float(u-L if phase['receipt']['side']=='incoming'else u)
        a=profile_preserving_lepton_sample(phase,t);op=a['operator'];raw=a['sample']['raw_fields']
        A=op['W'][np.ix_(fi,fi)]+op['Omega_tau'][np.ix_(fi,fi)]
        dA=op['W_raw_first_jet'][:,fi][:,:,fi]+op['Omega_tau_raw_first_jet'][:,fi][:,:,fi]
        # The fixed action's L/R-odd part is exactly Y*M(H).
        A=(A+sign@A@sign)/2;dA=(dA+np.einsum('ij,bjk,kl->bil',sign,dA,sign))/2
        other=op['W'][np.ix_(fj,fj)]+op['Omega_tau'][np.ix_(fj,fj)]
        other=(other+sign@other@sign)/2
        if np.max(abs(A-other))!=0:raise ValueError('shared fixed-family Y0 background is not identical')
        M=_unit_lepton_mass6(op['H']);dM=np.zeros((268,6,6),complex)
        dM[260:264]=np.array([_unit_lepton_mass6(H)for H in([1,0],[0,1],[1j,0],[0,1j])])
        N=op['N'];dN=N*op['proper_time_Haar_measure_first_jet']/op['proper_time_Haar_measure']
        points.append(dict(time=t,N=N,A=A,dA=dA,M=M,dM=dM,dN=dN))
    Gt=np.einsum('t,t,ta,tb->ab',weights,np.array([a['N']for a in points]),v,v)
    ct=cholesky(Gt,lower=True);T=solve_triangular(ct.T,np.eye(8),lower=False);v=v@T;vd=vd@T
    I=np.eye(6);size=48;K=[np.zeros((size,size),complex)for _ in range(3)];G=np.zeros_like(K[0]);app=[]
    for j,a in enumerate(points):
        V=np.concatenate([x*I for x in v[j]],axis=1);Vd=np.concatenate([x*I for x in vd[j]],axis=1)
        F0=Vd/a['N']+a['A']@V;Fm=a['M']@V;measure=weights[j]*a['N']
        K[0]+=measure*(F0.conj().T@F0);K[1]+=measure*(F0.conj().T@Fm+Fm.conj().T@F0)
        K[2]+=measure*(Fm.conj().T@Fm);G+=measure*(V.conj().T@V);app.append((V,Vd,F0,Fm))
    target=even_y_trace_duals(*K,G,cutoff);D0,D1,D2=target['action_duals'];DG=target['Gram_dual']
    maps=native_phase_midpoint_map(phase['representation']);midmap=maps['raw_from_phase'];coords=maps['coordinates'];n=coords['x_count']
    phase_gradient=np.zeros(midmap.shape[1]);raw_gradients=[]
    for j,(a,(V,Vd,F0,Fm))in enumerate(zip(points,app)):
        L0=F0@D0+Fm@D1;Lm=F0@D1+Fm@D2
        # dA and dM act on one actual coefficient fiber at this quadrature node.
        dF0=np.einsum('jab,bc->jac',a['dA'],V)-a['dN'][:,None,None]*Vd/a['N']**2
        dFm=np.einsum('jab,bc->jac',a['dM'],V)
        gram_density=(np.vdot(F0,F0@D0)+2*np.vdot(F0,Fm@D1)+np.vdot(Fm,Fm@D2)-np.vdot(V,V@DG)).real
        gradient=weights[j]*(a['dN']*gram_density+2*a['N']*(
            np.einsum('ab,jab->j',L0.conj(),dF0)+np.einsum('ab,jab->j',Lm.conj(),dFm)).real)
        raw_gradients.append(gradient)
        node_map=midmap.copy();node_map[:,2*n:3*n]+=(a['time']-( -L/2 if phase['receipt']['side']=='incoming'else L/2))*coords['lift'][:,:n]
        phase_gradient+=gradient@node_map
    Y=np.diag(lepton_current_hilbert_representation()['family_Y']).real;difference=Y[1]**2-Y[2]**2
    return dict(paired_Y2_value=difference*target['even_Y2_coefficient'],paired_phase_gradient=difference*phase_gradient,
        paired_raw_quadrature_cotangents=difference*np.array(raw_gradients),quadrature_coordinate_times=np.array([a['time']for a in points]),
        temporal_Gram=G,weak_P0=K[0],weak_P1=K[1],weak_P2=K[2],
        generalized_eigenvalues=target['generalized_eigenvalues'],
        generalized_eigen_residual=target['generalized_eigen_residual'],Gram_orthonormality_defect=target['Gram_orthonormality_defect'],
        coefficient_Y2_only=True,remaining_even_Y4_not_filled_zero=True,
        source_domain='n0 constant-angular C6, all eight retained source-product temporal functions',
        same_changing_coefficient_measure_and_phase_map_used=True,
        error_scope='binary64 coefficient-time integration and functional-calculus Y2 contraction; no complete Y4, temporal/angular complement or native/Pauli enclosure')


def contract_changing_phase_mean(phase_gradient,mean_load,phase,*,frame='temporal'):
    """Use the actual integrated phase target in the original chronological adjoint."""
    from .muon_primal_native_phase_adjoint import chronological_native_phase_jacobian
    J=phase['arrays']['stage_jacobian'][0]
    chrono=chronological_native_phase_jacobian(J,phase['representation'],phase['receipt']['span'])
    b=native_phase_named_border(chrono['jacobian'],phase['representation'],frame=frame);K=b['matrix']
    G=np.asarray(phase_gradient,float);F=native_phase_load_rows(mean_load,phase['representation'],chrono['step'])
    if G.shape!=(len(K)-2,):raise ValueError('actual same-phase integrated target required')
    row=1/np.maximum(np.max(abs(K),axis=1),np.finfo(float).tiny);col=1/np.maximum(np.max(abs(row[:,None]*K),axis=0),np.finfo(float).tiny)
    A=row[:,None]*K*col[None,:];rhs=np.r_[G,0.,0.];adj=row*np.linalg.solve(A.T,col*rhs)
    pair=-np.einsum('i,iab->ab',adj[:-2],F)
    return dict(ungraded_mean_contact=pair,target_adjoint=adj,phase_source_rows=F,phase_target=G,
        original_adjoint_residual=K.T@adj-rhs,balanced_condition_number=float(np.linalg.cond(A)),
        frame=frame,all_original_Euler_Legendre_Gauss_rows_retained=True,
        midpoint_raw_target_substituted=False,statistics_factor_applied=False)
