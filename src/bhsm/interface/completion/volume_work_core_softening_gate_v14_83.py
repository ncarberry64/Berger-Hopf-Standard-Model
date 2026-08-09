"""BHSM v14.83 conservation-consistent volume-work source and core-softening gate.

Mission
-------
v14.82 derived the exact black-hole/environment susceptibility

    chi = C - DR[K^-1 b].

v14.83 constructs the minimal reflection-even dilation/work bridge on the
existing v10/v14.68 radial core and derives a clean sign theorem.

Core branch
-----------
The archived radial truncation has

    V0(R) = a R^5 + b/R,      a,b>0,
    M(R)  = d R^5 + e/R,      d,e>0,

with stationary radius

    R_*^6 = b/(5a).

The local breathing stiffness is

    h(R) = V0''(R)/M(R).

A conservation-compatible coarse-grained outward work source enters as

    V_D(R) = V0(R) - D B0(R),

where D is the generalized outward stress/activity variable and B0'(R_*)>0.
The leading isotropic volume-work normal form in seven spatial dimensions is

    B0(R) proportional to R^7.

This is a Bridge-And-Prove source normal form, not yet an action-owned black-
hole functional.

Exact theorem
-------------
Stationarity gives

    R'_D|0 = B0'(R_*) / V0''(R_*).

Define the p2 share of the radial kinetic inertia at R_*,

    zeta = d R_*^5 / M(R_*),       0<zeta<1.

At the stationary point,

    h'(R_*) / h(R_*) = 2(1-3 zeta)/R_*.

Therefore the outward-drive susceptibility of the core stiffness is

    chi_h = - dh/dD
          = 2(3 zeta-1) B0'(R_*) / [R_* M(R_*)].

Hence, for B0'(R_*)>0,

    chi_h > 0  iff  zeta > 1/3,
    chi_h = 0  iff  zeta = 1/3,
    chi_h < 0  iff  zeta < 1/3.

For the seven-volume bridge B0=R^7,

    chi_h = 14 R_*^5 (3 zeta-1)/M(R_*).

Because the v11.4 lower attachment root mu_-(h,k) is strictly increasing in h
and k for h,k>0, if k is held fixed then

    chi_mu = (d mu_-/dh) chi_h,

so the same zeta=1/3 sign threshold carries into the attachment root.

Physical interpretation
-----------------------
The source D is NOT raw black-hole energy density.  Under a dilation, the
quantity conjugate to volume is a pressure/work or spatial-stress trace.
Positive energy density alone does not imply B0'(R)>0 in the required
effective potential convention.  The BH/accretion/jet sector must derive the
effective outward stress and its normalization.

No physical D_BH, zeta, chi, mass, splitting, CKM, PMNS, or mixing angle is
emitted.  PHYSICAL_EXECUTION_BLOCKED remains active.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

VERSION = "v14.83"

PRIMARY_VERDICT = (
    "BHSM_V14_83_THE_MINIMAL_REFLECTION_EVEN_OUTWARD_VOLUME_WORK_BRIDGE_ON_THE_"
    "EXISTING_RADIAL_CORE_GIVES_AN_EXACT_CORE_SOFTENING_SUSCEPTIBILITY_CHI_H_"
    "EQUALS_TWO_TIMES_THREE_ZETA_MINUS_ONE_TIMES_B0_PRIME_OVER_R_STAR_M_STAR_"
    "WITH_ZETA_THE_P2_SHARE_OF_RADIAL_KINETIC_INERTIA;_FOR_OUTWARD_B0_PRIME_"
    "POSITIVE_THE_BLACK_HOLE_ENVIRONMENT_DRIVE_SOFTENS_THE_CORE_IF_AND_ONLY_IF_"
    "ZETA_EXCEEDS_ONE_THIRD_AND_STIFFENS_IT_IF_ZETA_IS_BELOW_ONE_THIRD;_THE_"
    "SAME_SIGN_TRANSFERS_TO_THE_V11_4_LOWER_ATTACHMENT_ROOT_WHEN_K_D_IS_FIXED_"
    "BECAUSE_DMU_MINUS_DH_IS_POSITIVE;_THE_CURRENT_ARCHIVED_CORE_DATA_DO_NOT_"
    "FIX_ZETA_OR_AN_ACTION_OWNED_BH_OUTWARD_STRESS_SO_THE_PHYSICAL_SIGN_REMAINS_"
    "OPEN_BUT_THE_DRIVER_NOW_HAS_A_SHARP_NO_FIT_THRESHOLD"
)

EXACT_NEXT_OBJECT = (
    "RECOVER_OR_DERIVE_THE_ACTION_SELECTED_RADIAL_KINETIC_PARTITION_D_R5_AND_"
    "E_OVER_R_ON_THE_DYNAMIC_FULL_PREIMAGE_BACKGROUND_AND_DERIVE_THE_OUTWARD_"
    "BH_ACCRETION_JET_STRESS_TRACE_SOURCE_FROM_A_CONSERVED_SECTOR_ACTION_THEN_"
    "EVALUATE_ZETA_AND_B0_PRIME_COMPUTE_CHI_H_AND_CHI_ATTACHMENT_WITH_K_D_"
    "RESPONSE_INCLUDED_AND_TEST_ALPHA_CRITICALITY_AND_FLOQUET_STABILITY"
)


# ---------------------------------------------------------------------------
# Radial core
# ---------------------------------------------------------------------------

def stationary_radius(a: float, b: float) -> float:
    a=float(a); b=float(b)
    if a<=0 or b<=0:
        raise ValueError("a,b must be positive")
    return (b/(5.0*a))**(1.0/6.0)


def core_potential(R: float, a: float, b: float) -> float:
    R=float(R)
    if R<=0: raise ValueError("R>0")
    return float(a)*R**5 + float(b)/R


def core_potential_prime(R: float, a: float, b: float) -> float:
    R=float(R)
    return 5.0*float(a)*R**4 - float(b)/R**2


def core_potential_second(R: float, a: float, b: float) -> float:
    R=float(R)
    return 20.0*float(a)*R**3 + 2.0*float(b)/R**3


def core_potential_third(R: float, a: float, b: float) -> float:
    R=float(R)
    return 60.0*float(a)*R**2 - 6.0*float(b)/R**4


def radial_inertia(R: float, d: float, e: float) -> float:
    R=float(R); d=float(d); e=float(e)
    if R<=0 or d<=0 or e<=0:
        raise ValueError("R,d,e positive")
    return d*R**5 + e/R


def radial_inertia_prime(R: float, d: float, e: float) -> float:
    R=float(R)
    return 5.0*float(d)*R**4 - float(e)/R**2


def core_stiffness(R: float, a: float, b: float, d: float, e: float) -> float:
    return core_potential_second(R,a,b)/radial_inertia(R,d,e)


def kinetic_p2_share(R: float, d: float, e: float) -> float:
    M=radial_inertia(R,d,e)
    return float(d)*float(R)**5/M


def stationary_stiffness_log_derivative(a: float,b:float,d:float,e:float) -> float:
    R=stationary_radius(a,b)
    h=core_stiffness(R,a,b,d,e)
    hp=(
        core_potential_third(R,a,b)*radial_inertia(R,d,e)
        - core_potential_second(R,a,b)*radial_inertia_prime(R,d,e)
    )/radial_inertia(R,d,e)**2
    return hp/h


def stationary_log_derivative_closed(a:float,b:float,d:float,e:float) -> float:
    R=stationary_radius(a,b)
    z=kinetic_p2_share(R,d,e)
    return 2.0*(1.0-3.0*z)/R


# ---------------------------------------------------------------------------
# Source/work response
# ---------------------------------------------------------------------------

def volume_work_B(R:float, spatial_dimension:int=7) -> float:
    if R<=0 or spatial_dimension<1:
        raise ValueError("invalid")
    return float(R)**int(spatial_dimension)


def volume_work_B_prime(R:float, spatial_dimension:int=7) -> float:
    if R<=0 or spatial_dimension<1:
        raise ValueError("invalid")
    n=int(spatial_dimension)
    return n*float(R)**(n-1)


def driven_radius_derivative(
    a:float,b:float,Bprime:float
) -> float:
    R=stationary_radius(a,b)
    V2=core_potential_second(R,a,b)
    return float(Bprime)/V2


def core_drive_susceptibility(
    a:float,b:float,d:float,e:float,Bprime:float
) -> float:
    R=stationary_radius(a,b)
    z=kinetic_p2_share(R,d,e)
    M=radial_inertia(R,d,e)
    return 2.0*(3.0*z-1.0)*float(Bprime)/(R*M)


def core_drive_susceptibility_direct_fd(
    a:float,b:float,d:float,e:float,Bprime:float,hD:float=1e-6
) -> float:
    """Finite-difference local response using the linearized source B=B'*(R-R*)."""
    R0=stationary_radius(a,b)

    # Solve V'(R)-D*Bprime=0 by Newton.
    def root(D):
        R=R0
        for _ in range(12):
            f=core_potential_prime(R,a,b)-D*Bprime
            fp=core_potential_second(R,a,b)
            R-=f/fp
        return R

    hp=core_stiffness(root(hD),a,b,d,e)
    hm=core_stiffness(root(-hD),a,b,d,e)
    dhdD=(hp-hm)/(2*hD)
    return -dhdD


