"""Cross-band holdout of the candidate A fold, ESO 325-G004.
Two trial branches of arc A, based on the image symmetric structure.
The brightest blue peak on each branch sets alignment; all other structure is unused in training.
One-dimensional diagnostic, not full affine/PSF inference or BHSM result.
"""
import numpy as np
from scipy.ndimage import gaussian_filter,map_coordinates
from scipy.signal import find_peaks
from snl_light_audit import P,sky_cutout
from pathlib import Path
import json
tt=np.arange(-84,2.001,.1)
r=np.arange(2.36,3.121,.025)
az,rad=np.meshgrid(np.deg2rad(tt),r,indexing='ij')
files=sorted(P.glob("hst_10710_02_acs_wfc_f*_drc.fits"))
assert len(files)==2
data=[]
for f in files:
    x,d=sky_cutout(f,205.88825,-38.176,scale=.05)
    assert np.all(np.isfinite(d)) and np.all(d!=0)
    data.append((x,d))

def profiles(sig,lo,hi,narrow=1):
    vv=[]
    for x,d in data:
        v=map_coordinates(gaussian_filter(d,narrow)-gaussian_filter(d,sig),
              ((.22+rad*np.sin(az)-x[0])/.05,(.55+rad*np.cos(az)-x[0])/.05),order=1)
        vv.append(v[:,(r>=lo)&(r<=hi)].mean(axis=1))
    return vv
def peak(vals,tlo,thi):
    m=(tt>=tlo)&(tt<=thi)
    return tt[m][np.argmax(vals[m])]
def analyze(vv,known=None):
    p=vv[0]
    a,b=known if known is not None else [peak(p,-74,-66),peak(p,-14,-7)]
    # One-pixel scale along the arc is approximately 1 degree. The tested
    # window passes over the interior, withholding the anchor neighborhoods.
    x=np.arange(-63,-46.99,1.)
    y=a+b-x
    result={'blue_anchors_deg':[float(a),float(b)],'train_center_deg':float((a+b)/2)}
    for v,name in zip(vv,['blue','red']):
        vp=peak(v,-14,-7)
        left=peak(v,-74,-66)
        a0=np.interp(x,tt,v); b0=np.interp(y,tt,v)
        peaks=find_peaks(v,prominence=.0015,distance=22)[0]
        lp=tt[peaks][(tt[peaks]>=-63)&(tt[peaks]<=-47)]
        rp=tt[peaks][(tt[peaks]>=y.min()-2)&(tt[peaks]<=y.max()+2)]
        res=[{'left_deg':float(t),'predicted_right_deg':float(a+b-t),'nearest_right_deg':float(q),'arcsec_difference':float(abs(q-(a+b-t))*np.pi*2.75/180)} for t in lp for q in ([min(rp,key=lambda z:abs(z-(a+b-t)))] if len(rp) else [])]
        result[name]={'align_corr':float(np.corrcoef(a0,b0)[0,1]),'measured_end_peaks_deg':[float(left),float(vp)],
             'paired_end_differential_arcsec':float(abs(vp-(a+b-left))*np.pi*2.75/180),
             'peaks_nearest_diagnostic_not_unique':res}
    return result
nom=analyze(profiles(4,2.54,2.94))
pars=[(sig,lo,hi,n) for sig in (3.,4.,5.) for lo,hi in [(2.54,2.94),(2.52,2.99),(2.6,2.91)] for n in (.85,1.,1.2)]
sweep=[dict(params=p,**analyze(profiles(*p),nom['blue_anchors_deg'])) for p in pars]
out=dict(nominal=nom,range={k:[float(np.min([s[k]['align_corr'] for s in sweep])),float(np.max([s[k]['align_corr'] for s in sweep]))] for k in ['blue','red']},
    sensitivity=sweep,
    warning='Exploratory fold candidate from published morphology; filter bands are independent exposures of the same sky, not independent lens systems. Peak reflectivity is not a parity observation; no PSF-matching or p-value.')
print(json.dumps({k:v for k,v in out.items() if k!='sensitivity'},indent=2))
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')

# Allow different stretch and choose it using only the blue outer peak profile.
a,b=nom['blue_anchors_deg']
offset=np.arange(-4.,4.01,.25)
held=np.arange(-63.,-46.99,1.)
slopes=np.arange(.55,1.651,.01)
def cc(vv,x,y):
    return float(np.corrcoef(np.interp(x,tt,vv),np.interp(y,tt,vv))[0,1])
v=profiles(4,2.54,2.94)
def trial(j):
    s=float(slopes[j])
    return dict(stretch=s,outer_blue=cc(v[0],a+offset,b-s*offset),
        blue_held=cc(v[0],held,b-s*(held-a)),red_held=cc(v[1],held,b-s*(held-a)))
grid=[trial(j) for j in range(len(slopes))]
out['stretch_outer_peak_only']=max(grid,key=lambda z:z['outer_blue'])
out['stretch_descriptive_bounds']={k:[min(row[k] for row in grid),max(row[k] for row in grid)] for k in ('blue_held','red_held')}
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
print(out['stretch_outer_peak_only'])
