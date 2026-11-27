"""Frozen HE0435 benchmark transferred to WFI 2033−4723."""
from pathlib import Path
P=Path(__file__).resolve().parent
src=(P/'he0435_crystal_holdout.py').read_text().split('sweep=[]')[0]
# Change only input data and search centers, which are supplied by the
# reference band and image identifications. Centroid model, apertures,
# sensitivity grid and fit algorithm remain identical.
src=src.replace("P.parent/'common_host_20261126'","P/'wfi_crystal_inputs'").replace("hst+[1.26,.195]+[1.1706,.5665]","wfi_seeds")
exec(src)
ra0,dec0=308.425675,-47.39560
d,h=fits_sci(P/'wfi_crystal_inputs/f115w.fits')
x=coords(h,d.shape)
import sys
if '--inventory' in sys.argv:
 from scipy.ndimage import maximum_filter
 sel=(d==maximum_filter(d,size=15))&(np.linalg.norm(x,axis=-1)<2.9)
 inds=np.argwhere(sel)
 for q in sorted(inds,key=lambda a:d[tuple(a)],reverse=True)[:14]:
  z=tuple(q)
  print(np.round(x[z],5),float(d[z]))
 sys.exit()
# Absolute region seeds are read from light in F115W, before the
# three target-band image measurements. Never use target centers to seed.
wfi_seeds=np.array(json.loads((P/'wfi_crystal_inputs/wfi_seed_regions.json').read_text())['f115w_seeds_EN'])
labels=['A1','A2','B','C']
all_rows=[]
for rad in (.15,.19,.24):
 for profile in ('gaussian','moffat'):
  for bg in (1,2):
   pos={b:fit_all(b,rad,profile,bg) for b in bands}
   row={}
   for b in list(bands)[1:]:
    x,y=pos['f115w'],pos[b]
    row[b]={}
    for i,name in enumerate(labels):
     train=np.arange(len(x))!=i
     pred=map_pred(x[train],y[train],x[i],'translate')
     row[b][name]=((y[i]-pred)*1000).tolist()
   all_rows.append(dict(rad=rad,profile=profile,bg=bg,positions={b:p.tolist() for b,p in pos.items()},errors_EN_mas=row))
results={}
for band in list(bands)[1:]:
 results[band]={}
 for k in labels:
  q=np.array([v['errors_EN_mas'][band][k] for v in all_rows])
  norms=np.linalg.norm(q,axis=1)
  results[band][k]={'min_med_max_mas':np.percentile(norms,[0,50,100]).tolist(),'under5':int(sum(norms<5)),'median_EN_mas':np.median(q,axis=0).tolist()}
 print(band,results[band])
(P/'wfi2033_crystal_transfer.json').write_text(json.dumps(dict(frozen_reference_filter='F115W',pass_rule_mas_strict=5,results=results,details=all_rows),indent=2)+'\n')
