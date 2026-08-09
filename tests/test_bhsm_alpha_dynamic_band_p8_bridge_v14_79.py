from pathlib import Path
import json
import numpy as np
import pytest

from bhsm.interface.completion.alpha_dynamic_band_p8_bridge_v14_79 import (
    VERSION, PRIMARY_VERDICT, EXACT_NEXT_OBJECT,
    require_alpha, alpha_scaled_landau, locking_cone,
    alpha_scaling_preserves_locking_cone, isotropic_alpha_lock_residual,
    rank_one_alpha_lock_residual, alpha_commuting_dtn_landau,
    alpha_contract_payload, goldstone_lift_hamiltonian,
    goldstone_energy_spectrum, goldstone_lift_payload,
    normalized_fiber_moment8, fiber_moment8_lower_bound,
    constant_modulus_p8_bridge_moment, effective_p8_coefficient_from_profile,
    reflected_p8_mean_energy, bridge_p8_payload, p8_bridge_proof_ledger_payload,
    alpha_band_quadratic_schur, dynamic_band_coefficients,
    band_profile_coefficients, dynamic_band_payload,
    family_generation_gate_payload, safety_lock_payload, status_payload,
    completion_gate_payload, artifact_payloads, materialize,
)

def test_version():
    assert VERSION=="v14.79"
    assert "ALPHA" in PRIMARY_VERDICT
    assert "RETIRE_THE_P8_BRIDGE" in EXACT_NEXT_OBJECT

@pytest.mark.parametrize("bad",[0.0,-0.1,1.0,2.0])
def test_alpha_validation(bad):
    with pytest.raises(ValueError):
        require_alpha(bad)

def test_alpha_landau_scaling():
    a=0.01
    p=alpha_scaled_landau(-2,3,4,a)
    assert p["r_hat"]==-2*a*a
    assert p["u_hat"]==3*a**4
    assert p["v_hat"]==4*a**4
    assert p["three_u_plus_v_hat"]==13*a**4

def test_alpha_preserves_cone_true_case():
    assert locking_cone(-1,1,1) is True
    assert alpha_scaling_preserves_locking_cone(-1,1,1,0.01) is True

def test_alpha_preserves_cone_false_case():
    assert locking_cone(-1,1,-0.2) is False
    assert alpha_scaling_preserves_locking_cone(-1,1,-0.2,0.01) is True

def test_alpha_isotropic_lock_relation():
    a=0.02
    u,v=2.0,1.0
    r=-a*a*(3*u+v)
    assert abs(isotropic_alpha_lock_residual(r,u,v,a))<1e-15

def test_alpha_rank_one_lock_relation():
    a=0.03
    u,v=1.2,0.8
    r=-a*a*(u+v)
    assert abs(rank_one_alpha_lock_residual(r,u,v,a))<1e-15

def test_commuting_no_go_survives_alpha():
    p=alpha_commuting_dtn_landau(-1,0.5,0.01)
    assert abs(p["v_hat_plus_u_hat_over_2"])<1e-18
    assert p["locking_cone_Q"] is False
    assert p["locking_cone_Qhat"] is False

def test_alpha_contract():
    p=alpha_contract_payload()
    assert p["no_independent_ripple_epsilon"] is True
    assert p["no_independent_Goldstone_lift_epsilon"] is True
    assert p["v14_78_commuting_relation_survives"] is True

def test_goldstone_hamiltonian_linear_alpha():
    G=np.diag([-1.0,0.0,2.0])
    H1=goldstone_lift_hamiltonian(0.01,3.0,G)
    H2=goldstone_lift_hamiltonian(0.02,3.0,G)
    assert np.linalg.norm(H2-2*H1)<1e-14

def test_goldstone_spectrum_linear():
    G=np.array([[1,0.2],[0.2,-1]],dtype=float)
    s1=goldstone_energy_spectrum(0.01,2.0,G)
    s2=goldstone_energy_spectrum(0.02,2.0,G)
    assert abs(s2["max_abs_splitting"]/s1["max_abs_splitting"]-2)<1e-12

def test_goldstone_payload_blocked():
    p=goldstone_lift_payload()
    assert p["linear_alpha_energy_splitting_verified"] is True
    assert p["physical_Goldstone_gap"] is None
    assert p["physical_execution_allowed"] is False

def test_constant_profile_saturates_m8_bound():
    p=normalized_fiber_moment8(np.ones(4),np.ones(4))
    assert abs(p["L2_norm"]-1)<1e-14
    assert abs(p["M8"]-p["lower_bound"])<1e-14

def test_localized_profile_strictly_above_bound():
    p=normalized_fiber_moment8(np.array([1,0,0,0],dtype=float),np.ones(4))
    assert p["M8"]>p["lower_bound"]

