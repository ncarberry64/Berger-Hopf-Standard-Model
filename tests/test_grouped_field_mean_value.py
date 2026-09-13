import pytest
from flint import arb
from bhsm.interface.grouped_field_mean_value import enclose_field


def test_signed_tangent_cancellation_and_uncertain_anchor_are_retained():
    large = 2**70
    anchor = [arb(7, '.125'), arb(-2, '.25')]
    candidate, support, _ = enclose_field(anchor, [[large, -large], [1, 1]],
        [[1], [1]], [dict(start=0, stop=1, norm='interval', radius=1)])
    assert support[0].is_zero()
    assert candidate[0].contains(anchor[0])
    assert candidate[0].rad() > 0
    assert support[1] == 2
    assert candidate[1].contains(arb('-4.25'))
    assert candidate[1].contains(arb('.25'))


def test_missing_affine_group_cannot_shrink_the_enclosure():
    with pytest.raises(ValueError, match='all directions'):
        enclose_field([0], [[1, 1]], [[1, 0], [0, 1]],
                      [dict(start=0, stop=1, norm='interval', radius=1)])
