"""Acb-preserving finite canonical applications of actual action operands.

Every original x/Pi/velocity/Gauss row and named frame reaction is retained.
Inputs may be Acb matrices or explicit high/low arrays. No matrix is cast to
binary64, no source is conjugated, and no terminal condition is prescribed.
"""
import numpy as np
from flint import acb_mat,ctx


def _ball(high,low=None):
    from bhsm.interface.muon_stored_admission_correction import _matrix
    value=high if isinstance(high,acb_mat)else _matrix(np.asarray(high,complex))
    if low is not None:value+=low if isinstance(low,acb_mat)else _matrix(np.asarray(low,complex))
    return value


def phase_from_cauchy(H,F,initial,force,*,precision_bits=192):
    """Solve the actual original constitutive rows at one fixed epoch."""
    from bhsm.interface.muon_stored_admission_correction import _matrix,_upper
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _rows,_cat,_split
    old=ctx.prec;ctx.prec=precision_bits
    try:
        H,C,Q,g=map(_ball,(H,F,initial,force));n=Q.nrows()//2;dim=H.nrows();m=dim-2*n;nf=C.nrows();nc=Q.ncols()
        if H.ncols()!=dim or C.ncols()!=dim-n or g.nrows()!=dim or g.ncols()!=nc:raise ValueError('full same-epoch H/force and explicit canonical/frame dimensions required')
        x,p=_rows(Q,0,n),_rows(Q,n,2*n);K=acb_mat(dim-n+nf,dim-n+nf)
        for i in range(dim-n):
            for j in range(dim-n):K[i,j]=H[n+i,n+j]
            for j in range(nf):K[i,dim-n+j]=C[j,i]
        for i in range(nf):
            for j in range(dim-n):K[dim-n+i,j]=C[i,j]
        rhs=_cat(p-acb_mat([[sum((H[n+i,j]*x[j,c]for j in range(n)),0)for c in range(nc)]for i in range(n)])-_rows(g,n,2*n),
            -acb_mat([[sum((H[2*n+i,j]*x[j,c]for j in range(n)),0)for c in range(nc)]for i in range(m)])-_rows(g,2*n,dim),acb_mat(nf,nc))
        solution=K.solve(rhs);phase=_rows(solution,0,dim-n);stage=_cat(x,phase);cot=H*stage+g
        original=_cat(_rows(cot,n,2*n)-p,_rows(cot,2*n,dim));framed=K*solution-rhs
        values=dict(stage=stage,action_cotangent=cot,original_constitutive_rows=original,framed_rows=framed,frame_reactions=_rows(solution,dim-n,dim-n+nf))
        arrays={}
        for key,value in values.items():arrays[key+'_high'],arrays[key+'_low']=_split(value)
        return dict(arrays=arrays,values=values,original_rows_upper=_upper(original),framed_rows_upper=_upper(framed),physical_domain_selected=False)
    finally:ctx.prec=old


def canonical_force_cell(H,step,F,initial,force,*,analytic_transpose=False,precision_bits=192):
    """Apply a true MP action Hessian to all original finite canonical rows."""
    from bhsm.interface.muon_stored_admission_correction import _matrix,_upper
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _rows,_cat,_split
    old=ctx.prec;ctx.prec=precision_bits
    try:
        H,C,Q,g=map(_ball,(H,F,initial,force))
        if analytic_transpose:H=H.transpose()
        n=Q.nrows()//2;nc=Q.ncols();dim=H.nrows();m=dim-2*n;nf=C.nrows();d=dim+n;h=_matrix([[step]])[0,0]
        if H.ncols()!=dim or C.ncols()!=dim-n or g.nrows()!=dim or g.ncols()!=nc:raise ValueError('full original action/force/frame/Cauchy operands required')
        x0,p0=_rows(Q,0,n),_rows(Q,n,2*n);K=acb_mat(d+nf,d+nf)
        for i in range(n):
            K[i,i]=1;K[i,2*n+i]=-h;K[n+i,n+i]=1;K[2*n+i,n+i]=-.5
        for i in range(n):
            for j in range(n):K[n+i,j]=-h*H[i,j]/2;K[2*n+i,j]=H[n+i,j]/2
            for j in range(n+m):K[n+i,2*n+j]=-h*H[i,n+j];K[2*n+i,2*n+j]=H[n+i,n+j]
        for i in range(m):
            for j in range(n):K[3*n+i,j]=H[2*n+i,j]/2
            for j in range(n+m):K[3*n+i,2*n+j]=H[2*n+i,n+j]
        for i in range(nf):
            for j in range(n+m):K[2*n+j,d+i]=C[i,j];K[d+i,2*n+j]=C[i,j]
        def product(rows):return acb_mat([[sum((H[int(i),j]*x0[j,c]for j in range(n)),0)for c in range(nc)]for i in rows])
        rhs=_cat(x0,p0+h*product(range(n))/2,p0/2-product(range(n,2*n))/2,-product(range(2*n,dim))/2,acb_mat(nf,nc))
        forcing=_cat(acb_mat(n,nc),h*_rows(g,0,n),-_rows(g,n,2*n),-_rows(g,2*n,dim),acb_mat(nf,nc))
        z=K.solve(rhs+forcing);x,p=_rows(z,0,n),_rows(z,n,2*n);phase=_rows(z,2*n,d);stage=_cat((x0+x)/2,phase);cot=H*stage+g
        original=_cat(x-x0-h*_rows(phase,0,n),p-p0-h*_rows(cot,0,n),_rows(cot,n,2*n)-(p0+p)/2,_rows(cot,2*n,dim))
        framed=K*z-rhs-forcing;reaction=acb_mat(d,nc);rho=C.transpose()*_rows(z,d,d+nf)
        for i in range(n+m):
            for j in range(nc):reaction[2*n+i,j]=rho[i,j]
        values=dict(final_canonical=_cat(x,p),stage=stage,action_cotangent=cot,solution=z,original_rows=original,named_reaction_rows=reaction,
            framed_rows=framed,original_assembly_rows=original+reaction-_rows(framed,0,d))
        arrays={}
        for key,value in values.items():arrays[key+'_high'],arrays[key+'_low']=_split(value)
        return dict(arrays=arrays,values=values,original_rows_upper=_upper(original),reaction_upper=_upper(reaction),framed_rows_upper=_upper(framed),
            assembly_upper=_upper(values['original_assembly_rows']),analytic_transpose=analytic_transpose,physical_terminal_graph_selected=False)
    finally:ctx.prec=old
