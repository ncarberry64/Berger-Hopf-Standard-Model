"""Complete shared-parameter HS/dense-output incidence and rate pullbacks.

Caller-owned field derivatives must hold on the actual evaluation domain.
These identities never promote a center jet or a value enclosure to a jet.
"""


def dense_incidence(tau, step, left, right, left_field, right_field):
    """Physical-state u/v/uv jets of a cubic Hermite image at fixed tau.

    Endpoint jets and full 99-component field jets retain one shared domain.
    The uv endpoint state entries may be zero; descriptor entries are retained.
    """
    n=len(left['value'])
    keys=('value','u','v','uv')
    if any(len(jet[k])!=n for jet in (left,right,left_field,right_field) for k in keys):
        raise ValueError('complete matching state and field jets required')
    a=1-3*tau*tau+2*tau**3
    b=3*tau*tau-2*tau**3
    c=step*(tau-2*tau*tau+tau**3)
    d=step*(-tau*tau+tau**3)
    return {k:[a*x+b*y+c*f+d*g for x,y,f,g in
               zip(left[k],right[k],left_field[k],right_field[k],strict=True)] for k in keys}


def composed_rate_second(rate_hessian_on_first_incidence, rate_df_on_second_incidence):
    """D2(f o x)[u,v] = D2f[x_u,x_v] + Df*x_uv."""
    if len(rate_hessian_on_first_incidence)!=len(rate_df_on_second_incidence):
        raise ValueError('matching complete physical output required')
    return [a+b for a,b in zip(rate_hessian_on_first_incidence,rate_df_on_second_incidence,strict=True)]


def signed_hs_second(step, left_second, midpoint_rate_second, right_second):
    """HS residual second derivative; midpoint argument is the COMPLETE pullback.

    Affine endpoint state second derivatives vanish. Its midpoint term must
    include Df(m)*m_uv before this function is called. No Taylor half is used.
    """
    if not len(left_second)==len(midpoint_rate_second)==len(right_second):
        raise ValueError('matching complete physical outputs required')
    return [-step*(a+4*b+c)/6 for a,b,c in
            zip(left_second,midpoint_rate_second,right_second,strict=True)]
