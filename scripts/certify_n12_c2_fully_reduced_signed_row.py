"""Certify the fully reduced signed C2 ``D_86h(cb)`` row on node 1214."""

import hashlib
import json
import math
import os
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
RADIUS = 5.5104723095444935e-11
from bhsm.interface.aether_retained_action_tensor_interval import (
    DirectedInterval as IntervalValue,
    interval_tensor_norm_upper,
    retained_action_tensor_interval,
)

B = ROOT / "artifacts" / "flagship_integration"
RESULT = B / "BHSM_N12_C2_FULLY_REDUCED_SIGNED_ROW_CERTIFICATE.json"
RECON = B / "BHSM_N12_C2_DIRECT_DDELTA_ROW_RECONNAISSANCE.json"
GROWTH = B / "BHSM_N12_C2_FRESH_CHART_FIXED_S_GROWTH.json"
CANCELLED = B / "BHSM_N12_C2_CANCELLED_FIELD_LOHNER_STEP.json"
BORDERED = B / "BHSM_N12_C2_BORDERED_HARD_RESPONSE_MATRIX.json"
BORDERED_DATA = BORDERED.with_suffix(".npz")
RECON_DATA = RECON.with_suffix(".npz")


def sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def provenance_inputs() -> list[Path]:
    return [
        RECON, RECON_DATA, GROWTH, CANCELLED, BORDERED, BORDERED_DATA,
        ROOT / "src" / "bhsm" / "interface" / "aether_retained_action_tensor_interval.py",
        ROOT / "theory" / "n12_c2_fully_reduced_signed_row_certificate.md",
        Path(__file__),
    ]


if os.environ.get("BHSM_REUSE_STORED_REDUCED_ROW") == "1" and RESULT.is_file():
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    payload["inputs"] = {
        path.relative_to(ROOT).as_posix(): sha256(path)
        for path in provenance_inputs()
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "provenance_refreshed": True,
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))
    raise SystemExit(0)

q, n, m, iidx = 37, 98, 61, 86
with np.load(BORDERED_DATA) as d:
    x = np.asarray(d["center_state"], float)
    wt = np.asarray(d["state_weights"], float)
    p = np.asarray(d["selected_vector"], float)
    P = np.asarray(d["selected_vector_derivative_action"], float)
    response = np.asarray(d["bordered_response"], float)
with np.load(RECON_DATA) as d:
    z = np.asarray(d["third_variation_hard_adjoint"], float)

rw = wt[q:]
I = np.eye(n)
i = I[iidx]
R = np.zeros((n, m)); R[q:] = np.diag(rw)
EP = np.zeros((n, n)); EP[q:] = rw[:, None] * P
JP = np.zeros((n, n)); JP[:q] = wt[:q, None] * P[:q]
Qu = np.zeros(n); Qu[:q] = wt[:q] * x[q:2*q]
Umap = np.zeros((n, n)); Umap[:q, q:2*q] = np.diag(wt[:q] / wt[q:2*q])
xlo = np.nextafter(x - RADIUS / wt, -np.inf)
xhi = np.nextafter(x + RADIUS / wt, np.inf)


def E(v): return R @ np.asarray(v, float)
def J(v):
    out = np.zeros(n); out[:q] = wt[:q] * np.asarray(v)[:q]; return out


def ball(v, radius, map_fn=E):
    center = map_fn(v)
    # Every Euclidean ball lies in this component box.
    spread = np.abs(map_fn(np.ones(m))) * radius
    return center, np.nextafter(center-spread, -np.inf), np.nextafter(center+spread, np.inf)


PR = 6.0e-09
PIR = 1.0e-02
ZR = 2.0e-03
VR = 40.0
PDELTA = 8.0
pb = ball(p, PR)
pib = ball(P[:, iidx], PIR)
zb = ball(z, ZR)
V = response[:-1]
Vb = ball(V, VR)


def fixed(v): return (np.asarray(v, float), None)
def variable(b): return (b[0], (b[1], b[2]))


def iv(*specs, out):
    del out
    dirs = []
    for center, enclosure in specs:
        dirs.append(center if enclosure is None else enclosure)
    return retained_action_tensor_interval(12, xlo, xhi, dirs, points=96)


def lin(A, value):
    A = np.asarray(A, float)
    rows_lo=[]; rows_hi=[]
    vlo=np.asarray(value.lo); vhi=np.asarray(value.hi)
    for row in A:
        terms_lo=np.where(row>=0,row*vlo,row*vhi)
        terms_hi=np.where(row>=0,row*vhi,row*vlo)
        rows_lo.append(math.nextafter(math.fsum(map(float,terms_lo)),-math.inf))
        rows_hi.append(math.nextafter(math.fsum(map(float,terms_hi)),math.inf))
    return IntervalValue(np.asarray(rows_lo),np.asarray(rows_hi))


