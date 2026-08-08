"""BHSM v14.81 driven hypersphere, black-hole flux, and dynamic-locking gate.

Strategic question
------------------
Can black-hole activity be used as the physical engine that prevents a
hyperspherical BHSM background from settling into the static round branch and
instead drives dynamic bands through the alpha-scaled three-channel locking
transition?

v14.81 separates what is supported by standard GR, what is structurally
allowed in BHSM, and what remains an unproved BHSM-specific coupling.

Core results
------------
1. Dynamic baseline:
   The exact round background is retained as a reference geometry for harmonic
   decompositions and comparison theorems, not promoted to the physical vacuum.
   This changes the physical stability question from a static Hessian minimum to
   stability of a driven/relative-periodic orbit.

2. Covariant energy-transfer firewall:
   In a diffeomorphism-invariant closed theory, a "black-hole energy injection"
   into a boundary/band sector must be an exchange term,
       nabla_mu T_BH^{mu nu} = -Q^nu,
       nabla_mu T_band^{mu nu} = +Q^nu,
   so total stress-energy remains covariantly conserved.  It is redistribution,
   not energy creation.

3. GR expansion sign gate:
   For a timelike congruence,
       dot(theta) = -theta^2/3 - sigma^2 + omega^2
                    - R_mn u^m u^n + div(a).
   With geodesic, irrotational flow and Einstein gravity,
       R_uu = 4 pi G (rho+3p) - Lambda
   for a perfect fluid.  Ordinary positive-energy injection with
   rho+3p >= 0 focuses rather than generically defocuses.  Black-hole activity
   therefore does not, by itself, prove local spacetime expansion in standard GR.

4. Horizon-flux distinction:
   Positive flux into a dynamical horizon increases horizon area; jets/outflows
   can carry energy outward into the environment.  Neither statement is the same
   as a universal positive local expansion scalar or a cosmological
   de-enveloping source.

5. Reflection selection:
   The ell=2 order parameter is odd under equal-cap exchange Q -> -Q.
   A scalar black-hole activity measure D_BH is even.  A linear term D_BH Q
   explicitly breaks the reflection symmetry; the leading reflection-preserving
   coupling is parametric,
       V_drive = -(1/2) chi_b D_BH I2(Q),
   giving
       r_eff,b = r_0,b - chi_b D_BH.
   The sign and normalization of chi_b are NOT fixed by symmetry and must be
   derived from the BHSM master action.

6. Alpha-critical driven crossing:
   If the physical locked amplitude is Q=alpha R, the crossing condition is
       r_0,b - chi_b D_BH + alpha^2(3u_b+v_b) = 0.
   A black-hole drive can only solve the stability problem if the action derives
   chi_b D_BH with the required sign and magnitude while v_b>0 and 3u_b+v_b>0.

7. Additive forcing is not criticality:
   A source term -J_b(t):Q shifts the driven solution but does not change the
   homogeneous Hessian/monodromy.  It cannot by itself turn r positive into r
   negative.  Genuine criticality requires parametric coefficient modulation or
   a background response that changes the variational operator.

8. Dynamic stability:
   For periodic backgrounds the physical criterion is the Floquet/monodromy
   spectrum of the homogeneous linearized operator after gauge/Goldstone
   quotient.  Static H>0 is no longer the final physical gate, but a source term
   cannot be used to bypass stability without deriving the monodromy.

Public-literature context used by the accompanying report:
- dynamical-horizon flux laws: positive energy flux changes black-hole area;
- evolving black-hole backgrounds can nonlinearly excite additional modes;
- black holes in expanding cosmological backgrounds need not be exactly static;
- proposals that black holes source dark energy/cosmic expansion exist but are
  contested and observationally constrained.

No physical BHSM chi_b, drive power, family count, mass, splitting, CKM, PMNS,
mixing angle, or probability is emitted.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

VERSION = "v14.81"

PRIMARY_VERDICT = (
    "BHSM_V14_81_THE_DYNAMIC_HYPERSPHERICAL_BASELINE_IS_STRUCTURALLY_ALLOWED_"
    "AND_STATIC_ROUNDNESS_IS_RETAINED_ONLY_AS_A_REFERENCE_BRANCH_BUT_STANDARD_"
    "GR_DOES_NOT_SUPPORT_THE_STRONGER_CLAIM_THAT_ORDINARY_BLACK_HOLE_ACTIVITY_"
    "GENERALLY_PRODUCES_LOCAL_SPACETIME_DEFOCUSING_OR_COSMIC_DE_ENVELOPING;_"
    "RAYCHAUDHURI_FOCUSING_SHOWS_POSITIVE_ENERGY_WITH_RHO_PLUS_3P_NONNEGATIVE_"
    "TENDS_TO_REDUCE_EXPANSION_WHILE_DYNAMICAL_HORIZON_AREA_GROWTH_AND_AGN_"
    "OUTFLOWS_ARE_ENERGY_TRANSFER_NOT_UNIVERSAL_METRIC_EXPANSION;_WITHIN_BHSM_"
    "A_REFLECTION_EVEN_BLACK_HOLE_ACTIVITY_SCALAR_CAN_SHIFT_THE_ELL2_"
    "CRITICALITY_ONLY_THROUGH_AN_ACTION_DERIVED_PARAMETRIC_SUSCEPTIBILITY_CHI_"
    "B_GIVING_R_EFF_EQUALS_R0_MINUS_CHI_B_D_BH_AND_THE_ALPHA_LOCKING_CROSSING_"
    "R0_MINUS_CHI_B_D_BH_PLUS_ALPHA_SQUARED_TIMES_3U_PLUS_V_EQUALS_ZERO;_THE_"
    "SIGN_OF_CHI_B_IS_NOT_FIXED_BY_SYMMETRY_SO_BLACK_HOLE_DRIVEN_LOCKING_"
    "REMAINS_A_BRIDGED_HYPOTHESIS_NOT_A_DERIVED_RESULT"
)

EXACT_NEXT_OBJECT = (
    "DERIVE_THE_BLACK_HOLE_TO_BAND_PARAMETRIC_SUSCEPTIBILITY_CHI_B_FROM_THE_"
    "MASTER_ACTION_BY_LINEAR_RESPONSE_OF_THE_DYNAMIC_FULL_PREIMAGE_BACKGROUND_"
    "TO_A_CONSERVATION_CONSISTENT_HORIZON_JET_OR_ACCRETION_FLUX_SOURCE_THEN_"
    "PROJECT_THE_RESPONSE_ONTO_ELL2_DYNAMIC_BANDS_COMPUTE_R_B_T_U_B_T_V_B_T_"
    "AND_THE_GAUGE_REDUCED_FLOQUET_MONODROMY_AND_TEST_THE_ALPHA_CRITICALITY_"
    "CROSSING_WITHOUT_USING_ADDITIVE_FORCING_AS_A_STABILITY_SHORTCUT"
)

# ---------------------------------------------------------------------------
# Raychaudhuri / GR sign gate
# ---------------------------------------------------------------------------

def raychaudhuri_theta_dot(
    theta: float,
    shear_sq: float,
    vorticity_sq: float,
    R_uu: float,
    acceleration_divergence: float = 0.0,
) -> float:
    if shear_sq < 0 or vorticity_sq < 0:
        raise ValueError("squared kinematical invariants must be nonnegative")
    return (
        -(float(theta) ** 2) / 3.0
        - float(shear_sq)
        + float(vorticity_sq)
        - float(R_uu)
        + float(acceleration_divergence)
    )


def perfect_fluid_Ruu(
    rho: float,
    pressure: float,
    G: float = 1.0,
    Lambda: float = 0.0,
) -> float:
    """R_ab u^a u^b = 4 pi G (rho+3p) - Lambda for signature -+++."""
    return 4.0 * math.pi * float(G) * (float(rho) + 3.0 * float(pressure)) - float(Lambda)


def geodesic_irrotational_theta_dot(
    theta: float,
    shear_sq: float,
    rho: float,
    pressure: float,
    G: float = 1.0,
    Lambda: float = 0.0,
) -> float:
    Ruu = perfect_fluid_Ruu(rho, pressure, G, Lambda)
    return raychaudhuri_theta_dot(theta, shear_sq, 0.0, Ruu, 0.0)


def gr_defocusing_gate_payload() -> dict[str, Any]:
    dust = geodesic_irrotational_theta_dot(0.1, 0.02, 0.3, 0.0, 1.0, 0.0)
    radiation = geodesic_irrotational_theta_dot(0.1, 0.02, 0.3, 0.1, 1.0, 0.0)
    vacuum_energy = geodesic_irrotational_theta_dot(0.1, 0.02, 0.3, -0.3, 1.0, 0.0)
    return {
        "version": VERSION,
        "equation": (
            "dot(theta)=-theta^2/3-sigma^2+omega^2-R_uu+div(a)"
        ),
        "Einstein_perfect_fluid": "R_uu=4 pi G (rho+3p)-Lambda",
        "strong_energy_condition_gate": "rho+3p>=0 with omega=0, a=0 gives focusing contribution -R_uu<=0 for Lambda=0",
        "diagnostic_theta_dots": {
            "dust": dust,
            "radiation_like": radiation,
            "negative_pressure": vacuum_energy,
        },
        "dust_defocuses": dust > 0.0,
        "radiation_like_defocuses": radiation > 0.0,
        "negative_pressure_can_defocus": vacuum_energy > 0.0,
        "black_hole_positive_energy_injection_generically_implies_local_expansion_in_GR": False,
        "required_escape_classes": [
            "effective negative pressure / strong-energy-condition violation",
            "non-geodesic acceleration divergence",
            "vorticity",
            "modified gravitational field equations",
            "BHSM-specific geometry-to-band susceptibility with derived sign",
        ],
        "physical_prediction": False,
    }


# ---------------------------------------------------------------------------
# Covariant energy transfer
# ---------------------------------------------------------------------------

def conserved_exchange_residual(q_bh: np.ndarray, q_band: np.ndarray) -> float:
    a = np.asarray(q_bh, dtype=float)
    b = np.asarray(q_band, dtype=float)
    if a.shape != b.shape:
        raise ValueError("exchange vectors must have same shape")
    return float(np.linalg.norm(a + b))


def exchange_power_balance(
    E_bh_dot: float,
    E_band_dot: float,
    transport_loss: float = 0.0,
    relaxation_loss: float = 0.0,
) -> float:
    """Residual of closed-sector energy balance."""
    return float(E_bh_dot) + float(E_band_dot) + float(transport_loss) + float(relaxation_loss)


def energy_exchange_payload() -> dict[str, Any]:
    q = np.array([0.3, -0.2, 0.1, 0.4])
    residual = conserved_exchange_residual(-q, q)
    # Diagnostic closed budget: BH loses 2, band gains 1.3, 0.4 transported, 0.3 relaxed.
    budget = exchange_power_balance(-2.0, 1.3, 0.4, 0.3)
    return {
        "version": VERSION,
        "covariant_split": [
            "nabla_mu T_BH^{mu nu}=-Q^nu",
            "nabla_mu T_band^{mu nu}=+Q^nu",
            "nabla_mu(T_BH+T_band)^{mu nu}=0",
        ],
        "exchange_vector_residual": residual,
        "closed_energy_budget_residual": budget,
        "interpretation": (
            "black-hole injection is sector-to-sector transfer in a closed diffeomorphism-invariant theory, not net creation of energy"
        ),
        "gravitational_energy_localization_firewall": (
            "in GR geometry is not represented by a unique local gravitational stress tensor; a BHSM band-energy balance must come from its own action variables"
        ),
        "physical_Q_BH_to_band": None,
    }


# ---------------------------------------------------------------------------
# Reflection selection and driven Landau criticality
# ---------------------------------------------------------------------------

def reflection_allowed_couplings_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "transformations": {
            "Q": "odd under equal-cap exchange",
            "I2(Q)": "even",
            "D_BH_scalar_activity": "even",
        },
        "couplings": [
            {
                "term": "-D_BH <J,Q>",
                "parity": "odd unless J is itself reflection-odd",
                "status": "EXPLICIT_REFLECTION_BREAKING_FOR_SCALAR_ACTIVITY",
                "effect": "additive forcing / bias",
            },
            {
                "term": "-(1/2) chi_b D_BH I2(Q)",
                "parity": "even",
                "status": "LEADING_REFLECTION_PRESERVING_PARAMETRIC_COUPLING",
                "effect": "r_eff=r0-chi_b D_BH",
            },
            {
                "term": "-chi4_b D_BH I4(Q)",
                "parity": "even",
                "status": "ALLOWED_HIGHER_ORDER",
                "effect": "quartic coefficient modulation",
            },
        ],
        "symmetry_fixes_sign_of_chi_b": False,
        "symmetry_fixes_magnitude_of_chi_b": False,
        "physical_chi_b": None,
    }


def driven_r_eff(r0: float, chi: float, drive: float) -> float:
    return float(r0) - float(chi) * float(drive)


def alpha_critical_residual(
    r0: float,
    chi: float,
    drive: float,
    alpha: float,
    u: float,
    v: float,
) -> float:
    if not 0.0 < float(alpha) < 1.0:
        raise ValueError("alpha must lie in (0,1)")
    return driven_r_eff(r0, chi, drive) + float(alpha) ** 2 * (3.0 * float(u) + float(v))


def critical_drive_for_alpha_lock(
    r0: float,
    chi: float,
    alpha: float,
    u: float,
    v: float,
) -> float:
    if chi == 0.0:
        raise ValueError("chi must be nonzero")
    if not 0.0 < float(alpha) < 1.0:
        raise ValueError("alpha must lie in (0,1)")
    return (float(r0) + float(alpha) ** 2 * (3.0 * float(u) + float(v))) / float(chi)


def locking_cone(r: float, u: float, v: float) -> bool:
    return float(r) < 0.0 and float(v) > 0.0 and (3.0 * float(u) + float(v)) > 0.0


def parametric_drive_payload() -> dict[str, Any]:
    # Synthetic theorem witness only.
    r0 = 0.2
    u = 1.0
    v = 0.5
    alpha = 0.01
    chi = 0.8
    dstar = critical_drive_for_alpha_lock(r0, chi, alpha, u, v)
    reff = driven_r_eff(r0, chi, dstar)
    residual = alpha_critical_residual(r0, chi, dstar, alpha, u, v)
    return {
        "version": VERSION,
        "parametric_rule": "r_eff,b=r0,b-chi_b D_BH",
        "alpha_criticality": "r_eff,b+alpha^2(3u_b+v_b)=0",
        "diagnostic_parameters_are_physical": False,
        "diagnostic": {
            "r0": r0,
            "u": u,
            "v": v,
            "alpha": alpha,
            "chi": chi,
            "critical_drive": dstar,
            "r_eff_at_crossing": reff,
            "residual": residual,
            "locking_cone_at_crossing": locking_cone(reff, u, v),
        },
        "chi_sign_derived_from_master_action": False,
        "physical_critical_drive": None,
        "conclusion": (
            "a scalar BH activity variable can drive alpha-criticality only if an action-derived parametric susceptibility has the required sign"
        ),
    }


# ---------------------------------------------------------------------------
# Additive forcing vs true instability
# ---------------------------------------------------------------------------

def static_forced_equilibrium(r: float, source: float) -> float:
    if r == 0.0:
        raise ValueError("linear equilibrium is singular at r=0")
    return float(source) / float(r)


def additive_forcing_hessian(r: float) -> float:
    """For V=1/2 r q^2 - J q, d2V/dq2=r."""
    return float(r)


def additive_force_firewall_payload() -> dict[str, Any]:
    r = 2.0
    sources = [0.0, 1.0, 5.0, -3.0]
    rows = []
    for J in sources:
        rows.append({
            "J": J,
            "equilibrium_q": static_forced_equilibrium(r, J),
            "Hessian": additive_forcing_hessian(r),
        })
    return {
        "version": VERSION,
        "model": "V(q)=r q^2/2-J(t) q",
        "rows": rows,
        "Hessian_independent_of_additive_source": all(row["Hessian"] == r for row in rows),
        "additive_source_can_change_sign_of_r": False,
        "interpretation": (
            "additive forcing can maintain a nonzero driven deformation but is not equivalent to a phase-transition instability"
        ),
        "required_for_true_criticality": "parametric/background coupling that changes the homogeneous variational operator",
    }


# ---------------------------------------------------------------------------
# Floquet/monodromy diagnostic
# ---------------------------------------------------------------------------

def _rk4_step(Afunc, t: float, Y: np.ndarray, h: float) -> np.ndarray:
    k1 = Afunc(t) @ Y
    k2 = Afunc(t + 0.5*h) @ (Y + 0.5*h*k1)
    k3 = Afunc(t + 0.5*h) @ (Y + 0.5*h*k2)
    k4 = Afunc(t + h) @ (Y + h*k3)
    return Y + h*(k1 + 2*k2 + 2*k3 + k4)/6.0


def monodromy_matrix(
    r0: float,
    modulation: float,
    omega: float,
    damping: float,
    period_count: int = 1,
    steps_per_period: int = 4000,
) -> np.ndarray:
    """Linear q''+gamma q'+[r0-modulation cos(omega t)]q=0."""
    if omega <= 0 or steps_per_period < 100:
        raise ValueError("omega>0 and sufficient steps required")
    T = 2.0*math.pi/float(omega)
    total_T = int(period_count)*T
    h = T/steps_per_period
    steps = int(period_count)*steps_per_period

    def A(t):
        stiffness = float(r0) - float(modulation)*math.cos(float(omega)*t)
        return np.array([[0.0,1.0],[-stiffness,-float(damping)]],dtype=float)

    Y = np.eye(2)
    t = 0.0
    for _ in range(steps):
        Y = _rk4_step(A,t,Y,h)
        t += h
    return Y