def test_m8_bound_formula():
    assert fiber_moment8_lower_bound(4.0)==1/64
    assert constant_modulus_p8_bridge_moment(4.0)==1/64

def test_invalid_m8_inputs():
    with pytest.raises(ValueError):
        fiber_moment8_lower_bound(0)
    with pytest.raises(ValueError):
        effective_p8_coefficient_from_profile(0)
    with pytest.raises(ValueError):
        normalized_fiber_moment8(np.zeros(2),np.ones(2))

def test_effective_p8_coefficient():
    assert effective_p8_coefficient_from_profile(0.8)==0.1

def test_reflected_p8_exact_expansion():
    p=reflected_p8_mean_energy(0.01,1.0,0.5,0.2,1.0)
    assert p["reconstruction_residual"]<1e-15
    assert p["alpha2_coefficient"]>0
    assert p["alpha4_coefficient"]>0

def test_reflected_p8_rejects_negative_X_path():
    with pytest.raises(ValueError):
        reflected_p8_mean_energy(0.5,0.1,1.0,0.2,1.0)

def test_bridge_payload():
    p=bridge_p8_payload()
    assert p["localized_has_stronger_p8_reduction"] is True
    assert p["positive_alpha4_bridge_term"] is True
    assert p["physical_p8_Landau_coefficients"] is None

def test_bridge_ledger_fail_closed():
    p=p8_bridge_proof_ledger_payload()
    assert p["bridge_active"] is True
    assert p["bridge_retired"] is False
    assert p["bridge_may_emit_physical_predictions"] is False
    assert any(row["status"]=="OPEN" for row in p["rows"])

def test_alpha_band_schur():
    a=0.01
    K=np.diag([2.0,3.0])
    c=np.array([1.0,2.0])
    p=alpha_band_quadratic_schur(a,0.1,c,K)
    expected=0.1-a*a*(1/2+4/3)
    assert abs(p["r_eff"]-expected)<1e-14
    assert p["alpha2_shift"]<0

def test_alpha_band_schur_rejects_unstable_neighbor():
    with pytest.raises(ValueError):
        alpha_band_quadratic_schur(0.01,0.1,np.array([1.0]),np.array([[-1.0]]))

def test_dynamic_band_coefficients():
    p=dynamic_band_coefficients(0.01,0.001,1.0,1.0,np.array([1.0]),np.array([[2.0]]))
    assert "r_eff" in p
    assert "u_eff" in p
    assert "isotropic_alpha_lock_residual" in p

def test_profile_band_coefficients_vary():
    rows=band_profile_coefficients([
        {"band":"a","amplitudes":[1,1,1,1],"weights":[1,1,1,1]},
        {"band":"b","amplitudes":[1,0,0,0],"weights":[1,1,1,1]},
    ])
    assert rows[1]["p8_effective_coefficient"]>rows[0]["p8_effective_coefficient"]

def test_dynamic_band_payload():
    p=dynamic_band_payload()
    assert p["static_universal_r_u_v"] is False
    assert p["same_parent_p8_coefficient_can_yield_band_dependent_effective_strength"] is True
    assert p["physical_family_count"] is None

def test_family_gate_no_hardcoded_three():
    p=family_generation_gate_payload()
    assert p["number_three_inserted_by_hand"] is False
    assert p["physical_family_count"] is None

def test_safety_lock():
    p=safety_lock_payload()
    assert p["PHYSICAL_EXECUTION_BLOCKED"] is True
    assert p["physical_masses_emitted"] is False
    assert p["PMNS_emitted"] is False

def test_status_fail_closed():
    p=status_payload()
    assert len(p["validated"])>=12
    assert p["FULL_BHSM_COMPLETE"] is False
    assert p["MARK_III"]=="NOT_REACHED"
    assert p["PHYSICAL_EXECUTION_BLOCKED"] is True
    assert p["USB_touched"] is False

def test_completion_gate():
    p=completion_gate_payload()
    assert p["validation_passed"] is True
    assert p["p8_bridge_retired"] is False
    assert p["physical_family_count"] is None
    assert p["physical_Goldstone_gap"] is None
    assert p["physical_r_u_v"] is None
    assert p["physical_execution_allowed"] is False

def test_artifact_count():
    assert len(artifact_payloads())==9
    assert "BHSM_completion_gate_v14_79.json" in artifact_payloads()

def test_materialization_deterministic(tmp_path:Path):
    a=tmp_path/"a"; b=tmp_path/"b"
    pa=materialize(a); pb=materialize(b)
    assert [x.name for x in pa]==[x.name for x in pb]
    for x,y in zip(pa,pb):
        assert x.read_bytes()==y.read_bytes()
        json.loads(x.read_text())
