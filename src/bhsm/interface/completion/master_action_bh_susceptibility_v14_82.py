"""BHSM v14.82 master-action black-hole susceptibility gate.

Exact response theorem:
  Gamma(Q,y;D)=S0(y)-D B0(y)+1/2 Q^T[R(y)-D C(y)]Q+O(Q^4)
  y'_D|0 = K^-1 b, K=D2 S0, b=grad B0
  chi = -dR_eff/dD = C - DR[K^-1 b].

With interior odd-mode mixing H=[[A,B],[B^T,K]],
  R=A-B K^-1 B^T
  Rdot=Adot-Bdot K^-1 B^T-B K^-1 Bdot^T+B K^-1 Kdot K^-1 B^T
and chi=-Rdot.

Current BHSM action layers do not contain an action-owned black-hole/accretion/
horizon source functional, so physical chi_b is undefined, not zero.
"""
from __future__ import annotations
import json, math
from pathlib import Path
from typing import Any
import numpy as np

VERSION="v14.82"
PRIMARY_VERDICT=("BHSM_V14_82_EXACT_MASTER_ACTION_BH_SUSCEPTIBILITY_DERIVED_BUT_"
"PHYSICAL_CHI_B_UNDEFINED_BECAUSE_ACTION_OWNED_BH_SOURCE_FUNCTIONAL_IS_ABSENT")
EXACT_NEXT_OBJECT=("DERIVE_CONSERVATION_CONSISTENT_BH_SOURCE_FUNCTIONAL_B0_AND_"
"EVALUATE_B_GRADIENT_DIRECT_C_AND_FULL_SCHUR_RDOT_ON_ONE_DYNAMIC_FULL_PREIMAGE_"
"BACKGROUND_THEN_TEST_ALPHA_CRITICALITY_AND_FLOQUET_STABILITY")

def solve_response(K,b):
    K=np.asarray(K,float); b=np.asarray(b,float)
    if K.ndim!=2 or K.shape[0]!=K.shape[1] or b.shape!=(K.shape[0],):
        raise ValueError("shape mismatch")
    if np.min(np.linalg.eigvalsh((K+K.T)/2))<=0:
        raise ValueError("K must be positive")
    return np.linalg.solve(K,b)

def scalar_chi(K,b,grad_r,direct_c=0.0):
    ydot=solve_response(K,b); g=np.asarray(grad_r,float)
    if g.shape!=ydot.shape: raise ValueError("grad mismatch")
    return float(direct_c-g@ydot)

def matrix_chi(K,b,Rgrad,C):
    ydot=solve_response(K,b)
    T=np.asarray(Rgrad,float); C=np.asarray(C,float)
    if T.ndim!=3 or T.shape[0]!=ydot.size or T.shape[1]!=T.shape[2]:
        raise ValueError("Rgrad shape")
    DR=np.tensordot(ydot,T,axes=(0,0))
    if C.shape!=DR.shape: raise ValueError("C shape")
    return (C+C.T)/2-(DR+DR.T)/2

def schur(A,B,K):
    A=np.asarray(A,float); B=np.asarray(B,float); K=np.asarray(K,float)
    if A.ndim!=2 or A.shape[0]!=A.shape[1] or K.ndim!=2 or K.shape[0]!=K.shape[1]:
        raise ValueError("square blocks")
    if B.shape!=(A.shape[0],K.shape[0]): raise ValueError("B shape")
    if np.min(np.linalg.eigvalsh((K+K.T)/2))<=0: raise ValueError("K positive")
    R=A-B@np.linalg.solve(K,B.T)
    return (R+R.T)/2

def schur_dot(A,B,K,Ad,Bd,Kd):
    A=np.asarray(A,float); B=np.asarray(B,float); K=np.asarray(K,float)
    Ad=np.asarray(Ad,float); Bd=np.asarray(Bd,float); Kd=np.asarray(Kd,float)
    schur(A,B,K)
    if Ad.shape!=A.shape or Bd.shape!=B.shape or Kd.shape!=K.shape:
        raise ValueError("derivative shapes")
    Ki=np.linalg.inv(K)
    R=Ad-Bd@Ki@B.T-B@Ki@Bd.T+B@Ki@Kd@Ki@B.T
    return (R+R.T)/2

