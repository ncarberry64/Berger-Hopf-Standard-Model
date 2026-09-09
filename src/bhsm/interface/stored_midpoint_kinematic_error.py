"""Exact stored-operand midpoint geometry, including normalization arithmetic."""
import numpy as np
from flint import arb, arb_mat, ctx
from bhsm.interface import resolved_midpoint_coordinate_error as resolved
from bhsm.interface import stored_pullback_assembly_error as assembly


def _kinematic_matrix(frames, axes, first, step, fixed_left):
    outputs, coordinates = frames.shape[1:]
    blocks = []
    for side, sign in enumerate((1, -1)):
        if side == 0 and fixed_left:
            blocks.append(arb_mat(outputs, coordinates))
            continue
        axis = [arb(float(v)) for v in axes[side]]
        squared = sum((v*v for v in axis), arb(0))
        if not squared > 0:
            raise ValueError('nonzero active endpoint axis required')
        # (a/||a||)(a/||a||)^T = a a^T/(a^T a), avoiding unnecessary square roots.
        projector = arb_mat([[arb(int(i == j))-axis[i]*axis[j]/squared
                              for j in range(coordinates)] for i in range(coordinates)])
        blocks.append(resolved._exact_matrix(frames[side])*projector/2
                      + resolved._exact_matrix(first[side])*(sign*arb(float(step))/8))
    return arb_mat([[blocks[side][i,j] for side in range(2) for j in range(coordinates)]
                    for i in range(outputs)])


def _export(matrix):
    midpoint = np.empty((matrix.nrows(),matrix.ncols()))
    radius = np.empty_like(midpoint)
    for i,j in np.ndindex(midpoint.shape):
        value = matrix[i,j]
        if not value.is_finite():
            raise RuntimeError('nonfinite kinematic enclosure')
        midpoint[i,j] = float(value)
        radius[i,j] = resolved._float_upper(abs(value-arb(float(midpoint[i,j]))).upper())
        if not arb(float(midpoint[i,j]),float(radius[i,j])).contains(value):
            raise RuntimeError('kinematic ball export lost containment')
    return midpoint,radius


def _norms(matrix, retained):
    rows, columns = matrix.nrows(),matrix.ncols()
    bounds = []
    for start,stop in ((0,retained),(retained,rows)):
        block = arb_mat([[matrix[i,j] for j in range(columns)] for i in range(start,stop)])
        frobenius = resolved._block_error_norm(matrix,start,stop,columns)
        bounds.append(resolved._operator_norm_upper(block,frobenius))
    return dict(retained_operator_norm_upper=resolved._float_upper(bounds[0]),
                complement_operator_norm_upper=resolved._float_upper(bounds[1]),
                combined_operator_norm_upper=resolved._float_upper(
                    (bounds[0]**2+bounds[1]**2).sqrt()))


def enclose_midpoint_coordinates(basis, frames, axes, first_derivatives, step,
                                stored_target, approximate_coordinates,
                                retained_dimension, *, fixed_left=False):
    """Enclose S^-1 M* - Xhat for exact supplied binary64 operands.

    M* uses exactly normalized endpoint projectors, exact frame products and
    h/8 first-derivative addition. The supplied first derivatives and frames
    are exact operands here, not certified physical derivatives or frames.
    Construction-only and combined construction/solve errors are reported
    separately; the latter REPLACES a bound for S^-1 Mhat-Xhat.
    """
    s,f,a,d,m,x = [resolved._real_binary64(v,n) for v,n in (
        (basis,'basis'),(frames,'frames'),(axes,'axes'),(first_derivatives,'first derivatives'),
        (stored_target,'stored target'),(approximate_coordinates,'approximate coordinates'))]
    h = resolved._real_binary64(step,'step')
    if (s.ndim != 2 or s.shape[0] == 0 or s.shape[0] != s.shape[1]
            or f.ndim != 3 or f.shape[0] != 2 or f.shape[1] != s.shape[0]
            or f.shape[2] == 0 or a.shape != (2,f.shape[2]) or d.shape != f.shape
            or m.shape != (s.shape[0],2*f.shape[2]) or x.shape != m.shape
            or h.shape != () or float(h) <= 0
            or type(retained_dimension) is not int or not 0 < retained_dimension < s.shape[0]
            or type(fixed_left) is not bool):
        raise ValueError('compatible finite midpoint operands and positive step required')
    if fixed_left and (np.any(f[0] != 0) or np.any(d[0] != 0)):
        raise ValueError('fixed initial endpoint must have zero frame and derivative')
    previous = ctx.prec
    ctx.prec = resolved.PRECISION
    try:
        exact_basis = resolved._exact_matrix(s)
        inverse = exact_basis.inv()
        identity = arb_mat([[int(i == j) for j in range(s.shape[0])] for i in range(s.shape[0])])
        residual = identity-exact_basis*inverse
        inverse_residual = max(sum(abs(residual[i,j]) for j in range(s.shape[0])).upper()
                               for i in range(s.shape[0]))
        if not (inverse_residual.is_finite() and inverse_residual < 1):
            raise RuntimeError('stored basis inverse could not be certified')
        exact_target = _kinematic_matrix(f,a,d,float(h),fixed_left)
        target_error = exact_target-resolved._exact_matrix(m)
        construction = inverse*target_error
        combined = inverse*exact_target-resolved._exact_matrix(x)
        arrays = {}
        for name,matrix in (('target_error',target_error),('construction_coordinate_error',construction),
                            ('combined_coordinate_error',combined)):
            arrays[name+'_mid'],arrays[name+'_radius'] = _export(matrix)
        report = dict(
            scope='NORMALIZED_MIDPOINT_CONSTRUCTION_AND_SOLVE_FROM_EXACT_STORED_OPERANDS',
            precision_bits=resolved.PRECISION,
            inverse_residual_infinity_upper=resolved._float_upper(inverse_residual),
            target_construction_error_frobenius_upper=resolved._float_upper(
                resolved._block_error_norm(target_error,0,s.shape[0],m.shape[1])),
            construction_only_coordinate_error=_norms(construction,retained_dimension),
            combined_construction_and_solve_error=_norms(combined,retained_dimension),
            combined_bound_replaces_stored_target_coordinate_solve_bound=True,
            first_derivative_physical_error_enclosed=False,
            common_projector_derivative_consistency_enclosed=False,
            physical_frame_error_enclosed=False, physical_Hessian_error_enclosed=False,
            neighborhood_remainder_enclosed=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False)
        return arrays,report
    finally:
        ctx.prec = previous


