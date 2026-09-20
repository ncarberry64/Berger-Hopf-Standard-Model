"""A state-dependent input map may be enclosed before value support only."""
from flint import arb, arb_mat, ctx
from bhsm.interface.shared_action_taylor import TaylorDomain
from bhsm.interface.input_linear_taylor import InputLinearTaylor


def test_interval_input_direction_encloses_state_dependence_and_scales_tail():
    previous=ctx.prec
    try:
        ctx.prec=256
        domain=TaylorDomain([(0,1,'interval')],1)
        # f(theta,u,eta)=2u-3eta+theta*(u+4eta)+e,
        # with |e| <= 1/10 on max(|u|,|eta|)<=1.
        model=InputLinearTaylor(domain,arb_mat([[2,-3]]),arb_mat([[1,4]]),
                                arb('1/10'),[(0,1,'euclidean'),(1,2,'box')])
        # u=2, eta=(1/4+theta/2)*u; eta lies in [-1/2,3/2].
        direction=arb_mat([[2],[arb('1/2',1)]])
        restricted=model.at_input(direction)
        assert restricted.r==arb('1/5').upper()
        enclosure=restricted.enclosure()
        # The exact polynomial is 5/2+theta+4theta^2. Its minimum
        # occurs at theta=-1/8; endpoints and both remainder extremes
        # test the interior extremum as well as the boundary.
        for theta in (arb(-1),arb('-1/8'),arb(0),arb(1)):
            eta=arb('1/2')+theta
            exact=4-3*eta+theta*(2+4*eta)
            for sign in (-1,1):
                assert enclosure.contains(exact+sign*arb('1/5'))
    finally:
        ctx.prec=previous
