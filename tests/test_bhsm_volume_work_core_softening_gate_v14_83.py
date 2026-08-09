from pathlib import Path
import json, math
import pytest
from bhsm.interface.completion.volume_work_core_softening_gate_v14_83 import *

def test_version():
    assert VERSION=="v14.83"
    assert "ZETA" in PRIMARY_VERDICT

def test_stationary_radius():
    assert abs(stationary_radius(1,5)-1)<1e-14
    assert abs(core_potential_prime(1,1,5))<1e-14

def test_stiffness_positive():
    assert core_stiffness(1,1,5,.5,.5)>0

def test_zeta():
    assert abs(kinetic_p2_share(1,.3,.7)-.3)<1e-14

def test_closed_log_derivative():
    cases=[(1.2,4.5,.7,.8),(.8,7,1.2,.3),(2,3,.2,1.5)]
    for c in cases:
        assert abs(stationary_stiffness_log_derivative(*c)-stationary_log_derivative_closed(*c))<1e-10

def test_drive_radius_sign():
    R=stationary_radius(1,5)
    assert driven_radius_derivative(1,5,volume_work_B_prime(R,7))>0

def test_threshold_stiffen():
    chi=core_drive_susceptibility(1,5,.2,.8,7)
    assert chi<0

def test_threshold_neutral():
    chi=core_drive_susceptibility(1,5,1/3,2/3,7)
    assert abs(chi)<1e-14

def test_threshold_soften():
    chi=core_drive_susceptibility(1,5,.6,.4,7)
    assert chi>0

def test_seven_volume_closed():
    assert abs(seven_volume_susceptibility(1,5,.6,.4)-core_drive_susceptibility(1,5,.6,.4,7))<1e-14

def test_fd_chi():
    cases=[(1.2,4.5,.7,.8),(.8,7,1.2,.3),(2,3,.2,1.5)]
    for a,b,d,e in cases:
        R=stationary_radius(a,b); Bp=volume_work_B_prime(R,7)
        x=core_drive_susceptibility(a,b,d,e,Bp)
        y=core_drive_susceptibility_direct_fd(a,b,d,e,Bp)
        assert abs(x-y)<1e-7

def test_attachment_partials_positive():
    for h,k in ((.18,1),(.5,.8),(2,.3),(1,1)):
        assert attachment_partial_h(h,k)>0 and attachment_partial_k(h,k)>0

def test_attachment_sign_inherits():
    h=.181391690148362; k=1
    for chi_h in (-2,3):
        chi_mu=attachment_chi_from_core(h,k,chi_h,0)
        assert chi_mu*chi_h>0

def test_sign_payload():
    p=sign_theorem_payload()
    cls=[r["classification"] for r in p["rows"]]
    assert cls==["STIFFEN","NEUTRAL","SOFTEN"]
    assert p["physical_zeta"] is None

def test_verification_payload():
    p=formula_verification_payload()
    assert p["max_log_derivative_residual"]<1e-10
    assert p["max_chi_residual"]<1e-7

def test_stress_work_firewall():
    p=stress_work_payload()
    assert p["raw_positive_energy_density_is_equivalent_to_outward_D"] is False
    assert p["bridge_status"].startswith("PROVISIONAL")

def test_archived_provenance_missing_partition():
    p=archived_core_provenance_payload()
    assert p["missing_for_sign"]["zeta"] is None
    assert p["sign_can_be_inferred_from_archived_total_M_only"] is False

def test_bridge_fail_closed():
    p=bridge_and_prove_payload()
    assert p["physical_driver_derived"] is False
    assert p["bridge_may_emit_predictions"] is False

def test_status():
    p=status_payload()
    assert p["PHYSICAL_EXECUTION_BLOCKED"] is True
    assert p["FULL_BHSM_COMPLETE"] is False

def test_completion():
    p=completion_payload()
    assert p["validation_passed"] is True
    assert p["physical_zeta"] is None
    assert p["physical_execution_allowed"] is False

def test_artifact_count():
    assert len(artifact_payloads())==8

def test_deterministic(tmp_path:Path):
    a=materialize(tmp_path/"a"); b=materialize(tmp_path/"b")
    for x,y in zip(a,b):
        assert x.read_bytes()==y.read_bytes()
        json.loads(x.read_text())
