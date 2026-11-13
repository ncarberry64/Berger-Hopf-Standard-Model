"""Finite canonical cell checked by actual action-vector applications.

The supplied Hpre is solely a numerical preconditioner. linear_action
applies the actual same-epoch child/source Hessian to the passed child
field columns and parent source columns. Original rows, source returns
and named reactions are checked and retained without forming an inverse.
"""
import numpy as np
from flint import acb,acb_mat,ctx


def canonical_cell(Hpre,step,F,initial,parent_source,linear_action,force=None,*,
        guard=2e-10,max_iterations=12,precision_bits=192,checkpoint=None,warm_values=None):
    """Solve by defect correction; unresolved iterations remain explicit.

    linear_action(child368, parent252) returns Acb child_cotangent,
    parent_cotangent252 and optional direct_child_source_gradient252.
    No old history application is repeated by this function.
    """
    from bhsm_baton_zoo_acb_current_canonical import _ball
    from bhsm.interface.muon_stored_admission_correction import _matrix,_upper
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _rows,_cat,_split
    old=ctx.prec;ctx.prec=precision_bits
    def center(A):return acb_mat([[acb(A[i,j].real.mid(),A[i,j].imag.mid())for j in range(A.ncols())]for i in range(A.nrows())])
    try:
        H,C,Q,parent=map(_ball,(Hpre,F,initial,parent_source));n=Q.nrows()//2;dim=H.nrows();m=dim-2*n;nf=C.nrows();nc=Q.ncols();d=dim+n
        if H.ncols()!=dim or C.ncols()!=dim-n or parent.nrows()!=252 or parent.ncols()!=nc:raise ValueError('explicit same-domain action/frame/Cauchy/source dimensions required')
        g=acb_mat(dim,nc)if force is None else _ball(force)
        if g.nrows()!=dim or g.ncols()!=nc:raise ValueError('complete explicit baseline/source force rows required')
        h=_matrix([[step]])[0,0];xi,pi=_rows(Q,0,n),_rows(Q,n,2*n);z=_cat(xi,pi,acb_mat(dim-n,nc),acb_mat(nf,nc))
        if warm_values is not None:
            final,stage,reaction=map(_ball,(warm_values['final_canonical'],warm_values['stage'],warm_values['named_reaction_rows']))
            if final.nrows()!=2*n or stage.nrows()!=dim or reaction.nrows()!=d:raise ValueError('exact same-cell warm schema required')
            phase=_rows(stage,n,dim);named=_rows(reaction,2*n,d)
            multiplier=(C*C.transpose()).solve(C*named)
            z=_cat(final,phase,multiplier)
        K=acb_mat(d+nf,d+nf)
        for i in range(n):K[i,i]=1;K[i,2*n+i]=-h;K[n+i,n+i]=1;K[2*n+i,n+i]=-.5
        for i in range(n):
            for j in range(n):K[n+i,j]=-h*H[i,j]/2;K[2*n+i,j]=H[n+i,j]/2
            for j in range(n+m):K[n+i,2*n+j]=-h*H[i,n+j];K[2*n+i,2*n+j]=H[n+i,n+j]
        for i in range(m):
            for j in range(n):K[3*n+i,j]=H[2*n+i,j]/2
            for j in range(n+m):K[3*n+i,2*n+j]=H[2*n+i,n+j]
        for i in range(nf):
            for j in range(n+m):K[2*n+j,d+i]=C[i,j];K[d+i,2*n+j]=C[i,j]
        records=[];status='MATRIX_FREE_CANONICAL_ITERATIONS_UNRESOLVED';previous=None
        for iteration in range(max_iterations+1):
            x,p,phase=_rows(z,0,n),_rows(z,n,2*n),_rows(z,2*n,d);eta=_cat((xi+x)/2,phase)
            applied=linear_action(eta,parent);cot=_ball(applied['child_cotangent'])+g
            if cot.nrows()!=dim or cot.ncols()!=nc:raise ValueError('actual full child action-vector application required')
            original=_cat(x-xi-h*_rows(phase,0,n),p-pi-h*_rows(cot,0,n),_rows(cot,n,2*n)-(pi+p)/2,_rows(cot,2*n,dim))
            rho=C.transpose()*_rows(z,d,d+nf);reaction=acb_mat(d,nc)
            for i in range(dim-n):
                for j in range(nc):reaction[2*n+i,j]=rho[i,j]
            framed=_cat(original+reaction,C*phase);merit=_upper(framed);record=dict(iteration=iteration,original_rows_upper=_upper(original),framed_rows_upper=merit,reaction_upper=_upper(reaction));records.append(record)
            if checkpoint:checkpoint(record)
            if _upper(original)<=guard and merit<=guard:status='ALL_ACTUAL_MATRIX_FREE_ORIGINAL_CANONICAL_ROWS_PASS';break
            if iteration==max_iterations:break
            if previous is not None and merit>previous*4:status='MATRIX_FREE_PRECONDITIONED_CORRECTION_UNSTABLE';break
            correction=K.solve(framed);proposed=z-correction;z=center(proposed)
            record['trial_center_selection_radius_upper']=_upper(proposed-z)
            previous=merit
        values=dict(actual_solver_unknown=z,final_canonical=_cat(x,p),stage=eta,action_cotangent=cot,original_rows=original,named_reaction_rows=reaction,
            framed_rows=framed,parent_source_cotangent=_ball(applied['parent_cotangent252']))
        if 'direct_child_source_gradient252'in applied:values['actual_affine_primal_source_gradient252']=_ball(applied['direct_child_source_gradient252'])
        arrays={}
        for key,value in values.items():arrays[key+'_high'],arrays[key+'_low']=_split(value)
        return dict(status=status,records=records,values=values,arrays=arrays,original_rows_upper=_upper(original),framed_rows_upper=_upper(framed),
            preconditioner_substituted_as_actual_operator=False,physical_terminal_graph_selected=False)
    finally:ctx.prec=old
