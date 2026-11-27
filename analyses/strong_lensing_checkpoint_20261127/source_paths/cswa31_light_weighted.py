"""Photometric relative weights, dev-only common normalizations, same S4/S5 holdout."""
import json,math
import numpy as np
from scipy.linalg import helmert
from scipy.optimize import least_squares
import cswa31_catalog_planes as c
import cswa31_holdout as m
p=c.P
phot={a['id']:a for a in json.loads((p/'cswa31_hst_photometry.json').read_text())['rows']}
def panel(cat,aper,missing):
    flux=[phot[q['id']]['apertures'][aper]['flux_e_per_s'] for q in cat if phot[q['id']]['accepted']]
    rad=[phot[q['id']]['apertures'][aper]['half_positive_flux_radius_arcsec'] for q in cat if phot[q['id']]['accepted']]
    flux0,rad0=np.median(flux),np.median(rad)
    w=[];s=[]
    for q in cat:
        a=phot[q['id']]
        y=a['apertures'][aper] if a['accepted'] else None
        w.append(np.sqrt(y['flux_e_per_s'] if y else missing*flux0))
        # Photometric size tied but not equated to soft-isothermal core.
        s.append(np.clip(.60*(y['half_positive_flux_radius_arcsec'] if y else rad0),.10,.42))
    w=np.array(w)
    return np.array([a['EN_arcsec'] for a in cat]),w/w.sum(),np.array(s)
def comp(x,q,c0,scale,weights):
    d=np.asarray(x)[...,None,:]-q
    return scale*np.sum(weights[...,None]*d/np.sqrt((d*d).sum(axis=-1)+c0**2)[...,None],axis=-2)
def setup(aper,miss,scalar=False,sat=True,mid=True):
    G,W,GS=panel(c.main,aper,miss)
    H,V,HS=panel(c.mid,aper,miss)
    def config(p,sigma,scalar):
        ib=6 if mid else None
        ig=len(p)-1 if sat else None
        def g(x):
            return m.lens(p[:6],x,scalar)+comp(x,G,GS,p[ig] if sat else 0.,W)
        xh=H-c.pm*g(H)
        def early(x):
            f=g(x)
            t=x-c.pm*f
            return f,comp(t,xh,HS,p[ib] if mid else 0.,V)
        f,h=early(m.xy['S0'])
        cen=(m.xy['S0']-m.prop*f-c.p01*h).mean(axis=0)
        b0=4*np.pi*(sigma/m.speed)**2/m.xrad
        def trace(x,k):
            x=np.asarray(x)
            f,h=early(x)
            ans=x-m.wg[k]*f-c.wm[k]*h
            if k in ('S3','S4','S5') and b0:
                ans-=m.w0[k]*c.component(x-m.prop*f-c.p01*h,cen[None,:],.10,b0)
            return ans
        return trace
    return config,{'main_flux_weights':dict(zip([a['id'] for a in c.main],W.tolist())),
                   'intermediate_flux_weights':dict(zip([a['id'] for a in c.mid],V.tolist()))}
def run(tag,aper,miss,scalar,sat=True,mid=True):
    make,d=setup(aper,miss,scalar,sat,mid)
    low=m.lower+[0.]*(sat+mid)
    top=m.upper+([3.] if mid else [])+([20.] if sat else [])
    extras=([.3] if mid else [])+([4.] if sat else [])
    def fun(p):
        ray=make(p,c.s0_sig,scalar)
        return np.concatenate([(helmert(len(m.xy[k]))@ray(m.xy[k],k)).ravel() for k in m.train])
    starts=[[a,t,u,v,0,0]+extras for a in [18,33] for t in [.80,1.20] for u,v in [(0,0),(.12,-.08),(-.10,.10)]]
    res=min((least_squares(fun,z,bounds=(low,top),max_nfev=1100,ftol=1e-10,gtol=1e-10,xtol=1e-10) for z in starts),key=lambda x:x.cost)
    assert res.success
    score=c.score(res.x,c.s0_sig,scalar,make)
    for k in ['S4','S5']:
        vals=list(score[k]['matched_distances_arcsec'].values())
        score[k]['matched_counterimage_RMS_arcsec']=float(np.sqrt(np.mean(np.square(vals)))) if vals else None
    print(tag,np.sqrt(np.mean(fun(res.x)**2)),res.x[6:].tolist(),[(k,score[k]['matched_counterimage_RMS_arcsec'],score[k]['matched_distances_arcsec']) for k in ['S4','S5']],flush=True)
    return dict(tag=tag,aperture_index=aper,missing_median_flux_fraction=miss,params=res.x.tolist(),
                active_bounds=res.active_mask.tolist(),dev_component_rms_arcsec=float(np.sqrt(np.mean(fun(res.x)**2))),scores=score,**d)
if __name__=='__main__':
    jobs=[('light_nominal',1,0.,False),('light_nominal_stellar_R1',1,0.,True),
          ('light_small',0,0.,False),('light_large',2,0.,False),('light_missing_median',1,1.,False),
          ('light_mid_only',1,0.,False,False,True),('light_primary_only',1,0.,False,True,False)]
    rows=[run(*job) for job in jobs]
    (p/'cswa31_light_weighted.json').write_text(json.dumps({'scope':'Measured HST apparent aperture flux and size set relative weights and cores. Luminosity proxy SIS strength proportional to sqrt(F) (assumed). Common amplitude per plane still fit on S0-S3 only. Midplane weights use lensed apparent brightness. No pixel morphology fit or native collective BHSM law.', 'runs':rows},indent=2)+'\n')
