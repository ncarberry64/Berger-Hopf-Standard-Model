"""Public DR18 spectroscopy; luminosity proxy, not a complete census."""
import csv,json,io,urllib.parse as p,urllib.request as req
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from scipy.integrate import quad
import numpy as np
root=Path(__file__).resolve().parent
base='https://skyserver.sdss.org/dr18/SkyServerWS/SearchTools/SqlSearch?'
def run(a):
 name,ra,d,z=a
 path=root/'external_weak/sdss_lens_cones'/f'{name}.csv'
 try:
  if path.exists(): x=path.read_text()
  else:
   r=299792.458/70*quad(lambda zz:(.3*(1+zz)**3+.7)**-.5,0,z)[0]/(1+z)
   arc=min(18.,np.degrees(1.0/r)*60)
   s=f"select s.ra,s.dec,s.z,p.modelMag_r,p.modelMag_g from dbo.fGetNearbySpecObjEq({ra},{d},{arc}) as n join SpecObj as s on n.specObjID=s.specObjID left join PhotoObjAll as p on p.objID=s.bestObjID where s.class='GALAXY' and s.zWarning=0 and abs(s.z-{z})<0.012"
   with req.urlopen(base+p.urlencode({'cmd':s,'format':'csv'}),timeout=12) as f: x=f.read().decode()
   if 'modelMag_r' not in x:raise ValueError(x[:100])
   path.write_text(x)
  return name,list(csv.DictReader(io.StringIO('\n'.join(l for l in x.splitlines() if not l.startswith('#')))))
 except Exception as e:return name,{'error':str(e)}
def main():
 lis=[]
 names=set(json.load(open(root/'weighted_environment_holdout.json'))['sample'])
 for r in csv.DictReader((root/'external_weak/tdcosmo_LineOfSightData.csv').open()):
  n=r['#name'].replace('-','−')
  if n in names or '0946+1006' in n:
   lis.append((r['#name'],float(r['ra']),float(r['dec']),float(r['zd'])))
 if not any('0946+1006' in x[0] for x in lis):lis.append(('SDSSJ0946+1006',146.73617048,10.11469530,.2219305))
 (root/'external_weak/sdss_lens_cones').mkdir(exist_ok=True)
 with ThreadPoolExecutor(max_workers=5) as p:d=dict(p.map(run,lis))
 ans={t[0]:dict(ra=t[1],dec=t[2],z=t[3],rows=d[t[0]]) for t in lis}
 (root/'external_weak/sdss_lens_environment.json').write_text(json.dumps(ans,indent=2)+'\n')
 print('success',sum(isinstance(k,list) for k in d.values()),'failed',[k for k,v in d.items() if isinstance(v,dict)])
if __name__=='__main__':main()
