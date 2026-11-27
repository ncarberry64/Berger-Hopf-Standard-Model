"""Synthetic light-only positive controls. No astronomical data or foreground mass."""
import numpy as np
from scipy.ndimage import gaussian_filter
import json
def simulate(dx=.01):
 y,x=np.mgrid[-3:3+dx/2:dx,-3:3+dx/2:dx]
 def g(u,v,sx,sy): return np.exp(-.5*((u/sx)**2+(v/sy)**2))
 # Each B pixel samples the same source as A at u=-x/1.25, v=y/.96.
 # The clean B image is mirrored, with total area ratio 1.20.
 def components(u,v):
  return (g(u+.45,v+.20,.44,.27)+.68*g(u-.41,v-.29,.37,.25),
      .65*g(u+.10,v-.03,.075,.075))
 ext,core=components(x,y)
 ub,vb=-x/1.25,y/.96
 extB,coreB=components(ub,vb)
 def ps(im,sig): return gaussian_filter(im,sig/dx)
 mask=(x/1.2)**2+(y/.90)**2<=1
 maskB=(ub/1.2)**2+(vb/.90)**2<=1
 bands=[.50,.85]
 outputs={}
 for scenario in ['clean','small_static_warp','selective_dimming','compact_boost','unmodeled_blur','mixed']:
  geom=scenario in ['small_static_warp','mixed']
  dust=scenario in ['selective_dimming','mixed']
  compact=scenario in ['compact_boost','mixed']
  ue=ub-(.13*g(ub+.45,vb+.20,.37,.31) if geom else 0.)
  e,c=components(ue,vb)
  obs={}
  for t in range(2):
   for wave in bands:
    A=ps(ext+core,.055); cleanB=ps(extB+coreB,.075)
    attenuation=np.exp(-.22*(wave/.55)**-1.3*(.4+.6*g(ub+.30,vb+.10,.8,.7))) if dust else 1.
    boost=1+([1.4,.35][t]*(.50/wave)**.65 if compact else 0.)
    B=ps((e+boost*c)*attenuation,.145 if scenario=='unmodeled_blur' else .075)
    F=lambda image,roi: float(image[roi].sum()*dx**2)
    row={'aperture_ratio':F(B,maskB)/F(A,mask),'fractional_residual_vs_clean':F(B,maskB)/F(cleanB,maskB)-1,
      'resolved_rms_fraction_of_clean_rms':float(np.linalg.norm((B-cleanB)[maskB])/np.linalg.norm(cleanB[maskB]))}
    obs[f'{t}:{wave}']=row
  outputs[scenario]=obs
 return outputs
if __name__=='__main__':
 a=simulate(); b=simulate(.005)
 for s,x in a.items():
  for k,v in x.items():
   assert abs(v['fractional_residual_vs_clean']-b[s][k]['fractional_residual_vs_clean'])<.001
 assert abs(a['clean']['0:0.5']['aperture_ratio']-1.20)<.02
 print(json.dumps(a,indent=2))
