"""Source-corrected unsquared boundary attachment and analytic current jets.

The maps below belong to A=w^-1 D_s+H on its specified trace domain.
No square spectral parameter is converted to an external energy.  A finite
Friedrichs square response contributes its evaluated unsquared range/source
return; its terminal restriction does not by itself supply a physical Bout.
"""
from __future__ import annotations
import numpy as np
from .muon_native_unsquared_domain_matching import _weak_source_solve
from .muon_native_reset_friedrichs_return import chain_apply


_KEYS = ('trace', 'source_return', 'initial_boundary', 'final_boundary',
         'boundary_source', 'initial_target', 'final_target', 'direct_current')


def _coefficients(data, reference=None):
    if set(data) != set(_KEYS):
        raise ValueError('all trace, source, boundary and target maps/jets required')
    a = {k: np.asarray(data[k], complex) for k in _KEYS}
    if any(not x.ndim == 2 or not np.isfinite(x).all() for x in a.values()):
        raise ValueError('finite complete matrix maps required')
    U,r,Bi,Bf,b,Li,Lf,c = (a[k] for k in _KEYS)
    d,nc = r.shape
    nb,nl = Bi.shape[0],Li.shape[0]
    shapes = ((d,d),(d,nc),(nb,d),(nb,d),(nb,nc),(nl,d),(nl,d),(nl,nc))
    if any(a[k].shape != s for k,s in zip(_KEYS,shapes)):
        raise ValueError('same full action trace and independent source/target spaces required')
    if reference is not None and any(a[k].shape != reference[k].shape for k in _KEYS):
        raise ValueError('jets must retain every original map row and column')
    return a


def unsquared_boundary_source_two_jet(base, first, mixed):
    """Compose Gamma, forced numerator and literal current before inversion.

    chi_f=U chi_i+r and Bi chi_i+Bf chi_f=b imply
    Gamma=Bi+Bf U, f=b-Bf r.  A target Li chi_i+Lf chi_f+c has
    effective left Li+Lf U and direct return c+Lf r.  All maps and both
    ordered first jets must be explicit; zero contacts require zero arrays.
    The two directions can be energy/magnetic or any owned analytic chart.
    """
    a = _coefficients(base)
    if len(first) != 2:
        raise ValueError('two independently owned source/energy directions required')
    p,q = (_coefficients(x,a) for x in first)
    pq = _coefficients(mixed,a)
    products = (('boundary_matrix','initial_boundary','final_boundary','trace',1),
                ('forced_boundary_source','boundary_source','final_boundary','source_return',-1),
                ('effective_literal_left','initial_target','final_target','trace',1),
                ('direct_source_return_current','direct_current','final_target','source_return',1))
    out = {}
    for name,free,left,right,sign in products:
        out[name] = a[free]+sign*a[left]@a[right]
        out[name+'_first'] = np.array([
            t[free]+sign*(t[left]@a[right]+a[left]@t[right]) for t in (p,q)])
        out[name+'_mixed'] = pq[free]+sign*(pq[left]@a[right]
            +p[left]@q[right]+q[left]@p[right]+a[left]@pq[right])
    out.update(analytic_left_conjugated=False,
               square_parameter_identified_with_energy_squared=False,
               physical_exterior_relation_or_pole_selected=False)
    return out


def attached_current_two_jet(application):
    """Solve the original boundary rows and its independent transpose dual.

    At a pole this ordinary solve must be replaced by the owned null-space
    residue application.  No least-squares solution of a rectangular trace
    relation or eigenvector ordering is used as a pole selector here.
    """
    a = application
    G,f,L,c = (a[k] for k in ('boundary_matrix','forced_boundary_source',
                              'effective_literal_left','direct_source_return_current'))
    if G.shape[0] != G.shape[1]:
        raise ValueError('square attached relation required for this ordinary inverse action')
    G1,f1,L1,c1 = (a[k+'_first'] for k in ('boundary_matrix','forced_boundary_source',
                                        'effective_literal_left','direct_source_return_current'))
    G2,f2,L2,c2 = (a[k+'_mixed'] for k in ('boundary_matrix','forced_boundary_source',
                                        'effective_literal_left','direct_source_return_current'))
    x = np.linalg.solve(G,f)
    p = np.linalg.solve(G.T,L.T)
    x1 = np.array([np.linalg.solve(G,b-d@x) for b,d in zip(f1,G1)])
    x2 = np.linalg.solve(G,f2-G2@x-G1[0]@x1[1]-G1[1]@x1[0])
    C = c+L@x
    C1 = np.array([dc+dL@x+L@dx for dc,dL,dx in zip(c1,L1,x1)])
    C2 = c2+L2@x+L1[0]@x1[1]+L1[1]@x1[0]+L@x2
    C1dual = np.array([dc+dL@x+p.T@(df-dG@x)
                      for dc,dL,df,dG in zip(c1,L1,f1,G1)])
    return dict(initial_trace=x,initial_trace_first=x1,initial_trace_mixed=x2,
                analytic_transpose_boundary_adjoint=p,current=C,current_first=C1,
                current_mixed=C2,independent_transpose_current=c+p.T@f,
                first_transpose_current=C1dual,boundary_original_rows=G@x-f,
                boundary_transpose_rows=G.T@p-L.T,
                first_original_rows=np.array([G@dx+dG@x-df for dx,dG,df in zip(x1,G1,f1)]),
                mixed_original_rows=G@x2+G2@x+G1[0]@x1[1]+G1[1]@x1[0]-f2,
                physical_pole_or_residue_selected=False)


