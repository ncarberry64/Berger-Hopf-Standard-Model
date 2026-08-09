from pathlib import Path
import json, math
import numpy as np
import pytest

from bhsm.interface.completion.bulk_cancellation_dtn_shape_d4_v14_77 import (
    VERSION, PRIMARY_VERDICT, EXACT_NEXT_OBJECT,
    complementary_bulk_action, complementary_cap_sum, partition_derivative_witness,
    bulk_cancellation_payload, mismatch_formula_payload, dtn_two_sided_uniform,
    dtn_uniform_coefficients, dtn_uniform_derivatives, dtn_threshold,
    dtn_quartic_sign, dtn_shape_quartic_payload, finite_difference_even_coefficients,
    dtn_finite_difference_payload, dtn_action_shape_coefficients,
    dtn_vs_response_sign_payload, source_update_payload, ell2_handoff_payload,
    status_payload, completion_gate_payload, artifact_payloads, materialize,
)

def test_version():
    assert VERSION=="v14.77"
    assert "COMPLEMENTARY" in PRIMARY_VERDICT
    assert "OPERATOR_VALUED" in EXACT_NEXT_OBJECT

def test_complementary_sum():
    assert complementary_cap_sum(2.3,5.0,1,1)==7.3
    assert complementary_bulk_action(7.3)==7.3

def test_partition_witness_equal_constant():
    vals=[partition_derivative_witness(d)["equal_sum"] for d in (-1,-.2,0,.4,.9)]
    assert max(vals)-min(vals)<1e-14

def test_partition_witness_unequal_varies():
    vals=[partition_derivative_witness(d)["unequal_sum"] for d in (-1,-.2,0,.4,.9)]
    assert max(vals)-min(vals)>1e-3

def test_bulk_payload():
    p=bulk_cancellation_payload()
    assert p["D4_fixed_background_equal_cap_bulk"]==0
    assert p["synthetic_equal_sum_spread"]<1e-14
    assert p["synthetic_unequal_sum_spread"]>1e-3

def test_mismatch_payload():
    p=mismatch_formula_payload()
    assert "c+-c-" in p["formula"]
    assert p["physical_mismatch_derived"] is False

def test_dtn_even():
    q,L,d=.9,1.2,.1
    assert abs(dtn_two_sided_uniform(q,L,d)-dtn_two_sided_uniform(q,L,-d))<1e-14

def test_dtn_delta_zero():
    q,L=.8,1.1
    c=dtn_uniform_coefficients(q,L)
    assert abs(dtn_two_sided_uniform(q,L,0)-c["N0"])<1e-14

def test_dtn_derivative_parity():
    d=dtn_uniform_derivatives(1.0,.8)
    assert d["D1"]==0 and d["D3"]==0
    assert d["D2"]<0

def test_dtn_threshold():
    x=dtn_threshold()
    assert abs(math.tanh(x)**2-2/3)<1e-14
    assert 1.0<x<1.3

def test_dtn_quartic_signs():
    assert dtn_quartic_sign(1,.5)=="POSITIVE"
    assert dtn_quartic_sign(1,2)=="NEGATIVE"
    assert dtn_quartic_sign(1,dtn_threshold(),1e-10)=="ZERO"

def test_dtn_payload():
    p=dtn_shape_quartic_payload()
    assert p["this_is_v14_30_derivative_expansion_c4"] is False
    assert p["this_is_a_shape_derivative_of_exact_DtN"] is True
    assert p["physical_ell2_Landau_coefficient"] is False
    signs={r["quartic_sign"] for r in p["rows"]}
    assert {"POSITIVE","NEGATIVE","ZERO"}.issubset(signs)

def test_fd_coefficients_case1():
    q,L=.8,.7
    exact=dtn_uniform_coefficients(q,L)
    fd=finite_difference_even_coefficients(q,L,2e-3)
    assert abs(fd["a2"]-exact["a2"])<1e-7
    assert abs(fd["a4"]-exact["a4"])<2e-5

def test_fd_payload():
    p=dtn_finite_difference_payload()
    assert p["max_a2_residual"]<1e-7
    assert p["max_a4_residual"]<2e-5

def test_dtn_action_shape_scale():
    c=dtn_uniform_coefficients(1,.6)
    a=dtn_action_shape_coefficients(1,.6,2.0)
    assert abs(a["a2_shape"]-c["a2"])<1e-14
    assert abs(a["a4_shape"]-c["a4"])<1e-14

def test_dtn_action_invalid_norm():
    with pytest.raises(ValueError):
        dtn_action_shape_coefficients(1,1,-1)

def test_response_comparison():
    p=dtn_vs_response_sign_payload()
    assert p["thin_quartic_positive"] is True
    assert p["thick_quartic_negative"] is True
    assert p["no_contradiction"] is True

def test_source_update():
    p=source_update_payload()
    assert p["new_exact_positive_candidate"]=="two-sided DtN uniform-width shape a4 for qL below threshold"
    assert p["physical_ell2_positive_D4_derived"] is False
    assert p["physical_r_u_v_status"]=="OPEN"

def test_handoff_blocked():
    p=ell2_handoff_payload()
    assert p["uniform_width_theorem_is_ell2_result"] is False
    assert p["eligible_for_physical_Landau_extraction"] is False

def test_status():
    p=status_payload()
    assert len(p["validated"])>=10
    assert p["FULL_BHSM_COMPLETE"] is False
    assert p["MARK_III"]=="NOT_REACHED"
    assert p["USB_touched"] is False

def test_completion_gate():
    p=completion_gate_payload()
    assert p["validation_passed"] is True
    assert p["fixed_background_equal_cap_local_bulk_D4"]=="ZERO"
    assert p["fixed_background_equal_cap_GHY_D4"]=="ZERO"
    assert p["uniform_two_sided_DtN_shape_D4"]=="SIGN_INDEFINITE_WITH_POSITIVE_THIN_CAP_REGION"
    assert p["physical_ell2_DtN_D4"] is None
    assert p["physical_execution_allowed"] is False

def test_artifact_count():
    assert len(artifact_payloads())==9

def test_materialization_deterministic(tmp_path:Path):
    a=tmp_path/"a"; b=tmp_path/"b"
    pa=materialize(a); pb=materialize(b)
    assert [x.name for x in pa]==[x.name for x in pb]
    for x,y in zip(pa,pb):
        assert x.read_bytes()==y.read_bytes()
        json.loads(x.read_text())
