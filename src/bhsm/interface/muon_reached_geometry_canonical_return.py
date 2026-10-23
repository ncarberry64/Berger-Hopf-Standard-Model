"""Changing canonical geometry-source return on a supplied reached history.

The three sources are declared computational geometry covectors. They do
not replace the 67 birth directions or select an outgoing exterior graph.
Every original midpoint/Legendre/Gauss row and literal transpose remains.
"""
import numpy as np
from flint import acb, acb_mat, ctx
from .muon_stored_admission_correction import _matrix, _mid, _upper
from .muon_stored_fiber_canonical_tangent import _rows, _cat, _split


def structural_geometry_port_lift(trace, columns=(0, 1, 37)):
    """Hold all other x coefficients while varying the three named ports.

    This coordinate lift is an explicit trial, not a Euclidean least-norm
    or an action-selected normal mode. No field/multiplier is set to zero
    in the subsequent canonical solve.
    """
    B=np.asarray(trace,complex);ids=np.asarray(columns,int)
    if B.ndim!=2 or B.shape[0]!=3 or ids.shape!=(3,):
        raise ValueError('attachment2 plus proper-normal map and named columns required')
    L=np.zeros((B.shape[1],3),complex);L[ids]=np.linalg.solve(B[:,ids],np.eye(3))
    return dict(lift=L,columns=ids,trace_lift_rows=B@L-np.eye(3),
                minor_condition=float(np.linalg.cond(B[:,ids])))


def sourced_original_canonical_batch(H, step, frames, initial_high,
        initial_low, source_gradient, final_position_target, *, precision_bits=192):
    """Execute a batch of the literal sourced midpoint variational equations.

    Sources enter delta Pi_dot=H_x delta eta+g_x and the independent
    constitutive/Gauss rows. The frame border is a numerical chart whose
    reaction remains distinct from the unbordered original equations.
    Acb arithmetic covers only the exact supplied binary coefficients.
    """
    H=np.asarray(H,complex);F=np.asarray(frames,complex)
    hi,lo=np.asarray(initial_high,complex),np.asarray(initial_low,complex)
    g=np.asarray(source_gradient,complex);target=np.asarray(final_position_target,complex)
    if hi.ndim!=2 or lo.shape!=hi.shape or hi.shape[0]%2:
        raise ValueError('independent complete x/Pi high-low batch required')
    n=hi.shape[0]//2;m=len(H)-2*n;nf=len(F);nc=hi.shape[1];d=3*n+m
    if H.shape!=(2*n+m,)*2 or m<1 or F.shape!=(nf,n+m) or g.shape!=(len(H),nc) or target.ndim!=2 or target.shape[1]!=n or not step:
        raise ValueError('same full Hessian/source/frame/target and nonzero clock required')
    old=ctx.prec;ctx.prec=int(precision_bits)
    try:
        h=acb(complex(step).real,complex(step).imag);HH=_matrix(H);gg=_matrix(g)
        c=_matrix(hi)+_matrix(lo);xi,pi=_rows(c,0,n),_rows(c,n,2*n)
        K=acb_mat(d+nf,d+nf)
        for i in range(n):
            K[i,i]=1;K[i,2*n+i]=-h;K[n+i,n+i]=1;K[2*n+i,n+i]=-.5
        for i in range(n):
            for j in range(n):
                K[n+i,j]=-h*HH[i,j]/2;K[2*n+i,j]=HH[n+i,j]/2
            for j in range(n+m):
                K[n+i,2*n+j]=-h*HH[i,n+j];K[2*n+i,2*n+j]=HH[n+i,n+j]
        for i in range(m):
            for j in range(n):K[3*n+i,j]=HH[2*n+i,j]/2
            for j in range(n+m):K[3*n+i,2*n+j]=HH[2*n+i,n+j]
        FF=_matrix(F)
        for i in range(nf):
            for j in range(n+m):K[2*n+j,d+i]=FF[i,j];K[d+i,2*n+j]=FF[i,j]
        rhs=_cat(xi,pi+h*(_matrix(H[:n,:n])*xi/2+_rows(gg,0,n)),
            pi/2-_matrix(H[n:2*n,:n])*xi/2-_rows(gg,n,2*n),
            -_matrix(H[2*n:,:n])*xi/2-_rows(gg,2*n,len(H)),acb_mat(nf,nc))
        z=K.solve(rhs);zh,zl=_split(z);z=_matrix(zh)+_matrix(zl)
        xf,pf=_rows(z,0,n),_rows(z,n,2*n);phase=_rows(z,2*n,d)
        eta=_cat((xi+xf)/2,phase);cot=HH*eta+gg
        rows=_cat(xf-xi-h*_rows(phase,0,n),pf-pi-h*_rows(cot,0,n),
            _rows(cot,n,2*n)-(pi+pf)/2,_rows(cot,2*n,len(H)))
        reaction=FF.transpose()*_rows(z,d,d+nf) if nf else acb_mat(n+m,nc)
        T=acb_mat(d+nf,len(target))
        tt=_matrix(target.T)
        for i in range(n):
            for j in range(len(target)):T[i,j]=tt[i,j]
        ell=K.transpose().solve(T)
        direct=_matrix(target)*xf;dual=ell.transpose()*rhs
        ch,cl=_split(_cat(xf,pf));eh,el=_split(eta);qh,ql=_split(cot)
        return dict(canonical_final_high=ch,canonical_final_low=cl,
            stage_direction_high=eh,stage_direction_low=el,
            action_direction_high=qh,action_direction_low=ql,
            source_gradient=g,original_rows=_mid(rows),original_rows_upper=_upper(rows),
            original_Gauss_upper=_upper(_rows(rows,3*n,d)),
            framed_rows_upper=_upper(K*z-rhs),frame_reaction_rows=_mid(reaction),
            frame_reaction_upper=_upper(reaction),frame_rows_upper=_upper(FF*phase) if nf else 0.,
            literal_target_value=_mid(direct),literal_transpose_target_value=_mid(dual),
            literal_pairing_upper=_upper(direct-dual),literal_transpose_rows_upper=_upper(K.transpose()*ell-T),
            source_free_or_zero_initial_response_is_not_exterior_DtN=True)
    finally:ctx.prec=old