def floquet_multipliers(**kwargs) -> np.ndarray:
    return np.linalg.eigvals(monodromy_matrix(**kwargs))


def floquet_payload() -> dict[str, Any]:
    stable = floquet_multipliers(r0=1.0, modulation=0.1, omega=2.7, damping=0.1, steps_per_period=1800)
    unstable = floquet_multipliers(r0=1.0, modulation=0.8, omega=2.0, damping=0.0, steps_per_period=1800)
    return {
        "version": VERSION,
        "equation": "q_ddot+gamma q_dot+[r0-d cos(omega t)]q=0",
        "stable_diagnostic_moduli": [float(abs(x)) for x in stable],
        "unstable_diagnostic_moduli": [float(abs(x)) for x in unstable],
        "stable_witness": bool(max(abs(x) for x in stable) < 1.0),
        "parametric_instability_witness": bool(max(abs(x) for x in unstable) > 1.0),
        "diagnostic_parameters_are_physical": False,
        "physical_rule": (
            "driven BHSM branch stability must use gauge/Goldstone-reduced monodromy/Floquet multipliers on the action-selected periodic background"
        ),
        "static_Hessian_alone_is_final_dynamic_gate": False,
    }


# ---------------------------------------------------------------------------
# Evidence / classification ledger
# ---------------------------------------------------------------------------