def seven_volume_susceptibility(a:float,b:float,d:float,e:float) -> float:
    R=stationary_radius(a,b)
    return core_drive_susceptibility(a,b,d,e,volume_work_B_prime(R,7))


# ---------------------------------------------------------------------------
# v11.4 attachment chain
# ---------------------------------------------------------------------------

def attachment_mu(h:float,k:float) -> float:
    h=float(h); k=float(k)
    if h<=0 or k<=0:
        raise ValueError("positive")
    return (h+k-math.sqrt(h*h-h*k+k*k))/3.0


def attachment_partial_h(h:float,k:float) -> float:
    h=float(h); k=float(k)
    disc=math.sqrt(h*h-h*k+k*k)
    return (1.0-(2*h-k)/(2*disc))/3.0


def attachment_partial_k(h:float,k:float) -> float:
    h=float(h); k=float(k)
    disc=math.sqrt(h*h-h*k+k*k)
    return (1.0-(2*k-h)/(2*disc))/3.0


def attachment_chi_from_core(
    h:float,k:float,chi_h:float,chi_k:float=0.0
) -> float:
    """Since hdot=-chi_h and kdot=-chi_k, chi_mu=mu_h chi_h+mu_k chi_k."""
    return attachment_partial_h(h,k)*float(chi_h)+attachment_partial_k(h,k)*float(chi_k)


