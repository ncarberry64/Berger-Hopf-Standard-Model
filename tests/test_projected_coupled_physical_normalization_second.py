import numpy as np
import pytest
from flint import arb, ctx
from bhsm.interface.projected_coupled_physical_normalization_second import normalized_mixed


def jet(descriptor):
    return dict(configuration=np.array([[arb(0)],[arb(0)]],dtype=object),
        psi=np.array([[arb(0)]],dtype=object),hard=np.array([[arb(0)]],dtype=object),
        border=np.array([arb(0)],dtype=object),descriptor=np.array([descriptor],dtype=object),
        cpsi=np.array([arb(0)],dtype=object),remainder=np.array([arb(0)],dtype=object))


def evaluate(descriptor,projection):
    ctx.prec=256
    return normalized_mixed([arb(1),arb(1)],[arb(1)],[arb(1)],[arb(0)],arb(1),descriptor,
        arb(0),arb(0),jet(arb(1)),jet(arb(1)),jet(arb(0)),np.array(projection,dtype=object),
        coupled_identities_and_variations=True)


def test_common_scalar_cancellation_on_entire_descriptor_interval():
    # The first two physical outputs both equal s/sqrt(1+2s^2).
    # Their difference and every derivative are exactly zero even for interval s.
    result,proof=evaluate(arb(2,arb('0.1')),[[arb(1),arb(-1),arb(0),arb(0)]])
    assert result.shape==(1,1) and result[0,0].is_zero()
    assert proof['original_unprojected_physical_norm_retained']


def test_nonzero_projection_matches_closed_form_second_derivative():
    s=arb(2)
    result,_=evaluate(s,[[arb(2),arb(0),arb(0),arb(0)]])
    expected=-12*s/((1+2*s*s)**2*(1+2*s*s).sqrt())
    assert result[0,0].overlaps(expected)
    assert abs(result[0,0]-expected).upper()<arb('1e-70')


def test_projection_requires_every_physical_coordinate():
    with pytest.raises(ValueError,match='complete physical input'):
        evaluate(arb(2),[[arb(1),arb(0)]])
