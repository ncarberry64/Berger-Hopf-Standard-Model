"""BHSM v14.75 ell=2 Landau coefficient provenance and fourth-variation gate.

v14.74 reduced the candidate three-channel bifurcation to three coefficients
(r,u,v) in the reflection-even ell=2 Landau potential

    V(Q)=r/2 I2 + u/4 I2^2 + v/4 I4,

where Q in Mat(3,R), I2=Tr(Q^T Q), and I4=Tr[(Q^T Q)^2].

This sprint performs the strongest coefficient calculation currently licensed
by the repository and separates it from what the present stratified action
does not yet determine.

1.  The exact normal-graph AREA functional of the round equatorial S3 in unit
    S4 can be expanded through fourth order and projected onto the ell=2
    matrix coefficients f_Q(q)=Tr(Q^T R(q)), where R(q) is the SO(3) adjoint
    rotation of q in SU(2)=S3 and Haar measure is normalized to one.

    Exact Haar moments give
      <f^2>                  = I2/3
      <|grad f|^2>           = 8 I2/3
      <f^4>                  = (2 I2^2-I4)/5
      <f^2 |grad f|^2>       = 8(2 I2^2-I4)/15
      <|grad f|^4>           = 176 I2^2/15 - 16 I4/5.

    For chi=pi/2+t f,
      area density
        = 1 + t^2[|grad f|^2/2-3f^2/2]
          + t^4[7f^4/8-f^2|grad f|^2/4-|grad f|^4/8]+O(t^6).

    Hence the normalized unit-area Landau coefficients are
      r_area = 5/3,
      u_area = -83/15,
      v_area = 43/30.

    This witness does NOT satisfy the v14.74 locking cone.  It has r>0 and
    3u+v=-91/6<0.  Therefore the pure area functional cannot drive the desired
    bifurcation near the round seam.

2.  This area functional is a geometric Jacobi witness, not automatically an
    owned term of the authoritative BHSM action.  The v7.1 stratified action
    owns M8, M5, M4, GHY and compatibility sectors with independently typed
    Wilson data; it does not contain an independently declared seam-tension
    area term.  The v14.29 View-2 action is explicitly only a conditional
    candidate, and v14.30 reports that the nonlinear p8 parent reduction is not
    derived.

3.  Even after all bare fourth derivatives are known, the effective quartic
    coefficients require cubic response tensors of eliminated interior fields.
    In coordinates with the quadratic physical boundary/interior mixing already
    Schur-reduced,

      Gamma = 1/2 r(x,x) + 1/2 <y,K y>
              + 1/2 <y,B(x,x)> + 1/24 T4(x,x,x,x)+...

    gives
      y* = -1/2 K^{-1}B(x,x)+...
    and along x=t q,

      a4_eff(q) = T4(q^4)/24
                  - [B(q,q)^T K^{-1} B(q,q)]/8.

    Thus a Hessian alone cannot determine u and v.

4.  Two quartic rays are sufficient to extract u and v once the physical
    effective action is actually evaluable:
      Q_A=diag(1,0,0): a4_A=(u+v)/4,
      Q_B=diag(1,1,0): a4_B=u+v/2,
    so
      u=2 a4_B-4 a4_A,
      v=8 a4_A-2 a4_B.
    Quadratically r=2 a2_A=a2_B.

The physical BHSM coefficients r,u,v are therefore NOT_NUMERICALLY_DERIVED in
v14.75.  The next object is the action-owned D2/D3/D4 global shape-response
tensor on one stationary full-preimage background, including KKT/field
elimination and the nonlocal spectral sector.

No measured particle/flavor data are used and no physical prediction is
emitted.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

VERSION = "v14.75"

PRIMARY_VERDICT = (
    "BHSM_V14_75_THE_EXACT_ROUND_EQUATOR_NORMAL_GRAPH_AREA_FUNCTIONAL_CAN_BE_"
    "PROJECTED_THROUGH_FOURTH_ORDER_ONTO_THE_ELL2_MATRIX_ORDER_PARAMETER_AND_"
    "GIVES_NORMALIZED_COEFFICIENTS_R_EQUALS_5_OVER_3_U_EQUALS_MINUS_83_OVER_15_"
    "V_EQUALS_43_OVER_30_WHICH_FAIL_THE_LOCKING_CONE_BECAUSE_R_IS_POSITIVE_AND_"
    "THREE_U_PLUS_V_EQUALS_MINUS_91_OVER_6;_HOWEVER_THIS_AREA_FUNCTIONAL_IS_A_"
    "GEOMETRIC_JACOBI_WITNESS_NOT_AN_INDEPENDENTLY_OWNED_SEAM_TENSION_TERM_IN_"
    "THE_AUTHORITATIVE_STRATIFIED_ACTION_AND_THE_CURRENT_ARCHIVE_DOES_NOT_"
    "PROVIDE_THE_COMPLETE_GLOBAL_D2_D3_D4_SHAPE_RESPONSE_TENSORS_OR_THE_"
    "NONLINEAR_FULL_PREIMAGE_P8_REDUCTION_NEEDED_TO_COMPUTE_PHYSICAL_R_U_V;_"
    "MOREOVER_EFFECTIVE_QUARTICS_RECEIVE_NEGATIVE_CUBIC_RESPONSE_SCHUR_"
    "CORRECTIONS_SO_THE_HESSIAN_ALONE_IS_INSUFFICIENT;_PHYSICAL_R_U_V_REMAIN_"
    "OPEN_WITHOUT_FIT"
)

EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_FULL_PREIMAGE_STATIONARY_BACKGROUND_WITH_COMPLETE_GAUGE_"
    "REDUCED_SECOND_THIRD_AND_FOURTH_SHAPE_VARIATIONS_OF_S8_TWO_CAP_S5_GHY_"
    "M4_LOCALIZED_COMPATIBILITY_KKT_AND_NONLOCAL_SPECTRAL_SECTORS_THEN_"
    "QUADRATIC_SCHUR_REDUCTION_AND_CUBIC_RESPONSE_ELIMINATION_TO_FORM_THE_"
    "PHYSICAL_EFFECTIVE_ELL2_COEFFICIENTS_R_U_V_AND_APPLY_THE_NO_FIT_LOCKING_"
    "CONE_R_LESS_THAN_ZERO_V_GREATER_THAN_ZERO_THREE_U_PLUS_V_GREATER_THAN_"
    "ZERO_BEFORE_ANY_CALDERON_OR_NEUTRINO_EXECUTION"
)


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode("utf-8")


def sha256_payload(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def ell2_haar_moments(i2: Fraction | int | float, i4: Fraction | int | float) -> dict[str, Any]:
    """Exact invariant moments for f_Q=Tr(Q^T R(q)), q Haar-uniform on SU(2)."""
    I2 = Fraction(i2)
    I4 = Fraction(i4)
    return {
        "f2": I2 / 3,
        "grad2": Fraction(8, 3) * I2,
        "f4": (2 * I2 * I2 - I4) / 5,
        "f2_grad2": Fraction(8, 15) * (2 * I2 * I2 - I4),
        "grad4": Fraction(176, 15) * I2 * I2 - Fraction(16, 5) * I4,
    }


def area_quadratic_coefficient(i2: Fraction | int | float) -> Fraction:
    I2 = Fraction(i2)
    m = ell2_haar_moments(I2, I2)  # i4 unused by f2/grad2
    return Fraction(1, 2) * m["grad2"] - Fraction(3, 2) * m["f2"]


def area_quartic_coefficient(i2: Fraction | int | float, i4: Fraction | int | float) -> Fraction:
    m = ell2_haar_moments(i2, i4)
    return (
        Fraction(7, 8) * m["f4"]
        - Fraction(1, 4) * m["f2_grad2"]
        - Fraction(1, 8) * m["grad4"]
    )


def normalized_area_landau_coefficients() -> dict[str, Fraction]:
    """Landau convention a2=(r/2)I2 and a4=(u/4)I2^2+(v/4)I4."""
    return {
        "r": Fraction(5, 3),
        "u": Fraction(-83, 15),
        "v": Fraction(43, 30),
    }


def locking_cone(r: float, u: float, v: float) -> bool:
    return r < 0.0 and v > 0.0 and 3.0 * u + v > 0.0


def normalized_area_payload() -> dict[str, Any]:
    c = normalized_area_landau_coefficients()
    rays = [
        {"name": "A", "I2": 1, "I4": 1},
        {"name": "B", "I2": 2, "I4": 2},
        {"name": "C", "I2": 3, "I4": 3},
        {"name": "D", "I2": 2, "I4": 4},
    ]
    rows = []
    for ray in rays:
        a2 = area_quadratic_coefficient(ray["I2"])
        a4 = area_quartic_coefficient(ray["I2"], ray["I4"])
        expected2 = Fraction(c["r"], 2) * ray["I2"]
        expected4 = Fraction(c["u"], 4) * ray["I2"] ** 2 + Fraction(c["v"], 4) * ray["I4"]
        rows.append(
            {
                **ray,
                "a2": str(a2),
                "a4": str(a4),
                "quadratic_residual": float(a2 - expected2),
                "quartic_residual": float(a4 - expected4),
            }
        )
    three_u_plus_v = 3 * c["u"] + c["v"]
    return {
        "version": VERSION,
        "functional": "normalized mean area of normal graph chi=pi/2+t f_Q in unit S4",
        "normalization": "Haar mean over S3 equals one; physical area multiplies by Vol(S3) a^3 and any owned action coefficient",
        "ell2_eigenvalue": 8,
        "area_density_expansion": (
            "1+t^2[(grad f)^2/2-3f^2/2]+"
            "t^4[7f^4/8-f^2(grad f)^2/4-(grad f)^4/8]+O(t^6)"
        ),
        "exact_landau_coefficients": {k: str(v) for k, v in c.items()},
        "float_landau_coefficients": {k: float(v) for k, v in c.items()},
        "three_u_plus_v": str(three_u_plus_v),
        "locking_cone_satisfied": locking_cone(float(c["r"]), float(c["u"]), float(c["v"])),
        "reason_locking_fails": ["r_area>0", "3 u_area+v_area<0"],
        "ray_checks": rows,
        "action_ownership": "GEOMETRIC_JACOBI_WITNESS_ONLY_NOT_AUTOMATIC_BHSM_SEAM_TENSION",
        "physical_prediction": False,
    }


def moment_identity_payload() -> dict[str, Any]:
    examples = [
        ("rank1", 1, 1),
        ("rank2_equal", 2, 2),
        ("identity", 3, 3),
        ("rank2_unequal_invariant_witness", 5, 17),
    ]
    rows = []
    for name, i2, i4 in examples:
        m = ell2_haar_moments(i2, i4)
        rows.append({"name": name, "I2": i2, "I4": i4, **{k: str(v) for k, v in m.items()}})
    return {
        "version": VERSION,
        "basis": "f_Q(q)=Tr(Q^T Ad_q) with normalized Haar measure on SU(2)=S3",
        "identities": {
            "<f^2>": "I2/3",
            "<|grad f|^2>": "8 I2/3",
            "<f^4>": "(2 I2^2-I4)/5",
            "<f^2 |grad f|^2>": "8(2 I2^2-I4)/15",
            "<|grad f|^4>": "176 I2^2/15-16 I4/5",
        },
        "rows": rows,
        "physical_prediction": False,
    }


def extract_landau_coefficients(
    a2_A: float, a2_B: float, a4_A: float, a4_B: float
) -> dict[str, float]:
    """Extract r,u,v from A=diag(1,0,0), B=diag(1,1,0) ray coefficients."""
    r_A = 2.0 * float(a2_A)
    r_B = float(a2_B)
    u = 2.0 * float(a4_B) - 4.0 * float(a4_A)
    v = 8.0 * float(a4_A) - 2.0 * float(a4_B)
    return {
        "r": 0.5 * (r_A + r_B),
        "r_from_A": r_A,
        "r_from_B": r_B,
        "quadratic_consistency_residual": abs(r_A - r_B),
        "u": u,
        "v": v,
    }


def coefficient_extractor_payload() -> dict[str, Any]:
    c = normalized_area_landau_coefficients()
    a2A = float(area_quadratic_coefficient(1))
    a2B = float(area_quadratic_coefficient(2))
    a4A = float(area_quartic_coefficient(1, 1))
    a4B = float(area_quartic_coefficient(2, 2))
    result = extract_landau_coefficients(a2A, a2B, a4A, a4B)
    return {
        "version": VERSION,
        "ray_A": "diag(1,0,0): I2=1,I4=1; a2_A=r/2; a4_A=(u+v)/4",
        "ray_B": "diag(1,1,0): I2=2,I4=2; a2_B=r; a4_B=u+v/2",
        "inverse": {
            "r": "2 a2_A = a2_B",
            "u": "2 a4_B-4 a4_A",
            "v": "8 a4_A-2 a4_B",
        },
        "area_witness_extraction": result,
        "expected_area": {k: float(v) for k, v in c.items()},
        "max_area_extraction_residual": max(
            abs(result[k] - float(c[k])) for k in ("r", "u", "v")
        ),
        "ready_for_physical_action": True,
        "physical_action_currently_evaluable_on_these_rays": False,
    }


def reduced_quartic_coefficient(
    bare_T4_q4: float, cubic_response_vector: np.ndarray, interior_hessian: np.ndarray
) -> float:
    """a4_eff=T4/24-(B^T K^-1 B)/8 in quadratic-Schur coordinates."""
    b = np.asarray(cubic_response_vector, dtype=float)
    K = np.asarray(interior_hessian, dtype=float)
    if K.ndim != 2 or K.shape[0] != K.shape[1] or b.shape != (K.shape[0],):
        raise ValueError("incompatible cubic response and interior Hessian")
    values = np.linalg.eigvalsh((K + K.T) / 2.0)
    if np.min(values) <= 0:
        raise ValueError("interior Hessian must be positive definite on the eliminated complement")
    return float(bare_T4_q4 / 24.0 - 0.125 * b @ np.linalg.solve(K, b))


def direct_minimized_quartic_witness(
    t: float, r: float, bare_T4_q4: float, b: np.ndarray, K: np.ndarray
) -> float:
    """Evaluate Gamma(t,y*(t)) in the reduced toy model."""
    b = np.asarray(b, dtype=float)
    K = np.asarray(K, dtype=float)
    y = -0.5 * t * t * np.linalg.solve(K, b)
    return float(
        0.5 * r * t * t
        + 0.5 * y @ K @ y
        + 0.5 * t * t * y @ b
        + bare_T4_q4 * t**4 / 24.0
    )


def quartic_schur_payload() -> dict[str, Any]:
    K = np.array([[2.4, 0.3], [0.3, 1.7]])
    b = np.array([0.8, -0.5])
    T4 = 7.2
    a4 = reduced_quartic_coefficient(T4, b, K)
    r = 1.3
    tvals = [0.02, 0.04, 0.08]
    residuals = []
    for t in tvals:
        exact = direct_minimized_quartic_witness(t, r, T4, b, K)
        reconstructed = 0.5 * r * t * t + a4 * t**4
        residuals.append(abs(exact - reconstructed))
    correction = -0.125 * b @ np.linalg.solve(K, b)
    return {
        "version": VERSION,
        "coordinate_scope": "after quadratic boundary/interior Schur diagonalization",
        "expansion": (
            "Gamma=1/2 r(x,x)+1/2<y,Ky>+1/2<y,B(x,x)>+"
            "T4(x,x,x,x)/24+..."
        ),
        "interior_solution": "y*=-K^-1 B(x,x)/2+O(x^3)",
        "effective_ray_quartic": "a4_eff=T4(q^4)/24-[B(q,q)^T K^-1 B(q,q)]/8",
        "response_correction_sign_for_positive_K": "non-positive",
        "diagnostic_bare_T4_over_24": T4 / 24.0,
        "diagnostic_response_correction": float(correction),
        "diagnostic_effective_a4": a4,
        "direct_substitution_residual": float(max(residuals)),
        "theorem": "D2/Hessian data alone cannot determine the effective u,v; D3 response and D4 are required",
        "diagnostic_coefficients_are_physical": False,
    }


def equal_cap_GHY_cancellation_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "hypotheses": [
            "smooth internal seam shared by the two caps",
            "outward normals are opposite",
            "same induced metric",
            "equal reflection-related Einstein/GHY coefficient",
        ],
        "relations": ["n_-=-n_+", "K_-=-K_+", "sqrt(h)_-=sqrt(h)_+"],
        "sum": "c_GHY integral sqrt(h)(K_+ + K_-)=0",
        "conclusion": (
            "on the exactly reflection-symmetric smooth-gluing branch GHY is "
            "variational completion, not an independent seam-tension Landau source"
        ),
        "unequal_cap_coefficients_or_nonidentical_geometry": "requires separate evaluation",
        "physical_prediction": False,
    }


def action_provenance_payload() -> dict[str, Any]:
    rows = [
        {
            "sector": "M8 parent S8",
            "current_ownership": "independent parent-theory input in v7.1",
            "D2_ell2": "not fully evaluated on the required full-preimage nonround stationary background",
            "D3_D4_ell2": "not evaluated",
            "contributes_to_physical_r_u_v": True,
        },
        {
            "sector": "two M5 cap actions",
            "current_ownership": "independent target-stratum Wilson actions",
            "D2_ell2": "round geometric Jacobi piece known only as theorem component",
            "D3_D4_ell2": "complete action-normalized tensors not evaluated",
            "contributes_to_physical_r_u_v": True,
        },
        {
            "sector": "GHY",
            "current_ownership": "variational completion tied to cap gravity",
            "D2_ell2": "cancels pairwise on ideal equal-cap smooth reflection branch",
            "D3_D4_ell2": "requires full branch if cancellation hypotheses fail",
            "contributes_to_physical_r_u_v": "conditional",
        },
        {
            "sector": "M4 localized intrinsic action",
            "current_ownership": "fundamental localized Standard Model/gravity data",
            "D2_ell2": "physical background response not evaluated",
            "D3_D4_ell2": "not evaluated",
            "contributes_to_physical_r_u_v": True,
        },
        {
            "sector": "compatibility/KKT and eliminated interior fields",
            "current_ownership": "action-owned constraints/reactions",
            "D2_ell2": "quadratic Schur architecture exists",
            "D3_D4_ell2": "cubic-response and fourth-order reduction not evaluated",
            "contributes_to_physical_r_u_v": True,
        },
        {
            "sector": "nonlocal spectral/relative determinant",
            "current_ownership": "conditional microscopic/nonlocal branch",
            "D2_ell2": "round diagnostic pieces exist",
            "D3_D4_ell2": "physical full-background derivatives not evaluated",
            "contributes_to_physical_r_u_v": True,
        },
        {
            "sector": "v14.29 gauged eta p2+p8 candidate",
            "current_ownership": "conditional candidate, not authoritative master-action ownership",
            "D2_ell2": "not an action-owned seam-shape tensor",
            "D3_D4_ell2": "v14.30 parent nonlinear p8 reduction marked NOT_DERIVED",
            "contributes_to_physical_r_u_v": "cannot be inserted without missing common-domain/shape intertwiner",
        },
    ]
    return {
        "version": VERSION,
        "rows": rows,
        "physical_r_u_v_numeric_status": "NOT_DERIVED",
        "reason": (
            "the authoritative archive does not contain one stationary full-preimage "
            "background with complete action-normalized D2/D3/D4 shape tensors and "
            "the required cubic-response elimination"
        ),
        "area_witness_is_not_an_owned_seam_tension": True,
        "no_measured_input_used": True,
    }


def no_fit_gate_payload() -> dict[str, Any]:
    area = normalized_area_payload()
    return {
        "version": VERSION,
        "locking_test": "r<0, v>0, 3u+v>0",
        "area_witness": {
            "r": area["exact_landau_coefficients"]["r"],
            "u": area["exact_landau_coefficients"]["u"],
            "v": area["exact_landau_coefficients"]["v"],
            "passes": area["locking_cone_satisfied"],
        },
        "physical_BHSM": {"r": None, "u": None, "v": None, "passes": None},
        "physical_execution_allowed": False,
        "measured_data_may_be_used_to_select_coefficients": False,
        "result": "PHYSICAL_LOCKING_PHASE_UNDECIDED_FROM_CURRENT_ACTION",
    }


def status_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "validated": [
            "exact normalized Haar moment identities for the ell2 matrix coefficient basis",
            "exact fourth-order round-equator normal-graph area expansion",
            "area witness r=5/3, u=-83/15, v=43/30",
            "pure area witness fails the v14.74 locking cone",
            "two ray coefficient extractor reconstructs r,u,v exactly",
            "effective quartic receives a negative cubic-response Schur correction on a positive interior complement",
            "D2/Hessian alone is insufficient for physical u,v",
            "equal-cap internal GHY cancels under exact reflection/smooth-gluing hypotheses",
            "current action provenance does not license treating the area witness as an independent seam tension",
            "physical r,u,v remain uncomputed without fitting",
        ],
        "invalidated": [
            "the universal area/Jacobi functional by itself can trigger the stable ell2 locked phase near the round seam",
            "v14.68-v14.71 Hessian information alone is enough to compute u and v",
            "the v14.29 eta p2+p8 candidate can be inserted directly as the seam-shape quartic",
            "the existence of a structural Landau cone means the current authoritative action has selected it",
        ],
        "reclassified": [
            "v14.75 coefficient work splits into a fully derived geometric area witness and an unresolved physical action sum",
            "the decisive missing data are D3 and D4 as well as D2",
            "KKT/interior elimination is a quartic source, not merely a quadratic stability correction",
            "the no-fit phase test is ready but currently has null physical inputs",
        ],
        "open": [
            EXACT_NEXT_OBJECT,
            "physical stationary full-preimage background",
            "complete action-normalized D2 ell2 tensor",
            "complete D3 boundary-interior response tensor",
            "complete D4 ell2 tensor",
            "physical effective r,u,v",
            "nonround locked solution if the cone passes",
            "three physical Calderon derivatives",
            "Goldstone lifting/splitting",
            "relative heat supertrace",
            "frozen neutrino execution",
        ],
        "FULL_BHSM_COMPLETE": False,
        "MARK_III": "NOT_REACHED",
        "physical_prediction_emitted": False,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "USB_touched": False,
    }


def completion_gate_payload() -> dict[str, Any]:
    area = normalized_area_payload()
    extract = coefficient_extractor_payload()
    schur = quartic_schur_payload()
    gh = equal_cap_GHY_cancellation_payload()
    prov = action_provenance_payload()
    nofit = no_fit_gate_payload()
    validation = {
        "area_ray_checks_exact": all(
            row["quadratic_residual"] == 0.0 and row["quartic_residual"] == 0.0
            for row in area["ray_checks"]
        ),
        "area_fails_locking": area["locking_cone_satisfied"] is False,
        "area_extractor_exact": extract["max_area_extraction_residual"] < 1e-14,
        "quartic_schur_direct_check": schur["direct_substitution_residual"] < 1e-14,
        "quartic_response_is_nonpositive": schur["diagnostic_response_correction"] < 0.0,
        "equal_cap_GHY_cancellation_recorded": "K_+ + K_-" in gh["sum"],
        "physical_coefficients_fail_closed": prov["physical_r_u_v_numeric_status"] == "NOT_DERIVED",
        "no_fit_gate_blocked": nofit["physical_execution_allowed"] is False,
        "no_physical_prediction": True,
    }
    return {
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "geometric_area_coefficients": area["exact_landau_coefficients"],
        "geometric_area_locking_cone": "FAIL",
        "physical_r": None,
        "physical_u": None,
        "physical_v": None,
        "physical_locking_gate": "UNDECIDED",
        "full_BHSM_complete": False,
        "mark_III": "NOT_REACHED",
        "physical_execution_allowed": False,
        "physical_prediction_emitted": False,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "usb_touched": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def artifact_payloads() -> dict[str, Any]:
    return {
        "BHSM_ell2_Haar_moment_identities_v14_75.json": moment_identity_payload(),
        "BHSM_round_area_Landau_coefficients_v14_75.json": normalized_area_payload(),
        "BHSM_Landau_coefficient_extractor_v14_75.json": coefficient_extractor_payload(),
        "BHSM_quartic_response_Schur_formula_v14_75.json": quartic_schur_payload(),
        "BHSM_equal_cap_GHY_cancellation_v14_75.json": equal_cap_GHY_cancellation_payload(),
        "BHSM_global_shape_action_provenance_v14_75.json": action_provenance_payload(),
        "BHSM_no_fit_locking_gate_v14_75.json": no_fit_gate_payload(),
        "BHSM_status_ledger_v14_75.json": status_payload(),
        "BHSM_completion_gate_v14_75.json": completion_gate_payload(),
    }


def materialize(outdir: Path) -> list[Path]:
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for name, payload in sorted(artifact_payloads().items()):
        path = out / name
        path.write_text(
            json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        written.append(path)
    return written
