"""Fixed-input two-body smoothness diagnostic, not a BHSM threshold or optical fit."""
from contextlib import redirect_stdout
from pathlib import Path
import io,json
import numpy as np
from scipy.optimize import brentq,minimize_scalar
with redirect_stdout(io.StringIO()):
    from replay import s,speed,sep,gamma
def gal(r):
    mu,n=s.sphere(r/s.a)
    g=s.m*mu*speed**2/r**2
    return g,g*(n-2)/r,g/r
def grp(r):
    a,R=.025,.761
    m=gamma*(R*np.arctan(r/R)-a*np.arctan(r/a))*speed**2
    d=gamma*r*r*(1/(r*r+a*a)-1/(r*r+R*R))*speed**2
    return m/r**2,d/r**2-2*m/r**3,m/r**3
def diag(x):
    g,h,k=gal(x)
    v,j,l=grp(sep-x)
    return g-v,g-v+grp(sep)[0],h+j,k+l
def spec(x):
    a,b=diag(x)[2:]
    return max(abs(a),abs(b))
def root(k):
    return brentq(lambda x:diag(x)[k],.015,sep-.025,xtol=1e-15)
def zslope(x,k):
    dt=1e-6
    return (diag(x+dt)[k]-diag(x-dt)[k])/(2*dt)
def row(x):
    raw,rel,ax,tr=diag(x)
    assert np.allclose([ax,ax],[zslope(x,0),zslope(x,1)],rtol=2e-7)
    return dict(x_kpc=x*1000,raw_potential_slope_kms2_per_kpc=raw/1000,lens_center_frame_slope_kms2_per_kpc=rel/1000,
           hessian_axial_kms2_per_kpc2=ax/1e6,hessian_transverse_kms2_per_kpc2=tr/1e6)
search=np.linspace(.015,sep-.025,256)
grid=np.array(list(map(spec,search)))
i=np.argmin(grid)
assert 0<i<len(grid)-1
minx=minimize_scalar(spec,method='bounded',bounds=(search[i-1],search[i+1]),options={'xatol':1e-12}).x
out=dict(group_projected_sep_kpc=sep*1000,raw_saddle=row(root(0)),comoving_balance=row(root(1)),lowest_tide_on_axis=row(minx),nominal_seam=row(.01221),
         angular_12arcsec_impact=row(.007134))
Path(__file__).with_name('plateau.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
