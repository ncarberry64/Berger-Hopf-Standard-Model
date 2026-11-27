"""Photometric axis audit on archived public HST imaging. No image-position fitting."""
from pathlib import Path
import json
import numpy as np
from scipy.ndimage import map_coordinates,gaussian_filter
P=Path(__file__).resolve().parent
N=P.parent/'visible_mass_envelope_20261126/external_weak/jackpot_neighbor/u_phot'
def fits(path):
    d=path.read_bytes(); vals={}
    for j in range(0,len(d),80):
        a=d[j:j+80].decode('ascii','replace')
        if a[:8].strip()=='END': break
        if a[8:10]=='= ':
            try: vals[a[:8].strip()]=float(a[10:].split('/')[0])
            except ValueError:pass
    off=((j+80+2879)//2880)*2880
    sh=int(vals['NAXIS2']),int(vals['NAXIS1'])
    assert vals['BITPIX']==-32
    data=np.frombuffer(d,dtype='>f4',count=sh[0]*sh[1],offset=off).reshape(sh).astype(float)
    cd=np.array([[vals[f'CD{i}_{j}'] for j in (1,2)] for i in (1,2)])
    return vals,data,cd
target=np.array([146.73617048,10.11469530])
angle=np.linspace(0,2*np.pi,192,endpoint=False)
direction=np.vstack([np.sin(angle),np.cos(angle)]) # Astronomical PA, north through east
def axial_mean(q):
    v=np.asarray(q); z=np.mean(v/np.abs(v))
    return float((np.degrees(np.angle(z))/2)%180),float(abs(z))
out={}
for name in ['f814w','f160w']:
    vals,data,cd=fits(N/(name+'.fits'))
    dec=np.deg2rad(vals['CRVAL2'])
    ra_diff=np.deg2rad(target[0]-vals['CRVAL1'])
    dt=np.deg2rad(target[1])
    div=np.sin(dt)*np.sin(dec)+np.cos(dt)*np.cos(dec)*np.cos(ra_diff)
    tan=np.rad2deg([np.cos(dt)*np.sin(ra_diff)/div,(np.sin(dt)*np.cos(dec)-np.cos(dt)*np.sin(dec)*np.cos(ra_diff))/div])
    p=np.linalg.solve(cd,tan)+np.array([vals['CRPIX1']-1,vals['CRPIX2']-1])
    assert min(p)>50 and max(p)<min(data.shape)-50
    key=np.rint(p).astype(int)
    crop=gaussian_filter(data,1.2)[key[1]-14:key[1]+15,key[0]-14:key[0]+15]
    delta=np.array(np.unravel_index(np.argmax(crop),crop.shape))[::-1]-14+key-p
    offsky=3600*cd@delta
    co=[]
    for disp in ([0,0],[.03,0],[-.03,0],[0,.03],[0,-.03],offsky):
        z=[]
        for r in np.linspace(.35,1.05,15):
            xy=p[:,None]+np.linalg.solve(cd,(r*direction+np.array(disp)[:,None])/3600)
            y=map_coordinates(data,xy[::-1],order=3)
            z.append(np.mean(y*np.exp(2j*angle)))
        co.append(axial_mean(z))
    out[name]=dict(pixel_center_FITS1=(p+1).tolist(),inner_photometric_PA_deg=co[0][0],
                         ring_phase_coherence=co[0][1],offset_center_controls=co[1:-1],smoothed_bright_peak_offset_E_N_arcsec=offsky.tolist(), peak_recentered_PA_deg=co[-1][0])
g=np.array(json.loads((P/'jackpot_annular_tide.json').read_text())['variants']['whole_band']['both']['g'])
pa=(90-np.rad2deg(np.arctan2(g[1],g[0]))/2)%180
def off(a,b):return abs((a-b+90)%180-90)
out['earlier_lensing_only_tide_PA_deg']=float(pa)
out['tide_vs_light_axis_offsets_deg']={k:off(pa,v['inner_photometric_PA_deg']) for k,v in out.items() if k in ['f814w','f160w']}
(P/'jackpot_independent_axis.json').write_text(json.dumps(out,indent=2)+'\n')
print(out)
