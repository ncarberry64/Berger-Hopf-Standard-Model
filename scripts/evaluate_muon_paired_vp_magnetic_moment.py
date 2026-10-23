"""Carry the evaluated continuum overlap to its signed SI moment component.

Shared recoil-alpha, optical ratio and Rydberg dependence is retained
before forming the nonlinear measurement box. This graph is already in
the local QED ledger; it is not a new addend or a completed native result.
"""
from __future__ import annotations
import argparse
from decimal import Decimal
from hashlib import sha256
import json
import math
from pathlib import Path
import sys
import numpy as np
from flint import arb,ctx

ROOT=Path(__file__).resolve().parents[1]


def bounds(v):
    return [float(np.nextafter(float(v.lower()),-math.inf)),
            float(np.nextafter(float(v.upper()),math.inf))]


def binary_interval(v):
    lo,hi=map(float,v)
    return (arb(lo)+arb(hi))/2+arb(0,(arb(hi)-arb(lo))/2)


def materialize(output):
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve evaluated observable components')
    names=['artifacts/muon_calibrated_pauli_20261009/inputs.json',
        'artifacts/muon_paired_local_vp_pauli_20261011/run_1/result.json',
        'artifacts/muon_paired_vp_input_uncertainty_20261011/run_1/result.json',
        Path(__file__).relative_to(ROOT).as_posix()]
    hashes={n:sha256((ROOT/n).read_bytes()).hexdigest() for n in names}
    config,central,box=[json.loads((ROOT/n).read_bytes()) for n in names[:3]]
    primary=config['primary_measurements']
    A=Decimal(primary['alpha_inverse_0']['value_decimal'])
    r=Decimal(primary['muon_electron_mass_ratio']['value_decimal'])
    R=Decimal(primary['R_infinity']['value_decimal'])
    sa=Decimal(str(primary['alpha_inverse_0']['standard_uncertainty']))
    sr=Decimal(str(primary['muon_electron_mass_ratio']['standard_uncertainty']))
    sR=Decimal(str(primary['R_infinity']['standard_uncertainty']))
    if min(A-sa,r-sr,R-sR)<=0:raise ValueError('positive shared calibration box required')
    corners={c['corner']:c for c in box['actual_corner_applications']}
    with ctx.workprec(192):
        own=arb(119)/36-arb.pi()**2/3
        # At r_min, A_VP(r)-A_VP(1)>1/3. Everywhere
        # d A_VP/dlog r<=1/3 by z/(1+z)<=1. Thus
        # (A_VP(r)-A_VP(1))/r decreases over this entire box.
        electron_low=binary_interval(corners['upper']['application']['electron_integral']['coefficient_interval'])
        if not electron_low-own>arb(1)/3:
            raise ArithmeticError('mass-ratio monotonicity not certified on selected box')
        si=config['unit_convention']['exact_SI']
        e=arb(si['e_C']);c=arb(si['c_m_s'])
        def apply(ai,ratio,rydberg,electron):
            inverse=arb(str(ai));rr=arb(str(ratio));Ry=arb(str(rydberg))
            alpha=1/inverse;E=binary_interval(electron)
            da=(alpha/arb.pi())**2*(own-E)
            # For mu- with spin +1: Delta mu_z=-e hbar/(2m_mu)Delta a.
            # m_mu=2h Rinf r/(c alpha²). h cancels exactly. The
            # same primary alpha enters both factors, not two independent
            # charge/mass calibrations.
            magneton=e*c*alpha**2/(8*arb.pi()*Ry*rr)
            dm=-magneton*da
            return dict(a_component_interval=bounds(da),
                g_component_interval=bounds(2*da),
                mu_minus_spin_plus_component_J_per_T_interval=bounds(dm),
                mu_minus_component_in_selected_Bohr_magnetons_interval=bounds(-da/rr),
                selected_muon_magneton_J_per_T_interval=bounds(magneton))
        center=apply(A,r,R,central['electron_integral']['coefficient_interval'])
        # Moment is positive, decreases with inverse-alpha, r and Rinf.
        # For the moment these are DIFFERENT corners from extremal a.
        low=apply(A+sa,r+sr,R+sR,corners['lower']['application']['electron_integral']['coefficient_interval'])
        high=apply(A-sa,r-sr,R-sR,corners['upper']['application']['electron_integral']['coefficient_interval'])
        moment=[low['mu_minus_spin_plus_component_J_per_T_interval'][0],
            high['mu_minus_spin_plus_component_J_per_T_interval'][1]]
        result=dict(classification='EVALUATED_SIGNED_SI_MOMENT_COMPONENT_OF_CONTINUUM_LOCAL_VP_OVERLAP',
            input_hashes=hashes,charge_sign=-1,spin_projection_plus_one=True,
            central_component=center,actual_extremal_moment_corners=dict(lower=low,upper=high),
            moment_component_interval_on_shared_primary_one_sigma_box_J_per_T=moment,
            primary_box=dict(alpha_inverse=[str(A-sa),str(A+sa)],
                muon_electron_ratio=[str(r-sr),str(r+sr)],Rydberg_m_minus1=[str(R-sR),str(R+sR)]),
            common_mass_relation='m_mu_kg=2*h*R_infinity*r/(c*alpha^2)',
            moment_relation='Delta_mu_z=-e*hbar/(2*m_mu)*Delta_a for mu- spin+1',
            shared_alpha_scaling_at_fixed_optical_ratio_and_Rydberg='moment_component scales as alpha^4; no independent mass sigma appended',
            mass_ratio_monotonicity_certified=True,
            derivative_log_ratio_bound='dA_VP/dlog(r)<=1/3; A_VP(r_min)-A_VP(1)>1/3',
            measurement_box_has_no_assigned_joint_coverage=True,
            own_muon_and_electron_graphs_already_in_local_QED=True,
            contribution_added_again=False,full_native_overlap_subtracted=False,
            complete_a_mu=None,complete_g_mu=None,complete_magnetic_moment=None,
            complete_observable_uncertainty=None,
            error_scope='rigorous local graph continuum/corner arithmetic and specified shared primary box; native, remaining matched graphs and measurement coverage excluded')
    if hashes!={n:sha256((ROOT/n).read_bytes()).hexdigest() for n in names}:
        raise RuntimeError('consumed source changed during observable application')
    out.mkdir(parents=True)
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();print(json.dumps(materialize(args.output),sort_keys=True))
