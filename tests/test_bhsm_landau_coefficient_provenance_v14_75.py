from pathlib import Path
from fractions import Fraction
import json
import numpy as np
import pytest

from bhsm.interface.completion.landau_coefficient_provenance_v14_75 import (
    VERSION, PRIMARY_VERDICT, EXACT_NEXT_OBJECT,
    ell2_haar_moments, area_quadratic_coefficient, area_quartic_coefficient,
    normalized_area_landau_coefficients, locking_cone, normalized_area_payload,
    moment_identity_payload, extract_landau_coefficients,
    coefficient_extractor_payload, reduced_quartic_coefficient,
    direct_minimized_quartic_witness, quartic_schur_payload,
    equal_cap_GHY_cancellation_payload, action_provenance_payload,
    no_fit_gate_payload, status_payload, completion_gate_payload,
    artifact_payloads, materialize,
)

def test_version():
    assert VERSION=="v14.75"
    assert "R_EQUALS_5_OVER_3" in PRIMARY_VERDICT
    assert "SECOND_THIRD_AND_FOURTH" in EXACT_NEXT_OBJECT

def test_haar_second_moments():
    m=ell2_haar_moments(3,3)
    assert m["f2"]==1
    assert m["grad2"]==8

def test_haar_rank1_fourth_moments():
    m=ell2_haar_moments(1,1)
    assert m["f4"]==Fraction(1,5)
    assert m["f2_grad2"]==Fraction(8,15)
    assert m["grad4"]==Fraction(128,15)

def test_haar_identity_fourth_moments():
    m=ell2_haar_moments(3,3)
    assert m["f4"]==3
    assert m["f2_grad2"]==8
    assert m["grad4"]==96

def test_area_quadratic():
    assert area_quadratic_coefficient(1)==Fraction(5,6)
    assert area_quadratic_coefficient(2)==Fraction(5,3)

def test_area_quartic_rank1():
    assert area_quartic_coefficient(1,1)==Fraction(-41,40)

def test_area_quartic_rank2():
    assert area_quartic_coefficient(2,2)==Fraction(-289,60)

def test_area_quartic_identity():
    assert area_quartic_coefficient(3,3)==Fraction(-91,8)

def test_area_landau_coefficients():
    c=normalized_area_landau_coefficients()
    assert c["r"]==Fraction(5,3)
    assert c["u"]==Fraction(-83,15)
    assert c["v"]==Fraction(43,30)

def test_area_locking_fails():
    c=normalized_area_landau_coefficients()
    assert locking_cone(float(c["r"]),float(c["u"]),float(c["v"])) is False
    assert 3*c["u"]+c["v"]==Fraction(-91,6)

def test_area_payload_exact_rays():
    p=normalized_area_payload()
    assert p["locking_cone_satisfied"] is False
    assert all(row["quadratic_residual"]==0 for row in p["ray_checks"])
    assert all(row["quartic_residual"]==0 for row in p["ray_checks"])
    assert p["action_ownership"]=="GEOMETRIC_JACOBI_WITNESS_ONLY_NOT_AUTOMATIC_BHSM_SEAM_TENSION"

def test_moment_payload():
    p=moment_identity_payload()
    assert "<f^4>" in p["identities"]
    assert p["physical_prediction"] is False

def test_coefficient_extractor_general():
    r,u,v=1.7,-0.8,2.2
    a2A=r/2
    a2B=r
    a4A=(u+v)/4
    a4B=u+v/2
    x=extract_landau_coefficients(a2A,a2B,a4A,a4B)
    assert abs(x["r"]-r)<1e-14
    assert abs(x["u"]-u)<1e-14
    assert abs(x["v"]-v)<1e-14
    assert x["quadratic_consistency_residual"]<1e-14

def test_coefficient_extractor_area():
    p=coefficient_extractor_payload()
    assert p["max_area_extraction_residual"]<1e-14
    assert p["physical_action_currently_evaluable_on_these_rays"] is False

def test_quartic_response_formula_direct():
    K=np.array([[2.4,0.3],[0.3,1.7]])
    b=np.array([0.8,-0.5])
    T4=7.2
    a4=reduced_quartic_coefficient(T4,b,K)
    for t in (0.01,0.03,0.07):
        exact=direct_minimized_quartic_witness(t,1.3,T4,b,K)
        approx=0.5*1.3*t*t+a4*t**4
        assert abs(exact-approx)<1e-14

def test_quartic_response_negative_correction():
    K=np.diag([2.0,3.0])
    b=np.array([1.0,2.0])
    bare=24.0
    a4=reduced_quartic_coefficient(bare,b,K)
    assert a4 < bare/24

def test_quartic_invalid_hessian():
    with pytest.raises(ValueError):
        reduced_quartic_coefficient(1.0,np.array([1.0]),np.array([[-1.0]]))

def test_quartic_payload():
    p=quartic_schur_payload()
    assert p["direct_substitution_residual"]<1e-14
    assert p["diagnostic_response_correction"]<0
    assert "Hessian data alone" in p["theorem"]

def test_ghy_cancellation():
    p=equal_cap_GHY_cancellation_payload()
    assert "K_+ + K_-" in p["sum"]
    assert p["physical_prediction"] is False

def test_action_provenance_fail_closed():
    p=action_provenance_payload()
    assert p["physical_r_u_v_numeric_status"]=="NOT_DERIVED"
    assert p["area_witness_is_not_an_owned_seam_tension"] is True
    assert len(p["rows"])>=7

def test_no_fit_gate():
    p=no_fit_gate_payload()
    assert p["area_witness"]["passes"] is False
    assert p["physical_BHSM"]["r"] is None
    assert p["physical_execution_allowed"] is False

def test_status():
    p=status_payload()
    assert len(p["validated"])>=10
    assert p["FULL_BHSM_COMPLETE"] is False
    assert p["MARK_III"]=="NOT_REACHED"
    assert p["USB_touched"] is False

def test_completion_gate():
    p=completion_gate_payload()
    assert p["validation_passed"] is True
    assert p["geometric_area_locking_cone"]=="FAIL"
    assert p["physical_r"] is None
    assert p["physical_locking_gate"]=="UNDECIDED"
    assert p["physical_execution_allowed"] is False

def test_artifact_count():
    p=artifact_payloads()
    assert len(p)==9
    assert "BHSM_completion_gate_v14_75.json" in p

def test_materialization_deterministic(tmp_path:Path):
    a=tmp_path/"a"; b=tmp_path/"b"
    pa=materialize(a); pb=materialize(b)
    assert [x.name for x in pa]==[x.name for x in pb]
    for x,y in zip(pa,pb):
        assert x.read_bytes()==y.read_bytes()
        json.loads(x.read_text())
