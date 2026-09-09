"""Include a certified output-map perturbation in a physical Hessian error."""
import math
from flint import arb,ctx
from bhsm.interface import physical_hessian_error_pullback as physical
from bhsm.interface import stored_pullback_assembly_error as arithmetic


def pullback_with_frozen_output(output,error_mid,error_radius,coordinates,
                                coordinate_error_upper,output_error_upper):
    """Bound L* E[X*,X*] with caller-certified coordinate/output errors.

    The physical E ball must be verified independently. This includes the
    product of the output error with the complete physical ball at X*, not
    merely its stored-coordinate center.
    """
    error=float(output_error_upper)
    if not math.isfinite(error) or error<0:
        raise ValueError('finite nonnegative output operator error required')
    q,r,x=[arithmetic._real_binary64(v,n) for v,n in (
        (error_mid,'error midpoint'),(error_radius,'error radius'),(coordinates,'coordinates'))]
    correction,report=physical.pullback_hessian_error(
        output,q,r,x,coordinate_error_upper)
    previous=ctx.prec;ctx.prec=arithmetic.PRECISION
    try:
        source=arithmetic._norm(q)+arithmetic._norm(r)
        exact_coordinates=arithmetic._operator(x)+arb(float(coordinate_error_upper))
        cross=arb(error)*source*exact_coordinates**2
        enclosure=arb(report['correction_enclosure_frobenius_radius_upper'])+cross
        total=arb(report['total_error_pullback_frobenius_upper'])+cross
        report=dict(report,scope='PHYSICAL_HESSIAN_ERROR_WITH_CERTIFIED_COORDINATE_AND_FROZEN_OUTPUT_PERTURBATIONS',
            output_physical_coordinate_cross_error_frobenius_upper=arithmetic._float_upper(cross),
            correction_enclosure_frobenius_radius_upper=arithmetic._float_upper(enclosure),
            total_error_pullback_frobenius_upper=arithmetic._float_upper(total),
            local_pair_uniform_quadratic_coefficient_upper=arithmetic._float_upper(2*total),
            output_map_construction_error_enclosed=True,
            output_error_bound_requires_certificate=True)
        return correction,report
    finally:ctx.prec=previous
