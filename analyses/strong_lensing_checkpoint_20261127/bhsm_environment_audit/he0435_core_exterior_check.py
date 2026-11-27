"""Hold the saved two-plane mass inputs fixed; fit radial corrections as a diagnostic only."""
from pathlib import Path
import contextlib,io,json
import numpy as np
from scipy.optimize import least_squares,nnls,minimize_scalar
from scipy.interpolate import CubicSpline
P=Path(__file__).resolve().parent
# Replay baseline with an output-only hook that exposes pre-G1 deflections.
src=P/'he0435_joint_projected.py'
s=src.read_text(); marker='   diff=bj-bi; angle=w1*(joint-iso)/xrad'
assert s.count(marker)==1
ns={'__name__':'baseline_replay','__file__':str(src),'captured':{}}
exec(compile(s.replace(marker,'   captured[cutoff]=(np.array(th),ordinary+joint,bj)\n'+marker),str(src),'exec'),ns)
ns['Astar']=ns['Obj']('sersic')
with contextlib.redirect_stdout(io.StringIO()):
    run=ns['run'](115,1.5)
assert run['converged']
theta,aa,base=ns['captured'][.8]
archive=json.loads((P/'he0435_joint_projected.json').read_text())
saved=next(r for r in archive['runs'] if r['Nr']==115 and r['box_Mpc']==1.5)
assert np.max(np.abs(base-np.array(saved['LOS_half_length_Mpc']['0.8']['joint_sources_arcsec'])))<1e-8
d1,d2,d12,w1,w2,xrad,G,c=(ns[k] for k in ('d1','d2','d12','w1','w2','xrad','G','speed'))
r=np.linalg.norm(theta,axis=1)
order=np.argsort(r[:4]); idmap=np.argsort(order)
q=(theta/r[:,None]**2)*(4*G*1e9/(c*c*d1))
def center(v):return v-v.mean(axis=0)
rg=np.geomspace(.0007,1.,83)
mt=lambda R:ns["g_photo"].cyl(float(R),True)[0]
prof=lambda t:np.full_like(t,np.nan)
def forward(mass,exact=False):
    ar=aa+mass[:,None]*q
    xx=d2*(theta[:-1]-theta[-1])-d12*(ar[:-1]-ar[-1])
    R=np.linalg.norm(xx,axis=1)
    frac=prof(np.log(R))
    if exact or not np.all(np.isfinite(frac)):
        a2=np.array([ns["g_photo"].apply(x,True)[0] for x in xx])
    else:
        a2=4*ns["g_photo"].m*(frac/R**2)[:,None]*xx
    return (theta[:-1]-w1*ar[:-1]-w2*a2)/xrad
def rms(v):return float(np.linalg.norm(center(v))/2)
assert np.allclose(forward(np.zeros(5),True),base,rtol=0,atol=1e-12)
def trial(k,m):return k*m
out={'baseline_rms_mas':1000*rms(base),'image_impacts_kpc':(r[:4]*d1*1000).tolist(),'G1_impact_at_front_kpc':float(r[-1]*d1*1000),'mass_unit_Msun':1e9}
# Conditional topographic exterior, equal metric potentials and no return-flow contribution.
# The outer cutoff is a support sensitivity, not a measured compensation radius.
def integral(b,R):
    if R<b:return np.pi*b/2-R
    x=b/R
    return b*np.arcsin(x)-R*x*x/(1+np.sqrt(1-x*x))
from scipy.integrate import quad
b0=ns['b']; C=ns['C']; lam=ns['lam']; L=ns['L']; eps=ns['m'].eps
def point(mass,R):
    rv=(16*b0*G*mass/c**2*L**2/(lam*C**2))**(1/3)
    I=quad(lambda t:2*eps*np.cos(t)/(1+np.sqrt(1+(rv*np.cos(t)/R)**3)),0,np.pi/2,epsabs=1e-17,epsrel=1e-9)[0]
    return mass*I/1e9,rv
bk=r*d1*1000
out['source_radius_kpc']=bk.tolist()
out['R1_eps']=eps
out['compact_R1']=[]
for mass in [1e8,1e9,1e10,2e11]:
    inp=np.array([point(mass,x*d1)[0] for x in r])
    v=forward(inp,True)-base
    out['compact_R1'].append(dict(hypothetical_point_mass_Msun=mass,extra_mass_at_innermost_ray_Msun=float(inp.min()*1e9),max_differential_mas=float(1000*np.max(np.linalg.norm(v[:,None]-v,axis=2)))))
out['topographic']=[]
for rs in [8.53,9.62493,10.68356,12.16963,13.50815]:
    for R in [100,400,np.inf]:
        mp=np.array([integral(bb,rs)-(0 if np.isinf(R) else integral(bb,R)) for bb in bk])*10**11.1/rs/1e9
        # Independent direct integration of fraction of each spherical shell projected in cylinder.
        for BB,MM in zip(bk,mp):
            maxR=np.inf if np.isinf(R) else R
            def ff(rr):
                z=min(1.,(BB/rr)**2)
                return z/(1+np.sqrt(1-z))
            clipped=max(rs,BB)
            qi=clipped-rs+quad(ff,clipped,maxR,epsabs=1e-9)[0]
            assert abs(qi*10**11.1/rs/1e9-MM)<1e-7
        v=forward(mp,True)
        out['topographic'].append(dict(seam_kpc=rs,outer_support_kpc=None if np.isinf(R) else R,extra_mass_nearest_1e9_Msun=float(mp[:4].min()),rms_mas=1000*rms(v)))
(P/'he0435_core_exterior_check.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
