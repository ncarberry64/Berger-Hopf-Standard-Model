from pathlib import Path
import json, math
import numpy as np
import pytest

from bhsm.interface.completion.driven_hypersphere_black_hole_flux_gate_v14_81 import (
    VERSION, PRIMARY_VERDICT, EXACT_NEXT_OBJECT,
    raychaudhuri_theta_dot, perfect_fluid_Ruu, geodesic_irrotational_theta_dot,
    gr_defocusing_gate_payload, conserved_exchange_residual,
    exchange_power_balance, energy_exchange_payload,
    reflection_allowed_couplings_payload, driven_r_eff,
    alpha_critical_residual, critical_drive_for_alpha_lock, locking_cone,
    parametric_drive_payload, static_forced_equilibrium,
    additive_forcing_hessian, additive_force_firewall_payload,
    monodromy_matrix, floquet_multipliers, floquet_payload,
    black_hole_evidence_payload, research_verdict_payload,
    status_payload, completion_gate_payload, artifact_payloads, materialize,
)

def test_version():
    assert VERSION=="v14.81"
    assert "RAYCHAUDHURI" in PRIMARY_VERDICT
    assert "DERIVE_THE_BLACK_HOLE_TO_BAND_PARAMETRIC_SUSCEPTIBILITY_CHI_B" in EXACT_NEXT_OBJECT

def test_perfect_fluid_Ruu():
    assert abs(perfect_fluid_Ruu(1.0,0.0,1.0,0.0)-4*math.pi)<1e-14
    assert abs(perfect_fluid_Ruu(1.0,-1/3,1.0,0.0))<1e-14

def test_raychaudhuri_positive_energy_focuses():
    x=geodesic_irrotational_theta_dot(0.1,0.0,0.2,0.0,1.0,0.0)
    assert x<0

def test_negative_pressure_can_defocus():
    x=geodesic_irrotational_theta_dot(0.0,0.0,1.0,-1.0,1.0,0.0)
    assert x>0

def test_vorticity_can_counter_focus():
    x=raychaudhuri_theta_dot(0,0,2.0,1.0,0)
    assert x>0

def test_gr_payload():
    p=gr_defocusing_gate_payload()
    assert p["dust_defocuses"] is False
    assert p["radiation_like_defocuses"] is False
    assert p["negative_pressure_can_defocus"] is True
    assert p["black_hole_positive_energy_injection_generically_implies_local_expansion_in_GR"] is False

def test_exchange_conservation():
    q=np.array([1.0,-2.0,3.0])
    assert conserved_exchange_residual(q,-q)<1e-14

def test_exchange_shape_error():
    with pytest.raises(ValueError):
        conserved_exchange_residual(np.ones(2),np.ones(3))

def test_power_balance():
    assert abs(exchange_power_balance(-10,7,2,1))<1e-14

def test_exchange_payload():
    p=energy_exchange_payload()
    assert p["exchange_vector_residual"]<1e-14
    assert abs(p["closed_energy_budget_residual"])<1e-14
    assert p["physical_Q_BH_to_band"] is None

def test_reflection_selection():
    p=reflection_allowed_couplings_payload()
    assert p["couplings"][0]["status"]=="EXPLICIT_REFLECTION_BREAKING_FOR_SCALAR_ACTIVITY"
    assert p["couplings"][1]["status"]=="LEADING_REFLECTION_PRESERVING_PARAMETRIC_COUPLING"
    assert p["symmetry_fixes_sign_of_chi_b"] is False
    assert p["physical_chi_b"] is None

def test_driven_r_eff():
    assert abs(driven_r_eff(2.0,0.5,3.0)-0.5)<1e-14

def test_critical_drive_residual():
    r0,chi,a,u,v=0.2,0.8,0.01,1.0,0.5
    d=critical_drive_for_alpha_lock(r0,chi,a,u,v)
    assert abs(alpha_critical_residual(r0,chi,d,a,u,v))<1e-14

def test_critical_drive_requires_chi():
    with pytest.raises(ValueError):
        critical_drive_for_alpha_lock(1,0,0.01,1,1)

def test_alpha_validation():
    with pytest.raises(ValueError):
        alpha_critical_residual(1,1,1,0,1,1)

def test_locking_cone():
    assert locking_cone(-1,1,1) is True
    assert locking_cone(1,1,1) is False
    assert locking_cone(-1,1,-1) is False

def test_parametric_payload():
    p=parametric_drive_payload()
    assert abs(p["diagnostic"]["residual"])<1e-12
    assert p["chi_sign_derived_from_master_action"] is False
    assert p["physical_critical_drive"] is None

def test_additive_force_hessian_unchanged():
    for J in (-10,-1,0,1,10):
        assert additive_forcing_hessian(2.0)==2.0
        assert abs(static_forced_equilibrium(2.0,J)-J/2)<1e-14

def test_additive_force_singular():
    with pytest.raises(ValueError):
        static_forced_equilibrium(0,1)

def test_additive_payload():
    p=additive_force_firewall_payload()
    assert p["Hessian_independent_of_additive_source"] is True
    assert p["additive_source_can_change_sign_of_r"] is False

def test_monodromy_shape():
    M=monodromy_matrix(1.0,0.1,2.7,0.1,steps_per_period=800)
    assert M.shape==(2,2)
    assert np.all(np.isfinite(M))

def test_floquet_witnesses():
    p=floquet_payload()
    assert p["stable_witness"] is True
    assert p["parametric_instability_witness"] is True
    assert p["static_Hessian_alone_is_final_dynamic_gate"] is False

def test_black_hole_evidence_fail_closed():
    p=black_hole_evidence_payload()
    assert p["bridge_hypothesis_status"]=="OPEN_SIGN_AND_NORMALIZATION"
    assert len(p["not_established_as_standard_GR_fact"])>=4

def test_research_verdict():
    p=research_verdict_payload()
    assert p["black_hole_activity_as_generic_local_expansion_source"]=="NOT_DERIVED_AND_NOT_GENERIC_IN_GR"
    assert p["physical_chi_b"] is None
    assert p["physical_execution_allowed"] is False

def test_status():
    p=status_payload()
    assert len(p["validated"])>=12
    assert p["FULL_BHSM_COMPLETE"] is False
    assert p["MARK_III"]=="NOT_REACHED"
    assert p["PHYSICAL_EXECUTION_BLOCKED"] is True
    assert p["USB_touched"] is False

def test_completion_gate():
    p=completion_gate_payload()
    assert p["validation_passed"] is True
    assert p["dynamic_background_baseline"]=="ACTIVE_REFERENCE_ROUND_ONLY"
    assert p["black_hole_generic_GR_deenveloping"]=="NOT_DERIVED"
    assert p["physical_chi_b"] is None
    assert p["physical_execution_allowed"] is False

def test_artifact_count():
    assert len(artifact_payloads())==10
    assert "BHSM_completion_gate_v14_81.json" in artifact_payloads()

def test_materialization_deterministic(tmp_path:Path):
    a=tmp_path/"a"; b=tmp_path/"b"
    pa=materialize(a); pb=materialize(b)
    assert [x.name for x in pa]==[x.name for x in pb]
    for x,y in zip(pa,pb):
        assert x.read_bytes()==y.read_bytes()
        json.loads(x.read_text())
