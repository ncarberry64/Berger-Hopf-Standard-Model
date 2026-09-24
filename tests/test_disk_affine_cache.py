from flint import arb
from bhsm.interface.shared_expression_graph import ExpressionDomain, pair
from bhsm.interface.disk_affine_cache import DiskAffineCache


def test_eviction_does_not_change_outward_arithmetic():
    results=[]
    for capacity in (1, 100):
        d=ExpressionDomain([(0,1,'interval')],['theta'])
        d.bounds=DiskAffineCache(d.backend,capacity)
        x=d.variable(0,arb('1 +/- 0.01'),arb('0.1'))
        y=(x*x+x).exp()
        result=d.export({'result':y})
        results.append(result)
        for t in (-1,0,1):
            v=arb(1)+arb('0.1')*t
            assert y.enclosure().contains((v*v+v).exp())
    assert results[0]==results[1]


def test_cache_keeps_center_and_signed_coefficients_outward():
    d=ExpressionDomain([(0,1,'interval')],['theta'])
    x=d.backend.affine(arb('1 +/- 0.01'),[arb('-2 +/- 0.001')],3)
    cache=DiskAffineCache(d.backend,1)
    cache[0]=x
    first=cache[0]
    cache[1]=d.backend.affine(0)
    second=cache[0]
    assert pair(first.c)==pair(second.c)
    assert pair(first.coefficients[0])==pair(second.coefficients[0])
    assert second.c.contains(x.c)
    assert second.coefficients[0].contains(x.coefficients[0])
