"""ESO325-G004 archival light-only cross-filter ridge diagnostic.
Arc identification uses Smith et al. 2005 Figure 3, not mass coordinates.
This is not a cross-image source registration or a BHSM test.
"""
from snl_light_audit import *
x0,y0=.55,.22  # approximate optical center used only as plotting origin
files={k:next(P.glob(f'hst_10710_02_acs_wfc_{k}*_drc.fits')) for k in ('f475w','f625w')}
img={}
for k,f in files.items():
    x,d=sky_cutout(f,205.88825,-38.176,scale=.05)
    assert np.all(np.isfinite(d)) and np.count_nonzero(d)==d.size, f"No valid complete central SCI cutout: {f}"
    img[k]=d
def track(d,thetas,sig,rr):
    dt=gaussian_filter(d,1.0)-gaussian_filter(d,sig)
    az,r=np.meshgrid(np.deg2rad(thetas),rr,indexing='ij')
    xx=x0+np.cos(az)*r; yy=y0+np.sin(az)*r
    val=map_coordinates(dt,((yy-x[0])/.05,(xx-x[0])/.05),order=1)
    i=val.argmax(axis=1)
    return rr[i],val[np.arange(len(i)),i],(i==0)|(i==len(rr)-1)
params={'A': (list(range(-73,-4,4)), [2.45,3.0]),'B': (list(range(100,129,4)), [3.0,3.65]),'C':(list(range(218,235,4)), [2.25,2.95])}
# Tests below use only sectors that visually contain the specified arc, preselected via Fig. 3.
ans={}
for label,(angs,range_) in params.items():
    ans[label]={}
    for sig in (3.,4.,5.):
        rr=np.arange(*range_,.025)
        t=[track(d,angs,sig,rr) for d in img.values()]
        dif=t[1][0]-t[0][0]
        valid=~(t[0][2]|t[1][2])
        row=dict(angles_deg=angs,radii_f475w=t[0][0].tolist(),radii_f625w=t[1][0].tolist(),interior=valid.tolist(),num_valid=int(valid.sum()),
                 radial_rms_arcsec=float(np.sqrt(np.mean(dif[valid]**2))) if valid.any() else None)
        ans[label][sig]=row
        print(label,sig, row['num_valid'],row['radial_rms_arcsec'],np.round(t[0][0],2),np.round(t[1][0],2))
(Path(__file__).parent/'snl0_arc_shape.json').write_text(json.dumps(ans,indent=2)+'\n')
