from astropy.io import fits
from astropy.wcs import WCS
import urllib.request as u,concurrent.futures as cf,numpy as np
def cut(b):
 name=f'jw01198-o007_t005_nircam_clear-{b}_i2d.fits'; url='https://mast.stsci.edu/api/v0.1/Download/file?uri=mast:JWST/product/'+name
 def rng(a,z):
  h={'Range':f'bytes={a}-{z}'}
  for i in range(3):
   try:
    r=u.urlopen(u.Request(url+f"&rangeid={a}-{z}",headers=h),timeout=18)
    with r:
     assert r.headers.get('Content-Range','').startswith(f'bytes {a}-{z}/'),(b,r.status,r.headers.get('Content-Range'))
     c=r.read()
    assert len(c)==z-a+1
    return c
   except Exception as e: print(b,a,z,i,e,flush=True)
  raise IOError(a,z)
 def hdr(o):
  buf=rng(o,o+34559)
  i=next(i for i in range(0,len(buf),80) if buf[i:i+8]==b'END     ')
  l=((i+80+2879)//2880)*2880
  return fits.Header.fromstring(buf[:l].decode()),o+l
 o=0; result=[]
 for ix in range(8):
  h,d=hdr(o); en=h.get('EXTNAME',''); dim=[h[f'NAXIS{i+1}'] for i in range(h['NAXIS'])]
  if en=='SCI':
   w=WCS(h); x,y=w.all_world2pix(69.5619,-12.28745,0); N=321 if b in ['f115w','f150w'] else 181
   a=int(x)+int(1.25/np.sqrt(abs(np.linalg.det(w.pixel_scale_matrix)))/3600)-N//2;b0=int(y)-N//2
   wh=w.slice((slice(b0,b0+N),slice(a,a+N))).to_header(relax=True)
   wh['BUNIT']=h['BUNIT']
  if en in ['SCI','ERR','WHT']:
   ww=dim[0]; start=d+4*(b0*ww+a);end=start+4*((N-1)*ww+N)-1
   zz=np.ndarray((N,N),buffer=rng(start,end),dtype='>f4',strides=(ww*4,4)).astype('f4')
   result.append(fits.ImageHDU(zz,wh,name=en))
  if en=='WHT':break
  o=d+((int(np.prod(dim,dtype=int))*abs(h['BITPIX'])//8+2879)//2880)*2880 if dim else d
 fits.HDUList([fits.PrimaryHDU(),*result]).writeto(b+'.fits',overwrite=True,checksum=True);print(b,'SAVED',flush=True)
with cf.ThreadPoolExecutor(4) as p:list(p.map(cut,['f115w','f150w','f277w','f356w']))
