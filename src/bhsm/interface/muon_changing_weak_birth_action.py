"""Changing-coefficient chronological weak action and explicit source ports.

The full inherited source is pulled back at the parent birth parameters;
it is not added to the standalone parent bulk. Endpoint source/domain
constraints and outer momentum targets remain separate from the matrix.
"""
import numpy as np
from .muon_coupled_phase_trace_projection import _solve


def midpoint_weak_lift(step,dynamic_count=106,algebraic_count=40):
    h=complex(step);n=int(dynamic_count);m=int(algebraic_count)
    if h==0 or not np.isfinite(h):raise ValueError('actual nonzero chronological step required')
    T=np.zeros((2*n+m,2*n+m),complex)
    T[:n,:n]=T[:n,n:2*n]=np.eye(n)/2
    T[n:2*n,:n]=-np.eye(n)/h;T[n:2*n,n:2*n]=np.eye(n)/h
    T[2*n:,2*n:]=np.eye(m)
    return T


def chronological_arm_weak_action(hessians,gradients,steps):
    """Original midpoint action twojets; coefficient derivatives stay weak.

    Node x values and independent cell y variables are retained. This
    includes Lxx/Lxv/Lvx/Lvv/Lxy/Lvy/Lyx/Lyv/Lyy without imposing v=iωx.
    """
    H=np.asarray(hessians,complex);g=np.asarray(gradients,complex);hs=np.asarray(steps,complex)
    if H.ndim!=3 or H.shape[1:]!=(252,252) or g.shape!=(len(H),252) or hs.shape!=(len(H),):
        raise ValueError('all actual original252 cell actions and clocks required')
    nc=len(H);dim=(nc+1)*106+nc*40;W=np.zeros((dim,dim),complex);f=np.zeros(dim,complex);lifts=[]
    for k,h in enumerate(hs):
        local=midpoint_weak_lift(h);ids=np.r_[np.arange(k*106,(k+2)*106),
                                           (nc+1)*106+k*40+np.arange(40)]
        T=np.zeros((252,dim),complex);T[:,ids]=local;lifts.append(T)
        W+=h*T.T@H[k]@T;f+=h*T.T@g[k]
    return dict(matrix=W,gradient=f,cell_lifts=np.asarray(lifts),steps=hs,
        node_count=nc+1,cell_count=nc,dynamic_count=106,algebraic_count=40,
        variable_count=dim,coordinate_time_used=True,frequency_substitution_used=False)


def affine_parent_master_map(time):
    """Exact retained affine parent source map at held reference clock."""
    T=np.eye(252,dtype=complex);t=complex(time)
    T[np.arange(37),106+np.arange(37)]=t;T[37,143]=t
    return T


def inherited_source_weak_blocks(child_lifts,steps,child_full_hessians,parent_source_hessians,
                                 child_full_gradients,parent_source_gradients,times):
    """Complete Hpp/Hpc/Hcp pullback of CHILD source action, once.

    The supplied full graph subtracts its own-parent source action before
    integration. All nonlinear profile J2 contacts are already in Hpp.
    Parent birth parameters remain explicit source coordinates, not free
    stationary bulk variables or a grafted future parent trajectory.
    """
    lifts=np.asarray(child_lifts,complex);d=lifts.shape[2];nc=len(lifts)
    cross=np.zeros((d,252),complex);reverse=np.zeros((252,d),complex)
    source=np.zeros((252,252),complex);sourceg=np.zeros(252,complex)
    ccmotion=[];maps=[]
    for j in range(nc):
        h=complex(steps[j]);H=np.asarray(child_full_hessians[j],complex)
        own=np.asarray(parent_source_hessians[j],complex);S=affine_parent_master_map(times[j]);maps.append(S)
        cross+=h*lifts[j].T@H[252:,:252]@S
        reverse+=h*S.T@H[:252,252:]@lifts[j]
        source+=h*S.T@(H[:252,:252]-own)@S
        sourceg+=h*S.T@(child_full_gradients[j][:252]-parent_source_gradients[j])
        ccmotion.append(H[252:,252:])
    return dict(child_to_source=cross,source_to_child=reverse,source_self=source,
                source_gradient=sourceg,parent_affine_master_maps=np.asarray(maps),
                restricted_child_hessians=np.asarray(ccmotion),parent_bulk_feedback_added=False)


def constrained_weak_source_response(matrix,source_gradient,constraint_map,constraint_value,
                                     literal_target=None):
    """Signed conditional boundary action response, retaining every row.

    This fixed outer-coordinate application returns its outer momentum
    defect for the separate IVP/exterior matching equation. It does not
    replace fixed incoming momentum by a selected Euclidean representative.
    """
    W=np.asarray(matrix,complex);f=np.asarray(source_gradient,complex)
    C=np.asarray(constraint_map,complex);b=np.asarray(constraint_value,complex);n=len(W)
    if (W.shape!=(n,n)or f.ndim not in(1,2)or f.shape[0]!=n or C.ndim!=2
            or C.shape[1]!=n or b.shape!=(len(C),)+f.shape[1:]):
        raise ValueError('complete original weak source and explicit endpoint conditions required')
    K=np.block([[W,C.T],[C,np.zeros((len(C),len(C)),complex)]])
    rhs=np.r_[-f,b];z,rs,cs=_solve(K,rhs)
    target=np.zeros(n,complex)if literal_target is None else np.asarray(literal_target,complex)
    p,_,_=_solve(K.T,np.r_[target,np.zeros(len(C),complex)])
    q=z[:n];traction=W@q+f
    return dict(solution=q,reactions=z[n:],traction=traction,
        original_saddle=K,original_rhs=rhs,original_saddle_rows=K@z-rhs,
        original_weak_rows=traction+C.T@z[n:],original_constraint_rows=C@q-b,
        literal_transpose=p,literal_transpose_rows=K.T@p-np.r_[target,np.zeros(len(C))],
        literal_pairing_difference=target@q-p@rhs,row_scale=rs,column_scale=cs,
        quadratic_action_stationarity_difference=((W+W.T)/2-W)@q,
        conditional_outer_coordinate_domain=True,physical_IVP_or_matching_claimed=False)
