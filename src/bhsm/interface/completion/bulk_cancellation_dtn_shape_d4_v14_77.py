"""BHSM v14.77 complementary-bulk cancellation and DtN shape-D4 gate.

This sprint continues the v14.76 bare-D4 source hunt.

1. Complementary-domain theorem.
If two reflection-related caps M+ and M- exactly partition a fixed ambient
manifold M, carry the same local bulk Lagrangian density and coefficient, and
the ambient fields/metric are held fixed while the common seam moves, then

    S_bulk[X] = c int_{M+(X)} L + c int_{M-(X)} L
              = c int_M L,

so every pure seam-position derivative vanishes, including D4.  With the usual
opposite outward normals the equal-coefficient internal GHY pair also cancels.
The same statement applies to the lifted M8 preimages when they are merely a
partition of one fixed parent density.

Therefore fixed-background local bulk *domain reallocation* cannot be the
positive bare D4 source sought after v14.76.  A nonzero local contribution
requires metric/field deformation, unequal cap coefficients/densities, a
localized seam action, or another term that is not just complementary-domain
partitioning.

2. Exact two-sided DtN width-shape theorem.
For the v14.30 constant positive mode with q=sqrt(H)>0 and equal half-width L,

    N(delta)=q[tanh(q(L+delta))+tanh(q(L-delta))].

This is the exact two-sided DtN response when the seam is displaced uniformly
so the total width remains fixed.  It is even in delta.  Writing x=qL,
t=tanh x,

    N(delta)=2 q t
      -2 q^3 t(1-t^2) delta^2
      +(2/3) q^5 t(1-t^2)(2-3t^2) delta^4
      +O(delta^6).

Thus the geometric DtN shape quartic is positive for
    tanh^2(qL)<2/3,
zero at qL=atanh(sqrt(2/3)),
and negative for tanh^2(qL)>2/3.

This does not reuse the v14.30 derivative-expansion coefficient named c4.
It is a different fourth derivative: shape dependence of the exact DtN map.

The theorem is for a uniform seam-width displacement of one frozen quadratic
mode.  It is not yet the full ell=2 pseudodifferential shape derivative, so it
does not determine physical Landau u or v.

No measured input is used and no physical observable is emitted.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

VERSION = "v14.77"

PRIMARY_VERDICT = (
    "BHSM_V14_77_ON_THE_EQUAL_REFLECTION_BRANCH_FIXED_BACKGROUND_LOCAL_M5_"
    "BULK_ACTIONS_AND_THEIR_EQUAL_GHY_COMPLETION_CANCEL_ALL_PURE_SEAM_DOMAIN_"
    "MOTION_DERIVATIVES_AND_THE_SAME_COMPLEMENTARY_PREIMAGE_ARGUMENT_REMOVES_"
    "FIXED_PARENT_M8_DOMAIN_REALLOCATION_AS_A_BARE_D4_SOURCE;_HOWEVER_THE_"
    "EXACT_TWO_SIDED_DTN_MAP_HAS_A_DISTINCT_GEOMETRIC_SHAPE_FOURTH_DERIVATIVE_"
    "UNDER_FIXED_TOTAL_WIDTH_WITH_QUARTIC_COEFFICIENT_PROPORTIONAL_TO_"
    "TANH_X_ONE_MINUS_TANH_X_SQUARED_TIMES_TWO_MINUS_THREE_TANH_X_SQUARED_"
    "AND_IS_POSITIVE_FOR_X_LESS_THAN_ATANH_SQRT_TWO_THIRDS;_THIS_VALIDATES_A_"
    "POTENTIAL_POSITIVE_NONLOCAL_SHAPE_D4_MECHANISM_BUT_NOT_THE_PHYSICAL_ELL2_"
    "LANDAU_U_V_BECAUSE_THE_FULL_PSEUDODIFFERENTIAL_SHAPE_DERIVATIVE_AND_"
    "STATIONARY_BACKGROUND_ARE_STILL_OPEN"
)

EXACT_NEXT_OBJECT = (
    "COMPUTE_THE_FULL_ELL2_FIRST_THROUGH_FOURTH_SHAPE_DERIVATIVES_OF_THE_"
    "OPERATOR_VALUED_TWO_SIDED_CALDERON_DTN_MAP_ON_THE_ACTION_SELECTED_"
    "FULL_PREIMAGE_BACKGROUND_INCLUDING_TANGENTIAL_BERGER_BLOCKS_CONNECTION_"
    "TRANSPORT_AND_GAUGE_ZERO_MODE_PROJECTORS_THEN_EVALUATE_RAYS_A_AND_B_AND_"
    "COMBINE_WITH_DYNAMIC_M8_M5_METRIC_FIELD_DEFORMATIONS_NONCONSTANT_ETA_M4_"
    "LOCALIZED_AND_NONLOCAL_DETERMINANT_CONTRIBUTIONS_TO_FORM_PHYSICAL_R_U_V"
)


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("utf-8")


def sha256_payload(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def complementary_bulk_action(total_integral: float, coefficient: float = 1.0) -> float:
    return float(coefficient) * float(total_integral)


def complementary_cap_sum(
    plus_integral: float,
    minus_integral: float,
    coefficient_plus: float = 1.0,
    coefficient_minus: float = 1.0,
) -> float:
    return float(coefficient_plus)*float(plus_integral) + float(coefficient_minus)*float(minus_integral)


def partition_derivative_witness(delta: float, total: float = 7.3, base_plus: float = 3.1, slope: float = 0.8, quartic: float = 0.17) -> dict[str, float]:
    """Synthetic exact partition witness: I+ changes, I-=total-I+."""
    d=float(delta)
    plus=float(base_plus)+float(slope)*d+float(quartic)*d**4
    minus=float(total)-plus
    equal=complementary_cap_sum(plus,minus,1.0,1.0)
    unequal=complementary_cap_sum(plus,minus,1.0,1.3)
    return {"plus":plus,"minus":minus,"equal_sum":equal,"unequal_sum":unequal}


def bulk_cancellation_payload() -> dict[str, Any]:
    deltas=[-0.7,-0.2,0.0,0.3,0.8]
    rows=[{"delta":d,**partition_derivative_witness(d)} for d in deltas]
    equal_values=[r["equal_sum"] for r in rows]
    unequal_values=[r["unequal_sum"] for r in rows]
    return {
        "version":VERSION,
        "theorem":"if M+(X) union M-(X)=M fixed and coefficients/density agree, S_bulk=c int_M L is independent of seam X",
        "all_pure_shape_derivatives":"zero to every order",
        "D4_fixed_background_equal_cap_bulk":0.0,
        "GHY_equal_internal_seam":"K_-=-K_+ with identical induced metric and coefficient, so pair cancels",
        "lifted_M8_preimage_statement":"same cancellation for complementary preimages of one fixed parent density",
        "nonzero_local_shape_requires":[
            "metric or matter fields vary with the seam",
            "cap coefficients/densities differ",
            "localized seam action",
            "nonlocal/domain-sensitive spectral response",
        ],
        "synthetic_equal_sum_spread":float(max(equal_values)-min(equal_values)),
        "synthetic_unequal_sum_spread":float(max(unequal_values)-min(unequal_values)),
        "rows":rows,
        "scope":"fixed ambient fields/metric and exactly complementary reflection-related caps",
        "physical_prediction":False,
    }


def mismatch_formula_payload() -> dict[str, Any]:
    return {
        "version":VERSION,
        "formula":"c+ int_M+ L + c- int_M- L = c- int_M L + (c+-c-) int_M+ L",
        "equal_coefficient_limit":"c+=c- removes all pure domain-motion dependence",
        "unequal_coefficients":"shape dependence is proportional to coefficient/density mismatch",
        "retained_equal_reflection_branch_uses_mismatch_as_input":False,
        "physical_mismatch_derived":False,
    }


def dtn_two_sided_uniform(q: float, L: float, delta: float) -> float:
    q=float(q); L=float(L); delta=float(delta)
    if q < 0 or L <= 0 or abs(delta) >= L:
        raise ValueError("require q>=0, L>0, |delta|<L")
    if q == 0.0:
        return 0.0
    return q*(math.tanh(q*(L+delta))+math.tanh(q*(L-delta)))


def dtn_uniform_coefficients(q: float, L: float) -> dict[str, float]:
    q=float(q); L=float(L)
    if q < 0 or L <= 0:
        raise ValueError("require q>=0 and L>0")
    if q == 0.0:
        return {"N0":0.0,"a2":0.0,"a4":0.0,"x":0.0,"t":0.0}
    x=q*L
    t=math.tanh(x)
    a2=-2.0*q**3*t*(1.0-t*t)
    a4=(2.0/3.0)*q**5*t*(1.0-t*t)*(2.0-3.0*t*t)
    return {"N0":2.0*q*t,"a2":a2,"a4":a4,"x":x,"t":t}


def dtn_uniform_derivatives(q: float, L: float) -> dict[str, float]:
    c=dtn_uniform_coefficients(q,L)
    return {
        "D1":0.0,
        "D2":2.0*c["a2"],
        "D3":0.0,
        "D4":24.0*c["a4"],
    }


def dtn_threshold() -> float:
    return math.atanh(math.sqrt(2.0/3.0))


def dtn_quartic_sign(q: float, L: float, tol: float = 1e-12) -> str:
    a4=dtn_uniform_coefficients(q,L)["a4"]
    if abs(a4)<tol:
        return "ZERO"
    return "POSITIVE" if a4>0 else "NEGATIVE"


def dtn_shape_quartic_payload() -> dict[str, Any]:
    xstar=dtn_threshold()
    # Choose q=1 so L=x for transparent witnesses.
    xs=[0.25,0.75,xstar,1.5,3.0]
    rows=[]
    for x in xs:
        c=dtn_uniform_coefficients(1.0,x)
        rows.append({
            "x_qL":x,
            "tanh_squared":math.tanh(x)**2,
            "a2":c["a2"],
            "a4":c["a4"],
            "quartic_sign":dtn_quartic_sign(1.0,x,1e-10),
        })
    return {
        "version":VERSION,
        "exact_map":"N(delta)=q[tanh(q(L+delta))+tanh(q(L-delta))]",
        "expansion":"N=2qt-2q^3 t(1-t^2) delta^2+(2/3)q^5 t(1-t^2)(2-3t^2) delta^4+O(delta^6)",
        "x":"qL",
        "t":"tanh(qL)",
        "quadratic_coefficient":"-2 q^3 t(1-t^2) < 0 for q,L>0",
        "quartic_coefficient":"(2/3) q^5 t(1-t^2)(2-3t^2)",
        "threshold_exact":"atanh(sqrt(2/3))",
        "threshold_numeric":xstar,
        "positive_region":"0<qL<atanh(sqrt(2/3))",
        "negative_region":"qL>atanh(sqrt(2/3))",
        "odd_derivatives_cancel":"D1=D3=0 by equal-cap reflection",
        "rows":rows,
        "this_is_v14_30_derivative_expansion_c4":False,
        "this_is_a_shape_derivative_of_exact_DtN":True,
        "physical_ell2_Landau_coefficient":False,
    }


def finite_difference_even_coefficients(q: float, L: float, h: float = 2e-3) -> dict[str, float]:
    """Extract even Taylor a2,a4 using values at h and 2h."""
    f0=dtn_two_sided_uniform(q,L,0.0)
    f1=0.5*(dtn_two_sided_uniform(q,L,h)+dtn_two_sided_uniform(q,L,-h))-f0
    f2=0.5*(dtn_two_sided_uniform(q,L,2*h)+dtn_two_sided_uniform(q,L,-2*h))-f0
    # f1=a2 h^2+a4 h^4+..., f2=4a2 h^2+16a4 h^4+...
    a4=(f2-4.0*f1)/(12.0*h**4)
    a2=(f1-a4*h**4)/(h**2)
    return {"a2":a2,"a4":a4}


def dtn_finite_difference_payload() -> dict[str, Any]:
    cases=[(0.8,0.7),(1.2,0.9),(1.4,1.1)]
    rows=[]
    for q,L in cases:
        exact=dtn_uniform_coefficients(q,L)
        fd=finite_difference_even_coefficients(q,L)
        rows.append({
            "q":q,"L":L,
            "a2_exact":exact["a2"],"a2_fd":fd["a2"],
            "a4_exact":exact["a4"],"a4_fd":fd["a4"],
            "a2_residual":abs(exact["a2"]-fd["a2"]),
            "a4_residual":abs(exact["a4"]-fd["a4"]),
        })
    return {
        "version":VERSION,
        "rows":rows,
        "max_a2_residual":max(r["a2_residual"] for r in rows),
        "max_a4_residual":max(r["a4_residual"] for r in rows),
        "diagnostic_not_physical":True,
    }


def dtn_action_shape_coefficients(q: float, L: float, phi_norm_squared: float = 1.0) -> dict[str, float]:
    """For S=1/2 ||phi||^2 N(delta), return shape Taylor coefficients."""
    if phi_norm_squared < 0:
        raise ValueError("norm squared must be nonnegative")
    c=dtn_uniform_coefficients(q,L)
    scale=0.5*float(phi_norm_squared)
    return {"S0":scale*c["N0"],"a2_shape":scale*c["a2"],"a4_shape":scale*c["a4"]}


def dtn_vs_response_sign_payload() -> dict[str, Any]:
    thin=dtn_action_shape_coefficients(1.0,0.6,1.0)
    thick=dtn_action_shape_coefficients(1.0,2.0,1.0)
    return {
        "version":VERSION,
        "v14_76_eliminated_field_response":"-B^T K^-1 B/8 <=0 on every ray for K>0",
        "v14_77_DtN_width_shape_response":"sign-indefinite because the operator/domain itself changes with seam geometry",
        "thin_cap_witness":thin,
        "thick_cap_witness":thick,
        "thin_quartic_positive":thin["a4_shape"]>0,
        "thick_quartic_negative":thick["a4_shape"]<0,
        "no_contradiction":True,
        "reason":"these are different operations: integrating out stable fields at fixed bare action versus differentiating a domain-dependent nonlocal operator",
    }


def source_update_payload() -> dict[str, Any]:
    return {
        "version":VERSION,
        "invalidated_as_fixed_background_bare_D4_sources":[
            "equal-coefficient complementary M5 local bulk domain motion",
            "equal internal GHY pair under smooth reflection gluing",
            "complementary lifted M8 parent-domain reallocation at fixed fields",
            "constant eta p8",
            "fixed-operator quadratic DtN derivative-expansion c4",
        ],
        "validated_candidate_classes":[
            "dynamic M8/M5 metric or field deformation",
            "nonconstant degree-one eta background",
            "intrinsic/localized M4 induced-metric and field response",
            "shape dependence of exact nonlocal Calderon/DtN operator",
            "relative determinant/heat response",
            "cap coefficient/density mismatch if action-derived",
        ],
        "new_exact_positive_candidate":"two-sided DtN uniform-width shape a4 for qL below threshold",
        "physical_ell2_positive_D4_derived":False,
        "physical_r_u_v_status":"OPEN",
    }


def ell2_handoff_payload() -> dict[str, Any]:
    return {
        "version":VERSION,
        "uniform_width_theorem_is_ell2_result":False,
        "missing_operations":[
            "replace scalar q by operator-valued tangential K on retained Berger blocks",
            "differentiate the full Calderon/Weyl map under nonuniform ell2 seam deformation",
            "include variation of edge/cap lengths, induced metric, connection transport, and K itself",
            "project gauge/constraint/zero modes before inversion or determinant",
            "evaluate the two invariant matrix rays Q_A and Q_B",
            "combine with local dynamic-sector bare D4 and cubic-response corrections",
        ],
        "eligible_for_physical_Landau_extraction":False,
        "next_no_fit_output":"r,u,v only after both invariant rays are fully action-evaluable",
    }


def status_payload() -> dict[str, Any]:
    return {
        "version":VERSION,
        "validated":[
            "equal-coefficient complementary fixed-background local bulk action is seam-position independent to all orders",
            "equal internal GHY cancels on the smooth reflection branch",
            "the complementary-preimage statement removes fixed-parent M8 domain reallocation as a pure D4 source",
            "the exact two-sided DtN map under fixed-total-width seam displacement is even",
            "its quadratic shape coefficient is strictly negative for q,L>0",
            "its quartic shape coefficient has an exact sign threshold",
            "positive DtN shape quartic occurs for qL below atanh(sqrt(2/3))",
            "negative DtN shape quartic occurs above that threshold",
            "this shape quartic is distinct from the v14.30 derivative-expansion coefficient named c4",
            "domain-dependent nonlocal shape differentiation is not constrained by the v14.76 eliminated-field quartic sign theorem",
        ],
        "invalidated":[
            "fixed-background equal-cap M5 bulk domain motion as the missing positive D4 source",
            "equal-reflection GHY as an independent positive D4 source",
            "fixed-parent complementary M8 preimage motion as an independent positive D4 source",
            "assuming all stable/nonlocal response quartics must be nonpositive",
        ],
        "reclassified":[
            "positive bare D4 search now focuses on dynamic local fields/metrics and geometry-dependent nonlocal operators",
            "the exact DtN map is a concrete sign-indefinite D4 candidate, but only after genuine shape differentiation",
            "the decisive nonlocal calculation is an ell2 operator-valued shape derivative, not reuse of low-energy c4",
        ],
        "open":[
            EXACT_NEXT_OBJECT,
            "physical operator-valued ell2 Calderon shape D4",
            "dynamic M8/M5 local D4",
            "degree-one eta D4",
            "M4 localized D4",
            "relative determinant D4",
            "physical r,u,v",
            "locked branch if cone passes",
            "three physical Goldstone/Calderon derivatives",
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
    bulk=bulk_cancellation_payload()
    dtn=dtn_shape_quartic_payload()
    fd=dtn_finite_difference_payload()
    compare=dtn_vs_response_sign_payload()
    sources=source_update_payload()
    validation={
        "equal_bulk_exactly_constant":bulk["synthetic_equal_sum_spread"]<1e-14,
        "unequal_bulk_shape_dependent":bulk["synthetic_unequal_sum_spread"]>1e-3,
        "fixed_bulk_D4_zero":bulk["D4_fixed_background_equal_cap_bulk"]==0.0,
        "DtN_threshold_positive":dtn["threshold_numeric"]>1.0,
        "DtN_positive_witness":any(r["quartic_sign"]=="POSITIVE" for r in dtn["rows"]),
        "DtN_negative_witness":any(r["quartic_sign"]=="NEGATIVE" for r in dtn["rows"]),
        "DtN_odd_derivatives_cancel":dtn["odd_derivatives_cancel"]=="D1=D3=0 by equal-cap reflection",
        "DtN_not_old_c4":dtn["this_is_v14_30_derivative_expansion_c4"] is False,
        "finite_difference_a2":fd["max_a2_residual"]<1e-7,
        "finite_difference_a4":fd["max_a4_residual"]<2e-5,
        "response_theorems_distinguished":compare["no_contradiction"] is True,
        "physical_ell2_D4_not_overclaimed":sources["physical_ell2_positive_D4_derived"] is False,
        "no_physical_prediction":True,
    }
    return {
        "version":VERSION,
        "primary_verdict":PRIMARY_VERDICT,
        "exact_next_object":EXACT_NEXT_OBJECT,
        "fixed_background_equal_cap_local_bulk_D4":"ZERO",
        "fixed_background_equal_cap_GHY_D4":"ZERO",
        "uniform_two_sided_DtN_shape_D4":"SIGN_INDEFINITE_WITH_POSITIVE_THIN_CAP_REGION",
        "DtN_shape_threshold_qL":dtn["threshold_numeric"],
        "physical_ell2_DtN_D4":None,
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
        "BHSM_complementary_bulk_D4_cancellation_v14_77.json":bulk_cancellation_payload(),
        "BHSM_cap_coefficient_mismatch_formula_v14_77.json":mismatch_formula_payload(),
        "BHSM_two_sided_DtN_shape_quartic_v14_77.json":dtn_shape_quartic_payload(),
        "BHSM_DtN_shape_finite_difference_v14_77.json":dtn_finite_difference_payload(),
        "BHSM_DtN_vs_eliminated_response_sign_v14_77.json":dtn_vs_response_sign_payload(),
        "BHSM_bare_D4_source_update_v14_77.json":source_update_payload(),
        "BHSM_ell2_Calderon_D4_handoff_v14_77.json":ell2_handoff_payload(),
        "BHSM_status_ledger_v14_77.json":status_payload(),
        "BHSM_completion_gate_v14_77.json":completion_gate_payload(),
    }


def materialize(outdir: Path) -> list[Path]:
    out=Path(outdir); out.mkdir(parents=True,exist_ok=True)
    written=[]
    for name,payload in sorted(artifact_payloads().items()):
        path=out/name
        path.write_text(json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+"\n",encoding="utf-8")
        written.append(path)
    return written
