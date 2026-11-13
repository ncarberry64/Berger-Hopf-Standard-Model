"""Original signed canonical tail return with an explicit terminal graph.

The full Legendre/Gauss block and named frames determine the canonical
Jacobi generator.  A terminal graph is a required action-domain operand:
Y=0 is a finite natural-boundary control, never an outgoing tail selection.
Source coefficients and the independent action dual are analytic; no
Hilbert conjugation, positive reference, or spectral quotient is used.
"""
from __future__ import annotations

import numpy as np

from .muon_coupled_phase_trace_projection import _solve


def _finite(a, shape, name):
    a = np.asarray(a, complex)
    if a.shape != shape or not np.isfinite(a).all():
        raise ValueError('complete finite '+name+' required')
    return a


def full_canonical_jacobi_generator(hessian, dynamic_count, frames,
        source_gradient, frame_source):
    """Return the actual (delta x, own delta Pi) generator and compatibility.

    D phase+F.T rho=[delta Pi-H_vx delta x-g_v; -H_yx delta x-g_y],
    F phase=frame_source.  xdot=delta v and Pidot=H_x,* delta eta+g_x.
    The reaction rows must vanish on an admissible canonical source; they
    remain equations and are not deleted from arbitrary supplied data.
    """
    H = np.asarray(hessian, complex); n = int(dynamic_count)
    m = len(H)-2*n; d = n+m; F = np.asarray(frames, complex)
    if n < 1 or m < 1 or F.ndim != 2 or F.shape[1] != d:
        raise ValueError('full x/v/y chart and named frames required')
    H = _finite(H, (2*n+m,)*2, 'original signed Hessian')
    F = _finite(F, F.shape, 'frame map')
    g = _finite(source_gradient, (len(H),), 'full action source')
    fs = _finite(frame_source, (len(F),), 'frame source')
    K = np.block([[H[n:, n:], F.T],
                  [F, np.zeros((len(F), len(F)), complex)]])
    rhs = np.zeros((len(K), 2*n+1), complex)
    rhs[:d, :n] = -H[n:, :n]
    rhs[:n, n:2*n] = np.eye(n)
    rhs[:d, -1] = -g[n:]; rhs[d:, -1] = fs
    z, rs, cs = _solve(K, rhs); phase = z[:d]
    J = np.empty((2*n, 2*n), complex)
    J[:n] = phase[:n, :2*n]
    J[n:] = H[:n, n:]@phase[:, :2*n]
    J[n:, :n] += H[:n, :n]
    f = np.r_[phase[:n, -1], H[:n, n:]@phase[:, -1]+g[:n]]
    embedding = np.zeros((len(H), 2*n), complex)
    embedding[:n, :n] = np.eye(n); embedding[n:] = phase[:, :2*n]
    offset = np.r_[np.zeros(n, complex), phase[:, -1]]
    return dict(generator=J, forcing=f, action_embedding=embedding,
        action_source_embedding=offset, compatibility_map=z[d:, :2*n],
        compatibility_source=z[d:, -1], original_phase_operator=K,
        original_phase_rhs=rhs, original_phase_solution=z,
        original_phase_rows=K@z-rhs, row_scale=rs, column_scale=cs,
        full_Lyy_and_original_Gauss_rows_retained=True,
        own_canonical_momentum_not_joint_parent_momentum=True,
        outgoing_or_physical_tail_selected=False)


def full_canonical_jacobi_generator_first(hessian, hessian_first,
        dynamic_count, frames, frames_first, source_gradient,
        source_gradient_first, frame_source, frame_source_first):
    """Differentiate both full constitutive blocks and the moving frame.

    This acts on the SAME independent canonical x/Pi and analytic source
    coordinates.  Time-dependent coefficients or source-domain contacts
    must be supplied explicitly; this function does not freeze them.
    """
    base=full_canonical_jacobi_generator(hessian,dynamic_count,frames,
        source_gradient,frame_source)
    H=np.asarray(hessian,complex);n=int(dynamic_count);d=len(H)-n
    F=np.asarray(frames,complex);nf=len(F)
    dH=_finite(hessian_first,H.shape,'Hessian first')
    dF=_finite(frames_first,F.shape,'frame first')
    dg=_finite(source_gradient_first,(len(H),),'action source first')
    dfs=_finite(frame_source_first,(nf,),'frame source first')
    K=base['original_phase_operator'];z=base['original_phase_solution']
    dK=np.block([[dH[n:,n:],dF.T],[dF,np.zeros((nf,nf),complex)]])
    dr=np.zeros_like(base['original_phase_rhs']);dr[:d,:n]=-dH[n:,:n]
    dr[:d,-1]=-dg[n:];dr[d:,-1]=dfs
    dz=_solve(K,dr-dK@z)[0]
    J=np.empty((2*n,2*n),complex);J[:n]=dz[:n,:2*n]
    J[n:]=dH[:n,n:]@z[:d,:2*n]+H[:n,n:]@dz[:d,:2*n]
    J[n:,:n]+=dH[:n,:n]
    f=np.r_[dz[:n,-1],dH[:n,n:]@z[:d,-1]+H[:n,n:]@dz[:d,-1]+dg[:n]]
    E=np.zeros_like(base['action_embedding']);E[n:]=dz[:d,:2*n]
    return dict(base=base,generator_first=J,forcing_first=f,
        action_embedding_first=E,action_source_embedding_first=np.r_[np.zeros(n),dz[:d,-1]],
        compatibility_map_first=dz[d:,:2*n],compatibility_source_first=dz[d:,-1],
        original_phase_operator_first=dK,original_phase_rhs_first=dr,
        original_phase_solution_first=dz,original_phase_first_rows=K@dz+dK@z-dr,
        moving_frame_source_and_full_Lyy_contacts_retained=True,
        source_tangent_coefficients_conjugated=False)


