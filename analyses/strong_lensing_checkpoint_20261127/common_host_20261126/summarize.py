import numpy as np,json,itertools
from pathlib import Path
summary={}
for f in sorted(Path('.').glob('*matched.json')):
 rows=json.loads(f.read_text()); band=rows[0]['band']
 assert len(rows)==64,f
 out=[]
 for anc,g,psf,w in itertools.product([False,True],[5,65],[.93,1.12],[.043,.065]):
  aa=[a for a in rows if (a['anchor'],a['g4'],a['psf'],a['width'])==(anc,g,psf,w)]
  assert len(aa)==4 and all(a['nodes']==aa[0]['nodes'] for a in aa)
 for anc in [False,True]:
  results={}
  for j in 'ABCD':
   r=[a for a in rows if a['anchor']==anc and a['held']==j]
   g=np.array([a['frac_gain'] for a in r])
   results[j]=dict(positive_gain=int(np.sum(g>0)),median_gain=float(np.median(g)),gain_range=[float(g.min()),float(g.max())])
   for k in ('samples','joint','baseline','detail_to_residual','random_source_recovery','macro_miss_mas'):
    results[j][k]=float(np.median([a[k] for a in r]))
   for k in ('held_local_shift_yx_mas','shift20_to_residual'):
    results[j][k]=np.nanmedian([a[k] for a in r],axis=0).tolist()
  groups=[r for r in rows if r['anchor']==anc]; d=[r for r in groups if r['held']=='D']
  def rank(value,t):
   return 1+sum(v[value]>t[value] for v in groups if all(v[k]==t[k] for k in ('g4','psf','width')))
  out.append(dict(point_anchored=anc,images=results,D_rank_gain=[rank('frac_gain',t) for t in d],D_rank_raw_error=[rank('joint',t) for t in d]))
 summary[band]=out
 print(band,[(round(z['images']['D']['median_gain'],3),z['images']['D']['positive_gain'],z['images']['D']['held_local_shift_yx_mas'],z['images']['D']['shift20_to_residual'],z['D_rank_gain'],z['D_rank_raw_error']) for z in out])
Path('summary.json').write_text(json.dumps(summary,indent=2)+'\n')
