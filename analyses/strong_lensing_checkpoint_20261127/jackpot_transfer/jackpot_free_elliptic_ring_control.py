"""Conventional elliptical power law, 14 knots only; third source scored afterward."""
from pathlib import Path
import numpy as np,json
from scipy.optimize import least_squares
from scipy.special import hyp2f1
P=Path(__file__).resolve().parent
src=P/'jackpot_registered_knot_control.py'
aux={'__file__':str(src),'__name__':'base'}
exec(compile(src.read_text().split('\nout={}',1)[0],str(src),'exec'),aux)
g,z,z1,z2,z3,w,th,rings=(aux[k] for k in ('g','z','z1','z2','z3','w','th','rings'))
def epl(t,b,eta,q,ang):
    U=g['matrix'](ang)
    X,Y=(t@U.T).T
    zz=q*X+1j*Y
    R=np.abs(zz)
    ph=zz/R
    b=b*np.sqrt(q)
    v=2*b/(1+q)*(b/R)**(eta-1)*ph*hyp2f1(1.,eta/2,2-eta/2,-(1-q)/(1+q)*ph**2)
    return np.column_stack([v.real,v.imag])@U
for q in (.75,.946,1.):
 a=epl(th,1.397,1.027,q,37)
 b=np.array([g['ell'](t,q,37,lambda r:.5*(2-1.027)*(1.397/r)**1.027) for t in th])
 assert np.allclose(a,b,atol=1e-8)
fac=lambda zs:w(z,zs)/w(z,z1)
def unit(v):return v/np.maximum(1e-12,np.linalg.norm(v,axis=-1,keepdims=True))
def builder(groups):
    def bend(t,p):
        b,eta,q,ang,dx,dy,g1,g2,_=p
        t=t-np.array([dx,dy])
        return epl(t,b,eta,q,ang)+t@np.array([[g1,g2],[g2,-g1]])
    def train(p):
        s1=[t-bend(t,p) for t in groups[:4]]
        c1=np.mean([v.mean(axis=0) for v in s1],axis=0)
        y=groups[4]; a=bend(y,p)
        s2=y-fac(z2)*a-p[-1]*unit(y-a-c1)
        return s1,s2,c1
    def resid(p):
        es,es2,_=train(p)
        return np.concatenate([(t-t.mean(axis=0)).ravel() for t in es+[es2]])
    def score(p,disp):
        _,s2,c1=train(p)
        a=bend(th,p); k=p[-1]*unit(th-a-c1)
        x2=th-fac(z2)*a-k
        x3=th-fac(z3)*a-k*w(z1,z3)/w(z1,z2)-g['b2'](disp)*unit(x2-s2.mean(axis=0))
        return (x3[1]-x3[0]).tolist()
    return resid,score
out=[]
for mode,lim in [('near_CA14',(.90,1.1,.90,.14,.186)),('broad',(.60,1.4,.68,0.,.4))]:
 e0,e1,q0,slo,shi=lim
 bounds=([1.2,e0,q0,-360.,-.08,-.08,-.14,-.14,slo],[1.6,e1,1.,360.,.08,.08,.14,.14,shi])
 F,G=builder(rings)
 starts=[[1.397,1.027,.946,float(a),0,0,.052,.043,.16] for a in np.arange(-165,180,30)]
 opts=[least_squares(F,v,bounds=bounds,ftol=1e-11,xtol=1e-11,gtol=1e-11,max_nfev=350) for v in starts]
 fit=min(opts,key=lambda o:o.cost)
 pred={str(v):G(fit.x,v) for v in (0,60,150)}
 out.append(dict(mode=mode,x=fit.x.tolist(),ring_rms_arcsec=float(np.linalg.norm(fit.fun)/np.sqrt(14)),
                 success=bool(fit.success),starts_within_1pct=int(sum(o.cost<1.01*fit.cost for o in opts)),
                 s3_B_minus_A_arcsec=pred,s3_norm_arcsec={k:float(np.linalg.norm(v)) for k,v in pred.items()}))
(P/'jackpot_free_elliptic_ring_control.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
