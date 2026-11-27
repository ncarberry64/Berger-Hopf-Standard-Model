"""HE 0435 v0.5 weak-field monopole on the relative dominance surface. No lens fit."""
import sys
sys.dont_write_bytecode=True
import io,json
from contextlib import redirect_stdout
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
from scipy.interpolate import CubicSpline
from numpy.polynomial.legendre import leggauss
with redirect_stdout(io.StringIO()):
    from plateau import gal,grp,sep,speed
    from replay import RH,zl

def replay(n, d, scale=1):
    u,w=leggauss(n)
    def root(t):
        eq=lambda r:max(abs(v) for v in gal(r)[1:])-max(abs(v) for v in grp(np.sqrt(r*r+d*d-2*r*d*t))[1:])
        return brentq(eq,.015,.32,xtol=1e-14)
    rs=CubicSpline(np.r_[-1,u,1], np.array([root(t) for t in np.r_[-1,u,1]]))
    r=rs(u)*scale
    dr=rs(u,1)*scale
    sin=np.sqrt(1-u*u)
    slope=dr*sin/r
    # In coordinates (parallel, transverse), unit normal is proportional
    # to e_r + (r_u sin(theta)/r) e_theta.
    er=np.array([u,sin]); et=np.array([-sin,u])
    nvec=(er+slope*et)/np.sqrt(1+slope**2)
    a_weights=w*r*r*np.sqrt(1+slope**2)
    loc=er*r
    delta=loc-np.array([[d],[0]])
    los=np.linalg.norm(delta,axis=0)
    sg=np.array([gal(x)[0] for x in r])
    eg=np.array([grp(x)[0] for x in los])
    sz=er*sg
    ez=delta/los*eg
    ef=ez+np.array([[grp(d)[0]],[0]])
    dot=lambda v:np.sum(nvec*v,axis=0)
    avg=lambda x:float(np.dot(a_weights,x)/sum(a_weights))
    assert abs(avg(dot(ez-ef)))<1e-2, avg(dot(ez-ef))
    apex=rs(np.array([-1.,0.,1.]))
    t=np.linspace(-1,1,1201)
    radius=rs(t)
    rt=-np.sqrt(1-t*t)*rs(t,1)
    rtt=(1-t*t)*rs(t,2)-t*rs(t,1)
    convex=np.min([np.min(1+2*(rt/radius)**2-rtt/radius),np.min(1+t*rs(t,1)/radius)])
    assert convex>0
    v=dot(sz+ef)
    total=avg(v)
    # Independent Gauss-law check, as volume integral of the two specified density fields.
    ru,wr=leggauss(96); rad=(1+ru[:,None])/2*r
    q=np.sqrt(rad**2+d*d-2*rad*d*u)
    volq=.5*r*wr[:,None]*rad**2*gamma0*speed**2*(1/(q*q+.025**2)-1/(q*q+.761**2))
    volgroup=np.sum(w*np.sum(volq,axis=0))/np.sum(a_weights)
    volsrc=np.sum(w*r*r*sg)/np.sum(a_weights)
    assert abs(total-volgroup-volsrc)<1e-2, avg(dot(ez-ef))
    gv=RH/speed**2
    return dict(separation_kpc=d*1e3,radii_away_across_toward_kpc=(scale*apex*1e3).tolist(),
        min_convexity_test=float(convex),RH_lens_epoch_Xi=total*gv/(1+zl),
        RH_today_Xi=total*gv,RH_today_stars_only_Xi=avg(dot(sz))*gv,
        local_comoving_normal_proxy_RH_today=[float(v.min()*gv),float(v.max()*gv)],
        gaussian_volume_residual=total-volgroup-volsrc)
from replay import gamma as gamma0
rows=[replay(120,f*sep) for f in (1,1.5,2)]
for f,base in zip((1,1.5,2),rows):
    alt=replay(64,f*sep)
    assert abs(alt['RH_today_Xi']-base['RH_today_Xi'])<3e-6
    assert max(abs(np.array(alt['radii_away_across_toward_kpc'])-base['radii_away_across_toward_kpc']))<3e-6
nominal=rows[0]
out=dict(nominal=nominal,assumed_line_of_sight_sensitivity=rows,
    required_positive_direct_minus_relaxation_over_Zg_at_nominal=[
       1-nominal['RH_today_Xi'],1-nominal['RH_lens_epoch_Xi']],
    gravity_only_same_shape_uniform_rescaling=[])
for Rh in ('RH_today_Xi','RH_lens_epoch_Xi'):
    sc=brentq(lambda scale:replay(64,sep,scale)[Rh]-1,.08,.3,xtol=1e-10)
    row=replay(120,sep,sc)
    assert abs(row[Rh]-1)<1e-6
    out['gravity_only_same_shape_uniform_rescaling'].append(dict(convention=Rh,factor=sc,radii_kpc=row['radii_away_across_toward_kpc']))
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
