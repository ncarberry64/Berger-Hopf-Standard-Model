from pathlib import Path
import json
import numpy as np
import pytest

from bhsm.interface.completion.landau_source_exhaustion_response_sign_v14_76 import (
    VERSION, PRIMARY_VERDICT, EXACT_NEXT_OBJECT,
    eta_F_derivatives, scalar_chain_D2_D3_D4, constant_background_eta_path,
    constant_eta_order_payload, nonconstant_eta_activation_payload,
    gaussian_dtn_amplitude_derivatives, dtn_c4_firewall_payload,
    reflection_parity_payload, quadratic_schur_shift, quartic_response_shift,
    response_sign_payload, singlet_response_shifts, quintet_response_shifts,
    representation_response_payload, area_response_budget_payload,
    source_exhaustion_payload, no_fit_gate_payload, status_payload,
    completion_gate_payload, artifact_payloads, materialize,
)

def test_version():
    assert VERSION=="v14.76"
    assert "EIGHTH_FLUCTUATION_ORDER" in PRIMARY_VERDICT
    assert "BARE_ACTION_OWNED_D4" in EXACT_NEXT_OBJECT

def test_eta_F_derivatives_at_zero():
    assert eta_F_derivatives(0.0,2.0)=={"F1":1.0,"F2":0.0,"F3":0.0,"F4":3.0}

def test_eta_F_derivatives_nonzero():
    d=eta_F_derivatives(2.0,1.0)
    assert d["F1"]==4.5 and d["F2"]==6.0 and d["F3"]==6.0 and d["F4"]==3.0

def test_constant_path_order_count_numerically():
    x=1.7
    for t in (0.01,0.04,0.1):
        total=constant_background_eta_path(t,x,1.0)
        rem=total-0.5*x*t*t
        assert abs(rem-(x**4/8)*t**8)<1e-18

def test_constant_eta_payload():
    p=constant_eta_order_payload()
    assert p["D3_total"]==0 and p["D4_total"]==0 and p["D7_total"]==0
    assert p["p8_first_nonzero_amplitude_order"]==8
    assert p["p8_contributes_to_Landau_u_v_on_constant_branch"] is False

def test_constant_eta_D8_formula():
    x=1.7
    assert abs(constant_eta_order_payload(x)["D8_p8"]-5040*x**4)<1e-10

def test_chain_rule_linear_F_only():
    assert scalar_chain_D2_D3_D4(0,0,2,3,4,1.0)=={"D2":1.0,"D3":1.5,"D4":2.0}

def test_nonconstant_p8_activates():
    p=nonconstant_eta_activation_payload()
    assert p["p8_D2_active"] and p["p8_D3_active"] and p["p8_D4_active"]

def test_gaussian_DtN_amplitude_is_quadratic():
    p=gaussian_dtn_amplitude_derivatives(0.7,2.3)
    assert p["D2"]==2.3 and p["D3"]==0 and p["D4"]==0

def test_DtN_c4_firewall():
    p=dtn_c4_firewall_payload()
    assert p["c4_is_Landau_u_or_v"] is False and p["field_amplitude_D4"]==0

def test_reflection_parity():
    p=reflection_parity_payload()
    assert p["pure_D3_QQQ"]==0 and p["mixed_D3_evenInterior_QQ_allowed"]
    allowed={row["monomial"]:row["allowed"] for row in p["rows"]}
    assert allowed["Q^3"] is False and allowed["y_even Q^2"] is True and allowed["y_odd Q^2"] is False

def test_quadratic_schur_lowers():
    K=np.array([[2.0,0.2],[0.2,1.5]]); b=np.array([0.8,-0.4])
    assert quadratic_schur_shift(1.0,b,K)<1.0

def test_quartic_response_nonpositive():
    K=np.array([[2.0,0.2],[0.2,1.5]]); b=np.array([0.8,-0.4])
    assert quartic_response_shift(b,K)<0

def test_response_requires_positive_K():
    with pytest.raises(ValueError):
        quadratic_schur_shift(1.0,np.array([1.0]),np.array([[-1.0]]))
    with pytest.raises(ValueError):
        quartic_response_shift(np.array([1.0]),np.array([[-1.0]]))

def test_response_sign_payload():
    p=response_sign_payload()
    assert p["quadratic_response_nonpositive"] and p["quartic_response_nonpositive"]
    assert p["quadratic_shift"]<0 and p["quartic_response_shift"]<0

def test_singlet_response():
    p=singlet_response_shifts(2.0,4.0)
    assert p["Delta_u"]==-0.5 and p["Delta_v"]==0 and p["Delta_3u_plus_v"]==-1.5

def test_quintet_response():
    p=quintet_response_shifts(2.0,4.0)
    assert abs(p["Delta_u"]-1/6)<1e-14 and p["Delta_v"]==-0.5
    assert abs(p["Delta_3u_plus_v"])<1e-14

def test_representation_payload():
    p=representation_response_payload()
    assert p["singlet_even_interior"]["landau_shifts"]["Delta_3u_plus_v"]<0
    assert abs(p["traceless_Gram_quintet"]["landau_shifts"]["Delta_3u_plus_v"])<1e-14

def test_area_response_budget():
    p=area_response_budget_payload()
    assert abs(p["normalized_area_three_u_plus_v"]+91/6)<1e-14
    assert abs(p["normalized_area_isotropic_quartic_coefficient_at_s1"]+91/8)<1e-14
    assert p["quartic_response_can_reduce_required_positive_bare_budget"] is False
    assert p["physical_budget_claimed"] is False

def test_source_exhaustion():
    p=source_exhaustion_payload()
    assert p["constant_branch_sources_that_can_supply_positive_bare_D4_now"]==[]
    assert "nonconstant degree-one eta background" in p["eligible_but_unevaluated_positive_bare_D4_classes"]
    assert p["physical_r_u_v_status"]=="OPEN"

def test_no_fit_gate():
    p=no_fit_gate_payload()
    assert p["known_constant_eta_p8_help_at_quartic"] is False
    assert p["known_quadratic_DtN_help_at_field_quartic"] is False
    assert p["stable_response_can_rescue_negative_3u_plus_v"] is False
    assert p["physical_execution_allowed"] is False

def test_status():
    p=status_payload()
    assert len(p["validated"])>=11
    assert p["FULL_BHSM_COMPLETE"] is False and p["MARK_III"]=="NOT_REACHED" and p["USB_touched"] is False

def test_completion_gate():
    p=completion_gate_payload()
    assert p["validation_passed"] is True
    assert p["constant_eta_p8_Landau_quartic"]=="INVALIDATED"
    assert p["quadratic_DtN_c4_as_Landau_quartic"]=="INVALIDATED"
    assert p["stable_response_effect_on_r"]=="CAN_LOWER"
    assert p["stable_response_effect_on_isotropic_3u_plus_v"]=="CANNOT_INCREASE"
    assert p["positive_bare_D4_required"] is True
    assert p["physical_execution_allowed"] is False

def test_artifact_count():
    assert len(artifact_payloads())==11

def test_materialization_deterministic(tmp_path:Path):
    a=tmp_path/"a"; b=tmp_path/"b"
    pa=materialize(a); pb=materialize(b)
    assert [x.name for x in pa]==[x.name for x in pb]
    for x,y in zip(pa,pb):
        assert x.read_bytes()==y.read_bytes()
        json.loads(x.read_text())
