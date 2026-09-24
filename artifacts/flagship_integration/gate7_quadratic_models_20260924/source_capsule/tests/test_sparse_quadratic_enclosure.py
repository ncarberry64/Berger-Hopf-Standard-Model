"""Numerical compiler checks; no scientific producer is invoked."""
from flint import arb,ctx
from bhsm.interface.sparse_quadratic_enclosure import QuadraticDomain,QuadraticStore


def test_symmetric_shared_products_cancel_before_support():
    d=QuadraticDomain([(0,1,'interval'),(1,2,'interval')],2)
    x=d.model(a={0:arb(1)});y=d.model(a={1:arb(1)})
    z=x*y-y*x
    bound,q,_=z.final_support()
    assert not q and bound.is_zero()


def test_euclidean_identity_quadratic_is_one_not_dimension():
    d=QuadraticDomain([(0,74,'euclidean')],74)
    p=d.model()
    for i in range(74):
        x=d.model(a={i:arb(1)});p+=x*x
    bound,q,_=p.final_support()
    assert 1<=bound<arb('1.000001') and len(q)==74


def test_one_dimensional_stationary_point_and_signed_diagonal():
    d=QuadraticDomain([(0,1,'interval')],1)
    x=d.model(a={0:arb(1)})
    p=1-x*x
    assert 1<=p.final_support()[0]<arb('1.000001')
    interval,_=d.polynomial_range(arb(0),{0:arb(1)},{(0,0):arb(-1)})
    assert interval.contains(arb(1)/4) and interval.contains(-2)


def test_cubic_and_independent_error_terms_remain_enclosed():
    d=QuadraticDomain([(0,1,'interval')],1)
    x=d.model(a={0:arb(1)},tails={'leaf':arb(1)/8})
    y=x*x*x
    assert y.final_support()[0]>=arb(9)**3/arb(8)**3
    assert y.tails['cubic_and_higher']>0


def test_unary_degree_two_retains_coefficients_and_encloses_samples():
    ctx.prec=160
    for op,center,lower in [('inverse',2,1),('sqrt_positive',2,1),('log',2,None),('exp',0,None)]:
        d=QuadraticDomain([(0,1,'interval')],1)
        x=d.model(center,{0:arb(1)/8})
        y=x.unary(op,lower);q=y.expanded()
        assert (0,0) in q
        for t in (-1,arb(-1)/3,0,arb(1)/3,1):
            value=arb(center)+t/8
            actual={'inverse':lambda:1/value,'sqrt_positive':value.sqrt,'log':value.log,'exp':value.exp}[op]()
            prediction=y.c+y.a[0]*t+q[0,0]*t*t
            assert (prediction+arb(0,y.r)).contains(actual)


def test_disk_circuit_preserves_alias_cancellation(tmp_path):
    d=QuadraticDomain([(0,2,'euclidean')],2,QuadraticStore(tmp_path/'q.sqlite'))
    x=d.model(a={0:arb(2),1:arb(-3)})
    p=x*x
    z=p.scale(7)-p.scale(7)
    assert z.final_support()[0].is_zero()


def test_frontier_eviction_bit_exact_at_multiple_precisions(tmp_path):
    from bhsm.interface.quadratic_frontier_cache import FrontierCache,pack_ball,unpack_ball
    for bits in (53,160,512):
        ctx.prec=bits
        d=QuadraticDomain([(0,1,'interval')],1)
        cache=FrontierCache(d,tmp_path/f'frontier{bits}.sqlite',capacity=1)
        for i in range(1,40):
            value=(arb(i)/arb(41)).exp()+arb(0,arb(i)*arb(2)**(-i))
            assert pack_ball(unpack_ball(pack_ball(value)))==pack_ball(value)
            cache[i]=d.model(value,{0:value/7}, {'q_implicit_correction':abs(value).upper()})
        for i in range(1,40):
            value=(arb(i)/arb(41)).exp()+arb(0,arb(i)*arb(2)**(-i))
            assert pack_ball(cache[i].c)==pack_ball(value)


