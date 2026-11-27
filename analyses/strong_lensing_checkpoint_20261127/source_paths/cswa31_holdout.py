"""CSWA31 reduced projected map, dev-only fit followed by frozen S4/S5 checks."""
from pathlib import Path
import sys,json
import numpy as np
from scipy.integrate import quad
from scipy.interpolate import CubicSpline
from scipy.optimize import least_squares,root,linear_sum_assignment
from scipy.linalg import helmert
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'bhsm_environment_audit'/'pinned_extra'))
from r1_background_geometry import D,cfs,speed,xrad,G,L,bg
input=json.loads((P/'cswa31_paths.json').read_text())
zl=input['lens_z']; dl=D(0,zl); zs0=input['source_families'][0]['redshift']
zs={a['feature_family']:a['redshift'] for a in input['source_families']}
xy={a['feature_family']:np.array(a['EN_arcsec']) for a in input['source_families']}
wg={k:D(zl,z)/D(0,z) for k,z in zs.items()}
w0={k:D(zs0,z)/D(0,z) if z>zs0 else 0. for k,z in zs.items()}
prop=D(zl,zs0)/D(0,zs0)
b,C,eps,_=cfs(zl)
star_m=1.6e12*G/speed**2
a=.0272/1.81527 # spherical Hernquist control, projected half-mass radius 27.2 kpc
radii=np.geomspace(1e-4,200,450)
def star_rays(theta, add):
    R=theta*dl*xrad
    def ints(t):
        c=1/np.cosh(t);r=R/c;M=star_m*(r/(r+a))**2
        S=np.sqrt(1+16*b*L*L*M/(bg.LAMBDA*C*C*r**3))
        return M*c*c*(1 if not add else 2*eps/(1+S))
    return 4*quad(ints,0,42,epsabs=1e-24,epsrel=1e-9)[0]/(R*xrad)
sta=[CubicSpline(np.log(radii),[star_rays(t,m) for t in radii]) for m in [False,True]]
def stellar(x,include_scalar):
    r=np.linalg.norm(x,axis=-1)
    v=np.maximum(r,radii[0])
    y=sta[0](np.log(v))*(r/v)
    if include_scalar:y+=sta[1](np.log(v))*(r/v)
    return (y/np.maximum(r,1e-30))[...,None]*x
def group(x,p):
    strength,slope,u,v,dx,dy=p
    # Positive density power-law elliptical potential, softened with c=1.5".
    # A=exp([[u,v],[v,-u]]) has det 1, with eigenvalues exp(+/- e).
    e=np.hypot(u,v)
    A=np.cosh(e)*np.eye(2)+np.sinh(e)/max(e,1e-30)*np.array([[u,v],[v,-u]])
    y=x-np.array([dx,dy]); Ay=y@A
    r2=1.5**2+(Ay*y).sum(axis=-1)
    return (strength*(r2/100)**((slope-2)/2)/10)[...,None]*Ay
def lens(p,x,scalar):
    v=stellar(x,scalar)
    return v if p is None else v+group(x,p)
def make(p,sigma,scalar):
    c=(xy['S0']-prop*lens(p,xy['S0'],scalar)).mean(axis=0)
    b0=4*np.pi*(sigma/speed)**2/xrad
    def trace(x,k):
        x=np.asarray(x)
        al=lens(p,x,scalar)
        src=x-wg[k]*al
        # S2 shares essentially the S0 redshift; do not count it as a separate
        # meaningful secondary deflection plane in this reduced replay.
        if k in ('S3','S4','S5') and b0:
            offs=x-prop*al-c
            src=src-w0[k]*b0*offs/np.sqrt(.10**2+(offs*offs).sum(axis=-1))[...,None]
        return src
    return trace
train=('S0','S1','S2','S3')
lower=[.01,.66,-.35,-.35,-3,-3]
upper=[65.,1.55,.35,.35,3.,3.]
# For p>=.66 and e<=hypot(.35,.35) the projected density is nonnegative
# everywhere: trace(A) - (2-p)*lambda_max(A) remains positive.
assert 1+np.exp(-2*np.hypot(.35,.35))-(2-lower[1])>0
def fit(sigma,scalar):
    def fun(p):
        ray=make(p,sigma,scalar)
        return np.concatenate([(helmert(len(xy[k]))@ray(xy[k],k)).ravel() for k in train])
    starts=[[a,c,u,v,0,0] for a in (15,25,40) for c in (.8,1.2) for u,v in [(0.,0.),(.10,-.10)]]
    opt=min([least_squares(fun,p,bounds=(lower,upper),max_nfev=800,ftol=1e-11,xtol=1e-11,gtol=1e-11) for p in starts],key=lambda a:a.cost)
    assert opt.success
    return opt.x,float(np.sqrt(np.mean(fun(opt.x)**2)))
