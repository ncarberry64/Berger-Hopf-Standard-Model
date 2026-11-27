"""Foreground-mass-free optical quality audit for SNELLS controls, not a lens fit."""
import numpy as np
from pathlib import Path
from scipy.ndimage import gaussian_filter,map_coordinates
from scipy.spatial import cKDTree
import json
P=Path(__file__).parent/'snl_inputs'

def fits_sci(path):
    ptr=0
    with open(path,'rb') as f:
        while True:
            h={}
            while True:
                b=f.read(2880)
                if len(b)!=2880: raise EOFError(path)
                stop=False
                for i in range(0,2880,80):
                    card=b[i:i+80].decode('ascii')
                    if card.startswith('END     '): stop=True;break
                    if card[8:10]=='= ':
                        v=card[10:].strip()
                        if v.startswith("'"): v=v.split("'")[1].strip()
                        else:
                            v=v.split('/')[0].strip()
                            try:v=float(v.replace('D','E'));v=int(v) if v.is_integer() else v
                            except ValueError:pass
                        h[card[:8].strip()]=v
                if stop:break
            n=h.get('NAXIS',0); b=h['BITPIX']; size=int((np.prod([h[f'NAXIS{i+1}'] for i in range(n)]) if n else 0)*abs(b)//8)
            if h.get('EXTNAME')=='SCI':
                assert n==2 and b==-32
                arr=np.memmap(path,mode='r',dtype='>f4',offset=f.tell(),shape=(h['NAXIS2'],h['NAXIS1']))
                return arr,h
            f.seek(((size+2879)//2880)*2880,1)

def sky_cutout(file,ra,dec,scale=.04,halfspan=5.3):
    d,h=fits_sci(file)
    dc,ac=np.deg2rad([dec,h['CRVAL1']]); dr=np.deg2rad([ra])[0]-ac; dc0=np.deg2rad(h['CRVAL2'])
    dis=np.sin(dc0)*np.sin(dc)+np.cos(dc0)*np.cos(dc)*np.cos(dr)
    t=np.rad2deg([np.cos(dc)*np.sin(dr)/dis,(np.cos(dc0)*np.sin(dc)-np.sin(dc0)*np.cos(dc)*np.cos(dr))/dis])
    cd=np.asarray([[h[f'CD{i}_{j}'] for j in (1,2)] for i in (1,2)])
    u=np.round(halfspan/scale).astype(int); x=np.arange(-u,u+1)*scale
    yy,xx=np.meshgrid(x,x,indexing='ij')
    v=(np.linalg.inv(cd)@(np.vstack([xx.ravel(),yy.ravel()])/3600+t[:,None])+np.array([h['CRPIX1']-1,h['CRPIX2']-1])[:,None]).reshape(2,*xx.shape)
    # A small cutout only. Use native cropped pixels before resampling.
    lo=np.floor(v.min(axis=(1,2))).astype(int)-3
    hi=np.ceil(v.max(axis=(1,2))).astype(int)+4
    carr=d[lo[1]:hi[1],lo[0]:hi[0]].astype(float)
    arr=map_coordinates(carr,(v[1]-lo[1],v[0]-lo[0]),order=1)
    return x,arr

TARGETS={1:(315.1197416667,-42.42313055556,['03*f336w','03*f814w']),2:(25.42625,-7.591111111111,['04*f390w','04*f814w'])}
def load(t):
    ra,dec,pats=TARGETS[t]
    dat=[sky_cutout(next(P.glob('hst_14210_'+p+'*_drc.fits')),ra,dec) for p in pats]
    return dat[0][0],*[a for _,a in dat]
def plot():
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(2,4,figsize=(14,7),layout='constrained')
    for i in [1,2]:
        x,u,v=load(i)
        e=[x.min(),x.max(),x.min(),x.max()]
        for a,img,ti in zip(ax[i-1],[u,v,u-gaussian_filter(u,6),v-gaussian_filter(v,6)],['UV','I','UV hi pass','I hi pass']):
            a.imshow(img,origin='lower',extent=e,vmin=np.percentile(img,10),vmax=np.percentile(img,94),cmap='gray')
            a.invert_xaxis();a.set_title(f'SNL-{i} {ti}');a.set_xticks(np.arange(-5,6));a.set_yticks(np.arange(-5,6));a.grid(alpha=.16)
    fig.savefig('/tmp/snl_raw.png',dpi=125)
if __name__=='__main__':plot()
