"""Exact algebra tests for normalized-eigenpair Banach bounds."""
import itertools
import numpy as np
import pytest
from flint import arb,arb_mat,ctx
from bhsm.interface.affine_eigenpair_contraction import (
    affine_row_bounds,nonlinear_eigenpair_variation,certify_rows,grow_failed_coordinates)


@pytest.fixture(autouse=True)
def precision():
    previous=ctx.prec;ctx.prec=256
    yield
    ctx.prec=previous


def test_transverse_ball_uses_complete_signed_columns_and_euclidean_norm():
    result=affine_row_bounds([[2,-3,4]],.5,.25)
    assert result[0]>=arb(9)/4
    assert float(result[0])<2.251


def test_nonlinear_formula_covers_every_corner_of_small_eigenpair_box():
    R=arb_mat([[2,-1,3],[-2,4,-1],[1,2,-3]])
    r=[arb(1)/8,arb(1)/16,arb(1)/32]
    bounds=nonlinear_eigenpair_variation(np.array(R.entries()).reshape(3,3),r)
    for signs in itertools.product((-1,1),repeat=3):
        v0,v1,s=[a*b for a,b in zip(r,signs)]
        delta=arb_mat([[-s,0,-v0],[0,-s,-v1],[v0,v1,0]])
        product=R*delta
        for i in range(3):
            actual=sum((abs(product[i,j])*r[j] for j in range(3)),arb(0))
            assert bounds[i]>=actual


def test_factor_two_and_normalization_row_are_required():
    r=[arb(1)/8,arb(1)/16,arb(1)/32]
    bound=nonlinear_eigenpair_variation(np.eye(3),r)
    assert bound[0]==2*r[2]*r[0]
    assert bound[2]==r[0]**2+r[1]**2


def test_row_certificate_requires_strict_inclusion_not_only_contraction():
    r=[arb(1)/8,arb(1)/8]
    V,report=certify_rows([0,0],np.zeros((2,2)),np.eye(2),r,[0,0])
    assert report['validation_passed']
    _,boundary=certify_rows([r[i]-V[i] for i in range(2)],np.zeros((2,2)),np.eye(2),r,[0,0])
    assert not boundary['validation_passed']
    assert all(x['strict_contraction'] for x in boundary['rows'])


def test_growth_changes_only_failed_proposal_coordinates():
    result,changed=grow_failed_coordinates([.125,.125],[.125,1],[1,1])
    assert changed==[1] and result[0]==1 and result[1]==arb(27)/16


def test_negative_bounds_uncertain_radii_and_incomplete_shapes_fail_closed():
    with pytest.raises(ValueError,match='nonnegative'):
        certify_rows([-1,0],np.eye(2),np.eye(2),[1,1],[0,0])
    with pytest.raises(ValueError,match='exact positive'):
        nonlinear_eigenpair_variation(np.eye(2),[arb(1,'.1'),1])
    with pytest.raises(ValueError,match='complete'):
        certify_rows([0],np.eye(2),np.eye(2),[1,1],[0,0])
