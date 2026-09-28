import math
import mpmath as mp
import pytest
from flint import arb, ctx
from bhsm.interface.boundary_heat_moment import collar_weyl_upper, boundary_heat_moment_upper


def test_half_line_zero_threshold_continuous_spectrum():
    ctx.prec = 256
    # Exact M(-u)=sqrt(u), M(0)=0 for the free half-line. No positive gap.
    ell = arb(2); u = arb(1)/4
    upper = boundary_heat_moment_upper(weyl_shift_upper=u.sqrt(), weyl_zero_lower=0,
                                      heat_length=ell, spectral_shift=u)
    exact = 1/(2*arb.pi().sqrt()*ell)
    assert exact < upper
    assert upper == arb(1)/4


def test_complete_longer_interval_is_bounded_by_short_collar():
    # Current collar length .2, full Dirichlet domain length 3.
    # Its heat pressure is NOT the spectrum of the .2 collar.
    ctx.prec = 256
    bound = collar_weyl_upper(duration=arb('.2'), coefficient_upper=arb('.7'),
                             spectral_shift=1, channel='scalar')
    upper = boundary_heat_moment_upper(weyl_shift_upper=bound, weyl_zero_lower=0,
                                      heat_length=1, spectral_shift=1)
    with mp.workdps(80):
        T, V = mp.mpf(3), mp.mpf('.7')
        exact = sum(mp.exp(-((mp.pi*k/T)**2+V))*((mp.pi*k)**2/T**3)
                    /((mp.pi*k/T)**2+V) for k in range(1, 100))
        assert arb(str(exact)) < upper


@pytest.mark.parametrize('W', ['-2', '2'])
def test_factorized_trial_bound_includes_both_conormal_orientations(W):
    ctx.prec = 256
    T, w, u = arb('.3'), arb(W), arb(1)
    k = (w*w+u).sqrt()
    # Far Dirichlet is the extremal nonnegative terminal load.
    actual = k/(k*T).tanh()-w
    upper = collar_weyl_upper(duration=T, coefficient_upper=abs(w), spectral_shift=u,
                             channel='product_Dirac')
    assert actual < upper


def test_wrong_heat_shift_cannot_be_used_for_this_majorant():
    with pytest.raises(ValueError, match='ell'):
        boundary_heat_moment_upper(weyl_shift_upper=3, weyl_zero_lower=0,
                                   heat_length=1, spectral_shift=arb('.5'))
