"""Verify the coupled norm identity on exact normalized/orthogonal examples."""
import numpy as np
import pytest
from flint import arb,ctx
from bhsm.interface.coupled_physical_normalization import normalized_value


def test_unit_constraint_removes_spurious_norm_variation_at_zero_descriptor():
    previous=ctx.prec;ctx.prec=256
    try:
        psi=[arb('.6','.01'),arb('.8','.01')]
        result,proof=normalized_value([2],[1,1],psi,[-.8,.6],arb(1,'.2'),0,arb(1)/10,3,
            normalized_eigenpair=True,bordered_orthogonality=True)
        assert all(result[i+1].contains(v) and float(result[i+1].rad())<1.000001*float(v.rad())
                   for i,v in enumerate(psi))
        assert proof['factored_norm_lower_rational']=='1'
    finally:ctx.prec=previous


def test_identity_matches_original_formula_with_nontrivial_metric_and_both_signs():
    previous=ctx.prec;ctx.prec=256
    try:
        psi=np.array([arb(3)/5,arb(4)/5]);hard=np.array([-arb(8)/5,arb(6)/5])
        for b in (arb(2),arb(-2)):
            s=arb(1)/8;w=np.array([arb(1),arb(3)]);configuration=[arb(3)]
            result,_=normalized_value(configuration,w,psi,hard,b,s,arb(1)/4,arb(1)/16,
                normalized_eigenpair=True,bordered_orthogonality=True)
            G=np.concatenate((np.array([3*s]),w*(b*psi+s*hard)))
            norm=sum((v**2 for v in G),arb(0)).sqrt()
            expected=np.concatenate((G/norm,np.array([(b/4+s/16)/norm])))
            assert all(a.overlaps(v) for a,v in zip(result,expected))
    finally:ctx.prec=previous


def test_plain_component_boxes_do_not_authorize_coupled_identity():
    with pytest.raises(ValueError,match='verified coupled'):
        normalized_value([1],[1],[1],[0],1,1,1,1)
