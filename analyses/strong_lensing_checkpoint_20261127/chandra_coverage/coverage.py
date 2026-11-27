import sys,re,numpy as np, json,gzip,hashlib
from pathlib import Path
from matplotlib.path import Path as Poly
p=Path(__file__).parent
pts=np.array([[69.550841,-12.272258],[69.559414,-12.276026],[69.5620,-12.2874],[69.548372,-12.280593],[69.549725,-12.301072],[69.5521,-12.2839]])
names=['Sluse67','Sluse42','lens','foreground_z01744','foreground_z04185','Wilson37']
R=float(sys.argv[1]) if len(sys.argv)>1 else 42.05209195056528
v=(np.arange(513)-256)*R/256
x,y=np.meshgrid(v,v); sel=x*x+y*y<=R*R
sample=np.c_[x[sel],y[sel]]
def header(b,off):
 h={}
 for i in range(off,len(b),80):
  s=b[i:i+80].decode('ascii')
  if s[:8].strip()=='END':return h,((i+80+2879)//2880)*2880
  if s[8:10]!='= ':continue
  rhs=s[10:].strip()
  if rhs.startswith("'"):v=rhs[1:].split("'")[0].strip()
  else:
   v=rhs.split('/')[0].strip()
   try:v=float(v.replace('D','E')) if any(c in v for c in '.DE') else int(v)
   except ValueError:pass
  h[s[:8].strip()]=v
 raise ValueError
def ang_to_pix(ra,dec,h):
 a,b,x,y=np.deg2rad([ra,dec,h['TCRVL1'],h['TCRVL2']])
 d=a-x;zero=np.sin(b)*np.sin(y)+np.cos(b)*np.cos(y)*np.cos(d)
 en=np.rad2deg([np.cos(b)*np.sin(d)/zero,(np.sin(b)*np.cos(y)-np.cos(b)*np.sin(y)*np.cos(d))/zero])
 return en/np.array([h['TCDLT1'],h['TCDLT2']])+np.array([h['TCRPX1'],h['TCRPX2']])
out=[]
for f in sorted(p.glob('*_fov1.fits.gz')):
 b=gzip.decompress(f.read_bytes()); h,k=header(b,0); assert h['NAXIS']==0
 h,k=header(b,k); assert h['EXTNAME']=='FOV' and 'TAN' in str(h.values())
 n=int(h['TFORM1'][:-1]); cols=[]
 for j in range(h['NAXIS2']):
  r=b[k+j*h['NAXIS1']:k+(j+1)*h['NAXIS1']]; shape=r[16*n:16*n+16].decode('ascii').strip()
  assert shape.lower()=='polygon',shape
  x=np.frombuffer(r[:8*n],dtype='>f8'); y=np.frombuffer(r[8*n:16*n],dtype='>f8')
  good=np.isfinite(x+y); assert good.sum()>=4
  xy=np.c_[x[good],y[good]]
  cols.append((Poly(xy), int.from_bytes(r[-2:],'big'),xy))
 offsets=sample/(np.array([h['TCDLT1'],h['TCDLT2']])*3600)
 row=dict(obs=int(re.search(r'acisf(\d+)_',f.name).group(1)), time_ks=h['LIVETIME']/1000,regions={})
 for name,zz in zip(names,pts):
  z=ang_to_pix(*zz,h)
  region=np.zeros(len(sample),dtype=bool)
  chips={}
  for pp,chip,xy in cols:
   r=pp.contains_points(z+offsets); chips[chip]=round(float(r.mean()),7); region|=r
  best=0
  for pp,_,xy in cols:
   if pp.contains_point(z):
    d=np.diff(xy,axis=0); a=xy[:-1]
    t=np.sum((z-a)*d,axis=1)/np.maximum((d*d).sum(axis=1),1e-30)
    u=a+np.clip(t[:,None],0,1)*d
    best=max(best,np.linalg.norm(u-z,axis=1).min()*.492)
  row['regions'][name]=[float(region.mean()),float(best),[cip for pp,cip,_ in cols if pp.contains_point(z)], {c:f for c,f in chips.items() if f>0}]
 row['sha256']=hashlib.sha256(f.read_bytes()).hexdigest()
 out.append(row)
print(json.dumps(dict(radius_arcsec=R,scope='FOV union / sampled geometric area only; area-weighted nominal livetime is not an exposure map.',rows=out,sums_ks={n:sum(a['time_ks']*a['regions'][n][0] for a in out)for n in names}),indent=2))
