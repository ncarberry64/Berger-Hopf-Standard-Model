"""Fixed-adjoint weak-source actions and conditional canonical responses.

Only the completion relative to the already represented D_b H is supplied
as an additional action force. Rate work has its own true-face role. The
source covector is an analytic transpose; no Hilbert conjugation occurs.
"""
import numpy as np
from flint import acb_mat,ctx
from .muon_stored_admission_correction import _matrix,_upper
from .muon_stored_fiber_canonical_tangent import _rows,_cat,_split


def fixed_source_rate_time_actions(G,H,G_clock,H_clock,rate,da,dda,
        U,U_rate,alpha,alpha_rate,third_state_U,third_state_alpha,*,
        normal_velocity,amplitude=1,amplitude_coordinate_first=0):
    """Differentiate Fr_eta U and its independent left action along t.

    H_clock is the complete same-action time derivative, including the
    source-reference clock once. G_clock is likewise total Dt G. Directions
    are fixed tests whose stated rates are supplied, not D_U alpha.
    """
    G,H,Gt,Ht,r,d,dd,U,Ut,a,at,TU,Ta=map(lambda x:np.asarray(x,complex),
        (G,H,G_clock,H_clock,rate,da,dda,U,U_rate,alpha,alpha_rate,
         third_state_U,third_state_alpha))
    n=len(G);v=int(normal_velocity);psi=complex(amplitude);pt=complex(amplitude_coordinate_first)
    if H.shape!=(n,n)or Ht.shape!=H.shape or dd.shape!=H.shape or U.shape!=Ut.shape or TU.shape!=U.shape or a.shape!=(n,)or Ta.shape!=a.shape:
        raise ValueError('complete same-action time coefficients and both fixed-test rates required')
    dt=d@r;dr=dd@r
    def action(z,zt,tz):
        rate_action=psi*(d[:,None]*(H[v]@z)[None,:]+G[v]*(dd@z))
        time_action=pt*(d[:,None]*(H[v]@z)[None,:]+G[v]*(dd@z))
        time_action+=psi*(dr[:,None]*(H[v]@z)[None,:]+d[:,None]*(Ht[v]@z+H[v]@zt)[None,:]
            +Gt[v]*(dd@z)+G[v]*(tz+dd@zt))
        return rate_action,time_action
    rr,rt=action(U,Ut,TU);lr,lt=action(a[:,None],at[:,None],Ta[:,None])
    return dict(right_rate=rr,right_rate_time=rt,left_rate=lr[:,0],left_rate_time=lt[:,0],
        proper_coefficient_time_first=dt,proper_gradient_time_first=dr,
        fixed_adjoint_source_variation=True)


def fixed_source_completion(actions,time_actions,U,U_rate,alpha,alpha_rate):
    """Required full-vector deltaK X, with its local product-rule identity.

    The effective bulk is alternative to the unintegrated state/rate
    representation. True endpoint work must be retained separately.
    """
    U,Ut,a,at=map(lambda x:np.asarray(x,complex),(U,U_rate,alpha,alpha_rate))
    rs=actions['source_right_state_action']-actions['ordinary_Hb_right_action']
    ls=actions['source_transpose_left_state_action']-actions['ordinary_Hb_transpose_left_action']
    rr=actions['source_right_rate_action'];lr=actions['source_transpose_left_rate_action']
    rt=time_actions['right_rate_time'];lt=time_actions['left_rate_time']
    rg=rs-rt;lg=ls-lt
    weak=a@rs+at@rr;weak_left=ls@U+lr@Ut
    boundary_derivative=at@rr+a@rt
    return dict(right_state_completion=rs,right_rate_completion=rr,
        left_state_completion=ls,left_rate_completion=lr,
        right_effective_completion=rg,left_effective_completion=lg,
        right_rate_time=rt,left_rate_time=lt,
        unintegrated_completion_pair=weak,unintegrated_transpose_pair=weak_left,
        effective_completion_pair=a@rg,rate_work_time_first=boundary_derivative,
        exact_product_rule_rows=weak-a@rg-boundary_derivative,
        independent_transpose_pair_rows=weak-weak_left,
        ordinary_Hb_excluded=True,moving_adjoint_under_U_excluded=True)


def conditional_canonical_force_cell(H,step,frames,initial_high,initial_low,
        force,*,analytic_transpose=False,precision_bits=192):
    """Apply a complete action force to every original canonical cell row.

    For the left application H.T is used without conjugation. These
    initial-value applications leave all outer returns available; they do
    not prescribe a physical terminal graph or a coupled matching state.
    """
    H,F,gh=map(lambda x:np.asarray(x,complex),(H,frames,force))
    if analytic_transpose:H=H.T
    if gh.ndim==1:gh=gh[:,None]
    hi,lo=map(lambda x:np.asarray(x,complex),(initial_high,initial_low))
    n=len(hi)//2;nc=hi.shape[1];m=len(H)-2*n;nf=len(F);d=3*n+m
    if gh.shape!=(len(H),nc):raise ValueError('all x/v/y force rows and same canonical columns required')
    old=ctx.prec;ctx.prec=int(precision_bits)
    try:
        g=_matrix(gh);h=_matrix(np.array([[step]],complex))[0,0]
        HH=_matrix(H);FF=_matrix(F);initial=_matrix(hi)+_matrix(lo)
        xi,pi=_rows(initial,0,n),_rows(initial,n,2*n)
        # Assemble only the RHS actually consumed. No full transfer matrix,
        # inverse or unused212-target adjoint batch is constructed.
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
        for i in range(nf):
            for j in range(n+m):K[2*n+j,d+i]=FF[i,j];K[d+i,2*n+j]=FF[i,j]
        rhs=_cat(xi,pi+h*_matrix(H[:n,:n])*xi/2,
            pi/2-_matrix(H[n:2*n,:n])*xi/2,
            -_matrix(H[2*n:,:n])*xi/2,acb_mat(nf,nc))
        forcing=_cat(acb_mat(n,nc),h*_rows(g,0,n),-_rows(g,n,2*n),-_rows(g,2*n,len(H)),acb_mat(nf,nc))
        z=K.solve(rhs+forcing);x,p=_rows(z,0,n),_rows(z,n,2*n);phase=_rows(z,2*n,d)
        eta=_cat((xi+x)/2,phase);cot=_matrix(H)*eta+g
        original=_cat(x-xi-h*_rows(phase,0,n),p-pi-h*_rows(cot,0,n),
            _rows(cot,n,2*n)-(pi+p)/2,_rows(cot,2*n,len(H)))
        framed=K*z-rhs-forcing;reaction=acb_mat(d,nc)
        if nf:
            rho=_matrix(F.T)*_rows(z,d,d+nf)
            for i in range(n+m):
                for j in range(nc):reaction[2*n+i,j]=rho[i,j]
        fields=dict(final_canonical=_cat(x,p),stage=eta,action_cotangent=cot,
            solution=z,original_rows=original,named_reaction_rows=reaction,
            framed_rows=framed,original_assembly_rows=original+reaction-_rows(framed,0,d))
        arrays={}
        for key,value in fields.items():arrays[key+'_high'],arrays[key+'_low']=_split(value)
        return dict(arrays=arrays,original_rows_upper=_upper(original),
            reaction_upper=_upper(reaction),framed_rows_upper=_upper(framed),
            assembly_upper=_upper(fields['original_assembly_rows']),analytic_transpose=analytic_transpose,
            physical_terminal_graph_selected=False)
    finally:ctx.prec=old
