"""Exact-stored full canonical tangent batches, not action accuracy bounds.

The input is a fixed original signed H, fixed oriented cell h and named
frame. Source-free Jacobi equations are assembled from these operands in
Acb before solving. Every original phase and frame reaction remains.
"""
from __future__ import annotations
import numpy as np
from flint import acb, acb_mat, ctx
from .muon_stored_admission_correction import _matrix,_mid,_upper


def _rows(a,lo,hi):
    return acb_mat([[a[i,j]for j in range(a.ncols())]for i in range(lo,hi)])


def _cat(*arrays):
    return acb_mat([[a[i,j]for j in range(a.ncols())]for a in arrays for i in range(a.nrows())])


def _split(a):
    hi=_mid(a);return hi,_mid(a-_matrix(hi))


def exact_fiber_ward_lift(embedding,fiber,ward_map,ward_position_contact,pivots,*,precision_bits=192):
    """Multiply E*N exactly and repair only the two dependent Pi coordinates.

    ward_map dPi+ward_position_contact dx=0 is the independently supplied
    literal Ward derivative. All free positions and Pi columns are kept.
    """
    E,N,C,A=map(lambda a:np.asarray(a,complex),(embedding,fiber,ward_map,ward_position_contact))
    n=E.shape[0]//2;piv=np.asarray(pivots,int)
    if E.shape[0]!=2*n or N.ndim!=2 or E.shape[1]!=N.shape[0]or C.shape!=(2,n)or A.shape!=(2,n)or piv.shape!=(2,):
        raise ValueError('same full canonical fiber and literal two Ward identities required')
    old=ctx.prec;ctx.prec=int(precision_bits)
    try:
        z=_matrix(E)*_matrix(N);before=_matrix(C)*_rows(z,n,2*n)+_matrix(A)*_rows(z,0,n)
        correction=_matrix(C[:,piv]).solve(-before)
        for i,k in enumerate(piv):
            for j in range(z.ncols()):z[n+k,j]+=correction[i,j]
        hi,lo=_split(z)
        after=_matrix(C)*_rows(z,n,2*n)+_matrix(A)*_rows(z,0,n)
        return dict(canonical_direction_high=hi,canonical_direction_low=lo,
            dependent_Pi_correction_high=_mid(correction),ward_before_upper=_upper(before),
            ward_after_upper=_upper(after),ward_after=_mid(after),
            only_named_dependent_Pi_corrected=True,precision_bits=precision_bits)
    finally:ctx.prec=old


