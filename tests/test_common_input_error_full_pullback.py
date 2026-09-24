import pytest
from flint import arb,arb_mat,ctx
from bhsm.interface.shared_action_taylor import TaylorDomain
from bhsm.interface.input_linear_taylor import InputLinearTaylor
from bhsm.interface.common_input_error_full_pullback import pullback_all_errors


def test_shared_error_substitution_cancels_constant_and_state_terms():
    domain=TaylorDomain([(0,1,'interval')],1)
    model=InputLinearTaylor(domain,arb_mat([[0,0,1,-1]]),arb_mat([[0,0,2,-2]]),
                            arb('1/4'),[(0,2,'euclidean'),(2,4,'box')])
    result=pullback_all_errors(model,[(2,arb_mat([[1,0],[1,0]]))],2)
    assert result.c==arb_mat(1,4) and result.a==arb_mat(1,4)
    assert result.support()==arb('1/4')
    assert result.support()<model.support()
    with pytest.raises(ValueError,match='every auxiliary'):
        pullback_all_errors(model,[(2,arb_mat([[1,0]]))],2)


def test_state_dependent_map_preserves_domain_and_remainder_gauge():
    domain=TaylorDomain([(0,1,'interval')],1)
    model=InputLinearTaylor(domain,arb_mat([[1,-1]]),arb_mat([[2,3]]),
                            arb('1/8'),[(0,1,'euclidean'),(1,2,'box')])
    result=pullback_all_errors(model,[(1,arb_mat([[arb(1,1)]]))],1)
    assert result.domain is domain and result.input_groups==model.input_groups
    # Arb rounds the input ball's radius outward; the enlarged gauge
    # must include that rounding as well as the exact factor two.
    assert arb('1/4')<=result.r<arb('0.250000001')
    for theta in (arb(-1),arb(0),arb(1)):
        for u in (-1,1):
            eta=(1+theta)*u
            actual=u-eta+theta*(2*u+3*eta)
            column=arb_mat([[u],[0]])
            enclosed=result.at_input(column).enclosure()
            for sign in (-1,1): assert enclosed.contains(actual+sign*arb('1/4'))


@pytest.fixture(autouse=True)
def restore_precision():
    previous=ctx.prec;ctx.prec=256
    try: yield
    finally: ctx.prec=previous
