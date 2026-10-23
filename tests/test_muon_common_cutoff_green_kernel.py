import math
import numpy as np
import pytest
from bhsm.interface.muon_common_cutoff_green_kernel import (
    common_total_cutoff_green_kernel,common_total_cutoff_boundary_kernel,
    certified_three_green_point,
    rigorous_frobenius_upper,outward_positive_product_sum,contraction_series_tail_upper,
)


def test_coincident_and_near_coincident_three_green_resolve_without_subtraction():
    p=9.6813540017e10;c=1.0329133712274834e-11
    for triple in ((p,p,p),(p,np.nextafter(p,np.inf),p+100.)):
        a=common_total_cutoff_green_kernel(*triple,cutoff=c)
        lo,hi=certified_three_green_point(*triple,c)
        roundoff=32*np.finfo(float).eps*float(a['value'])
        assert lo-a['positive_series_truncation_upper']-roundoff<=a['value']<=hi+roundoff
    exact=math.exp(-c*p)*(c*c/(2*p)+c/p**2+1/p**3)
    assert float(common_total_cutoff_green_kernel(p,p,p,cutoff=c)['value'])==pytest.approx(exact,rel=3e-15)


def test_common_simplex_tail_covers_noncoincident_three_green_and_cutoff_motion():
    p,q,r=3.,3.1,3.2;c=.7
    a=common_total_cutoff_green_kernel(p,q,r,cutoff=c,terms=4)
    lo,hi=certified_three_green_point(p,q,r,c)
    assert a['value']<=hi
    assert lo<=a['value']+a['positive_series_truncation_upper']
    b=common_total_cutoff_boundary_kernel(p,p,cutoff=c)
    assert float(b['value'])==pytest.approx(c*math.exp(-c*p),rel=2e-15)
    d=common_total_cutoff_boundary_kernel(p,p,p,cutoff=c)
    assert float(d['value'])==pytest.approx(c*c*math.exp(-c*p)/2,rel=2e-15)


def test_zero_cutoff_and_unresolved_spectral_ranges_fail_cleanly():
    a=common_total_cutoff_green_kernel(2.,2.1,2.2,cutoff=0.)
    assert a['value']==pytest.approx(1/(2*2.1*2.2))
    with pytest.raises(ValueError):common_total_cutoff_green_kernel(1.,2.,3.,cutoff=.1)
    with pytest.raises(ValueError):common_total_cutoff_green_kernel(1.,0.,1.,cutoff=.1)
    for value in (1.+0j, 1.+1j, '1', np.array([1.],dtype=object)):
        with pytest.raises(ValueError):common_total_cutoff_green_kernel(value,1.,1.,cutoff=.1)
        with pytest.raises(ValueError):certified_three_green_point(value,1.,1.,.1)
    with pytest.raises(ValueError):common_total_cutoff_green_kernel(1.,1.,1.,cutoff=.1+0j)


def test_contracted_series_tail_norms_and_positive_arithmetic_are_outward():
    from flint import arb,ctx
    rng=np.random.default_rng(3)
    matrices=[rng.normal(size=(3,4))+1j*rng.normal(size=(3,4)),
              rng.normal(size=(4,5))+1j*rng.normal(size=(4,5)),
              rng.normal(size=(5,2))+1j*rng.normal(size=(5,2))]
    with ctx.workprec(192):
        exact=[]
        for a in matrices:
            squared=sum((arb(float(z.real))**2+arb(float(z.imag))**2 for z in a.flat),arb(0))
            bound=rigorous_frobenius_upper(a)
            assert arb(bound)**2>=squared
            exact.append(squared.sqrt())
        t=1e-43;gram=.73
        bound=contraction_series_tail_upper(t,*matrices,gram)
        assert arb(bound)>=arb(t)*exact[0]*exact[1]*exact[2]/arb(gram)
        value=outward_positive_product_sum([[t,bound],[1e-55,3.1]])
        assert arb(value)>=arb(t)*arb(bound)+arb(1e-55)*arb(3.1)
    assert rigorous_frobenius_upper(np.zeros((2,2)))==0.
    with pytest.raises(ValueError):rigorous_frobenius_upper(np.array([arb(1)],dtype=object))
    with pytest.raises(ValueError):outward_positive_product_sum([[1.,-.1]])