def stored_original_canonical_tangent(H,step,frame,canonical_high,canonical_low,*,precision_bits=192):
    """Solve every original358-style row with all batch RHS and literal dual.

    n is inferred from the full (dx,dPi) input. The frame is fixed at the
    supplied coefficient chart; no event trace is inserted as a bulk row.
    This is the exact derivative of the original midpoint equations for
    the stored H and h, without rounding the h*H coefficient assembly.
    """
    H=np.asarray(H,complex);F=np.asarray(frame,complex)
    high,low=np.asarray(canonical_high,complex),np.asarray(canonical_low,complex)
    n=high.shape[0]//2;m=len(H)-2*n;nf=len(F);nc=high.shape[1];d=3*n+m
    if high.ndim!=2 or low.shape!=high.shape or H.shape!=(2*n+m,)*2 or m<1 or F.shape!=(nf,n+m)or not step:
        raise ValueError('full original signed H, canonical batch, frame and nonzero clock required')
    old=ctx.prec;ctx.prec=int(precision_bits)
    try:
        hs=acb(complex(step).real,complex(step).imag);HH=_matrix(H)
        initial=_matrix(high)+_matrix(low);xi,pi=_rows(initial,0,n),_rows(initial,n,2*n)
        K=acb_mat(d+nf,d+nf)
        for i in range(n):
            K[i,i]=1;K[i,2*n+i]=-hs;K[n+i,n+i]=1;K[2*n+i,n+i]=-.5
        for i in range(n):
            for j in range(n):
                K[n+i,j]=-hs*HH[i,j]/2;K[2*n+i,j]=HH[n+i,j]/2
            for j in range(n+m):
                K[n+i,2*n+j]=-hs*HH[i,n+j];K[2*n+i,2*n+j]=HH[n+i,n+j]
        for i in range(m):
            for j in range(n):K[3*n+i,j]=HH[2*n+i,j]/2
            for j in range(n+m):K[3*n+i,2*n+j]=HH[2*n+i,n+j]
        FF=_matrix(F)
        for i in range(nf):
            for j in range(n+m):K[2*n+j,d+i]=FF[i,j];K[d+i,2*n+j]=FF[i,j]
        rhs=_cat(xi,pi+hs*_matrix(H[:n,:n])*xi/2,
            pi/2-_matrix(H[n:2*n,:n])*xi/2,
            -_matrix(H[2*n:,:n])*xi/2,acb_mat(nf,nc))
        z=K.solve(rhs);zh,zl=_split(z);pair=_matrix(zh)+_matrix(zl)
        xf,pf=_rows(pair,0,n),_rows(pair,n,2*n);phase=_rows(pair,2*n,d)
        eta=_cat((xi+xf)/2,phase);cot=HH*eta
        original=_cat(xf-xi-hs*_rows(phase,0,n),pf-pi-hs*_rows(cot,0,n),
            _rows(cot,n,2*n)-(pi+pf)/2,_rows(cot,2*n,len(H)))
        reaction=acb_mat(d,nc)
        rp=FF.transpose()*_rows(pair,d,d+nf)
        for i in range(n+m):
            for j in range(nc):reaction[2*n+i,j]=rp[i,j]
        framed=K*pair-rhs;assembled=_rows(framed,0,d)-reaction
        # Literal transpose tests use all final canonical coordinates.
        targets=acb_mat(d+nf,2*n)
        for i in range(2*n):targets[i,i]=1
        left=K.transpose().solve(targets)
        pairing=left.transpose()*rhs-_rows(pair,0,2*n)
        final_hi,final_lo=_split(_cat(xf,pf));eh,el=_split(eta);ch,cl=_split(cot)
        kh,kl=_split(K);rh,rl=_split(rhs)
        return dict(canonical_final_high=final_hi,canonical_final_low=final_lo,
            stage_direction_high=eh,stage_direction_low=el,
            action_direction_high=ch,action_direction_low=cl,
            solution_high=zh,solution_low=zl,operator_high=kh,operator_low=kl,
            rhs_high=rh,rhs_low=rl,original_rows=_mid(original),framed_rows=_mid(framed),
            reaction_rows=_mid(reaction),original_assembly_difference=_mid(original-assembled),
            original_rows_upper=_upper(original),framed_rows_upper=_upper(framed),
            reaction_rows_upper=_upper(reaction),assembly_difference_upper=_upper(original-assembled),
            literal_transpose_rows_upper=_upper(K.transpose()*left-targets),
            literal_pairing_difference_upper=_upper(pairing),
            exact_stored_H_and_clock_assembly=True,precision_bits=precision_bits)
    finally:ctx.prec=old


def stored_endpoint_constitutive_tangent(H,frame,canonical_high,canonical_low,*,precision_bits=192):
    """Reconstitute original v/y tangents at the true saved endpoint H.

    The same independently propagated dx/dPi is held. No momentum is
    silently recomputed from rates and no canonical source is changed.
    """
    H=np.asarray(H,complex);F=np.asarray(frame,complex)
    hi,lo=np.asarray(canonical_high,complex),np.asarray(canonical_low,complex)
    n=hi.shape[0]//2;d=len(H)-n;nf=len(F);nc=hi.shape[1]
    old=ctx.prec;ctx.prec=int(precision_bits)
    try:
        c=_matrix(hi)+_matrix(lo);x,p=_rows(c,0,n),_rows(c,n,2*n)
        target=_cat(p,acb_mat(d-n,nc));rhs=_cat(target-_matrix(H[n:,:n])*x,acb_mat(nf,nc))
        K=_matrix(np.block([[H[n:,n:],F.T],[F,np.zeros((nf,nf),complex)]]))
        z=K.solve(rhs);zh,zl=_split(z);z=_matrix(zh)+_matrix(zl)
        eta=_cat(x,_rows(z,0,d));eh,el=_split(eta)
        original=_matrix(H[n:])*eta-target;reaction=_matrix(F.T)*_rows(z,d,d+nf)
        return dict(direction_high=eh,direction_low=el,solution_high=zh,solution_low=zl,
            original_rows=_mid(original),reaction_rows=_mid(reaction),
            original_rows_upper=_upper(original),framed_rows_upper=_upper(K*z-rhs),
            reaction_rows_upper=_upper(reaction),
            original_assembly_difference_upper=_upper(original+reaction-_rows(K*z-rhs,0,d)),
            canonical_position_and_momentum_unchanged=True,precision_bits=precision_bits)
    finally:ctx.prec=old