# ---------------------------------------------------------------------------
# Payloads
# ---------------------------------------------------------------------------

def sign_theorem_payload() -> dict[str,Any]:
    # Three synthetic kinetic partitions, same a,b,R.
    a=1.0; b=5.0  # R*=1 exactly.
    rows=[]
    for z in (0.2,1/3,0.6):
        # At R=1 choose d=z, e=1-z so M=1.
        d=z; e=1-z
        R=stationary_radius(a,b)
        Bp=volume_work_B_prime(R,7)
        chi=core_drive_susceptibility(a,b,d,e,Bp)
        rows.append({
            "zeta":z,
            "chi_h":chi,
            "classification":"SOFTEN" if chi>1e-12 else ("STIFFEN" if chi<-1e-12 else "NEUTRAL")
        })
    return {
        "version":VERSION,
        "radial_core":"V0=aR^5+b/R, M=dR^5+e/R",
        "stationarity":"R_*^6=b/(5a)",
        "zeta":"d R_*^5 / M(R_*)",
        "exact_log_derivative":"h'/h=2(1-3zeta)/R_*",
        "general_outward_chi":"chi_h=2(3zeta-1) B0'(R_*)/[R_* M(R_*)]",
        "seven_volume_chi":"chi_h=14 R_*^5(3zeta-1)/M(R_*)",
        "threshold":"zeta=1/3",
        "outward_source_softens_iff":"zeta>1/3",
        "rows":rows,
        "physical_zeta":None,
        "physical_chi_h":None,
    }


def formula_verification_payload() -> dict[str,Any]:
    cases=[
        (1.2,4.5,.7,.8),
        (.8,7.0,1.2,.3),
        (2.0,3.0,.2,1.5),
    ]
    rows=[]
    for a,b,d,e in cases:
        R=stationary_radius(a,b)
        closed=stationary_log_derivative_closed(a,b,d,e)
        direct=stationary_stiffness_log_derivative(a,b,d,e)
        Bp=volume_work_B_prime(R,7)
        chi=core_drive_susceptibility(a,b,d,e,Bp)
        fd=core_drive_susceptibility_direct_fd(a,b,d,e,Bp)
        rows.append({
            "a":a,"b":b,"d":d,"e":e,"R":R,
            "zeta":kinetic_p2_share(R,d,e),
            "log_derivative_direct":direct,
            "log_derivative_closed":closed,
            "log_derivative_residual":abs(direct-closed),
            "chi_closed":chi,
            "chi_fd":fd,
            "chi_residual":abs(chi-fd),
        })
    return {
        "version":VERSION,
        "rows":rows,
        "max_log_derivative_residual":max(x["log_derivative_residual"] for x in rows),
        "max_chi_residual":max(x["chi_residual"] for x in rows),
    }


