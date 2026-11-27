"""Hold the saved two-plane mass inputs fixed; fit radial corrections as a diagnostic only."""
from pathlib import Path
import contextlib,io,json
import numpy as np
from scipy.optimize import least_squares,nnls,minimize_scalar
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
q=(theta/r[:,None]**2)*(4*G*1e9/(c*c*d1*1000))
def center(v):return v-v.mean(axis=0)
def forward(mass):
    ar=aa+mass[:,None]*q
    xx=d2*(theta[:-1]-theta[-1])-d12*(ar[:-1]-ar[-1])
    a2=np.array([ns['g_photo'].apply(x,True)[0] for x in xx])
    return (theta[:-1]-w1*ar[:-1]-w2*a2)/xrad
def rms(v):return float(np.linalg.norm(center(v))/2)
assert np.allclose(forward(np.zeros(5)),base,rtol=0,atol=1e-12)
def trial(k,m):return k*m
out={'baseline_rms_mas':1000*rms(base),'image_impacts_kpc':(r[:4]*d1*1000).tolist(),'G1_impact_at_front_kpc':float(r[-1]*d1*1000),'mass_unit_Msun':1e9}
for label,k in [('compact',np.ones(5)),('flat_rotation',r/r[order[0]]),('uniform_projected_sheet',(r/r[order[0]])**2)]:
    fun=lambda m:rms(forward(trial(k,m)))
    grid=np.linspace(0,1000,201); j=np.argmin([fun(g) for g in grid])
    a=minimize_scalar(fun,bounds=(grid[max(0,j-1)],grid[min(len(grid)-1,j+1)]),method='bounded')
    out[label]=dict(fitted_amplitude_at_innermost_ray=float(a.x),rms_mas=1000*a.fun)
# Flexible positive radial column: increments at image radii and one nonnegative
# increment at G1. G1 lies beyond every quasar image. Scan a broad range of the
# last increment to expose sensitivity; these are conditional inverse fits.
def calc(a):
    b=np.cumsum(a)
    return np.r_[b[:4][idmap],b[4]]
out['free_radial_g1_sensitivity']=[]
for g1_extra in [0,100,300,1000,3000]:
    def zz(m):return center(forward(calc(np.r_[m,g1_extra]))).ravel()
    a=least_squares(zz,[200,40,65,0.001],bounds=(0,np.inf),ftol=1e-10,gtol=1e-10,xtol=1e-10)
    out['free_radial_g1_sensitivity'].append(dict(extra_G1_cylinder=g1_extra,mass_sorted=calc(np.r_[a.x,g1_extra])[:4][order].tolist(),rms_mas=500*np.linalg.norm(a.fun)))
(P/'he0435_core_pull_screen.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
