"""Wong/Sluse spherical halo target, not a direct measurement or a GLEE replay."""
from pathlib import Path
import json,numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq
from math import pi,sqrt,log,atanh,atan
P=Path(__file__).resolve().parent
src=P/'he0435_core_exterior_check.py'
s=src.read_text()
ns={'__name__':'core_replay','__file__':str(src)}
exec(compile(s[:s.index('# Conditional topographic exterior')],str(src),'exec'),ns)
d1,G,c,xrad,w1,r=[ns[k] for k in ('d1','G','c','xrad','w1','r')]
rc=r*d1*1000
sc=c*c/(4*pi*G*d1*w1)/1e6                    # Msun/kpc²
re=1.182*xrad*d1*1000; Mref=.45*pi*re**2*sc # Einstein-aperture mass proxy
def massshape(x):return np.log1p(x)-x/(1+x)
def projected(x):
    if abs(x-1)<1e-9:return 1+log(.5)
    if x<1: return log(x/2)+atanh(sqrt(1-x*x))/sqrt(1-x*x)
    return log(x/2)+atan(sqrt(x*x-1))/sqrt(x*x-1)
def shellfrac(u):
    t=min(1.,u*u);return t/(1+sqrt(1-t))
def proj_integrated(x):
    return massshape(x)+quad(lambda y:y/(1+y)**2*shellfrac(x/y),x,np.inf,epsabs=1e-12)[0]
out={'scope':'spherical proxy for the fitted halo only; shape median and published Einstein-aperture fraction normalize without software convention for kappa0', 'RE_kpc':re,'sigma_crit_Msun_kpc2':sc,'projected_DM_Msun_at_RE':Mref,'runs':[]}
for scale in [6.49,8.43,9.01]:
    rs=scale*xrad*d1*1000; amp=Mref/projected(re/rs)
    pp=lambda b:amp*projected(b/rs)
    mm=lambda x:amp*massshape(x/rs)
    for b in [*rc,20,50,100]:assert abs(amp*proj_integrated(b/rs)/pp(b)-1)<1e-8
    v=ns['forward'](np.array([pp(x) for x in rc])/1e9,True)
    def row(x):
        mass=mm(x)
        return dict(r_kpc=x,M3D=mass,M2D=pp(x),g_extra_m_s2=G*1000*mass/x**2*1e6/3.085677581491367e19,flux_log_slope=(x/rs)**2/(1+x/rs)**2/massshape(x/rs))
    n=float(min(rc))
    out['runs'].append(dict(scale_arcsec=scale,scale_kpc=rs,M0=amp,relative_to_10p11p1_stars=amp/10**11.1,targets=[row(x) for x in [n,re,10,20,30,50,100]],simple_foreground_redistribution_RMS_mas=1e3*ns['rms'](v)))
# Separate mass versus shape from the earlier free, sheet-like case. Ratio is not a coupling fit.
out['earlier_fitted_sheet_Msun_at_nearest']=2.059784953666363e11
(P/'he0435_halo_calibration.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
