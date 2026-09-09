"""Stream signed sparse quadratic coefficients through a frozen causal inverse."""
import numpy as np
from flint import arb, arb_mat, ctx
from bhsm.interface.direct_physical_hs_jacobian import _matrix
from bhsm.interface.centered_causal_linear_defect import _squared_norm, _sqrt_upper
from bhsm.interface.current_green_midpoint_coordinate_error import _float_upper, _real_binary64
from bhsm.interface.current_green_causal_error import transport_local_errors
from bhsm.interface.stored_causal_arithmetic_envelope import fixed_axis_projection_norms, combine_stored_causal_errors


def transpose_inputs(block,n):
    """Swap the Cartesian input indices of an n-output, n-by-n input tensor."""
    if block.nrows()!=n or block.ncols()!=n*n:raise ValueError('square Cartesian input tensor required')
    return arb_mat(n,n*n,[block[k,b*n+a] for k in range(n) for a in range(n) for b in range(n)])


def projected_norms(block,axis):
    """Frobenius output-projection bounds without assuming the axis is unit."""
    e=arb_mat(block.nrows(),1,[arb(float(v)) for v in axis])
    longitudinal=e.transpose()*block
    l2=_squared_norm(longitudinal.entries())
    t2=_squared_norm(block.entries())+(_squared_norm(e.entries())-2)*l2
    return _sqrt_upper(l2),_sqrt_upper(t2)


def bound_causal_quadratic_family(maps,axes,read_interval,family,map_gain,
                                  *,active_intervals=None,precision=512,block_size=10,progress=None):
    """Bound one LL/LT/TT family for independent block-sup input amplitudes.

    read_interval(i) supplies exactly four n-by-q Arb source blocks, indexed
    00,01,10,11. Default coverage is every interval. An explicit subset is an
    isolated additive component, never a complete bound with absent data zeroed.
    Only two local intervals and one propagated coefficient tensor are held.
    """
    if type(precision) is not int or precision<64:raise ValueError('at least 64 bits required')
    previous=ctx.prec;ctx.prec=precision
    try:
        p=_real_binary64(maps,'causal maps');a=_real_binary64(axes,'axes')
        if (p.ndim!=3 or min(p.shape)==0 or p.shape[1]!=p.shape[2]
                or a.shape!=(p.shape[0]+1,p.shape[1]) or family not in ('LL','LT','TT')):
            raise ValueError('matching nonempty maps, axes and quadratic family required')
        gain=_real_binary64(map_gain,'map gain')
        if gain.shape!=() or not 0<=float(gain)<1:raise ValueError('map gain in [0,1) required')
        count,n,_=p.shape;q={'LL':1,'LT':n,'TT':n*n}[family]
        indices=list(range(count)) if active_intervals is None else list(active_intervals)
        if (not indices or any(type(i) is not int or not 0<=i<count for i in indices)
                or len(set(indices))!=len(indices)):
            raise ValueError('distinct valid active intervals required')
        selected=set(indices);exact=[arb_mat(m.tolist()) for m in p]
        totals=[[arb(0),arb(0)] for _ in range(count+1)]
        fresh=[arb(0) for _ in range(count)];calls=[];atoms=0
        def read(i):
            if i not in selected:return None
            blocks=read_interval(i)
            if ctx.prec!=precision:raise RuntimeError('source loader changed arithmetic precision')
            if set(blocks)!=set(('00','01','10','11')):raise ValueError('all four endpoint source blocks required')
            blocks={key:_matrix(value) for key,value in blocks.items()}
            if any(m.nrows()!=n or m.ncols()!=q for m in blocks.values()):
                raise ValueError('complete matching quadratic-source shape required')
            if i==0 and any(not v.is_zero() for key in ('00','01','10') for v in blocks[key].entries()):
                raise ValueError('fixed initial endpoint source blocks must be zero')
            calls.append(i);return blocks
        def propagate(start,initial,second=None):
            nonlocal atoms
            atoms+=1;current=initial
            for node in range(start,count+1):
                if node!=start:
                    current=exact[node-1]*current
                    if node==start+1 and second is not None:current+=second
                entries=current.entries()
                if not all(v.is_finite() for v in entries):raise ArithmeticError('nonfinite causal quadratic coefficient')
                # For a unit pair of input blocks, the Kronecker input has
                # Euclidean norm <=1. Frobenius radius bounds its output error.
                radius=max(v.rad() for v in entries)
                fresh[node-1]+=(arb(n*q).sqrt()*radius).upper()
                current=arb_mat(n,q,[v.mid() for v in entries])
                l,t=projected_norms(current,a[node]);totals[node][0]+=l;totals[node][1]+=t
            if progress is not None:
                progress(atoms,start,count)
                if ctx.prec!=precision:raise RuntimeError('progress callback changed arithmetic precision')
        left=read(0)
        for j in range(1,count+1):
            right=read(j) if j<count else None
            if left is not None or right is not None:
                # The same input-node diagonal is injected at node j and j+1.
                # Join those signed coefficients before evaluating later norms.
                initial=left['11'] if left is not None else arb_mat(n,q)
                propagate(j,initial,right['00'] if right is not None else None)
            if right is not None:
                if family=='LT':
                    # l_j*t_(j+1) and l_(j+1)*t_j are distinct input atoms.
                    propagate(j+1,right['01']);propagate(j+1,right['10'])
                else:
                    reversed_block=transpose_inputs(right['10'],n) if family=='TT' else right['10']
                    propagate(j+1,right['01']+reversed_block)
            left=right
        if set(calls)!=selected or len(calls)!=len(selected):raise RuntimeError('source coverage changed')
        centers=[max(_float_upper(row[i]) for row in totals) for i in (0,1)]
        errors=[_float_upper(v) for v in fresh]
        transport=transport_local_errors(p,np.array(errors),block_size=block_size)
        projections=fixed_axis_projection_norms(a)
        combined=combine_stored_causal_errors(centers,[transport['maximum_node_error_norm_upper']],map_gain,projections)
        complete=selected==set(range(count))
        return dict(scope=('COMPLETE_FIXED_FRAME_CAUSAL_QUADRATIC_FAMILY_CONDITIONAL_ON_INPUTS' if complete
                           else 'ISOLATED_ADDITIVE_FIXED_FRAME_CAUSAL_QUADRATIC_FAMILY_COMPONENT'),
            family=family,active_intervals=sorted(selected),all_intervals_covered=complete,dimension=n,
            arithmetic_precision_bits=precision,atoms=atoms,
            signed_center_node_bounds_upper=[[_float_upper(v) for v in row] for row in totals],
            signed_center_bounds_upper=centers,local_rounding_error_bounds_upper=errors,error_transport=transport,
            fixed_axis_projection_norms_upper=projections,map_perturbation=combined,
            frozen_inverse_quadratic_coefficients_upper=combined['frozen_map_transverse_quadratic_coefficients_upper'],
            longitudinal_amplitudes_independent_between_nodes=True,transverse_input_domain='FULL_COORDINATE_SPACE_SUPERSET',
            neighboring_diagonal_coefficients_combined_before_norm=True,taylor_half_already_in_sources=True,
            mixed_two_radius_factor=2,physical_inputs_require_external_verification=True,
            neighborhood_remainder_enclosed=False,physical_quotient_identified=False,
            physical_contraction_proved=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    finally:ctx.prec=previous
