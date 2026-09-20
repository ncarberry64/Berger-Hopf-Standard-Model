from flint import arb, arb_mat, ctx
import pytest
from bhsm.interface.shared_action_taylor import TaylorDomain
from bhsm.interface.input_linear_taylor import InputLinearTaylor
from bhsm.interface.fixed_axis_input_restriction import restrict_physical_axis


@pytest.mark.parametrize('axis',[(0.6,0.8),(3,4),(0,0)])
@pytest.mark.parametrize('scale',[0,0.25,2])
@pytest.mark.parametrize('json_groups',[False,True])
def test_restriction_encloses_original_at_complete_inputs(axis,scale,json_groups):
    ctx.prec=128
    domain=TaylorDomain([(0,2,'box')],2)
    groups=[(0,2,'euclidean'),(2,3,'box')]
    if json_groups: groups=[list(group) for group in groups]
    original=InputLinearTaylor(domain,arb_mat([[2,3,5]]),
        arb_mat([[7,11,13],[17,19,23]]),arb('0.125'),
        groups)
    restricted=restrict_physical_axis(original,arb_mat([[axis[0]],[axis[1]]]),2,[scale])
    assert restricted.domain is domain
    assert restricted.input_groups==((0,1,'euclidean'),(1,2,'box'))
    for t,e in ((1,1),(-1,-1),(0.25,-0.5)):
        old=original.at_input(arb_mat([[arb(axis[0])*t],[arb(axis[1])*t],[arb(e)*scale]]))
        new=restricted.at_input(arb_mat([[t],[e]]))
        assert new.c.overlaps(old.c)
        assert all(a.overlaps(b) for a,b in zip(new.a.entries(),old.a.entries(),strict=True))
        assert new.r >= old.r


def test_restriction_rejects_unmapped_auxiliary_groups():
    domain=TaylorDomain([(0,1,'box')],1)
    model=InputLinearTaylor(domain,arb_mat([[1,2,3]]),arb_mat([[0,0,0]]),
        input_groups=[(0,3,'euclidean')])
    with pytest.raises(ValueError):
        restrict_physical_axis(model,arb_mat([[1],[0]]),2)
