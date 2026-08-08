"""BHSM v14.76 Landau source exhaustion and response-sign theorem.

v14.75 showed that the exact round-equator area witness has
r_area=5/3, u_area=-83/15, v_area=43/30, so it fails the v14.74 locking cone,
while physical BHSM coefficients remain unavailable because the complete
global D2/D3/D4 shape response has not been evaluated.

This sprint narrows the allowed physical sources.

For the retained eta density F(X)=kappa1 X/2+X^4/8, X=|D eta|^2, the v14.30
constant background D eta_0=0 has X(t)=x2 t^2 for a linear tangent
perturbation. Therefore F=kappa1 x2 t^2/2+x2^4 t^8/8: the p8 term has no
D3-D7 amplitude contribution and cannot supply Landau u or v on that branch.

On a nonconstant degree-one background X0!=0, exact chain derivatives activate
the p8 term already in D2,D3,D4, so the missing full-preimage background is
genuinely upstream.

The v14.30 DtN theorem is quadratic:
S_DtN=1/2 <phi,N(H)phi>. Its low-energy coefficient called c4 multiplies z^2
inside a quadratic differential operator; it is not a Q^4 Landau coefficient.

Reflection sends Q->-Q, so pure D3_QQQ vanishes. Mixed y_even Q^2 cubic
response remains allowed.

After quadratic Schur reduction,
a4_eff(q)=a4_bare(q)-B(q,q)^T K^-1 B(q,q)/8. For positive physical K the
response shift is nonpositive on every ray. Along Q=sI,
a4=3(3u+v)s^4/4, so stable eliminated-field response can never increase
3u+v. Quadratic Schur response can lower r, but quartic stabilization requires
a separate positive bare D4 contribution.

No physical coefficients are assigned and no measured input is used.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

VERSION = "v14.76"

PRIMARY_VERDICT = (
    "BHSM_V14_76_SOURCE_EXHAUSTION_SHOWS_THAT_ON_THE_V14_30_CONSTANT_ETA_"
    "BACKGROUND_THE_RETAINED_P8_TERM_STARTS_AT_EIGHTH_FLUCTUATION_ORDER_AND_"
    "THEREFORE_CANNOT_SUPPLY_THE_ELL2_LANDAU_U_OR_V_WHILE_THE_QUADRATIC_DTN_"
    "C4_IS_A_FOUR_DERIVATIVE_QUADRATIC_COEFFICIENT_NOT_A_FIELD_QUARTIC;_"
    "REFLECTION_KILLS_PURE_Q_CUBICS_BUT_ALLOWS_EVEN_INTERIOR_Y_Q_SQUARED_"
    "RESPONSE_AND_FOR_POSITIVE_ELIMINATED_HESSIAN_EVERY_SUCH_CUBIC_RESPONSE_"
    "LOWERS_THE_QUARTIC_ACTION_ON_EACH_RAY_SO_IT_CAN_NEVER_RAISE_THREE_U_PLUS_"
    "V;_QUADRATIC_SCHUR_RESPONSE_CAN_LOWER_R_BUT_STABLE_LOCKING_REQUIRES_A_"
    "SEPARATE_POSITIVE_BARE_D4_SOURCE_FROM_THE_FULL_GRAVITY_NONLOCAL_M4_OR_"
    "NONCONSTANT_DEGREE_ONE_ETA_BACKGROUND;_PHYSICAL_R_U_V_REMAIN_OPEN"
)

EXACT_NEXT_OBJECT = (
    "EVALUATE_THE_BARE_ACTION_OWNED_D4_SHAPE_TENSORS_ON_THE_TWO_INVARIANT_"
    "ELL2_RAYS_FOR_M8_AND_M5_GEOMETRY_M4_LOCALIZED_AND_NONLOCAL_SPECTRAL_"
    "SECTORS_ON_THE_FULL_PREIMAGE_STATIONARY_BACKGROUND_WHILE_COMPUTING_THE_"
    "EVEN_INTERIOR_D3_QQ_RESPONSE_AND_QUADRATIC_SCHUR_SHIFT_OF_R;_IF_THE_"
    "DEGREE_ONE_ETA_BACKGROUND_HAS_X0_NONZERO_INCLUDE_ITS_CHAIN_RULE_D2_D3_D4_"
    "CONTRIBUTIONS;_THEN_ASSEMBLE_PHYSICAL_R_U_V_AND_APPLY_THE_NO_FIT_LOCKING_"
    "CONE_BEFORE_CALDERON_OR_NEUTRINO_EXECUTION"
)


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("utf-8")


def sha256_payload(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def eta_F_derivatives(X: float, kappa1: float = 1.0) -> dict[str, float]:
    X = float(X)
    k = float(kappa1)
    return {"F1": 0.5*k+0.5*X**3, "F2": 1.5*X**2, "F3": 3.0*X, "F4": 3.0}


def scalar_chain_D2_D3_D4(X0: float, x1: float, x2: float, x3: float, x4: float, kappa1: float = 1.0) -> dict[str, float]:
    d = eta_F_derivatives(X0, kappa1)
    return {
        "D2": d["F1"]*x2 + d["F2"]*x1**2,
        "D3": d["F1"]*x3 + 3.0*d["F2"]*x1*x2 + d["F3"]*x1**3,
        "D4": (
            d["F1"]*x4 + 4.0*d["F2"]*x1*x3 + 3.0*d["F2"]*x2**2
            + 6.0*d["F3"]*x1**2*x2 + d["F4"]*x1**4
        ),
    }


def constant_background_eta_path(t: float, x2_coeff: float, kappa1: float = 1.0) -> float:
    X = float(x2_coeff)*float(t)**2
    return 0.5*float(kappa1)*X + 0.125*X**4


def constant_eta_order_payload(x2_coeff: float = 1.7, kappa1: float = 1.0) -> dict[str, Any]:
    x=float(x2_coeff); k=float(kappa1)
    return {
        "version": VERSION,
        "density_core": "F(X)=kappa1 X/2+X^4/8",
        "constant_background": "D eta_0=0, hence X0=0",
        "linear_tangent_path": "X(t)=x2 t^2",
        "path_expansion": "F=kappa1 x2 t^2/2+x2^4 t^8/8",
        "D2_total": k*x,
        "D3_total": 0.0, "D4_total": 0.0, "D5_total": 0.0,
        "D6_total": 0.0, "D7_total": 0.0,
        "D8_p8": 5040.0*x**4,
        "p8_first_nonzero_amplitude_order": 8,
        "p8_contributes_to_Landau_u_v_on_constant_branch": False,
        "overall_action_sign_and_weight_do_not_change_order_count": True,
        "physical_prediction": False,
    }


def nonconstant_eta_activation_payload() -> dict[str, Any]:
    X0=0.8; x1,x2,x3,x4=0.6,-0.2,0.3,-0.4
    total=scalar_chain_D2_D3_D4(X0,x1,x2,x3,x4,1.0)
    p2={"D2":0.5*x2,"D3":0.5*x3,"D4":0.5*x4}
    p8={key:total[key]-p2[key] for key in total}
    return {
        "version": VERSION,
        "chain_rule": {
            "D2": "F1*x2+F2*x1^2",
            "D3": "F1*x3+3F2*x1*x2+F3*x1^3",
            "D4": "F1*x4+4F2*x1*x3+3F2*x2^2+6F3*x1^2*x2+F4*x1^4",
        },
        "synthetic_X0": X0,
        "synthetic_path_derivatives": {"x1":x1,"x2":x2,"x3":x3,"x4":x4},
        "p8_contributions": p8,
        "p8_D2_active": abs(p8["D2"])>1e-12,
        "p8_D3_active": abs(p8["D3"])>1e-12,
        "p8_D4_active": abs(p8["D4"])>1e-12,
        "meaning": "actual degree-one X0!=0 background can activate p8 at low orders",
        "synthetic_values_are_physical": False,
    }


def gaussian_dtn_amplitude_derivatives(amplitude: float, eigenvalue: float) -> dict[str, float]:
    a=float(amplitude); N=float(eigenvalue)
    return {"S":0.5*N*a*a,"D1":N*a,"D2":N,"D3":0.0,"D4":0.0}


def dtn_c4_firewall_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "v14_30_operator_expansion": "N(z)=mass_term+Z z+c4 z^2+O(z^3), z=-D_A^2",
        "stored_reference_c4": -0.10901441699630973,
        "meaning_of_c4": "four-derivative coefficient inside a quadratic boundary operator",
        "boundary_action": "S_DtN=1/2 <phi,N phi>",
        "field_amplitude_D3": 0.0,
        "field_amplitude_D4": 0.0,
        "c4_is_Landau_u_or_v": False,
        "nonlinear_geometry_or_background_dependence_can_generate_higher_shape_variations": True,
        "fixed_operator_quadratic_proxy_can_generate_field_quartic": False,
    }


def reflection_parity_payload() -> dict[str, Any]:
    rows=[
        {"monomial":"Q","parity":-1,"allowed":False},
        {"monomial":"Q^2","parity":1,"allowed":True},
        {"monomial":"Q^3","parity":-1,"allowed":False},
        {"monomial":"Q^4","parity":1,"allowed":True},
        {"monomial":"y_even Q^2","parity":1,"allowed":True},
        {"monomial":"y_odd Q^2","parity":-1,"allowed":False},
        {"monomial":"y_odd Q","parity":1,"allowed":True},
        {"monomial":"y_even Q","parity":-1,"allowed":False},
    ]
    return {
        "version":VERSION,
        "symmetry":"equal-cap reflection Q->-Q",
        "rows":rows,
        "pure_D3_QQQ":0.0,
        "mixed_D3_evenInterior_QQ_allowed":True,
        "interpretation":"effective Q potential is even, but even-interior y Q^2 cubic response is allowed",
    }


def quadratic_schur_shift(Hbb: float, coupling: np.ndarray, K: np.ndarray) -> float:
    b=np.asarray(coupling,dtype=float); k=np.asarray(K,dtype=float)
    if k.ndim!=2 or k.shape[0]!=k.shape[1] or b.shape!=(k.shape[0],):
        raise ValueError("incompatible quadratic response")
    if np.min(np.linalg.eigvalsh((k+k.T)/2.0))<=0:
        raise ValueError("K must be positive definite")
    return float(Hbb-b@np.linalg.solve(k,b))


def quartic_response_shift(Bqq: np.ndarray, K: np.ndarray) -> float:
    b=np.asarray(Bqq,dtype=float); k=np.asarray(K,dtype=float)
    if k.ndim!=2 or k.shape[0]!=k.shape[1] or b.shape!=(k.shape[0],):
        raise ValueError("incompatible quartic response")
    if np.min(np.linalg.eigvalsh((k+k.T)/2.0))<=0:
        raise ValueError("K must be positive definite")
    return float(-0.125*b@np.linalg.solve(k,b))


def response_sign_payload() -> dict[str, Any]:
    K=np.array([[2.0,0.3],[0.3,1.4]])
    b2=np.array([0.9,-0.5]); b4=np.array([0.7,0.4]); Hbb=1.2
    heff=quadratic_schur_shift(Hbb,b2,K); dq4=quartic_response_shift(b4,K)
    return {
        "version":VERSION,
        "positive_interior_Hessian_eigenvalues":[float(x) for x in np.linalg.eigvalsh(K)],
        "quadratic_bare":Hbb,
        "quadratic_effective":heff,
        "quadratic_shift":heff-Hbb,
        "quartic_response_shift":dq4,
        "quadratic_response_nonpositive":heff-Hbb<=0.0,
        "quartic_response_nonpositive":dq4<=0.0,
        "isotropic_ray_relation":"a4(Q=sI)=3(3u+v)s^4/4",
        "theorem":"positive-complement cubic response cannot increase 3u+v",
        "consequence":"negative bare isotropic quartic cannot be rescued by stable interior response",
        "diagnostic_numbers_are_physical":False,
    }


def singlet_response_shifts(g: float, k: float) -> dict[str, float]:
    if k<=0: raise ValueError("k must be positive")
    alpha=g*g/k
    return {"Delta_u":-0.5*alpha,"Delta_v":0.0,"Delta_3u_plus_v":-1.5*alpha}


def quintet_response_shifts(g: float, k: float) -> dict[str, float]:
    if k<=0: raise ValueError("k must be positive")
    alpha=g*g/k
    return {"Delta_u":alpha/6.0,"Delta_v":-alpha/2.0,"Delta_3u_plus_v":0.0}


def representation_response_payload() -> dict[str, Any]:
    sing=singlet_response_shifts(1.3,2.1); quin=quintet_response_shifts(0.8,1.7)
    return {
        "version":VERSION,
        "singlet_even_interior":{
            "coupling":"B_s(Q,Q)=g_s I2",
            "correction":"-g_s^2 I2^2/(8 k_s)",
            "landau_shifts":sing,
            "effect":"decreases u, leaves v fixed, worsens 3u+v",
        },
        "traceless_Gram_quintet":{
            "coupling":"B_5=g_5(Q^TQ-I2 I/3)",
            "norm_square":"I4-I2^2/3",
            "correction":"-g_5^2(I4-I2^2/3)/(8 k_5)",
            "landau_shifts":quin,
            "effect":"raises u, lowers v, leaves 3u+v exactly unchanged",
        },
        "general_response_sign":"every positive-K channel gives a nonpositive quartic correction on each ray",
        "physical_couplings_derived":False,
    }


def area_response_budget_payload() -> dict[str, Any]:
    u=-83.0/15.0; v=43.0/30.0; combo=3*u+v; a4iso=3*combo/4
    return {
        "version":VERSION,
        "normalized_area_three_u_plus_v":combo,
        "normalized_area_isotropic_quartic_coefficient_at_s1":a4iso,
        "required_other_bare_D4_before_response":"more than +91/8 on normalized Q=I ray if a unit positive area-like term were actually owned",
        "quartic_response_can_reduce_required_positive_bare_budget":False,
        "quartic_response_only_increases_required_positive_bare_budget":True,
        "area_term_is_action_owned_with_unit_coefficient":False,
        "physical_budget_claimed":False,
    }


def source_exhaustion_payload() -> dict[str, Any]:
    rows=[
        {"source":"round normal-graph area/Jacobi witness","D2":"exact","D3":"zero by reflection","D4":"exact","locking_effect":"r>0 and 3u+v<0; fails","physical_ownership":"not an independent retained seam-tension term"},
        {"source":"eta p2 on v14.30 constant background","D2":"nonzero quadratic Hessian","D3":"zero in linear tangent amplitude","D4":"zero in linear tangent amplitude","locking_effect":"quadratic eta response only","physical_ownership":"retained parent eta term; eta-to-shape map open"},
        {"source":"eta p8 on v14.30 constant background","D2":"zero","D3":"zero","D4":"zero; first amplitude order 8","locking_effect":"cannot provide u or v","physical_ownership":"retained parent term"},
        {"source":"eta p8 on degree-one nonconstant background X0!=0","D2":"generically active","D3":"generically active","D4":"generically active","locking_effect":"eligible physical source","physical_ownership":"background/full-preimage reduction absent"},
        {"source":"quadratic constant-mode DtN","D2":"exact nonlocal quadratic response","D3":"zero at fixed operator/background","D4":"zero in field amplitude; derivative c4 is not Landau quartic","locking_effect":"can shift quadratic spectrum, not u/v at fixed proxy","physical_ownership":"exact conditional quadratic theorem"},
        {"source":"equal-cap GHY","D2":"pair cancels on ideal smooth reflection branch","D3":"pair cancels under same hypotheses","D4":"pair cancels under same hypotheses","locking_effect":"not independent seam tension","physical_ownership":"variational completion"},
        {"source":"stable eliminated interior response","D2":"negative-semidefinite Schur shift","D3":"mixed y_even Q^2 allowed","D4":"induced correction nonpositive on each ray","locking_effect":"can lower r; cannot raise isotropic 3u+v","physical_ownership":"requires actual D3 and physical K"},
        {"source":"M8/M5 nonlinear gravity and scalar geometry","D2":"partial theorem components exist","D3":"not evaluated","D4":"not evaluated","locking_effect":"eligible positive bare D4 source","physical_ownership":"yes; coefficients/background incomplete"},
        {"source":"M4 localized background response","D2":"not evaluated","D3":"not evaluated","D4":"not evaluated","locking_effect":"eligible","physical_ownership":"intrinsic M4 action"},
        {"source":"nonlocal relative heat/zeta determinant","D2":"round diagnostic pieces exist","D3":"background dependent","D4":"physical derivative not evaluated","locking_effect":"eligible bare/effective D4 source","physical_ownership":"conditional microscopic/nonlocal branch"},
    ]
    return {
        "version":VERSION,
        "rows":rows,
        "constant_branch_sources_that_can_supply_positive_bare_D4_now":[],
        "eligible_but_unevaluated_positive_bare_D4_classes":[
            "M8/M5 nonlinear geometry",
            "nonconstant degree-one eta background",
            "M4 localized background response",
            "nonlocal spectral determinant",
        ],
        "physical_r_u_v_status":"OPEN",
        "phase_decision_status":"UNDECIDED",
    }


def no_fit_gate_payload() -> dict[str, Any]:
    return {
        "version":VERSION,
        "required_phase_conditions":["r<0","v>0","3u+v>0"],
        "physical_r":None,"physical_u":None,"physical_v":None,
        "known_constant_eta_p8_help_at_quartic":False,
        "known_quadratic_DtN_help_at_field_quartic":False,
        "stable_response_can_rescue_negative_3u_plus_v":False,
        "positive_bare_D4_source_still_required":True,
        "physical_execution_allowed":False,
        "measured_data_used":False,
    }


def status_payload() -> dict[str, Any]:
    return {
        "version":VERSION,
        "validated":[
            "eta p8 begins at eighth fluctuation order on the v14.30 constant background",
            "eta p8 supplies no D3 or D4 Landau coefficient on that branch",
            "nonconstant X0 activates p8 in D2/D3/D4 through exact chain rules",
            "v14.30 DtN c4 is derivative-expansion data of a quadratic operator, not a field quartic",
            "reflection forces pure Q cubic to vanish",
            "even-interior y Q^2 cubic response remains allowed",
            "positive-complement quadratic Schur response can lower r",
            "positive-complement cubic response gives nonpositive quartic shift on every ray",
            "such response cannot increase isotropic 3u+v",
            "singlet response worsens 3u+v while traceless-Gram quintet response leaves it unchanged",
            "a separate positive bare D4 source is necessary if the locked phase is to be stabilized",
        ],
        "invalidated":[
            "constant-branch eta p8 as the missing quartic stabilizer",
            "v14.30 DtN c4 as Landau u or v",
            "stable interior response as a mechanism for repairing negative isotropic quartic",
            "D2 information alone as sufficient for phase closure",
        ],
        "reclassified":[
            "quadratic response remains a plausible mechanism for driving r through zero",
            "quartic stabilization must come from bare D4 action sectors before negative response corrections",
            "degree-one eta background changes p8 fluctuation order",
            "next computation should prioritize bare D4 ray evaluations and even-interior D3 response",
        ],
        "open":[
            EXACT_NEXT_OBJECT,
            "physical stationary full-preimage background",
            "physical r after quadratic Schur reduction",
            "bare D4 on invariant rays A and B by sector",
            "even-interior D3_QQ response tensors",
            "physical u and v",
            "locked nonround branch if cone passes",
            "three physical Calderon derivatives",
            "Goldstone lifting",
            "relative heat supertrace",
            "frozen neutrino execution",
        ],
        "FULL_BHSM_COMPLETE":False,
        "MARK_III":"NOT_REACHED",
        "physical_prediction_emitted":False,
        "frozen_predictions_changed":False,
        "official_prediction_logic_changed":False,
        "USB_touched":False,
    }


def completion_gate_payload() -> dict[str, Any]:
    eta0=constant_eta_order_payload(); etan=nonconstant_eta_activation_payload()
    dtn=dtn_c4_firewall_payload(); parity=reflection_parity_payload()
    sign=response_sign_payload(); reps=representation_response_payload()
    src=source_exhaustion_payload()
    validation={
        "constant_eta_p8_starts_at_order8":eta0["p8_first_nonzero_amplitude_order"]==8,
        "constant_eta_p8_no_D4":eta0["D4_total"]==0.0,
        "nonconstant_eta_p8_activates_D4":etan["p8_D4_active"],
        "DtN_c4_firewall":dtn["c4_is_Landau_u_or_v"] is False,
        "pure_Q_cubic_killed":parity["pure_D3_QQQ"]==0.0,
        "even_interior_cubic_allowed":parity["mixed_D3_evenInterior_QQ_allowed"],
        "quadratic_response_can_lower":sign["quadratic_shift"]<0.0,
        "quartic_response_nonpositive":sign["quartic_response_shift"]<0.0,
        "singlet_worsens_combo":reps["singlet_even_interior"]["landau_shifts"]["Delta_3u_plus_v"]<0.0,
        "quintet_preserves_combo":abs(reps["traceless_Gram_quintet"]["landau_shifts"]["Delta_3u_plus_v"])<1e-14,
        "no_known_constant_positive_D4_source_claimed":src["constant_branch_sources_that_can_supply_positive_bare_D4_now"]==[],
        "no_physical_prediction":True,
    }
    return {
        "version":VERSION,
        "primary_verdict":PRIMARY_VERDICT,
        "exact_next_object":EXACT_NEXT_OBJECT,
        "constant_eta_p8_Landau_quartic":"INVALIDATED",
        "quadratic_DtN_c4_as_Landau_quartic":"INVALIDATED",
        "stable_response_effect_on_r":"CAN_LOWER",
        "stable_response_effect_on_isotropic_3u_plus_v":"CANNOT_INCREASE",
        "positive_bare_D4_required":True,
        "physical_r":None,"physical_u":None,"physical_v":None,
        "physical_locking_gate":"UNDECIDED",
        "full_BHSM_complete":False,
        "mark_III":"NOT_REACHED",
        "physical_execution_allowed":False,
        "physical_prediction_emitted":False,
        "frozen_predictions_changed":False,
        "official_prediction_logic_changed":False,
        "usb_touched":False,
        "validation":validation,
        "validation_passed":all(validation.values()),
    }


def artifact_payloads() -> dict[str, Any]:
    return {
        "BHSM_constant_eta_p8_order_count_v14_76.json":constant_eta_order_payload(),
        "BHSM_nonconstant_eta_p8_activation_v14_76.json":nonconstant_eta_activation_payload(),
        "BHSM_DtN_c4_field_quartic_firewall_v14_76.json":dtn_c4_firewall_payload(),
        "BHSM_reflection_cubic_selection_rules_v14_76.json":reflection_parity_payload(),
        "BHSM_quadratic_quartic_response_sign_v14_76.json":response_sign_payload(),
        "BHSM_singlet_quintet_response_shifts_v14_76.json":representation_response_payload(),
        "BHSM_area_response_stabilization_budget_v14_76.json":area_response_budget_payload(),
        "BHSM_Landau_source_exhaustion_v14_76.json":source_exhaustion_payload(),
        "BHSM_no_fit_locking_gate_v14_76.json":no_fit_gate_payload(),
        "BHSM_status_ledger_v14_76.json":status_payload(),
        "BHSM_completion_gate_v14_76.json":completion_gate_payload(),
    }


def materialize(outdir: Path) -> list[Path]:
    out=Path(outdir); out.mkdir(parents=True,exist_ok=True)
    written=[]
    for name,payload in sorted(artifact_payloads().items()):
        path=out/name
        path.write_text(json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+"\n",encoding="utf-8")
        written.append(path)
    return written
