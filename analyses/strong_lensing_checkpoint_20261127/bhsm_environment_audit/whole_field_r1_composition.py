"""Pinned R1 conditional static composition check; no new observational fit."""
import json, sys
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parents[1]/'wgd_frozen_transfer'/'pr23'
sys.path.insert(0,str(root/'code'))
sys.path.insert(0,str(Path(__file__).parent/'pinned_extra'))
from strong_lensing_local_family import TolmanVIILens
from strong_lensing_r1_screened import R1ScreenedLens,R1Coefficients
c=R1Coefficients.frozen(z_l=.2283)
M=10**11.57
R=.015
one=lambda m:R1ScreenedLens(TolmanVIILens(m,R),c)
total,gal,env=[one(m) for m in [M,.6*M,.4*M]]
rows=[]
for r in [0.005,0.015,.05,.2,1.]:
    phys=[v.scalar_gradient_natural(r) for v in (total,gal,env)]
    combined=phys[0]
    summed=phys[1]+phys[2]
    x=r/c.hubble_length_Mpc
    mu=total.mass_and_slope(r)[0]
    rhs=-c.b*total.mass_length_Mpc/c.hubble_length_Mpc*mu
    flux=lambda p:c.C*x*x*p-4*x*p*p/c.lambda_over_MplH02
    err=lambda p:abs((flux(p)-rhs)/rhs)
    assert err(combined)<2e-13
    deflect=[v.extra_alpha(r) for v in (total,gal,env)]
    full=total.application([r,0.])[1][0]
    rows.append(dict(r_Mpc=r,correct_flux_relative_residual=err(combined),
      stacked_flux_relative_residual=err(summed),stacked_over_correct_scalar_response=summed/combined,
      stacked_over_correct_optical_scalar_response=(deflect[1]+deflect[2])/deflect[0],
      excess_optical_scalar_response_fraction_of_full=(deflect[1]+deflect[2]-deflect[0])/full))
out=dict(scope='Synthetic concentric 60/40 split of a single fixed Tolman VII excess, not external WGD environment, no data fit or delay.',z_l=c.z_l, C=c.C,b=c.b,lambda_hat=c.lambda_over_MplH02, R_Mpc=R, M_Msun=M, rows=rows)
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
