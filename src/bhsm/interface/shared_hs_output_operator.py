"""Compose repeated HS incidence and fixed output maps before ball support.

These operators preserve known linear dependence of each same physical
Hessian leaf. They cannot recover state/direction correlations erased by
an upstream interval enclosure.
"""
from flint import arb,arb_mat


def composed_operators(output,midpoint_df,step):
    """Return the signed Newton coefficients of H0, Hm and H1, without 1/2."""
    n=midpoint_df.nrows()
    if midpoint_df.ncols()!=n or output.ncols()!=n:
        raise ValueError('matching complete physical output and midpoint DF required')
    P=output;PA=P*midpoint_df
    return (step*P/6+step**2*PA/12,2*step*P/3,step*P/6-step**2*PA/12)


def evaluate_same_leaves(operators,leaves):
    if len(operators)!=3 or len(leaves)!=3:raise ValueError('all three HS sites required')
    result=arb_mat(operators[0].nrows(),1)
    for operator,leaf in zip(operators,leaves):
        if leaf.nrows()!=operator.ncols() or leaf.ncols()!=1:raise ValueError('complete same-site leaf required')
        result+=operator*leaf
    return result


def projected_operator(output,axis):
    if axis.ncols()!=1 or axis.nrows()!=output.nrows():raise ValueError('matching fixed axis required')
    longitudinal=axis.transpose()*output
    return longitudinal,output-axis*longitudinal