def stress_work_payload() -> dict[str,Any]:
    return {
        "version":VERSION,
        "source_normal_form":"V_D(R)=V0(R)-D_BH B0(R)",
        "isotropic_seven_volume_bridge":"B0(R) proportional to R^7",
        "source_conjugate":"outward generalized pressure / spatial stress trace / dilation work",
        "raw_positive_energy_density_is_equivalent_to_outward_D":False,
        "why":"under metric dilation the work-conjugate quantity is spatial stress; energy density alone does not fix the sign of mechanical work",
        "black_hole_interpretation":"accretion/jet/horizon environment may supply outward momentum flux, but its projection and normalization must be derived",
        "bridge_status":"PROVISIONAL_CONSERVATION_COMPATIBLE_WORK_SOURCE_NOT_ACTION_OWNED",
        "new_free_coupling_added":False,
        "normalization_rule":"any geometric volume factor is absorbed into the definition of the derived D_BH; no fitted chi is introduced",
        "physical_D_BH":None,
    }


def attachment_payload() -> dict[str,Any]:
    h=.181391690148362; k=1.0
    rows=[]
    for z in (.2,.6):
        # Dimensionless theorem witness at R*=1, M=1, B'=7.
        chi_h=14*(3*z-1)
        chi_mu=attachment_chi_from_core(h,k,chi_h,0)
        rows.append({
            "zeta":z,
            "chi_h":chi_h,
            "chi_mu":chi_mu,
            "same_sign":bool(chi_h*chi_mu>0),
        })
    return {
        "version":VERSION,
        "mu_minus_reference":attachment_mu(h,k),
        "dmu_dh":attachment_partial_h(h,k),
        "dmu_dk":attachment_partial_k(h,k),
        "partials_positive":attachment_partial_h(h,k)>0 and attachment_partial_k(h,k)>0,
        "fixed_k_relation":"chi_mu=(dmu/dh) chi_h",
        "same_sign_threshold_as_core":"zeta=1/3 when chi_k=0",
        "rows":rows,
        "physical_chi_k":None,
        "physical_attachment_chi":None,
    }


def archived_core_provenance_payload() -> dict[str,Any]:
    return {
        "version":VERSION,
        "recovered_v14_68_formulae":{
            "potential":"V_C(R)=kappa1 A2 R^5 + A8/R",
            "stationary_radius":"R_*=(A8/(5 kappa1 A2))^(1/6)",
            "inertia":"M_RR(R)=kappa1 D2 R^5 + D8/R",
            "stiffness":"h_C=V_C''(R_*)/M_RR(R_*)",
        },
        "recovered_v14_68_proxy":{
            "R_star":2.2052964058317697,
            "V_RR":124387.78634175545,
            "M_RR":685741.3712834204,
            "h_C_proxy":0.18139169014836257,
        },
        "missing_for_sign":{
            "kappa1_D2_R5":None,
            "D8_over_R":None,
            "zeta":None,
        },
        "sign_can_be_inferred_from_archived_total_M_only":False,
        "reason":"M_RR gives only the sum of the p2 and p8 inertia pieces; the zeta threshold requires their partition",
        "physical_v10_profile_status":"fixed proxy, not unique full-global stationary profile",
    }


def bridge_and_prove_payload() -> dict[str,Any]:
    rows=[
        ["radial core V0,M formula","RECOVERED_V14_68"],
        ["generic work response R'_D=B'/V''","DERIVED_V14_83"],
        ["core susceptibility threshold zeta=1/3","DERIVED_V14_83"],
        ["seven-volume source normal form B0~R^7","PROVISIONAL_BRIDGE"],
        ["derive D_BH from conserved spatial stress/work","OPEN"],
        ["derive physical p2/p8 inertia partition zeta","OPEN"],
        ["include k_D drive response","OPEN"],
        ["evaluate physical attachment chi","OPEN"],
        ["alpha-critical driven branch","OPEN"],
        ["Floquet stability","OPEN"],
    ]
    return {
        "version":VERSION,
        "protocol":"BRIDGE_AND_PROVE_VOLUME_WORK_DRIVER",
        "rows":rows,
        "physical_driver_derived":False,
        "bridge_may_emit_predictions":False,
    }


