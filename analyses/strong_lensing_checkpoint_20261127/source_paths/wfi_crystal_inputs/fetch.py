"""Extract calibrated JWST SCI cutouts via verified HTTP byte ranges."""
from pathlib import Path
import numpy as np, urllib.request as u,re,itertools,time
from concurrent.futures import ThreadPoolExecutor
P=Path(__file__).parent
def cut(b):
 n=f'jw01198-o004_t004_nircam_clear-{b}_i2d.fits'
 base='https://mast.stsci.edu/api/v0.1/Download/file?uri=mast:JWST/product/'+n
 def get(a,z):
  for i in range(3):
   try:
    h={'Range':f'bytes={a}-{z}'}
    with u.urlopen(u.Request(base+f'&rangeid={a}-{z}',headers=h),timeout=15) as r:
     assert r.headers.get('Content-Range','').startswith(f'bytes {a}-{z}/'),(r.status,r.headers.get('Content-Range'))
     c=r.read()
    assert len(c)==z-a+1
    return c
   except Exception as e: print(b,a,z,i,e,flush=True)
  raise OSError(b,a,z)
 def hdr(o):
  c=get(o,o+34559)
  cards=[c[i:i+80].decode('ascii',errors='replace') for i in range(0,len(c)-79,80)]
  i=next(i for i,v in enumerate(cards) if v.startswith('END     '))
  return cards[:i],o+((80*(i+1)+2879)//2880)*2880
 o=0
 for _ in range(6):
  cards,d=hdr(o)
  h={c[:8].strip():c[10:].split('/')[0].strip().strip("'").strip() for c in cards if c[8:10]=='= '}
  ns=[int(h[f'NAXIS{i+1}']) for i in range(int(h['NAXIS']))]
  if h.get('EXTNAME')=='SCI':break
  o=d+((int(np.prod(ns))*abs(int(h['BITPIX']))//8+2879)//2880)*2880 if ns else d
 else:raise ValueError('SCI HDU absent')
 xySky=np.radians([308.425675,-47.39560]); a0,b0=np.radians([float(h['CRVAL1']),float(h['CRVAL2'])]); a,b0s=xySky
 K=np.sin(b0)*np.sin(b0s)+np.cos(b0)*np.cos(b0s)*np.cos(a-a0)
 xy=np.rad2deg([np.cos(b0s)*np.sin(a-a0)/K,(np.cos(b0)*np.sin(b0s)-np.sin(b0)*np.cos(b0s)*np.cos(a-a0))/K])
 cd=np.array([[float(h[f'CDELT{i}'])*float(h[f'PC{i}_{j}']) for j in (1,2)] for i in (1,2)])
 xc,yc=np.linalg.solve(cd,xy)+np.array([float(h['CRPIX1']),float(h['CRPIX2'])])-1
 pix=3600*np.sqrt(abs(np.linalg.det(cd))); N=2*int(np.ceil(4/pix))+1
 x,y=np.round([xc-N//2,yc-N//2]).astype(int)
 assert 0<=x and 0<=y and x+N<=ns[0] and y+N<=ns[1]
 off=d+4*(y*ns[0]+x); Z=get(off,off+4*((N-1)*ns[0]+N)-1)
 z=np.ndarray((N,N),buffer=Z,dtype='>f4',strides=(4*ns[0],4))
 keys={'NAXIS1':N,'NAXIS2':N,'CRPIX1':float(h['CRPIX1'])-x,'CRPIX2':float(h['CRPIX2'])-y}
 out=[v[:10]+str(keys[v[:8].strip()]).rjust(20).ljust(70) if v[:8].strip() in keys else v for v in cards]
 def block(q):return q+b' '*((-len(q))%2880)
 def header(lst):return block((''.join(c.ljust(80)[:80] for c in lst)+'END'.ljust(80)).encode('ascii','replace'))
 (P/(b+'.fits')).write_bytes(header(['SIMPLE  =                    T','BITPIX  =                    8','NAXIS   =                    0','EXTEND  =                    T'])+header(out)+block(z.tobytes()))
 print(b,n,(x,y,N),pix,flush=True)
with ThreadPoolExecutor(4) as t: list(t.map(cut,('f115w','f150w','f277w','f356w')))
