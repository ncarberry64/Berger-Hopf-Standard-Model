"""Signed Arb centers and separate error transport for a causal linear map."""
import numpy as np
from flint import arb, arb_mat, ctx
from bhsm.interface.direct_physical_hs_jacobian import _matrix
from bhsm.interface.current_green_midpoint_coordinate_error import _float_upper, _real_binary64
from bhsm.interface.current_green_causal_error import transport_local_errors
from bhsm.interface.stored_causal_arithmetic_envelope import (
    fixed_axis_projection_norms, combine_stored_causal_errors,
)


def _squared_norm(entries):
    values=list(entries)
    if not values:return arb(0)
    # A single Arb dot product keeps norm formation out of binary64,
    # including subnormal and overflow ranges of the stored operands.
    return (arb_mat(1,len(values),values)*arb_mat(len(values),1,values))[0,0]


def _sqrt_upper(value):
    upper=value.upper()
    if not upper.is_finite() or upper<0:
        raise ArithmeticError('nonfinite or inconsistent squared norm enclosure')
    return upper.sqrt().upper()


def projected_row_bounds(row,input_axes,output_axis):
    """Bound a fixed row on u_j=e_j*l_j+t_j without unit-axis assumptions."""
    n=row.nrows();count=len(input_axes)
    if row.ncols()!=n*count:raise ValueError('one square block per input axis required')
    e=arb_mat(n,1,[arb(float(v)) for v in output_axis])
    e2=_squared_norm(e.entries())
    coefficient=e2-2
    entries=np.array(row.entries(),dtype=object).reshape(n,n*count)
    totals=[[arb(0),arb(0)],[arb(0),arb(0)]]
    for j,axis in enumerate(input_axes):
        block_entries=entries[:,j*n:(j+1)*n].ravel().tolist()
        block=arb_mat(n,n,block_entries)
        incoming=arb_mat(n,1,[arb(float(v)) for v in axis])
        column=block*incoming
        longitudinal_row=e.transpose()*block
        ll=(e.transpose()*column)[0,0]
        # ||(I-ee.T)X||_F^2 = ||X||_F^2+(||e||^2-2)||e.T X||^2.
        # The identity holds for every e, not just a normalized axis.
        tl2=_squared_norm(column.entries())+coefficient*ll**2
        lt2=_squared_norm(longitudinal_row.entries())
        tt2=_squared_norm(block_entries)+coefficient*lt2
        totals[0][0]+=abs(ll).upper()
        totals[0][1]+=_sqrt_upper(lt2)
        totals[1][0]+=_sqrt_upper(tl2)
        totals[1][1]+=_sqrt_upper(tt2)
    return [[_float_upper(v) for v in line] for line in totals]


def centered_step(mapping,previous,left,right,*,initial=False):
    """Compute a signed center and bound only this step's fresh row error."""
    n=mapping.nrows();old_columns=previous.ncols()
    if (mapping.ncols()!=n or previous.nrows()!=n or old_columns%n
            or any(v.nrows()!=n or v.ncols()!=n for v in (left,right))
            or initial!=(old_columns==0)):
        raise ValueError('compatible causal row, local blocks and initial condition required')
    product=mapping*previous
    if not initial:
        for i in range(n):
            for j in range(n):product[i,old_columns-n+j]+=left[i,j]
    old=product.entries();new=right.entries();joined=[]
    for i in range(n):
        joined.extend(old[i*old_columns:(i+1)*old_columns]);joined.extend(new[i*n:(i+1)*n])
    if not all(v.is_finite() for v in joined):raise ArithmeticError('nonfinite causal linear step')
    largest=max(v.rad() for v in joined)
    # There are old_columns/n+1 square blocks. Each error block has
    # Frobenius norm <= n*largest, so their row sum <= new_columns*largest.
    error=_float_upper((old_columns+n)*largest)
    center=arb_mat(n,old_columns+n,[v.mid() for v in joined])
    return center,error


def bound_causal_linear_defect(maps,left_blocks,right_blocks,axes,map_gain,
                              *,precision=512,block_size=10,progress=None):
    """Bound the complete fixed-frame causal linear operator in two radii.

    Inputs are caller-certified local DL/DR balls and matching stored maps.
    map_gain bounds the complete frozen-map perturbation in Euclidean
    block-sup norm. This function does not certify their physical origin.
    """
    if type(precision) is not int or precision<64:
        raise ValueError('at least 64 bits of arithmetic precision required')
    p=_real_binary64(maps,'maps').copy();a=_real_binary64(axes,'axes').copy()
    if (p.ndim!=3 or not all(p.shape) or p.shape[1]!=p.shape[2]
            or a.shape!=(p.shape[0]+1,p.shape[1]) or len(left_blocks)!=len(p) or len(right_blocks)!=len(p)):
        raise ValueError('complete matching maps, axes and local blocks required')
    if progress is not None and not callable(progress):raise ValueError('callable progress callback required')
    previous_precision=ctx.prec;ctx.prec=precision
    try:
        n=p.shape[1];left=[_matrix(v) for v in left_blocks];right=[_matrix(v) for v in right_blocks]
        if any(v.nrows()!=n or v.ncols()!=n for v in left+right):
            raise ValueError('square local blocks matching map dimension required')
        row=arb_mat(n,0);rows=[];errors=[]
        for i,mapping in enumerate(p):
            row,error=centered_step(arb_mat(mapping.tolist()),row,left[i],right[i],initial=i==0)
            errors.append(error)
            bounds=projected_row_bounds(row,a[1:i+2],a[i+1])
            rows.append(dict(node=i+1,signed_center_block_bounds_upper=bounds,local_row_error_upper=error))
            if progress is not None:
                progress(i+1,len(p))
                if ctx.prec!=precision:raise RuntimeError('progress callback changed arithmetic precision')
        center=np.max(np.asarray([r['signed_center_block_bounds_upper'] for r in rows]),axis=0)
        transported=transport_local_errors(p,np.asarray(errors),block_size=block_size)
        projections=fixed_axis_projection_norms(a)
        euclidean_error=transported['maximum_node_error_norm_upper']
        input_errors=[_float_upper(arb(projections[0])*arb(euclidean_error)),euclidean_error]
        columns=[combine_stored_causal_errors(center[:,j],[input_errors[j]],map_gain,projections) for j in range(2)]
        total=[[columns[j]['frozen_map_transverse_quadratic_coefficients_upper'][i] for j in range(2)] for i in range(2)]
        return dict(scope='COMPLETE_FIXED_FRAME_CAUSAL_LINEAR_DEFECT_CONDITIONAL_ON_INPUT_CERTIFICATES',
            arithmetic_precision_bits=precision,intervals=len(p),dimension=n,signed_center_rows=rows,
            signed_center_block_bounds_upper=center.tolist(),local_row_error_bounds_upper=errors,
            error_transport=transported,input_column_error_bounds_upper=input_errors,
            fixed_axis_projection_norms_upper=projections,map_perturbation_columns=columns,
            frozen_inverse_linear_defect_bounds_upper=total,
            fixed_initial_endpoint_omitted=True,stored_axis_unit_norm_assumed=False,
            local_DF_frame_and_map_bounds_require_verification=True,physical_branch_continuation_certified=False,
            physical_quotient_identified=False,physical_Z1_recertified=False,physical_contraction_proved=False,
            Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    finally:ctx.prec=previous_precision
