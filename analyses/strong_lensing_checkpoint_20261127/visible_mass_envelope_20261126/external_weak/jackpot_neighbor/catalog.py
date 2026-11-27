import re,struct,math,json
from pathlib import Path
import numpy as np
def tables(p):
 b=p.read_bytes()
 out={}
 for j in range(0,len(b),2880):
  if b[j:j+8]!=b'XTENSION':continue
  h={}
  for k in range(j,len(b),80):
   s=b[k:k+80].decode('ascii'); key=s[:8].strip()
   if key=='END':break
   if k==j and 'BINTABLE' not in s:break
   if s[8:10]=='= ':h[key]=s[10:].split('/')[0].strip().strip("'").strip()
  if not h or h.get("XTENSION")!="BINTABLE":continue
  d=((k+80+2879)//2880)*2880
  items=[];offsets=[]; t=0
  for i in range(1,1+int(h['TFIELDS'])):
   n,c=re.fullmatch(r'(\d*)([A-IJKL])',h['TFORM'+str(i)]).groups();n=int(n or 1)
   fmt={'A':f'S{n}','B':'u1','L':'S1','D':'>f8','E':'>f4','I':'>i2','J':'>i4','K':'>i8'}[c]
   items.append((h['TTYPE'+str(i)],fmt if n==1 or c=='A' else (fmt,(n,))));offsets.append(t)
   t+=np.dtype(fmt).itemsize*(1 if c=='A' else n)
  assert t==int(h['NAXIS1'])
  out[h['EXTNAME']]=np.frombuffer(b, dtype=np.dtype(items),count=int(h['NAXIS2']),offset=d)
 return out
def dist(a,b,c,d):
 return 3600*np.degrees(2*np.arcsin(np.sqrt(np.sin(np.radians(b-d)/2)**2+np.cos(np.radians(b))*np.cos(np.radians(d))*np.sin(np.radians(a-c)/2)**2)))
lens=(146.73617048,10.11469530); plume=(146.733004235044,10.1036436603437)
out={}
for p in sorted(Path('.').glob('desi*.fits')):
 t=tables(p); F=t['FIBERMAP']; Z=t['REDSHIFTS']; z={int(row['TARGETID']):row for row in Z}
 dr=dist(F['TARGET_RA'],F['TARGET_DEC'],*lens);ds=dist(F['TARGET_RA'],F['TARGET_DEC'],*plume)
 rows=[]
 for i in np.where(dr<=300)[0]:
  f=F[i];id=int(f['TARGETID']); zz=z[id]
  rows.append(dict(id=id,ra=float(f['TARGET_RA']),dec=float(f['TARGET_DEC']),arcsec=float(dr[i]),plume_arcsec=float(ds[i]),z=float(zz['Z']),zerr=float(zz['ZERR']),zwarn=int(zz['ZWARN']),type=zz['SPECTYPE'].decode().strip(),dchi2=float(zz['DELTACHI2'])))
 rows.sort(key=lambda r:r['arcsec'])
 out[p.name]=rows
 print(p.name,'total',len(F),'nearest plume',min(ds))
 for r in rows:
  if r['plume_arcsec']<4 or abs(r['z']-.2219305)<.02: print(r)
print('plume-lens',dist(*plume,*lens))
Path('desi_cone.json').write_text(json.dumps(out,indent=2)+'\n')
