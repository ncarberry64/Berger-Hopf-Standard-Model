"""Aperture photometry audit; all target data from HST + spectroscopic catalogue, no lens scoring."""
from pathlib import Path
import argparse,json,hashlib,math
from astropy.io import fits
from astropy.wcs import WCS
from astropy.wcs.utils import proj_plane_pixel_scales
import numpy as np
from scipy.ndimage import gaussian_filter
P=Path(__file__).resolve().parent
names=json.loads((P/'cswa31_catalog_planes.json').read_text())
spec={}
for s in (P/'cswa31_muse_raw.tsv').read_text().splitlines():
    t=s.split()
    if len(t)==6 and t[0].isdigit() and float(t[4])<1.37:spec[int(t[1])]=[float(t[2]),float(t[3])]
def robust_plane(x,y,values):
    dm=np.array([np.ones(len(x)),x,y]).T
    cur=np.ones(len(x),bool)
    for m in range(5):
        p=np.linalg.lstsq(dm[cur],values[cur],rcond=None)[0]
        d=values-dm@p
        sigma=max(1e-8,float(np.median(np.abs(d[cur]-np.median(d[cur])))*1.4826))
        good=np.abs(d-np.median(d[cur]))<2.8*sigma
        if good.sum()<20 or (good==cur).all():break
        cur=good
    return p,sigma
def main(f):
    with fits.open(f) as hd:
        img=hd['SCI'].data.astype(float)
        wt=hd['WHT'].data
        hdr=hd['SCI'].header
        w=WCS(hdr)
    ps=float(np.mean(proj_plane_pixel_scales(w))*3600)
    photflam,photplam=map(float,(hdr['PHOTFLAM'],hdr['PHOTPLAM']))
    zp=-2.5*np.log10(photflam)-5*np.log10(photplam)-2.408
    loc={k:np.asarray(w.world_to_pixel_values(*ra)) for k,ra in spec.items()}
    def estimate(k,shift,ap):
        loc0=loc[k]+shift
        dy,dx=np.mgrid[-20:21,-20:21]
        xp,yp=np.round(loc0).astype(int)
        px,py=xp+dx,yp+dy
        x,y=(px-loc0[0])*ps,(py-loc0[1])*ps
        R=np.hypot(x,y)
        a=img[py,px]; valid=(wt[py,px]>0)&np.isfinite(a)
        # mask spectroscopic neighbors in the local sky estimate; assign
        # overlapping aperture pixels only to the nearest catalog center.
        dN=np.full(R.shape,100.)
        for j,other in loc.items():
            if k==j or np.linalg.norm(other-loc[k])*ps>4.0:continue
            dN=np.minimum(dN,np.hypot(px-other[0]-shift[0],py-other[1]-shift[1])*ps)
        sv=(R>=1.2)&(R<=2.2)&valid&(dN>.55)
        if sv.sum()<20:return None
        coef,sig=robust_plane(x[sv],y[sv],a[sv])
        v=a-(coef[0]+coef[1]*x+coef[2]*y)
        core=(R<ap)&valid&(R<dN)
        aper=(R<ap)&valid
        val=float(v[core].sum())
        noise=float(sig*np.sqrt(core.sum())*1.65) # correlated-noise heuristic
        pos=np.maximum(v[core],0); rr=R[core]
        iii=np.argsort(rr); cumul=np.cumsum(pos[iii])
        rh=float(np.interp(.5*cumul[-1],cumul,rr[iii]))
        cx,cy=(float(np.sum(ax[core]*pos)/sum(pos)) if sum(pos)>0 else 0 for ax in (x,y))
        return dict(flux_e_per_s=val, aperture_AB=float(zp-2.5*np.log10(val)) if val>0 else None,
            half_positive_flux_radius_arcsec=rh,SNR_proxy=val/noise,
            aperture_kept_fraction=float(core.sum()/aper.sum()),centroid_residual_EN_image_arcsec=[cx,cy],
            nearest_catalog_neighbor_arcsec=float(np.min(dN[R==R.min()])))
    bg=loc[354]
    iy,ix=round(bg[1]),round(bg[0])
    sm=gaussian_filter(img[iy-7:iy+8,ix-7:ix+8],1)
    j,i=np.unravel_index(sm.argmax(),sm.shape)
    shift=np.array([ix-7+i,iy-7+j])-bg
    assert np.linalg.norm(shift)*ps<.7
    res=[]
    for zone,key in [('primary','primary_satellite_proxy'),('intermediate','mid_members')]:
        for q in names[key]:
            k=q['id']; vals=[estimate(k,shift,r) for r in [.64,.84,1.04]]
            val=vals[1]
            good=bool(all(t is not None and t['flux_e_per_s']>0 and t['SNR_proxy']>6 for t in vals)
                  and val['aperture_kept_fraction']>.77 and np.linalg.norm(val['centroid_residual_EN_image_arcsec'])<.34)
            res.append(dict(**q,zone=zone,accepted=good,apertures=vals))
    out={'hst_program':15253,'mast_science_product':Path(f).name,'catalog_product_ID':'hst_15253_04_wfc3_ir_f160w_idki04_drz.fits',
         'sha256':hashlib.sha256(Path(f).read_bytes()).hexdigest(),'pixel_arcsec':ps,'AB_zero_point':float(zp),
         'bg_peak_alignment_px':shift.tolist(),'search_evidence':'These are local sky-subtracted fixed aperture fluxes and apparent aperture half-light proxies, not total magnitudes or deconvolved structural sizes.',
         'aperture_radii_arcsec':[.64,.84,1.04],'rows':res}
    (P/'cswa31_hst_photometry.json').write_text(json.dumps(out,indent=2)+'\n')
    for zone in ['primary','intermediate']:
        q=[v for v in res if v['zone']==zone]; print(zone,sum(x['accepted'] for x in q),len(q))
        if zone=='intermediate':print([(x['id'],x['accepted'],None if x['apertures'][1] is None else round(x['apertures'][1]['aperture_AB'] or 99,2)) for x in q])
    print('pixel scale, BGG offset, zeropoint',ps,shift,zp)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('image');main(p.parse_args().image)