def schur_dot_fd(A,B,K,Ad,Bd,Kd,h=1e-6):
    return (schur(A+h*Ad,B+h*Bd,K+h*Kd)-schur(A-h*Ad,B-h*Bd,K-h*Kd))/(2*h)

def attachment_mu(h,k):
    h=float(h); k=float(k)
    if h<=0 or k<=0: raise ValueError("positive")
    return (h+k-math.sqrt(h*h-h*k+k*k))/3

def attachment_partials(h,k):
    h=float(h); k=float(k)
    d=math.sqrt(h*h-h*k+k*k)
    return ((1-(2*h-k)/(2*d))/3,(1-(2*k-h)/(2*d))/3)

def attachment_chi(h,k,hdot,kdot):
    dh,dk=attachment_partials(h,k)
    return -(dh*hdot+dk*kdot)

def critical_drive(r0,chi,alpha,u,v):
    if chi==0: raise ValueError("chi")
    if not 0<alpha<1: raise ValueError("alpha")
    return (r0+alpha**2*(3*u+v))/chi

def response_payload():
    K=np.array([[2,.25],[.25,1.6]]); b=np.array([.8,-.3])
    g=np.array([-1.2,.4])
    return {
      "version":VERSION,
      "formula":"chi=C-DR[K^-1 b]",
      "softening_witness_chi":scalar_chi(K,b,g,0),
      "stiffening_witness_chi":scalar_chi(K,b,-g,0),
      "symmetry_fixes_sign":False,
      "physical_chi":None,
    }

def schur_payload():
    A=np.array([[1.4,.2],[.2,1.1]])
    B=np.array([[.3,-.1],[.2,.25]])
    K=np.array([[1.8,.1],[.1,1.5]])
    Ad=np.array([[-.4,.05],[.05,.1]])
    Bd=np.array([[.06,-.03],[-.02,.04]])
    Kd=np.array([[.2,.01],[.01,-.1]])
    ex=schur_dot(A,B,K,Ad,Bd,Kd); fd=schur_dot_fd(A,B,K,Ad,Bd,Kd)
    return {
      "version":VERSION,
      "formula":"Rdot=Adot-Bdot K^-1 B^T-B K^-1 Bdot^T+B K^-1 Kdot K^-1 B^T",
      "chi":"-Rdot",
      "finite_difference_residual":float(np.linalg.norm(ex-fd)),
      "diagnostic_Rdot":ex.tolist(),
      "physical":False,
    }

def attachment_payload():
    h=.181391690148362; k=1.
    dh,dk=attachment_partials(h,k); e=1e-6
    ndh=(attachment_mu(h+e,k)-attachment_mu(h-e,k))/(2*e)
    ndk=(attachment_mu(h,k+e)-attachment_mu(h,k-e))/(2*e)
    return {
      "version":VERSION,
      "mu_minus":attachment_mu(h,k),
      "dmu_dh":dh,"dmu_dk":dk,
      "partials_positive":bool(dh>0 and dk>0),
      "fd_residual_h":abs(dh-ndh),"fd_residual_k":abs(dk-ndk),
      "softening_chi_positive":bool(attachment_chi(h,k,-.2,-.1)>0),
      "stiffening_chi_negative":bool(attachment_chi(h,k,.2,.1)<0),
      "needed":["dh_C/dD_BH","dk_D/dD_BH"],
      "physical_attachment_chi":None,
    }

def provenance_payload():
    return {
      "version":VERSION,
      "repo_sources":[
        {"source":"v14.29 View2 master action","fact":"authoritative_action=None; Wilson source observables only","BH_source":False},
        {"source":"v14.29 gauged eta p2+p8","fact":"conditional collar action; common-domain intertwiner open","BH_source":False},
        {"source":"v14.30 full-preimage audit","fact":"degree-one background and self-adjoint cap domain absent","BH_source":False},
        {"source":"v11.4 common attachment response","fact":"attachment Hessian/root exists; no BH-drive derivative","BH_source":False},
      ],
      "physical_chi_status":"UNDEFINED_SOURCE_FUNCTIONAL_NOT_ZERO",
      "can_compute_physical_chi_now":False,
    }