def black_hole_evidence_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "supported_by_standard_GR_or_astrophysics": [
            "dynamical black holes exchange positive energy/angular-momentum flux across horizons and horizon area changes",
            "black-hole mergers/ringdown are genuinely nonequilibrium and evolving backgrounds can excite additional modes",
            "AGN accretion/jet systems transfer substantial energy and momentum into surrounding matter",
            "an exactly static isolated black-hole idealization need not remain valid in a time-dependent cosmological embedding",
        ],
        "not_established_as_standard_GR_fact": [
            "black-hole activity generically produces positive local spacetime expansion scalar",
            "black holes generically de-envelope the cosmological hypersurface",
            "ordinary positive black-hole energy flux automatically drives r_b negative",
            "black-hole populations are established as the source of cosmic acceleration/dark energy",
        ],
        "contested_public_research_direction": (
            "cosmologically coupled black-hole models have been proposed as a dark-energy source, "
            "while stellar-binary and merger-population studies place substantial constraints on strong coupling"
        ),
        "BHSM_bridge_hypothesis": (
            "black-hole/accretion/horizon activity sources an action-owned dynamic background response whose "
            "ell2 projection changes r_b,u_b,v_b and can maintain a nonequilibrium locked phase"
        ),
        "bridge_hypothesis_status": "OPEN_SIGN_AND_NORMALIZATION",
    }