def source_corrected_unsquared_return(weak_factor,right_moments,literal_left,
        natural_square_response,core_square_response,*,weak_factor_first,
        right_moments_first,literal_left_first,natural_square_response_first,
        core_square_response_first):
    """Carry the square/range and forced final return ONCE into the current.

    r_N=Aw x_N-J, r_D=Aw x_D-J, r_F=r_N-r_D=Aw(x_N-x_D).
    Original transpose p solves Aw.T p=L.T, hence
    L(x_N-x_D)=p.T r_F and L x_D=L Aw^-1 J+p.T r_D.
    These are actual sourced finite-domain equations, not a homogeneous
    exterior condition. The derivative includes operator, source, target
    and both square-response contacts on that same coordinate domain.
    """
    P = tuple(np.asarray(x,complex) for x in weak_factor)
    dP = tuple(np.asarray(x,complex) for x in weak_factor_first)
    R,L,xN,xD,dR,dL,dxN,dxD = map(lambda x:np.asarray(x,complex),(
        right_moments,literal_left,natural_square_response,core_square_response,
        right_moments_first,literal_left_first,natural_square_response_first,
        core_square_response_first))
    if (R.ndim != 3 or xN.shape != R.shape or xD.shape != R.shape
            or dR.shape != R.shape or dxN.shape != R.shape or dxD.shape != R.shape
            or L.ndim != 3 or L.shape[0] != R.shape[0] or L.shape[2] != R.shape[1]
            or dL.shape != L.shape):
        raise ValueError('complete same-domain square responses, moments and derivative contacts required')
    PT = (P[0].transpose(0,2,1),P[2].transpose(0,2,1),P[1].transpose(0,2,1))
    x = _weak_source_solve(P,R)
    p = _weak_source_solve(PT,L.transpose(0,2,1))
    dx = _weak_source_solve(P,dR-chain_apply(*dP,x))
    dp = _weak_source_solve(PT,dL.transpose(0,2,1)-chain_apply(
        dP[0].transpose(0,2,1),dP[2].transpose(0,2,1),dP[1].transpose(0,2,1),p))
    rN,rD = (chain_apply(*P,t)-R for t in (xN,xD))
    drN,drD = (chain_apply(*dP,t)+chain_apply(*P,dt)-dR
               for t,dt in ((xN,dxN),(xD,dxD)))
    rF,drF = rN-rD,drN-drD
    target = lambda t:np.einsum('nci,nij->cj',L,t)
    dual = lambda t:np.einsum('nic,nij->cj',p,t)
    dtar = lambda t,dt:np.einsum('nci,nij->cj',dL,t)+target(dt)
    ddual = lambda t,dt:np.einsum('nic,nij->cj',dp,t)+dual(dt)
    return dict(unsquared_response=x,original_unsquared_transpose_adjoint=p,
        natural_range_source=rN,core_range_source=rD,forced_unsquared_boundary_source=rF,
        natural_range_source_first=drN,core_range_source_first=drD,
        forced_unsquared_boundary_source_first=drF,
        actual_unsquared_current=target(x),natural_square_current=target(xN),core_square_current=target(xD),
        forced_boundary_current=target(xN-xD),independent_forced_boundary_current=dual(rF),
        original_current_with_core_source_return=target(x)+dual(rD),
        forced_boundary_current_first=dtar(xN-xD,dxN-dxD),
        independent_forced_boundary_current_first=ddual(rF,drF),
        original_current_with_core_source_return_first=dtar(x,dx)+ddual(rD,drD),
        original_unsquared_rows=chain_apply(*P,x)-R,
        original_unsquared_transpose_rows=chain_apply(*PT,p)-L.transpose(0,2,1),
        forced_original_source_identity=chain_apply(*P,xN-xD)-rF,
        forced_original_source_first_identity=chain_apply(*dP,xN-xD)+chain_apply(*P,dxN-dxD)-drF,
        initial_square_trace_held=True,final_square_trace_restriction_is_not_first_order_Bout=True,
        source_range_contact_count=1,forced_face_return_count=1,
        analytic_source_or_target_conjugated=False,physical_exterior_pole_selected=False)