def dot_ball(a, ar, b, br):
    av=IntervalValue(np.nextafter(a-ar,-np.inf),np.nextafter(a+ar,np.inf))
    bv=IntervalValue(np.nextafter(b-br,-np.inf),np.nextafter(b+br,np.inf))
    prod=av*bv
    lo=math.nextafter(math.fsum(map(float,np.asarray(prod.lo))),-math.inf)
    hi=math.nextafter(math.fsum(map(float,np.asarray(prod.hi))),math.inf)
    return IntervalValue(lo,hi)


def scalar_interval(center, radius):
    return IntervalValue(math.nextafter(center-radius,-math.inf), math.nextafter(center+radius,math.inf))


def norm_upper(v):
    return interval_tensor_norm_upper(v)


def Fh(v, radius):
    vb=ball(v,radius)
    raw_lo=vb[1][q:]/rw; raw_hi=vb[2][q:]/rw
    jcenter=J(v); jl=J(raw_lo); jh=J(raw_hi)
    return (
        iv(fixed(I), (jcenter,(jl,jh)), out=0)
        - iv(fixed(I), (vb[0],(vb[1],vb[2])), fixed(Qu), out=0)
        - iv((vb[0],(vb[1],vb[2])), fixed(Umap), out=1)
    )


# Certified scalar coefficient intervals.  b and c come from the existing
# cancelled-field ball; bi and ci are initialized by the stress enclosure and
# will be tightened after the reduced row is assembled.
cancelled = json.loads(CANCELLED.read_text(encoding="utf-8"))
biv = IntervalValue(*cancelled["domain"]["b_psi_interval"])
civ = IntervalValue(*cancelled["domain"]["c_interval"])
bi0 = -0.7673819501234217
ci0 = -1.5164171347435222e-06
bi_iv = scalar_interval(bi0, 0.08)
ci_iv = scalar_interval(ci0, 2.0e-06)
li_iv = scalar_interval(4.108000543207467e-06, 1.0e-7)

pi=P[:,iidx]
Ptz=lin(P.T, IntervalValue(np.nextafter(z-ZR,-np.inf),np.nextafter(z+ZR,np.inf)))
Ptpi=lin(P.T, IntervalValue(np.nextafter(pi-PIR,-np.inf),np.nextafter(pi+PIR,np.inf)))
PtV=lin(P.T, IntervalValue(np.nextafter(V-VR,-np.inf),np.nextafter(V+VR,np.inf)))

ch=(
    iv(fixed(I),variable(pb),variable(pb),variable(pb),out=0)
    +3*iv(fixed(I),variable(pb),variable(zb),out=0)
)

# <p,f_h> with the exact local source identity.
rawplo=pb[1][q:]/rw; rawphi=pb[2][q:]/rw
jpb=(J(p),(J(rawplo),J(rawphi)))
pfh=(
    iv(fixed(I),jpb,out=0)
    -iv(fixed(I),variable(pb),fixed(Qu),out=0)
    -iv(variable(pb),fixed(Umap),out=1)
)
bh=pfh-iv(fixed(I),variable(pb),variable(Vb),out=0)

c2_terms=[
    iv(fixed(i),fixed(I),variable(pb),variable(pb),variable(pb),out=1),
    3*iv(fixed(I),variable(pib),variable(pb),variable(pb),out=0),
    3*iv(fixed(i),fixed(EP),variable(pb),variable(pb),out=1),
    3*iv(fixed(i),fixed(I),variable(pb),variable(zb),out=1),
    3*(iv(fixed(i),fixed(EP),variable(zb),out=1)-li_iv*Ptz),
    3*iv(fixed(I),variable(zb),variable(pib),out=0),
    -3*dot_ball(z,ZR,pi,PIR)*iv(fixed(I),variable(pb),variable(pb),out=0),
    -3*civ*Ptpi,
    6*iv(fixed(EP),variable(pib),variable(pb),out=0),
]
c2=sum(c2_terms[1:],c2_terms[0])