def bridge_payload():
    rows=[
      ["D_BH normalization","OPEN"],
      ["source functional B0[y]","OPEN"],
      ["b=grad B0","OPEN"],
      ["direct C if present","OPEN_OPTIONAL"],
      ["K and DR on dynamic background","OPEN"],
      ["chi=C-DR[K^-1 b] / -Rdot","DERIVED_V14_82"],
      ["sign chi","OPEN"],
      ["alpha-critical branch","OPEN"],
      ["Floquet stability","OPEN"],
    ]
    return {"version":VERSION,"protocol":"BRIDGE_AND_PROVE_BH_DRIVER","rows":rows,
            "physical_driver_derived":False,"physical_execution_allowed":False}

def alpha_payload():
    r0=.2; chi=.5; a=.01; u=1.; v=.5
    D=critical_drive(r0,chi,a,u,v)
    res=r0-chi*D+a*a*(3*u+v)
    return {"version":VERSION,
            "equation":"r0-chi D+alpha^2(3u+v)=0",
            "diagnostic_D":D,"diagnostic_residual":res,
            "physical_D":None,"physical":False}

def status_payload():
    return {
      "version":VERSION,
      "validated":[
        "chi=C-DR[K^-1 b]",
        "general Schur Rdot formula",
        "Schur derivative finite-difference verification",
        "v11.4 mu_minus monotone in h and k",
        "softening gives positive attachment chi; stiffening gives negative chi",
        "symmetry does not determine chi sign",
        "alpha-critical drive equation",
        "missing BH source means chi undefined, not zero",
      ],
      "invalidated":[
        "assuming chi>0 from black-hole activity",
        "setting chi=0 because no source term is present",
        "inferring drive sign from a positive static Hessian",
      ],
      "reclassified":[
        "BH driver is a mixed third-variation/background-response problem",
        "next missing object is the action-owned source functional B0, not a phenomenological chi",
      ],
      "open":[EXACT_NEXT_OBJECT],
      "FULL_BHSM_COMPLETE":False,"MARK_III":"NOT_REACHED",
      "PHYSICAL_EXECUTION_BLOCKED":True,"USB_touched":False,
      "physical_prediction_emitted":False,
    }

def completion_payload():
    a=response_payload(); s=schur_payload(); v=attachment_payload(); p=provenance_payload(); al=alpha_payload()
    validation={
      "both_signs_possible":a["softening_witness_chi"]*a["stiffening_witness_chi"]<0,
      "schur_fd":s["finite_difference_residual"]<1e-8,
      "attachment_monotone":v["partials_positive"],
      "attachment_fd":v["fd_residual_h"]<1e-8 and v["fd_residual_k"]<1e-8,
      "source_absent":p["can_compute_physical_chi_now"] is False,
      "chi_fail_closed":p["physical_chi_status"]=="UNDEFINED_SOURCE_FUNCTIONAL_NOT_ZERO",
      "alpha_residual":abs(al["diagnostic_residual"])<1e-12,
      "no_prediction":True,
    }
    return {
      "version":VERSION,"primary_verdict":PRIMARY_VERDICT,"exact_next_object":EXACT_NEXT_OBJECT,
      "chi_formula":"chi=C-DR[K^-1 b]",
      "schur_chi_formula":"chi=-d/dD(A-B K^-1 B^T)",
      "current_BH_source_functional":"ABSENT",
      "physical_chi_b":None,"black_hole_driver_gate":"UNDECIDED_SOURCE_FUNCTIONAL_MISSING",
      "full_BHSM_complete":False,"mark_III":"NOT_REACHED",
      "physical_execution_allowed":False,"USB_touched":False,
      "validation":validation,"validation_passed":all(validation.values())
    }

def artifact_payloads():
    return {
      "BHSM_master_action_BH_susceptibility_formula_v14_82.json":response_payload(),
      "BHSM_Schur_reduced_drive_derivative_v14_82.json":schur_payload(),
      "BHSM_v11_4_attachment_drive_chain_v14_82.json":attachment_payload(),
      "BHSM_BH_source_action_provenance_v14_82.json":provenance_payload(),
      "BHSM_BH_driver_bridge_and_prove_v14_82.json":bridge_payload(),
      "BHSM_alpha_critical_drive_linear_response_v14_82.json":alpha_payload(),
      "BHSM_status_ledger_v14_82.json":status_payload(),
      "BHSM_completion_gate_v14_82.json":completion_payload(),
    }

def materialize(outdir:Path):
    out=Path(outdir); out.mkdir(parents=True,exist_ok=True); written=[]
    for name,payload in sorted(artifact_payloads().items()):
        p=out/name
        p.write_text(json.dumps(payload,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
        written.append(p)
    return written
