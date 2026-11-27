"""Reduced optical fit to Gavazzi Table 1; additive vs fixed joint-well tensor.
No S3 training, no changes to stellar masses or central point mass. Not pixel likelihood.
"""
from pathlib import Path
import json
import numpy as np
from scipy.integrate import quad
from scipy.optimize import least_squares
from scipy.ndimage import map_coordinates,spline_filter
import coupled_well_screen as cw
P=Path(__file__).resolve().parent
width=.03
D=np.deg2rad(180.-161.348)
# Fig.1 compass: N upper left, E lower left; x right/y up in Table 1.
ROT=np.array([[-np.sin(D),-np.cos(D)],[-np.cos(D),np.sin(D)]])
GROUPS=[[[.34,-1.50],[-.94,.68],[1.52,.19]],[[-1.16,.22],[1.44,.88]],[[-.43,-1.42],[-1.10,.67],[1.23,.88]],[[-.14,-1.68],[-.57,.96]],[[-1.51,-1.78],[1.56,-1.19],[1.55,1.65],[-1.34,1.32]]]
observed=[np.asarray(g)@ROT.T for g in GROUPS]
z0=.2219305;z1=.609;z2=2.035;z3=5.975
chi={z:cw.chi(z) for z in [z0,z1,z2,z3]}
def w(a,b):return 1-chi[a]/chi[b]
pair=cw.A
stars=cw.main_m
asc=cw.arad
dk=cw.dk
A0=4*cw.G/(cw.c*cw.c*dk*asc)
# Published main optical stellar profile sphericalized, black-hole proxy fixed.
# plummer projection for nearby cataloged stellar masses.
centers=cw.centers[1:]/dk
scale=cw.scale/dk
def basic(t):
    r=np.linalg.norm(t,axis=-1)
    proj=sum(m*(np.hypot(r,a)-a-np.hypot(r,b)+b)/(b-a) for m,(a,b) in zip(stars,scale))
    v=A0*(proj+1.6e9)[:,None]*t/r[:,None]**2
    for center,m in zip(centers,cw.star_near):
        dr=t-center
        v+=A0*m*dr/(np.sum(dr*dr,axis=1)[:,None]+(3/dk)**2)
    return v
row=json.loads((P/'coupled_well_wide_screen.json').read_text())['pair']['5.975']
g1,g2=row['local_shear']
k=row['local_kappa']
K=np.array([[k+g1,g2],[g2,k-g1]])/w(z0,z3)
Id=np.eye(2)
def get_exact(angles):
    pos=(angles*dk+gridbox).T/gridstep
    return np.array([map_coordinates(field,pos,order=3,prefilter=False) for field in grid]).T
fpath=P/'coupled_well_fit_field.npz'
exact_on=fpath.exists()
if exact_on:
    npz=np.load(fpath)
    grid=[spline_filter(x,order=3) for x in npz['field']]
    gridbox=float(npz['box'])
    gridstep=float(npz['step'])
    assert abs(float(npz['dk'])-dk)<1e-12
    exact_origin=get_exact(np.zeros((1,2)))

def mk(groups):
    all1=np.vstack(groups[:4])
    coords=[all1,groups[4],pair]
    base=[basic(t) for t in coords]
    if exact_on:
        base_exact=[v+get_exact(t)-exact_origin for v,t in zip(base,coords)]
    split=[3,5,8]
    def trial(p,mat,s2=0,report=False):
        physical=base_exact if mat is None else base
        if mat is None:mat=np.zeros((2,2))
        a,s,p1,p2,b=p
        S=np.array([[p1,p2],[p2,-p1]])+mat
        def primary(t,v):
            r=np.linalg.norm(t,axis=1)[:,None]
            return v+a*(r/1.43)**s*t/r+t@S.T
        def sis(t,ctr):
            diff=t-ctr
            return diff/np.maximum(1e-10,np.linalg.norm(diff,axis=1)[:,None])
        q1=all1-w(z0,z1)*primary(all1,physical[0])
        # Nominal S1 perturber centered on equally weighted source-knot centers.
        t1=np.split(q1,split)
        center1=np.mean([x.mean(axis=0) for x in t1],axis=0)
        def at(t,v,zs):
            u=primary(t,v)
            u1=b*sis(t-w(z0,z1)*u,center1)
            return t-w(z0,zs)*u-w(z1,zs)*u1
        t2=at(groups[4],physical[1],z2)
        tr=t1+[t2]
        r=np.concatenate([(x-x.mean(axis=0)).ravel() for x in tr])
        if not report:return r
        t3=at(pair,physical[2],z3)
        if s2:
            p2=at(pair,physical[2],z2)
            t3-=w(z2,z3)*4*np.pi*(s2/cw.c)**2/asc*sis(p2,t2.mean(axis=0))
        return r,t3[0]-t3[1]
    return trial
lo=[0,-.65,-.4,-.4,0];hi=[6,.98,.4,.4,.6]
starts=[[.9,s,-.05,.06,.12] for s in [-.4,0,.5,.89]]
def fit(f,M,seeds):
    return min((least_squares(f,x,bounds=(lo,hi),args=(M,),xtol=2e-10,gtol=2e-10,ftol=2e-10,max_nfev=220) for x in seeds),key=lambda a:a.cost)
def run(groups,unc=0):
    f=mk(groups)
    b=fit(f,np.zeros((2,2)),starts)
    case={}
    for name,mat in [('none',np.zeros((2,2))),('fixed_joint',K),('shear_only',K-np.trace(K)/2*Id),('convergence_only',np.trace(K)/2*Id)]+([('full_sampled_joint',None)] if exact_on else []):
        a=b if name=='none' else fit(f,mat,[b.x]+starts[:1])
        case[name]=dict(params=a.x.tolist(),train_rms_mas=np.sqrt(np.sum(a.fun**2)/14)*1000,
                        singular=np.linalg.svd(a.jac,compute_uv=False).tolist(),
                        held={str(s):dict(vector_mas=(v:=f(a.x,mat,s,True)[1]*1000).tolist(),norm_mas=np.linalg.norm(v))
                              for s in [0,75,150]})
    return case
def main():
    ans=run(observed)
    for name,r in ans.items():print(name,r,flush=True)
    # Paired sensitivity using illustrative independent 30 mas image-coordinate jitter;
    # not posterior errors and no assumed S3 uncertainty in these pairs.
    rng=np.random.default_rng(34261)
    comps={case:{str(s):[] for s in [0,75,150]} for case in (['fixed_joint','full_sampled_joint'] if exact_on else ['fixed_joint'])}
    for _ in range(96):
        result=run([x+rng.normal(0,width,x.shape) for x in observed])
        for name in comps:
            for s in comps[name]:
                orig=result['none']['held'][s]; alt=result[name]['held'][s]
                comps[name][s].append([orig['norm_mas'],alt['norm_mas'],alt['norm_mas']-orig['norm_mas'],
                 np.linalg.norm(np.subtract(orig['vector_mas'],alt['vector_mas']))])
    ob=dict(well_tensor_unreduced=K.tolist(),rotation=ROT.tolist(),fit=ans,
          jitter_percentiles={name:{s:np.percentile(x,[16,50,84],axis=0).tolist() for s,x in comp.items()} for name,comp in comps.items()},
          jitter_columns=['baseline_norm_mas','joint_norm_mas','signed_norm_change_mas','vector_change_mas'])
    (P/'inner_rings_shared_well.json').write_text(json.dumps(ob,indent=2)+'\n')
    print(ob['jitter_percentiles'],flush=True)
if __name__=='__main__':main()