def status_payload() -> dict[str,Any]:
    return {
        "version":VERSION,
        "validated":[
            "exact radial response R'_D=B0'/V0''",
            "exact stationary stiffness identity h'/h=2(1-3zeta)/R_*",
            "exact core susceptibility chi_h=2(3zeta-1)B0'/(R_* M_*)",
            "outward volume work softens iff zeta>1/3",
            "seven-volume source gives chi_h=14 R_*^5(3zeta-1)/M_*",
            "finite-difference verification of susceptibility",
            "v11.4 attachment root inherits the core sign when k_D is fixed",
            "raw positive energy density is not the same object as outward dilation work",
            "archived total inertia alone cannot determine zeta",
        ],
        "invalidated":[
            "black-hole outward work necessarily softens the core for every radial kinetic partition",
            "the archived h_C and total M_RR values are enough to determine the drive sign",
            "raw luminosity or positive energy density can be inserted directly as D_BH without a stress/work reduction",
        ],
        "reclassified":[
            "black-hole-driver sign on the radial core is a kinetic-partition threshold problem",
            "the relevant environmental source is generalized dilation work/spatial stress rather than energy density alone",
            "the next action object is the p2/p8 inertia partition together with the conserved stress projection",
        ],
        "open":[EXACT_NEXT_OBJECT],
        "FULL_BHSM_COMPLETE":False,
        "MARK_III":"NOT_REACHED",
        "PHYSICAL_EXECUTION_BLOCKED":True,
        "physical_prediction_emitted":False,
        "USB_touched":False,
    }


def completion_payload() -> dict[str,Any]:
    s=sign_theorem_payload()
    f=formula_verification_payload()
    w=stress_work_payload()
    a=attachment_payload()
    p=archived_core_provenance_payload()
    b=bridge_and_prove_payload()
    validation={
        "softening_threshold":s["rows"][2]["classification"]=="SOFTEN",
        "neutral_threshold":s["rows"][1]["classification"]=="NEUTRAL",
        "stiffening_threshold":s["rows"][0]["classification"]=="STIFFEN",
        "closed_formula_verified":f["max_log_derivative_residual"]<1e-10,
        "chi_fd_verified":f["max_chi_residual"]<1e-7,
        "work_energy_firewall":w["raw_positive_energy_density_is_equivalent_to_outward_D"] is False,
        "attachment_sign_inheritance":all(x["same_sign"] for x in a["rows"]),
        "physical_zeta_missing":p["missing_for_sign"]["zeta"] is None,
        "bridge_fail_closed":b["physical_driver_derived"] is False,
        "no_prediction":True,
    }
    return {
        "version":VERSION,
        "primary_verdict":PRIMARY_VERDICT,
        "exact_next_object":EXACT_NEXT_OBJECT,
        "core_softening_gate":"chi_h>0 iff zeta>1/3 for B0'>0",
        "seven_volume_bridge":"B0~R^7",
        "physical_zeta":None,
        "physical_D_BH":None,
        "physical_chi_h":None,
        "physical_attachment_chi":None,
        "black_hole_driver_gate":"SHARP_THRESHOLD_DERIVED_INPUTS_OPEN",
        "full_BHSM_complete":False,
        "mark_III":"NOT_REACHED",
        "physical_execution_allowed":False,
        "USB_touched":False,
        "validation":validation,
        "validation_passed":all(validation.values()),
    }


def artifact_payloads():
    return {
        "BHSM_radial_core_softening_sign_theorem_v14_83.json":sign_theorem_payload(),
        "BHSM_radial_susceptibility_formula_verification_v14_83.json":formula_verification_payload(),
        "BHSM_BH_spatial_stress_volume_work_source_v14_83.json":stress_work_payload(),
        "BHSM_v11_4_attachment_volume_work_chain_v14_83.json":attachment_payload(),
        "BHSM_v14_68_core_drive_provenance_v14_83.json":archived_core_provenance_payload(),
        "BHSM_BH_volume_work_bridge_and_prove_v14_83.json":bridge_and_prove_payload(),
        "BHSM_status_ledger_v14_83.json":status_payload(),
        "BHSM_completion_gate_v14_83.json":completion_payload(),
    }


def materialize(outdir:Path):
    out=Path(outdir); out.mkdir(parents=True,exist_ok=True)
    written=[]
    for name,payload in sorted(artifact_payloads().items()):
        p=out/name
        p.write_text(json.dumps(payload,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
        written.append(p)
    return written