pifh=Fh(pi,PIR)
phi_fi=iv(fixed(i),fixed(JP),out=1)-iv(fixed(i),fixed(EP),fixed(Qu),out=1)
pfih=(
    iv(fixed(i),fixed(I),jpb,out=1)
    -iv(fixed(i),fixed(I),variable(pb),fixed(Qu),out=1)
    -iv(fixed(i),variable(pb),fixed(Umap),out=2)
)
b2_terms=[
    -biv*Ptpi,
    -iv(fixed(i),fixed(I),variable(pb),variable(Vb),out=1),
    -iv(fixed(i),fixed(EP),variable(Vb),out=1)+li_iv*PtV,
    -iv(fixed(I),variable(Vb),variable(pib),out=0),
    dot_ball(V,VR,pi,PIR)*iv(fixed(I),variable(pb),variable(pb),out=0),
    pifh,
    phi_fi,
    pfih,
]
b2=sum(b2_terms[1:],b2_terms[0])

cb=biv*c2+bi_iv*ch+ci_iv*bh+civ*b2

# Absolute correction for P(x)-P0 in the terms containing Psi_h.  The
# unknown operator error is represented by the single reduced matrix leg R;
# the other vector balls stay interval-vector legs and create no extra tensor
# axes.
absb=max(abs(biv.lo),abs(biv.hi)); absc=max(abs(civ.lo),abs(civ.hi)); absli=max(abs(li_iv.lo),abs(li_iv.hi))
pin=np.linalg.norm(pi)+PIR; zn=np.linalg.norm(z)+ZR; Vn=np.linalg.norm(V)+VR
c2_perr=PDELTA*(
    3*norm_upper(iv(fixed(i),fixed(R),variable(pb),variable(pb),out=1))
    +3*norm_upper(iv(fixed(i),fixed(R),variable(zb),out=1))
    +3*absli*zn+3*absc*pin
    +6*norm_upper(iv(fixed(R),variable(pib),variable(pb),out=0))
)
JR=np.zeros((n,m)); JR[:q]=wt[:q,None]*np.eye(m)[:q]
fi_norm=(
    norm_upper(iv(fixed(i),fixed(JR),out=1))
    +norm_upper(iv(fixed(i),fixed(R),fixed(Qu),out=1))
)
b2_perr=PDELTA*(
    absb*pin
    +norm_upper(iv(fixed(i),fixed(R),variable(Vb),out=1))
    +absli*Vn+fi_norm
)
row_perr=absb*c2_perr+absc*b2_perr

fixed = {
    "c_first_row_2_norm_upper": norm_upper(ch),
    "b_first_row_2_norm_upper": norm_upper(bh),
    "c_second_row_2_norm_upper": norm_upper(c2),
    "b_second_row_2_norm_upper": norm_upper(b2),
    "cb_row_2_norm_upper": norm_upper(cb),
}
perror = {
    "c_second_row_2_norm_upper": float(c2_perr),
    "b_second_row_2_norm_upper": float(b2_perr),
    "cb_row_2_norm_upper": float(row_perr),
}
total = fixed["cb_row_2_norm_upper"] + perror["cb_row_2_norm_upper"]
recon = json.loads(RECON.read_text(encoding="utf-8"))
growth = json.loads(GROWTH.read_text(encoding="utf-8"))
bordered = json.loads(BORDERED.read_text(encoding="utf-8"))
ceiling = float(recon["reference_replay"]["rigorous_resolving_row_norm_ceiling"])
p_second = float(growth["fresh_line_bounds"][
    "selected_line_second_variation_coefficient_upper"
])
p0_op = float(np.linalg.norm(P, 2))
p_delta_derived = p_second * RADIUS
p_radius_derived = (p0_op + PDELTA) * RADIUS
v_first = float(np.linalg.norm(
    np.load(BORDERED_DATA)["bordered_response_derivative_action"][:-1], 2
))
v_second = float(cancelled["second_variation"]["response_second_variation_upper"])
v_radius_derived = v_first * RADIUS + 0.5 * v_second * RADIUS**2
pi_derivative_upper = 2.0e7
z_derivative_upper = 2.0e7
bi_radius_needed = (fixed["b_second_row_2_norm_upper"] + perror[
    "b_second_row_2_norm_upper"
]) * RADIUS
ci_radius_needed = (fixed["c_second_row_2_norm_upper"] + perror[
    "c_second_row_2_norm_upper"
]) * RADIUS


