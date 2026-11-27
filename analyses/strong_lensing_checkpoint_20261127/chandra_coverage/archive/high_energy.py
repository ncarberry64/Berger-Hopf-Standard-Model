"""Particle-rate time-stability diagnostic, not a calibrated sky-background fit."""
from pathlib import Path
from astropy.io import fits
from scipy.stats import chi2
import numpy as np,json
p=Path(__file__).parent
res={}
for f in sorted(p.glob('*/primary/*evt2.fits.gz')):
 oid=int(f.parent.parent.name)
 with fits.open(f) as a:
  d=a['EVENTS'].data
  gt=next(g.data for g in a[2:] if g.name=='GTI' and g.header.get('CCD_ID')==7)
  s,e=gt['START'],gt['STOP']
  assert len(s)==1
  sel=(d['ccd_id']==7)&np.isin(d['grade'],[0,2,3,4,6])
  t=d['time'][sel & (d['energy']>=9500) & (d['energy']<12000)]
  time=np.linspace(s[0],e[0],max(4,int((e[0]-s[0])/1800))+1)
  k=np.histogram(t,time)[0]; total=int(k.sum()); exp=np.diff(time)
  mu=total*exp/exp.sum()
  x=float(np.sum((k-mu)**2/mu))
  res[oid]={'gti_time_s':float(e[0]-s[0]),'bins':k.tolist(),'avg_count_rate':float(total/exp.sum()),
            'ratio_max_to_min':float(k.max()/k.min()),'p_steady_poisson_unadjusted':float(chi2.sf(x,len(k)-1)),
            'max_abs_z':float(np.max(np.abs(k-mu)/np.sqrt(mu)))}
print(json.dumps(res,indent=2))
