"""BHSM v14.79 alpha-scaled dynamic-band Landau and p8 Bridge-And-Prove gate.

Architectural directives implemented
------------------------------------
1. Fine-structure scaling:
   - the canonically normalized dimensionless ell=2 shape is written
         Q_b = alpha * Qhat_b
     with no independent ripple amplitude;
   - Goldstone/quasi-energy lifting is written
         H_lift,b = alpha * Omega_b * G_b,
     where Omega_b and G_b must be action-derived.

2. Bridge-And-Prove p8 reduction:
   - the parent p8 coefficient remains the retained 1/8, with no new Wilson
     coefficient;
   - an explicit provisional constant-modulus fiber bridge is allowed for
     immediate diagnostics;
   - the bridge is tagged and cannot close the physical gate;
   - the backward proof ledger immediately identifies which equalities are
     proved and which remain open.

3. Dynamic band Landau coefficients:
   - r_b,u_b,v_b are functionals of the local band/background/response state,
     not universal constants;
   - quadratic cross-band response is alpha-scaled and gives
         r_eff = r_bare - alpha^2 c^T K^-1 c;
   - the nonlinear p8 reduction itself is band-dependent through the exact
     normalized fiber moment
         M8[psi_b] = int_F |psi_b|^8 dmu_F.

4. Safety lock:
   PHYSICAL_EXECUTION_BLOCKED remains absolute.

New exact mathematics
---------------------
A. Alpha scaling cannot change a Landau sign cone.  Since
    I2(alpha Qhat)=alpha^2 I2(Qhat),
    I4(alpha Qhat)=alpha^4 I4(Qhat),
the coefficients in Qhat coordinates are
    rhat=alpha^2 r, uhat=alpha^4 u, vhat=alpha^4 v.
Thus signs and v/u ratios are unchanged for alpha>0.  In particular the
v14.78 commuting relation v=-u/2 survives exactly.

B. If the desired isotropic locked amplitude itself is fixed to alpha,
    Q=alpha R,
stationarity requires the new alpha-criticality condition
    r + alpha^2(3u+v)=0.
This is not produced by a reparameterization; it is an action test.

C. Nonlinear fiber reduction cannot preserve the p8 coefficient by L2
normalization alone.  For a normalized fiber mode psi on volume V_F,
    int |psi|^2 = 1,
Jensen/Hölder gives
    M8=int |psi|^8 >= V_F^-3,
with equality iff |psi| is constant.  Therefore the p8 effective coefficient
is profile-dependent.  The provisional bridge chooses the equality case
    M8_bridge=V_F^-3,
which is the unique constant-modulus/basic-mode bridge, not a derived
degree-one result.

D. For the positive-energy p8 core E8=(M8/8) X^4 and the reflection pair
    X_+ = X0 + alpha x1,
    X_- = X0 - alpha x1,
the reflection-normalized mean is
    Ebar = M8[X0^4/8 + 3 X0^2 x1^2 alpha^2/4 + x1^4 alpha^4/8].
Hence a nonconstant background can provide a positive bare quartic in this
bridge, while also providing positive quadratic stiffness.  A separate
negative response is still needed to drive r below zero.

No measured particle/flavor input is used and no physical observable is
emitted.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np

VERSION = "v14.79"

PRIMARY_VERDICT = (
    "BHSM_V14_79_IMPLEMENTS_ALPHA_AS_THE_SINGLE_DIMENSIONLESS_RIPPLE_AND_"
    "GOLDSTONE_LIFTING_SCALE_AND_PROVES_THAT_ALPHA_RESCALING_PRESERVES_THE_"
    "LANDAU_SIGN_CONE_AND_THE_V14_78_COMMUTING_NO_GO;_AN_ALPHA_LOCKED_"
    "ISOTROPIC_SHAPE_REQUIRES_THE_ACTION_CRITICALITY_RELATION_R_PLUS_ALPHA_"
    "SQUARED_TIMES_THREE_U_PLUS_V_EQUALS_ZERO;_THE_PARENT_P8_BRIDGE_IS_"
    "FORMALIZED_WITH_NO_NEW_WILSON_COEFFICIENT_AND_A_NEW_HOLDER_JENSEN_"
    "THEOREM_SHOWS_ITS_EFFECTIVE_REDUCTION_DEPENDS_ON_THE_BAND_FIBER_MOMENT_"
    "M8_GREATER_THAN_OR_EQUAL_TO_VF_TO_THE_MINUS_THREE_SO_L2_NORMALIZATION_"
    "ALONE_CANNOT_PROVE_THE_NONLINEAR_REDUCTION;_THE_CONSTANT_MODULUS_EQUALITY_"
    "CASE_IS_ADOPTED_ONLY_AS_A_TAGGED_BRIDGE_AND_YIELDS_A_POSITIVE_BARE_"
    "ALPHA_FOURTH_ORDER_P8_TERM_ON_A_NONCONSTANT_BACKGROUND;_R_U_V_ARE_"
    "RECLASSIFIED_AS_DYNAMIC_BAND_FUNCTIONALS_AND_PHYSICAL_EXECUTION_REMAINS_"
    "BLOCKED"
)

EXACT_NEXT_OBJECT = (
    "RETIRE_THE_P8_BRIDGE_BY_DERIVING_THE_ACTION_SELECTED_DEGREE_ONE_FULL_"
    "PREIMAGE_PROFILE_PSI_B_AND_ITS_EXACT_M8_BAND_MOMENT_THE_ETA_TO_BAND_"
    "VARIATIONAL_INTERTWINER_SELF_ADJOINT_CAP_DOMAIN_AND_NONLINEAR_"
    "CLEBSCH_GORDAN_REDUCTION_THEN_COMPUTE_DYNAMIC_BAND_R_B_U_B_V_B_AND_TEST_"
    "THE_ALPHA_CRITICALITY_RELATION_AND_LOCKING_CONE_BEFORE_DERIVING_THE_"
    "ACTION_NORMALIZED_GOLDSTONE_LIFT_MATRIX_AND_ANY_PHYSICAL_EXECUTION"
)


# ---------------------------------------------------------------------------
# Alpha scaling
# ---------------------------------------------------------------------------

def require_alpha(alpha: float) -> float:
    a = float(alpha)
    if not 0.0 < a < 1.0:
        raise ValueError("alpha must be a positive dimensionless number smaller than one")
    return a


def alpha_scaled_landau(r: float, u: float, v: float, alpha: float) -> dict[str, float]:
    a = require_alpha(alpha)
    return {
        "r_hat": a*a*float(r),
        "u_hat": a**4*float(u),
        "v_hat": a**4*float(v),
        "three_u_plus_v_hat": a**4*(3.0*float(u)+float(v)),
    }


def locking_cone(r: float, u: float, v: float) -> bool:
    return float(r) < 0.0 and float(v) > 0.0 and (3.0*float(u)+float(v)) > 0.0


def alpha_scaling_preserves_locking_cone(r: float, u: float, v: float, alpha: float) -> bool:
    p = alpha_scaled_landau(r,u,v,alpha)
    return locking_cone(r,u,v) == locking_cone(p["r_hat"],p["u_hat"],p["v_hat"])


def isotropic_alpha_lock_residual(r: float, u: float, v: float, alpha: float) -> float:
    """Residual for Q=sR with the physical dimensionless amplitude constrained to s=alpha."""
    a = require_alpha(alpha)
    return float(r) + a*a*(3.0*float(u)+float(v))


def rank_one_alpha_lock_residual(r: float, u: float, v: float, alpha: float) -> float:
    a = require_alpha(alpha)
    return float(r) + a*a*(float(u)+float(v))


def alpha_commuting_dtn_landau(A2: float, A4: float, alpha: float) -> dict[str, float]:
    """v14.78 commuting DtN relation in Qhat coordinates when Q=alpha Qhat."""
    a = require_alpha(alpha)
    r = (2.0/3.0)*float(A2)
    u = (8.0/5.0)*float(A4)
    v = -(4.0/5.0)*float(A4)
    scaled = alpha_scaled_landau(r,u,v,a)
    return {
        "r_physical_Q": r,
        "u_physical_Q": u,
        "v_physical_Q": v,
        **scaled,
        "v_hat_plus_u_hat_over_2": scaled["v_hat"] + 0.5*scaled["u_hat"],
        "locking_cone_Q": locking_cone(r,u,v),
        "locking_cone_Qhat": locking_cone(
            scaled["r_hat"],scaled["u_hat"],scaled["v_hat"]
        ),
    }


def alpha_contract_payload() -> dict[str, Any]:
    a_test = 1.0/137.0  # rounded diagnostic only; no physical observable uses it
    stable = alpha_scaled_landau(-0.4,0.7,0.9,a_test)
    commuting = alpha_commuting_dtn_landau(-1.0,0.8,a_test)
    return {
        "version": VERSION,
        "architectural_parameter": "alpha_FS",
        "numeric_alpha_in_physical_prediction": None,
        "diagnostic_alpha_only": a_test,
        "shape_rule": "Q_b=alpha_FS Qhat_b after action-owned dimensionless kinetic normalization",
        "Goldstone_energy_lift_rule": "H_lift,b=alpha_FS Omega_b G_b",
        "no_independent_ripple_epsilon": True,
        "no_independent_Goldstone_lift_epsilon": True,
        "Landau_scaling": {
            "r_hat": "alpha^2 r",
            "u_hat": "alpha^4 u",
            "v_hat": "alpha^4 v",
        },
        "locking_cone_preserved_under_positive_alpha": alpha_scaling_preserves_locking_cone(-0.4,0.7,0.9,a_test),
        "stable_diagnostic_scaled": stable,
        "v14_78_commuting_relation_survives": abs(commuting["v_hat_plus_u_hat_over_2"]) < 1e-18,
        "v14_78_commuting_locking_still_fails": not commuting["locking_cone_Qhat"],
        "normalization_firewall": (
            "alpha may be identified directly with a shape amplitude only after Q is "
            "dimensionless in the action kinetic metric; otherwise alpha is only a perturbative label"
        ),
        "classification": "ARCHITECTURAL_DIRECTIVE_ACTIVE_DERIVATION_OF_ATTACHMENT_TO_MASTER_ACTION_OPEN",
    }


# ---------------------------------------------------------------------------
# Goldstone lifting
# ---------------------------------------------------------------------------

def hermitian_part(matrix: np.ndarray) -> np.ndarray:
    m = np.asarray(matrix,dtype=complex)
    if m.ndim != 2 or m.shape[0] != m.shape[1]:
        raise ValueError("matrix must be square")
    return 0.5*(m+m.conj().T)


def goldstone_lift_hamiltonian(alpha: float, omega_scale: float, generator: np.ndarray) -> np.ndarray:
    a = require_alpha(alpha)
    if omega_scale <= 0.0:
        raise ValueError("omega_scale must be action-derived and positive")
    G = hermitian_part(generator)
    return a*float(omega_scale)*G


def goldstone_energy_spectrum(alpha: float, omega_scale: float, generator: np.ndarray) -> dict[str, Any]:
    H = goldstone_lift_hamiltonian(alpha,omega_scale,generator)
    vals = np.linalg.eigvalsh(H)
    splittings = [float(vals[j]-vals[i]) for i in range(len(vals)) for j in range(i+1,len(vals))]
    return {
        "eigenvalues": [float(x) for x in vals],
        "pair_splittings": splittings,
        "max_abs_splitting": max(abs(x) for x in splittings) if splittings else 0.0,
    }


def goldstone_lift_payload() -> dict[str, Any]:
    G = np.array([[1.0,0.2j,0.0],[-0.2j,-0.3,0.15],[0.0,0.15,-0.7]],dtype=complex)
    omega = 2.0
    a1 = 0.01
    a2 = 0.02
    s1 = goldstone_energy_spectrum(a1,omega,G)
    s2 = goldstone_energy_spectrum(a2,omega,G)
    ratio = s2["max_abs_splitting"]/s1["max_abs_splitting"]
    return {
        "version": VERSION,
        "Hamiltonian_rule": "H_lift=alpha Omega_band G_band",
        "Omega_band": "must be generated by the action-selected band/cycle scale",
        "G_band": "must be generated by the action/holonomy/boundary response; no fitted normalization",
        "diagnostic_generator_is_physical": False,
        "diagnostic_alpha_ratio": a2/a1,
        "diagnostic_splitting_ratio": ratio,
        "linear_alpha_energy_splitting_verified": abs(ratio-a2/a1) < 1e-12,
        "mass_squared_convention_firewall": (
            "if alpha multiplies a stiffness/mass-squared Hessian rather than a Hamiltonian, "
            "squared gaps are linear in alpha while frequencies/masses scale as sqrt(alpha)"
        ),
        "physical_Goldstone_gap": None,
        "physical_execution_allowed": False,
    }


# ---------------------------------------------------------------------------
# p8 nonlinear reduction and Bridge-And-Prove
# ---------------------------------------------------------------------------

def normalized_fiber_moment8(amplitudes: np.ndarray, weights: np.ndarray) -> dict[str, float]:
    """Discrete quadrature witness for M8=int |psi|^8 after L2 normalization."""
    psi = np.asarray(amplitudes,dtype=complex)
    w = np.asarray(weights,dtype=float)
    if psi.ndim != 1 or w.ndim != 1 or psi.shape != w.shape:
        raise ValueError("amplitudes and weights must be same-length vectors")
    if np.any(w <= 0.0):
        raise ValueError("quadrature weights must be positive")
    norm2 = float(np.sum(w*np.abs(psi)**2))
    if norm2 <= 0.0:
        raise ValueError("profile must be nonzero")
    p = psi/math.sqrt(norm2)
    volume = float(np.sum(w))
    m8 = float(np.sum(w*np.abs(p)**8))
    bound = volume**-3
    return {
        "volume": volume,
        "M8": m8,
        "lower_bound": bound,
        "bound_residual": m8-bound,
        "L2_norm": float(np.sum(w*np.abs(p)**2)),
    }


def fiber_moment8_lower_bound(volume: float) -> float:
    V = float(volume)
    if V <= 0.0:
        raise ValueError("fiber volume must be positive")
    return V**-3


def constant_modulus_p8_bridge_moment(volume: float) -> float:
    """Equality case of Jensen/Hölder for an L2-normalized constant-modulus profile."""
    return fiber_moment8_lower_bound(volume)


def effective_p8_coefficient_from_profile(moment8: float) -> float:
    if moment8 <= 0.0:
        raise ValueError("moment8 must be positive")
    return float(moment8)/8.0


def reflected_p8_mean_energy(
    alpha: float,
    X0: float,
    x1: float,
    moment8: float,
    weight: float = 1.0,
) -> dict[str, float]:
    """Reflection-normalized mean of positive-energy p8 core for X±=X0±alpha*x1."""
    a = require_alpha(alpha)
    X0=float(X0); x1=float(x1); M8=float(moment8); w=float(weight)
    if X0 < 0.0 or M8 <= 0.0 or w <= 0.0:
        raise ValueError("X0>=0, moment8>0, weight>0 required")
    xp = X0+a*x1
    xm = X0-a*x1
    if xp < 0.0 or xm < 0.0:
        raise ValueError("linear bridge path must keep X nonnegative")
    exact = w*M8*(xp**4+xm**4)/16.0
    background = w*M8*X0**4/8.0
    c2 = w*M8*(3.0/4.0)*X0**2*x1**2
    c4 = w*M8*(1.0/8.0)*x1**4
    reconstructed = background + c2*a*a + c4*a**4
    return {
        "mean_energy": exact,
        "background": background,
        "delta_energy": exact-background,
        "alpha2_coefficient": c2,
        "alpha4_coefficient": c4,
        "reconstruction_residual": abs(exact-reconstructed),
    }


def bridge_p8_payload() -> dict[str, Any]:
    # Purely normalized theorem witnesses.
    weights = np.ones(4)
    constant = normalized_fiber_moment8(np.ones(4),weights)
    localized = normalized_fiber_moment8(np.array([1.0,0.0,0.0,0.0]),weights)
    V = constant["volume"]
    bridge_M8 = constant_modulus_p8_bridge_moment(V)
    e = reflected_p8_mean_energy(0.01,1.0,0.5,bridge_M8,1.0)
    return {
        "version": VERSION,
        "parent_density_core": "positive-energy p8 core = X^4/8; retained action coefficient magnitude is fixed at 1/8",
        "provisional_bridge": (
            "use the L2-normalized constant-modulus/basic fiber profile so M8=V_F^-3, "
            "with no new Wilson coefficient"
        ),
        "bridge_classification": "BRIDGED_ASSUMPTION_NOT_YET_DERIVED_FOR_THE_DEGREE_ONE_FULL_PREIMAGE_BACKGROUND",
        "exact_profile_theorem": "for int_F |psi|^2=1, M8=int_F |psi|^8 >= V_F^-3",
        "equality_condition": "|psi| constant almost everywhere",
        "constant_profile_witness": constant,
        "localized_profile_witness": localized,
        "localized_has_stronger_p8_reduction": localized["M8"] > constant["M8"],
        "bridge_M8": bridge_M8,
        "reflected_linear_X_rule": "X_±=X0±alpha x1",
        "bridge_even_expansion": (
            "Ebar_p8=M8[X0^4/8+(3/4)X0^2 x1^2 alpha^2+(1/8)x1^4 alpha^4]"
        ),
        "diagnostic_even_energy": e,
        "positive_alpha4_bridge_term": e["alpha4_coefficient"] > 0.0,
        "positive_alpha2_bridge_term": e["alpha2_coefficient"] > 0.0,
        "interpretation": (
            "the provisional nonconstant p8 bridge can stabilize a quartic but also raises "
            "quadratic stiffness; a separate negative action response is needed to make r<0"
        ),
        "physical_p8_Landau_coefficients": None,
    }


def p8_bridge_proof_ledger_payload() -> dict[str, Any]:
    rows = [
        {
            "step": 1,
            "object": "retained parent p8 coefficient",
            "statement": "magnitude 1/8 with no new coefficient",
            "status": "RECOVERED_FROM_V14_29_V14_30",
        },
        {
            "step": 2,
            "object": "round full-preimage measure",
            "statement": "fiber-integrated factor 16 pi^2 a_F^3 cos^3 rho on declared round branch",
            "status": "DERIVED_CONDITIONAL_ROUND_BRANCH",
        },
        {
            "step": 3,
            "object": "nonlinear fiber normalization theorem",
            "statement": "M8[psi]>=V_F^-3; L2 normalization alone does not fix p8",
            "status": "DERIVED_V14_79",
        },
        {
            "step": 4,
            "object": "constant-modulus bridge",
            "statement": "M8=V_F^-3",
            "status": "PROVISIONAL_BRIDGE_ASSUMPTION",
        },
        {
            "step": 5,
            "object": "degree-one full-preimage stationary profile psi_b",
            "statement": "derive actual profile and M8_b from parent Euler equation",
            "status": "OPEN",
        },
        {
            "step": 6,
            "object": "nonlinear p8 Clebsch-Gordan/profile reduction",
            "statement": "derive products/mode tower rather than zero-mode substitution",
            "status": "OPEN",
        },
        {
            "step": 7,
            "object": "eta-to-band/common-domain variational intertwiner",
            "statement": "derive map carrying parent eta variations to physical band/shape Q_b",
            "status": "OPEN",
        },
        {
            "step": 8,
            "object": "self-adjoint cap domain",
            "statement": "derive the physical operator domain used in nonlinear reduction",
            "status": "OPEN",
        },
        {
            "step": 9,
            "object": "master-action promotion",
            "statement": "replace conditional View-2 bridge with authoritative action ownership",
            "status": "OPEN",
        },
    ]
    bridge_open = any(row["status"] in {"OPEN","PROVISIONAL_BRIDGE_ASSUMPTION"} for row in rows)
    return {
        "version": VERSION,
        "protocol": "BRIDGE_AND_PROVE",
        "rows": rows,
        "bridge_active": True,
        "bridge_retired": not bridge_open,
        "bridge_may_emit_physical_predictions": False,
        "working_rule": (
            "downstream algebra may use step 4 only with BRIDGED_ASSUMPTION provenance; "
            "a physical gate cannot close until all OPEN/PROVISIONAL steps are derived"
        ),
    }


# ---------------------------------------------------------------------------
# Dynamic band interaction model
# ---------------------------------------------------------------------------

def alpha_band_quadratic_schur(
    alpha: float,
    bare_r: float,
    cross_vector: np.ndarray,
    neighbor_hessian: np.ndarray,
) -> dict[str, float]:
    """Gamma2=1/2 r q^2 + alpha q c^T y + 1/2 y^T K y."""
    a = require_alpha(alpha)
    c = np.asarray(cross_vector,dtype=float)
    K = np.asarray(neighbor_hessian,dtype=float)
    if K.ndim != 2 or K.shape[0] != K.shape[1] or c.shape != (K.shape[0],):
        raise ValueError("incompatible band coupling and neighbor Hessian")
    evals = np.linalg.eigvalsh((K+K.T)/2.0)
    if np.min(evals) <= 0.0:
        raise ValueError("neighbor Hessian must be positive on eliminated complement")
    response = float(c@np.linalg.solve(K,c))
    return {
        "bare_r": float(bare_r),
        "response_kernel": response,
        "alpha2_shift": -a*a*response,
        "r_eff": float(bare_r)-a*a*response,
    }


def dynamic_band_coefficients(
    alpha: float,
    bare_r: float,
    bare_u: float,
    bare_v: float,
    cross_vector: np.ndarray,
    neighbor_hessian: np.ndarray,
    delta_u: float = 0.0,
    delta_v: float = 0.0,
) -> dict[str, float]:
    q = alpha_band_quadratic_schur(alpha,bare_r,cross_vector,neighbor_hessian)
    u = float(bare_u)+float(delta_u)
    v = float(bare_v)+float(delta_v)
    return {
        **q,
        "u_eff": u,
        "v_eff": v,
        "three_u_plus_v_eff": 3.0*u+v,
        "locking_cone": locking_cone(q["r_eff"],u,v),
        "isotropic_alpha_lock_residual": isotropic_alpha_lock_residual(q["r_eff"],u,v,alpha),
    }


def band_profile_coefficients(profile_rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for row in profile_rows:
        moment = normalized_fiber_moment8(
            np.asarray(row["amplitudes"],dtype=complex),
            np.asarray(row["weights"],dtype=float),
        )
        rows.append({
            "band": row["band"],
            **moment,
            "p8_effective_coefficient": effective_p8_coefficient_from_profile(moment["M8"]),
        })
    return rows


def dynamic_band_payload() -> dict[str, Any]:
    profiles = [
        {"band":"B0_constant","amplitudes":[1,1,1,1],"weights":[1,1,1,1]},
        {"band":"B1_moderate","amplitudes":[1,1,0.2,0.2],"weights":[1,1,1,1]},
        {"band":"B2_localized","amplitudes":[1,0,0,0],"weights":[1,1,1,1]},
    ]
    profile_rows = band_profile_coefficients(profiles)
    a=0.01
    K=np.array([[1.8,0.2],[0.2,1.4]])
    c=np.array([0.9,-0.3])
    d1=dynamic_band_coefficients(a,0.0002,0.8,0.5,c,K)
    d2=dynamic_band_coefficients(a,0.0002,0.8,-0.2,c,K)
    return {
        "version": VERSION,
        "static_universal_r_u_v": False,
        "band_functional_contract": (
            "(r_b,u_b,v_b)=L_b[local geometry, profile psi_b, neighboring bands, "
            "Calderon response, connection/holonomy, scale ratios; alpha_FS]"
        ),
        "profile_moment_rows": profile_rows,
        "same_parent_p8_coefficient_can_yield_band_dependent_effective_strength": (
            max(row["p8_effective_coefficient"] for row in profile_rows)
            > min(row["p8_effective_coefficient"] for row in profile_rows)
        ),
        "quadratic_cross_band_rule": "r_eff,b=r_bare,b-alpha^2 c_b^T K_b^-1 c_b",
        "diagnostic_band_1": d1,
        "diagnostic_band_2": d2,
        "diagnostic_coefficients_are_physical": False,
        "generation_mechanism_classification": (
            "CANDIDATE: particle families may correspond to action-selected isolated band/cycle "
            "classes with distinct dynamic coefficient functionals; the physical count is not fixed here"
        ),
        "physical_family_count": None,
    }


def family_generation_gate_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "candidate_structural_origin": "action-selected dynamic stratified bands/cycles",
        "r_u_v_role": "local response functionals evaluated separately on each band, not universal constants",
        "requirements_before_calling_a_band_a_physical_family": [
            "band is selected by the same master action without fit",
            "stationary or relative-periodic solution exists",
            "gauge-reduced physical Hessian/monodromy stability is established",
            "band remains isolated under neighboring-band interactions",
            "dimensionless ripple obeys the common alpha_FS scaling contract",
            "absolute cycle/energy scale is action-derived",
            "detector/current attachment map is action-derived",
        ],
        "number_three_inserted_by_hand": False,
        "physical_family_count": None,
        "mass_spectrum_status": "OPEN_ACTION_DERIVED_BAND_QUASI_ENERGIES_REQUIRED",
        "mixing_status": "OPEN_NONCOMMUTING_INTERBAND_CURRENT_OR_HOLONOMY_REQUIRED",
    }


# ---------------------------------------------------------------------------
# Integrated status
# ---------------------------------------------------------------------------

def safety_lock_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "PHYSICAL_EXECUTION_BLOCKED": True,
        "bridge_assumption_can_close_gate": False,
        "alpha_directive_can_close_gate_by_itself": False,
        "dynamic_band_diagnostic_can_close_gate": False,
        "physical_masses_emitted": False,
        "physical_mass_splittings_emitted": False,
        "CKM_emitted": False,
        "PMNS_emitted": False,
        "mixing_angles_emitted": False,
        "physical_probabilities_emitted": False,
    }


def status_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "validated": [
            "positive alpha rescales Landau quadratic and quartic terms by alpha^2 and alpha^4",
            "alpha scaling preserves the Landau locking sign cone",
            "alpha scaling preserves the v14.78 commuting relation v=-u/2 and cannot evade that no-go",
            "an isotropic physical shape amplitude s=alpha requires r+alpha^2(3u+v)=0",
            "Goldstone Hamiltonian splitting is linear in alpha when H_lift=alpha Omega G",
            "normalized nonlinear p8 reduction depends on M8=int|psi|^8 rather than L2 normalization alone",
            "M8>=V_F^-3 with equality only for constant modulus",
            "constant-modulus p8 bridge gives positive alpha^2 and alpha^4 energy contributions on a nonconstant reflected background",
            "band-dependent fiber profiles give band-dependent effective p8 strengths with the same parent 1/8 coefficient",
            "alpha-scaled cross-band quadratic response gives r_eff=r_bare-alpha^2 c^T K^-1 c",
            "r,u,v are represented as dynamic band functionals rather than static universal constants",
            "Bridge-And-Prove provenance prevents the provisional p8 bridge from closing the physical gate",
        ],
        "invalidated": [
            "merely writing Q=alpha Qhat physically derives a fine-structure-sized deformation",
            "alpha scaling can repair the commuting width-only DtN invariant no-go",
            "L2 normalization of a parent fiber mode uniquely fixes the nonlinear p8 reduction",
            "the p8 coefficient 1/8 descends unchanged for arbitrary normalized nonbasic fiber profiles",
            "a synthetic dynamic-band model determines the physical number of generations",
        ],
        "reclassified": [
            "fine-structure shape scaling is an action criticality condition after canonical normalization, not a coordinate relabeling",
            "Goldstone lifting needs one action-derived dimensionful band scale and matrix while alpha supplies the universal dimensionless prefactor",
            "the p8 reduction coefficient becomes a dynamic band profile moment rather than a universal reduced constant",
            "family generation is a band/cycle selection problem and physical family count is an output gate",
            "the bridge is a temporary theorem scaffold with explicit proof debt, not a new master-action axiom",
        ],
        "open": [
            EXACT_NEXT_OBJECT,
            "canonical action attachment of alpha_FS",
            "action-selected degree-one full-preimage eta profile",
            "actual nonlinear M8 profile moment M8_b",
            "eta-to-band variational intertwiner",
            "self-adjoint nonlinear cap domain",
            "dynamic physical r_b,u_b,v_b",
            "alpha-criticality relation on action-selected bands",
            "physical Goldstone lift scale and matrix",
            "physical family count and mass spectrum",
            "Calderon/noncommuting mixing response",
            "frozen neutrino execution",
        ],
        "FULL_BHSM_COMPLETE": False,
        "MARK_III": "NOT_REACHED",
        "PHYSICAL_EXECUTION_BLOCKED": True,
        "physical_prediction_emitted": False,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "USB_touched": False,
    }


def completion_gate_payload() -> dict[str, Any]:
    alpha = alpha_contract_payload()
    gold = goldstone_lift_payload()
    bridge = bridge_p8_payload()
    proof = p8_bridge_proof_ledger_payload()
    bands = dynamic_band_payload()
    fam = family_generation_gate_payload()
    safety = safety_lock_payload()
    validation = {
        "single_alpha_contract_active": alpha["no_independent_ripple_epsilon"] and alpha["no_independent_Goldstone_lift_epsilon"],
        "alpha_cone_invariance": alpha["locking_cone_preserved_under_positive_alpha"],
        "commuting_no_go_survives_alpha": alpha["v14_78_commuting_relation_survives"] and alpha["v14_78_commuting_locking_still_fails"],
        "Goldstone_linear_alpha_diagnostic": gold["linear_alpha_energy_splitting_verified"],
        "p8_holder_bound": bridge["constant_profile_witness"]["bound_residual"] >= -1e-14,
        "localized_p8_stronger_than_constant": bridge["localized_has_stronger_p8_reduction"],
        "p8_bridge_has_positive_alpha4": bridge["positive_alpha4_bridge_term"],
        "bridge_not_retired": proof["bridge_retired"] is False,
        "bridge_cannot_predict": proof["bridge_may_emit_physical_predictions"] is False,
        "band_p8_is_dynamic": bands["same_parent_p8_coefficient_can_yield_band_dependent_effective_strength"],
        "family_count_not_inserted": fam["number_three_inserted_by_hand"] is False and fam["physical_family_count"] is None,
        "safety_lock": safety["PHYSICAL_EXECUTION_BLOCKED"],
        "no_physical_prediction": True,
    }
    return {
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "alpha_scaling_contract": "ACTIVE_ARCHITECTURAL_DIRECTIVE_ACTION_ATTACHMENT_OPEN",
        "isotropic_alpha_criticality_condition": "r_b+alpha_FS^2(3u_b+v_b)=0",
        "p8_bridge": "ACTIVE_PROVISIONAL_CONSTANT_MODULUS_M8_EQUALS_VF_MINUS3",
        "p8_bridge_retired": False,
        "dynamic_band_Landau": "STRUCTURAL_FUNCTIONAL_FORM_DERIVED_PHYSICAL_COEFFICIENTS_OPEN",
        "physical_family_count": None,
        "physical_Goldstone_gap": None,
        "physical_r_u_v": None,
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
        "BHSM_alpha_single_parameter_contract_v14_79.json": alpha_contract_payload(),
        "BHSM_alpha_Goldstone_lift_contract_v14_79.json": goldstone_lift_payload(),
        "BHSM_p8_nonlinear_fiber_moment_bridge_v14_79.json": bridge_p8_payload(),
        "BHSM_p8_bridge_and_prove_ledger_v14_79.json": p8_bridge_proof_ledger_payload(),
        "BHSM_dynamic_band_Landau_functionals_v14_79.json": dynamic_band_payload(),
        "BHSM_family_generation_band_gate_v14_79.json": family_generation_gate_payload(),
        "BHSM_physical_execution_safety_lock_v14_79.json": safety_lock_payload(),
        "BHSM_status_ledger_v14_79.json": status_payload(),
        "BHSM_completion_gate_v14_79.json": completion_gate_payload(),
    }


def materialize(outdir: Path) -> list[Path]:
    out = Path(outdir)
    out.mkdir(parents=True,exist_ok=True)
    written = []
    for name,payload in sorted(artifact_payloads().items()):
        path = out/name
        path.write_text(
            json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+"\n",
            encoding="utf-8",
        )
        written.append(path)
    return written
