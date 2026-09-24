from flint import arb,arb_mat,ctx
from bhsm.interface.shared_expression_graph import ExpressionDomain
from bhsm.interface.sparse_affine_enclosure import SparseDomain
from bhsm.interface.projected_affine_enclosures import ProjectedAffineModels,booked_affine_relaxation
from bhsm.interface.shared_projected_rate import LinkedModels,projected_mixed


def test_matrix_projection_compiler_matches_exact_constant_jet_recipe():
    old=ctx.prec;ctx.prec=256
    try:
        d=ExpressionDomain([(0,1,'interval')],['theta'])
        roots={}
        for key,row in zip(('value','u','v','uv'),((2,3),(4,-1),(-2,1),(3,7))):
            for i,x in enumerate(row):roots[f'factored_numerator/{key}/{i}']=d.affine(x)
        for key,x in zip(('norm','norm_u','norm_v','norm_uv'),(2,3,-2,4)):
            roots['normalization/'+key]=d.affine(x)
        payload=d.export(roots);backend=SparseDomain(d.groups,1)
        fast=ProjectedAffineModels(backend,payload,2)
        q=ExpressionDomain(d.groups,d.names);models=LinkedModels(q,payload,'test-parent')
        P=arb_mat([[1,-2],[3,1]])
        for i,value in enumerate(fast.mixed(P)):
            slow=projected_mixed(models,[P[i,j] for j in range(2)]).enclosure()
            assert (value.enclosure()-slow).contains(0)
            assert value.enclosure().rad()<arb('1e-60')
    finally:ctx.prec=old


def test_bilinear_booking_compiler_fuses_opposite_cross_coefficients():
    d=SparseDomain([(0,1,'interval')],1)
    zero=arb_mat([[0]])
    blocks={'LL':{'00':zero,'11':zero,'01':arb_mat([[3]]),'10':arb_mat([[-3]])},
        'LT':{'00':zero,'01':zero,'10':zero,'11':zero}}
    assert booked_affine_relaxation(d,blocks,arb(1),arb(1))[0].support().is_zero()


def test_matrix_compiler_cancels_a_repeated_parent_function_before_tail_bound():
    d=ExpressionDomain([(0,1,'interval'),(1,2,'interval')],['u','v'])
    u,v=d.variable(0),d.variable(1);one=d.affine(1);zero=d.affine(0)
    roots={}
    for key,x in (('value',one),('u',u),('v',v),('uv',u*v)):
        for i in range(2):roots[f'factored_numerator/{key}/{i}']=x
    for key,x in (('norm',one),('norm_u',zero),('norm_v',zero),('norm_uv',zero)):
        roots['normalization/'+key]=x
    metadata=d.export(roots)
    model=ProjectedAffineModels(SparseDomain(d.groups,2),metadata,2)
    assert model.mixed(arb_mat([[1,-1]]))[0].support().is_zero()
