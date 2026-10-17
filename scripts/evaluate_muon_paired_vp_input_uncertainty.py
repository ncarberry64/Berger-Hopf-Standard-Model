"""Enclose the local Pauli overlap on the selected measurement box.

The box is +/- one quoted standard uncertainty in each primary input,
not a confidence region. No measured magnetic moment is consumed. The
complete native observable and its uncertainty are separate consumers.
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

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_paired_local_vp_pauli import paired_local_vp_pauli


def materialize(output):
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve executed measurement applications')
    names=['artifacts/muon_calibrated_pauli_20261009/inputs.json',
        'artifacts/muon_paired_local_vp_pauli_20261011/run_1/result.json',
        'src/bhsm/interface/muon_paired_local_vp_pauli.py',
        Path(__file__).relative_to(ROOT).as_posix()]
    hashes={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in names}
    config=json.loads((ROOT/names[0]).read_bytes())
    center=json.loads((ROOT/names[1]).read_bytes())
    p=config['primary_measurements']
    A=Decimal(p['alpha_inverse_0']['value_decimal'])
    r=Decimal(p['muon_electron_mass_ratio']['value_decimal'])
    sa=Decimal(str(p['alpha_inverse_0']['standard_uncertainty']))
    sr=Decimal(str(p['muon_electron_mass_ratio']['standard_uncertainty']))
    if min(A-sa,r-sr)<=0 or r-sr<=1:
        raise ValueError('positive Thomson inverse and muon/electron ratio>1 required')
    # A_VP(r) increases strictly: its positive integrand derivative is
    # 4 z/(1+z) y(1-y)(1-x), z=r²x²y(1-y)/(1-x).
    # Delta=(A_VP(1)-A_VP(r))/(pi A)^2 is negative, increases
    # with A=alpha^-1, and decreases with r. Thus these two
    # actual continuum corner applications enclose the entire box.
    corners=[]
    for tag,ai,ratio in (('lower',A-sa,r+sr),('upper',A+sa,r-sr)):
        print(json.dumps(dict(stage='certified_measurement_corner',corner=tag)),flush=True)
        application=paired_local_vp_pauli(alpha_inverse_decimal=str(ai),
            mass_ratio_decimal=str(ratio))
        if application['paired_muon_minus_electron_interval'][1]>=0:
            raise ArithmeticError('paired VP sign required for box monotonicity')
        corners.append(dict(corner=tag,alpha_inverse_decimal=str(ai),
            mass_ratio_decimal=str(ratio),application=application))
    interval=[corners[0]['application']['paired_muon_minus_electron_interval'][0],
        corners[1]['application']['paired_muon_minus_electron_interval'][1]]
    a0=float(A);r0=float(r);sai=float(sa);sri=float(sr)
    # Correlation of these primary measurements is unprovided. Retain
    # separate slopes and report the largest linear sigma over all
    # admissible correlations, as well as the independent illustration.
    da=center['derivative_alpha_interval'];dr=center['derivative_log_muon_electron_ratio_interval']
    slope_A=[-da[1]/a0**2,-da[0]/a0**2]
    slope_r=[dr[0]/r0,dr[1]/r0]
    sigma_terms=[max(map(abs,slope_A))*sai,max(map(abs,slope_r))*sri]
    up=lambda x:float(np.nextafter(x,math.inf))
    result=dict(classification='EVALUATED_CONTINUUM_LOCAL_VP_MEASUREMENT_BOX_AND_INPUT_SENSITIVITY',
        input_hashes=hashes,actual_corner_applications=corners,
        central_paired_interval=center['paired_muon_minus_electron_interval'],
        paired_interval_on_primary_one_sigma_box=interval,
        maximum_deviation_from_central_interval_on_box=up(max(
            center['paired_muon_minus_electron_interval'][1]-interval[0],
            interval[1]-center['paired_muon_minus_electron_interval'][0])),
        g_component_interval_on_box=[float(np.nextafter(2*interval[0],-math.inf)),
            float(np.nextafter(2*interval[1],math.inf))],
        primary_input_order=['alpha_inverse_0','muon_electron_mass_ratio'],
        primary_one_sigma_decimal=[str(sa),str(sr)],
        central_derivative_intervals=dict(alpha_inverse=slope_A,mass_ratio=slope_r),
        input_only_linear_standard_uncertainty_assuming_independent=up(math.hypot(*sigma_terms)),
        input_only_linear_standard_uncertainty_upper_over_correlations=up(sum(sigma_terms)),
        physical_cross_source_covariance=None,
        box_meaning='each selected primary lies within its quoted +/- one standard uncertainty; no joint coverage probability asserted',
        monotonicity='A_VP(r) strictly increasing for r>0; paired negative for r>1; Delta increases with alpha_inverse and decreases with r',
        same_external_muon_shell=True,local_shared_graph_already_in_frozen_QED=True,
        value_added_to_retained_subtotal=False,native_overlap_subtracted=False,
        complete_a_mu=None,complete_g_mu=None,complete_observable_uncertainty=None,
        error_scope='rigorous local continuum quadrature plus nonlinear extrema on specified primary measurement box; native completion, matching, higher graphs and measurement coverage excluded')
    if hashes!={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in names}:
        raise RuntimeError('consumed measurement/source changed during evaluation')
    out.mkdir(parents=True)
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();print(json.dumps(materialize(args.output),sort_keys=True))