def test_booking_symmetric_pairs_and_transverse_groups_share_keys():
    from flint import arb_mat
    from bhsm.interface.shared_quadratic_booking import projected_booking
    blocks={'LL':{},'LT':{}}
    for key in ('00','01','10','11'):
        blocks['LL'][key]=arb_mat([[0]])
        blocks['LT'][key]=arb_mat(1,74)
    blocks['LL']['01'][0,0]=2;blocks['LL']['10'][0,0]=3
    blocks['LT']['01'][0,4]=-7
    q=projected_booking(blocks,arb_mat([[1]]),arb(1)/2,arb(1)/4)
    assert q[150,375]==arb(5)/4
    assert q[225,300]==arb(5)/4
    assert q[150,380]==arb(-7)/4
    assert q[230,300]==arb(-7)/4


def test_full_second_incidence_reuses_endpoint_products_including_descriptor():
    from bhsm.interface.shared_hs_output_operator import composed_operators
    from flint import arb_mat
    d=QuadraticDomain([(0,1,'interval'),(1,2,'interval')],2)
    u=d.model(a={0:arb(1)});v=d.model(a={1:arb(1)})
    left=[u*v*(i+1) for i in range(99)]
    right=[u*v*(2*i-7) for i in range(99)]
    A=arb_mat(99,99,[arb(i==j)*(i+1)/100 for i in range(99) for j in range(99)])
    P=arb_mat(1,99,[arb(0)]*98+[arb(1)])
    h=arb(1)/4
    M=[(a-b)*(h/8) for a,b in zip(left,right)]
    incidence=sum((M[j]*A[98,j] for j in range(99)),d.model())
    direct=(left[98]+right[98])*(h/6)+incidence*(2*h/3)
    op=composed_operators(P,A,h)
    fused=sum((left[j]*op[0][0,j]+right[j]*op[2][0,j] for j in range(99)),d.model())
    assert direct.expanded()[0,1].overlaps(fused.expanded()[0,1])
    assert direct.r.is_zero() and fused.r.is_zero()


def test_common_normalization_first_products_remain_quadratic():
    d=QuadraticDomain([(0,1,'interval'),(1,2,'interval')],2)
    u=d.model(a={0:arb(1)});v=d.model(a={1:arb(1)})
    nu=d.model(1);nuu=u;nuv=v
    nuuv=(d.model()-nuu*nuv)*nu.unary('inverse',1)
    rateuv=(d.model()-nuuv*d.model(2)-nuu*(3*v)-nuv*(5*u))*nu.unary('inverse',1)
    assert rateuv.expanded()[0,1]==-6
    assert rateuv.r.is_zero()


def test_block_expansion_matches_scalar_with_canonical_transposes():
    from bhsm.interface.block_quadratic_expansion import expand_blocks,expand_batched
    groups=[(0,12,'euclidean'),(12,24,'euclidean')]
    d=QuadraticDomain(groups,24)
    a=d.model(a={i:arb(i-7) for i in range(24)})
    b=d.model(a={i:arb(11-i) for i in range(24)})
    q=a*b+3*b*a-a*a
    scalar=q.expanded();block=expand_blocks(d.store,[(q.q,arb(1))],groups)
    assert scalar.keys()==block.keys()
    assert all(scalar[k]==block[k] for k in scalar)
    batched=expand_batched(d.store,[(q.q,arb(1))],groups,batch_size=2)
    assert scalar.keys()==batched.keys()
    assert all(scalar[k]==batched[k] for k in scalar)


def test_longitudinal_cross_block_signs_survive_until_vertex_support():
    from bhsm.interface.quadratic_group_support import grouped_range
    d=QuadraticDomain([(i,i+1,'interval') for i in range(4)],4)
    q={(0,2):arb(1),(0,3):arb(1),(1,2):arb(1),(1,3):arb(-1)}
    value,structure=grouped_range(d,arb(0),{},q)
    assert value.contains(-2) and value.contains(2)
    assert abs(value).upper()<arb('2.000001')
    assert structure[-1]['vertices']==16


def test_circuit_reuse_preserves_aliases_and_refuses_changed_coefficients():
    import pytest
    from bhsm.interface.quadratic_circuit_identity import verify_identity
    a=QuadraticDomain([(0,2,'euclidean')],2);b=QuadraticDomain([(0,2,'euclidean')],2)
    ax=a.model(a={0:arb(1)});ay=a.model(a={1:arb(2)})
    bx=b.model(a={0:arb(1)});by=b.model(a={1:arb(2)})
    unused=bx*bx
    left=ax*ay;right=bx*by
    assert left.q!=right.q
    assert verify_identity(a.store.db,b.store.db,[(left.q,right.q)])['verified']
    with pytest.raises(ValueError):verify_identity(a.store.db,b.store.db,[(left.q,unused.q)])