def model_score(p,sigma,scalar,seek_full):
    ray=make(p,sigma,scalar)
    out={}
    for k,pts in xy.items():
        src=ray(pts,k)
        rec=dict(scatter_arcsec=float(np.sqrt(np.mean(np.sum((src-src.mean(axis=0))**2,axis=1)))),
                  backprojected_arcsec=src.tolist(), max_gap_arcsec=float(np.max(np.linalg.norm(src[:,None]-src,axis=2))))
        if seek_full and k in ('S4','S5'):
            # Source fixed by first image only. Search a fixed regular sky grid.
            anchor=src[0]
            def f(x):return ray(x,k)-anchor
            sols=[]
            for t in np.array(np.meshgrid(np.linspace(-45,45,31),np.linspace(-45,45,31))).reshape(2,-1).T:
                a=root(f,t,tol=1e-9)
                if np.linalg.norm(f(a.x))<1e-7 and np.max(abs(a.x))<=45+1e-7 and all(np.linalg.norm(a.x-r)>1e-4 for r in sols):
                    sols.append(a.x)
            if all(np.linalg.norm(pts[0]-r)>1e-4 for r in sols):sols.append(pts[0])
            sols=np.array(sols)
            rest=sols[np.linalg.norm(sols-pts[0],axis=1)>1e-4]
            cnt=len(pts)-1
            dist=np.linalg.norm(pts[1:,None]-rest,axis=2)
            if len(rest):
                i,j=linear_sum_assignment(dist)
                matched={str(ii+2):float(dist[ii,jj]) for ii,jj in zip(i,j)}
            else: matched={}
            rec.update({'anchor':k+'(a)','solutions_in_90_arcsec_square':sols.tolist(),
                        'matched_distances_arcsec':matched,'unmatched_reported_counterimages':cnt-len(matched),
                        'unmatched_predicted_roots':len(rest)-len(matched)})
        out[k]=rec
    return out

if __name__=='__main__':
 models=[]
 s0_kinematic_sis=(speed*np.sqrt(.20*xrad/(4*np.pi)))
 for sig in (0.,s0_kinematic_sis,130.,220.):
  for scalar in (False,True):
   p,d=fit(sig,scalar)
   models.append(dict(tag=('ordinary' if not scalar else 'central_star_R1_overlay'),sigma_s0_km_s=sig,
                  group_params=p.tolist(),train_helmert_component_rms=d,scores=model_score(p,sig,scalar,True)))
 for scalar in (False,True):
  models.append(dict(tag='stars_only_R1' if scalar else 'stars_only_GR',sigma_s0_km_s=130.,scores=model_score(None,130.,scalar,False)))
 out={'scope':'Development-only positive projected group profile plus central photometric spherical stellar proxy. R1 is applied only to the isolated central stars; group remains an effective lens fit. Sigma is a held-fixed scenario not an observed velocity dispersion; intermediate source estimated from development configurations. Geometry check not a full BHSM or published GR model.',
      'train':train,'held_out':['S4','S5'],'source_anchor_rule':'first image only','kinematics_motivated_SIS_sigma':s0_kinematic_sis,'kinematics_reference':'Wang et al. 2024, arXiv:2404.13205, Sect. 4.2.1, median equivalent Einstein angle .20 arcsec; conversion depends on their lens magnification','models':models}
 (P/'cswa31_holdout.json').write_text(json.dumps(out,indent=2)+'\n')
 for m in models:
  print(m['tag'],m['sigma_s0_km_s'],m.get('train_helmert_component_rms'),
        [(k,m['scores'][k]['max_gap_arcsec'],m['scores'][k].get('matched_distances_arcsec'),m['scores'][k].get('unmatched_reported_counterimages')) for k in ('S4','S5')])
