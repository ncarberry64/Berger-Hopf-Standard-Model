"""Frozen R1 local cubic-Galileon coefficients and spherical principal symbol.

This is a conditional classical R1 effective-action calculation. It does not
identify the physical Path-B eta phase with either the R1 scalar or the spatial
metric deformation. All metric and scalar coefficients follow from the frozen
R1 cubic action; no independent matter coupling or fourth-order kernel is added.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'code'))
import action_native_matter_n2 as an
import background as bg

C_KM_S = 299792.458
G_MPC_KMS2_MSUN = 4.300917270036279e-9


def evaluate(z=0.3, mass_Msun=1e11, radius_kpc=3.0):
    manifest_path = ROOT / 'preregistration' / 'prediction_manifest.json'
    manifest = json.loads(manifest_path.read_text())
    H0 = manifest['geometry']['H0_km_s_Mpc']
    DH = C_KM_S / H0
    N = -math.log1p(z)
    solution = an.frozen_background()
    T, v, H = map(float, solution.sol(N))
    d = float(bg.rhs(N, solution.sol(N))[1] * H)
    lam = bg.LAMBDA
    # M_Pl=H0=1; physical Lambda^3=M_Pl H0^2*lam.
    b = 2*v*v/lam
    A = 1 + 4*(d + 2*H*v)/lam
    C = A - b*b/2
    D = 1 + 12*H*v/lam + 6*v**4/lam**2
    m_Mpc = G_MPC_KMS2_MSUN*mass_Msun/C_KM_S**2
    m = m_Mpc / DH
    R = radius_kpc / 1000 / DH
    rV = (16*b*m/(lam*C*C))**(1/3)

    def at_radius(r_kpc):
        r = r_kpc/1000/DH
        x = r/R
        fraction = 0.5*x**3*(5-3*x*x) if x < 1 else 1.0
        mass_slope = 15*(1-x*x)/(5-3*x*x) if x < 1 else 0.0
        enclosed = m*fraction
        S = math.sqrt(C*C + 16*b*enclosed/(lam*r**3))
        rSprime = (S*S-C*C)*(mass_slope-3)/(2*S)
        pi_prime = -2*b*enclosed/(r*r*(C+S))
        enhancement = b*b/(C+S)
        Kr = S
        Ka = S + rSprime/2
        Kt = D + 1.5*(S-C) + rSprime/2
        return dict(radius_kpc=float(r_kpc), enclosed_mass_fraction=fraction,
                    dlogM_dlogr=mass_slope, pi_prime_in_MplH0=pi_prime,
                    gradient_ratio_squared_to_rolling_background=(pi_prime/v)**2,
                    Phi_force_fractional_enhancement=enhancement,
                    Weyl_force_fractional_enhancement=enhancement,
                    Kr=Kr, Kangular=Ka, Ktime=Kt,
                    scalar_radial_characteristic_speed_squared=Kr/Kt,
                    scalar_angular_characteristic_speed_squared=Ka/Kt)

    # Exterior maximum is analytic: s=S/C, d=D/C;
    # c_r^2=s/[d+3(s+1/s-2)/4], stationary s=1.5/(1.5-d).
    ratio = D/C
    peak = None
    if ratio < 1.5:
        s_peak = 1.5/(1.5-ratio)
        r_peak = rV/(s_peak*s_peak-1)**(1/3)
        if r_peak >= R:
            peak = at_radius(r_peak*DH*1000)
    radii = sorted(set([0.003, .3, 1., 1.5, 2.7, 3., 6., 10., 30., 100.,
                       rV*DH*1000, 300., 1000., 3000.]))
    source_files = ['code/action_native_matter_n2.py', 'code/background.py',
                    'code/closed_horndeski_n2.py', 'preregistration/prediction_manifest.json']
    return dict(
        classification='conditional sourced finite-body prediction of frozen classical cubic R1 EFT',
        source_revision='49a1dabbe148f8ba9da4ac079a8d93fe97c5de76',
        input_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
                      for p in source_files},
        units=dict(background='M_Pl=H0=1', hubble_distance_Mpc=DH,
                   lambda_definition='Lambda^3/(M_Pl H0^2)', b_definition='b_physical/M_Pl'),
        background=dict(z=z,N=N,T=T,v=v,H=H,ddotT=d,lambda_dimensionless=lam),
        coefficients=dict(b=b,A=A,C=C,D=D,background_scalar_speed_squared=C/D,
                          beta1_Barreira_c3_equals_1=-C/6,
                          beta2_Barreira_M3_equals_lambda=-lam*C/(3*v*v)),
        body=dict(mass_Msun=mass_Msun,radius_kpc=radius_kpc,
                  mass_length_Mpc=m_Mpc,compactness=m/R,
                  density='Tolman VII: M(r)/M=x^3(5-3x^2)/2 inside; one outside'),
        prediction=dict(unscreened_mu_minus_one=b*b/(2*C),
                        unscreened_Sigma_minus_one=b*b/(2*C),
                        slip_Phi_over_Psi=1.,rV_Mpc=rV*DH,rV_kpc=rV*DH*1000,
                        H_times_rV_over_c=H*rV,
                        rV_background_curvature_parameter=bg.KCURV*math.exp(-2*N)*rV*rV),
        principal_scope='leading weak-field high-frequency principal coefficients after metric debraiding; spatial-gradient corrections suppressed by local weak potential; not full-system or UV certification',
        principal_result='C,D,Kr,Kangular,Ktime positive on the nonnegative-mass branch; scalar radial characteristics exceed the metric light speed in part of the screened exterior',
        exterior_scalar_radial_speed_maximum=peak,
        radius_samples=[at_radius(r) for r in radii],
        assumptions=['subtract homogeneous rolling R1 background before inserting the finite matter excess',
                     'same body mass and radius as the matched local control',
                     'regular decaying branch connected to linear R1 at r much larger than rV',
                     'weak metric, leading quasi-static derivatives, nonlinear cubic Hessian retained',
                     'no independent eta-phase source and no added fourth-order spatial kernel',
                     'galaxy encounter replaced by its R1-sourced response, not added twice to reference maps'])


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=ROOT/'artifacts/strong_lensing_r1_screened_20261020/review/r1_qs_coefficients.json')
    args=parser.parse_args()
    result=evaluate()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({k:result[k] for k in ['coefficients','prediction','exterior_scalar_radial_speed_maximum']},indent=2))
