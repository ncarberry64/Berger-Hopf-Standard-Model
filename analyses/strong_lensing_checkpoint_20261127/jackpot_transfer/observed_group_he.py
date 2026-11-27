"""Alternate published centroid in the same nonlinear pipeline; no lens fit."""
from pathlib import Path
from contextlib import redirect_stdout
import sys,io,json
import numpy as np
p=Path(__file__).resolve().parent
sys.path.insert(0,str(p.parent/'bhsm_environment_audit'))
with redirect_stdout(io.StringIO()):
 import he0435_joint_projected as h
h.Astar=h.Obj('sersic')
# Hold the velocity normalization fixed to Table 4 to isolate position.
center=np.array([69.559414,-12.276026])
origin=np.array([h.cfg['main_RA_Deg'],h.cfg['main_Dec_Deg']])
t=(center-origin)*3600*np.array([np.cos(np.deg2rad(origin[1])),1.])
assert abs(np.linalg.norm(t)-41.9)<.3
h.axis=t/np.linalg.norm(t)
t=41.9*h.axis
h.sep=41.9*h.d1*h.xrad
rows=[]
for n,B in [(80,1.5),(90,1.5),(90,2.25),(100,2.25),(115,2.25)]:
 a=h.run(n,B)
 print('residual',a['last_max_scaled_residual'],a['minimum_principal_eigenvalue'],flush=True)
 rows.append(a)
(p/'observed_group_he.json').write_text(json.dumps({'scope':'Sluse B1 alternate group centroid, Table 4 470 km/s normalization fixed, same group proxy; assumed same plane and zero LOS group-main depth.', 'centroid_arcsec':t.tolist(),'runs':rows},indent=2)+'\n')
