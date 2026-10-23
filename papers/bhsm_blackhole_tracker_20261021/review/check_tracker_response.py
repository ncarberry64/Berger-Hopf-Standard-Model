"""Nonlinear primary-branch and response-matrix controls for the tracker."""
from pathlib import Path
import json
import sys
import numpy as np
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from tracker_response import Tracker,design

t=Tracker(table_nodes=241)
checks=[]
for y in [np.array([.7,.4]),np.array([-.9,.6]),np.array([1.2,-.7])]:
    pair,obs=t.pair(y)
    for kind in ['envelope+','envelopex','shear+','compactx','center0','convergence']:
        expected=t.response(pair,kind)
        step=3e-6
        plus,rp=t.finite_pair(y,step,kind);minus,rm=t.finite_pair(y,-step,kind)
        measured=(plus-minus)/(2*step)
        err=float(np.max(abs(measured-expected))/max(1,np.max(abs(expected))))
        assert err<2e-7,(kind,y,err)
        checks.append({'source':y.tolist(),'kind':kind,'scaled_derivative_error':err,
                       'max_stationary_residual':max(rp,rm)})
expt,res,signal,cols=design(t)
# Independently recover each column's residual by a least-squares nuisance fit.
names=expt['nuisance_names'];N=np.column_stack([cols[k] for k in names])
norm=np.linalg.norm(N,axis=0);N=N/norm
# Independent high-precision QR solve. A preliminary double-precision
# least-squares subtraction differed by 3.1e-10 after admitting the nearly
# masslike axial nuisance; preserve that diagnostic rather than loosening
# the original 2e-11 acceptance threshold.
double_residual=signal-N@np.linalg.lstsq(N,signal,rcond=1e-9)[0]
with mp.workdps(70):
    nm=mp.matrix(N.tolist());sm=mp.matrix(signal.tolist())
    fitted=[]
    for j in range(sm.cols):
        solution,error=mp.qr_solve(nm,sm[:,j]);fitted.append(nm*solution)
    independent=np.array([[float(sm[i,j]-fitted[j][i]) for j in range(sm.cols)] for i in range(sm.rows)])
diff=float(np.max(abs(independent-res)))
assert diff<2e-11
# Changing the quadrature interpolation density must not create the separation.
coarse=Tracker(table_nodes=121)
cex,*_=design(coarse)
sv=np.array(expt['full_pair']['projected_signal_singular_values'])
csv=np.array(cex['full_pair']['projected_signal_singular_values'])
sv_error=float(np.max(abs(sv-csv)))
assert sv_error<1e-6
zero=Tracker(flux=0.)
zex,*_=design(zero)
zero_fraction=max(zex['full_pair']['retained_signal_norm_fractions'])
assert zero_fraction<1e-7
j={'status':'PASS','checks':checks,'independent_70digit_QR_vs_projection_max_abs':diff,
   'pre_refinement_double_LS_max_abs_difference':float(np.max(abs(double_residual-res))),
   'projected_singular_value_121_vs_241node_max_abs_difference':sv_error,
   'zero_flux_harmonic_retained_fraction_max':zero_fraction,
   'scope':'internal AI-assisted numerical checks, not data or external peer review'}
(ROOT/'review/tracker_response_check.json').write_text(json.dumps(j,indent=2)+'\n')
print(json.dumps(j,indent=2))