def full_canonical_midpoint_transfer(hessian, dynamic_count, frames,
        source_gradient, frame_source, step):
    """Exact affine canonical transfer of the supplied signed midpoint cell.

    The Cayley map uses the full constitutive generator, not a frozen
    frequency substitution. Every original first/second-face, Legendre
    and algebraic row is returned, including explicit frame reactions.
    """
    h=complex(step)
    if h==0 or not np.isfinite(h):raise ValueError('actual nonzero cell clock required')
    a=full_canonical_jacobi_generator(hessian,dynamic_count,frames,
        source_gradient,frame_source)
    H=np.asarray(hessian,complex);g=np.asarray(source_gradient,complex)
    n=int(dynamic_count);I=np.eye(2*n,dtype=complex);J=a['generator'];f=a['forcing']
    result=_solve(I-h*J/2,np.c_[I+h*J/2,h*f])[0]
    M=result[:,:2*n];r=result[:,-1]
    initial=np.c_[I,np.zeros(2*n)];final=np.c_[M,r];mid=(initial+final)/2
    eta=a['action_embedding']@mid
    eta[:,-1]+=a['action_source_embedding']
    cot=H@eta;cot[:,-1]+=g
    rho=a['compatibility_map']@mid;rho[:,-1]+=a['compatibility_source']
    rows=np.vstack((final[:n]-initial[:n]-h*eta[n:2*n],
        final[n:]-initial[n:]-h*cot[:n],cot[n:2*n]-mid[n:],cot[2*n:]))
    reaction=np.zeros_like(rows);reaction[2*n:]=np.asarray(frames,complex).T@rho
    return dict(transfer=M,forcing=r,midpoint_action_lift=eta,
        original358_rows=rows,original358_frame_reaction_rows=reaction,
        original358_rows_with_named_reactions=rows+reaction,
        frame_reaction_map=rho[:,:2*n],frame_reaction_source=rho[:,-1],
        initial_action_cotangent=h*cot[:n]/2-cot[n:2*n],
        final_action_cotangent=h*cot[:n]/2+cot[n:2*n],
        named_frame_rows=np.asarray(frames,complex)@eta[n:]
            -np.c_[np.zeros((len(frames),2*n)),np.asarray(frame_source,complex)],
        canonical_generator_application=a,actual_signed_midpoint_clock=h,
        physical_tail_or_new_compatible_data_selected=False)


def _packet(a, n):
    required = ('transfer', 'forcing', 'terminal_matrix', 'terminal_source')
    if any(k not in a for k in required):
        raise ValueError('explicit transfer, forcing and terminal graph in every jet required')
    return [_finite(a[k], s, k) for k, s in zip(required,
        ((2*n, 2*n), (2*n,), (n, n), (n,)))]


def _product(a, b):
    return [a[0]@b[0], a[1]@b[0]+a[0]@b[1],
        a[2]@b[0]+a[0]@b[2],
        a[3]@b[0]+a[1]@b[2]+a[2]@b[1]+a[0]@b[3]]


def _inverse_action(K, rhs):
    answer = [_solve(K[0], rhs[0])[0]]
    answer.append(_solve(K[0], rhs[1]-K[1]@answer[0])[0])
    answer.append(_solve(K[0], rhs[2]-K[2]@answer[0])[0])
    answer.append(_solve(K[0], rhs[3]-K[3]@answer[0]
        -K[1]@answer[2]-K[2]@answer[1])[0])
    return answer


