"""Fixed-shape, axisymmetric two-body tidal smoothness control; no fits."""
import io,json
from contextlib import redirect_stdout
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq
from scipy.ndimage import label
with redirect_stdout(io.StringIO()):
    from plateau import gal,grp,minx,sep,speed,s
    from replay import RH,gamma
def fill(n):
    g=np.geomspace(.001,2.5,n)
    tab=np.array([gal(r)[1:] for r in g]).T
    sp=PchipInterpolator(np.log(g),tab,axis=1)
    def tide(x,y):
        d=np.array([x,y])
        e=np.array([x-sep,y])
        r=np.maximum(1e-3,np.linalg.norm(d,axis=0))
        q=np.maximum(1e-3,np.linalg.norm(e,axis=0))
        ar,ap=sp(np.log(r))
        aa,bb=.025,.761
        gm=gamma*(bb*np.arctan(q/bb)-aa*np.arctan(q/aa))*speed**2
        dg=gamma*q*q*(1/(q*q+aa*aa)-1/(q*q+bb*bb))*speed**2
        br,bp=dg/q**2-2*gm/q**3,gm/q**3
        u,v=d/r,e/q
        a=ap+bp
        xx=a+(ar-ap)*u[0]**2+(br-bp)*v[0]**2
        yy=a+(ar-ap)*u[1]**2+(br-bp)*v[1]**2
        xy=(ar-ap)*u[0]*u[1]+(br-bp)*v[0]*v[1]
        av=(xx+yy)/2
        rad=np.hypot((xx-yy)/2,xy)
        return np.maximum(np.maximum(abs(av-rad),abs(av+rad)),abs(a))/1e6
    return tide
def run(n,dx):
    tide=fill(n)
    m=float(tide(minx,0))
    assert abs(m-4.975778794)<2e-5
    tr=np.array([0,25,50,100,150,200,300,500,800,1000])
    line=tide(np.full(len(tr),minx),tr/1e3)
    along={p: float(tide(minx,p*.001)) for p in [-50,-10,-1,0,1,10,50]}
    X=np.arange(-.2,sep+.2,dx);Y=np.arange(0,1.0005,dx)
    xx,yy=np.meshgrid(X,Y)
    Q=tide(xx,yy)
    j=np.argmin(abs(X-minx))
    topology=[]
    for scale in [1.,1.05,1.25,2.]:
        ids,ncomp=label(Q<=m*scale)
        group=ids[0,j]
        ar=(ids==group) if group else np.zeros_like(Q,dtype=bool)
        topology.append(dict(level_factor=scale,connected_axis_point=bool(group),extends_upper_edge=bool(ar[-1,:].any()),
            connected_max_lateral_kpc=float(1000*yy[ar].max()) if group else None))
    cut= speed**2/RH/1e3 / (s.a*1000)
    # Along a transverse line: solve cap crossing if one exists.
    return dict(desired_axis_kpc=minx*1e3,axis_norm=m,transverse=list(zip(tr.tolist(),line.tolist())),
      at_same_x_off_axis=along,topology=topology,
      toy_re_based_cutoff=cut, ratio_axis_to_this_cutoff=m/cut,
      example_exit_limits=[float(tide(-.2,1)),float(tide(sep+.2,1))])
a,b=run(1200,.002),run(1800,.001)
assert np.max(np.abs(np.array(a['transverse'])-np.array(b['transverse'])))<2e-5
assert a['topology'][1:]==b['topology'][1:]
Path(__file__).with_name('plateau_3d.json').write_text(json.dumps(b,indent=2)+'\n')
print(json.dumps(b,indent=2))
def balance(theta):
    d=np.cos(theta)
    f=lambda r:max(map(abs,gal(r)[1:]))-max(map(abs,grp(np.sqrt(r*r+sep*sep-2*r*sep*d))[1:]))
    r=brentq(f,.015,.3,xtol=1e-14)
    assert abs(f(r))/max(map(abs,gal(r)[1:]))<1e-10
    return float(1000*r)
bounds=[balance(t) for t in np.linspace(0,np.pi,181)]
b['relative_dominance_equal_strength_surface_kpc']=dict(toward=bounds[0],across=bounds[90],away=bounds[-1],sample_min=min(bounds),sample_max=max(bounds))
Path(__file__).with_name('plateau_3d.json').write_text(json.dumps(b,indent=2)+'\n')
print(b['relative_dominance_equal_strength_surface_kpc'])
