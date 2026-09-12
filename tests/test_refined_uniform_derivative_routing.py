"""Refinement must use private producers and retain the original derivative call."""
from pathlib import Path
import sys
import numpy as np
from flint import arb

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import certify_n12_gate7_coupled_endpoint_uniform_derivatives as original
import certify_n12_gate7_coupled_midpoint_uniform_derivatives as original_midpoint
import certify_n12_gate7_uniform_physical_local_defects as original_local
import certify_n12_gate7_refined_endpoint_uniform_derivatives as endpoint
import certify_n12_gate7_refined_midpoint_uniform_derivatives as midpoint
import certify_n12_gate7_refined_uniform_physical_local_defects as local
import n12_gate7_refined_uniform_derivative_adapter as adapter


def test_refinement_does_not_mutate_original_dependency_graphs():
    assert original.WORK.name=='.coupled_endpoint_uniform_df_work'
    assert original_midpoint.WORK.name=='.coupled_midpoint_uniform_df_work'
    assert original_local.endpoint is original and original_local.midpoint is original_midpoint
    assert local.engine.endpoint is endpoint and local.engine.midpoint is midpoint
    assert endpoint.engine is not original and midpoint.engine is not original_midpoint


def test_refinement_calls_the_unwrapped_batch_and_retains_new_source_binding(monkeypatch):
    calls=[]
    def refine(base,source,start,stop):
        assert base.evaluate_batch is not endpoint.engine.evaluate_batch
        calls.append((start,stop))
        return dict(derivative=np.full((99,stop-start),arb(1)),
            preconditioned_variation_rhs=np.full((2,62,stop-start),arb(0))),dict(refined=True)
    monkeypatch.setattr(adapter.refinement,'refine_batch',refine)
    monkeypatch.setattr(endpoint.p,'verify_sources',lambda binding:None)
    _,report=endpoint.evaluate(dict(binding={},raw_domain=np.full(99,arb(0))))
    assert calls==[(i,min(i+9,99)) for i in range(0,99,9)]
    assert report['common_border_scale_canceled_before_differentiation']
    assert report['actual_HS_midpoint_domain_enclosed'] is False
    assert len(report['coupled_normalization_batches'])==11
