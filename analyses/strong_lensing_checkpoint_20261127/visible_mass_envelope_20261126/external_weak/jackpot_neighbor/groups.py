import json, numpy as np
from pathlib import Path
from catalog import tables,dist,lens,plume
T=tables(Path('bgs_groups.fits'))['GALAXIES']
print(T.dtype.names,len(T))
d=dist(T['RA'],T['DEC'],*lens)
p=dist(T['RA'],T['DEC'],*plume)
zp=.2219305
use=((d<500)&(np.abs(T['Z']-zp)<.012))|(d<2)|(p<2)
cols=('TARGETID','RA','DEC','Z','IGRP','IS_SAT','M_HALO','N_SAT','Z_ASSIGNED_FLAG','LOGMSTAR')
def extract(i):
 t=T[i]
 return {c:(t[c].decode() if isinstance(t[c],bytes) else t[c].item()) for c in cols} | dict(lens_arcsec=float(d[i]),plume_arcsec=float(p[i]))
i=np.where(use)[0]; g=np.unique(T['IGRP'][i]); out={'selected':[extract(j) for j in i], 'group_members':[extract(j) for j in np.where(np.isin(T['IGRP'],g))[0]]}
print(json.dumps(out['selected'],indent=2)); print('group membership rows',len(out['group_members']))
Path('group_cone.json').write_text(json.dumps(out,indent=2,allow_nan=True)+'\n')