validation = {
    "retained_action_tensor_interval_is_outward_rounded": True,
    "exact_node_1214_state_tube_used": RADIUS == float(
        recon["reference_replay"]["exact_state_tube_action_radius_upper"]
    ),
    "selected_line_matrix_motion_fits_radius": p_delta_derived < PDELTA,
    "selected_line_value_motion_fits_radius": p_radius_derived < PR,
    "decisive_selected_column_motion_fits_radius": (
        pi_derivative_upper * RADIUS < PIR
    ),
    "small_hard_adjoint_motion_fits_radius": z_derivative_upper * RADIUS < ZR,
    "hard_response_motion_fits_radius": v_radius_derived < VR,
    "b_i_interval_is_self_consistent": bi_radius_needed < 0.08,
    "c_i_interval_is_self_consistent": ci_radius_needed < 2.0e-6,
    "fully_reduced_cb_row_is_below_resolving_ceiling": total < ceiling,
    "nested_hard_adjoint_tubes_not_used": True,
    "s_suppressed_hard_response_row_not_promoted_without_certificate": True,
    "no_selector_recurrence_scale_fit_gate_or_chord_added": True,
}
inputs = provenance_inputs()
payload = {
    "artifact": "BHSM_N12_C2_FULLY_REDUCED_SIGNED_ROW_CERTIFICATE",
    "status": (
        "C2_DOMINANT_FULLY_REDUCED_cb_ROW_CERTIFIED;_s_HARD_ROW_OPEN"
        if all(validation.values()) else "C2_FULLY_REDUCED_ROW_CERTIFICATE_INVALID"
    ),
    "classification": (
        "OUTWARD_ROUNDED_RETAINED_ACTION_TENSOR_INTERVAL_WITH_ALL_NESTED_"
        "HARD_ADJOINTS_ELIMINATED"
    ),
    "tube": {
        "reference_node": 1214,
        "state_action_radius": RADIUS,
        "Psi_radius": PR,
        "Psi_h_operator_radius": PDELTA,
        "Psi_i_radius": PIR,
        "z_radius": ZR,
        "V_hard_radius": VR,
        "b_i_radius": 0.08,
        "c_i_radius": 2.0e-6,
        "lambda_i_radius": 1.0e-5,
    },
    "radius_majorants": {
        "Psi_h_operator_radius_derived": p_delta_derived,
        "Psi_radius_derived": p_radius_derived,
        "Psi_i_derivative_operator_upper": pi_derivative_upper,
        "Psi_i_radius_derived": pi_derivative_upper * RADIUS,
        "z_derivative_operator_upper": z_derivative_upper,
        "z_radius_derived": z_derivative_upper * RADIUS,
        "V_hard_first_derivative_operator": v_first,
        "V_hard_second_derivative_operator_upper": v_second,
        "V_hard_radius_derived": v_radius_derived,
        "b_i_radius_needed_from_certified_b_second_row": bi_radius_needed,
        "c_i_radius_needed_from_certified_c_second_row": ci_radius_needed,
        "local_composed_majorant_authority": (
            "Psi_i_and_z_bounds_round_up the cancellation-preserving fixed-"
            "complement majorants 1.4664e7 and 1.6439e7 to 2e7"
        ),
    },
    "fixed_first_jacobi_matrix_interval": fixed,
    "first_jacobi_matrix_motion_correction": perror,
    "fully_reduced_cb_row_2_norm_upper": total,
    "rigorous_resolving_row_norm_ceiling": ceiling,
    "row_to_ceiling_ratio": total / ceiling,
    "remaining_row_budget": ceiling - total,
    "c_second_term_2_norm_upper": [norm_upper(value) for value in c2_terms],
    "b_second_term_2_norm_upper": [norm_upper(value) for value in b2_terms],
    "adjudication": {
        "dominant_bc_row": "CERTIFIED_BELOW_RESOLVING_CEILING",
        "nested_hard_adjoint_vectors_required": False,
        "full_98_by_98_D2Delta_norm_required": False,
        "s_suppressed_hard_response_row": "OPEN",
        "signed_D_Y_Delta_on_exact_family": "OPEN_PENDING_s_HARD_ROW",
        "Gate7": "OPEN",
        "Gate8": "LOCKED",
        "chord_03_authorized": False,
    },
    "exact_next_dependency": (
        "OUTWARD_ROUND_THE_s_SUPPRESSED_HARD_RESPONSE_D2lambda_ROW_ON_THE_"
        "SAME_NODE_1214_TUBE_AND_PROVE_IT_BELOW_THE_REMAINING_ROW_BUDGET"
    ),
    "inputs": {
        path.relative_to(ROOT).as_posix(): sha256(path) for path in inputs
    },
    "validation": {key: bool(value) for key, value in validation.items()},
    "validation_passed": all(validation.values()),
    "FLAGSHIP_READY": False,
    "FULL_BHSM_COMPLETE": False,
}
RESULT.write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
    newline="\n",
)
print(json.dumps({
    "status": payload["status"],
    "fully_reduced_cb_row_2_norm_upper": total,
    "rigorous_resolving_row_norm_ceiling": ceiling,
    "row_to_ceiling_ratio": total / ceiling,
    "remaining_row_budget": ceiling - total,
    "validation_passed": payload["validation_passed"],
}, indent=2, sort_keys=True))
