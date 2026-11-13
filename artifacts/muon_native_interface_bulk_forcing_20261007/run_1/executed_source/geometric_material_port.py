"""The owned 3-geometric/4-material port, with its dynamic-flux operator.

Trace coordinates are not action seeds. Configuration virtual work is force;
the native dynamic flux additionally contains conormal and momentum-rate
terms. All inputs must be owned and evaluated in the same material frame.
"""
from flint import arb_mat
from bhsm.interface.heat_zeta_mixed_boundary_launch import heat_divided_difference

TRACE_OBJECT = 'GEOMETRIC_TRACE_HISTORY_JET_3x73'
MATERIAL_OBJECT = 'CURRENT_CENTER_HEAT_ZETA_MIXED_MATERIAL_LAUNCH_JET_4x73'


def geometric_trace_jet(trace_map, state_jet, explicit_shape):
    """D(Tq)=T Dq plus an explicitly supplied shape/frame derivative.

    The retained fixed material section has constant T. Shape motion already
    present in Dq must not be added a second time as an explicit shape term.
    """
    if trace_map.nrows()!=3 or trace_map.ncols()!=state_jet.nrows():
        raise ValueError('three geometric traces and common state coordinates required')
    if explicit_shape is None or (explicit_shape.nrows(),explicit_shape.ncols())!=(3,state_jet.ncols()):
        raise ValueError('explicit owned trace shape term required, including proved zero')
    return trace_map*state_jet+explicit_shape


def required_material_jet(momentum, force, conormal, momentum_mixed, momentum_rate_direction):
    """D[P; F-G-DP[X]] in common columns, before support.

    The last two inputs are D2P[X,u] and DP[DX u]. This is a differential
    operator on canonical action data, not a constant 4x4 change of basis.
    """
    terms=(momentum,force,conormal,momentum_mixed,momentum_rate_direction)
    if any(x is None for x in terms):
        raise ValueError('all five owned material terms required')
    if any(x.nrows()!=2 for x in terms) or len({x.ncols() for x in terms})!=1:
        raise ValueError('two canonical channels in common parameter columns required')
    flux=force-conormal-momentum_mixed-momentum_rate_direction
    return arb_mat(momentum.tolist()+flux.tolist())


def heat_pair_4x73(eigenvalues, material_first, launch_first, heat_length=1):
    """Stream Tr(DQ[P_j] P_Balpha), using four actual supplied directions.

    Conditional on an owned common real spectral frame. No trace-action
    seeds or zero-padded seven-direction contractions are introduced.
    """
    n=len(eigenvalues)
    if n<1 or len(material_first)!=4 or len(launch_first)!=73:
        raise ValueError('four material and 73 launch jets required')
    if any((m.nrows(),m.ncols())!=(n,n) for m in list(material_first)+list(launch_first)):
        raise ValueError('operator jets must share the owned spectral frame')
    result=arb_mat(4,73)
    for k,x in enumerate(eigenvalues):
        for l,y in enumerate(eigenvalues):
            b=arb_mat(4,1,[m[l,k] for m in material_first])
            p=arb_mat(1,73,[m[k,l] for m in launch_first])
            result+=(b*p)*heat_divided_difference(x,y,heat_length)
    return result


def reduce_material_mixed(*, L_bp, L_bn, L_np, L_nn, F_n, F_b, F_p, moving_seed):
    """Four-direction general implicit-objective adjoint, with PLUS seed motion.

    L_uv = Gamma_uv - eta^T F_uv, F_n^T eta = Gamma_n^T. These must be
    full, signed, common-frame blocks; a history-only objective is not assumed
    separately stationary. This yields canonical action contractions. Apply
    the actual dynamic-flux operator before calling them native material rows.
    """
    n=F_n.nrows()
    blocks=((L_bp,4,73),(L_bn,4,n),(L_np,n,73),(L_nn,n,n),
            (F_n,n,n),(F_b,n,4),(F_p,n,73),(moving_seed,4,73))
    if any(x is None or (x.nrows(),x.ncols())!=(r,c) for x,r,c in blocks):
        raise ValueError(MATERIAL_OBJECT+': complete four-direction mixed inputs required')
    phi=-F_n.solve(F_b)
    normal=L_bn+phi.transpose()*L_nn
    adjoint=F_n.transpose().solve(normal.transpose())
    fixed=L_bp+phi.transpose()*L_np-adjoint.transpose()*F_p
    return dict(fixed_seed=fixed,moving_seed=moving_seed,total=fixed+moving_seed,
                boundary_normal=phi,adjoint=adjoint,
                boundary_replay=F_n*phi+F_b,
                adjoint_replay=F_n.transpose()*adjoint-normal.transpose())