def canonical_terminal_return_two_jet(base, first_a, first_b, mixed):
    """Pull Pi_T=Y_T x_T+s_T back through the full forced canonical flow.

    For M=(A B;C D), forcing=(rq,rp),
      (D-Y_T B) Pi_birth=(Y_T A-C)x_birth+s_T+Y_T rq-rp.
    Both ordered inverse contacts, moving terminal graph and source return
    are retained.  The child initial OUTWARD conormal is -Pi_birth.
    A singular graph chart is reported by the solve, never regularized.
    """
    M = np.asarray(base.get('transfer'), complex)
    if M.ndim != 2 or M.shape[0] != M.shape[1] or len(M)%2:
        raise ValueError('complete even-dimensional canonical transfer required')
    n = len(M)//2
    jets = [_packet(p, n) for p in (base, first_a, first_b, mixed)]
    Mj, fj, Yj, sj = map(list, zip(*jets))
    A = [x[:n, :n] for x in Mj]; B = [x[:n, n:] for x in Mj]
    C = [x[n:, :n] for x in Mj]; D = [x[n:, n:] for x in Mj]
    YB = _product(Yj, B); YA = _product(Yj, A)
    Yrq = _product(Yj, [x[:n] for x in fj])
    K = [D[k]-YB[k] for k in range(4)]
    R = [YA[k]-C[k] for k in range(4)]
    r = [sj[k]+Yrq[k]-fj[k][n:] for k in range(4)]
    rhs = [np.c_[R[k], r[k]] for k in range(4)]
    W = _inverse_action(K, rhs)
    names = ('value', 'first_a', 'first_b', 'mixed')
    residuals = [K[0]@W[0]-rhs[0],
        K[0]@W[1]+K[1]@W[0]-rhs[1],
        K[0]@W[2]+K[2]@W[0]-rhs[2],
        K[0]@W[3]+K[1]@W[2]+K[2]@W[1]+K[3]@W[0]-rhs[3]]
    result = dict(original_graph_operator=np.asarray(K),
        original_graph_rhs=np.asarray(rhs), original_graph_rows=np.asarray(residuals),
        graph_condition_number=float(np.linalg.cond(K[0])),
        terminal_graph_is_explicit=True, physical_terminal_domain_identification_performed=False,
        finite_natural_terminal_zero_is_control_only=True,
        analytic_source_coefficients_conjugated=False,
        original_signed_action_or_operator_replaced=False,
        outgoing_retarded_support_domain_selected_by_this_consumer=False)
    for name, w in zip(names, W):
        result[name] = dict(birth_momentum_matrix=w[:, :n],
            birth_momentum_source=w[:, n],
            child_initial_outward_conormal_matrix=-w[:, :n],
            child_initial_outward_conormal_source=-w[:, n])
    return result


def literal_terminal_current_two_jet(base, first_a, first_b, mixed,
        target_base, target_first_a, target_first_b, target_mixed):
    """Pull literal initial/final targets through the SAME forced return.

    Every target jet supplies left_initial, left_final and direct.
    The independently solved graph transpose verifies the coefficient and
    direct source contractions; no dagger or additional Gram is inserted.
    """
    a = canonical_terminal_return_two_jet(base, first_a, first_b, mixed)
    n = len(a['value']['birth_momentum_source'])
    ps = [_packet(p, n) for p in (base, first_a, first_b, mixed)]
    Ms, fs, _, _ = map(list, zip(*ps))
    li=[]; lf=[]; direct=[]
    shape=np.asarray(target_base.get('left_initial')).shape
    if len(shape)!=2 or shape[1]!=2*n:
        raise ValueError('literal target rows on full canonical trace required')
    for t in (target_base, target_first_a, target_first_b, target_mixed):
        if any(k not in t for k in ('left_initial','left_final','direct')):
            raise ValueError('every independent literal target/source jet required')
        li.append(_finite(t['left_initial'], shape, 'initial target'))
        lf.append(_finite(t['left_final'], shape, 'final target'))
        direct.append(_finite(t['direct'], (shape[0],), 'direct current'))
    lfm=_product(lf, Ms); total=[li[k]+lfm[k] for k in range(4)]
    q=[l[:, :n] for l in total]; p=[l[:, n:] for l in total]
    K=list(a['original_graph_operator']); rhs=list(a['original_graph_rhs'])
    dual=_inverse_action([k.T for k in K], [x.T for x in p])
    returned=_product([x.T for x in dual], rhs)
    force=_product(lf, fs)
    W=[np.c_[a[k]['birth_momentum_matrix'],a[k]['birth_momentum_source']]
       for k in ('value','first_a','first_b','mixed')]
    primal=_product(p, W)
    out=dict(return_application=a, literal_transpose_solution=np.asarray(dual),
        literal_transpose_pairing_rows=np.asarray([returned[k]-primal[k] for k in range(4)]),
        source_or_target_coefficients_conjugated=False,
        physical_current_pole_or_Pauli_selected=False)
    for k,name in enumerate(('value','first_a','first_b','mixed')):
        out[name]=dict(birth_coordinate_target=q[k]+returned[k][:,:n],
            direct_source_current=direct[k]+force[k]+returned[k][:,n])
    return out