def complete_natural_boundary_work(initial_high,initial_low,final_high,final_low,
        initial_Pi,final_Pi,*,coordinate_interval,precision_bits=192):
    """All supplied directions, both actual endpoint cotangents, no Y=0 fit."""
    hi,lo=np.asarray(initial_high,complex),np.asarray(initial_low,complex)
    n=len(initial_Pi);h=complex(coordinate_interval)
    if hi.shape!=lo.shape or hi.shape[0]!=2*n or h==0:
        raise ValueError('same full canonical directions and actual interval required')
    old=ctx.prec;ctx.prec=int(precision_bits)
    try:
        a=_matrix(hi)+_matrix(lo);b=_matrix(final_high)+_matrix(final_low)
        first=_matrix(np.asarray(initial_Pi)[None])*_rows(a,0,n)
        last=_matrix(np.asarray(final_Pi)[None])*_rows(b,0,n)
        work=last-first;wh,wl=_split(work);sh,sl=_split(work/acb(h.real,h.imag))
        return dict(initial_cotangent_work=_mid(first),terminal_cotangent_work=_mid(last),
            complete_boundary_work_high=wh,complete_boundary_work_low=wl,
            clock_scaled_boundary_work_high=sh,clock_scaled_boundary_work_low=sl,
            stored_work_radius_upper=_upper(work-_matrix(wh)-_matrix(wl)),
            coordinate_interval=np.array(h),explicit_inherited_source_work_not_inferred_zero=True)
    finally:ctx.prec=old
