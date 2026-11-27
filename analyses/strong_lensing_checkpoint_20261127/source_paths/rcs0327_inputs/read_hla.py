import numpy as np
from pathlib import Path
from PIL import Image
P=Path(__file__).resolve().parent
def fits(p):
 with p.open('rb') as f:
  ads=[]
  while not any(c.startswith('END     ') for c in ads):
   b=f.read(2880); assert len(b)==2880
   ads.extend(b[i:i+80].decode('ascii') for i in range(0,2880,80))
  h={c[:8].strip():c[10:].split('/')[0].strip().strip("'") for c in ads if c[8:10]=='= '}
  assert int(h['BITPIX'])==-32 and int(h['NAXIS'])==2
  return h,np.fromfile(f,dtype='>f4',count=int(h['NAXIS1'])*int(h['NAXIS2'])).reshape(int(h['NAXIS2']),int(h['NAXIS1']))
if __name__=='__main__':
 h,a=fits(P/'hla_f606w.fits')
 for l,(x,y,R) in [('A',(1100,1180,160)),('B',(880,200,150)),('C',(900,900,100))]:
  s=a[y-R:y+R,x-R:x+R][::-1]
  v=np.arcsinh(np.nan_to_num(s)/.03); im=Image.fromarray(np.uint8(255*np.clip((v+.2)/4,0,1)))
  im.save('/tmp/rcs_cal_'+l+'.png')
