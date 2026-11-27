"""Frozen Sunburst Table 2 light-only benchmark. See CRYSTAL_RESOLVED_TRANSFER_V1.md."""
from itertools import combinations
from pathlib import Path
import json,re,numpy as np
P=Path(__file__).resolve().parent
t=(P/'sunburst_inputs/sharon.txt').read_text().replace('−','-')
start=t.index('List of Lensing Constraints within the Sunburst Arc')
stop=t.index('List of Lensing Constraints from Secondary Lensed Galaxies',start)
matches=re.findall(r'(?m)(?<!\S)(\d{1,3})\.(\d{1,2})[a-z]?\s+(237\.\d{6})\s+(-78\.\d{6})',t[start:stop])
def sky(ra,dec):
 a,d=np.radians([ra,dec]); b,c=np.radians([237.53,-78.19]); k=np.sin(d)*np.sin(c)+np.cos(d)*np.cos(c)*np.cos(a-b)
 return np.rad2deg([np.cos(d)*np.sin(a-b)/k,(np.cos(c)*np.sin(d)-np.sin(c)*np.cos(d)*np.cos(a-b))/k])*3600
sets={}
for x,j,a,d in matches:
 x,j=int(x),int(j)
 if not 1<=x<=19: continue
 D=sets.setdefault(j,{})
 assert x not in D
 D[x]=sky(float(a),float(d))
assert len(sets)==12 and all(1 in v for v in sets.values())
res=[]
for a,b in combinations(sorted(sets),2):
 common=sorted(sets[a].keys()&sets[b].keys())
 if len(common)<7:continue
 for l,r in [(a,b),(b,a)]:
  X=np.array([sets[l][i] for i in common]); Y=np.array([sets[r][i] for i in common])
  qs=[]
  for i,k in enumerate(common):
   p=np.argsort(np.sum((X-X[i])**2,axis=1),kind='stable')
   ix=p[p!=i][:6]; assert i not in ix and len(ix)==6
   u,v=X[ix].mean(0),Y[ix].mean(0)
   xx,yy=X[ix]-u,Y[ix]-v
   aff,_,rank,_=np.linalg.lstsq(xx,yy,rcond=None);assert rank==2
   U,s,V=np.linalg.svd(xx.T@yy)
   q=np.diag([1,np.sign(np.linalg.det(aff))*np.linalg.det(U@V)])
   h=U@q@V*(s@q.diagonal())/np.sum(xx**2)
   shifts={n:(X[i]-u)@j+v-Y[i] for n,j in [('bhsm',h),('affine',aff)]}
   err={n:float(np.linalg.norm(w)) for n,w in shifts.items()}
   qs.append(dict(knot=k,training=[common[j] for j in ix],negative_parity=bool(np.linalg.det(aff)<0),train_condition=float(np.linalg.cond(xx)),error=err))
  rms={n:float(np.sqrt(np.mean([q['error'][n]**2 for q in qs]))) for n in err}
  res.append(dict(source=l,target=r,common=common,rms=rms,queries=qs,win=rms['bhsm']<rms['affine']))
  print(f'{l:2d}->{r:2d} {len(common):2d}',rms)
allq=[q for row in res for q in row['queries']]
stats={n:{'rms':float(np.sqrt(np.mean([q['error'][n]**2 for q in allq]))),'median':float(np.median([q['error'][n] for q in allq]))} for n in ['affine','bhsm']}
agg=1-(stats['bhsm']['rms']/stats['affine']['rms'])**2
wins=sum(res[i]['win'] and res[i+1]['win'] for i in range(0,len(res),2))
summary=dict(positions_n=sum(map(len,sets.values())),unordered_pairs=len(res)//2,both_directions_wins=wins,queries=len(allq),stats=stats,pooled_squared_error_gain=agg,
 passes=bool(agg>=.1 and stats['bhsm']['median']<stats['affine']['median'] and wins>len(res)/4))
print(summary)
(P/'sunburst_crystal_transfer.json').write_text(json.dumps(dict(summary=summary,pairs=res),indent=2)+'\n')
