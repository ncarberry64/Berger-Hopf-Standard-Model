"""Development counts screen; no calibrated exposure/background or detection claims."""
import numpy as np, json, math, warnings,re
from pathlib import Path
from astropy.table import Table
from astropy.io import fits
from astropy.wcs import WCS
from matplotlib.path import Path as Polygon
p=Path(__file__).parent
lens=np.array([69.562,-12.2874]); C=np.cos(np.radians(lens[1]))
using=['Sluse 67','Sluse 42','Wilson','foreground .1744','foreground .4185']
world=np.array([[69.550841,-12.272258],[69.559414,-12.276026],[69.5521,-12.2839],[69.548372,-12.280593],[69.549725,-12.301072]])
def to_xy(ra,dec):return np.column_stack((3600*C*(ra-lens[0]),3600*(dec-lens[1])))
def to_rd(xy):return (xy[:,0]/(3600*C)+lens[0],xy[:,1]/3600+lens[1])
ctr=to_xy(*world.T)
t=Table.read(p/'csc22scs.xml',format='votable')
src=to_xy(np.asarray(t['ra']),np.asarray(t['dec']))
src=src[np.linalg.norm(src,axis=1)>3]
gr=np.arange(-130,130,.65)+.325
grid=np.column_stack(tuple(a.ravel() for a in np.meshgrid(gr,gr)))
def rad(xy,z=(0,0)):return np.linalg.norm(xy-z,axis=1)
def wcs(h,i,j):
 w=WCS(naxis=2)
 w.wcs.ctype=[h['TCTYP'+str(k)] for k in (i,j)]
 w.wcs.crpix=[h['TCRPX'+str(k)] for k in (i,j)]
 w.wcs.crval=[h['TCRVL'+str(k)] for k in (i,j)]
 w.wcs.cdelt=[h['TCDLT'+str(k)] for k in (i,j)]
 return w
def mask(xy,quasar,src_radius):
 valid=(rad(xy)>quasar)&(rad(xy)<130)
 for z in src: valid&=rad(xy,z)>src_radius
 return valid
bins=np.arange(0,131,2.)
obs={}; injections={}
for f in sorted(p.glob('*/primary/*evt2.fits.gz')):
 oid=int(f.parent.parent.name)
 fov=next(p.parent.glob('*'+str(oid).zfill(5)+'_*fov1.fits.gz'))
 with fits.open(fov) as a:
  d=a[1].data[a[1].data['CCD_ID']==7][0]
  polygon=Polygon(np.column_stack((d['X'],d['Y']))[np.isfinite(d['X']+d['Y'])])
  w=wcs(a[1].header,1,2)
 for qw,sw in [(15,4),(25,6)]:
  gg=grid[mask(grid,qw,sw)]
  gp=np.column_stack(w.all_world2pix(*to_rd(gg),1))
  keep=polygon.contains_points(gp,radius=0)
  # Reject grid points within ~5 arcsec of the swept chip edge. Accept only
  # the eroded region in both event and geometric area calculations.
  for dx,dy in [(-10,0),(10,0),(0,-10),(0,10),(-7,-7),(7,-7),(-7,7),(7,7)]:
   keep &= polygon.contains_points(gp+(dx,dy))
  gg=gg[keep]
  with fits.open(f) as a:
   d=a[1].data
   d=d[(d['ccd_id']==7)& np.isin(d['grade'],[0,2,3,4,6])]
   w1=wcs(a[1].header,11,12)
   sky=to_xy(*w1.all_pix2world(d['x'],d['y'],1))
   sel=mask(sky,qw,sw)
   ep=np.column_stack(w.all_world2pix(*to_rd(sky[sel]),1))
   inside=polygon.contains_points(ep)
   for dx,dy in [(-10,0),(10,0),(0,-10),(0,10),(-7,-7),(7,-7),(-7,7),(7,7)]:
    inside &= polygon.contains_points(ep+(dx,dy))
   xy=sky[sel][inside]; en=d['energy'][sel][inside]
  den=np.histogram(rad(gg),bins)[0]
  ins={}; which_bin=np.searchsorted(bins,rad(gg),side="right")-1
  for lo,hi,band in [(500,2000,'soft'),(3000,7000,'hard')]:
   xy1=xy[(en>=lo)&(en<hi)]
   N=np.histogram(rad(xy1),bins)[0]
   res={}
   for i,z in enumerate(ctr):
    for R in (21.,42.052):
     num=np.histogram(rad(gg[rad(gg,z)<R]),bins)[0]
     pr=np.divide(num,den,out=np.zeros_like(den,dtype=float),where=den>0)
     m=float(N@pr); v=float(N@(pr*(1-pr)))
     n=int((rad(xy1,z)<R).sum())
     if band=='soft':
      for rc in (15,25):
       pix=(1+(rad(gg,z)/rc)**2)**(-1.5)
       ins[f'{using[i]}:{R}|{rc}']=float((pix*((rad(gg,z)<R).astype(float)-pr[which_bin])).sum()/pix.sum())
     res[using[i]+':'+str(R)]=[n,m,v]
     res[using[i]+':'+str(R)]=[n,m,v]
   obs[f'{oid}:{qw}:{band}']=res
  injections[f'{oid}:{qw}']=ins
res={}
for which in ('all','full','half','original','later','later_a','later_b'):
 ids={'all':[7761,11550,11551,11552,14489,14490,14491,14492,14493,14494,23798],
      'full':[7761,23798],'half':[11550,11551,11552,14489,14490,14491,14492,14493,14494],
      'original':[7761],'later':[11550,11551,11552,14489,14490,14491,14492,14493,14494,23798],
      'later_a':[11550,11552,14489,14491,14493],'later_b':[11551,14490,14492,14494,23798]}[which]
 for qw in (15,25):
  for band in ('soft','hard'):
   tab=[obs[f'{o}:{qw}:{band}'] for o in ids]
   dd={}
   for k in tab[0]:
    n,m,v=np.array([a[k] for a in tab]).sum(axis=0)
    dd[k]=[float(n),float(m),float((n-m)/math.sqrt(v)) if v else None]
   res[f'{which}:{qw}:{band}']=dd
(p/'counts_triage.json').write_text(json.dumps({'scope':'uncalibrated geometric counts diagnostic; standardized conditional residuals are not detection significances','stacked':res,'perobs':obs,'conditional_template_retention':injections},indent=2)+'\n')
for k,v in res.items():
 if k.split(':')[0] in ['all','full','original','later','later_a','later_b']: print(k,{n:tuple(round(a,2) for a in v[n]) for n in v if v[n][-1] is not None})
