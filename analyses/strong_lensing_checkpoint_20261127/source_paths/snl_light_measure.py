"""Local optical astrometry/photometry sensitivity; not aperture-conjugate flux."""
from snl_light_audit import *
from scipy.ndimage import maximum_filter
SEEDS={1: [(3.0,-.4),(-1.8,0.)],2:[(2.,1.75),(-1.55,-1.)]}
RAD=[.12,.16,.20,.24,.32,.40]
def measurement(q,im,x,xy,mode,search):
    xx,yy=np.meshgrid(x-xy[0],x-xy[1]); r=np.hypot(xx,yy)
    df=np.stack([np.ones_like(r),xx,yy,xx**2,xx*yy,yy**2],axis=-1)
    jlo,jhi,deg=mode
    ann=(r>=jlo)&(r<jhi)&np.isfinite(im)&(im!=0)
    df=df[:,:,:deg]
    if ann.sum()<25:return None
    def robust_sel():
        keep=ann.copy()
        for _ in range(5):
            c=np.linalg.lstsq(df[keep],im[keep],rcond=None)[0]
            resid=im-df@c
            m=np.median(resid[keep]); sd=np.median(np.abs(resid[keep]-m))*1.4826
            keep=ann&(np.abs(resid-m)<3*sd)
        return resid,float(sd),float(np.median(im[ann]))
    resid,sd,base=robust_sel()
    sm=gaussian_filter(resid,1.)
    mask=(r<search)&(im!=0)
    if not mask.any():return None
    yi,xi=np.unravel_index(np.argmax(np.where(mask,sm,-np.inf)),r.shape)
    region=np.hypot(xx-xx[yi,xi],yy-yy[yi,xi])
    ww=np.maximum(resid,0)*(region<=.10)
    peak=[float((ww*(a+xy[i])).sum()/ww.sum()) for i,a in enumerate((xx,yy))]
    rr=np.hypot(xx+xy[0]-peak[0],yy+xy[1]-peak[1])
    apertures=[float(resid[rr<ap].sum()) for ap in RAD]
    return dict(pos_EN_arcsec=peak,pk_to_local_pixel_noise=float(sm[yi,xi]/sd),flux_grid=apertures,bkg=base)
ans={}
for q in (1,2):
    x,uv,red=load(q)
    ans[q]={}
    for name,im in [('blue',uv),('F814W',red)]:
        tries=[]
        for m in [(.48,.70,3),(.50,.72,6),(.53,.80,6),(.62,.88,6)]:
            ab=[measurement(q,im,x,xy,m,.23 if i==0 else .31) for i,xy in enumerate(SEEDS[q])]
            if not all(ab): continue
            a,b=ab
            tries.append(dict(fit=m,A=a,B=b,full_separation=float(np.linalg.norm(np.subtract(a['pos_EN_arcsec'],b['pos_EN_arcsec']))),
                              aperture_ratios=np.divide(a['flux_grid'],b['flux_grid']).tolist()))
        ans[q][name]=tries
        print(q,name, list((np.round(t['A']['pos_EN_arcsec'],3),np.round(t['B']['pos_EN_arcsec'],3),round(t['full_separation'],3),np.round(t['aperture_ratios'],2),round(t['B']['pk_to_local_pixel_noise'],1)) for t in tries))
meta={'aperture_radii_arcsec':RAD,'data':ans,'caveat':'Exploratory local sky aperture products: unequal source support, unmodeled PSF, resampling and foreground dust. Do not claim a matched flux test or independent precision.'}
(Path(__file__).parent/'snl_light_measure.json').write_text(json.dumps(meta,indent=2)+'\n')