def bound_stored_tensor_pullback(output, tensor, coordinates, retained_dimension,
                                retained_error_upper, complement_error_upper):
    """Bound L(Q[X*,X*]-Q[Xhat,Xhat]) using caller-certified U/C errors.

    The exact stored symmetric Q is mapped into output units BEFORE its block
    norms are bounded. No error in Q, L or the physical frame is included.
    """
    l,q,x = [resolved._real_binary64(v,n) for v,n in
             ((output,'output'),(tensor,'tensor'),(coordinates,'coordinates'))]
    errors = [resolved._real_binary64(v,'coordinate error upper') for v in
              (retained_error_upper,complement_error_upper)]
    if (q.ndim != 3 or min(q.shape) == 0 or q.shape[1] != q.shape[2]
            or l.ndim != 2 or l.shape[1] != q.shape[0] or l.shape[0] == 0
            or x.ndim != 2 or x.shape[0] != q.shape[1] or x.shape[1] == 0
            or type(retained_dimension) is not int or not 0 < retained_dimension < q.shape[1]
            or not np.array_equal(q,q.transpose(0,2,1))
            or any(v.shape != () or float(v) < 0 for v in errors)):
        raise ValueError('symmetric stored tensor and compatible certified bounds required')
    previous = ctx.prec;ctx.prec = resolved.PRECISION
    try:
        k = retained_dimension
        norms = []
        for block in (q[:,:k,:k],q[:,k:,:k],q[:,k:,k:]):
            matrix = block.reshape(q.shape[0],-1)
            formed = l@matrix
            if not np.all(np.isfinite(formed)):
                raise RuntimeError('mapped tensor overflow')
            rounding = assembly._dot_error(l.shape[1],np.abs(l)@np.abs(matrix))
            norms.append((assembly._norm(formed)+rounding).upper())
        au,ac = assembly._operator(x[:k]),assembly._operator(x[k:])
        eu,ec = [arb(float(v)) for v in errors]
        quu,qcu,qcc = norms
        terms = [quu*(2*au*eu+eu*eu),
                 2*qcu*(au*ec+ac*eu+eu*ec),qcc*(2*ac*ec+ec*ec)]
        return dict(scope='STORED_OUTPUT_TENSOR_PULLBACK_OF_CERTIFIED_COORDINATE_ERRORS',
            mapped_tensor_block_norms_upper=[resolved._float_upper(v) for v in norms],
            block_error_contributions_upper=[resolved._float_upper(v) for v in terms],
            pullback_error_frobenius_upper=resolved._float_upper(sum(terms)),
            local_pair_uniform_quadratic_coefficient_upper=resolved._float_upper(2*sum(terms)),
            coordinate_error_bounds_require_certificate=True,
            physical_tensor_error_enclosed=False,output_construction_error_enclosed=False,
            Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    finally:
        ctx.prec=previous