def research_verdict_payload() -> dict[str, Any]:
    gr = gr_defocusing_gate_payload()
    param = parametric_drive_payload()
    return {
        "version": VERSION,
        "question": "does black-hole activity resolve the BHSM static-round stability problem?",
        "answer": "NOT_BY_STANDARD_GR_ENERGY_INJECTION_ALONE; POSSIBLE_ONLY_AS_AN_ACTION_DERIVED_DYNAMIC_PARAMETRIC_RESPONSE",
        "dynamic_baseline": "VALID_AS_WORKING_PHYSICAL_ARCHITECTURE",
        "static_round_branch": "REFERENCE_AND_KILL_SCREEN_ONLY_NOT_ASSUMED_PHYSICAL_VACUUM",
        "black_hole_activity_as_nonequilibrium_driver": "PLAUSIBLE_STRUCTURAL_SOURCE",
        "black_hole_activity_as_generic_local_expansion_source": "NOT_DERIVED_AND_NOT_GENERIC_IN_GR",
        "GR_positive_energy_defocusing_gate": gr["black_hole_positive_energy_injection_generically_implies_local_expansion_in_GR"],
        "BHSM_parametric_escape": param["parametric_rule"],
        "required_new_derived_object": "chi_b = delta r_b / delta D_BH from the master action",
        "physical_chi_b": None,
        "physical_execution_allowed": False,
    }


