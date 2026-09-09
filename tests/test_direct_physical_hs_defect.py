import pytest
from flint import arb,ctx
from bhsm.interface.direct_physical_hs_defect import local_defect_blocks


def test_scalar_linear_ode_has_exact_expected_newton_defect_signs():
    result=local_defect_blocks([[.75]],[[.75]],[[.75]],.5,[[1]],[[1]],[[1]],[[-1]],[[1]])
    assert result['C'][0,0]==-1
    assert result['DL'][0,0].contains(arb(51)/256)
    assert result['DR'][0,0].contains(arb(45)/256)


def test_exact_frozen_jacobian_has_zero_defect_with_nonorthogonal_frames():
    # f=0, trial=[1,2]^T, test=[3,4], R=T*E=11; L=-I.
    zero=[[0,0],[0,0]]
    result=local_defect_blocks(zero,zero,zero,1,[[1],[2]],[[1],[2]],[[3,4]],[[-1,0],[0,-1]],[[11]])
    assert result['C'][0,0].contains(-1)
    assert result['DL'][0,0].is_zero() and result['DR'][0,0].contains(0)


def test_fixed_initial_endpoint_removes_only_its_input_block():
    args=([ [.75] ],[ [.75] ],[ [.75] ],.5,[[1]],[[1]],[[1]],[[-1]],[[1]])
    free=local_defect_blocks(*args)
    fixed=local_defect_blocks(*args,initial_endpoint_fixed=True)
    assert fixed['DL'][0,0].is_zero()
    for name in ('C','DR'):
        assert fixed[name][0,0].mid()==free[name][0,0].mid()
        assert fixed[name][0,0].rad()==free[name][0,0].rad()


def test_invalid_frame_or_initial_condition_restores_precision():
    previous=ctx.prec
    args=([[0]],[[0]],[[0]],1,[[1]],[[1]],[[1]],[[-1]],[[1]])
    with pytest.raises(ValueError):local_defect_blocks(*args,initial_endpoint_fixed=1)
    with pytest.raises(ValueError):local_defect_blocks(*args[:-1],[[1,0],[0,1]])
    assert ctx.prec==previous
