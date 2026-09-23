"""Tests of restrictions, nonlinear incidence and global signed cancellation."""
from flint import arb, arb_mat, ctx
from bhsm.interface.shared_parameter_residual import PolynomialMatrix
from bhsm.interface.shared_history_pullback import history_residuals,causal_pullback,derivative


def scalar(terms,parameters=1):
    return PolynomialMatrix({k:arb_mat([[v]]) for k,v in terms.items()},1,1,parameters)


def test_common_endpoint_cancels_instead_of_independent_boxes():
    theta=scalar({(0,):1});zero=scalar({})
    _,residuals=history_residuals([theta,theta],[1],lambda z:zero)
    assert residuals[0].terms=={}
    independent=scalar({(0,):-1,(1,):1},parameters=2)
    assert independent.absolute_entry_bounds()[0,0]==2


def test_nonlinear_midpoint_curvature_term_is_required():
    old=ctx.prec;ctx.prec=256
    try:
        theta=scalar({(0,):1});one=scalar({():1})
        middle,residual=history_residuals([theta,one],[1],lambda z:z@z)
        d2=derivative(derivative(residual[0],0),0).terms[()][0,0]
        assert d2.contains(-arb(19)/24)
        assert not d2.overlaps(-arb(2)/3)  # P*H*P without D r D2F is wrong.
        assert derivative(derivative(middle[0],0),0).terms[()][0,0]==arb('0.25')
    finally:ctx.prec=old


def test_causal_transport_combines_shared_node_before_support():
    theta=scalar({(0,):1});zero=scalar({})
    _,residuals=history_residuals([zero,theta,zero],[1,1],lambda z:zero)
    history=causal_pullback(residuals,[arb_mat([[1]])]*2,[arb_mat([[1]])]*2)
    assert history[-1].terms=={}
    assert sum(r.absolute_entry_bounds()[0,0] for r in residuals)==2


def test_tangent_restriction_can_increase_euclidean_susceptibility():
    # Exact counterexample, not physical BHSM coefficients.
    h=arb_mat([[1,2],[2,5]]);b=arb_mat([[2],[5]])
    full=h.solve(b);restricted=arb_mat([[1]]).solve(arb_mat([[2]]))
    assert full==arb_mat([[0],[1]]) and restricted==arb_mat([[2]])
    assert (full.transpose()*full)[0,0]==1
    assert (restricted.transpose()*restricted)[0,0]==4
    # Energy/compliance decreases even though the state norm increases.
    assert (full.transpose()*h*full)[0,0]==5
    assert (restricted.transpose()*restricted)[0,0]==4


def test_reducing_subspace_gives_orthogonal_response_projection():
    h=arb_mat([[2,0],[0,4]]);b=arb_mat([[6,2],[8,4]])
    inclusion=arb_mat([[1],[0]])
    full=h.solve(b)
    reduced=(inclusion.transpose()*h*inclusion).solve(inclusion.transpose()*b)
    assert inclusion*reduced==inclusion*inclusion.transpose()*full