def status_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "validated": [
            "dynamic backgrounds are compatible with the framework while round geometry remains an exact reference branch",
            "covariant black-hole-to-band injection must be energy redistribution in a closed diffeomorphism-invariant theory",
            "Raychaudhuri focusing prevents ordinary positive-energy injection from being identified generically with local spacetime expansion",
            "dynamical-horizon area growth is distinct from cosmic or local congruence expansion",
            "black-hole nonequilibrium activity can legitimately act as a time-dependent environmental source",
            "reflection-even scalar activity cannot linearly couple to odd Q without explicit symmetry breaking",
            "the leading reflection-preserving scalar activity coupling is parametric in I2",
            "parametric activity shifts r_eff=r0-chi_b D_BH",
            "the alpha-locked driven crossing is r0-chi_b D_BH+alpha^2(3u+v)=0",
            "symmetry does not determine the sign of chi_b",
            "additive forcing does not change the Hessian and cannot be used as a criticality shortcut",
            "periodic driven stability is a Floquet/monodromy problem rather than a static-Hessian-only problem",
        ],
        "invalidated": [
            "ordinary black-hole positive energy flux by itself proves local de-enveloping in standard GR",
            "horizon area growth is equivalent to expansion of surrounding spacetime",
            "a linear external source can turn positive r into negative r without modifying the homogeneous operator",
            "the static round r>0 theorem can simply be discarded rather than retained as a reference-branch restoring term",
            "black-hole driving may be assumed to have the desired sign without deriving chi_b",
        ],
        "reclassified": [
            "the static round result is an elastic/reference contribution rather than the full physical r_b",
            "black-hole activity is a candidate nonequilibrium environment/parametric driver, not yet a derived expansion engine",
            "the core stability problem becomes action-derived driven criticality plus Floquet stability",
            "the BH de-enveloping concept is a Bridge-And-Prove hypothesis whose sign must emerge from master-action response",
        ],
        "open": [
            EXACT_NEXT_OBJECT,
            "master-action derivation of chi_b",
            "conservation-consistent physical BH/accretion/jet source D_BH",
            "dynamic full-preimage stationary or relative-periodic background",
            "ell2 projection of source-induced metric/field response",
            "dynamic r_b(t),u_b(t),v_b(t)",
            "gauge/Goldstone-reduced Floquet monodromy",
            "action attachment of alpha_FS",
            "physical family count/mass spectrum",
            "physical Goldstone lifting",
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
    gr = gr_defocusing_gate_payload()
    ex = energy_exchange_payload()
    ref = reflection_allowed_couplings_payload()
    par = parametric_drive_payload()
    add = additive_force_firewall_payload()
    floq = floquet_payload()
    evidence = black_hole_evidence_payload()
    verdict = research_verdict_payload()
    validation = {
        "ordinary_dust_not_defocusing": gr["dust_defocuses"] is False,
        "ordinary_radiation_not_defocusing": gr["radiation_like_defocuses"] is False,
        "negative_pressure_can_defocus_witness": gr["negative_pressure_can_defocus"] is True,
        "covariant_exchange_closes": ex["exchange_vector_residual"] < 1e-14 and abs(ex["closed_energy_budget_residual"]) < 1e-14,
        "reflection_parametric_coupling_allowed": ref["couplings"][1]["status"] == "LEADING_REFLECTION_PRESERVING_PARAMETRIC_COUPLING",
        "chi_sign_not_assumed": ref["symmetry_fixes_sign_of_chi_b"] is False,
        "alpha_crossing_exact": abs(par["diagnostic"]["residual"]) < 1e-12,
        "additive_force_hessian_firewall": add["Hessian_independent_of_additive_source"] is True,
        "floquet_stable_witness": floq["stable_witness"],
        "floquet_instability_witness": floq["parametric_instability_witness"],
        "strong_BH_expansion_claim_not_promoted": evidence["bridge_hypothesis_status"] == "OPEN_SIGN_AND_NORMALIZATION",
        "research_verdict_fail_closed": verdict["physical_execution_allowed"] is False,
        "no_physical_prediction": True,
    }
    return {
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "dynamic_background_baseline": "ACTIVE_REFERENCE_ROUND_ONLY",
        "black_hole_nonequilibrium_driver": "STRUCTURALLY_PLAUSIBLE",
        "black_hole_generic_GR_deenveloping": "NOT_DERIVED",
        "BHSM_black_hole_drive": "BRIDGED_HYPOTHESIS_REQUIRES_ACTION_DERIVED_CHI_B",
        "alpha_driven_criticality": "r0-chi_b D_BH+alpha^2(3u+v)=0",
        "physical_chi_b": None,
        "physical_drive_power": None,
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
        "BHSM_GR_Raychaudhuri_black_hole_defocusing_gate_v14_81.json": gr_defocusing_gate_payload(),
        "BHSM_covariant_black_hole_band_energy_exchange_v14_81.json": energy_exchange_payload(),
        "BHSM_black_hole_drive_reflection_selection_v14_81.json": reflection_allowed_couplings_payload(),
        "BHSM_alpha_parametric_black_hole_criticality_v14_81.json": parametric_drive_payload(),
        "BHSM_additive_forcing_criticality_firewall_v14_81.json": additive_force_firewall_payload(),
        "BHSM_dynamic_Floquet_monodromy_gate_v14_81.json": floquet_payload(),
        "BHSM_black_hole_public_evidence_ledger_v14_81.json": black_hole_evidence_payload(),
        "BHSM_black_hole_dynamic_baseline_research_verdict_v14_81.json": research_verdict_payload(),
        "BHSM_status_ledger_v14_81.json": status_payload(),
        "BHSM_completion_gate_v14_81.json": completion_gate_payload(),
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
