"""Independent ring-only conventional benchmark, not a CA14 best-fit replay."""
from pathlib import Path
import numpy as np,json
from scipy.optimize import least_squares
P=Path(__file__).resolve().parent
src=P/'jackpot_registered_knot_control.py'
aux={'__file__':str(src),'__name__':'base'}
exec(compile(src.read_text().split('\nout={}',1)[0],str(src),'exec'),aux)
g,j,z,z1,z2,z3,w,th,rings=(aux[k] for k in ('g','j','z','z1','z2','z3','w','th','rings'))
fac=lambda zs:w(z,zs)/w(z,z1)
def unit(v):return v/np.maximum(1e-12,np.linalg.norm(v,axis=-1,keepdims=True))
def builder(groups):
    def bend(t,p):
        thetaE,sl,g1,g2,b=p
        r=np.linalg.norm(t,axis=1)
        return thetaE*((r/thetaE)**sl)[:,None]*unit(t)+t@np.array([[g1,g2],[g2,-g1]])
    def train(p,group=groups):
        s1=[t-bend(t,p) for t in group[:4]]
        c1=np.mean([v.mean(axis=0) for v in s1],axis=0)
        y=group[4]
        oa=bend(y,p)
        q2=y-fac(z2)*oa-p[-1]*unit(y-oa-c1)
        return s1,q2,c1
    def resid(p):
        s1,q2,_=train(p)
        return np.concatenate([(v-v.mean(axis=0)).ravel() for v in s1+[q2]])
    def predict(p,t,disp):
        _,q2,c1=train(p)
        a=bend(t,p); k=p[-1]*unit(t-a-c1)
        y=t-fac(z3)*a-k*w(z1,z3)/w(z1,z2)
        x2=t-fac(z2)*a-k
        y-=g['b2'](disp)*unit(x2-q2.mean(axis=0))
        return y[1]-y[0]
    return resid,predict
def fit(groups,ref=None):
    cost,pred=builder(groups)
    bounds=([1.,-.40,-.15,-.15,0.],[1.8,.40,.15,.15,.40])
    seeds=[[1.397,s,.06,.04,.16] for s in [-.25,0.,.25]] if ref is None else [ref]
    opt=min([least_squares(cost,p,bounds=bounds,ftol=1e-11,gtol=1e-11,xtol=1e-11) for p in seeds],key=lambda F:F.cost)
    return opt,pred
opt,pred=fit(rings)
nom={str(s):pred(opt.x,th,s).tolist() for s in (0,60,150)}
rng=np.random.default_rng(2308)
sim=[]
for k in range(192):
    grp=[a+rng.normal(0,.03,a.shape) for a in rings]
    t=th+rng.normal(0,[[.02,.02],[.05,.04]])
    sol,pp=fit(grp,opt.x)
    sim.append([np.linalg.norm(pp(sol.x,t,s)) for s in (0,60,150)])
out=dict(method='Gavazzi 14 ring knots only; circular conventional power-law with external shear and S1 SIS. Same R1 ratios. No S3 optimization.',
         fit=opt.x.tolist(),ring_rms_arcsec=float(np.linalg.norm(opt.fun)/np.sqrt(sum(map(len,rings)))),
         nominal_s3_vectors_arcsec=nom,nominal_s3_norms_arcsec={k:float(np.linalg.norm(a)) for k,a in nom.items()},
         jitter_quantiles_16_50_84_no_covariance=np.quantile(sim,[.16,.5,.84],axis=0).tolist())
(P/'jackpot_conventional_milestone.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
